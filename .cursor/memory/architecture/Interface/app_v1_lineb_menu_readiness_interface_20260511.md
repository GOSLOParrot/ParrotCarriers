---
title: App V1 LineB Menu Readiness Interface
date: 2026-05-11
status: partial-implementation
category: business-interface
owner: Codex / App V1
scope: LineA/LineB menu status, ASR/TTS readiness, Google ADC, voiceprint/speaker state, echo risk, runtime audio-route evidence
code:
  - src/parrot/brain/line_profile.py
  - src/parrot/brain/lineb_audio_guard.py
  - src/parrot/brain/line_status.py
  - src/parrot/brain/room_setting.py
  - src/parrot/brain/app_first_version.py
  - src/parrot/brain/app_monitor_server.py
  - src/parrot/brain/agent.py
  - src/parrot/shared/bb_schema.py
tests:
  - tests/test_brain/test_app_first_version_facade.py
  - tests/test_brain/test_app_v1_monitor.py
  - tests/test_brain/test_menu_workspace.py
related:
  - app_v1_room_setting_room_profile_interface_20260510.md
  - app_v1_current_status_and_test_report_20260510.md
  - app_v1_lineb_ner_realdevice_config_report_20260511.md
  - ../../../codex_workspace/thesis_lineb_voiceprint_echo_addendum.md
---

# App V1 LineB Menu Readiness Interface

## 0. Decision

LineB is no longer a bare `PARROT_LLM_PIPELINE=line_b` option in the App menu.
It now has an App-configurable `LineProfile` layer for ASR/TTS/voiceprint/echo
settings, while keeping env-var overrides for local development.

App menus must show a structured voice-pipeline status:

- LineA / LineB selector state.
- Google API key readiness.
- Google ADC readiness for STT/TTS.
- ASR readiness.
- TTS readiness.
- VAD readiness.
- voiceprint / speaker state.
- echo risk and echo handling mode.
- recent LineB TTS segment count and last mic-input turn decision.

This document covers the menu/status layer plus the first runtime guard skeleton. It does not claim that final real-device LineB voiceprint echo suppression is complete.

## 1. Current Implementation

Implemented read model:

- `parrot.brain.line_profile.LineProfile`
- `parrot.brain.line_profile.LineProfileLoader`
- `parrot.brain.lineb_audio_guard.apply_audio_route_policy()`
- `parrot.brain.lineb_audio_guard.register_tts_segment()`
- `parrot.brain.lineb_audio_guard.classify_mic_input()`
- `parrot.brain.line_status.list_lines()`
- `parrot.brain.line_status.active_line_status()`
- `AppFirstVersionFacade.module_status(ExternalModuleId.VOICE_PIPELINE)`
- RoomSetting `selectors.lines` now carries the same structured data.
- RoomSetting `selectors.line_profiles` lists builtin and saved LineProfile
  options.
- RoomProfile now stores `line_profile_id`, `asr_profile_id`,
  `tts_profile_id`, `voiceprint_profile_id`, and `echo_policy_id`.
- App facade LineProfile methods:
  - `list_line_profiles()`
  - `preview_line_profile()`
  - `save_line_profile()`
  - `apply_line_profile()`
- Web monitor endpoints:
  - `GET /api/app/line-profiles`
  - `POST /api/app/line-profiles/preview`
  - `POST /api/app/line-profiles/save`
  - `POST /api/app/line-profiles/apply`
  - `POST /api/app/lineb/audio-route`
  - `POST /api/app/lineb/tts-segment`
  - `POST /api/app/lineb/mic-input`
- LiveKit RPCs:
  - `setLineBAudioRoutePolicy`
  - `registerLineBTtsSegment`
  - `classifyLineBMicInput`

LineB critical readiness:

| Component | Source |
|:--|:--|
| Gemini text LLM | `GOOGLE_API_KEY` |
| Google ADC | `GOOGLE_APPLICATION_CREDENTIALS` or `GOOGLE_APPLICATION_CREDENTIALS_JSON` |
| ASR | Google ADC + `GOOGLE_STT_MODEL` / `GOOGLE_STT_LANGUAGES` |
| TTS | Google ADC + `GOOGLE_TTS_VOICE` / `GOOGLE_TTS_LANGUAGE` |
| VAD | `livekit.plugins.silero` importability |

Saved profile path:

- `data/line_profiles/lineb_google_default.json`

Env override policy:

- `GEMINI_TEXT_MODEL`
- `GOOGLE_STT_MODEL`
- `GOOGLE_STT_LANGUAGES`
- `GOOGLE_TTS_LANGUAGE`
- `GOOGLE_TTS_VOICE`
- `PARROT_LINEB_VOICEPRINT_ENABLED`
- `PARROT_AUDIO_OUTPUT_ROUTE`
- `PARROT_LINEB_ECHO_HANDLING_MODE`

Voiceprint and echo state:

- Voiceprint can be surfaced from `session/audio_route_policy.voiceprint`.
- If absent, `PARROT_LINEB_VOICEPRINT_ENABLED` marks a provisional monitoring state.
- Echo can be surfaced from `session/audio_route_policy.echo`.
- If absent, echo risk is inferred from `PARROT_AUDIO_OUTPUT_ROUTE` and whether voiceprint is enabled.

Runtime evidence:

| Blackboard key | Writer | Purpose |
|:--|:--|:--|
| `global/active_line_profile_id` | `brain.preset_loader` | Active LineProfile id. |
| `global/active_line_profile` | `brain.preset_loader` | Resolved active LineProfile payload for unsaved RoomSetting drafts. |
| `global/active_asr_profile_id` | `brain.preset_loader` | Active ASR profile id. |
| `global/active_tts_profile_id` | `brain.preset_loader` | Active TTS profile id. |
| `global/active_voiceprint_profile_id` | `brain.preset_loader` | Active voiceprint profile id. |
| `global/active_echo_policy_id` | `brain.preset_loader` | Active echo policy id. |
| `session/audio_route_policy` | `brain.lineb_audio_guard` | Input/output route, voiceprint status, echo risk, handling mode. |
| `session/lineb_recent_tts_segments` | `brain.lineb_audio_guard` | Recent assistant TTS output windows for echo matching. |
| `transient/lineb_last_input_decision` | `brain.lineb_audio_guard` | Latest mic fragment decision: user turn, agent echo, noise, or uncertain. |

`brain.agent` registers approximate TTS windows from LineB assistant messages and classifies final LineB mic transcripts. It only suppresses a transcript when the guard returns `agent_echo`.

## 2. State Semantics

| State | Meaning |
|:--|:--|
| `ready` | Critical configuration is present. |
| `degraded` | The option can be shown, but the menu should warn that a path is incomplete. |
| `blocked` | The option should not be started without fixing configuration. |
| `not_configured` | Non-critical optional feature, such as voiceprint, is not configured. |
| `not_available` | The selected line cannot expose this capability. |

LineB overall state:

- `blocked` when `GOOGLE_API_KEY` is missing.
- `degraded` when API key exists but Google ADC is missing or VAD import is not confirmed.
- `blocked` when a selected profile is missing required ASR/TTS fields such
  as `tts.voice_name` while ADC is otherwise available.
- `ready` when API key, ADC, selected ASR/TTS profile, and VAD look configured.

## 3. Menu Contract

RoomSetting receives:

```json
{
  "line_id": "line_b",
  "state": "degraded",
  "readiness": {
    "line_profile_id": "lineb_google_default",
    "asr_profile_id": "google_stt_cmn_en_default",
    "tts_profile_id": "google_tts_cmn_default",
    "voiceprint_profile_id": "voiceprint_monitor_default",
    "echo_policy_id": "echo_isolated_default",
    "llm_model": "gemini-2.5-flash",
    "google_api_key": "ready",
    "google_adc": "blocked",
    "asr": "blocked",
    "tts": "blocked",
    "vad": "ready",
    "voiceprint": "not_configured",
    "echo_risk": "medium",
    "echo_handling_mode": "monitor_only",
    "recent_tts_segment_count": 0,
    "last_input_decision": "none",
    "last_speaker_role": "unknown"
  }
}
```

The App module rail receives a new module:

- `module_id = voice_pipeline`
- `metrics.active_line_id`
- `metrics.active_line_profile_id`
- `metrics.echo_risk`
- `metrics.echo_handling_mode`
- `metrics.voiceprint_state`
- `metrics.speaker_state`
- `metrics.recent_tts_segment_count`
- `metrics.last_input_decision`
- `metrics.last_speaker_role`
- `refs.lines`
- `refs.active_line`
- `refs.line_profiles`

LineProfile preview/apply returns:

```json
{
  "line_profile": {},
  "resolved_line_profile": {},
  "device_check": {
    "line_profile_id": "lineb_google_default",
    "state": "degraded",
    "health": "warning",
    "findings": []
  },
  "applied_keys": []
}
```

## 4. Real-Device Startup Checklist

Before marking LineB as device-ready:

1. Select `line_b` and `lineb_google_default` or a saved Ner profile from
   RoomSetting.
2. Confirm `GOOGLE_API_KEY` is ready.
3. Confirm Google ADC is ready for STT/TTS.
4. Confirm selected ASR languages and TTS voice are visible in the menu.
5. Confirm `session/audio_route_policy` matches the device output route.
6. Test isolated output first, then speaker output with `voiceprint_gate`.
7. Register a TTS segment and verify a matching mic fragment becomes
   `agent_echo`, not `user_turn`.

## 5. Remaining Work

Not complete yet:

1. Real device LineB smoke.
2. Real acoustic/DSP echo score and true voiceprint comparison.
3. Unity UI rendering for warning badges and blocked/degraded line selection.
4. Character-specific TTS styling audit before shipping Ner-derived voice settings.

Completion requires proving that LineB does not generate a user turn from GOSLO's own TTS echo under the intended device/audio route.
