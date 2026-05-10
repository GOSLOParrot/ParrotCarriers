"""Runtime audio-route and echo-guard state for LineB.

This module does not perform DSP. It provides the backend contract that LineB
needs before real device audio filtering lands:

* write ``session/audio_route_policy`` from an explicit app/audio route update;
* register recent TTS output segments;
* classify a mic input fragment against recent TTS segments using time overlap
  and optional voiceprint/echo scores;
* expose the latest decision to menus and tests.
"""

from __future__ import annotations

import math
import time
import uuid
from collections import deque
from dataclasses import asdict, dataclass, field
from difflib import SequenceMatcher
from typing import Any

from parrot.scheduler.blackboard import open_bb_client


WRITER = "brain.lineb_audio_guard"
MAX_SEGMENTS = 32
DEFAULT_ECHO_WINDOW_S = 1.25
DEFAULT_ECHO_SCORE_THRESHOLD = 0.82

_recent_segments: deque["TtsSegment"] = deque(maxlen=MAX_SEGMENTS)
_last_decision: "MicInputDecision | None" = None


@dataclass(frozen=True)
class TtsSegment:
    segment_id: str
    text_summary: str
    started_at: float
    expected_end_at: float
    tts_voice: str = ""
    voiceprint_hash: str = ""
    conversation_turn_id: str = ""
    acoustic_refs: dict[str, Any] = field(default_factory=dict)

    def as_json(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class MicInputDecision:
    input_id: str
    observed_at: float
    speaker_role: str
    turn_decision: str
    echo_score: float
    matched_segment_id: str = ""
    reason: str = ""
    asr_text: str = ""
    voiceprint_hash: str = ""
    voiceprint_decision: str = ""
    voiceprint_profile_id: str = ""
    speaker_similarity: float = 0.0

    def as_json(self) -> dict[str, Any]:
        return asdict(self)


def apply_audio_route_policy(
    *,
    input_route: str = "unknown",
    output_route: str = "unknown",
    microphone_enabled: bool = True,
    speaker_output_enabled: bool | None = None,
    echo_handling_mode: str | None = None,
    voiceprint_enabled: bool = False,
    speaker_state: str = "unknown",
    source: str = "manual",
) -> dict[str, Any]:
    """Write the current audio route policy to the Blackboard."""
    output = _clean(output_route, "unknown")
    input_ = _clean(input_route, "unknown")
    isolated = _is_isolated_output(output)
    speaker = _is_speaker_output(output)
    if speaker_output_enabled is None:
        speaker_output_enabled = speaker
    risk = _risk_for_route(output, voiceprint_enabled)
    handling = echo_handling_mode or _default_handling(
        output_route=output,
        voiceprint_enabled=voiceprint_enabled,
    )
    policy = {
        "schema_version": 1,
        "updated_at": time.time(),
        "source": source,
        "input_route": input_,
        "output_route": output,
        "microphone_enabled": bool(microphone_enabled),
        "speaker_output_enabled": bool(speaker_output_enabled),
        "is_isolated_output": isolated,
        "voiceprint": {
            "enabled": bool(voiceprint_enabled),
            "state": "monitoring" if voiceprint_enabled else "not_configured",
            "speaker_state": speaker_state,
            "summary": (
                "Voiceprint echo gate is enabled."
                if voiceprint_enabled
                else "Voiceprint echo gate is not configured."
            ),
        },
        "echo": {
            "risk_level": risk,
            "handling_mode": handling,
            "summary": _echo_summary(output, risk, handling),
        },
    }
    _write_bb("session/audio_route_policy", policy)
    return policy


def register_tts_segment(
    *,
    text_summary: str,
    duration_s: float,
    started_at: float | None = None,
    tts_voice: str = "",
    voiceprint_hash: str = "",
    conversation_turn_id: str = "",
    acoustic_refs: dict[str, Any] | None = None,
) -> TtsSegment:
    """Register one agent TTS output window for future echo decisions."""
    now = time.time() if started_at is None else _float_or_default(started_at, time.time())
    duration = max(0.05, _float_or_default(duration_s, 0.05))
    segment = TtsSegment(
        segment_id=f"tts_{uuid.uuid4().hex[:10]}",
        text_summary=str(text_summary or "")[:240],
        started_at=now,
        expected_end_at=now + duration,
        tts_voice=str(tts_voice or ""),
        voiceprint_hash=str(voiceprint_hash or ""),
        conversation_turn_id=str(conversation_turn_id or ""),
        acoustic_refs=dict(acoustic_refs or {}),
    )
    _recent_segments.append(segment)
    _write_segments()
    _write_voice_activity(
        state="speaking",
        source="tts_segment",
        segment=segment,
        model_reaction_policy="suppress_touch_and_cheek_reactions",
        recommended_model_trigger="lineb_speaking",
    )
    return segment


def classify_mic_input(
    *,
    observed_at: float | None = None,
    duration_s: float = 0.0,
    asr_text: str = "",
    voiceprint_hash: str = "",
    echo_score: float | None = None,
    speaker_similarity: float | None = None,
    voiceprint_decision: str = "",
    speaker_label: str = "",
    voiceprint_profile_id: str = "",
    voiceprint_enabled: bool | None = None,
    voiceprint_provider: str = "",
    voiceprint_manifest_path: str = "",
    voiceprint_threshold_accept: float | None = None,
    voiceprint_threshold_reject: float | None = None,
) -> MicInputDecision:
    """Classify a mic fragment as user input, agent echo, noise, or uncertain."""
    global _last_decision

    now = time.time() if observed_at is None else _float_or_default(observed_at, time.time())
    match = _matching_segment(now, max(0.0, _float_or_default(duration_s, 0.0)))
    score = _score(match, voiceprint_hash, echo_score, asr_text)
    voiceprint = _voiceprint_payload(
        speaker_similarity=speaker_similarity,
        voiceprint_decision=voiceprint_decision,
        speaker_label=speaker_label,
        voiceprint_profile_id=voiceprint_profile_id,
        voiceprint_enabled=voiceprint_enabled,
        voiceprint_provider=voiceprint_provider,
        voiceprint_manifest_path=voiceprint_manifest_path,
        voiceprint_threshold_accept=voiceprint_threshold_accept,
        voiceprint_threshold_reject=voiceprint_threshold_reject,
    )
    owner_verified = _voiceprint_accepts(voiceprint)
    speaker_rejected = _voiceprint_rejects(voiceprint)

    if match is not None and score >= DEFAULT_ECHO_SCORE_THRESHOLD:
        speaker_role = "agent"
        turn_decision = "agent_echo"
        reason = "matches_recent_tts_segment"
    elif match is not None and owner_verified:
        speaker_role = "user"
        turn_decision = "user_turn"
        reason = "owner_voiceprint_overrides_tts_overlap"
    elif match is None and echo_score is not None and score >= DEFAULT_ECHO_SCORE_THRESHOLD:
        speaker_role = "uncertain"
        turn_decision = "uncertain"
        reason = "high_echo_score_without_recent_tts"
    elif speaker_rejected:
        speaker_role = "other"
        turn_decision = "speaker_rejected"
        reason = "speaker_voiceprint_rejected"
    elif owner_verified:
        speaker_role = "user"
        turn_decision = "user_turn"
        reason = "speaker_voiceprint_accepted"
    elif not str(asr_text or "").strip() and score < 0.25:
        speaker_role = "unknown"
        turn_decision = "noise"
        reason = "empty_asr_low_echo_score"
    elif not str(asr_text or "").strip():
        speaker_role = "uncertain"
        turn_decision = "uncertain"
        reason = "empty_asr_with_echo_score"
    elif match is not None:
        speaker_role = "uncertain"
        turn_decision = "uncertain"
        reason = "time_overlap_but_low_similarity"
    else:
        speaker_role = "user"
        turn_decision = "user_turn"
        reason = "no_recent_tts_overlap"

    decision = MicInputDecision(
        input_id=f"mic_{uuid.uuid4().hex[:10]}",
        observed_at=now,
        speaker_role=speaker_role,
        turn_decision=turn_decision,
        echo_score=round(float(score), 4),
        matched_segment_id=match.segment_id if match else "",
        reason=reason,
        asr_text=str(asr_text or ""),
        voiceprint_hash=str(voiceprint_hash or ""),
        voiceprint_decision=str(voiceprint.get("decision") or ""),
        voiceprint_profile_id=str(voiceprint.get("profile_id") or ""),
        speaker_similarity=_float_or_default(voiceprint.get("similarity"), 0.0),
    )
    _last_decision = decision
    _write_bb("transient/lineb_last_input_decision", decision.as_json())
    _write_voice_activity_for_decision(decision)
    return decision


def recent_tts_segments() -> tuple[TtsSegment, ...]:
    return tuple(_recent_segments)


def latest_mic_decision() -> MicInputDecision | None:
    return _last_decision


def reset_lineb_audio_guard_for_test() -> None:
    global _last_decision
    _recent_segments.clear()
    _last_decision = None


def _write_segments() -> None:
    _write_bb("session/lineb_recent_tts_segments", [s.as_json() for s in _recent_segments])


def _write_voice_activity_for_decision(decision: MicInputDecision) -> dict[str, Any]:
    if decision.turn_decision == "agent_echo":
        return _write_voice_activity(
            state="agent_echo_suppressed",
            source="mic_input_classifier",
            decision=decision,
            model_reaction_policy="keep_listening_no_reply",
            recommended_model_trigger="lineb_echo_suppressed",
        )
    if decision.turn_decision == "noise":
        return _write_voice_activity(
            state="listening_noise",
            source="mic_input_classifier",
            decision=decision,
            model_reaction_policy="no_model_reaction",
            recommended_model_trigger="lineb_listening_noise",
        )
    if decision.turn_decision == "uncertain":
        return _write_voice_activity(
            state="listening_uncertain",
            source="mic_input_classifier",
            decision=decision,
            model_reaction_policy="subtle_listen_only",
            recommended_model_trigger="lineb_listening_uncertain",
        )
    if decision.turn_decision == "speaker_rejected":
        return _write_voice_activity(
            state="listening_uncertain",
            source="mic_input_classifier",
            decision=decision,
            model_reaction_policy="reject_non_owner_no_reply",
            recommended_model_trigger="lineb_listening_uncertain",
        )
    return _write_voice_activity(
        state="listening",
        source="mic_input_classifier",
        decision=decision,
        model_reaction_policy="listen_user_turn",
        recommended_model_trigger="lineb_listening",
    )


def _write_voice_activity(
    *,
    state: str,
    source: str,
    segment: TtsSegment | None = None,
    decision: MicInputDecision | None = None,
    model_reaction_policy: str,
    recommended_model_trigger: str,
) -> dict[str, Any]:
    payload = {
        "schema_version": 1,
        "updated_at": time.time(),
        "state": state,
        "source": source,
        "model_reaction_policy": model_reaction_policy,
        "recommended_model_trigger": recommended_model_trigger,
        "segment_id": segment.segment_id if segment else "",
        "input_id": decision.input_id if decision else "",
        "turn_decision": decision.turn_decision if decision else "",
        "speaker_role": decision.speaker_role if decision else "",
        "echo_score": decision.echo_score if decision else 0.0,
        "voiceprint_decision": decision.voiceprint_decision if decision else "",
        "voiceprint_profile_id": decision.voiceprint_profile_id if decision else "",
        "speaker_similarity": decision.speaker_similarity if decision else 0.0,
        "started_at": segment.started_at if segment else 0.0,
        "expected_end_at": segment.expected_end_at if segment else 0.0,
        "suppression_duration_s": (
            max(0.35, segment.expected_end_at - time.time() + 0.35)
            if segment
            else 0.0
        ),
    }
    _write_bb("session/lineb_voice_activity", payload)
    return payload


def _write_bb(key: str, value: Any) -> None:
    bb = open_bb_client(name="lineb_audio_guard", writer=WRITER)
    bb.set(key, value)


def _matching_segment(observed_at: float, duration_s: float) -> TtsSegment | None:
    end = observed_at + max(0.0, duration_s)
    for segment in reversed(_recent_segments):
        window_start = segment.started_at - DEFAULT_ECHO_WINDOW_S
        window_end = segment.expected_end_at + DEFAULT_ECHO_WINDOW_S
        if observed_at <= window_end and end >= window_start:
            return segment
    return None


def _score(
    match: TtsSegment | None,
    voiceprint_hash: str,
    echo_score: float | None,
    asr_text: str = "",
) -> float:
    scores: list[float] = []
    if echo_score is not None:
        scores.append(max(0.0, min(1.0, _float_or_default(echo_score, 0.0))))
    if (
        match is not None
        and voiceprint_hash
        and match.voiceprint_hash
        and voiceprint_hash == match.voiceprint_hash
    ):
        scores.append(1.0)
    if match is not None:
        text_score = _text_echo_score(match.text_summary, asr_text)
        if text_score > 0.0:
            scores.append(text_score)
        scores.append(0.5)
    return max(scores) if scores else 0.0


def _text_echo_score(tts_text: str, asr_text: str) -> float:
    expected = _normalize_echo_text(tts_text)
    observed = _normalize_echo_text(asr_text)
    if len(expected) < 4 or len(observed) < 4:
        return 0.0
    if expected in observed or observed in expected:
        return 0.95
    return SequenceMatcher(None, expected, observed).ratio()


def _normalize_echo_text(text: str) -> str:
    return "".join(ch.lower() for ch in str(text or "") if ch.isalnum())


def _voiceprint_payload(
    *,
    speaker_similarity: float | None,
    voiceprint_decision: str,
    speaker_label: str,
    voiceprint_profile_id: str,
    voiceprint_enabled: bool | None,
    voiceprint_provider: str,
    voiceprint_manifest_path: str,
    voiceprint_threshold_accept: float | None,
    voiceprint_threshold_reject: float | None,
) -> dict[str, Any]:
    decision = str(voiceprint_decision or "").strip().lower()
    label = str(speaker_label or "").strip().lower()
    explicit = {
        "decision": decision or _decision_from_label(label),
        "speaker_role": _speaker_role_from_label(label, decision),
        "similarity": _float_or_default(speaker_similarity, 0.0),
        "profile_id": str(voiceprint_profile_id or ""),
        "source": "explicit",
    }
    if _voiceprint_rejects(explicit):
        return explicit
    if speaker_similarity is not None:
        try:
            from parrot.brain.lineb_voiceprint import decision_payload_for_similarity

            return decision_payload_for_similarity(
                speaker_similarity,
                enabled=voiceprint_enabled,
                manifest_path=voiceprint_manifest_path or None,
                provider=voiceprint_provider,
                profile_id=voiceprint_profile_id,
                threshold_accept=voiceprint_threshold_accept,
                threshold_reject=voiceprint_threshold_reject,
            )
        except Exception:
            return {
                "decision": "not_configured",
                "speaker_role": "unknown",
                "similarity": _float_or_default(speaker_similarity, 0.0),
                "profile_id": str(voiceprint_profile_id or ""),
                "source": "speaker_similarity_fallback",
            }
    if _voiceprint_accepts(explicit):
        return {
            "decision": "untrusted_owner_claim",
            "speaker_role": "unknown",
            "similarity": 0.0,
            "profile_id": str(voiceprint_profile_id or ""),
            "source": "explicit_untrusted",
        }
    if decision:
        return explicit
    if label:
        return {
            "decision": _decision_from_label(label),
            "speaker_role": _speaker_role_from_label(label, ""),
            "similarity": _float_or_default(speaker_similarity, 0.0),
            "profile_id": str(voiceprint_profile_id or ""),
            "source": "speaker_label",
        }
    return {}


def _voiceprint_accepts(payload: dict[str, Any]) -> bool:
    decision = str(payload.get("decision") or "").strip().lower()
    role = str(payload.get("speaker_role") or "").strip().lower()
    return decision in {"owner_user", "accepted", "verified_user"} or role == "user"


def _voiceprint_rejects(payload: dict[str, Any]) -> bool:
    decision = str(payload.get("decision") or "").strip().lower()
    role = str(payload.get("speaker_role") or "").strip().lower()
    return decision in {"other_speaker", "rejected", "speaker_rejected"} or role == "other"


def _decision_from_label(label: str) -> str:
    if label in {"owner", "user", "enrolled_user"}:
        return "owner_user"
    if label in {"other", "unknown_speaker", "guest"}:
        return "other_speaker"
    return "uncertain"


def _speaker_role_from_label(label: str, decision: str) -> str:
    if label in {"owner", "user", "enrolled_user"}:
        return "user"
    if label in {"other", "unknown_speaker", "guest"}:
        return "other"
    if decision in {"owner_user", "accepted", "verified_user"}:
        return "user"
    if decision in {"other_speaker", "rejected", "speaker_rejected"}:
        return "other"
    if decision:
        return "uncertain"
    return ""


def _risk_for_route(output_route: str, voiceprint_enabled: bool) -> str:
    if _is_isolated_output(output_route):
        return "low"
    if _is_speaker_output(output_route):
        return "medium" if voiceprint_enabled else "high"
    return "low" if voiceprint_enabled else "medium"


def _default_handling(*, output_route: str, voiceprint_enabled: bool) -> str:
    if _is_isolated_output(output_route):
        return "isolated_route"
    if voiceprint_enabled:
        return "voiceprint_gate"
    return "monitor_only"


def _echo_summary(output_route: str, risk: str, handling: str) -> str:
    return (
        f"output_route={output_route}; echo_risk={risk}; "
        f"handling_mode={handling}."
    )


def _is_isolated_output(output_route: str) -> bool:
    return output_route.lower() in {
        "headphones",
        "headset",
        "wired_headset",
        "bluetooth",
        "bluetooth_headset",
        "bluetooth_sco",
        "bluetooth_a2dp",
        "earpiece",
    }


def _is_speaker_output(output_route: str) -> bool:
    return output_route.lower() in {"speaker", "phone_speaker", "loudspeaker"}


def _clean(value: str, fallback: str) -> str:
    text = str(value or "").strip().lower()
    return text or fallback


def _float_or_default(value: Any, fallback: float) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return fallback
    return parsed if math.isfinite(parsed) else fallback


__all__ = [
    "MicInputDecision",
    "TtsSegment",
    "apply_audio_route_policy",
    "classify_mic_input",
    "latest_mic_decision",
    "recent_tts_segments",
    "register_tts_segment",
    "reset_lineb_audio_guard_for_test",
]
