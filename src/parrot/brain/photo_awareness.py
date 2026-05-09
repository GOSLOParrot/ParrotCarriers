"""Photo Awareness v1 policy and preview-ref bridge.

Photo capture has two independent concerns:

* Camera mode decides whether the app is allowed to capture frames.
* Awareness decides whether GOSLO is notified about the capture and whether a
  short-lived preview reference is staged for immediate reasoning.

This module owns the Awareness decision so Unity, the App facade, and the
photo observer do not each invent their own behavior. App v1 deliberately
blocks interruptions; even ``AWARE_REACT`` means "react at a safe turn
boundary", not "barge into the current LiveKit speech lifecycle".
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any

from parrot.brain.intent_workspace import (
    PayloadSource,
    StagedRefKind,
    StagedRefMetadata,
    StagedRefRequest,
    get_intent_workspace,
)
from parrot.scheduler.blackboard import open_bb_client

logger = logging.getLogger(__name__)

_BB_WRITER_SETTINGS = "brain.app_first_version"
_BB_WRITER_DECISION = "brain.photo_awareness"
_BB_KEY_POLICY = "session/photo_awareness_policy"
_BB_KEY_ENABLED = "session/photo_awareness_enabled"
_BB_KEY_ALLOW_INTERRUPT = "session/photo_awareness_allows_interrupt"
_BB_KEY_PREVIEW_TTL = "session/photo_awareness_preview_ttl_seconds"
_BB_KEY_NOTICE = "transient/photo_awareness_notice"
_DEFAULT_PREVIEW_TTL_SECONDS = 15 * 60


class PhotoAwarenessPolicy(str, Enum):
    """App v1 photo awareness policies."""

    UNAWARE_RECORDED = "UNAWARE_RECORDED"
    AWARE_SILENT = "AWARE_SILENT"
    AWARE_REACT = "AWARE_REACT"


@dataclass(frozen=True)
class PhotoAwarenessSettings:
    """Current session settings used by the photo observer."""

    enabled: bool
    policy: PhotoAwarenessPolicy
    allows_interrupt: bool
    preview_ttl_seconds: int


@dataclass(frozen=True)
class PhotoAwarenessDecision:
    """Result of evaluating one photo preview event."""

    photo_id: str
    policy: PhotoAwarenessPolicy
    notify_goslo: bool
    allow_react: bool
    allow_interrupt: bool
    preview_ref_id: str = ""
    reason: str = ""

    def as_json(self) -> dict[str, Any]:
        return {
            "photo_id": self.photo_id,
            "policy": self.policy.value,
            "notify_goslo": self.notify_goslo,
            "allow_react": self.allow_react,
            "allow_interrupt": self.allow_interrupt,
            "preview_ref_id": self.preview_ref_id,
            "reason": self.reason,
        }


def apply_photo_awareness_settings(
    policy: PhotoAwarenessPolicy | str,
    *,
    enabled: bool = True,
    preview_ttl_seconds: int = _DEFAULT_PREVIEW_TTL_SECONDS,
) -> tuple[str, ...]:
    """Write Awareness settings through the App facade's backend-owned keys."""
    selected = PhotoAwarenessPolicy(policy)
    ttl = _normalize_preview_ttl(preview_ttl_seconds)
    bb = open_bb_client(name="app_facade.awareness", writer=_BB_WRITER_SETTINGS)
    bb.set(_BB_KEY_POLICY, selected.value)
    bb.set(_BB_KEY_ENABLED, bool(enabled))
    # First-version product rule: Awareness may inform GOSLO, never interrupt.
    bb.set(_BB_KEY_ALLOW_INTERRUPT, False)
    bb.set(_BB_KEY_PREVIEW_TTL, ttl)
    return (
        _BB_KEY_POLICY,
        _BB_KEY_ENABLED,
        _BB_KEY_ALLOW_INTERRUPT,
        _BB_KEY_PREVIEW_TTL,
    )


def read_photo_awareness_settings() -> PhotoAwarenessSettings:
    """Read current settings with conservative defaults."""
    bb = open_bb_client(name="photo_awareness.read", writer=None)
    raw_policy = bb.get(_BB_KEY_POLICY) or PhotoAwarenessPolicy.UNAWARE_RECORDED.value
    try:
        policy = PhotoAwarenessPolicy(str(raw_policy))
    except ValueError:
        policy = PhotoAwarenessPolicy.UNAWARE_RECORDED
    return PhotoAwarenessSettings(
        enabled=bool(bb.get(_BB_KEY_ENABLED) or False),
        policy=policy,
        allows_interrupt=bool(bb.get(_BB_KEY_ALLOW_INTERRUPT) or False),
        preview_ttl_seconds=_normalize_preview_ttl(
            int(bb.get(_BB_KEY_PREVIEW_TTL) or _DEFAULT_PREVIEW_TTL_SECONDS)
        ),
    )


def handle_photo_preview_awareness(
    *,
    photo_id: str,
    payload: dict[str, Any],
    source_event_id: str,
) -> PhotoAwarenessDecision:
    """Evaluate one preview event and stage a short-lived preview ref if needed."""
    settings = read_photo_awareness_settings()
    if not settings.enabled or settings.policy == PhotoAwarenessPolicy.UNAWARE_RECORDED:
        decision = PhotoAwarenessDecision(
            photo_id=photo_id,
            policy=settings.policy,
            notify_goslo=False,
            allow_react=False,
            allow_interrupt=False,
            reason="awareness_disabled_or_unaware",
        )
        _write_notice(decision)
        return decision

    preview_b64 = str(payload.get("preview_jpeg_b64", "") or "")
    if not preview_b64:
        decision = PhotoAwarenessDecision(
            photo_id=photo_id,
            policy=settings.policy,
            notify_goslo=True,
            allow_react=settings.policy == PhotoAwarenessPolicy.AWARE_REACT,
            allow_interrupt=False,
            reason="preview_missing",
        )
        _write_notice(decision)
        return decision

    return _stage_preview_ref_sync(
        photo_id=photo_id,
        payload=payload,
        source_event_id=source_event_id,
        settings=settings,
    )


def latest_photo_awareness_notice() -> dict[str, Any]:
    """Return the last lightweight Awareness decision for monitors."""
    bb = open_bb_client(name="photo_awareness.notice_read", writer=None)
    try:
        value = bb.get(_BB_KEY_NOTICE)
    except KeyError:
        return {}
    return dict(value or {}) if isinstance(value, dict) else {}


def _stage_preview_ref_sync(
    *,
    photo_id: str,
    payload: dict[str, Any],
    source_event_id: str,
    settings: PhotoAwarenessSettings,
) -> PhotoAwarenessDecision:
    async def _stage() -> PhotoAwarenessDecision:
        ws = get_intent_workspace()
        preview_payload = {
            "schema_version": 1,
            "photo_id": photo_id,
            "source_event_id": source_event_id,
            "preview_jpeg_b64": str(payload.get("preview_jpeg_b64", "") or ""),
            "pose": payload.get("pose") if isinstance(payload.get("pose"), dict) else {},
            "candidate_subject_uuid": str(payload.get("candidate_subject_uuid", "") or ""),
            "focus_refs": list(payload.get("focus_refs") or ()),
            "bbox_refs": list(payload.get("bbox_refs") or ()),
        }
        handle = await ws.stage(StagedRefRequest(
            kind=StagedRefKind.PHOTO,
            payload_source=PayloadSource.INLINE_TEXT,
            payload_value=json.dumps(preview_payload, ensure_ascii=False),
            metadata=StagedRefMetadata(
                origin="photo_awareness.preview",
                kind=StagedRefKind.PHOTO,
                payload_source=PayloadSource.INLINE_TEXT,
                related_node_uuid=photo_id,
                expires_at=time.time() + settings.preview_ttl_seconds,
                custom_meta={
                    "role": "photo_preview_awareness",
                    "photo_id": photo_id,
                    "source_event_id": source_event_id,
                    "awareness_policy": settings.policy.value,
                },
            ),
        ))
        return PhotoAwarenessDecision(
            photo_id=photo_id,
            policy=settings.policy,
            notify_goslo=True,
            allow_react=settings.policy == PhotoAwarenessPolicy.AWARE_REACT,
            allow_interrupt=False,
            preview_ref_id=handle.ref_id,
            reason="preview_ref_staged",
        )

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        decision = asyncio.run(_stage())
        _write_notice(decision)
        return decision

    # In an already-running loop we cannot block this synchronous observer.
    # Schedule the staging and immediately publish a pending notice; the task
    # overwrites it with the ref id after IntentWorkspace completes.
    pending = PhotoAwarenessDecision(
        photo_id=photo_id,
        policy=settings.policy,
        notify_goslo=True,
        allow_react=settings.policy == PhotoAwarenessPolicy.AWARE_REACT,
        allow_interrupt=False,
        reason="preview_ref_pending",
    )
    _write_notice(pending)

    async def _stage_and_notice() -> None:
        try:
            _write_notice(await _stage())
        except Exception:
            logger.debug("photo awareness preview staging failed", exc_info=True)

    loop.create_task(_stage_and_notice())
    return pending


def _write_notice(decision: PhotoAwarenessDecision) -> None:
    bb = open_bb_client(name="photo_awareness.notice", writer=_BB_WRITER_DECISION)
    notice = decision.as_json()
    notice["ts_ms"] = int(time.time() * 1000)
    bb.set(_BB_KEY_NOTICE, notice)


def _normalize_preview_ttl(value: int) -> int:
    # Keep TTL in a predictable operational band: enough for immediate GOSLO
    # inspection, short enough that previews do not behave like permanent files.
    return max(60, min(int(value or _DEFAULT_PREVIEW_TTL_SECONDS), 30 * 60))


__all__ = [
    "PhotoAwarenessDecision",
    "PhotoAwarenessPolicy",
    "PhotoAwarenessSettings",
    "apply_photo_awareness_settings",
    "handle_photo_preview_awareness",
    "latest_photo_awareness_notice",
    "read_photo_awareness_settings",
]
