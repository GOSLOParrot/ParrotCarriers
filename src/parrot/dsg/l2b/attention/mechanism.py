"""AttentionMechanism — pluggable associative-activation strategy.

Strategy candidates (主设计稿 § 3.3 + dsg-rustworkx-master § 3):
    - BoundedBfsActivation     desktop baseline (limit 4 hops, AGCN-validated)
    - SpreadingActivationPlaceholder    Collins-Loftus 1975 (P3 actual)
    - PPRPlaceholder           HippoRAG style (P3)
    - GatLikeSoftmaxPlaceholder GAT-inspired neighbour softmax (P3)

Returns a ranked list of (node_uuid, score) for the seed activation.
The L2-B graph is not mutated by activation; results feed Brain Intent
layer / Context Injector / RecallTool consumers.
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


class SpreadingActivationPlaceholder:
    """Placeholder for Collins-Loftus 1975 spreading-activation.

    # TODO(P3-attention-spreading): SKELETON. Currently delegates to
    #   ``BoundedBfsActivation``. P3 should replace with iterative
    #   diffusion:
    #     activation[t+1][n] = decay * sum(weight[n,m] * activation[t][m]
    #                                       for m in neighbors(n))
    #   Stop when sum of new activations < epsilon or iter > max_iter.
    #   See dsg-attention-schema-papers § 5.4 + dsg-rustworkx-master § 3.3.
    """

    def __init__(self, decay: float = 0.5) -> None:
        self._inner = BoundedBfsActivation(hop_decay=decay)

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
    "NoOpActivation",
    "SpreadingActivationPlaceholder",
    "get_attention_mechanism",
    "register_attention_mechanism",
]
