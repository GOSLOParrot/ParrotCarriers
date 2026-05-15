"""Visual-tool evidence lifecycle for App BBox and Magnifier tools.

This module is intentionally not the DSG/L3 attention system.  It defines a
small, auditable contract for App UI tools to report interaction milestones
that produce visual evidence: BBox is a strong "look here" tool, while MAG is
a weaker focus/magnifier tool.  The backend owns the delivery policy so Unity
can keep animation and gesture feel local without guessing when GOSLO should
be notified.

Images are never embedded in ECP events.  A tool may attach ``asset_path`` or
``asset_uri`` after it uploads a crop/rendered preview through HTTP/storage; if
not, the lifecycle sample still anchors the time/region so frame-cache or SVA
workers can attach the nearest image later.
"""

from __future__ import annotations

import asyncio
import datetime
import logging
import os
import time
import uuid as uuid_lib
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from threading import RLock
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from parrot.brain import refs as refs_registry
from parrot.brain.vision.evidence import (
    ClockDomain,
    EvidenceKind,
    EvidenceStatus,
    SampleRegion,
    TimeAlignedSampleRef,
    TimebaseStamp,
    get_evidence_ledger,
)
from parrot.brain.vision.evidence_awareness import (
    EvidenceAwarenessDecision,
    stage_sample_for_goslo,
)
from parrot.scheduler.blackboard import open_bb_client

logger = logging.getLogger(__name__)

_BB_WRITER = "brain.vision.tool_lifecycle"
_BB_KEY_RECEIPT = "transient/visual_tool_lifecycle_receipt"
_ASSET_ROOT_ENV = "PARROT_VISUAL_TOOL_ASSET_ROOT"
_DEFAULT_ASSET_ROOT = "data/visual_tools"
_MAX_ASSET_BYTES = 10 * 1024 * 1024
_FORBIDDEN_PATH_CHARS = ("/", "\\", "..", "\0", " ", "\t", "\n", "\r")


class VisualToolKind(str, Enum):
    """App-side tool family.

    ``MAG`` and ``FOCUS`` both map to Focus RefBinding in V1.  Keeping them as
    distinct tool kinds lets the UI and receipts preserve user intent without
    adding a new shared ``RefKind`` before App/Web agree on it.
    """

    BBOX = "bbox"
    MAG = "mag"
    FOCUS = "focus"


class VisualToolPhase(str, Enum):
    """Stable interaction milestones emitted by App controllers."""

    PREVIEW_START = "preview_start"
    HOVER = "hover"
    DRAG_UPDATE = "drag_update"
    RESIZE_UPDATE = "resize_update"
    DWELL_TICK = "dwell_tick"
    LOCK = "lock"
    UNLOCK = "unlock"
    SETTINGS_OPEN = "settings_open"
    CONFIRM = "confirm"
    EXPLICIT_SEND = "explicit_send"
    CANCEL = "cancel"
    RELEASE = "release"


class VisualToolDeliveryPreference(str, Enum):
    """Requested notification level for a lifecycle event."""

    DEFAULT = "default"
    SILENT = "silent"
    INTENT_ONLY = "intent_only"
    C3 = "c3"
    C4 = "c4"


class VisualToolLifecyclePacket(BaseModel):
    """Validated payload accepted by HTTP route and ECP event."""

    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    schema_version: int = Field(default=1, ge=1, le=5)
    tool_event_id: str = Field(
        default_factory=lambda: f"vtool_{int(time.time() * 1000)}_{uuid_lib.uuid4().hex[:8]}",
        max_length=96,
    )
    tool_id: str = Field(min_length=1, max_length=128)
    tool_kind: VisualToolKind
    interaction_phase: VisualToolPhase
    region: SampleRegion | None = None
    pose: dict[str, Any] = Field(default_factory=dict)
    source_surface: str = Field(default="app_ar_overlay", max_length=96)
    timebase: dict[str, Any] = Field(default_factory=dict)
    asset_ref: str = Field(default="", max_length=512)
    asset_path: str = Field(default="", max_length=1024)
    asset_uri: str = Field(default="", max_length=1024)
    mime_type: str = Field(default="", max_length=96)
    evidence_id: str = Field(default="", max_length=128)
    attention_hint: float = Field(default=0.0, ge=0.0, le=2.0)
    delivery_preference: VisualToolDeliveryPreference = VisualToolDeliveryPreference.DEFAULT
    subject_hint: str = Field(default="", max_length=256)
    label: str = Field(default="", max_length=256)
    meta: dict[str, Any] = Field(default_factory=dict)

    @field_validator("tool_event_id")
    @classmethod
    def _default_event_id(cls, value: str) -> str:
        return value or f"vtool_{int(time.time() * 1000)}_{uuid_lib.uuid4().hex[:8]}"


class VisualToolReceipt(BaseModel):
    """App/Web receipt for one visual-tool lifecycle event."""

    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    action: str = "vision.tool.lifecycle"
    success: bool
    receipt_id: str = Field(default_factory=lambda: f"vtool_rcpt_{uuid_lib.uuid4().hex[:12]}")
    error: str = ""
    packet: dict[str, Any] = Field(default_factory=dict)
    ref_id: str = ""
    ref_kind: str = ""
    evidence: dict[str, Any] = Field(default_factory=dict)
    staged_ref_id: str = ""
    salience: dict[str, Any] = Field(default_factory=dict)
    delivery: dict[str, Any] = Field(default_factory=dict)
    awareness: dict[str, Any] = Field(default_factory=dict)
    audit: dict[str, Any] = Field(default_factory=dict)

    def as_json(self) -> dict[str, Any]:
        return self.model_dump(mode="json")


@dataclass
class _VisualToolState:
    tool_id: str
    tool_kind: str
    ref_id: str = ""
    salience: float = 0.0
    locked: bool = False
    latest_evidence_id: str = ""
    latest_phase: str = ""
    updated_at_ms: int = 0


_STATE_LOCK = RLock()
_STATES: dict[str, _VisualToolState] = {}

_PHASE_DELTA: dict[VisualToolPhase, float] = {
    VisualToolPhase.PREVIEW_START: 0.08,
    VisualToolPhase.HOVER: 0.02,
    VisualToolPhase.DRAG_UPDATE: 0.04,
    VisualToolPhase.RESIZE_UPDATE: 0.04,
    VisualToolPhase.DWELL_TICK: 0.12,
    VisualToolPhase.LOCK: 0.35,
    VisualToolPhase.UNLOCK: -0.20,
    VisualToolPhase.SETTINGS_OPEN: 0.0,
    VisualToolPhase.CONFIRM: 1.10,
    VisualToolPhase.EXPLICIT_SEND: 1.25,
    VisualToolPhase.CANCEL: -1.00,
    VisualToolPhase.RELEASE: -0.60,
}

_KIND_MULTIPLIER: dict[VisualToolKind, float] = {
    VisualToolKind.BBOX: 1.0,
    VisualToolKind.MAG: 0.45,
    VisualToolKind.FOCUS: 0.50,
}

_INTENT_STAGE_THRESHOLD = 0.60
_C3_THRESHOLD = 1.00


async def handle_visual_tool_lifecycle(
    payload: dict[str, Any] | None,
    *,
    source: str = "app_http",
    source_event: Any | None = None,
) -> dict[str, Any]:
    """Record one visual-tool event and stage/notify according to policy.

    App should use this for stable milestones such as ``lock``/``confirm`` and
    coarse drag updates.  High-frequency pointer streams belong on the lossy
    ``parrot.ecp.tick`` topic or local Unity state; they should be summarized
    into lifecycle events before reaching this route.
    """
    try:
        packet = VisualToolLifecyclePacket.model_validate(payload or {})
    except ValidationError as exc:
        receipt = VisualToolReceipt(
            success=False,
            error="invalid_visual_tool_lifecycle_payload",
            audit={
                "schema": "VisualToolEvidenceLifecycle.backend_v1",
                "validation_errors": exc.errors(),
                "source": source,
            },
        )
        _write_receipt(receipt)
        return receipt.as_json()

    ref = _bind_or_lookup_ref(packet, source_event=source_event)
    sample = _record_lifecycle_sample(packet, ref_id=ref.ref_id if ref else "", source=source, source_event=source_event)
    state = _update_tool_state(packet, ref_id=ref.ref_id if ref else "", evidence_id=sample.evidence_id)
    delivery = _delivery_for_packet(packet, state)

    awareness: EvidenceAwarenessDecision | None = None
    if delivery["stage_intent_workspace"]:
        awareness = await stage_sample_for_goslo(
            sample,
            description=_description(packet, state),
            notify_requested=delivery["notify_goslo"],
            source="vision.tool_lifecycle",
        )

    if packet.interaction_phase in {VisualToolPhase.CANCEL, VisualToolPhase.RELEASE}:
        _unbind_tool_ref(packet)

    receipt = VisualToolReceipt(
        success=True,
        packet=packet.model_dump(mode="json"),
        ref_id=ref.ref_id if ref else "",
        ref_kind=str(ref.kind) if ref else "",
        evidence=sample.as_json(),
        staged_ref_id=awareness.staged_ref_id if awareness else "",
        salience={
            "tool_score": round(state.salience, 3),
            "delta": round(_salience_delta(packet), 3),
            "intent_stage_threshold": _INTENT_STAGE_THRESHOLD,
            "c3_threshold": _C3_THRESHOLD,
            "locked": state.locked,
            "scope": "visual_tool_evidence_salience_not_dsg_l3_attention",
        },
        delivery=delivery,
        awareness=awareness.as_json() if awareness else {},
        audit={
            "schema": "VisualToolEvidenceLifecycle.backend_v1",
            "source": source,
            "source_event_id": str(getattr(source_event, "event_id", "") or ""),
            "source_event_type": str(getattr(source_event, "event_type", "") or ""),
            "image_transport": "asset_path_or_asset_uri_only_no_inline_image_bytes",
            "intent_workspace_is_passive_until_c3_notice": True,
            "c4_interrupt_supported": False,
        },
    )
    _write_receipt(receipt)
    return receipt.as_json()


def bridge_visual_tool_lifecycle_event(event: Any) -> dict[str, Any]:
    """Bridge reliable ECP ``visual_tool.lifecycle`` into the same handler."""
    payload = dict(getattr(event, "payload", {}) or {})
    summary = {
        "action": "vision.tool.lifecycle.ecp_bridge",
        "event_id": str(getattr(event, "event_id", "") or ""),
        "scheduled": False,
    }
    coro = handle_visual_tool_lifecycle(payload, source="ecp_event", source_event=event)
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return {**summary, "receipt": asyncio.run(coro)}
    task = loop.create_task(coro)
    task.add_done_callback(_log_task_result)
    return {**summary, "scheduled": True}


def latest_visual_tool_lifecycle_receipt() -> dict[str, Any]:
    bb = open_bb_client(name="visual_tool.receipt_read", writer=None)
    try:
        value = bb.get(_BB_KEY_RECEIPT)
    except KeyError:
        return {}
    return dict(value or {}) if isinstance(value, dict) else {}


def reset_visual_tool_lifecycle_for_tests() -> None:
    with _STATE_LOCK:
        _STATES.clear()


def store_visual_tool_asset(
    *,
    asset_id: str,
    body: bytes,
    content_type: str = "application/octet-stream",
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Store a BBox/MAG rendered crop or preview image as evidence.

    This is the HTTP/storage half of CORE-014.  App uploads bytes here, then
    sends the returned ``asset_path`` in a later lifecycle packet.  The split is
    deliberate: ECP/RPC carries only lightweight refs, never image bytes.
    """
    if not _is_safe_asset_id(asset_id):
        return {"action": "vision.tool.asset_upload", "success": False, "error": "invalid_asset_id"}
    if not body:
        return {"action": "vision.tool.asset_upload", "success": False, "error": "empty_body"}
    if len(body) > _MAX_ASSET_BYTES:
        return {
            "action": "vision.tool.asset_upload",
            "success": False,
            "error": "asset_too_large",
            "max_bytes": _MAX_ASSET_BYTES,
        }

    meta = dict(metadata or {})
    mime_type = content_type.split(";", 1)[0].strip().lower() or "application/octet-stream"
    path = _asset_path_for(asset_id, mime_type=mime_type)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(body)
    except OSError as exc:
        logger.exception("visual tool asset save failed asset_id=%s", asset_id)
        return {
            "action": "vision.tool.asset_upload",
            "success": False,
            "error": "save_failed",
            "detail": str(exc),
        }

    region = _region_from_meta(meta.get("region"))
    timebase = TimebaseStamp.from_payload(
        meta,
        default_domain=ClockDomain.UNITY,
        default_source_id=str(meta.get("source_id") or meta.get("tool_id") or "visual_tool_asset"),
    )
    sample = get_evidence_ledger().record_sample(
        kind=EvidenceKind.IMAGE_ASSET,
        status=EvidenceStatus.READY,
        timebase=timebase,
        asset_path=str(path),
        mime_type=mime_type,
        region=region,
        description=str(meta.get("description") or f"visual tool asset {asset_id}"),
        meta={
            "schema": "VisualToolEvidenceLifecycle.asset_upload_v1",
            "asset_id": asset_id,
            "tool_id": str(meta.get("tool_id") or ""),
            "tool_kind": str(meta.get("tool_kind") or ""),
            "interaction_phase": str(meta.get("interaction_phase") or ""),
            "source_surface": str(meta.get("source_surface") or "app_ar_overlay"),
        },
    )
    return {
        "action": "vision.tool.asset_upload",
        "success": True,
        "asset_id": asset_id,
        "asset_path": str(path),
        "bytes": len(body),
        "mime_type": mime_type,
        "evidence": sample.as_json(),
        "audit": {
            "schema": "VisualToolEvidenceLifecycle.asset_upload_v1",
            "image_transport": "http_storage_not_ecp_or_rpc",
            "max_bytes": _MAX_ASSET_BYTES,
        },
    }


def _bind_or_lookup_ref(packet: VisualToolLifecyclePacket, *, source_event: Any | None) -> Any | None:
    source_event_id = str(getattr(source_event, "event_id", "") or packet.tool_event_id)
    if packet.tool_kind == VisualToolKind.BBOX:
        if packet.interaction_phase in {VisualToolPhase.RELEASE, VisualToolPhase.CANCEL}:
            return refs_registry.get_ref_by_bbox(packet.tool_id)
        return refs_registry.bind_bbox(
            bbox_id=packet.tool_id,
            source_event_id=source_event_id,
            label=packet.label or packet.subject_hint or f"bbox:{packet.tool_id}",
        )

    if packet.interaction_phase in {VisualToolPhase.RELEASE, VisualToolPhase.CANCEL}:
        return refs_registry.get_ref_by_focus(packet.tool_id)
    return refs_registry.bind_focus(
        focus_id=packet.tool_id,
        source_event_id=source_event_id,
        label=packet.label or packet.subject_hint or f"{packet.tool_kind}:{packet.tool_id}",
    )


def _record_lifecycle_sample(
    packet: VisualToolLifecyclePacket,
    *,
    ref_id: str,
    source: str,
    source_event: Any | None,
) -> TimeAlignedSampleRef:
    event_payload = dict(getattr(source_event, "payload", {}) or {})
    body_for_timebase = dict(packet.model_dump(mode="json"))
    if packet.timebase:
        body_for_timebase["timebase"] = packet.timebase
    elif event_payload:
        body_for_timebase.update({k: v for k, v in event_payload.items() if k in {"timebase", "ts_ms", "timestamp", "observed_at"}})
    timebase = TimebaseStamp.from_payload(
        body_for_timebase,
        default_domain=ClockDomain.UNITY if source in {"ecp_event", "app_http"} else ClockDomain.WEB,
        default_source_id=packet.source_surface,
        envelope_created_at_ms=int(getattr(source_event, "created_at", 0) or 0),
    )
    kind = EvidenceKind.IMAGE_ASSET if packet.asset_path or packet.asset_uri else EvidenceKind.BBOX_FOCUS
    bbox_refs = (ref_id,) if ref_id and packet.tool_kind == VisualToolKind.BBOX else ()
    focus_refs = (ref_id,) if ref_id and packet.tool_kind != VisualToolKind.BBOX else ()
    return get_evidence_ledger().record_sample(
        kind=kind,
        status=EvidenceStatus.READY,
        timebase=timebase,
        asset_path=packet.asset_path,
        asset_uri=packet.asset_uri,
        mime_type=packet.mime_type,
        region=packet.region,
        related_refs=(ref_id,) if ref_id else (),
        bbox_refs=bbox_refs,
        focus_refs=focus_refs,
        description=_description(packet, None),
        meta={
            "schema": "VisualToolEvidenceLifecycle.backend_v1",
            "tool_event_id": packet.tool_event_id,
            "tool_id": packet.tool_id,
            "tool_kind": packet.tool_kind,
            "interaction_phase": packet.interaction_phase,
            "source_surface": packet.source_surface,
            "source": source,
            "asset_ref": packet.asset_ref,
            "subject_hint": packet.subject_hint,
            "label": packet.label,
            "pose": packet.pose,
            "meta": packet.meta,
            "source_event_id": str(getattr(source_event, "event_id", "") or ""),
        },
    )


def _update_tool_state(
    packet: VisualToolLifecyclePacket,
    *,
    ref_id: str,
    evidence_id: str,
) -> _VisualToolState:
    key = f"{packet.tool_kind}:{packet.tool_id}"
    now_ms = int(time.time() * 1000)
    with _STATE_LOCK:
        state = _STATES.get(key)
        if state is None:
            state = _VisualToolState(
                tool_id=packet.tool_id,
                tool_kind=str(packet.tool_kind),
                updated_at_ms=now_ms,
            )
        delta = _salience_delta(packet)
        state.salience = max(0.0, min(2.0, state.salience + delta))
        if packet.interaction_phase == VisualToolPhase.LOCK:
            state.locked = True
        elif packet.interaction_phase in {VisualToolPhase.UNLOCK, VisualToolPhase.CANCEL, VisualToolPhase.RELEASE}:
            state.locked = False
        state.ref_id = ref_id or state.ref_id
        state.latest_evidence_id = evidence_id
        state.latest_phase = str(packet.interaction_phase)
        state.updated_at_ms = now_ms
        _STATES[key] = state
        return _VisualToolState(**state.__dict__)


def _salience_delta(packet: VisualToolLifecyclePacket) -> float:
    base = _PHASE_DELTA.get(packet.interaction_phase, 0.0)
    multiplier = _KIND_MULTIPLIER.get(packet.tool_kind, 0.5)
    return (base * multiplier) + float(packet.attention_hint or 0.0)


def _delivery_for_packet(packet: VisualToolLifecyclePacket, state: _VisualToolState) -> dict[str, Any]:
    pref = packet.delivery_preference
    phase = packet.interaction_phase
    stage_by_phase = phase in {
        VisualToolPhase.LOCK,
        VisualToolPhase.CONFIRM,
        VisualToolPhase.EXPLICIT_SEND,
    }
    stage = bool(stage_by_phase or state.salience >= _INTENT_STAGE_THRESHOLD)
    notify = False
    channel = "intent_workspace" if stage else "none"
    reason = "stage_by_tool_policy" if stage else "below_stage_threshold"
    c4_requested = pref == VisualToolDeliveryPreference.C4

    if pref == VisualToolDeliveryPreference.SILENT:
        notify = False
        channel = "intent_workspace" if stage else "none"
        reason = "user_requested_silent"
    elif pref == VisualToolDeliveryPreference.INTENT_ONLY:
        stage = True
        notify = False
        channel = "intent_workspace"
        reason = "user_requested_intent_only"
    elif pref == VisualToolDeliveryPreference.C3:
        stage = True
        notify = True
        channel = "c3_context_notice"
        reason = "user_requested_c3"
    elif pref == VisualToolDeliveryPreference.C4:
        stage = True
        notify = True
        channel = "c3_context_notice_c4_downgraded"
        reason = "c4_requested_but_interrupt_disabled_in_v1"
    elif packet.tool_kind == VisualToolKind.BBOX and phase in {VisualToolPhase.CONFIRM, VisualToolPhase.EXPLICIT_SEND}:
        stage = True
        notify = True
        channel = "c3_context_notice"
        reason = "bbox_confirm_is_strong_user_intent"
    elif packet.tool_kind in {VisualToolKind.MAG, VisualToolKind.FOCUS} and phase == VisualToolPhase.EXPLICIT_SEND:
        stage = True
        notify = True
        channel = "c3_context_notice"
        reason = "magnifier_explicit_send"
    elif state.salience >= _C3_THRESHOLD and packet.tool_kind == VisualToolKind.BBOX:
        stage = True
        notify = True
        channel = "c3_context_notice"
        reason = "bbox_salience_threshold"
    elif packet.tool_kind in {VisualToolKind.MAG, VisualToolKind.FOCUS} and phase == VisualToolPhase.CONFIRM:
        stage = True
        notify = False
        channel = "intent_workspace"
        reason = "magnifier_confirm_is_silent_by_default"

    return {
        "stage_intent_workspace": bool(stage),
        "notify_goslo": bool(notify),
        "allow_interrupt": False,
        "requested_level": pref,
        "resolved_channel": channel,
        "reason": reason,
        "c4_requested": c4_requested,
        "c4_downgraded": c4_requested,
    }


def _unbind_tool_ref(packet: VisualToolLifecyclePacket) -> None:
    if packet.tool_kind == VisualToolKind.BBOX:
        refs_registry.unbind_bbox(packet.tool_id)
    else:
        refs_registry.unbind_focus(packet.tool_id)


def _description(packet: VisualToolLifecyclePacket, state: _VisualToolState | None) -> str:
    subject = packet.subject_hint or packet.label or packet.tool_id
    suffix = f", score={state.salience:.2f}" if state else ""
    return f"{packet.tool_kind} {packet.interaction_phase}: {subject}{suffix}"


def _write_receipt(receipt: VisualToolReceipt) -> None:
    bb = open_bb_client(name="visual_tool.receipt_write", writer=_BB_WRITER)
    bb.set(_BB_KEY_RECEIPT, receipt.as_json())


def _asset_path_for(asset_id: str, *, mime_type: str) -> Path:
    day = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    return Path(os.getenv(_ASSET_ROOT_ENV, _DEFAULT_ASSET_ROOT)) / day / f"{asset_id}{_extension_for_mime(mime_type)}"


def _extension_for_mime(mime_type: str) -> str:
    if mime_type in {"image/jpeg", "image/jpg"}:
        return ".jpg"
    if mime_type == "image/png":
        return ".png"
    if mime_type == "image/webp":
        return ".webp"
    return ".bin"


def _is_safe_asset_id(asset_id: str) -> bool:
    if not asset_id or not asset_id.strip() or len(asset_id) > 128:
        return False
    return not any(ch in asset_id for ch in _FORBIDDEN_PATH_CHARS)


def _region_from_meta(raw: Any) -> SampleRegion | None:
    if not isinstance(raw, dict):
        return None
    try:
        return SampleRegion.model_validate(raw)
    except ValidationError:
        return None


def _log_task_result(task: asyncio.Task[dict[str, Any]]) -> None:
    try:
        task.result()
    except Exception:  # pragma: no cover - defensive async logging
        logger.exception("visual tool lifecycle bridge failed")


__all__ = [
    "VisualToolDeliveryPreference",
    "VisualToolKind",
    "VisualToolLifecyclePacket",
    "VisualToolPhase",
    "VisualToolReceipt",
    "bridge_visual_tool_lifecycle_event",
    "handle_visual_tool_lifecycle",
    "latest_visual_tool_lifecycle_receipt",
    "reset_visual_tool_lifecycle_for_tests",
    "store_visual_tool_asset",
]
