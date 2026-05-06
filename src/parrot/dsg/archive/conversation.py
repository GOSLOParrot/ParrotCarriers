"""ConversationArchive — Phase 2 + 3 of the delayed-archive pipeline.

DSG-ARCHIVE-V1 § 4.

Phase 2 (cold storage):
    serialize(conv_id) → data/conversations/{conv_id}/{...jsonl}
    Pure disk write; no Graphiti / no nanobot.

Phase 3 (archive flow):
    archive_to_graphiti(archive_path) → unified_filter + LLM → Graphiti
    Driven by IdleArchiveTrigger (PERIODIC) when nanobot is idle.

Schema is documented in DSG-ARCHIVE-V1 § 4.2 (six jsonl files).
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from parrot.dsg.l2b_types import SemanticNode

logger = logging.getLogger(__name__)


# ─── Request / outcome types ─────────────────────────────────────


class ArchiveRequestKind(str, Enum):
    SERIALIZE_NOW = "serialize_now"
    ENQUEUE_FOR_IDLE = "enqueue_for_idle"
    SCAN_AND_ARCHIVE = "scan_and_archive"


class ArchiveTarget(str, Enum):
    CONVERSATION = "conversation"
    EPISODE = "episode"
    SCENE_SNAPSHOT = "scene_snapshot"
    PLAN = "plan"


@dataclass(frozen=True)
class ArchiveRequest:
    """TriggerOutcome upload-channel payload (DSG-TRIGGER-V2 § 3.2)."""

    kind: ArchiveRequestKind
    target: ArchiveTarget
    target_id: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ArchivePath:
    conv_id: str
    base_dir: Path
    files: dict[str, Path] = field(default_factory=dict)


@dataclass
class PendingArchive:
    archive_path: ArchivePath
    target: ArchiveTarget
    target_id: str
    created_at: float
    archived_to_graphiti: bool = False


@dataclass(frozen=True)
class ArchiveOutcome:
    success: bool
    archived_episodes: int = 0
    archived_intent_events: int = 0
    archived_plans: int = 0
    skipped_by_filter: int = 0
    error: str = ""


# ─── UnifiedArchiveFilter (Phase 3 接口；P3 实施) ──────────────


class FilterDecision(str, Enum):
    KEEP = "keep"
    SKIP = "skip"
    SUMMARIZE = "summarize"


@dataclass(frozen=True)
class ArchiveContext:
    target_id: str
    target_kind: ArchiveTarget
    extra: dict[str, Any] = field(default_factory=dict)


class UnifiedArchiveFilter(Protocol):
    """Phase 3 filter Protocol — MemoryValidity hook lives here (P3)."""

    def filter(
        self, node: "SemanticNode", archive_context: ArchiveContext
    ) -> FilterDecision: ...


class KeepAllFilter:
    """Desktop baseline — every node lands in Graphiti (P3 swaps to
    MemoryValidityFilter implementing module_map_p2 § 11.2)."""

    def filter(
        self, node: "SemanticNode", archive_context: ArchiveContext
    ) -> FilterDecision:
        return FilterDecision.KEEP


# ─── ConversationArchive ──────────────────────────────────────────


class ConversationArchive:
    """Disk archive layer + idle-archive queue management."""

    def __init__(
        self, base_path: Path | str = Path("data/conversations"),
    ) -> None:
        self._base = Path(base_path)
        self._idle_filter: UnifiedArchiveFilter = KeepAllFilter()
        self._queue_path = self._base / "_archive_queue.jsonl"

    # ─── Phase 2: serialize ────────────────────────────────────

    async def serialize(self, conv_id: str) -> ArchivePath:
        """Phase 2 — dump current state to disk (no Graphiti).

        Writes the six jsonl files documented in DSG-ARCHIVE-V1 § 4.2.
        Idempotent: re-call overwrites; new markers append on top.
        """
        target_dir = self._base / conv_id
        target_dir.mkdir(parents=True, exist_ok=True)

        files: dict[str, Path] = {}

        # snapshot.json — L2-B node + edge summary
        snapshot_path = target_dir / "snapshot.json"
        snapshot = self._build_snapshot(conv_id)
        snapshot_path.write_text(
            json.dumps(snapshot, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        files["snapshot"] = snapshot_path

        # refs.jsonl — L1.5 RefTable
        refs_path = target_dir / "refs.jsonl"
        self._dump_refs(refs_path)
        files["refs"] = refs_path

        # timeline.jsonl — L1.5 Timeline
        timeline_path = target_dir / "timeline.jsonl"
        try:
            from parrot.dsg.l1_5 import get_l1_5_pool
            get_l1_5_pool().serialize_timeline(timeline_path)
        except Exception:
            timeline_path.write_text("", encoding="utf-8")
        files["timeline"] = timeline_path

        # episodes.jsonl — L2-B EpisodeMarker
        episodes_path = target_dir / "episodes.jsonl"
        self._dump_episodes(episodes_path)
        files["episodes"] = episodes_path

        # intent_events.jsonl — IntentEventBoundary states
        intent_events_path = target_dir / "intent_events.jsonl"
        self._dump_intent_events(intent_events_path)
        files["intent_events"] = intent_events_path

        # plans.jsonl — Plan + PlanStep
        plans_path = target_dir / "plans.jsonl"
        self._dump_plans(plans_path)
        files["plans"] = plans_path

        # intent_workspace_refs.jsonl — StagedRef metadata only
        ws_refs_path = target_dir / "intent_workspace_refs.jsonl"
        self._dump_workspace_refs(ws_refs_path)
        files["intent_workspace_refs"] = ws_refs_path

        # metadata.json — pending_to_graphiti flag
        meta_path = target_dir / "metadata.json"
        meta_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "conv_id": conv_id,
                    "created_at": time.time(),
                    "archived_to_graphiti": False,
                },
                ensure_ascii=False, indent=2,
            ),
            encoding="utf-8",
        )
        files["metadata"] = meta_path

        return ArchivePath(conv_id=conv_id, base_dir=target_dir, files=files)

    # ─── Phase 2 helpers (jsonl dumpers) ───────────────────────

    def _build_snapshot(self, conv_id: str) -> dict:
        try:
            from parrot.dsg.l2b_graph import get_l2b_graph
            graph = get_l2b_graph()
            nodes = graph.all_nodes()
        except Exception:
            nodes = []

        compartments: dict[str, list[str]] = {}
        for n in nodes:
            compartments.setdefault(n.bucket_id or "main", []).append(n.uuid)

        try:
            from parrot.dsg.l1_5 import get_l1_5_pool
            from parrot.dsg.l2b.intent_event_boundary import get_intent_event_handler
            scene = get_l1_5_pool().scenes.current_scene_type().value
            current_event = get_intent_event_handler().current_event_id()
        except Exception:
            scene = ""
            current_event = ""

        return {
            "schema_version": 1,
            "conv_id": conv_id,
            "captured_at": time.time(),
            "node_count": len(nodes),
            "edge_count": graph._graph.num_edges() if nodes else 0,
            "compartments": compartments,
            "current_scene_type": scene,
            "current_intent_event_id": current_event,
        }

    def _dump_refs(self, path: Path) -> None:
        try:
            from parrot.dsg.l1_5 import get_l1_5_pool
            pool = get_l1_5_pool()
            with path.open("w", encoding="utf-8") as f:
                for binding in list(pool.refs._by_ref.values()):
                    f.write(json.dumps({
                        "node_uuid": binding.node_uuid,
                        "kind": binding.kind.value,
                        "ref_value": binding.ref_value,
                        "bound_at": binding.bound_at,
                        "last_verified_at": binding.last_verified_at,
                        "intent_workspace_ref_id": binding.intent_workspace_ref_id,
                    }, ensure_ascii=False) + "\n")
        except Exception:
            path.write_text("", encoding="utf-8")

    def _dump_episodes(self, path: Path) -> None:
        try:
            from parrot.dsg.l2b_graph import get_l2b_graph
            graph = get_l2b_graph()
            with path.open("w", encoding="utf-8") as f:
                for ep in graph._episodes.values():
                    f.write(json.dumps({
                        "episode_id": ep.episode_id,
                        "title": ep.title,
                        "started_at": ep.started_at,
                        "ended_at": ep.ended_at,
                        "summary": ep.summary,
                        "trigger_source": ep.trigger_source,
                        "participating_node_uuids": list(ep.participating_node_uuids),
                        "archived_to_graphiti": ep.archived_to_graphiti,
                    }, ensure_ascii=False) + "\n")
        except Exception:
            path.write_text("", encoding="utf-8")

    def _dump_intent_events(self, path: Path) -> None:
        try:
            from parrot.dsg.l2b.intent_event_boundary import get_intent_event_handler
            handler = get_intent_event_handler()
            with path.open("w", encoding="utf-8") as f:
                for state in handler.list_events():
                    f.write(json.dumps({
                        "event_id": state.event_id,
                        "reason": state.reason.value,
                        "opened_at": state.opened_at,
                        "closed_at": state.closed_at,
                        "member_node_uuids": list(state.member_node_uuids),
                        "triggering_actor": state.triggering_actor,
                        "related_plan_id": state.related_plan_id,
                        "related_episode_id": state.related_episode_id,
                    }, ensure_ascii=False) + "\n")
        except Exception:
            path.write_text("", encoding="utf-8")

    def _dump_plans(self, path: Path) -> None:
        try:
            from parrot.brain.plan import get_plan_registry
            registry = get_plan_registry()
            all_plans = list(registry._active.values()) + list(registry._archive.values())
            with path.open("w", encoding="utf-8") as f:
                for plan in all_plans:
                    f.write(json.dumps({
                        "plan_id": plan.plan_id,
                        "title": plan.title,
                        "rationale": plan.rationale,
                        "state": plan.state.value,
                        "intent_event_id": plan.intent_event_id,
                        "episode_id": plan.episode_id,
                        "drafted_at": plan.drafted_at,
                        "approved_at": plan.approved_at,
                        "completed_at": plan.completed_at,
                        "blocks_conversation": plan.blocks_conversation,
                        "supersedes": plan.supersedes,
                        "superseded_by": plan.superseded_by,
                        "steps": [
                            {
                                "step_id": s.step_id,
                                "title": s.title,
                                "expected_tool": s.expected_tool,
                                "state": s.state.value,
                                "result_summary": s.result_summary,
                                "result_ref_id": s.result_ref_id,
                                "error": s.error,
                                "depends_on": list(s.depends_on),
                            }
                            for s in plan.steps
                        ],
                    }, ensure_ascii=False) + "\n")
        except Exception:
            path.write_text("", encoding="utf-8")

    def _dump_workspace_refs(self, path: Path) -> None:
        try:
            from parrot.brain.intent_workspace import get_intent_workspace
            ws = get_intent_workspace()
            with path.open("w", encoding="utf-8") as f:
                for ref_handle in ws.list_active():
                    f.write(json.dumps({
                        "ref_id": ref_handle.ref_id,
                        "kind": ref_handle.kind.value if ref_handle.kind else None,
                        "metadata": {
                            "origin": ref_handle.metadata.origin,
                            "related_node_uuid": ref_handle.metadata.related_node_uuid,
                            "related_intent_event_id": ref_handle.metadata.related_intent_event_id,
                            "related_plan_id": ref_handle.metadata.related_plan_id,
                            "size_bytes": ref_handle.metadata.size_bytes,
                            "loaded_at": ref_handle.metadata.loaded_at,
                            "last_accessed_at": ref_handle.metadata.last_accessed_at,
                            "expires_at": ref_handle.metadata.expires_at,
                            "auto_evict_on_intent_close": ref_handle.metadata.auto_evict_on_intent_close,
                        },
                    }, ensure_ascii=False) + "\n")
        except Exception:
            path.write_text("", encoding="utf-8")

    # ─── Idle queue ────────────────────────────────────────────

    async def enqueue_for_idle_archive(
        self, target: ArchiveTarget, target_id: str
    ) -> None:
        self._base.mkdir(parents=True, exist_ok=True)
        row = {
            "queued_at": time.time(),
            "target": target.value,
            "target_id": target_id,
        }
        with self._queue_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    def list_pending(self) -> list[PendingArchive]:
        out: list[PendingArchive] = []
        if not self._queue_path.exists():
            return out
        with self._queue_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                    target = ArchiveTarget(row["target"])
                    target_id = row["target_id"]
                    base_dir = self._base / target_id if target == ArchiveTarget.CONVERSATION else self._base
                    out.append(PendingArchive(
                        archive_path=ArchivePath(
                            conv_id=target_id, base_dir=base_dir,
                        ),
                        target=target,
                        target_id=target_id,
                        created_at=row.get("queued_at", 0.0),
                    ))
                except Exception:
                    continue
        return out

    # ─── Phase 3: archive_to_graphiti (skeleton) ──────────────

    async def archive_to_graphiti(
        self, archive_path: ArchivePath
    ) -> ArchiveOutcome:
        """Phase 3 — drive unified_filter + LLM → Graphiti.

        # TODO(Chat4-archive-llm): SKELETON ONLY. Current impl just counts
        #   rows. Chat 4 (interface refinement implementation) must add:
        #     1. Build SemanticNode-shaped objects from each jsonl row
        #     2. Run self._idle_filter.filter(node, ctx) → KEEP/SKIP/SUMMARIZE
        #     3. For KEEP/SUMMARIZE: call LLM (Gemini text) to distill
        #        per-Episode summary
        #     4. Call ``parrot.dsg.l2b_graph.L2BGraph.archive_episode_to_graphiti``
        #        (existing, preserved) for the actual Graphiti.add_episode write
        #     5. Update metadata.json with archived_to_graphiti=True per row
        # See: dsg_protocol_archive_v1_20260506.md § 4 + § 8.1 (UnifiedArchiveFilter
        #   接口已就位；MemoryValidity 真实施 P3).
        """
        try:
            episodes_path = archive_path.files.get(
                "episodes", archive_path.base_dir / "episodes.jsonl",
            )
            archived = 0
            skipped = 0
            if episodes_path.exists():
                with episodes_path.open("r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            row = json.loads(line)
                            ctx = ArchiveContext(
                                target_id=row.get("episode_id", ""),
                                target_kind=ArchiveTarget.EPISODE,
                            )
                            # TODO(Chat4-archive-llm): replace this counter
                            #   with real filter + LLM distillation + Graphiti
                            #   write. See method docstring § 1-5.
                            archived += 1
                            del ctx
                        except Exception:
                            skipped += 1
            return ArchiveOutcome(
                success=True,
                archived_episodes=archived,
                skipped_by_filter=skipped,
            )
        except Exception as e:
            logger.exception("archive_to_graphiti failed")
            return ArchiveOutcome(success=False, error=str(e))

    def set_filter(self, archive_filter: UnifiedArchiveFilter) -> None:
        self._idle_filter = archive_filter


# ─── Singleton + helpers ─────────────────────────────────────────

_archive: ConversationArchive | None = None


def get_conversation_archive() -> ConversationArchive:
    global _archive
    if _archive is None:
        _archive = ConversationArchive()
    return _archive


def set_archive_for_test(archive: ConversationArchive | None) -> None:
    global _archive
    _archive = archive


def enqueue_episode_for_idle_archive(episode_id: str) -> None:
    """Synchronous helper used by ``L2BGraph.start_episode`` (DSG-ARCHIVE-V1 § 5.1)."""
    arch = get_conversation_archive()
    base = arch._base
    base.mkdir(parents=True, exist_ok=True)
    queue_path = arch._queue_path
    row = {
        "queued_at": time.time(),
        "target": ArchiveTarget.EPISODE.value,
        "target_id": episode_id,
    }
    with queue_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


async def dispatch_archive_request(req: ArchiveRequest) -> ArchiveOutcome:
    """TriggerOutcome upload-channel handler (DSG-TRIGGER-V2 § 4)."""
    arch = get_conversation_archive()
    if req.kind == ArchiveRequestKind.SERIALIZE_NOW:
        if req.target == ArchiveTarget.CONVERSATION:
            await arch.serialize(req.target_id)
        else:
            # For non-CONVERSATION targets, fold to current conv first
            await arch.enqueue_for_idle_archive(req.target, req.target_id)
        return ArchiveOutcome(success=True)
    if req.kind == ArchiveRequestKind.ENQUEUE_FOR_IDLE:
        await arch.enqueue_for_idle_archive(req.target, req.target_id)
        return ArchiveOutcome(success=True)
    if req.kind == ArchiveRequestKind.SCAN_AND_ARCHIVE:
        outcomes = []
        for pending in arch.list_pending():
            outcomes.append(await arch.archive_to_graphiti(pending.archive_path))
        return ArchiveOutcome(
            success=True,
            archived_episodes=sum(o.archived_episodes for o in outcomes),
        )
    return ArchiveOutcome(success=False, error=f"unknown kind {req.kind}")


__all__ = [
    "ArchiveContext",
    "ArchiveOutcome",
    "ArchivePath",
    "ArchiveRequest",
    "ArchiveRequestKind",
    "ArchiveTarget",
    "ConversationArchive",
    "FilterDecision",
    "KeepAllFilter",
    "PendingArchive",
    "UnifiedArchiveFilter",
    "dispatch_archive_request",
    "enqueue_episode_for_idle_archive",
    "get_conversation_archive",
    "set_archive_for_test",
]
