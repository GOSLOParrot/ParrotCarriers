"""GOSLO awareness policy for time-aligned visual evidence.

This is the visual-evidence counterpart of Photo Awareness.  It stages a
compact evidence hint into IntentWorkspace and records a Blackboard notice, but
it does not directly call ``generate_reply``.  The actual speech push remains
session-owned so the LiveKit/Gemini turn lifecycle can enforce safe timing.
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from dataclasses import dataclass
from typing import Any

from parrot.brain.intent_workspace import (
    PayloadSource,
    StagedRefKind,
    StagedRefMetadata,
    StagedRefRequest,
    get_intent_workspace,
)
from parrot.brain.session_policy import should_stage_context_notice
from parrot.brain.vision.evidence import (
    ClockDomain,
    TimeAlignedSampleRef,
    TimebaseStamp,
    resolve_identify_evidence,
)
from parrot.scheduler.blackboard import open_bb_client

logger = logging.getLogger(__name__)

_BB_WRITER = "brain.vision.evidence_awareness"
_BB_KEY_NOTICE = "transient/evidence_awareness_notice"
_DEFAULT_TTL_SECONDS = 15 * 60


@dataclass(frozen=True)
class EvidenceAwarenessDecision:
    """Decision for staging/announcing one evidence sample."""

    evidence_id: str
    staged_ref_id: str = ""
    notify_goslo: bool = False
    allow_react: bool = False
    allow_interrupt: bool = False
    reason: str = ""
    message: str = ""

    def as_json(self) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "staged_ref_id": self.staged_ref_id,
            "notify_goslo": self.notify_goslo,
            "allow_react": self.allow_react,
            "allow_interrupt": self.allow_interrupt,
            "reason": self.reason,
            "message": self.message,
        }


async def stage_evidence_for_goslo(
    *,
    evidence_id: str = "",
    bbox_ref_id: str = "",
    focus_ref_id: str = "",
    target_time_ms: int = 0,
    description: str = "",
    notify_requested: bool = True,
    source: str = "vision.evidence",
    ttl_seconds: int = _DEFAULT_TTL_SECONDS,
) -> EvidenceAwarenessDecision:
    """Resolve an evidence sample and stage a compact hint for GOSLO.

    V1 deliberately separates "stage context" from "speak now".  The decision
    marks whether a speech notification would be allowed by session policy, but
    it never calls ``generate_reply`` from this backend utility.
    """
    sample = await resolve_identify_evidence(
        evidence_id=evidence_id,
        bbox_ref_id=bbox_ref_id,
        focus_ref_id=focus_ref_id,
        target_time_ms=target_time_ms,
        description=description,
        request_source=source,
    )
    if sample is None:
        decision = EvidenceAwarenessDecision(
            evidence_id=evidence_id,
            notify_goslo=False,
            allow_react=False,
            allow_interrupt=False,
            reason="evidence_missing_or_pending",
            message="No ready stored evidence was available for GOSLO.",
        )
        _write_notice(decision)
        return decision

    return await stage_sample_for_goslo(
        sample,
        description=description,
        notify_requested=notify_requested,
        source=source,
        ttl_seconds=ttl_seconds,
    )


def bridge_attention_threshold_to_goslo(
    payload: dict[str, Any] | None,
    *,
    source_event: Any | None = None,
) -> dict[str, Any]:
    """Schedule the conservative BBox/Focus threshold -> GOSLO bridge.

    This is the automatic side of WEB-015.12.  The threshold accumulator is a
    synchronous ECP subscriber, while IntentWorkspace staging is async.  When a
    LiveKit/Brain loop is already running we schedule a task; in simple scripts
    or tests without a loop we run the same coroutine to completion.

    The bridge is intentionally narrow: it never captures a frame, never calls
    ``generate_reply``, and never mutates L2-B.  It only asks the evidence
    ledger for the nearest stored frame/photo and stages a compact hint if one
    is already available; otherwise ``resolve_identify_evidence`` records a
    pending evidence request.
    """
    body = dict(payload or {})
    subject_kind = str(body.get("subject_kind") or "").strip().lower()
    subject_id = str(body.get("subject_id") or "").strip()
    ref_id = str(body.get("ref_id") or "").strip()
    summary = {
        "action": "vision.evidence.attention_bridge",
        "subject_kind": subject_kind,
        "subject_id": subject_id,
        "ref_id": ref_id,
        "scheduled": False,
    }
    coro = stage_attention_threshold_for_goslo(body, source_event=source_event)
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        decision = asyncio.run(coro)
        return {**summary, "scheduled": False, "decision": decision.as_json()}

    task = loop.create_task(coro)
    task.add_done_callback(_log_bridge_task_result)
    return {**summary, "scheduled": True}


async def stage_attention_threshold_for_goslo(
    payload: dict[str, Any] | None,
    *,
    source_event: Any | None = None,
) -> EvidenceAwarenessDecision:
    """Resolve/stage evidence for an ``attention.threshold.crossed`` hint.

    BBox/Mag/Focus attention is an evidence-ref tool, not a NodeKind.  The
    threshold payload supplies the user's region ref and sample time; this
    helper turns that into a normal ``visual_evidence_hint`` so GOSLO can see
    it through the existing IntentWorkspace + C3 context path.
    """
    body = dict(payload or {})
    subject_kind = str(body.get("subject_kind") or "").strip().lower()
    ref_id = str(body.get("ref_id") or "").strip()
    bbox_ref_id = ref_id if subject_kind == "bbox" else ""
    focus_ref_id = ref_id if subject_kind == "focus" else ""
    description = _attention_description(body)
    target_time_ms = _threshold_target_time_ms(body, source_event=source_event)
    return await stage_evidence_for_goslo(
        evidence_id=str(body.get("evidence_id") or ""),
        bbox_ref_id=bbox_ref_id,
        focus_ref_id=focus_ref_id,
        target_time_ms=target_time_ms,
        description=description,
        notify_requested=True,
        source="dsg.attention.threshold",
        ttl_seconds=_DEFAULT_TTL_SECONDS,
    )


async def stage_sample_for_goslo(
    sample: TimeAlignedSampleRef,
    *,
    description: str = "",
    notify_requested: bool = True,
    source: str = "vision.evidence",
    ttl_seconds: int = _DEFAULT_TTL_SECONDS,
) -> EvidenceAwarenessDecision:
    """Stage an already-resolved sample in IntentWorkspace."""
    ttl = max(60, min(int(ttl_seconds or _DEFAULT_TTL_SECONDS), 30 * 60))
    session_allows_notice = should_stage_context_notice("vision.evidence_awareness")
    allow_react = bool(notify_requested and session_allows_notice)
    payload = _payload_for_sample(sample, description=description, source=source)
    handle = await get_intent_workspace().stage(StagedRefRequest(
        kind=StagedRefKind.DOC,
        payload_source=PayloadSource.INLINE_TEXT,
        payload_value=json.dumps(payload, ensure_ascii=False),
        metadata=StagedRefMetadata(
            origin=f"{source}:awareness",
            kind=StagedRefKind.DOC,
            payload_source=PayloadSource.INLINE_TEXT,
            related_node_uuid=sample.evidence_id,
            expires_at=time.time() + ttl,
            custom_meta={
                "role": "visual_evidence_hint",
                "evidence_id": sample.evidence_id,
                "evidence_kind": str(sample.kind),
                "notify_requested": bool(notify_requested),
                "notify_goslo": allow_react,
                "workspace_id": "runtime_flow",
            },
        ),
    ))
    decision = EvidenceAwarenessDecision(
        evidence_id=sample.evidence_id,
        staged_ref_id=handle.ref_id,
        notify_goslo=allow_react,
        allow_react=allow_react,
        allow_interrupt=False,
        reason="staged_notify_allowed" if allow_react else "staged_silent",
        message=_message_for_sample(sample, description=description, staged_ref_id=handle.ref_id),
    )
    _write_notice(decision)
    return decision


def latest_evidence_awareness_notice() -> dict[str, Any]:
    bb = open_bb_client(name="evidence_awareness.notice_read", writer=None)
    try:
        value = bb.get(_BB_KEY_NOTICE)
    except KeyError:
        return {}
    return dict(value or {}) if isinstance(value, dict) else {}


def _payload_for_sample(
    sample: TimeAlignedSampleRef,
    *,
    description: str,
    source: str,
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "role": "visual_evidence_hint",
        "source": source,
        "description": description,
        "evidence": sample.as_json(),
        "timebase": sample.timebase.model_dump(mode="json"),
        "asset": {
            "asset_path": sample.asset_path,
            "asset_uri": sample.asset_uri,
            "mime_type": sample.mime_type,
            "asset_exists": sample.as_json().get("asset_exists", False),
        },
    }


def _message_for_sample(
    sample: TimeAlignedSampleRef,
    *,
    description: str,
    staged_ref_id: str,
) -> str:
    label = description.strip() or sample.description or str(sample.kind)
    return (
        "Time-aligned visual evidence is ready for inspection: "
        f"{label} (evidence_id={sample.evidence_id}, ref={staged_ref_id})."
    )


def _write_notice(decision: EvidenceAwarenessDecision) -> None:
    try:
        bb = open_bb_client(name="evidence_awareness.notice", writer=_BB_WRITER)
        notice = decision.as_json()
        notice["ts_ms"] = int(time.time() * 1000)
        bb.set(_BB_KEY_NOTICE, notice)
    except Exception:
        logger.debug("evidence awareness notice write failed", exc_info=True)


def _attention_description(payload: dict[str, Any]) -> str:
    subject_kind = str(payload.get("subject_kind") or "attention").strip()
    subject_id = str(payload.get("subject_id") or "").strip()
    label = str(payload.get("label") or "").strip()
    weight = payload.get("weight")
    bits = ["attention threshold crossed"]
    if subject_kind:
        bits.append(subject_kind)
    if subject_id:
        bits.append(subject_id)
    if label and label not in bits:
        bits.append(label)
    if isinstance(weight, (int, float)) and not isinstance(weight, bool):
        bits.append(f"weight={weight:.2f}")
    return " / ".join(bits)


def _threshold_target_time_ms(
    payload: dict[str, Any],
    *,
    source_event: Any | None,
) -> int:
    """Prefer producer sample time over threshold envelope time."""
    if source_event is not None:
        try:
            stamp = TimebaseStamp.from_payload(
                getattr(source_event, "payload", {}) or {},
                default_domain=ClockDomain.UNITY,
                default_source_id=str(getattr(source_event, "unity_identity", "") or ""),
                envelope_created_at_ms=int(getattr(source_event, "created_at", 0) or 0),
            )
            if stamp.wall_time_ms > 0:
                return stamp.wall_time_ms
        except Exception:
            logger.debug("attention bridge source_event timebase parse failed", exc_info=True)
    try:
        return int(payload.get("ts_ms") or 0)
    except Exception:
        return 0


def _log_bridge_task_result(task: asyncio.Task[EvidenceAwarenessDecision]) -> None:
    try:
        task.result()
    except asyncio.CancelledError:
        return
    except Exception:
        logger.debug("attention evidence bridge task failed", exc_info=True)


__all__ = [
    "EvidenceAwarenessDecision",
    "bridge_attention_threshold_to_goslo",
    "latest_evidence_awareness_notice",
    "stage_attention_threshold_for_goslo",
    "stage_evidence_for_goslo",
    "stage_sample_for_goslo",
]
