"""L1.5 Pool — singleton management plane orchestrator.

DSG-POOL-V1 § 1, § 2.

L15Pool aggregates the four sub-modules (BucketRegistry / RefTable /
Timeline / SceneRegistry) and the AdmissionPolicy strategy into a
single management-plane facade. It does NOT own SemanticNode bytes —
those live in ``parrot.dsg.l2b_graph.L2BGraph``. L15Pool's role is:
    1. Gatekeep observations entering the L2-B graph (admission)
    2. Track which Bucket each node belongs to
    3. Maintain Ref bindings (lightweight UUID/path → node lookup)
    4. Append Timeline markers (cognitive boundaries / lifecycle events)
    5. Manage Scene switches (freeze authority buckets, clear fresh)

Invariants:
    - Ingest is still the only L2-B write gate (preload excepted).
    - L15Pool delegates the actual node creation / merge logic to the
      existing IngestRunner (which is now wrapped under .admit()).
    - Heavy payloads (large files) live in ``parrot.brain.intent_workspace``
      (BRAIN-INTENT-WS-V1); L15Pool only stores the lightweight ref.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any

from parrot.dsg.l1_5.admission import (
    AdmissionContext,
    PoolAdmissionPolicy,
    get_admission_policy,
)
from parrot.dsg.l1_5.buckets import (
    BucketHandle,
    BucketKind,
    BucketOp,
    BucketOpKind,
    BucketOpResult,
    BucketRegistry,
    BucketSpec,
)
from parrot.dsg.l1_5.ref_table import (
    RefBinding,
    RefHealth,
    RefHealthStatus,
    RefKind,
    RefTable,
)
from parrot.dsg.l1_5.scene_snapshot import (
    SceneProfile,
    SceneRegistry,
    SceneSwitchOutcome,
    SceneType,
)
from parrot.dsg.l1_5.timeline import (
    Timeline,
    TimelineMarker,
    TimelineMarkerKind,
)

if TYPE_CHECKING:
    from parrot.dsg.ingest.base import Observation

logger = logging.getLogger(__name__)


# ─── Outcome / reason types ──────────────────────────────────────────


class AdmitRejectReason(str, Enum):
    BELOW_CONFIDENCE = "below_confidence"
    BLOCKED_BY_MODE = "blocked_by_mode"
    BLOCKED_BY_BUCKET_FROZEN = "bucket_frozen"
    DUPLICATE_IDEMPOTENT = "duplicate_idempotent"
    IMPOSSIBLE_EVENT = "impossible_event"
    POOL_AT_CAPACITY = "pool_at_capacity"
    UNKNOWN_BUCKET = "unknown_bucket"
    POLICY_REJECTED = "policy_rejected"


@dataclass(frozen=True)
class RejectedObservation:
    obs_id: str
    reason: AdmitRejectReason
    detail: str = ""


@dataclass(frozen=True)
class AdmitOutcome:
    admitted_node_uuids: tuple[str, ...] = ()
    rejected: tuple[RejectedObservation, ...] = ()
    promoted: tuple[str, ...] = ()
    bucket_assignments: dict[str, BucketKind] = field(default_factory=dict)


class EvictReason(str, Enum):
    TTL_EXPIRED = "ttl_expired"
    BUCKET_CLEARED = "bucket_cleared"
    SCENE_SWITCHED = "scene_switched"
    EXPLICIT = "explicit"
    GHOST_TRANSITION = "ghost_transition"


class PoolCapacityPressure(str, Enum):
    OK = "ok"
    WATCH = "watch"
    WARN = "warn"
    CRITICAL = "critical"


@dataclass(frozen=True)
class PoolHealthReport:
    total_nodes: int
    nodes_per_bucket: dict[BucketKind, int]
    refs_total: int
    refs_health_distribution: dict[RefHealthStatus, int]
    timeline_marker_count: int
    current_scene: str
    capacity_pressure: PoolCapacityPressure


# ─── L15Pool ────────────────────────────────────────────────────────


class L15Pool:
    """L1.5 management-plane singleton."""

    def __init__(
        self,
        admission_policy: PoolAdmissionPolicy | None = None,
    ) -> None:
        self._buckets = BucketRegistry()
        self._refs = RefTable()
        self._timeline = Timeline()
        self._scenes = SceneRegistry()
        self._policy = admission_policy or get_admission_policy()

    # ─── Sub-module accessors (testable in isolation) ──────────────

    @property
    def buckets(self) -> BucketRegistry:
        return self._buckets

    @property
    def refs(self) -> RefTable:
        return self._refs

    @property
    def timeline(self) -> Timeline:
        return self._timeline

    @property
    def scenes(self) -> SceneRegistry:
        return self._scenes

    # ─── Admission / Eviction ───────────────────────────────────────

    async def admit(
        self,
        observations: tuple["Observation", ...],
        *,
        target_bucket: BucketKind | None = None,
        ctx: AdmissionContext | None = None,
    ) -> AdmitOutcome:
        """Submit a batch of Observations to the pool.

        Path:
            1. AdmissionPolicy.evaluate(obs, ctx) → AdmitDecision
            2. Bucket assignment (target_bucket override OR decision)
            3. Delegate to IngestRunner for actual L2-B commit (existing
               _find_existing / _merge / _observation_to_node logic
               continues to work; we just record bucket assignment).
            4. Update BucketRegistry node_uuid set
            5. Bind ref via RefTable when obsidian_uuid / graphiti_uuid
               present
            6. Mark timeline (single AUTONOMOUS_CURIOSITY marker if
               source=GOSLO_AUTONOMOUS; otherwise lazy)
        """
        # Lazy import to break runner ↔ pool cycle
        from parrot.dsg.ingest.base import ObservationSource
        from parrot.dsg.ingest.runner import IngestRunner, get_ingest_runner

        ctx = ctx or AdmissionContext(current_scene=self._scenes.current_profile())
        runner: IngestRunner = get_ingest_runner()

        admitted: list[str] = []
        promoted: list[str] = []
        rejected: list[RejectedObservation] = []
        assignments: dict[str, BucketKind] = {}

        for obs in observations:
            decision = self._policy.evaluate(obs, ctx)
            bucket = target_bucket or decision.target_bucket

            # Obsidian profile=ref is normally a lightweight strengthening
            # link, not a new L2-B node. Operator-selected UUID-free ref diary
            # notes set ref_mode=direct_context; those continue through the
            # normal commit path so the note becomes visible to L2-B and the
            # high-priority context channel without pretending it has a stable
            # RefBinding target.
            if (
                obs.source == ObservationSource.USER_TAG_OBSIDIAN
                and (obs.meta or {}).get("profile") == "ref"
                and (obs.meta or {}).get("ref_mode") != "direct_context"
            ):
                ref_node_uuid = self._bind_obsidian_ref_observation(obs, runner)
                if ref_node_uuid:
                    promoted.append(ref_node_uuid)
                else:
                    rejected.append(RejectedObservation(
                        obs_id=obs.obs_id,
                        reason=AdmitRejectReason.POLICY_REJECTED,
                        detail=(
                            "obsidian profile=ref requires an existing target "
                            "node matched by target_node_uuid, obsidian_uuid, "
                            "graphiti_uuid, or label"
                        ),
                    ))
                continue

            # Bucket frozen / unknown gate
            handle = self._buckets.get(bucket)
            if handle is None:
                rejected.append(RejectedObservation(
                    obs_id=obs.obs_id,
                    reason=AdmitRejectReason.UNKNOWN_BUCKET,
                    detail=f"bucket {bucket} not registered",
                ))
                continue
            if handle.frozen:
                rejected.append(RejectedObservation(
                    obs_id=obs.obs_id,
                    reason=AdmitRejectReason.BLOCKED_BY_BUCKET_FROZEN,
                    detail=f"bucket {bucket.value} frozen",
                ))
                continue

            if not decision.admit:
                try:
                    reason_enum = AdmitRejectReason(decision.reject_reason)
                except ValueError:
                    reason_enum = AdmitRejectReason.POLICY_REJECTED
                rejected.append(RejectedObservation(
                    obs_id=obs.obs_id,
                    reason=reason_enum,
                    detail=decision.notes,
                ))
                continue

            # Delegate to IngestRunner for actual node commit. The
            # runner is the historical owner of merge / 30s-promotion /
            # source authority comparison; we keep that path intact.
            changed = await runner.commit_observation(obs)

            # Locate the node we just touched (by label / uuid) so we
            # can stamp bucket_id and record the assignment.
            node = self._locate_node(obs, runner)
            if node is None:
                # commit succeeded but node lookup raced — log + skip
                # bookkeeping; the L2-B graph is still consistent.
                if changed:
                    admitted.append("")  # opaque marker
                continue

            node.bucket_id = bucket.value
            node.scene_type = self._scenes.current_scene_type().value
            if not node.location_tag:
                node.location_tag = self._scenes.current_profile().location_default
            if ctx.current_intent_event_id and not node.event_id:
                node.event_id = ctx.current_intent_event_id

            if decision.salience_override is not None:
                node.salience = decision.salience_override
            if decision.confirmation_override is not None:
                node.confirmation = decision.confirmation_override

            self._buckets.add_node(bucket, node.uuid)
            assignments[node.uuid] = bucket

            # Bind refs from obsidian_uuid / graphiti_uuid if present
            if obs.obsidian_uuid:
                self._refs.bind_ref(
                    node.uuid, RefKind.OBSIDIAN_UUID, obs.obsidian_uuid,
                )
            if obs.graphiti_uuid:
                self._refs.bind_ref(
                    node.uuid, RefKind.GRAPHITI_UUID, obs.graphiti_uuid,
                )
            if obs.reference_image_path:
                self._refs.bind_ref(
                    node.uuid, RefKind.PHOTO_PATH, obs.reference_image_path,
                )
            if obs.source == ObservationSource.GOOGLE_CALENDAR:
                ref_value = self._google_calendar_ref_value(obs)
                if ref_value:
                    self._refs.bind_ref(node.uuid, RefKind.OTHER, ref_value)
            if obs.source == ObservationSource.GOOGLE_MESSAGE:
                ref_value = self._google_message_ref_value(obs)
                if ref_value:
                    self._refs.bind_ref(node.uuid, RefKind.OTHER, ref_value)

            if changed:
                admitted.append(node.uuid)

            # Curiosity marker for traceability
            if obs.source == ObservationSource.GOSLO_AUTONOMOUS:
                self._timeline.mark(
                    TimelineMarkerKind.AUTONOMOUS_CURIOSITY,
                    payload={"label": obs.label, "obs_id": obs.obs_id},
                    related_node_uuids=(node.uuid,),
                )

        return AdmitOutcome(
            admitted_node_uuids=tuple(admitted),
            rejected=tuple(rejected),
            promoted=tuple(promoted),
            bucket_assignments=assignments,
        )

    @staticmethod
    def _locate_node(obs: "Observation", runner: Any):
        """Best-effort lookup of the node we just committed."""
        try:
            graph = runner._graph
            if graph is None:
                return None
            if obs.source.value == "google_calendar":
                ref_value = L15Pool._google_calendar_ref_value(obs)
                if ref_value:
                    _, calendar_id, event_id = ref_value.split(":", 2)
                    for n in graph.all_nodes():
                        meta = n.source_meta or {}
                        if (
                            meta.get("calendar_id", "primary") == calendar_id
                            and meta.get("calendar_event_id") == event_id
                        ):
                            return n
            if obs.source.value == "google_message":
                ref_value = L15Pool._google_message_ref_value(obs)
                if ref_value:
                    _, message_id = ref_value.split(":", 1)
                    for n in graph.all_nodes():
                        meta = n.source_meta or {}
                        if meta.get("message_id") == message_id:
                            return n
            if obs.obsidian_uuid:
                for n in graph.all_nodes():
                    if n.obsidian_uuid == obs.obsidian_uuid:
                        return n
            if obs.graphiti_uuid:
                for n in graph.all_nodes():
                    if n.graphiti_uuid == obs.graphiti_uuid:
                        return n
            # Match the ingest runner fallback: label is scoped by NodeKind,
            # not a graph-wide unique key. Stable provider identities above
            # remain the preferred lookup path.
            return graph.get_node_by_label_and_kind(obs.label, obs.kind)
        except Exception:
            return None

    def _bind_obsidian_ref_observation(
        self,
        obs: "Observation",
        runner: Any,
    ) -> str:
        """Bind an Obsidian reference note to an existing L2-B node.

        ``profile=ref`` notes are documentation/strengthening refs. They must
        not create a new node or enter an authority bucket. The binding is
        intentionally lightweight: RefTable owns the UUID lookup, and the node
        gets only trace metadata so future health/status views can show which
        Obsidian file strengthened it.
        """
        try:
            graph = runner._graph
            if graph is None or not obs.obsidian_uuid:
                return ""

            meta = obs.meta or {}
            target_node_uuid = str(meta.get("target_node_uuid", "") or "")
            node = graph.get_node(target_node_uuid) if target_node_uuid else None

            if node is None and obs.graphiti_uuid:
                for candidate in graph.all_nodes():
                    if candidate.graphiti_uuid == obs.graphiti_uuid:
                        node = candidate
                        break

            if node is None and obs.obsidian_uuid:
                for candidate in graph.all_nodes():
                    if candidate.obsidian_uuid == obs.obsidian_uuid:
                        node = candidate
                        break

            if node is None:
                node = graph.get_node_by_label_and_kind(obs.label, obs.kind)

            if node is None:
                return ""

            if not node.obsidian_uuid:
                node.obsidian_uuid = obs.obsidian_uuid
            node.source_meta.setdefault("obsidian_ref_profile", "ref")
            node.source_meta.setdefault("obsidian_refs", [])
            refs = node.source_meta["obsidian_refs"]
            if isinstance(refs, list) and obs.obsidian_uuid not in refs:
                refs.append(obs.obsidian_uuid)
            if meta.get("obsidian_path"):
                node.source_meta["obsidian_path"] = meta["obsidian_path"]

            self._refs.bind_ref(node.uuid, RefKind.OBSIDIAN_UUID, obs.obsidian_uuid)
            return node.uuid
        except Exception:
            logger.exception("L15Pool: obsidian ref binding failed")
            return ""

    @staticmethod
    def _google_calendar_ref_value(obs: "Observation") -> str:
        """Return the lightweight RefTable key for a Google Calendar event."""
        meta = obs.meta or {}
        event_id = str(meta.get("calendar_event_id", "") or "")
        if not event_id:
            return ""
        calendar_id = str(meta.get("calendar_id", "primary") or "primary")
        return f"google_calendar:{calendar_id}:{event_id}"

    @staticmethod
    def _google_message_ref_value(obs: "Observation") -> str:
        """Return the lightweight RefTable key for a Google/Gmail message."""
        message_id = str((obs.meta or {}).get("message_id", "") or "")
        if not message_id:
            return ""
        return f"google_message:{message_id}"

    async def evict(self, node_uuid: str, reason: EvictReason) -> bool:
        """Remove a node from the L2-B graph and clean up bookkeeping."""
        try:
            from parrot.dsg.l2b_graph import get_l2b_graph
        except ImportError:
            logger.warning("L15Pool.evict: l2b_graph unavailable")
            return False

        graph = get_l2b_graph()
        bucket_kind = self._buckets.find_bucket_of_node(node_uuid)
        if bucket_kind is not None:
            self._buckets.remove_node(bucket_kind, node_uuid)

        self._refs.unbind_all_for_node(node_uuid)
        graph.remove_node(node_uuid)

        self._timeline.mark(
            TimelineMarkerKind.BUCKET_OP,
            payload={
                "op": "evict",
                "reason": reason.value,
                "bucket": bucket_kind.value if bucket_kind else "",
            },
            related_node_uuids=(node_uuid,),
        )
        return True

    # ─── Bucket management ──────────────────────────────────────────

    def register_bucket(self, spec: BucketSpec) -> BucketHandle:
        return self._buckets.register(spec)

    def get_bucket(self, kind: BucketKind) -> BucketHandle | None:
        return self._buckets.get(kind)

    def list_buckets(self, only_unfrozen: bool = False) -> list[BucketHandle]:
        return self._buckets.list(only_unfrozen=only_unfrozen)

    async def import_bucket(
        self, kind: BucketKind, items: tuple["Observation", ...]
    ) -> AdmitOutcome:
        return await self.admit(items, target_bucket=kind)

    async def freeze_bucket(self, kind: BucketKind) -> bool:
        ok = self._buckets.freeze(kind)
        if ok:
            self._timeline.mark(
                TimelineMarkerKind.BUCKET_OP,
                payload={"op": "freeze", "bucket": kind.value},
            )
        return ok

    async def unfreeze_bucket(self, kind: BucketKind) -> bool:
        ok = self._buckets.unfreeze(kind)
        if ok:
            self._timeline.mark(
                TimelineMarkerKind.BUCKET_OP,
                payload={"op": "unfreeze", "bucket": kind.value},
            )
        return ok

    async def clear_bucket(self, kind: BucketKind) -> int:
        evicted_uuids = self._buckets.clear(kind)
        for uuid in evicted_uuids:
            await self.evict(uuid, EvictReason.BUCKET_CLEARED)
        self._timeline.mark(
            TimelineMarkerKind.BUCKET_OP,
            payload={
                "op": "clear",
                "bucket": kind.value,
                "evicted": len(evicted_uuids),
            },
        )
        return len(evicted_uuids)

    async def apply_bucket_op(self, op: BucketOp) -> BucketOpResult:
        """TriggerOutcome upload-channel entry point (DSG-TRIGGER-V2 § 4)."""
        try:
            if op.op == BucketOpKind.REGISTER:
                spec = op.payload.get("spec")
                if spec is None:
                    spec = BucketSpec(kind=op.kind)
                handle = self.register_bucket(spec)
                return BucketOpResult(op=op, success=True, bucket_handle=handle)
            if op.op == BucketOpKind.IMPORT:
                items = tuple(op.payload.get("items", ()))
                outcome = await self.import_bucket(op.kind, items)
                return BucketOpResult(
                    op=op,
                    success=True,
                    bucket_handle=self.get_bucket(op.kind),
                    affected_nodes=len(outcome.admitted_node_uuids),
                )
            if op.op == BucketOpKind.FREEZE:
                ok = await self.freeze_bucket(op.kind)
                return BucketOpResult(
                    op=op, success=ok,
                    bucket_handle=self.get_bucket(op.kind),
                )
            if op.op == BucketOpKind.UNFREEZE:
                ok = await self.unfreeze_bucket(op.kind)
                return BucketOpResult(
                    op=op, success=ok,
                    bucket_handle=self.get_bucket(op.kind),
                )
            if op.op == BucketOpKind.CLEAR:
                affected = await self.clear_bucket(op.kind)
                return BucketOpResult(
                    op=op, success=True,
                    bucket_handle=self.get_bucket(op.kind),
                    affected_nodes=affected,
                )
            if op.op == BucketOpKind.UNREGISTER:
                ok = self._buckets.unregister(op.kind)
                return BucketOpResult(op=op, success=ok)
            return BucketOpResult(
                op=op, success=False, error=f"unknown op {op.op}",
            )
        except Exception as e:
            logger.exception("L15Pool.apply_bucket_op failed")
            return BucketOpResult(op=op, success=False, error=str(e))

    # ─── Ref table passthroughs ─────────────────────────────────────

    def bind_ref(
        self,
        node_uuid: str,
        kind: RefKind,
        ref_value: str,
        intent_workspace_ref_id: str = "",
    ) -> RefBinding:
        return self._refs.bind_ref(node_uuid, kind, ref_value, intent_workspace_ref_id)

    def lookup_by_ref(self, kind: RefKind, ref_value: str) -> str | None:
        return self._refs.lookup_by_ref(kind, ref_value)

    def list_refs_of_node(self, node_uuid: str) -> list[RefBinding]:
        return self._refs.list_refs_of_node(node_uuid)

    async def verify_ref(self, binding: RefBinding) -> RefHealth:
        return await self._refs.verify_ref(binding)

    async def ref_health_report(
        self, kinds: frozenset[RefKind] | None = None
    ) -> list[RefHealth]:
        return await self._refs.ref_health_report(kinds)

    def unbind_ref(self, binding: RefBinding) -> bool:
        return self._refs.unbind_ref(binding.kind, binding.ref_value)

    def clear_intent_workspace_ref(self, ws_ref_id: str) -> int:
        return self._refs.clear_intent_workspace_ref(ws_ref_id)

    # ─── Timeline passthroughs ──────────────────────────────────────

    def mark(
        self,
        kind: TimelineMarkerKind,
        ts: float | None = None,
        payload: dict[str, Any] | None = None,
        related_node_uuids: tuple[str, ...] = (),
    ) -> TimelineMarker:
        return self._timeline.mark(kind, ts, payload, related_node_uuids)

    def get_timeline(
        self,
        window: tuple[float, float] | None = None,
        kinds: frozenset[TimelineMarkerKind] | None = None,
    ) -> list[TimelineMarker]:
        return self._timeline.get_timeline(window, kinds)

    def serialize_timeline(self, dst):
        from pathlib import Path
        return self._timeline.serialize_timeline(Path(dst))

    # ─── Scene management ───────────────────────────────────────────

    def current_scene(self) -> SceneProfile:
        return self._scenes.current_profile()

    async def switch_scene(self, new_scene_type: SceneType) -> SceneSwitchOutcome:
        """Switch SceneType. Detailed flow in DSG-SCENE-V1 § 3."""
        old_type = self._scenes.current_scene_type()
        if old_type == new_scene_type:
            return SceneSwitchOutcome(
                old_scene_type=old_type,
                new_scene_type=new_scene_type,
                switched_at=time.time(),
                success=True,
            )

        new_profile = self._scenes.get(new_scene_type)
        if new_profile is None:
            return SceneSwitchOutcome(
                old_scene_type=old_type,
                new_scene_type=new_scene_type,
                switched_at=time.time(),
                success=False,
                errors=(f"SceneType {new_scene_type.value} not registered",),
            )

        old_profile = self._scenes.current_profile()
        preserved: list = []
        cleared: list = []
        affected = 0

        # Freeze authority / preserved buckets, clear fresh ones
        for kind in new_profile.preserved_bucket_kinds:
            handle = self._buckets.get(kind)
            if handle and handle.spec.is_authority:
                if await self.freeze_bucket(kind):
                    preserved.append(kind)
            elif handle:
                preserved.append(kind)

        for kind in new_profile.fresh_bucket_kinds:
            n = await self.clear_bucket(kind)
            cleared.append(kind)
            affected += n

        self._scenes.set_current(new_scene_type)

        self._timeline.mark(
            TimelineMarkerKind.SCENE_SWITCHED,
            payload={
                "old": old_type.value,
                "new": new_scene_type.value,
                "preserved": [k.value for k in preserved],
                "cleared": [k.value for k in cleared],
                "affected_nodes": affected,
            },
        )

        return SceneSwitchOutcome(
            old_scene_type=old_type,
            new_scene_type=new_scene_type,
            switched_at=time.time(),
            preserved_buckets=tuple(preserved),
            cleared_buckets=tuple(cleared),
            affected_node_count=affected,
            dsg_mode_change=(old_profile.dsg_mode, new_profile.dsg_mode),
            video_tier_change=(old_profile.video_tier_hint, new_profile.video_tier_hint),
            success=True,
        )

    # ─── Health ─────────────────────────────────────────────────────

    def health(self) -> PoolHealthReport:
        per_bucket = {h.spec.kind: len(h.node_uuids) for h in self._buckets.list()}
        total = sum(per_bucket.values())
        # Desktop baseline: never flag pressure
        return PoolHealthReport(
            total_nodes=total,
            nodes_per_bucket=per_bucket,
            refs_total=self._refs.total_bindings(),
            refs_health_distribution={},  # populated by health_report() async
            timeline_marker_count=self._timeline.count(),
            current_scene=self._scenes.current_scene_type().value,
            capacity_pressure=PoolCapacityPressure.OK,
        )


# ─── Singleton + test injection ─────────────────────────────────────

_pool: L15Pool | None = None


def get_l1_5_pool() -> L15Pool:
    global _pool
    if _pool is None:
        _pool = L15Pool()
    return _pool


def set_pool_for_test(pool: L15Pool | None) -> None:
    global _pool
    _pool = pool


__all__ = [
    "AdmitOutcome",
    "AdmitRejectReason",
    "EvictReason",
    "L15Pool",
    "PoolCapacityPressure",
    "PoolHealthReport",
    "RejectedObservation",
    "get_l1_5_pool",
    "set_pool_for_test",
]
