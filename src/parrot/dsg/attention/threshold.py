"""Phase 4 临时阈值器 — **不是** DSG L3 完整注意力模块.

Authoritative spec: ``architecture/sprint4_phase4_entry_20260430.md §3.7``
+ §8.1 L9 (Δ weights + threshold values) + §8.1 L13 (naming constraint).

DO NOT rename this module to ``attention.py`` or export an ``Attention`` class
from the package ``__init__``. The point of the awkward ``threshold.py`` name
is to keep the ergonomics of ``parrot.dsg.attention.threshold`` ≠
``parrot.dsg.attention.Attention`` so future readers cannot mistake this
Phase 4 minimal weight-accumulator for the unbuilt DSG L3 注意力模块.

What this module actually does (Phase 4)
----------------------------------------
1. Subscribes to Focus / BBox EcpEvents from
   :class:`parrot.brain.event_ingest.EcpEventIngest`.
2. Maintains a per-correlation_id (= per-attention-target) weight tally:

       weight += Δ_focus  on  ``focus.anchored``
       weight += Δ_bbox   on  ``bbox.placed``
       weight -= Δ_focus  on  ``focus.released``   (cap at 0)
       weight -= Δ_bbox   on  ``bbox.removed``    (cap at 0)

3. When weight ≥ ``threshold``, emit ``attention.threshold.crossed``
   EcpEvent (brain source) and write ``transient/current_attention_hint``
   on the Blackboard.

Phase 4 starter values (locked in §8.1 L9):

    Δ_focus  = 0.2
    Δ_bbox   = 1.0
    threshold = 1.0

Reasoning: 1 BBox direct cross (= "user explicit confirm" hits threshold
immediately); 5 Focuses to cross (= "user inspecting" needs accumulation).
Numbers chosen to be tunable from a Unity ScriptableObject
(``ParrotAttentionConfig``, W6-7) without code changes — see L9 entry-doc
lock. W6-7 real-device tuning may want to drop Δ_bbox below threshold (e.g.
0.8) to leave room for a bbox.removed → re-place hysteresis loop without
oscillation; that is a tuning decision, not a contract change.

What this module deliberately does NOT do
-----------------------------------------
* Does not capture frames (Observer's job).
* Does not write Graphiti (memory.archiver's job).
* Does not write L2-B nodes directly (sibling ``hint_writer`` will, W6-7).
* Does not arbitrate against other attention sources (gesture, gaze, etc.).
* Does not persist weight across sessions (transient by design — closing the
  session is the user-perceptible "I'm not interested anymore" signal).

Phase 5+ migration path
-----------------------
When DSG L3 lands, this module can either be deleted (L3 absorbs the
Focus/BBox path) or kept as a compatibility shim. Either way, the **public
contract** is:

    * EcpEventType inputs (focus.anchored / focus.released / bbox.placed /
      bbox.removed)  — won't change.
    * EcpEventType output (attention.threshold.crossed)  — won't change.
    * BB key (transient/current_attention_hint)  — won't change.

Anything else (internal weight math, per-target dictionaries, the
``FocusBboxThreshold`` class) is implementation-private and Phase 5 may
replace.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

from parrot.brain.event_ingest import EcpEventIngest
from parrot.shared.ecp_event import EcpEvent, EcpEventType


logger = logging.getLogger(__name__)


# BB writer name — must match `bb_schema.py` declaration for
# transient/current_attention_hint (Phase 4 §8.4 reassignment to
# dsg.attention.threshold).
_BB_WRITER = "dsg.attention.threshold"
_BB_KEY_HINT = "transient/current_attention_hint"

# AttentionHint schema_version — embedded in BB payload + EcpEvent payload
# so consumers can detect upgrade. Bump only on field-set change.
_HINT_SCHEMA_VERSION = 1


# ─── Phase 4 starter values (§8.1 L9) ───────────────────────────────────
# Default Δ / threshold. Producers may override at construction time so the
# Unity-side ScriptableObject (W6-7) can inject runtime values via the BB
# `global/attention_thresholds` Echo.
DEFAULT_DELTA_FOCUS: float = 0.2
DEFAULT_DELTA_BBOX: float = 1.0
DEFAULT_THRESHOLD: float = 1.0

# How long a target's weight is retained without new input before being
# evicted. Keeps memory bounded for long sessions where users place + abandon
# many regions. Tuned to "user attention is sticky for ~30s of silence";
# Phase 5+ DSG L3 may replace with a real decay curve.
TARGET_TTL_SECONDS: float = 30.0


@dataclass
class _TargetState:
    """Per-target (per-bbox_id / per-focus_id) accumulator state."""

    weight: float = 0.0
    last_update_ts: float = field(default_factory=time.time)
    crossed: bool = False  # Once crossed, suppress repeat emissions until reset
    label: str = ""  # Human-readable hint (from the originating event payload)
    subject_kind: str = ""  # "bbox" or "focus" — drives Δ pick + hint payload
    subject_id: str = ""  # Unity-side bbox_id or focus_id (correlation key)
    last_event_id: str = ""  # source EcpEvent.event_id of latest weight contribution


class FocusBboxThreshold:
    """Phase 4 minimal Focus/BBox attention weight accumulator.

    Per-instance state is intentionally in-process. If Phase 4 W6-7 reveals a
    real need for cross-process consistency (e.g. multi-Brain shards), the
    fix is to back this with Redis HSET, NOT to start writing weight to BB
    (BB is shared *state*, not algorithm scratch — see §8.1 L9 lock).
    """

    def __init__(
        self,
        *,
        delta_focus: float = DEFAULT_DELTA_FOCUS,
        delta_bbox: float = DEFAULT_DELTA_BBOX,
        threshold: float = DEFAULT_THRESHOLD,
        target_ttl_s: float = TARGET_TTL_SECONDS,
    ) -> None:
        self.delta_focus = delta_focus
        self.delta_bbox = delta_bbox
        self.threshold = threshold
        self.target_ttl_s = target_ttl_s

        # Keyed by correlation_id (= attention target id). Empty
        # correlation_id is treated as "default target" — Phase 4 UI emits
        # one BBox at a time, so a missing correlation_id won't cause cross-
        # contamination, but Phase 5+ multi-target will need correlation_ids
        # populated by the producer.
        self._targets: dict[str, _TargetState] = {}

        # Observability counters (parallel to EcpEventIngest's own counters)
        self.events_processed: int = 0
        self.thresholds_crossed: int = 0
        self.targets_evicted: int = 0

    # ─── ingest hookup ──────────────────────────────────────────────

    def register(self, ingest: EcpEventIngest) -> None:
        """Subscribe to all four Focus/BBox EcpEvents on the given ingest."""
        ingest.subscribe(EcpEventType.FOCUS_ANCHORED, self._on_focus_anchored)
        ingest.subscribe(EcpEventType.FOCUS_RELEASED, self._on_focus_released)
        ingest.subscribe(EcpEventType.BBOX_PLACED, self._on_bbox_placed)
        ingest.subscribe(EcpEventType.BBOX_REMOVED, self._on_bbox_removed)

    # ─── event handlers ─────────────────────────────────────────────

    def _on_focus_anchored(self, event: EcpEvent) -> None:
        self._add_weight(event, +self.delta_focus, subject_kind="focus")

    def _on_focus_released(self, event: EcpEvent) -> None:
        self._add_weight(event, -self.delta_focus, subject_kind="focus")

    def _on_bbox_placed(self, event: EcpEvent) -> None:
        self._add_weight(event, +self.delta_bbox, subject_kind="bbox")

    def _on_bbox_removed(self, event: EcpEvent) -> None:
        self._add_weight(event, -self.delta_bbox, subject_kind="bbox")

    # ─── core math ───────────────────────────────────────────────────

    def _add_weight(
        self,
        event: EcpEvent,
        delta: float,
        *,
        subject_kind: str,
    ) -> None:
        self.events_processed += 1
        self._evict_stale()

        # Prefer Unity-supplied artifact id (bbox_id / focus_id) so two
        # different BBoxes track independently. Fall back to event
        # correlation_id, then to a "_default" bucket so single-target UIs
        # still work without populating either field.
        payload = event.payload or {}
        artifact_key = "bbox_id" if subject_kind == "bbox" else "focus_id"
        subject_id = (
            str(payload.get(artifact_key, "") or "")
            or event.correlation_id
            or "_default"
        )

        state = self._targets.get(subject_id)
        if state is None:
            state = _TargetState(
                label=f"{subject_kind}:{subject_id}",
                subject_kind=subject_kind,
                subject_id=subject_id,
            )
            self._targets[subject_id] = state
        # Defensive: a bbox+focus collision on the same id keeps the kind
        # of whatever wrote first; we don't try to merge cross-kind
        # weights since the UI semantics differ.
        state.weight = max(0.0, state.weight + delta)
        state.last_update_ts = time.time()
        state.last_event_id = event.event_id

        # If a positive delta pushes us across, fire (once). If a negative
        # delta drops us below, allow re-firing the next time we cross.
        if delta > 0 and not state.crossed and state.weight >= self.threshold:
            state.crossed = True
            self._emit_threshold_crossed(subject_id, state, source_event=event)
        elif delta < 0 and state.crossed and state.weight < self.threshold:
            state.crossed = False

    def _emit_threshold_crossed(
        self,
        subject_id: str,
        state: _TargetState,
        *,
        source_event: EcpEvent,
    ) -> None:
        """Phase 4 W6-7 (entry doc §8.1 L9 + §8.4): publish
        ``attention.threshold.crossed`` EcpEvent + write
        ``transient/current_attention_hint`` BB key + delegate L2-B
        candidate-weight bump to ``dsg.attention.hint_writer``.

        Wired three independent fan-out targets, each isolated in its own
        try/except: a failure on one path (e.g. publisher not attached
        during cold-start) does not skip the others.
        """
        self.thresholds_crossed += 1
        logger.info(
            "[attention.threshold] crossed subject=%s weight=%.2f source_event_id=%s",
            subject_id, state.weight, source_event.event_id,
        )

        ref_id = self._lookup_ref_id(state)
        delta = self.delta_bbox if state.subject_kind == "bbox" else self.delta_focus

        hint_payload = {
            "schema_version": _HINT_SCHEMA_VERSION,
            "ref_id": ref_id,
            "weight": state.weight,
            "subject_kind": state.subject_kind,
            "subject_id": state.subject_id,
            "label": state.label,
            "delta_applied": delta,
            "source_event_id": source_event.event_id,
            "ts_ms": int(time.time() * 1000),
        }

        # 1) Publish attention.threshold.crossed EcpEvent (brain source).
        self._publish_attention_event(
            payload=hint_payload, source_event=source_event,
        )

        # 2) Write transient/current_attention_hint BB key.
        self._write_bb_attention_hint(hint_payload)

        # 3) Delegate L2-B candidate-weight bump to hint_writer (no-op when
        # ref is UNRESOLVED, which is the common case at threshold time).
        self._dispatch_to_hint_writer(ref_id=ref_id, delta=delta)

    # ─── fan-out helpers ────────────────────────────────────────────

    def _lookup_ref_id(self, state: _TargetState) -> str:
        """Find the RefBinding ref_id corresponding to this state's
        Unity-side artifact id. Returns "" if none registered yet — the
        subscriber may have not landed before the threshold crossed
        (race), in which case downstream still gets a useful hint via
        subject_kind / subject_id, just no Ref handle.
        """
        try:
            from parrot.brain import refs as refs_registry
        except Exception:
            return ""

        if state.subject_kind == "bbox":
            ref = refs_registry.get_ref_by_bbox(state.subject_id)
        else:
            ref = refs_registry.get_ref_by_focus(state.subject_id)
        return ref.ref_id if ref is not None else ""

    def _publish_attention_event(
        self,
        *,
        payload: dict[str, Any],
        source_event: EcpEvent,
    ) -> None:
        try:
            from parrot.brain.event_publisher import get_ecp_event_publisher
        except Exception:
            return
        publisher = get_ecp_event_publisher()
        if publisher is None:
            return
        try:
            event = publisher.make_brain_event(
                event_type=EcpEventType.ATTENTION_THRESHOLD_CROSSED,
                payload=payload,
                correlation_id=source_event.event_id,
            )
            publisher.publish_nowait(event)
        except Exception:
            logger.debug(
                "[attention.threshold] publish_nowait failed", exc_info=True,
            )

    def _write_bb_attention_hint(self, payload: dict[str, Any]) -> None:
        try:
            from parrot.scheduler.blackboard import open_bb_client
        except Exception:
            return
        try:
            bb = open_bb_client(name="attention_threshold", writer=_BB_WRITER)
            bb.set(_BB_KEY_HINT, payload)
        except Exception:
            logger.debug(
                "[attention.threshold] BB write failed", exc_info=True,
            )

    def _dispatch_to_hint_writer(self, *, ref_id: str, delta: float) -> None:
        if not ref_id:
            return
        try:
            from parrot.brain import refs as refs_registry
            from parrot.dsg.attention.hint_writer import bump_l2b_for_resolved_ref
        except Exception:
            return
        ref = refs_registry.get_ref(ref_id)
        if ref is None:
            return
        try:
            bump_l2b_for_resolved_ref(ref, delta=delta)
        except Exception:
            logger.debug(
                "[attention.threshold] hint_writer bump failed", exc_info=True,
            )

    # ─── housekeeping ───────────────────────────────────────────────

    def _evict_stale(self) -> None:
        now = time.time()
        cutoff = now - self.target_ttl_s
        stale = [k for k, s in self._targets.items() if s.last_update_ts < cutoff]
        for k in stale:
            del self._targets[k]
            self.targets_evicted += 1

    def metrics_snapshot(self) -> dict[str, Any]:
        return {
            "events_processed": self.events_processed,
            "thresholds_crossed": self.thresholds_crossed,
            "targets_evicted": self.targets_evicted,
            "active_targets": len(self._targets),
        }


__all__ = [
    "DEFAULT_DELTA_BBOX",
    "DEFAULT_DELTA_FOCUS",
    "DEFAULT_THRESHOLD",
    "FocusBboxThreshold",
    "TARGET_TTL_SECONDS",
]
