---
status: active
category: app-v1-status-report
status_note: "Single clean App V1 status/test report after route cleanup. It replaces longline/self-check/smoke-derived App-completion claims. Formal App frontend remains not complete."
last_reviewed: 2026-05-11
---

# App V1 Current Status And Test Report

## 1. Current Truth

The formal App frontend is **not complete**.

Do not treat any of the following as App completion evidence:

- `ParrotSmokeScene` validation.
- Web monitor / browser smoke.
- Longline self-check completion documents.
- Unity runtime UI prototype mounted into a smoke scene.

The production frontend must be validated from the startup page through the real App scene and Android build path.

## 2. Completed Work

| Area | Status | Evidence |
|:--|:--|:--|
| Mint | completed smoke | Castle token mint endpoint returned valid token in prior ECS smoke. |
| LiveKit | completed smoke | Unity-like join reached Castle LiveKit and Brain participant appeared. |
| Photo upload | completed smoke | Session-scoped `7889` upload path accepted photo POST during live session. |
| Backend facade | completed interface layer | `app_v1_facade_core_business_interface_20260510.md` and tests cover App-facing facade concepts. |
| RoomSetting backend contract | partial interface layer | `app_v1_room_setting_room_profile_interface_20260510.md`, `RoomProfile`, `RoomSettingService`, facade/Web/RPC entrypoints, and focused tests exist. Unity startup page is not wired yet. |
| RoomSetting Line cold-start contract | partial lifecycle layer | `app_v1_brain_cold_start_line_lifecycle_audit_20260511.md`; RoomSetting exposes `selectors.lines` / `selectors.line_profiles`, marks Line as `cold_start_only`, blocks mismatched runtime Line apply, and Brain room-scoped Redis/listener/upload tasks now clean up on disconnect. External process restart/supervisor is still pending. |
| LineB menu readiness | partial interface layer | `app_v1_lineb_menu_readiness_interface_20260511.md`, `line_profile.py`, `line_status.py`, `lineb_audio_guard.py`, `lineb_model_reaction.py`, RoomSetting `selectors.lines` / `selectors.line_profiles`, `lineb_google_default`, and `lineb_ner_ja_test` expose ASR/TTS/ADC/voiceprint/echo plus runtime audio-route/TTS/mic-decision/voice-activity evidence. Missing TTS voice now blocks even when ADC is also missing. LineB voice activity can now dispatch strict model capabilities for Ner, but real DSP/voiceprint echo suppression, Unity Editor/device verification, and device smoke are not complete. |
| Model capability resolver | partial interface layer | `app_v1_model_capability_resolver_interface_20260511.md`, `ModelManifestRegistry`, RoomSetting capability decisions, `play_capability`, and model-aware tool hiding now distinguish GOSLO parrot actions from Ner custom face/touch capabilities. Strict custom capability calls now preserve Unity parameters and return `capability_unsupported:<id>` when rejected. |
| Web monitor | test tool only | Useful for BB/IW/L2-B visibility, not formal App UI. |
| Unity tool controllers | partial | Photo / Focus / BBox / lifecycle controllers exist; formal App pages are not wired. |
| Assets | partial | Wood, paper, NekoClaw, BBox frame, icon atlas, and Ner raw assets exist. |

## 3. Not Complete

| Area | Status |
|:--|:--|
| Formal App scene | not complete; Android Build Settings still need a real App entry, not smoke validation. |
| Startup page implementation | not complete; design exists in `codex_workspace/design_workspace`. |
| Room Setting page | backend partial; Unity startup page not complete. Room means saved App `RoomProfile`, not LiveKit room. Line is startup/cold-start only and requires Brain restart when changing LineA/LineB. |
| LineB menu upgrade | backend configurable-profile layer exists; menu can read/save/apply LineProfile, ADC/ASR/TTS/voiceprint/echo state, and runtime guard evidence. Unity rendering, real-device LineB smoke, and actual DSP/voiceprint suppression remain pending. |
| Ner selectable model | backend/menu selectable candidate; manifest and controller probes exist, Brain can expose custom capability ids, and Unity Editor has verified imported Spine animations / primary manifest handlers. First-pass cheek pinch, body pickup/place, Ner persona trigger rules, a roleplay Obsidian setting source, and a Ner LineB TTS profile exist. Final audit fixed pickup cancel/lost-touch suspension and targetRoot raycast handling. Production prefab/startup UI/real-device animation verification are not complete. |
| Asset-matched production UI | not complete; selected assets are not yet proven inside the formal App scene. |
| 2D Workspace production flow | not complete; design exists, implementation pending. |

## 4. Current Usable Assets

| Slot | Current asset state |
|:--|:--|
| Wood drawer / wood button | Selected under `unity/ArSpike/Assets/ParrotApp/Art/AppV1/ToolCabinet/`. |
| Paper notes | Selected under `unity/ArSpike/Assets/ParrotApp/Art/AppV1/Notifications/`. |
| NekoClaw | Selected as `Notifications/NekoClaw_Cutout.png`. |
| BBox frame | Placeholder/selected frame under `Icons/BoundaryBox_Frame.png`. |
| Icon atlas | Placeholder icon source under `Icons/Items_16x16.png` and `Icons/Adventure_Icons.png`. |
| Ner | Raw Spine assets under `unity/ArSpike/Assets/ParrotApp/Models/Ner/`; not yet selectable in production App flow. |

## 5. Blocking Tasks

1. **Formal App frontend scene**: create/route a production App scene and stop using `ParrotSmokeScene` as App evidence.
2. **Room Setting**: wire startup `SCENE` menu to the new `RoomProfile` backend: Room select/new/save plus Model, Room, Persona, Line, and Scene selectors.
3. **LineB productization**: render the new LineProfile/readiness state in Unity menus, then add real-device LineB smoke and actual TTS echo/voiceprint suppression.
4. **Ner model path**: add model manifest/controller/prefab/preview status and only enable selection when complete.
5. **Brain cold-start supervisor**: add a RemoteSSH/ECS/manual launcher path that restarts Brain with `PARROT_LLM_PIPELINE` and `PARROT_ACTIVE_LINE_PROFILE_ID` from the selected RoomProfile.
6. **Design route cleanup**: new App frontend chats must start from `codex_workspace/design_workspace/tasks/ACTIVE_CONTEXT.md` and the HTML/page design docs before backend interfaces.

## 6. Next Chat Entry Rule

Read in this order:

1. `codex_workspace/design_workspace/tasks/ACTIVE_CONTEXT.md`
2. `codex_workspace/design_workspace/unity_ar_app/startup_menu_design_v0_20260509.md`
3. `codex_workspace/design_workspace/sketches/startup_menu_landscape_v0.html`
4. `codex_workspace/design_workspace/unity_ar_app/main_hud_landscape_v0_20260509.md`
5. `codex_workspace/design_workspace/sketches/main_hud_landscape_v0.html`
6. Backend interface docs only after the App page flow is understood.

## 7. Cleanup Verification 2026-05-10

Route cleanup:

- `D:\GOSLOParrot\codex_workspace` exists: false.
- `codex_workspace/design_workspace/asset_pipeline/pixel_asset_workspace/extracted` exists: false.
- `rg -n "longline|self-check|ParrotSmokeScene.*completion"` now only finds warnings that these records are not App completion evidence.

Regression:

```text
.\.venv\Scripts\python.exe -m pytest tests\test_brain\test_app_first_version_facade.py tests\test_brain\test_app_v1_monitor.py tests\test_ecp_event\test_w8_observer_photo.py tests\test_unity\test_app_v1_meta_ui_static.py
27 passed
```

LineB backend/interface regression on 2026-05-11:

```text
.\.venv\Scripts\python.exe -m pytest tests\test_brain\test_app_first_version_facade.py tests\test_brain\test_app_v1_monitor.py -q
20 passed
```

Related RoomSetting / monitor / photo observer / Unity meta regression on 2026-05-11:

```text
.\.venv\Scripts\python.exe -m pytest tests\test_brain\test_app_first_version_facade.py tests\test_brain\test_app_v1_monitor.py tests\test_brain\test_menu_workspace.py tests\test_ecp_event\test_w8_observer_photo.py tests\test_unity\test_app_v1_meta_ui_static.py -q
42 passed
```

LineB configurable-profile regression on 2026-05-11:

```text
.\.venv\Scripts\python.exe -m pytest tests\test_brain\test_app_first_version_facade.py tests\test_brain\test_app_v1_monitor.py tests\test_brain\test_menu_workspace.py -q
33 passed
```

LineB configurable-profile + App V1 related regression on 2026-05-11:

```text
.\.venv\Scripts\python.exe -m pytest tests\test_brain\test_app_first_version_facade.py tests\test_brain\test_app_v1_monitor.py tests\test_brain\test_menu_workspace.py tests\test_ecp_event\test_w8_observer_photo.py tests\test_unity\test_app_v1_meta_ui_static.py -q
50 passed
```

LineB configurable profile + model capability resolver regression on 2026-05-11:

```text
.\.venv\Scripts\python.exe -m pytest tests\test_brain\test_app_first_version_facade.py tests\test_brain\test_app_v1_monitor.py tests\test_brain\test_menu_workspace.py tests\test_brain\test_tools_model_id.py tests\test_shared\test_model_manifest.py tests\test_ecp_event\test_w8_observer_photo.py tests\test_unity\test_app_v1_meta_ui_static.py -q
88 passed
```

LineB/Ner strict capability bugfix regression on 2026-05-11:

```text
.\.venv\Scripts\python.exe -m pytest tests\test_brain\test_menu_workspace.py tests\test_brain\test_tools_model_id.py tests\test_unity\test_app_v1_meta_ui_static.py -q
29 passed
.\.venv\Scripts\python.exe -m py_compile src\parrot\brain\line_profile.py src\parrot\brain\tools\animate.py src\parrot\brain\tools\play_capability.py src\parrot\brain\tools\fly_to.py
passed
```

Ner Spine animation manifest regression on 2026-05-11:

```text
Unity Editor: NerSpineAnimationAudit validated 28 manifest handlers against 60 imported animations.
.\.venv\Scripts\python.exe -m pytest tests\test_brain\test_menu_workspace.py tests\test_brain\test_tools_model_id.py tests\test_unity\test_app_v1_meta_ui_static.py -q
31 passed
```

Ner persona / roleplay setting / LineB profile regression on 2026-05-11:

```text
.\.venv\Scripts\python.exe -m pytest tests\test_brain\test_menu_workspace.py -q
15 passed
.\.venv\Scripts\python.exe -m pytest tests\test_brain\test_app_first_version_facade.py tests\test_brain\test_app_v1_monitor.py tests\test_brain\test_menu_workspace.py tests\test_brain\test_tools_model_id.py tests\test_shared\test_model_manifest.py tests\test_ecp_event\test_w8_observer_photo.py tests\test_unity\test_app_v1_meta_ui_static.py -q
91 passed
```

LineB TTS-voice blocking + backend voice-activity bridge regression on
2026-05-11:

```text
.\.venv\Scripts\python.exe -m pytest tests\test_brain\test_app_first_version_facade.py tests\test_brain\test_app_v1_monitor.py tests\test_brain\test_menu_workspace.py tests\test_brain\test_tools_model_id.py tests\test_shared\test_model_manifest.py tests\test_ecp_event\test_w8_observer_photo.py tests\test_unity\test_app_v1_meta_ui_static.py -q
93 passed
.\.venv\Scripts\python.exe -m py_compile src\parrot\brain\line_profile.py src\parrot\brain\line_status.py src\parrot\brain\lineb_audio_guard.py src\parrot\brain\app_first_version.py src\parrot\shared\bb_schema.py
passed
```

LineB voice-activity model reaction bridge regression on 2026-05-11:

```text
.\.venv\Scripts\python.exe -m pytest tests\test_brain\test_app_first_version_facade.py tests\test_brain\test_app_v1_monitor.py tests\test_brain\test_menu_workspace.py tests\test_brain\test_lineb_model_reaction.py tests\test_brain\test_tools_model_id.py tests\test_shared\test_model_manifest.py tests\test_ecp_event\test_w8_observer_photo.py tests\test_unity\test_app_v1_meta_ui_static.py -q
97 passed
.\.venv\Scripts\python.exe -m py_compile src\parrot\brain\lineb_model_reaction.py src\parrot\brain\lineb_audio_guard.py src\parrot\brain\agent.py
passed
```

LineB defensive echo-score guard regression on 2026-05-11:

```text
.\.venv\Scripts\python.exe -m pytest tests\test_brain\test_app_first_version_facade.py::test_lineb_high_echo_score_without_recent_tts_is_uncertain tests\test_brain\test_app_first_version_facade.py::test_lineb_malformed_echo_score_does_not_break_mic_classification tests\test_brain\test_lineb_model_reaction.py::test_lineb_voice_activity_parameters_tolerate_malformed_numbers -q
3 passed
.\.venv\Scripts\python.exe -m py_compile src\parrot\brain\lineb_audio_guard.py src\parrot\brain\lineb_model_reaction.py
passed
.\.venv\Scripts\python.exe -m pytest tests\test_brain\test_app_first_version_facade.py tests\test_brain\test_app_v1_monitor.py tests\test_brain\test_menu_workspace.py tests\test_brain\test_lineb_model_reaction.py tests\test_brain\test_tools_model_id.py tests\test_shared\test_model_manifest.py tests\test_ecp_event\test_w8_observer_photo.py tests\test_unity\test_app_v1_meta_ui_static.py -q
100 passed
```

Ner pickup/place first-pass regression on 2026-05-11:

```text
.\.venv\Scripts\python.exe -m pytest tests\test_unity\test_app_v1_meta_ui_static.py tests\test_brain\test_menu_workspace.py tests\test_brain\test_tools_model_id.py tests\test_shared\test_model_manifest.py -q
59 passed
.\.venv\Scripts\python.exe -m pytest tests\test_brain\test_app_first_version_facade.py tests\test_brain\test_app_v1_monitor.py tests\test_brain\test_menu_workspace.py tests\test_brain\test_lineb_model_reaction.py tests\test_brain\test_tools_model_id.py tests\test_shared\test_model_manifest.py tests\test_ecp_event\test_w8_observer_photo.py tests\test_unity\test_app_v1_meta_ui_static.py -q
101 passed
Unity MCP validate_script for NerPickupPlaceInteractor.cs and
NerSpineController.cs: 0 errors; Console after refresh: 0 errors / 0 warnings.
```

Ner pickup/place final audit bugfix on 2026-05-11:

- Cancel/lost-touch/LineB-suppressed drag now drops Ner to the last resolved
  ground point instead of leaving the model suspended.
- Body and placement raycasts now handle prefab variants where the interactor
  transform and `targetRoot` are different.

RoomSetting Line cold-start + Brain lifecycle regression on 2026-05-11:

```text
.\.venv\Scripts\python.exe -m pytest tests\test_brain\test_app_first_version_facade.py tests\test_brain\test_menu_workspace.py tests\test_brain\test_session_context_pack.py tests\test_brain\test_brain_lifecycle_static.py tests\test_unity\test_app_v1_meta_ui_static.py
71 passed
.\.venv\Scripts\python.exe -m py_compile src\parrot\brain\agent.py src\parrot\brain\room_setting.py src\parrot\brain\photo_upload_server.py src\parrot\dsg\trigger_listener.py src\parrot\brain\line_profile.py src\parrot\brain\line_status.py
passed
```

