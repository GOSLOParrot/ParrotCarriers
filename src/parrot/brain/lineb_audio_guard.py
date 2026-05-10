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
) -> MicInputDecision:
    """Classify a mic fragment as user input, agent echo, noise, or uncertain."""
    global _last_decision

    now = time.time() if observed_at is None else _float_or_default(observed_at, time.time())
    match = _matching_segment(now, max(0.0, _float_or_default(duration_s, 0.0)))
    score = _score(match, voiceprint_hash, echo_score)

    if match is not None and score >= DEFAULT_ECHO_SCORE_THRESHOLD:
        speaker_role = "agent"
        turn_decision = "agent_echo"
        reason = "matches_recent_tts_segment"
    elif match is None and echo_score is not None and score >= DEFAULT_ECHO_SCORE_THRESHOLD:
        speaker_role = "uncertain"
        turn_decision = "uncertain"
        reason = "high_echo_score_without_recent_tts"
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
            recommended_model_trigger="lineb_noise",
        )
    if decision.turn_decision == "uncertain":
        return _write_voice_activity(
            state="listening_uncertain",
            source="mic_input_classifier",
            decision=decision,
            model_reaction_policy="subtle_listen_only",
            recommended_model_trigger="lineb_uncertain_input",
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
) -> float:
    if echo_score is not None:
        return max(0.0, min(1.0, _float_or_default(echo_score, 0.0)))
    if (
        match is not None
        and voiceprint_hash
        and match.voiceprint_hash
        and voiceprint_hash == match.voiceprint_hash
    ):
        return 1.0
    if match is not None:
        return 0.5
    return 0.0


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
    return output_route.lower() in {"headphones", "headset", "bluetooth", "bluetooth_headset"}


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
