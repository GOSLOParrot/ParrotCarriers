"""AttentionMechanism — pluggable associative-activation strategy.

Strategy candidates (主设计稿 § 3.3 + dsg-rustworkx-master § 3):
    - BoundedBfsActivation        desktop baseline (4 hops, AGCN-validated)
    - IterativeSpreadingActivation Phase 4 baseline real Collins-Loftus
                                   diffusion (NEW: replaces the placeholder)
    - SpreadingActivationPlaceholder Back-compat alias of the iterative
                                   strategy (kept for tests / call sites
                                   that imported the old placeholder).
    - PPRPlaceholder              HippoRAG style (P3 仿生 chat)
    - GatLikeSoftmaxPlaceholder   GAT-inspired neighbour softmax (P3)

Returns a ranked list of (node_uuid, score) for the seed activation.
The L2-B graph is not mutated by activation; results feed Brain Intent
layer / Context Injector / RecallTool consumers.

Cross-compartment edge weighting (Phase 4):
    Iterative Spreading reads ``edge.meta["cross_compartment"]`` and
    multiplies the propagated score by ``cross_compartment_weight``
    (default 0.5) to keep activation from leaking across IntentEvent /
    Bucket boundaries unless an explicit cross-event channel is opened.
    See DSG-INTENT-EVENT-V1 § 3.4 + plan §Phase 4.
"""

from __future__ import annotations

from collections import deque
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from parrot.dsg.l2b_graph import L2BGraph


class AttentionMechanism(Protocol):
    def activate(
        self,
        graph: "L2BGraph",
        seed_uuids: tuple[str, ...],
        max_depth: int = 4,
        top_k: int = 16,
    ) -> list[tuple[str, float]]: ...


class NoOpActivation:
    """Returns just the seeds with constant score; for tests."""

    def activate(
        self,
        graph: "L2BGraph",
        seed_uuids: tuple[str, ...],
        max_depth: int = 4,
        top_k: int = 16,
    ) -> list[tuple[str, float]]:
        return [(u, 1.0) for u in seed_uuids[:top_k]]


class BoundedBfsActivation:
    """Desktop baseline activation — limited-depth BFS with evidence
    weighting.

    Score function:
        score(n) = node.evidence_score * (decay ** depth)
    Where ``decay`` defaults to 0.7. Hops ≥ ``max_depth`` are dropped.

    Hard upper bound 4 hops follows AGCN empirical study
    (dsg-attention-schema-papers § 1.3). P3 may up-weight cross-event
    edges so associative recall traverses Compartment boundaries.
    """

    def __init__(self, hop_decay: float = 0.7) -> None:
        self._decay = hop_decay

    def activate(
        self,
        graph: "L2BGraph",
        seed_uuids: tuple[str, ...],
        max_depth: int = 4,
        top_k: int = 16,
    ) -> list[tuple[str, float]]:
        scores: dict[str, float] = {}
        max_depth = min(max(0, max_depth), 4)  # AGCN hard ceiling

        queue: deque[tuple[str, int, float]] = deque()
        for seed in seed_uuids:
            seed_node = graph.get_node(seed)
            if seed_node is None:
                continue
            scores[seed] = max(scores.get(seed, 0.0), seed_node.evidence_score or 1.0)
            queue.append((seed, 0, scores[seed]))

        visited: set[str] = set(seed_uuids)
        while queue:
            uuid, depth, score = queue.popleft()
            if depth >= max_depth:
                continue
            for neighbour in graph.get_neighbors(uuid):
                if neighbour.uuid in visited:
                    continue
                visited.add(neighbour.uuid)
                next_score = score * self._decay
                weight = neighbour.evidence_score or 0.5
                scores[neighbour.uuid] = max(
                    scores.get(neighbour.uuid, 0.0), next_score * weight,
                )
                queue.append((neighbour.uuid, depth + 1, scores[neighbour.uuid]))

        return sorted(scores.items(), key=lambda kv: kv[1], reverse=True)[:top_k]


class IterativeSpreadingActivation:
    """Phase 4 baseline real Collins-Loftus 1975 spreading-activation.

    Algorithm (dsg-attention-schema-papers § 5.4):
        activation[t+1][n] = decay * Σ ( w[m→n] * activation[t][m] )
                              for m in incoming-neighbours of n

    Stops when:
        * iteration count reaches ``max_iter`` (default 5)
        * sum of new activations < ``epsilon`` (default 0.01)
        * hop distance from any seed exceeds ``max_depth`` (hard cap 4
          per AGCN empirical, dsg-rustworkx-master § 3.5).

    Cross-compartment downweighting:
        edges flagged ``meta["cross_compartment"]`` propagate at
        ``cross_compartment_weight`` of the normal flow (default 0.5).
        Use ``cross_compartment_weight=1.0`` for "open channel" mode.

    Edge weighting uses ``SemanticEdge.strength`` (range [0, 1], default
    0.5) and node ``evidence_score``. Result is a ranked list of
    ``(uuid, score)`` truncated to ``top_k``.

    Read-only: does NOT mutate any node attention or edge meta.
    """

    def __init__(
        self,
        decay: float = 0.7,
        epsilon: float = 0.01,
        max_iter: int = 5,
        cross_compartment_weight: float = 0.5,
    ) -> None:
        if not 0.0 < decay <= 1.0:
            raise ValueError("decay must be in (0, 1]")
        if epsilon <= 0:
            raise ValueError("epsilon must be > 0")
        if max_iter <= 0:
            raise ValueError("max_iter must be > 0")
        self._decay = decay
        self._epsilon = epsilon
        self._max_iter = max_iter
        self._xc_weight = cross_compartment_weight

    def activate(
        self,
        graph: "L2BGraph",
        seed_uuids: tuple[str, ...],
        max_depth: int = 4,
        top_k: int = 16,
    ) -> list[tuple[str, float]]:
        max_depth = min(max(0, max_depth), 4)  # AGCN hop hard ceiling

        scores: dict[str, float] = {}
        depth: dict[str, int] = {}
        for seed in seed_uuids:
            seed_node = graph.get_node(seed)
            if seed_node is None:
                continue
            scores[seed] = max(scores.get(seed, 0.0), seed_node.evidence_score or 1.0)
            depth[seed] = 0

        if not scores:
            return []

        for _iteration in range(self._max_iter):
            delta: dict[str, float] = {}
            for src_uuid, src_score in list(scores.items()):
                src_depth = depth.get(src_uuid, max_depth)
                if src_depth >= max_depth:
                    continue
                try:
                    pairs = graph.get_edges_from(src_uuid)
                except Exception:
                    continue
                for neighbour, edge in pairs:
                    edge_strength = float(getattr(edge, "strength", 0.5) or 0.5)
                    cross = bool((getattr(edge, "meta", None) or {}).get(
                        "cross_compartment",
                    ))
                    weight = edge_strength * (
                        self._xc_weight if cross else 1.0
                    )
                    flow = self._decay * weight * src_score * (
                        neighbour.evidence_score or 0.5
                    )
                    if flow <= 0:
                        continue
                    nbr_uuid = neighbour.uuid
                    prev = scores.get(nbr_uuid, 0.0) + delta.get(nbr_uuid, 0.0)
                    if flow > prev:
                        delta[nbr_uuid] = flow - scores.get(nbr_uuid, 0.0)
                        # Track shallowest depth seen so we keep
                        # propagating until max_depth.
                        depth[nbr_uuid] = min(
                            depth.get(nbr_uuid, max_depth),
                            src_depth + 1,
                        )

            if not delta or sum(delta.values()) < self._epsilon:
                break
            for uuid, add in delta.items():
                scores[uuid] = scores.get(uuid, 0.0) + add

        return sorted(scores.items(), key=lambda kv: kv[1], reverse=True)[:top_k]


class SpreadingActivationPlaceholder:
    """Backward-compat alias — delegates to :class:`IterativeSpreadingActivation`.

    Kept so existing tests / call sites that imported
    ``SpreadingActivationPlaceholder`` still work unchanged. New code
    should import :class:`IterativeSpreadingActivation` directly.
    """

    def __init__(self, decay: float = 0.5) -> None:
        self._inner = IterativeSpreadingActivation(decay=decay)

    def activate(
        self,
        graph: "L2BGraph",
        seed_uuids: tuple[str, ...],
        max_depth: int = 4,
        top_k: int = 16,
    ) -> list[tuple[str, float]]:
        return self._inner.activate(graph, seed_uuids, max_depth, top_k)


# ─── Registry ────────────────────────────────────────────────────

_mechanism: AttentionMechanism | None = None


def register_attention_mechanism(mechanism: AttentionMechanism) -> None:
    global _mechanism
    _mechanism = mechanism


def get_attention_mechanism() -> AttentionMechanism:
    global _mechanism
    if _mechanism is None:
        _mechanism = BoundedBfsActivation()
    return _mechanism


__all__ = [
    "AttentionMechanism",
    "BoundedBfsActivation",
    "IterativeSpreadingActivation",
    "NoOpActivation",
    "SpreadingActivationPlaceholder",
    "get_attention_mechanism",
    "register_attention_mechanism",
]
