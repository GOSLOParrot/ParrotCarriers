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
import json
import logging
import os
import re
from dataclasses import fields
from enum import Enum
from pathlib import Path
from typing import Any, Callable

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

    def get_node_by_label_and_kind(self, label: str, kind: object) -> SemanticNode | None:
        """Find a node by exact label within the same NodeKind namespace.

        L2-B labels are human-facing names, not global identifiers. Web/manual
        imports must allow different kinds to reuse a label ("desk" as a zone
        and "desk" as an object), while repeated writes of the same kind/label
        should still merge unless a stable provider UUID says otherwise.
        """
        try:
            expected_kind = NodeKind(kind)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            expected_kind = kind
        label_lower = label.strip().lower()
        if not label_lower:
            return None
        for idx in self._graph.node_indices():
            node: SemanticNode = self._graph[idx]
            if node.kind == expected_kind and node.label.strip().lower() == label_lower:
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
        """Add a directed edge between two nodes by UUID.

        Phase 4 baseline: also stamps ``edge.meta["cross_compartment"]`` so
        IterativeSpreadingActivation can downweight edges that span
        IntentEvent / Bucket / Scene / Location boundaries (interface in
        ``parrot.dsg.l2b.compartments`` + plan §Phase 4). Tag is best-effort
        — never blocks edge creation.
        """
        src = self._uuid_to_idx.get(from_uuid)
        dst = self._uuid_to_idx.get(to_uuid)
        if src is None or dst is None:
            return False
        if edge is None:
            edge = SemanticEdge()
        try:
            src_node: SemanticNode = self._graph[src]
            dst_node: SemanticNode = self._graph[dst]
            cross_axes: list[str] = []
            if src_node.event_id and dst_node.event_id and src_node.event_id != dst_node.event_id:
                cross_axes.append("event")
            if src_node.bucket_id != dst_node.bucket_id:
                cross_axes.append("bucket")
            if src_node.scene_type and dst_node.scene_type and src_node.scene_type != dst_node.scene_type:
                cross_axes.append("scene")
            if src_node.location_tag and dst_node.location_tag and src_node.location_tag != dst_node.location_tag:
                cross_axes.append("location")
            if cross_axes:
                # Use the first axis as the canonical tag value (so existing
                # readers that check truthiness still work; full set in
                # ``cross_compartment_axes`` for sophisticated consumers).
                edge.meta.setdefault("cross_compartment", cross_axes[0])
                edge.meta.setdefault("cross_compartment_axes", tuple(cross_axes))
        except Exception:
            pass
        self._graph.add_edge(src, dst, edge)
        return True

    def update_edge_between(
        self,
        from_uuid: str,
        to_uuid: str,
        edge: SemanticEdge,
        *,
        match_kind: str = "",
        match_source: str = "",
    ) -> bool:
        """Replace the first matching edge payload between two UUIDs.

        RustworkX owns the directed topology and stores edge payloads by
        integer edge index. L2-B callers should not persist those transient
        indexes, so the Web/operator path identifies an edge by endpoints plus
        optional kind/source filters and updates the first matching payload.
        Parallel edges are still possible; when UI needs exact parallel-edge
        surgery, promote a stable edge id into ``SemanticEdge.meta`` first.
        """
        edge_idx = self._first_matching_edge_index(
            from_uuid,
            to_uuid,
            match_kind=match_kind,
            match_source=match_source,
        )
        if edge_idx is None:
            return False
        self._graph.update_edge_by_index(edge_idx, edge)
        return True

    def remove_edge_between(
        self,
        from_uuid: str,
        to_uuid: str,
        *,
        match_kind: str = "",
        match_source: str = "",
    ) -> bool:
        """Remove the first matching directed edge between two UUIDs.

        This is intentionally endpoint-based instead of exposing RustworkX's
        edge index through Web DTOs. It keeps the backend free to rebuild the
        graph while giving the operator console a safe, auditable delete path.
        """
        edge_idx = self._first_matching_edge_index(
            from_uuid,
            to_uuid,
            match_kind=match_kind,
            match_source=match_source,
        )
        if edge_idx is None:
            return False
        self._graph.remove_edge_from_index(edge_idx)
        return True

    def _first_matching_edge_index(
        self,
        from_uuid: str,
        to_uuid: str,
        *,
        match_kind: str = "",
        match_source: str = "",
    ) -> int | None:
        """Return a RustworkX edge index for endpoint/kind/source filters."""
        src = self._uuid_to_idx.get(from_uuid)
        dst = self._uuid_to_idx.get(to_uuid)
        if src is None or dst is None:
            return None
        try:
            edge_indices = list(self._graph.edge_indices_from_endpoints(src, dst))
        except Exception:
            return None
        for edge_idx in edge_indices:
            edge = self._graph.get_edge_data_by_index(edge_idx)
            if _edge_matches(edge, match_kind=match_kind, match_source=match_source):
                return int(edge_idx)
        return None

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

    def all_edges(self) -> list[tuple[SemanticNode, SemanticNode, SemanticEdge]]:
        """Return all directed edges with source/target node payloads.

        This is primarily a read-only monitor/export surface. It keeps Web
        consoles and smoke tests away from RustworkX internals while preserving
        ``L2BGraph`` as the only owner of the PyDiGraph index mapping.
        """
        result: list[tuple[SemanticNode, SemanticNode, SemanticEdge]] = []
        for edge_idx in self._graph.edge_indices():
            src_idx, dst_idx = self._graph.get_edge_endpoints_by_index(edge_idx)
            result.append((
                self._graph[src_idx],
                self._graph[dst_idx],
                self._graph.get_edge_data_by_index(edge_idx),
            ))
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
_hydrated_pointer_store_paths: set[str] = set()


def get_l2b_graph() -> L2BGraph:
    global _instance
    if _instance is None:
        _instance = L2BGraph()
        if os.getenv("PARROT_L2B_GRAPH_POINTER_STORE_DISABLED", "0") != "1":
            try:
                hydrate_materialized_graphiti_pointers(_instance, once=True)
            except Exception:
                logger.exception("L2B: failed to hydrate Graphiti pointer store")
    return _instance


def l2b_pointer_store_path(path: str | os.PathLike[str] | None = None) -> Path:
    """Return the JSON store for durable Graphiti pointer materializations.

    RustWorkX integer indices stay runtime-only. This file stores only stable
    business UUIDs plus SemanticNode/SemanticEdge payloads generated by the
    Graphiti materialize route.
    """

    configured = str(path or os.getenv("PARROT_L2B_GRAPH_POINTER_STORE_PATH") or "").strip()
    if configured:
        return Path(configured).expanduser()
    return Path("data") / "web_console" / "l2b_materialized_graphiti_pointers.json"


def persist_materialized_graphiti_pointers(
    graph: L2BGraph | None = None,
    *,
    path: str | os.PathLike[str] | None = None,
) -> Path:
    """Persist only operator-reviewed Graphiti pointer nodes/edges."""

    graph = graph or get_l2b_graph()
    store_path = l2b_pointer_store_path(path)
    payload = _materialized_graphiti_payload(graph)
    store_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = store_path.with_name(f"{store_path.name}.tmp")
    tmp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp_path.replace(store_path)
    return store_path


def hydrate_materialized_graphiti_pointers(
    graph: L2BGraph | None = None,
    *,
    path: str | os.PathLike[str] | None = None,
    once: bool = False,
) -> int:
    """Load durable Graphiti pointer nodes/edges into the runtime graph."""

    graph = graph or get_l2b_graph()
    store_path = l2b_pointer_store_path(path)
    marker = str(store_path.resolve())
    if once and marker in _hydrated_pointer_store_paths:
        return 0
    _hydrated_pointer_store_paths.add(marker)
    if not store_path.exists():
        return 0
    payload = json.loads(store_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        return 0
    nodes = payload.get("nodes") if isinstance(payload.get("nodes"), list) else []
    edges = payload.get("edges") if isinstance(payload.get("edges"), list) else []
    loaded = 0
    for item in nodes:
        if not isinstance(item, dict):
            continue
        try:
            graph.upsert_node(_semantic_node_from_payload(item))
            loaded += 1
        except Exception:
            logger.exception("L2B: failed to hydrate node from pointer store")

    existing = _stable_edge_keys(graph)
    for item in edges:
        if not isinstance(item, dict):
            continue
        source = str(item.get("source") or "")
        target = str(item.get("target") or "")
        edge_payload = item.get("edge") if isinstance(item.get("edge"), dict) else {}
        if not source or not target:
            continue
        key = _stable_edge_key(source, target, edge_payload)
        if key in existing:
            continue
        try:
            if graph.connect(source, target, _semantic_edge_from_payload(edge_payload)):
                existing.add(key)
        except Exception:
            logger.exception("L2B: failed to hydrate edge from pointer store")
    return loaded


def _materialized_graphiti_payload(graph: L2BGraph) -> dict[str, Any]:
    nodes = [
        node
        for node in graph.all_nodes()
        if str(getattr(node, "source", "") or "") == "graphiti"
        and (getattr(node, "meta", {}) or {}).get("materialization_state")
        == "materialized_l2b_pointer"
    ]
    node_uuids = {str(node.uuid) for node in nodes}
    edges = [
        (src, dst, edge)
        for src, dst, edge in graph.all_edges()
        if str(getattr(src, "uuid", "") or "") in node_uuids
        and str(getattr(dst, "uuid", "") or "") in node_uuids
        and (getattr(edge, "meta", {}) or {}).get("materialization_state")
        == "materialized_l2b_pointer_edge"
    ]
    return {
        "schema_version": 1,
        "store_kind": "l2b_materialized_graphiti_pointers",
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes": [_node_payload(node) for node in nodes],
        "edges": [
            {
                "source": src.uuid,
                "target": dst.uuid,
                "edge": _edge_payload(edge),
            }
            for src, dst, edge in edges
        ],
        "policy": {
            "preserve_raw_graphiti": True,
            "rwx_indices_persisted": False,
            "graphiti_authoritative": True,
        },
    }


def _node_payload(node: SemanticNode) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for field in fields(SemanticNode):
        if field.name == "_rx_index":
            continue
        payload[field.name] = _jsonable(getattr(node, field.name))
    return payload


def _edge_payload(edge: SemanticEdge) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for field in fields(SemanticEdge):
        payload[field.name] = _jsonable(getattr(edge, field.name))
    return payload


def _semantic_node_from_payload(data: dict[str, Any]) -> SemanticNode:
    kwargs: dict[str, Any] = {}
    for field in fields(SemanticNode):
        if field.name == "_rx_index" or field.name not in data:
            continue
        value = data[field.name]
        if field.name == "kind":
            kwargs[field.name] = _enum_or_default(NodeKind, value, NodeKind.OBJECT)
        elif field.name == "salience":
            kwargs[field.name] = _enum_or_default(Salience, value, Salience.BACKGROUND)
        elif field.name == "confirmation":
            kwargs[field.name] = _enum_or_default(
                ConfirmationStatus,
                value,
                ConfirmationStatus.EXPECTED,
            )
        elif field.name == "time_span":
            if isinstance(value, list):
                kwargs[field.name] = tuple(value[:2]) if len(value) >= 2 else (0.0, None)
            else:
                kwargs[field.name] = value
        elif field.name in {"known_facts", "tags"}:
            kwargs[field.name] = list(value or [])
        elif field.name in {"source_meta", "meta"}:
            kwargs[field.name] = dict(value or {})
        else:
            kwargs[field.name] = value
    return SemanticNode(**kwargs)


def _semantic_edge_from_payload(data: dict[str, Any]) -> SemanticEdge:
    kwargs: dict[str, Any] = {}
    for field in fields(SemanticEdge):
        if field.name not in data:
            continue
        value = data[field.name]
        if field.name == "kind":
            kwargs[field.name] = _enum_or_default(EdgeKind, value, EdgeKind.ASSOCIATED_WITH)
        elif field.name in {"ref_ids", "view_classes"}:
            kwargs[field.name] = tuple(value or [])
        elif field.name == "meta":
            kwargs[field.name] = dict(value or {})
        else:
            kwargs[field.name] = value
    return SemanticEdge(**kwargs)


def _stable_edge_keys(graph: L2BGraph) -> set[tuple[str, str, str, str, str]]:
    return {
        _stable_edge_key(src.uuid, dst.uuid, _edge_payload(edge))
        for src, dst, edge in graph.all_edges()
    }


def _stable_edge_key(
    source: str,
    target: str,
    edge_payload: dict[str, Any],
) -> tuple[str, str, str, str, str]:
    return (
        str(source or ""),
        str(target or ""),
        str(edge_payload.get("kind") or ""),
        str(edge_payload.get("source") or ""),
        str(edge_payload.get("graphiti_uuid") or ""),
    )


def _enum_or_default(enum_cls: type[Enum], value: Any, default: Enum) -> Enum:
    try:
        return enum_cls(str(value))
    except (TypeError, ValueError):
        return default


def _jsonable(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    return value


def _edge_matches(edge: SemanticEdge, *, match_kind: str, match_source: str) -> bool:
    """Match a semantic edge without leaking RustworkX internals to callers."""
    if match_kind:
        kind = getattr(edge.kind, "value", str(edge.kind))
        if kind != match_kind:
            return False
    if match_source and str(edge.source) != match_source:
        return False
    return True
