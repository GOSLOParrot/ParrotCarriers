"""L2-B cluster strategy — RustworkX-based subgraph grouping.

Phase 4 baseline (NEED-P3-B / Plan §Phase 4):
    * ``ConnectedComponentsClusterStrategy`` — wraps
      ``rustworkx.weakly_connected_components`` over the directed L2-B
      graph. Returns one cluster per WCC; deterministic ordering by node
      uuid so tests are stable.

P3 alternatives (interfaces ready, deferred):
    * Leiden Community detection (NetworkX bridge) — needs density gate
      tuning; not on Phase 4 scope.
    * Louvain — same family, different resolution parameter.
    * VF2++ subgraph isomorphism for "experience matching" — deferred to
      ``intent_event_boundary.SubgraphFoldStrategy`` once a real
      cross-event channel matures.

How TODO decisions:
    * Cluster is a *read-only* result type. We don't mutate the graph,
      don't tag nodes with ``cluster_id`` in their fields, and don't add
      synthetic Cluster nodes. Mutation belongs to ``IntentEventBoundary
      .fold_strategy`` if/when we adopt the rustworkx subgraph fold path.
    * Hop hard cap = 4 (AGCN empirical) is enforced inside the spreading
      module, not here — clustering is global, not seed-bounded.
    * Cross-compartment edges (``edge.meta["cross_compartment"] = axis``)
      can be deprioritised by cluster strategies but the baseline
      Connected-Components ignores them; that boundary downweighting
      lives in ``IterativeSpreadingActivation`` next door.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Iterable, Protocol

if TYPE_CHECKING:
    from parrot.dsg.l2b_graph import L2BGraph
    from parrot.dsg.l2b_types import SemanticNode

logger = logging.getLogger(__name__)

try:
    import rustworkx as rx
except ImportError:
    rx = None  # type: ignore[assignment]


# ─── Result dataclass ────────────────────────────────────────────────


@dataclass(frozen=True)
class Cluster:
    """A single cluster's identity + member uuids.

    ``cluster_id`` is deterministic: ``"cluster_<axis>_<sha1-prefix>"``
    so two runs with the same node set produce the same id.
    """

    cluster_id: str
    member_uuids: tuple[str, ...]
    axis: str = "wcc"

    def size(self) -> int:
        return len(self.member_uuids)


@dataclass(frozen=True)
class ClusterResult:
    """All clusters from a single :meth:`detect` call."""

    clusters: tuple[Cluster, ...]
    total_nodes: int

    def largest(self) -> Cluster | None:
        if not self.clusters:
            return None
        return max(self.clusters, key=lambda c: c.size())


# ─── Strategy protocol ───────────────────────────────────────────────


class ClusterStrategy(Protocol):
    """Strategy contract for L2-B clustering.

    Strategies MUST be pure: no node mutation; no graph add/remove. The
    L2-B single-write boundary stays at IngestRunner / IntentEventBoundary.
    """

    def detect(
        self,
        graph: "L2BGraph",
        node_filter: "Callable[[SemanticNode], bool] | None" = None,  # noqa: F821
    ) -> ClusterResult: ...


# ─── Baseline implementation ────────────────────────────────────────


def _hash_member_set(member_uuids: Iterable[str]) -> str:
    """Stable hex digest of a member set, independent of iteration order."""
    import hashlib

    h = hashlib.sha1()
    for u in sorted(member_uuids):
        h.update(u.encode("utf-8"))
        h.update(b"\x00")
    return h.hexdigest()[:12]


class NoOpClusterStrategy:
    """Returns one cluster per node — useful as fallback / test sentinel."""

    def detect(
        self,
        graph: "L2BGraph",
        node_filter=None,  # noqa: ANN001
    ) -> ClusterResult:
        nodes = graph.all_nodes()
        if node_filter:
            nodes = [n for n in nodes if node_filter(n)]
        clusters = tuple(
            Cluster(
                cluster_id=f"cluster_singleton_{n.uuid}",
                member_uuids=(n.uuid,),
                axis="singleton",
            )
            for n in nodes
        )
        return ClusterResult(clusters=clusters, total_nodes=len(nodes))


class ConnectedComponentsClusterStrategy:
    """Phase 4 baseline — undirected weakly-connected components.

    Algorithm:
        1. Filter nodes through ``node_filter`` (if any).
        2. Build a temporary undirected adjacency over the filtered set,
           dropping edges that connect to filtered-out nodes.
        3. Use ``rustworkx.connected_components`` on a fresh ``PyGraph``
           (not PyDiGraph) — RustworkX provides true WCC over directed
           graphs via ``weakly_connected_components`` but the cluster
           identity is the same.
        4. Map back to uuids; emit deterministic ``cluster_id`` digests.

    The temporary graph approach keeps this strategy from depending on
    L2BGraph's internal RustworkX index, so it stays robust across
    episodes / scene clears that change the underlying graph identity.
    """

    def detect(
        self,
        graph: "L2BGraph",
        node_filter=None,  # noqa: ANN001
    ) -> ClusterResult:
        if rx is None:
            logger.warning(
                "ConnectedComponentsClusterStrategy: rustworkx unavailable, "
                "returning no clusters",
            )
            return ClusterResult(clusters=(), total_nodes=0)

        nodes = graph.all_nodes()
        if node_filter:
            nodes = [n for n in nodes if node_filter(n)]

        if not nodes:
            return ClusterResult(clusters=(), total_nodes=0)

        # Build a fresh undirected helper graph for WCC.
        helper = rx.PyGraph()
        uuid_set = {n.uuid for n in nodes}
        idx_by_uuid: dict[str, int] = {}
        for n in nodes:
            idx = helper.add_node(n.uuid)
            idx_by_uuid[n.uuid] = idx

        # Re-stamp edges from L2BGraph; skip endpoints not in the filtered set.
        for n in nodes:
            try:
                pairs = graph.get_edges_from(n.uuid)
            except Exception:
                continue
            for tgt, _edge in pairs:
                if tgt.uuid in uuid_set and tgt.uuid != n.uuid:
                    a, b = idx_by_uuid[n.uuid], idx_by_uuid[tgt.uuid]
                    if not helper.has_edge(a, b):
                        helper.add_edge(a, b, None)

        components: list[set[int]] = list(rx.connected_components(helper))

        clusters: list[Cluster] = []
        for comp in components:
            members = tuple(sorted(helper[i] for i in comp))
            clusters.append(Cluster(
                cluster_id=f"cluster_wcc_{_hash_member_set(members)}",
                member_uuids=members,
                axis="wcc",
            ))

        # Stable ordering: largest first then by id, so tests can compare
        # without sorting at the call site.
        clusters.sort(key=lambda c: (-c.size(), c.cluster_id))
        return ClusterResult(clusters=tuple(clusters), total_nodes=len(nodes))


# ─── Registry singleton ──────────────────────────────────────────────


_strategy: ClusterStrategy | None = None


def get_cluster_strategy() -> ClusterStrategy:
    global _strategy
    if _strategy is None:
        _strategy = ConnectedComponentsClusterStrategy()
    return _strategy


def register_cluster_strategy(strategy: ClusterStrategy) -> None:
    """Replace the singleton (P3 chat / tests). New strategies must
    honour the read-only contract — no graph mutation."""
    global _strategy
    _strategy = strategy


__all__ = [
    "Cluster",
    "ClusterResult",
    "ClusterStrategy",
    "ConnectedComponentsClusterStrategy",
    "NoOpClusterStrategy",
    "get_cluster_strategy",
    "register_cluster_strategy",
]
