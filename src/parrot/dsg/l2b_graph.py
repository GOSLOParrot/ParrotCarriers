"""L2-B Semantic Graph — RustworkX-backed working memory.

This is the runtime semantic graph. It holds enriched views of entities
that Graphiti knows about, plus attention/episode metadata that only
lives in memory.

Key operations:
  - preload_from_graphiti(): fill graph from Graphiti scene partition
  - upsert_node(): add or update a semantic node
  - connect(): create edges between nodes
  - get_episode_subgraph(): nodes active in an episode window
  - archive_episode(): persist episode data back to Graphiti
  - query_by_attention(): get top-N attended nodes for Context Injector

Design:
  - RustworkX PyDiGraph stores SemanticNode / SemanticEdge dataclasses
  - UUID → rx_index mapping maintained in a dict for O(1) lookup
  - Graph is session-scoped: cleared on scene switch, rebuilt from Graphiti
"""

from __future__ import annotations

import datetime
import logging
import re
import time
from typing import Callable

from parrot.dsg.l2b_types import (
    ConfirmationStatus,
    EdgeKind,
    EpisodeMarker,
    NodeKind,
    Salience,
    SemanticEdge,
    SemanticNode,
)

logger = logging.getLogger(__name__)

try:
    import rustworkx as rx
except ImportError:
    rx = None  # type: ignore[assignment]
    logger.warning("rustworkx not installed — L2-B graph disabled")


class L2BGraph:
    """Semantic working memory graph backed by RustworkX."""

    def __init__(self) -> None:
        if rx is None:
            raise RuntimeError("rustworkx required: pip install rustworkx")
        self._graph: rx.PyDiGraph = rx.PyDiGraph()
        self._uuid_to_idx: dict[str, int] = {}
        self._episodes: dict[str, EpisodeMarker] = {}
        self._current_episode_id: str = ""

    # ━━━ Node operations ━━━

    def upsert_node(self, node: SemanticNode) -> int:
        """Add a new node or update existing by UUID. Returns rx index."""
        if node.uuid in self._uuid_to_idx:
            idx = self._uuid_to_idx[node.uuid]
            node._rx_index = idx
            self._graph[idx] = node
            return idx

        idx = self._graph.add_node(node)
        node._rx_index = idx
        self._uuid_to_idx[node.uuid] = idx
        logger.debug("L2B: added node %s (%s) idx=%d", node.label, node.kind.value, idx)
        return idx

    def get_node(self, uuid: str) -> SemanticNode | None:
        idx = self._uuid_to_idx.get(uuid)
        if idx is None:
            return None
        return self._graph[idx]

    def get_node_by_label(self, label: str) -> SemanticNode | None:
        """Find first node matching label (case-insensitive substring)."""
        label_lower = label.lower()
        for idx in self._graph.node_indices():
            node: SemanticNode = self._graph[idx]
            if label_lower in node.label.lower():
                return node
        return None

    def remove_node(self, uuid: str) -> bool:
        idx = self._uuid_to_idx.pop(uuid, None)
        if idx is None:
            return False
        self._graph.remove_node(idx)
        return True

    def all_nodes(self) -> list[SemanticNode]:
        return [self._graph[i] for i in self._graph.node_indices()]

    def node_count(self) -> int:
        return self._graph.num_nodes()

    # ━━━ Edge operations ━━━

    def connect(
        self,
        from_uuid: str,
        to_uuid: str,
        edge: SemanticEdge | None = None,
    ) -> bool:
        """Add a directed edge between two nodes by UUID."""
        src = self._uuid_to_idx.get(from_uuid)
        dst = self._uuid_to_idx.get(to_uuid)
        if src is None or dst is None:
            return False
        if edge is None:
            edge = SemanticEdge()
        self._graph.add_edge(src, dst, edge)
        return True

    def get_neighbors(self, uuid: str) -> list[SemanticNode]:
        """Get nodes connected TO this node (successors)."""
        idx = self._uuid_to_idx.get(uuid)
        if idx is None:
            return []
        return [self._graph[n] for n in self._graph.neighbors(idx)]

    def get_edges_from(self, uuid: str) -> list[tuple[SemanticNode, SemanticEdge]]:
        """Get (target_node, edge) pairs for all outgoing edges."""
        idx = self._uuid_to_idx.get(uuid)
        if idx is None:
            return []
        result = []
        for target_idx in self._graph.neighbors(idx):
            edge_data = self._graph.get_edge_data(idx, target_idx)
            result.append((self._graph[target_idx], edge_data))
        return result

    # ━━━ Attention queries ━━━

    def query_by_attention(self, top_n: int = 5, min_attention: float = 0.0) -> list[SemanticNode]:
        """Return top-N nodes sorted by attention weight."""
        nodes = [
            self._graph[i] for i in self._graph.node_indices()
            if self._graph[i].attention >= min_attention
        ]
        nodes.sort(key=lambda n: n.attention, reverse=True)
        return nodes[:top_n]

    def query_notable(self) -> list[SemanticNode]:
        """Return all nodes worth mentioning to Gemini."""
        return [
            self._graph[i] for i in self._graph.node_indices()
            if self._graph[i].is_notable()
        ]

    def query_by_kind(self, kind: NodeKind) -> list[SemanticNode]:
        return [
            self._graph[i] for i in self._graph.node_indices()
            if self._graph[i].kind == kind
        ]

    def filter_nodes(self, predicate: Callable[[SemanticNode], bool]) -> list[SemanticNode]:
        return [
            self._graph[i] for i in self._graph.node_indices()
            if predicate(self._graph[i])
        ]

    # ━━━ Episode management ━━━

    def start_episode(self, title: str = "", trigger_source: str = "") -> EpisodeMarker:
        """Begin a new episode.

        DSG-ARCHIVE-V1 § 5.1 (2026-05-06): the previous episode is
        **not** immediately archived to Graphiti anymore. It is
        enqueued into the idle-archive disk queue and processed by
        ``IdleArchiveTrigger`` when the nanobot worker is idle.

        ``archive_episode_to_graphiti`` itself is preserved; it is
        invoked by ``ConversationArchive.archive_to_graphiti`` during
        Phase 3 of the delayed-archive pipeline.
        """
        if self._current_episode_id:
            old_ep = self.close_current_episode()
            if old_ep:
                try:
                    from parrot.dsg.archive.conversation import (
                        enqueue_episode_for_idle_archive,
                    )
                    enqueue_episode_for_idle_archive(old_ep.episode_id)
                except Exception:
                    logger.exception("L2B: enqueue_for_idle_archive failed")

        ep = EpisodeMarker(title=title, trigger_source=trigger_source)
        self._episodes[ep.episode_id] = ep
        self._current_episode_id = ep.episode_id
        logger.info("L2B: started episode %s — %s", ep.episode_id, title or "(untitled)")
        return ep

    def close_current_episode(self, summary: str = "") -> EpisodeMarker | None:
        ep = self._episodes.get(self._current_episode_id)
        if ep and ep.is_open:
            active = [
                n.uuid for n in self.all_nodes()
                if n.episode_id == ep.episode_id
            ]
            ep.participating_node_uuids = active
            ep.close(summary)
            logger.info(
                "L2B: closed episode %s — %d nodes, summary=%s",
                ep.episode_id, len(active), summary[:60] if summary else "(none)",
            )
        self._current_episode_id = ""
        return ep

    def get_current_episode(self) -> EpisodeMarker | None:
        return self._episodes.get(self._current_episode_id)

    def assign_node_to_current_episode(self, uuid: str) -> None:
        """Tag a node as belonging to the current episode."""
        node = self.get_node(uuid)
        if node and self._current_episode_id:
            node.episode_id = self._current_episode_id

    def get_episode_nodes(self, episode_id: str) -> list[SemanticNode]:
        return [
            self._graph[i] for i in self._graph.node_indices()
            if self._graph[i].episode_id == episode_id
        ]

    # ━━━ Graphiti bridge ━━━

    async def preload_from_graphiti(self, zone: str = "") -> int:
        """Load known objects from Graphiti scene partition into the graph.

        Returns number of nodes loaded.
        """
        try:
            from parrot.memory.graphiti_client import PARTITIONS, get_graphiti
        except ImportError:
            logger.warning("L2B: graphiti not available for preload")
            return 0

        g = await get_graphiti()
        query = f"objects in zone '{zone}'" if zone else "known scene objects"
        results = await g.search(
            query=query,
            group_ids=[PARTITIONS.SCENE],
            num_results=30,
        )

        _uuid_re = re.compile(r"\(uuid=([^)]+)\)")
        loaded = 0
        for r in results:
            fact = getattr(r, "fact", None) or getattr(r, "text", str(r))
            m = _uuid_re.search(fact)
            obsidian_uuid = m.group(1) if m else ""
            clean_fact = _uuid_re.sub("", fact).strip()

            node = SemanticNode(
                uuid=obsidian_uuid or getattr(r, "uuid", ""),
                kind=NodeKind.OBJECT,
                label=clean_fact[:60],
                graphiti_uuid=getattr(r, "uuid", ""),
                obsidian_uuid=obsidian_uuid,
                known_facts=[fact],
                confirmation=ConfirmationStatus.EXPECTED,
                attention=0.3,
                salience=Salience.BACKGROUND,
            )
            self.upsert_node(node)
            loaded += 1

        logger.info("L2B: preloaded %d nodes from Graphiti (zone=%s)", loaded, zone or "all")
        return loaded

    async def enrich_from_obsidian(self, uuid: str) -> bool:
        """Try to enrich a node with additional info from Obsidian SSOT via Graphiti.

        Searches user partition for extra facts about this object.
        Returns True if enrichment found.
        """
        node = self.get_node(uuid)
        if not node:
            return False

        try:
            from parrot.memory.graphiti_client import PARTITIONS, get_graphiti

            g = await get_graphiti()
            query = f"details about {node.label}"
            if node.obsidian_uuid:
                query += f" (uuid={node.obsidian_uuid})"

            results = await g.search(
                query=query,
                group_ids=[PARTITIONS.SCENE, PARTITIONS.USER],
                num_results=5,
            )

            if results:
                for r in results:
                    fact = getattr(r, "fact", None) or getattr(r, "text", str(r))
                    if fact not in node.known_facts:
                        node.known_facts.append(fact)

                node.evidence_score += 0.15
                if node.evidence_score >= 0.6:
                    node.confirmation = ConfirmationStatus.CONFIRMED
                logger.debug("L2B: enriched %s with %d facts", node.label, len(results))
                return True
        except Exception:
            logger.debug("L2B: enrichment failed for %s", node.label)
        return False

    async def archive_episode_to_graphiti(self, episode_id: str) -> bool:
        """Archive a closed episode back to Graphiti for long-term memory."""
        ep = self._episodes.get(episode_id)
        if not ep or ep.is_open:
            return False
        if ep.archived_to_graphiti:
            return True

        try:
            from graphiti_core.nodes import EpisodeType

            from parrot.memory.graphiti_client import PARTITIONS, get_graphiti

            g = await get_graphiti()

            parts = [f"Episode: {ep.title or '(untitled)'}"]
            if ep.summary:
                parts.append(f"Summary: {ep.summary}")
            parts.append(f"Duration: {ep.ended_at - ep.started_at:.0f}s")

            nodes = self.get_episode_nodes(episode_id)
            if nodes:
                obj_labels = [n.label for n in nodes if n.kind == NodeKind.OBJECT]
                if obj_labels:
                    parts.append(f"Objects involved: {', '.join(obj_labels[:10])}")

            text = "\n".join(parts)

            await g.add_episode(
                name=f"dsg_episode_{episode_id}",
                episode_body=text,
                source=EpisodeType.text,
                source_description=f"dsg_episode:{episode_id}",
                reference_time=datetime.datetime.fromtimestamp(
                    ep.ended_at, tz=datetime.timezone.utc,
                ),
                group_id=PARTITIONS.GOSLO,
            )

            ep.archived_to_graphiti = True
            logger.info("L2B: archived episode %s to Graphiti", episode_id)
            return True

        except Exception:
            logger.exception("L2B: failed to archive episode %s", episode_id)
            return False

    # ━━━ Scene summary for Context Injector ━━━

    def build_scene_summary(self, max_items: int = 10) -> str:
        """Build a human-readable scene summary for Gemini context injection."""
        notable = self.query_by_attention(top_n=max_items, min_attention=0.2)
        if not notable:
            return "No objects currently tracked in the scene."

        lines = [f"Scene ({self.node_count()} objects tracked):"]
        for n in notable:
            status = f"[{n.confirmation.value}]" if n.confirmation != ConfirmationStatus.CONFIRMED else ""
            if n.salience == Salience.ALERT:
                status = "[ALERT]"
            attention_bar = "●" * int(n.attention * 5) + "○" * (5 - int(n.attention * 5))
            line = f"  - {n.label} {status} {attention_bar}"
            if n.known_facts:
                line += f" — {n.known_facts[0][:40]}"
            lines.append(line)

        ep = self.get_current_episode()
        if ep:
            lines.append(f"  [episode: {ep.title or ep.episode_id}]")

        return "\n".join(lines)

    # ━━━ Reset ━━━

    def clear(self) -> None:
        """Clear all nodes, edges, and episodes — used on scene switch."""
        self._graph = rx.PyDiGraph()
        self._uuid_to_idx.clear()
        self._episodes.clear()
        self._current_episode_id = ""
        logger.info("L2B: graph cleared")


# ━━━ Module-level singleton ━━━

_instance: L2BGraph | None = None


def get_l2b_graph() -> L2BGraph:
    global _instance
    if _instance is None:
        _instance = L2BGraph()
    return _instance
