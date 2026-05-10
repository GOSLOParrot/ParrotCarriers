"""Configurable LineA/LineB profile loader for startup RoomSetting.

LineB started as env-var-only plumbing. This module makes the same choices
visible and saveable from the App: ASR, TTS, voiceprint, and echo policy.
Environment variables still override saved profiles for local development.
"""

from __future__ import annotations

import importlib.util
import json
import math
import os
from dataclasses import asdict, dataclass, field, replace
from pathlib import Path
from typing import Any, Mapping

from parrot.scheduler.blackboard import open_bb_client


LINE_PROFILES_DIR_ENV = "PARROT_LINE_PROFILES_DIR"
ACTIVE_LINE_PROFILE_ENV = "PARROT_LINE_PROFILE"
ACTIVE_LINE_PROFILE_ID_ENV = "PARROT_ACTIVE_LINE_PROFILE_ID"
DEFAULT_LINEA_PROFILE_ID = "linea_gemini_realtime"
DEFAULT_LINEB_PROFILE_ID = "lineb_google_default"
DEFAULT_LINE_PROFILE_ID = DEFAULT_LINEA_PROFILE_ID
LINE_PROFILE_SCHEMA_VERSION = 1


@dataclass(frozen=True)
class LlmProfile:
    provider: str = "google.LLM"
    model: str = "gemini-2.5-flash"

    @classmethod
    def from_json(cls, raw: Mapping[str, Any] | None) -> "LlmProfile":
        data = dict(raw or {})
        return cls(
            provider=_clean_text(data.get("provider"), "google.LLM"),
            model=_clean_text(data.get("model"), "gemini-2.5-flash"),
        )

    def as_json(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AsrProfile:
    asr_profile_id: str = "google_stt_default"
    provider: str = "google.STT"
    model: str = "latest_long"
    languages: tuple[str, ...] = ("cmn-CN", "en-US")

    @classmethod
    def from_json(cls, raw: Mapping[str, Any] | None) -> "AsrProfile":
        data = dict(raw or {})
        return cls(
            asr_profile_id=_clean_text(data.get("asr_profile_id"), "google_stt_default"),
            provider=_clean_text(data.get("provider"), "google.STT"),
            model=_clean_text(data.get("model"), "latest_long"),
            languages=_tuple_text(data.get("languages")) or ("cmn-CN", "en-US"),
        )

    def as_json(self) -> dict[str, Any]:
        data = asdict(self)
        data["languages"] = list(self.languages)
        return data


@dataclass(frozen=True)
class TtsProfile:
    tts_profile_id: str = "google_tts_default"
    provider: str = "google.TTS"
    language: str = "cmn-CN"
    voice_name: str = "cmn-CN-Wavenet-D"
    style_note: str = ""
    voice_asset_manifest_path: str = ""
    sample_audio_root: str = ""
    rights_mode: str = ""

    @classmethod
    def from_json(cls, raw: Mapping[str, Any] | None) -> "TtsProfile":
        data = dict(raw or {})
        return cls(
            tts_profile_id=_clean_text(data.get("tts_profile_id"), "google_tts_default"),
            provider=_clean_text(data.get("provider"), "google.TTS"),
            language=_clean_text(data.get("language"), "cmn-CN"),
            voice_name=_clean_text(data.get("voice_name"), ""),
            style_note=str(data.get("style_note") or ""),
            voice_asset_manifest_path=str(data.get("voice_asset_manifest_path") or ""),
            sample_audio_root=str(data.get("sample_audio_root") or ""),
            rights_mode=str(data.get("rights_mode") or ""),
        )

    def as_json(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class VoiceprintProfile:
    voiceprint_profile_id: str = "voiceprint_monitor_default"
    enabled: bool = False
    speaker_policy: str = "monitor_only"
    speaker_state: str = "unknown"
    provider: str = ""
    manifest_path: str = ""
    data_root: str = ""
    threshold_accept: float = 0.78
    threshold_reject: float = 0.62

    @classmethod
    def from_json(cls, raw: Mapping[str, Any] | None) -> "VoiceprintProfile":
        data = dict(raw or {})
        return cls(
            voiceprint_profile_id=_clean_text(
                data.get("voiceprint_profile_id"),
                "voiceprint_monitor_default",
            ),
            enabled=_bool_from_raw(data.get("enabled"), False),
            speaker_policy=_clean_text(data.get("speaker_policy"), "monitor_only"),
            speaker_state=_clean_text(data.get("speaker_state"), "unknown"),
            provider=str(data.get("provider") or ""),
            manifest_path=str(data.get("manifest_path") or ""),
            data_root=str(data.get("data_root") or ""),
            threshold_accept=_float_from_raw(data.get("threshold_accept"), 0.78),
            threshold_reject=_float_from_raw(data.get("threshold_reject"), 0.62),
        )

    def as_json(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class EchoPolicy:
    echo_policy_id: str = "echo_isolated_default"
    input_route: str = "unknown"
    output_route: str = "headphones"
    handling_mode: str = "isolated_route"
    microphone_enabled: bool = True
    speaker_output_enabled: bool | None = None

    @classmethod
    def from_json(cls, raw: Mapping[str, Any] | None) -> "EchoPolicy":
        data = dict(raw or {})
        speaker_output = data.get("speaker_output_enabled")
        return cls(
            echo_policy_id=_clean_text(data.get("echo_policy_id"), "echo_isolated_default"),
            input_route=_clean_text(data.get("input_route"), "unknown"),
            output_route=_clean_text(data.get("output_route"), "headphones"),
            handling_mode=_clean_text(data.get("handling_mode"), "isolated_route"),
            microphone_enabled=_bool_from_raw(data.get("microphone_enabled"), True),
            speaker_output_enabled=(
                None if speaker_output is None else _bool_from_raw(speaker_output, False)
            ),
        )

    def as_json(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class LineProfile:
    line_profile_id: str
    display_name: str
    line_id: str = "line_b"
    llm: LlmProfile = field(default_factory=LlmProfile)
    asr: AsrProfile = field(default_factory=AsrProfile)
    tts: TtsProfile = field(default_factory=TtsProfile)
    voiceprint: VoiceprintProfile = field(default_factory=VoiceprintProfile)
    echo: EchoPolicy = field(default_factory=EchoPolicy)
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def builtin_linea(cls) -> "LineProfile":
        return cls(
            line_profile_id=DEFAULT_LINEA_PROFILE_ID,
            display_name="LineA Gemini Realtime",
            line_id="line_a",
            llm=LlmProfile(provider="google.realtime.RealtimeModel", model="gemini-live"),
            asr=AsrProfile(asr_profile_id="native_realtime_asr", provider="native_model"),
            tts=TtsProfile(
                tts_profile_id="native_realtime_tts",
                provider="native_model",
                language="native",
                voice_name="native",
            ),
            voiceprint=VoiceprintProfile(
                voiceprint_profile_id="not_available",
                enabled=False,
                speaker_policy="native_model_black_box",
                speaker_state="native_model_black_box",
            ),
            echo=EchoPolicy(
                echo_policy_id="linea_headphones_recommended",
                output_route="unknown",
                handling_mode="headphones_recommended",
            ),
            metadata={"builtin": True},
        )

    @classmethod
    def builtin_lineb(cls) -> "LineProfile":
        return cls(
            line_profile_id=DEFAULT_LINEB_PROFILE_ID,
            display_name="LineB Google Default",
            line_id="line_b",
            metadata={"builtin": True},
        )

    @classmethod
    def from_json(cls, raw: Mapping[str, Any]) -> "LineProfile":
        if not isinstance(raw, Mapping):
            raise ValueError("line profile payload must be a JSON object")
        line_profile_id = _clean_text(raw.get("line_profile_id"), DEFAULT_LINEB_PROFILE_ID)
        return cls(
            line_profile_id=line_profile_id,
            display_name=_clean_text(raw.get("display_name"), line_profile_id),
            line_id=_clean_text(raw.get("line_id"), "line_b").lower(),
            llm=LlmProfile.from_json(raw.get("llm") if isinstance(raw.get("llm"), Mapping) else None),
            asr=AsrProfile.from_json(raw.get("asr") if isinstance(raw.get("asr"), Mapping) else None),
            tts=TtsProfile.from_json(raw.get("tts") if isinstance(raw.get("tts"), Mapping) else None),
            voiceprint=VoiceprintProfile.from_json(
                raw.get("voiceprint") if isinstance(raw.get("voiceprint"), Mapping) else None
            ),
            echo=EchoPolicy.from_json(
                raw.get("echo") if isinstance(raw.get("echo"), Mapping) else None
            ),
            metadata=dict(raw.get("metadata") or {}),
        )

    def as_json(self) -> dict[str, Any]:
        return {
            "schema_version": LINE_PROFILE_SCHEMA_VERSION,
            "kind": "line_profile",
            "line_profile_id": self.line_profile_id,
            "display_name": self.display_name,
            "line_id": self.line_id,
            "llm": self.llm.as_json(),
            "asr": self.asr.as_json(),
            "tts": self.tts.as_json(),
            "voiceprint": self.voiceprint.as_json(),
            "echo": self.echo.as_json(),
            "metadata": dict(self.metadata),
        }

    def with_env_overrides(self, env: Mapping[str, str] | None = None) -> "LineProfile":
        env = os.environ if env is None else env
        if self.line_id != "line_b":
            return self

        llm_model = _env_text(env, "GEMINI_TEXT_MODEL")
        stt_model = _env_text(env, "GOOGLE_STT_MODEL")
        stt_languages = _env_text(env, "GOOGLE_STT_LANGUAGES")
        tts_voice = _env_text(env, "GOOGLE_TTS_VOICE")
        tts_language = _env_text(env, "GOOGLE_TTS_LANGUAGE")
        tts_manifest = _env_text(env, "NER_PRIVATE_VOICE_MANIFEST")
        tts_audio_root = _env_text(env, "NER_PRIVATE_VOICE_AUDIO_ROOT")
        voiceprint_enabled = _env_text(env, "PARROT_LINEB_VOICEPRINT_ENABLED")
        voiceprint_profile_id = _env_text(env, "PARROT_LINEB_VOICEPRINT_PROFILE_ID")
        voiceprint_provider = _env_text(env, "PARROT_LINEB_VOICEPRINT_PROVIDER")
        voiceprint_manifest = _env_text(env, "PARROT_LINEB_VOICEPRINT_MANIFEST")
        voiceprint_data_root = _env_text(env, "PARROT_VOICEPRINT_AUDIO_ROOT")
        voiceprint_accept = _env_text(env, "PARROT_LINEB_VOICEPRINT_THRESHOLD_ACCEPT")
        voiceprint_reject = _env_text(env, "PARROT_LINEB_VOICEPRINT_THRESHOLD_REJECT")
        echo_output = _env_text(env, "PARROT_AUDIO_OUTPUT_ROUTE")
        echo_handling = _env_text(env, "PARROT_LINEB_ECHO_HANDLING_MODE")

        return replace(
            self,
            llm=replace(self.llm, model=llm_model or self.llm.model),
            asr=replace(
                self.asr,
                model=stt_model or self.asr.model,
                languages=_tuple_text(stt_languages) or self.asr.languages,
            ),
            tts=replace(
                self.tts,
                language=tts_language or self.tts.language,
                voice_name=tts_voice if tts_voice is not None else self.tts.voice_name,
                voice_asset_manifest_path=(
                    tts_manifest or self.tts.voice_asset_manifest_path
                ),
                sample_audio_root=tts_audio_root or self.tts.sample_audio_root,
            ),
            voiceprint=replace(
                self.voiceprint,
                enabled=(
                    _truthy(voiceprint_enabled)
                    if voiceprint_enabled is not None
                    else self.voiceprint.enabled
                ),
                provider=voiceprint_provider or self.voiceprint.provider,
                voiceprint_profile_id=(
                    voiceprint_profile_id or self.voiceprint.voiceprint_profile_id
                ),
                manifest_path=voiceprint_manifest or self.voiceprint.manifest_path,
                data_root=voiceprint_data_root or self.voiceprint.data_root,
                threshold_accept=(
                    _float_from_raw(voiceprint_accept, self.voiceprint.threshold_accept)
                    if voiceprint_accept is not None
                    else self.voiceprint.threshold_accept
                ),
                threshold_reject=(
                    _float_from_raw(voiceprint_reject, self.voiceprint.threshold_reject)
                    if voiceprint_reject is not None
                    else self.voiceprint.threshold_reject
                ),
            ),
            echo=replace(
                self.echo,
                output_route=echo_output or self.echo.output_route,
                handling_mode=echo_handling or self.echo.handling_mode,
            ),
        )


@dataclass(frozen=True)
class LineDeviceCheckResult:
    line_profile_id: str
    state: str
    health: str
    findings: tuple[dict[str, Any], ...]

    def as_json(self) -> dict[str, Any]:
        return {
            "line_profile_id": self.line_profile_id,
            "state": self.state,
            "health": self.health,
            "findings": [dict(f) for f in self.findings],
        }


class LineProfileLoader:
    """Disk-backed LineProfile loader with env override support."""

    def __init__(self, search_paths: list[Path] | None = None) -> None:
        if search_paths is None:
            search_paths = self._default_search_paths()
        self._search_paths = [Path(p) for p in search_paths]

    @staticmethod
    def _default_search_paths() -> list[Path]:
        out: list[Path] = []
        env = os.environ.get(LINE_PROFILES_DIR_ENV, "").strip()
        if env:
            out.extend(Path(p) for p in env.split(os.pathsep) if p)
        out.append(Path("data") / "line_profiles")
        return out

    def list_profiles(self, *, apply_env: bool = False) -> tuple[LineProfile, ...]:
        seen: dict[str, LineProfile] = {
            DEFAULT_LINEA_PROFILE_ID: LineProfile.builtin_linea(),
            DEFAULT_LINEB_PROFILE_ID: LineProfile.builtin_lineb(),
        }
        for directory in self._search_paths:
            try:
                if not directory.is_dir():
                    continue
                for path in sorted(directory.glob("*.json")):
                    try:
                        profile = LineProfile.from_json(
                            json.loads(path.read_text(encoding="utf-8"))
                        )
                    except (OSError, ValueError, json.JSONDecodeError):
                        continue
                    seen[profile.line_profile_id] = profile
            except OSError:
                continue
        profiles = tuple(
            sorted(seen.values(), key=lambda p: (p.line_id, p.display_name.lower()))
        )
        if apply_env:
            return tuple(profile.with_env_overrides() for profile in profiles)
        return profiles

    def load(self, line_profile_id: str, *, apply_env: bool = False) -> LineProfile:
        safe = _clean_text(line_profile_id, DEFAULT_LINE_PROFILE_ID)
        for profile in self.list_profiles(apply_env=False):
            if profile.line_profile_id == safe:
                return profile.with_env_overrides() if apply_env else profile
        active_payload = _bb_value("global/active_line_profile", {})
        if isinstance(active_payload, dict):
            try:
                active_profile = LineProfile.from_json(active_payload)
                if active_profile.line_profile_id == safe:
                    return (
                        active_profile.with_env_overrides()
                        if apply_env
                        else active_profile
                    )
            except ValueError:
                pass
        fallback = (
            LineProfile.builtin_lineb()
            if safe == DEFAULT_LINEB_PROFILE_ID
            else LineProfile.builtin_linea()
        )
        return fallback.with_env_overrides() if apply_env else fallback

    def profile_for_line(self, line_id: str, *, apply_env: bool = True) -> LineProfile:
        safe_line = _clean_text(line_id, "line_a").lower()
        active = self.active_profile(apply_env=apply_env)
        if active.line_id == safe_line:
            return active
        default_id = default_line_profile_id(safe_line)
        return self.load(default_id, apply_env=apply_env)

    def active_profile_id(self) -> str:
        bb_value = _bb_value("global/active_line_profile_id", "")
        if isinstance(bb_value, str) and bb_value.strip():
            return bb_value.strip()
        env_value = (
            os.getenv(ACTIVE_LINE_PROFILE_ENV, "").strip()
            or os.getenv(ACTIVE_LINE_PROFILE_ID_ENV, "").strip()
        )
        if env_value:
            return env_value
        active_line = _bb_value("global/active_line_id", "")
        if isinstance(active_line, str) and active_line.strip():
            return default_line_profile_id(active_line)
        pipeline = os.getenv("PARROT_LLM_PIPELINE", "").strip()
        if pipeline:
            return default_line_profile_id(pipeline)
        return DEFAULT_LINE_PROFILE_ID

    def active_profile(self, *, apply_env: bool = True) -> LineProfile:
        return self.load(self.active_profile_id(), apply_env=apply_env)

    def save(self, profile: LineProfile) -> Path:
        target_dir = self._writable_dir()
        target_dir.mkdir(parents=True, exist_ok=True)
        path = target_dir / f"{profile.line_profile_id}.json"
        path.write_text(
            json.dumps(profile.as_json(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return path

    def preview(self, draft: dict[str, Any] | LineProfile) -> dict[str, Any]:
        profile = draft if isinstance(draft, LineProfile) else LineProfile.from_json(draft)
        resolved = profile.with_env_overrides()
        return {
            "line_profile": profile.as_json(),
            "resolved_line_profile": resolved.as_json(),
            "device_check": evaluate_line_profile(resolved).as_json(),
        }

    def apply(self, draft_or_id: dict[str, Any] | LineProfile | str) -> dict[str, Any]:
        if isinstance(draft_or_id, LineProfile):
            profile = draft_or_id
        elif isinstance(draft_or_id, dict):
            profile = LineProfile.from_json(draft_or_id)
        else:
            profile = self.load(str(draft_or_id or DEFAULT_LINE_PROFILE_ID))
        resolved = profile.with_env_overrides()
        check = evaluate_line_profile(resolved)

        applied: list[str] = []
        errors: list[str] = []
        try:
            bb = open_bb_client(name="line_profile.apply", writer="brain.preset_loader")
            for key, value in {
                "global/active_line_id": resolved.line_id,
                "global/active_line_profile_id": resolved.line_profile_id,
                "global/active_line_profile": resolved.as_json(),
                "global/active_asr_profile_id": resolved.asr.asr_profile_id,
                "global/active_tts_profile_id": resolved.tts.tts_profile_id,
                "global/active_voiceprint_profile_id": resolved.voiceprint.voiceprint_profile_id,
                "global/active_echo_policy_id": resolved.echo.echo_policy_id,
            }.items():
                bb.set(key, value)
                applied.append(key)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"blackboard write failed: {exc!r}")

        audio_policy: dict[str, Any] = {}
        if resolved.line_id == "line_b":
            try:
                from parrot.brain.lineb_audio_guard import apply_audio_route_policy

                audio_policy = apply_audio_route_policy(
                    input_route=resolved.echo.input_route,
                    output_route=resolved.echo.output_route,
                    microphone_enabled=resolved.echo.microphone_enabled,
                    speaker_output_enabled=resolved.echo.speaker_output_enabled,
                    echo_handling_mode=resolved.echo.handling_mode,
                    voiceprint_enabled=resolved.voiceprint.enabled,
                    speaker_state=resolved.voiceprint.speaker_state,
                    source=f"line_profile:{resolved.line_profile_id}",
                )
            except Exception as exc:  # noqa: BLE001
                errors.append(f"audio route policy failed: {exc!r}")

        return {
            "success": not errors,
            "line_profile": profile.as_json(),
            "resolved_line_profile": resolved.as_json(),
            "device_check": check.as_json(),
            "applied_keys": applied,
            "errors": errors,
            "audio_route_policy": audio_policy,
        }

    def _writable_dir(self) -> Path:
        for directory in self._search_paths:
            try:
                directory.mkdir(parents=True, exist_ok=True)
                return directory
            except OSError:
                continue
        return Path("data") / "line_profiles"


def evaluate_line_profile(profile: LineProfile) -> LineDeviceCheckResult:
    if profile.line_id == "line_a":
        return LineDeviceCheckResult(
            line_profile_id=profile.line_profile_id,
            state="ready",
            health="ok",
            findings=(
                _finding("line_a.realtime", "ready", "ok", "LineA uses native Gemini Realtime."),
            ),
        )

    api_key_ready = bool(os.getenv("GOOGLE_API_KEY"))
    adc_ready, adc_summary, adc_refs = _adc_state()
    vad_ready = importlib.util.find_spec("livekit.plugins.silero") is not None
    tts_voice_ready = bool(profile.tts.voice_name.strip())
    asr_ready = bool(profile.asr.model.strip() and profile.asr.languages)
    echo_risk = _echo_risk(profile.echo.output_route, profile.voiceprint.enabled)
    voiceprint_state, voiceprint_health, voiceprint_summary, voiceprint_refs = (
        _voiceprint_eval(profile)
    )

    findings = (
        _finding(
            "google_api_key",
            "ready" if api_key_ready else "blocked",
            "ok" if api_key_ready else "error",
            "GOOGLE_API_KEY is present." if api_key_ready else "GOOGLE_API_KEY is missing.",
            {"provider": profile.llm.provider, "model": profile.llm.model},
        ),
        _finding(
            "google_adc",
            "ready" if adc_ready else "blocked",
            "ok" if adc_ready else "error",
            adc_summary,
            adc_refs,
        ),
        _finding(
            "asr",
            "ready" if asr_ready and adc_ready else "blocked",
            "ok" if asr_ready and adc_ready else "error",
            "ASR profile and ADC are configured."
            if asr_ready and adc_ready
            else "ASR needs model/languages and Google ADC.",
            profile.asr.as_json(),
        ),
        _finding(
            "tts",
            "ready" if tts_voice_ready and adc_ready else "blocked",
            "ok" if tts_voice_ready and adc_ready else "error",
            "TTS profile and ADC are configured."
            if tts_voice_ready and adc_ready
            else "TTS needs voice_name/language and Google ADC.",
            profile.tts.as_json(),
        ),
        _finding(
            "vad",
            "ready" if vad_ready else "degraded",
            "ok" if vad_ready else "warning",
            "Silero VAD plugin is importable." if vad_ready else "Silero VAD plugin was not found.",
            {"provider": "silero.VAD"},
        ),
        _finding(
            "voiceprint",
            voiceprint_state,
            voiceprint_health,
            voiceprint_summary,
            voiceprint_refs,
        ),
        _finding(
            "echo",
            echo_risk,
            "warning" if echo_risk == "high" else "ok",
            f"output_route={profile.echo.output_route}; handling={profile.echo.handling_mode}.",
            profile.echo.as_json(),
        ),
    )

    state = "ready"
    health = "ok"
    if not api_key_ready or not tts_voice_ready or not asr_ready:
        state = "blocked"
        health = "error"
    elif (
        not adc_ready
        or not vad_ready
        or not profile.voiceprint.enabled
        or voiceprint_health != "ok"
        or echo_risk == "high"
    ):
        state = "degraded"
        health = "warning"
    return LineDeviceCheckResult(
        line_profile_id=profile.line_profile_id,
        state=state,
        health=health,
        findings=findings,
    )


@dataclass(frozen=True)
class LineBRuntimeSettings:
    llm_model: str
    stt_model: str
    stt_languages: tuple[str, ...]
    tts_language: str
    tts_voice: str
    line_profile_id: str


def active_lineb_runtime_settings() -> LineBRuntimeSettings:
    profile = get_line_profile_loader().profile_for_line("line_b", apply_env=True)
    if not profile.tts.voice_name.strip():
        raise RuntimeError(
            f"LineB profile {profile.line_profile_id!r} is missing tts.voice_name."
        )
    return LineBRuntimeSettings(
        llm_model=profile.llm.model,
        stt_model=profile.asr.model,
        stt_languages=profile.asr.languages,
        tts_language=profile.tts.language,
        tts_voice=profile.tts.voice_name,
        line_profile_id=profile.line_profile_id,
    )


def default_line_profile_id(line_id: str) -> str:
    return DEFAULT_LINEB_PROFILE_ID if str(line_id).strip().lower() == "line_b" else DEFAULT_LINEA_PROFILE_ID


_loader: LineProfileLoader | None = None


def get_line_profile_loader() -> LineProfileLoader:
    global _loader
    if _loader is None:
        _loader = LineProfileLoader()
    return _loader


def set_line_profile_loader_for_test(loader: LineProfileLoader | None) -> None:
    global _loader
    _loader = loader


def _adc_state() -> tuple[bool, str, dict[str, Any]]:
    json_payload = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON", "")
    if json_payload.strip():
        return True, "GOOGLE_APPLICATION_CREDENTIALS_JSON is present.", {
            "source": "GOOGLE_APPLICATION_CREDENTIALS_JSON"
        }
    path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "").strip()
    if not path:
        return False, "GOOGLE_APPLICATION_CREDENTIALS is missing.", {
            "source": "GOOGLE_APPLICATION_CREDENTIALS"
        }
    exists = Path(path).expanduser().is_file()
    return (
        exists,
        "GOOGLE_APPLICATION_CREDENTIALS file exists."
        if exists
        else "GOOGLE_APPLICATION_CREDENTIALS file does not exist.",
        {"source": "GOOGLE_APPLICATION_CREDENTIALS", "path": path, "exists": exists},
    )


def _echo_risk(output_route: str, voiceprint_enabled: bool) -> str:
    route = output_route.lower()
    if route in {
        "headphones",
        "headset",
        "wired_headset",
        "bluetooth",
        "bluetooth_headset",
        "bluetooth_sco",
        "bluetooth_a2dp",
        "earpiece",
    }:
        return "low"
    if route in {"speaker", "phone_speaker", "loudspeaker"}:
        return "medium" if voiceprint_enabled else "high"
    return "low" if voiceprint_enabled else "medium"


def _voiceprint_eval(profile: LineProfile) -> tuple[str, str, str, dict[str, Any]]:
    if not profile.voiceprint.enabled:
        return (
            "not_configured",
            "warning",
            "Voiceprint/speaker gate is disabled for this profile.",
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
    except Exception as exc:  # noqa: BLE001
        return (
            "degraded",
            "warning",
            f"Voiceprint verifier status failed: {type(exc).__name__}: {exc}",
            profile.voiceprint.as_json(),
        )
    if status.state == "disabled":
        return (
            "not_configured",
            "warning",
            "LineProfile enables voiceprint, but PARROT_LINEB_VOICEPRINT_ENABLED is not active.",
            {**profile.voiceprint.as_json(), "runtime": status.as_json()},
        )
    return (
        status.state,
        status.health,
        status.summary,
        {**profile.voiceprint.as_json(), "runtime": status.as_json()},
    )


def _finding(
    component_id: str,
    state: str,
    health: str,
    summary: str,
    refs: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "component_id": component_id,
        "state": state,
        "health": health,
        "summary": summary,
        "refs": dict(refs or {}),
    }


def _bb_value(key: str, default: Any) -> Any:
    try:
        bb = open_bb_client(name="line_profile.read", writer=None)
        value = bb.get(key)
        return default if value is None else value
    except Exception:
        return default


def _clean_text(value: Any, fallback: str) -> str:
    text = str(value or "").strip()
    return text if text else fallback


def _tuple_text(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        splitter = "," if "," in value else "|"
        return tuple(s.strip() for s in value.split(splitter) if s.strip())
    if isinstance(value, (list, tuple)):
        return tuple(str(v).strip() for v in value if str(v).strip())
    return ()


def _env_text(env: Mapping[str, str], key: str) -> str | None:
    if key not in env:
        return None
    text = env[key].strip()
    return text or None


def _truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on", "enabled"}


def _bool_from_raw(value: Any, fallback: bool) -> bool:
    if value is None:
        return fallback
    if isinstance(value, bool):
        return value
    return _truthy(str(value))


def _float_from_raw(value: Any, fallback: float) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return fallback
    return parsed if math.isfinite(parsed) else fallback


__all__ = [
    "AsrProfile",
    "DEFAULT_LINEA_PROFILE_ID",
    "DEFAULT_LINEB_PROFILE_ID",
    "DEFAULT_LINE_PROFILE_ID",
    "EchoPolicy",
    "LINE_PROFILES_DIR_ENV",
    "LINE_PROFILE_SCHEMA_VERSION",
    "LineBRuntimeSettings",
    "LineDeviceCheckResult",
    "LineProfile",
    "LineProfileLoader",
    "LlmProfile",
    "TtsProfile",
    "VoiceprintProfile",
    "active_lineb_runtime_settings",
    "default_line_profile_id",
    "evaluate_line_profile",
    "get_line_profile_loader",
    "set_line_profile_loader_for_test",
]
