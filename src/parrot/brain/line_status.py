"""LineA/LineB readiness and audio-risk status for App menus.

The actual voice session is still built in ``brain.agent``. This module is a
side-effect-free read model for startup RoomSetting, HUD/menu surfaces, and
the Web monitor.
"""

from __future__ import annotations

import importlib.util
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from parrot.brain.linea_turn_policy import linea_turn_policy_status
from parrot.brain.line_profile import LineProfile, get_line_profile_loader
from parrot.brain.preset_loader import DEFAULT_LINE_ID


LINE_A_ID = "line_a"
LINE_B_ID = "line_b"


@dataclass(frozen=True)
class ComponentReadiness:
    component_id: str
    state: str
    health: str = "ok"
    summary: str = ""
    refs: dict[str, Any] = field(default_factory=dict)

    def as_json(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class VoiceprintStatus:
    state: str
    speaker_state: str
    summary: str
    enabled: bool = False
    refs: dict[str, Any] = field(default_factory=dict)

    def as_json(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class EchoRiskStatus:
    risk_level: str
    handling_mode: str
    summary: str
    route: dict[str, Any] = field(default_factory=dict)

    def as_json(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class LineSummary:
    """Startup-facing Brain pipeline option."""

    line_id: str
    display_name: str
    state: str
    health: str = "ok"
    summary: str = ""
    readiness: dict[str, Any] = field(default_factory=dict)
    components: tuple[ComponentReadiness, ...] = ()
    voiceprint: VoiceprintStatus | None = None
    echo: EchoRiskStatus | None = None
    line_profile: dict[str, Any] = field(default_factory=dict)
    refs: dict[str, Any] = field(default_factory=dict)

    def as_json(self) -> dict[str, Any]:
        data = asdict(self)
        data["components"] = [c.as_json() for c in self.components]
        data["voiceprint"] = self.voiceprint.as_json() if self.voiceprint else {}
        data["echo"] = self.echo.as_json() if self.echo else {}
        data["refs"] = dict(self.refs)
        return data


def list_lines() -> tuple[LineSummary, ...]:
    """Return LineA/LineB selector status without creating AgentSessions."""
    profile_loader = get_line_profile_loader()
    line_a_profile = profile_loader.profile_for_line(LINE_A_ID)
    line_b_profile = profile_loader.profile_for_line(LINE_B_ID)
    audio_route = _audio_route_policy()
    line_a_echo = _echo_status(
        line_id=LINE_A_ID,
        audio_route=audio_route,
        profile=line_a_profile,
    )
    line_b_voiceprint = _voiceprint_status(audio_route, line_b_profile)
    line_b_echo = _echo_status(
        line_id=LINE_B_ID,
        audio_route=audio_route,
        profile=line_b_profile,
        voiceprint=line_b_voiceprint,
    )
    line_b_runtime = _line_b_runtime(audio_route)
    line_a_turn_policy = linea_turn_policy_status()

    line_a = LineSummary(
        line_id=LINE_A_ID,
        display_name="LineA Gemini Realtime",
        state="ready",
        health="ok",
        summary="Default Gemini Realtime voice pipeline.",
        readiness={
            "pipeline": "gemini_realtime",
            "turn_detection": line_a_turn_policy["turn_detection"],
            "turn_policy": line_a_turn_policy["policy"],
            "barge_in_enabled": line_a_turn_policy["barge_in_enabled"],
            "activity_handling": line_a_turn_policy["activity_handling"],
            "barge_in_env_key": line_a_turn_policy["env_key"],
            "recommended_audio_route": "headphones_or_isolated_output",
            "line_profile_id": line_a_profile.line_profile_id,
        },
        components=(
            ComponentReadiness(
                "line_a.gemini_realtime",
                "ready",
                summary="Gemini Realtime session is selected by default.",
            ),
        ),
        voiceprint=VoiceprintStatus(
            state="not_available",
            speaker_state="native_model_black_box",
            summary="LineA does not expose a local voiceprint gate.",
            enabled=False,
        ),
        echo=line_a_echo,
        line_profile=line_a_profile.as_json(),
    )

    line_b_components = _line_b_components(line_b_profile)
    line_b_state, line_b_health, line_b_summary = _line_b_overall(line_b_components)
    line_b = LineSummary(
        line_id=LINE_B_ID,
        display_name="LineB STT-LLM-TTS",
        state=line_b_state,
        health=line_b_health,
        summary=line_b_summary,
        readiness={
            "pipeline": "stt_llm_tts",
            "line_profile_id": line_b_profile.line_profile_id,
            "asr_profile_id": line_b_profile.asr.asr_profile_id,
            "tts_profile_id": line_b_profile.tts.tts_profile_id,
            "tts_provider": line_b_profile.tts.provider,
            "voiceprint_profile_id": line_b_profile.voiceprint.voiceprint_profile_id,
            "echo_policy_id": line_b_profile.echo.echo_policy_id,
            "llm_model": line_b_profile.llm.model,
            "google_api_key": _component_state(line_b_components, "google_api_key"),
            "google_adc": _component_state(line_b_components, "google_adc"),
            "asr": _component_state(line_b_components, "asr"),
            "tts": _component_state(line_b_components, "tts"),
            "vad": _component_state(line_b_components, "vad"),
            "voiceprint": line_b_voiceprint.state,
            "echo_risk": line_b_echo.risk_level,
            "echo_handling_mode": line_b_echo.handling_mode,
            "recent_tts_segment_count": line_b_runtime["recent_tts_segment_count"],
            "last_input_decision": line_b_runtime["last_input_decision"],
            "last_speaker_role": line_b_runtime["last_speaker_role"],
            "voice_activity_state": line_b_runtime["voice_activity_state"],
        },
        components=line_b_components,
        voiceprint=line_b_voiceprint,
        echo=line_b_echo,
        line_profile=line_b_profile.as_json(),
        refs=line_b_runtime["refs"],
    )
    return (line_a, line_b)


def line_status(line_id: str) -> LineSummary | None:
    safe = str(line_id or DEFAULT_LINE_ID).strip().lower()
    for line in list_lines():
        if line.line_id == safe:
            return line
    return None


def active_line_id() -> str:
    """Return the **selected / saved** Line id (BB first, env second).

    See :func:`running_line_id` for what is *actually* live in the
    current Brain process. The two answers can disagree on cold-start
    Line switches: an applied RoomProfile writes ``global/active_line_id``
    to BB, but the running ``PARROT_LLM_PIPELINE`` env was fixed at
    process boot and only an external supervisor can swap it. Callers
    should pick deliberately:

    * preference / RoomSetting UI / "what would START use next"
      → :func:`active_line_id` (this function).
    * runtime status / Web monitor / canvas voice pipeline tile / any
      "what's actually serving voice right now" — must call
      :func:`running_line_id`.
    """
    value = _bb_value("global/active_line_id", "")
    if isinstance(value, str) and value:
        return value
    env_value = os.getenv("PARROT_LLM_PIPELINE", "").strip().lower()
    if env_value in {LINE_A_ID, LINE_B_ID}:
        return env_value
    profile_id = str(
        _bb_value("global/active_line_profile_id", "")
        or os.getenv("PARROT_LINE_PROFILE", "")
        or os.getenv("PARROT_ACTIVE_LINE_PROFILE_ID", "")
    ).strip()
    if profile_id:
        return get_line_profile_loader().load(profile_id).line_id
    return DEFAULT_LINE_ID


def running_line_id() -> str:
    """Return the **live** Line id of the running Brain process.

    Mirrors :func:`parrot.brain.agent._resolve_pipeline` exactly so the
    canvas voice tile, RoomSetting compatibility resolver, and any
    "what's actually serving voice right now" query agree on a single
    answer.

    Resolution order (highest first; see
    ``parrot.castle.runtime_config`` for full layering rationale):

    1. ``data/runtime_config.json`` (Castle Orchestrator-controlled).
    2. Process env ``PARROT_LLM_PIPELINE``.
    3. Default (``line_a``).

    Note: this function intentionally **does not** read BB
    ``global/active_line_id``. That key is "what the user *selected*"
    and is consulted by :func:`active_line_id`. Mixing it in here
    would re-introduce the Round 5 Bug O drift symptom.

    Defaults to ``line_a`` if neither file nor env yields a valid
    value (mirrors agent's ``_DEFAULT_PIPELINE``).
    """
    try:
        from parrot.castle.runtime_config import resolve_runtime_config

        resolved = resolve_runtime_config()
        # Only honour file/env source for "running"; BB drift would
        # mask the cold-start invariant the audit Round 5 set up.
        if resolved.source.get("line_id") in {"file", "env", "default"}:
            line_id = resolved.line_id
            if line_id in {LINE_A_ID, LINE_B_ID}:
                return line_id
    except Exception:
        pass
    raw = os.getenv("PARROT_LLM_PIPELINE", DEFAULT_LINE_ID).strip().lower()
    if raw in {LINE_A_ID, LINE_B_ID}:
        return raw
    return DEFAULT_LINE_ID


def active_line_status() -> LineSummary:
    """Status for the **selected / saved** Line. See :func:`active_line_id`."""
    return line_status(active_line_id()) or list_lines()[0]


def running_line_status() -> LineSummary:
    """Status for the **running** Line. See :func:`running_line_id`."""
    return line_status(running_line_id()) or list_lines()[0]


def _line_b_components(profile: LineProfile) -> tuple[ComponentReadiness, ...]:
    api_key_ready = bool(os.getenv("GOOGLE_API_KEY"))
    adc_state, adc_summary, adc_refs = _adc_state()
    stt_model = profile.asr.model
    stt_languages = ",".join(profile.asr.languages)
    tts_voice = profile.tts.voice_name
    tts_language = profile.tts.language
    tts_provider = profile.tts.provider
    text_model = profile.llm.model
    vad_ready = importlib.util.find_spec("livekit.plugins.silero") is not None
    asr_profile_ready = bool(stt_model and profile.asr.languages)
    tts_profile_ready = bool(tts_voice and tts_language)
    cartesia_tts = _is_cartesia_tts(tts_provider)
    cartesia_key_ready = bool(os.getenv("CARTESIA_API_KEY"))
    cartesia_plugin_ready = (
        importlib.util.find_spec("livekit.plugins.cartesia") is not None
        if cartesia_tts
        else True
    )
    tts_auth_ready = cartesia_key_ready if cartesia_tts else adc_state == "ready"
    tts_ready = tts_profile_ready and tts_auth_ready and cartesia_plugin_ready

    api_key = ComponentReadiness(
        "google_api_key",
        "ready" if api_key_ready else "blocked",
        "ok" if api_key_ready else "error",
        "GOOGLE_API_KEY is present." if api_key_ready else "GOOGLE_API_KEY is missing.",
        {
            "model": text_model,
            "line_profile_id": profile.line_profile_id,
            "provider": profile.llm.provider,
        },
    )
    adc = ComponentReadiness(
        "google_adc",
        adc_state,
        "ok" if adc_state == "ready" else "error",
        adc_summary,
        adc_refs,
    )
    asr = ComponentReadiness(
        "asr",
        "ready" if adc_state == "ready" and asr_profile_ready else "blocked",
        "ok" if adc_state == "ready" and asr_profile_ready else "error",
        "Google STT can use ADC and selected ASR profile."
        if adc_state == "ready" and asr_profile_ready
        else "Google STT needs ADC plus model/languages.",
        {
            "provider": profile.asr.provider,
            "model": stt_model,
            "languages": stt_languages,
            "asr_profile_id": profile.asr.asr_profile_id,
        },
    )
    tts = ComponentReadiness(
        "tts",
        "ready" if tts_ready else "blocked",
        "ok" if tts_ready else "error",
        _tts_summary(profile, tts_profile_ready, tts_auth_ready, cartesia_plugin_ready),
        {
            "provider": tts_provider,
            "voice": tts_voice,
            "language": tts_language,
            "tts_profile_id": profile.tts.tts_profile_id,
            "style_note": profile.tts.style_note,
            "cartesia_api_key": "ready" if cartesia_key_ready else "missing",
            "cartesia_plugin": "ready" if cartesia_plugin_ready else "missing",
        },
    )
    vad = ComponentReadiness(
        "vad",
        "ready" if vad_ready else "degraded",
        "ok" if vad_ready else "warning",
        "Silero VAD plugin is importable." if vad_ready else "Silero VAD plugin was not found.",
        {"provider": "silero.VAD"},
    )
    voiceprint_verifier = _voiceprint_verifier_component(profile)
    return (api_key, adc, asr, tts, vad, voiceprint_verifier)


def _line_b_overall(
    components: tuple[ComponentReadiness, ...],
) -> tuple[str, str, str]:
    api_key = _component_state(components, "google_api_key")
    adc = _component_state(components, "google_adc")
    asr = _component_state(components, "asr")
    tts = _component_state(components, "tts")
    vad = _component_state(components, "vad")
    voiceprint_verifier = _component_state(components, "voiceprint_verifier")
    if api_key == "blocked":
        return ("blocked", "error", "LineB needs GOOGLE_API_KEY for Gemini text LLM.")
    if tts == "blocked":
        return ("blocked", "error", "LineB selected TTS profile is missing a usable voice.")
    if asr == "blocked":
        return ("blocked", "error", "LineB selected ASR profile is missing model/languages.")
    if adc == "blocked":
        return (
            "degraded",
            "warning",
            "LineB LLM is configured; Google ADC for STT/TTS is missing.",
        )
    if vad == "degraded":
        return (
            "degraded",
            "warning",
            "LineB credentials look ready, but Silero VAD import is not confirmed.",
        )
    if voiceprint_verifier in {"pending_enrollment", "degraded", "not_configured"}:
        return (
            "degraded",
            "warning",
            "LineB is configured, but owner voiceprint verification still needs enrollment/runtime setup.",
        )
    return ("ready", "ok", "LineB STT/LLM/TTS environment looks configured.")


def _is_cartesia_tts(provider: str) -> bool:
    text = str(provider or "").strip().lower()
    return text == "cartesia" or text.startswith("cartesia.")


def _tts_summary(
    profile: LineProfile,
    profile_ready: bool,
    auth_ready: bool,
    plugin_ready: bool,
) -> str:
    if _is_cartesia_tts(profile.tts.provider):
        if profile_ready and auth_ready and plugin_ready:
            return "Cartesia TTS can use the selected voice."
        missing = []
        if not profile_ready:
            missing.append("tts.voice_name/language")
        if not auth_ready:
            missing.append("CARTESIA_API_KEY")
        if not plugin_ready:
            missing.append("livekit.plugins.cartesia")
        return "Cartesia TTS needs " + ", ".join(missing) + "."
    if profile_ready and auth_ready:
        return "Google TTS can use ADC and selected TTS voice."
    return "Google TTS needs ADC plus tts.voice_name/language."


def _voiceprint_verifier_component(profile: LineProfile) -> ComponentReadiness:
    if not profile.voiceprint.enabled:
        return ComponentReadiness(
            "voiceprint_verifier",
            "disabled",
            "warning",
            "Owner voiceprint verification is disabled for this LineProfile.",
            profile.voiceprint.as_json(),
        )
    try:
        from parrot.brain.lineb_voiceprint import runtime_status

        status = runtime_status(
            enabled=profile.voiceprint.enabled,
            manifest_path=profile.voiceprint.manifest_path or None,
            provider=profile.voiceprint.provider,
            profile_id=profile.voiceprint.voiceprint_profile_id,
            threshold_accept=profile.voiceprint.threshold_accept,
            threshold_reject=profile.voiceprint.threshold_reject,
        )
    except Exception as exc:  # noqa: BLE001 - status read should never break menus.
        return ComponentReadiness(
            "voiceprint_verifier",
            "degraded",
            "warning",
            f"Voiceprint verifier status failed: {type(exc).__name__}: {exc}",
            profile.voiceprint.as_json(),
        )
    if status.state == "disabled":
        return ComponentReadiness(
            "voiceprint_verifier",
            "not_configured",
            "warning",
            (
                "LineProfile enables voiceprint, but "
                "PARROT_LINEB_VOICEPRINT_ENABLED is not active."
            ),
            {
                **profile.voiceprint.as_json(),
                "runtime": status.as_json(),
            },
        )
    return ComponentReadiness(
        "voiceprint_verifier",
        status.state,
        status.health,
        status.summary,
        {
            **profile.voiceprint.as_json(),
            "runtime": status.as_json(),
        },
    )


def _adc_state() -> tuple[str, str, dict[str, Any]]:
    json_payload = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON", "")
    if json_payload.strip():
        return (
            "ready",
            "GOOGLE_APPLICATION_CREDENTIALS_JSON is present.",
            {"source": "GOOGLE_APPLICATION_CREDENTIALS_JSON"},
        )
    path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "").strip()
    if not path:
        return (
            "blocked",
            "GOOGLE_APPLICATION_CREDENTIALS is missing.",
            {"source": "GOOGLE_APPLICATION_CREDENTIALS"},
        )
    exists = Path(path).expanduser().is_file()
    return (
        "ready" if exists else "blocked",
        "GOOGLE_APPLICATION_CREDENTIALS file exists."
        if exists
        else "GOOGLE_APPLICATION_CREDENTIALS file does not exist.",
        {"source": "GOOGLE_APPLICATION_CREDENTIALS", "path": path, "exists": exists},
    )


def _voiceprint_status(
    audio_route: dict[str, Any],
    profile: LineProfile,
) -> VoiceprintStatus:
    bb_value = audio_route.get("voiceprint")
    if isinstance(bb_value, dict):
        state = str(bb_value.get("state") or "unknown")
        return VoiceprintStatus(
            state=state,
            speaker_state=str(bb_value.get("speaker_state") or "unknown"),
            summary=str(bb_value.get("summary") or "Voiceprint state from audio route policy."),
            enabled=bool(bb_value.get("enabled", state in {"ready", "monitoring"})),
            refs=dict(bb_value),
        )

    if profile.voiceprint.enabled:
        return VoiceprintStatus(
            state="monitoring",
            speaker_state=profile.voiceprint.speaker_state,
            summary=(
                "Voiceprint speaker policy is enabled; classifier integration is still "
                "provisional."
            ),
            enabled=True,
            refs=profile.voiceprint.as_json(),
        )
    return VoiceprintStatus(
        state="not_configured",
        speaker_state=profile.voiceprint.speaker_state,
        summary="Voiceprint/speaker gate is disabled by the active LineProfile.",
        enabled=False,
        refs=profile.voiceprint.as_json(),
    )


def _echo_status(
    *,
    line_id: str,
    audio_route: dict[str, Any],
    profile: LineProfile,
    voiceprint: VoiceprintStatus | None = None,
) -> EchoRiskStatus:
    route_echo = audio_route.get("echo")
    if isinstance(route_echo, dict):
        return EchoRiskStatus(
            risk_level=str(route_echo.get("risk_level") or "unknown"),
            handling_mode=str(route_echo.get("handling_mode") or "monitor_only"),
            summary=str(route_echo.get("summary") or "Echo status from audio route policy."),
            route=dict(audio_route),
        )

    output_route = str(
        audio_route.get("output_route")
        or profile.echo.output_route
        or os.getenv("PARROT_AUDIO_OUTPUT_ROUTE", "unknown")
    ).lower()
    handling_override = (
        os.getenv("PARROT_LINEB_ECHO_HANDLING_MODE", "").strip()
        or profile.echo.handling_mode
    )

    isolated = output_route in {
        "headphones",
        "headset",
        "wired_headset",
        "bluetooth",
        "bluetooth_headset",
        "bluetooth_sco",
        "bluetooth_a2dp",
        "earpiece",
    }
    speaker = output_route in {"speaker", "phone_speaker", "loudspeaker"}

    if line_id == LINE_A_ID:
        if isolated:
            return EchoRiskStatus(
                risk_level="low",
                handling_mode=handling_override or "isolated_route",
                summary="LineA is on an isolated output route.",
                route=dict(audio_route),
            )
        return EchoRiskStatus(
            risk_level="high" if speaker else "medium",
            handling_mode=handling_override or "headphones_recommended",
            summary="LineA uses native turn detection; isolated audio output is recommended.",
            route=dict(audio_route),
        )

    if isolated:
        return EchoRiskStatus(
            risk_level="low",
            handling_mode=handling_override or "isolated_route",
            summary="LineB is on an isolated output route.",
            route=dict(audio_route),
        )
    if voiceprint and voiceprint.enabled:
        return EchoRiskStatus(
            risk_level="medium" if speaker else "low",
            handling_mode=handling_override or "voiceprint_gate_pending",
            summary="LineB voiceprint/speaker gate is enabled for echo handling.",
            route=dict(audio_route),
        )
    return EchoRiskStatus(
        risk_level="high" if speaker else "medium",
        handling_mode=handling_override or "monitor_only",
        summary="LineB can expose echo state, but voiceprint echo suppression is not configured.",
        route=dict(audio_route),
    )


def _audio_route_policy() -> dict[str, Any]:
    value = _bb_value("session/audio_route_policy", {})
    return value if isinstance(value, dict) else {}


def _line_b_runtime(audio_route: dict[str, Any]) -> dict[str, Any]:
    segments = _recent_tts_segments()
    decision = _last_input_decision()
    voice_activity = _voice_activity()
    return {
        "recent_tts_segment_count": len(segments),
        "last_input_decision": str(decision.get("turn_decision") or "none")
        if decision
        else "none",
        "last_speaker_role": str(decision.get("speaker_role") or "unknown")
        if decision
        else "unknown",
        "voice_activity_state": str(voice_activity.get("state") or "idle"),
        "refs": {
            "audio_route_policy": dict(audio_route),
            "recent_tts_segments": segments[-5:],
            "last_input_decision": decision,
            "voice_activity": voice_activity,
        },
    }


def _recent_tts_segments() -> list[dict[str, Any]]:
    value = _bb_value("session/lineb_recent_tts_segments", [])
    if isinstance(value, list):
        return [dict(item) for item in value if isinstance(item, dict)]
    try:
        from parrot.brain.lineb_audio_guard import recent_tts_segments

        return [segment.as_json() for segment in recent_tts_segments()]
    except Exception:
        return []


def _last_input_decision() -> dict[str, Any]:
    value = _bb_value("transient/lineb_last_input_decision", {})
    if isinstance(value, dict):
        return dict(value)
    try:
        from parrot.brain.lineb_audio_guard import latest_mic_decision

        decision = latest_mic_decision()
        return decision.as_json() if decision else {}
    except Exception:
        return {}


def _voice_activity() -> dict[str, Any]:
    value = _bb_value("session/lineb_voice_activity", {})
    return dict(value) if isinstance(value, dict) else {}


def _bb_value(key: str, default: Any) -> Any:
    try:
        from parrot.scheduler.blackboard import open_bb_client

        bb = open_bb_client(name="line_status.read", writer=None)
        value = bb.get(key)
        return default if value is None else value
    except Exception:
        return default


def _component_state(components: tuple[ComponentReadiness, ...], component_id: str) -> str:
    for component in components:
        if component.component_id == component_id:
            return component.state
    return "unknown"


def _truthy(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on", "enabled"}


__all__ = [
    "ComponentReadiness",
    "EchoRiskStatus",
    "LINE_A_ID",
    "LINE_B_ID",
    "LineSummary",
    "VoiceprintStatus",
    "active_line_id",
    "active_line_status",
    "line_status",
    "list_lines",
    "running_line_id",
    "running_line_status",
]
