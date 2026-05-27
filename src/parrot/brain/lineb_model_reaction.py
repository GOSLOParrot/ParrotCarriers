"""Bridge LineB voice-activity state to model capabilities.

LineB audio guard owns the turn-taking truth: speaking, listening, echo
suppressed, and uncertain/noise input. This module maps that state to
model-declared capabilities so Unity controllers can react without hard-coding
LineB policy into every prefab.
"""

from __future__ import annotations

import json
import logging
import math
from dataclasses import asdict, dataclass
from typing import Any

from parrot.brain.tools._capability_gate import resolve_model_id, supports_capability
from parrot.brain.tools._rpc_bridge import UNITY_RPC_ECP_TTL_S, call_unity_rpc
from parrot.scheduler.blackboard import open_bb_client
from parrot.shared.ecp import EcpCommandKind, wrap_legacy_rpc_payload

logger = logging.getLogger(__name__)

_STATE_TO_CAPABILITY: dict[str, str] = {
    "speaking": "lineb_speaking",
    "listening": "lineb_listening",
    "agent_echo_suppressed": "lineb_echo_suppressed",
    "listening_uncertain": "lineb_listening_uncertain",
    "listening_noise": "lineb_listening_noise",
}


@dataclass(frozen=True)
class LineBModelReactionResult:
    ok: bool
    reason: str
    capability_id: str = ""
    model_id: str = ""
    detail: str = ""

    def as_json(self) -> dict[str, Any]:
        return asdict(self)


def capability_for_voice_activity(activity: dict[str, Any] | None) -> str:
    """Return the model capability id for one LineB voice-activity payload."""
    state = str((activity or {}).get("state") or "").strip().lower()
    return _STATE_TO_CAPABILITY.get(state, "")


def voice_activity_parameters_json(activity: dict[str, Any] | None) -> str:
    """Build the small JsonUtility-friendly payload Unity controllers read."""
    data = dict(activity or {})
    payload = {
        "state": str(data.get("state") or ""),
        "source": str(data.get("source") or ""),
        "segment_id": str(data.get("segment_id") or ""),
        "input_id": str(data.get("input_id") or ""),
        "turn_decision": str(data.get("turn_decision") or ""),
        "speaker_role": str(data.get("speaker_role") or ""),
        "echo_score": _float_or_default(data.get("echo_score"), 0.0),
        "voiceprint_decision": str(data.get("voiceprint_decision") or ""),
        "voiceprint_profile_id": str(data.get("voiceprint_profile_id") or ""),
        "speaker_similarity": _float_or_default(data.get("speaker_similarity"), 0.0),
        "model_reaction_policy": str(data.get("model_reaction_policy") or ""),
        "recommended_model_trigger": str(data.get("recommended_model_trigger") or ""),
        "suppression_duration_s": _suppression_duration_s(data),
    }
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


async def dispatch_latest_lineb_voice_activity_to_model(
    *,
    model_id: str = "",
    reason: str = "lineb_voice_activity",
) -> LineBModelReactionResult:
    """Read latest LineB voice activity from BB and dispatch if supported."""
    activity = _bb_dict("session/lineb_voice_activity")
    return await dispatch_lineb_voice_activity_to_model(
        activity,
        model_id=model_id,
        reason=reason,
    )


async def dispatch_lineb_voice_activity_to_model(
    activity: dict[str, Any] | None,
    *,
    model_id: str = "",
    reason: str = "lineb_voice_activity",
) -> LineBModelReactionResult:
    """Send one LineB voice-activity capability to Unity when available.

    This is best-effort. If the active model does not declare the capability,
    or Unity is not connected, the caller receives a structured skip/failure
    instead of breaking transcript/TTS processing.
    """
    capability_id = capability_for_voice_activity(activity)
    selected_model_id = resolve_model_id(model_id)
    if not capability_id:
        return LineBModelReactionResult(
            ok=False,
            reason="no_capability_for_voice_activity",
            model_id=selected_model_id,
        )
    if not supports_capability(capability_id, selected_model_id):
        return LineBModelReactionResult(
            ok=False,
            reason="capability_not_declared_by_model",
            capability_id=capability_id,
            model_id=selected_model_id,
        )

    params = voice_activity_parameters_json(activity)
    payload, _command = wrap_legacy_rpc_payload(
        {
            "animation": capability_id,
            "parameters_json": params,
            "strict_capability": True,
        },
        kind=EcpCommandKind.ANIMATE,
        target={
            "body_channel": "body",
            "capability_id": capability_id,
            "parameters_json": params,
            "reason": reason,
        },
        actor="brain.lineb_model_reaction",
        expires_in_s=UNITY_RPC_ECP_TTL_S,
        expected_duration_ms=250,
        meta={"model_id": selected_model_id},
    )
    try:
        response = await call_unity_rpc(method="animate", payload=payload, timeout=2.0)
    except Exception as exc:  # noqa: BLE001 - best-effort Unity side effect.
        logger.debug("LineB voice activity dispatch skipped: %r", exc)
        return LineBModelReactionResult(
            ok=False,
            reason="unity_dispatch_failed",
            capability_id=capability_id,
            model_id=selected_model_id,
            detail=f"{type(exc).__name__}: {exc}",
        )
    return LineBModelReactionResult(
        ok=True,
        reason="dispatched",
        capability_id=capability_id,
        model_id=selected_model_id,
        detail=response[:240],
    )


def _suppression_duration_s(activity: dict[str, Any]) -> float:
    state = str(activity.get("state") or "").strip().lower()
    if state == "speaking":
        return max(0.35, _float_or_default(activity.get("suppression_duration_s"), 1.2))
    if state == "agent_echo_suppressed":
        return 0.9
    if state in {"listening_uncertain", "listening_noise"}:
        return 0.35
    return 0.0


def _float_or_default(value: Any, fallback: float) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return fallback
    return parsed if math.isfinite(parsed) else fallback


def _bb_dict(key: str) -> dict[str, Any]:
    try:
        bb = open_bb_client(name="lineb_model_reaction.read", writer=None)
        value = bb.get(key)
    except Exception:
        return {}
    return dict(value) if isinstance(value, dict) else {}


__all__ = [
    "LineBModelReactionResult",
    "capability_for_voice_activity",
    "dispatch_latest_lineb_voice_activity_to_model",
    "dispatch_lineb_voice_activity_to_model",
    "voice_activity_parameters_json",
]
