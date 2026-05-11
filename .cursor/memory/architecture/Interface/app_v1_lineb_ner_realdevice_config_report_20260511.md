---
title: App V1 LineB + Ner Real Device Config Report
date: 2026-05-11
status: partial-implementation / ready-for-device-config
category: business-interface
owner: Codex / App V1
scope: LineB readiness, Ner selectable model preparation, RoomSetting validation profile, ASR/TTS real-device plan
code:
  - src/parrot/brain/line_profile.py
  - src/parrot/brain/line_status.py
  - src/parrot/brain/lineb_audio_guard.py
  - src/parrot/brain/menu_registry.py
  - src/parrot/brain/personas/ner_companion.md
  - data/line_profiles/lineb_google_default.json
  - data/line_profiles/lineb_ner_ja_test.json
  - data/presets/ner_lineb_room.json
  - codex_workspace/design_workspace/unity_ar_app/ner_roleplay_setting_obsidian_v0_20260511.md
  - unity/ArSpike/Assets/Resources/parrot_models/ner_skin2.json
  - unity/ArSpike/Assets/Scripts/ParrotApp/Parrot/NerSpineController.cs
  - unity/ArSpike/Assets/Scripts/ParrotApp/Parrot/NerPickupPlaceInteractor.cs
related:
  - app_v1_lineb_menu_readiness_interface_20260511.md
  - app_v1_room_setting_room_profile_interface_20260510.md
  - ../../../codex_workspace/design_workspace/unity_ar_app/ner_mochi_scene_v0_20260511.md
---

# App V1 LineB + Ner Real Device Config Report

## 0. Verdict

LineB is now a real App menu/backend option, not just an env var. It has a
saveable `LineProfile` layer and can report Google API key, Google ADC, ASR,
TTS, VAD, voiceprint/speaker state, echo risk, recent TTS evidence, and last
mic-input decision.

Ner is now prepared as a selectable App model candidate:

- Model manifest: `unity/ArSpike/Assets/Resources/parrot_models/ner_skin2.json`
- Controller probe: `NerSpineController`
- Pickup/place probe: `NerPickupPlaceInteractor`
- Brain capability resolver: `ModelManifestRegistry` + `play_capability`
- Persona: `src/parrot/brain/personas/ner_companion.md`
- Roleplay setting source:
  `codex_workspace/design_workspace/unity_ar_app/ner_roleplay_setting_obsidian_v0_20260511.md`
- RoomProfile: `data/presets/ner_lineb_room.json`
- Scene setting draft: `codex_workspace/design_workspace/unity_ar_app/ner_mochi_scene_v0_20260511.md`

This does not yet equal final production completion. The missing proof is Unity
prefab wiring plus a real-device pass where startup selects Ner + LineB and
ASR/TTS behaves correctly under the intended audio route.

## 1. LineB Current Status

Implemented:

- `PARROT_LLM_PIPELINE=line_b` resolves to STT -> LLM -> TTS in `brain.agent`.
- LineB readiness is exposed by `line_status.list_lines()`.
- LineProfile config is exposed by `line_profile.LineProfileLoader`.
- Default saved config exists at `data/line_profiles/lineb_google_default.json`.
- Ner-specific selectable config exists at
  `data/line_profiles/lineb_ner_ja_test.json`.
- App facade and Web monitor expose audio-route, TTS-segment, and mic-input
  classification endpoints.
- RoomSetting compatibility consumes LineB state.
- `lineb_audio_guard` records:
  - `session/audio_route_policy`
  - `session/lineb_recent_tts_segments`
  - `transient/lineb_last_input_decision`
- Strict Ner/custom capability calls preserve `parameters_json` into Unity
  model controllers and fail with `capability_unsupported:<id>` when rejected.

Pending:

- True acoustic echo score.
- True voiceprint/speaker identity comparison.
- Unity warning badges for LineB blocked/degraded states.
- Real-device smoke with phone speaker/headphones route.
- Official voice/source audit for any character-specific TTS voice choice.

## 2. LineB Runtime Config

Preferred App config path:

1. Select or save a LineProfile from RoomSetting / Web monitor.
2. Apply it through `AppFirstVersionFacade.apply_line_profile()` or
   `POST /api/app/line-profiles/apply`.
3. Start LineB with `PARROT_LLM_PIPELINE=line_b`.

The default LineB profile is `lineb_google_default`. For Ner validation, use
`lineb_ner_ja_test`. Env vars still override the saved profile for local
real-device tuning.

Ner LineB baseline:

- ASR languages: `ja-JP`, `cmn-CN`, `en-US`.
- TTS language: `ja-JP`.
- TTS provider/voice: `cartesia.TTS` /
  `bfd1cc5a-5c3b-4e88-b7be-df9f3ec7e9a5`.
- Voiceprint policy: `monitor_then_gate`.
- Echo policy: headphones / isolated route first.
- Voice-source policy: Ner-inspired test voice only; no official character
  voice or CV clone in this repository.

Minimum env for a real-device LineB pass:

```powershell
$env:PARROT_LLM_PIPELINE = "line_b"
$env:GOOGLE_API_KEY = "<gemini-api-key>"
$env:GOOGLE_APPLICATION_CREDENTIALS = "D:\path\to\google-adc-service-account.json"
$env:GEMINI_TEXT_MODEL = "gemini-2.5-flash"
$env:GOOGLE_STT_MODEL = "latest_long"
$env:GOOGLE_STT_LANGUAGES = "cmn-CN,ja-JP,en-US"
$env:PARROT_LINEB_TTS_PROVIDER = "cartesia"
$env:CARTESIA_API_KEY = "<cartesia-api-key>"
$env:PARROT_LINEB_CARTESIA_VOICE_ID = "bfd1cc5a-5c3b-4e88-b7be-df9f3ec7e9a5"
$env:PARROT_AUDIO_OUTPUT_ROUTE = "headphones"
$env:PARROT_LINEB_ECHO_HANDLING_MODE = "isolated_route"
$env:PARROT_LINEB_VOICEPRINT_ENABLED = "1"
```

Speaker-route stress test:

```powershell
$env:PARROT_AUDIO_OUTPUT_ROUTE = "phone_speaker"
$env:PARROT_LINEB_ECHO_HANDLING_MODE = "voiceprint_gate"
```

Notes:

- `GOOGLE_API_KEY` gates the Gemini text LLM.
- Google ADC gates STT. Cartesia TTS gates on `CARTESIA_API_KEY` and the
  selected LineProfile voice id.
- `PARROT_LINEB_CARTESIA_VOICE_ID` overrides the saved profile voice only in
  the external/private device environment.
- The current Ner persona is a test persona and must not be treated as an
  official script or voice clone.

## 3. Real Device Use Flow

1. Start backend with LineB env configured.
2. Open startup page.
3. Open `SCENE` -> RoomSetting.
4. Select Room `ner_lineb_room`.
5. Confirm selectors:
   - Model: `ner_skin2`
   - Room: `ner_lineb_room`
   - Persona: `ner_companion`
   - Line: `line_b`
   - LineProfile: `lineb_ner_ja_test`
   - Scene: `ar_handheld` with `skin_id=ner_mochi_room_v0`
6. START enters IPoAC transition.
7. Permissions, Mint, and LiveKit connect run during transition.
8. LiveKit connection success stays silent.
9. AR plane becomes ready.
10. User places model.
11. Only then Ner may greet and run the first ASR/TTS test.

## 4. Expected Compatibility

For `ner_lineb_room`:

| Capability | Expected |
|:--|:--|
| `model.available` | enabled if `ner_skin2` manifest is readable |
| `model.capability.face_happy` / `touch_idle` / `pat_idle` / `tickle_idle` | enabled if declared by `ner_skin2` manifest |
| `parrot.fly_to_hand` | disabled, because Ner manifest does not declare `fly`/`perch` |
| `line.available` | blocked/degraded/ready according to Google API + ADC + VAD |
| `scene.available` | enabled through existing `ar_handheld` |
| `workspace.available` | enabled through `mansion_hub` |

This is the right conflict behavior: selecting a custom model should not break
the Room. It should disable only the unavailable actions and keep the rest of
the App profile usable.

## 5. Ner Asset Audit

Existing raw assets:

- `Assets/Models/Ner/NerSkin2.skel.bytes`
- `Assets/Models/Ner/NerSkin2.atlas.txt`
- `Assets/Models/Ner/NerSkin2.png`
- `Assets/Models/Ner/NerSkin2_SkeletonData.asset`
- `Assets/Models/Ner/NerSkin2_Atlas.asset`
- `Assets/Models/Ner/NerSkin2_Material.mat`

Spine package is present in Unity Packages. On 2026-05-11, Unity Editor
enumerated 60 exact animation names from `NerSkin2_SkeletonData.asset`.
Primary verified families now include:

- Expressions: angry, happy, sad, shame, surprise, panic, blank, close,
  not-my-fault, proud, serious, sulky, think, tired, worry.
- Touch/actions: touch, pat, tickle, eat, smash end.
- Runtime default: `Idle_1`.
- Body hints: wing/body slots exist, but no production fly/perch path is proven.

Current manifest maps only non-parrot custom capability IDs and keeps raw
animation variants under capability parameters so menus can show primary
actions without exploding into every raw clip:

- `spine_idle`
- `spine_walk`
- `face_happy`
- `face_angry`
- `face_sad`
- `face_shame`
- `face_surprise`
- `face_panic`
- `face_blank`
- `face_close`
- `face_notmyfault`
- `face_proud`
- `face_serious`
- `face_sulky`
- `face_think`
- `face_tired`
- `face_worry`
- `touch_idle`
- `touch_end`
- `pat_idle`
- `pat_end`
- `tickle_idle`
- `tickle_end`
- `eat`
- `smash_end`
- `cheek_pinch_start`
- `cheek_pinch_hold`
- `cheek_pinch_warning`
- `cheek_pinch_release`
- `cheek_recover`
- `body_pickup_start`
- `body_held_in_air`
- `body_dragging_in_air`
- `body_place_preview`
- `body_place_release`
- `body_place_cancel`

No `fly` or `perch` is declared.
`NerSpineAnimationAudit` validates manifest handlers against the imported
SkeletonDataAsset and currently reports: `28 manifest handlers match 60
imported animations`.

## 6. Parrot / Joystick / Expression Audit

GOSLO Parrot:

- Plane joystick movement exists through `ParrotController.WalkOnPlane()` and
  `AnimationDriver.WalkOnPlane()`.
- Existing joystick is still bound to the legacy Parrot controller path.
- Face customization is not a GOSLO production menu yet.

Ner:

- `NerSpineController` can dispatch manifest capabilities and has a
  `spine_walk` transform movement probe.
- `NerSpineController` now caches imported animation names, accepts
  `parameters_json` with `variant` or exact `animation`, and returns false
  with an idle visual fallback when a handler is missing.
- First-pass cheek pinch is implemented: `NerCheekPinchInteractor` raycasts
  against cheek trigger colliders and sends drag strength to `NerSpineController`,
  which offsets Spine cheek bones and resets them on release.
- First-pass pickup/place is implemented: `NerPickupPlaceInteractor` long-presses
  the body, lifts the model, drags over AR plane colliders or a horizontal
  fallback plane, and releases through body placement capabilities.
- The existing App joystick does not yet route through the model registry or
  `IParrotController.ApplyCapability("spine_walk", ...)`.
- Expression switching is prepared by manifest/controller capability IDs, but
  needs Unity prefab verification.
- Production cheek tuning is still pending: prefab-local collider positions,
  stretch strength, device feel, and optional LineB voice reactions.

## 7. Blocking Plan

1. RoomSetting UI binding:
   - Startup `SCENE` loads RoomSetting snapshot.
   - Model list shows `GOSLO_default` and `ner_skin2`.
   - Selecting `ner_lineb_room` populates Model, Room, Persona, Line, Scene.
   - START applies the selected RoomProfile.

2. LineB device pass:
   - Run headphones route first.
   - Verify ASR hears user phrase.
   - Verify TTS response is registered as recent LineB TTS.
   - Verify the next mic fragment is not misclassified as user speech when it
     matches recent TTS.
   - Repeat with phone speaker and `voiceprint_gate` mode.

3. Ner Unity production wiring:
   - Create/verify a prefab containing the Spine skeleton component,
     `ModelDriver(modelId=ner_skin2)`, and `NerSpineController`.
   - Verify `Type.GetType("ParrotApp.Parrot.NerSpineController")` resolves.
   - Verify `ConfigureFromManifest` is called by `ModelDriver`.
   - Verify expression actions play real Spine animations.
   - Verify unsupported parrot actions are disabled in UI and rejected by
     backend/Unity.

4. Control menu:
   - Add runtime expression buttons for Ner.
   - Route joystick through model capability when active model is `ner_skin2`.
   - Keep GOSLO joystick on existing `AnimationDriver` path.
   - Add face/appearance menu only after expression switching is proven.

5. Report closure:
   - Update the single App V1 status report with completed/partial/pending.
   - Do not mark App frontend complete until the formal App scene, startup,
     RoomSetting, transition, AR placement, HUD, menu canvas, and 2D workspace
     are verified.

## 8. Ner Cheek Pinch Completion / Status

Date: 2026-05-11

Research decision:

- Public Trickcal sources and guide pages confirm the user-facing behavior:
  cheek pull / touch / pat / tickle is a core character interaction, and room
  interaction is part of the product feel.
- Public sources do not expose the original game's internal implementation.
  The App implementation therefore uses a compatible Unity/AR pattern:
  screen/touch raycast -> cheek hit region -> drag strength -> Spine cheek
  bone offset -> expression/mood response.
- Local assets are stronger implementation evidence. `NerSkin2` includes
  cheek/ball bones: `S1_F_Ball_L_CT`, `S1_F_Ball_R_CT`, and
  `Character_Ball_Move`.

Implemented:

- Manifest capabilities:
  - `cheek_pinch_start`
  - `cheek_pinch_hold`
  - `cheek_pinch_warning`
  - `cheek_pinch_release`
  - `cheek_recover`
- `NerSpineController`:
  - Parses cheek pinch `parameters_json`.
  - Normalizes `side` to `left` / `right` / `both`.
  - Offsets and scales the cheek bones during hold.
  - Resets cheek bones on release/recover.
  - Uses `Touch_Idle`, `Touch_End`, `Serious_1`, and `Angry_1` for first-pass
    visual feedback.
- `NerCheekPinchInteractor`:
  - Uses `Camera.ScreenPointToRay` and `Physics.RaycastAll` so cheek triggers
    can be found even when another model collider is closer.
  - Supports phone touch and Editor mouse.
  - Avoids stealing UI touches via `EventSystem`.
  - Recovers the cheek pose when the component is disabled or a touch is lost.
- `NerCheekHitRegion`:
  - Gives hand-authored prefab colliders a stable side marker.

Bug fixes from review:

- Lost/canceled touch no longer leaves Ner stuck in a pinch state.
- Disabling the interactor now sends `cheek_recover`.
- Raycast now scans all hits instead of only the closest hit, avoiding body
  collider occlusion of cheek triggers.
- Invalid/case-mismatched `side` values now normalize to `both`.

Coverage audit:

| Gameplay | Status | Notes |
|:--|:--|:--|
| Cheek pinch / pull | first-pass implemented | Needs prefab collider and strength tuning on device. |
| Touch / pat / tickle | capability ready | Spine handlers exist; gesture/UI binding still pending. |
| Expression switching | capability ready | Menu buttons and mood rules pending. |
| Universal joystick movement | partial | GOSLO path exists; Ner `spine_walk` exists; shared UI routing pending. |
| Long-press pickup / drag / place | first-pass implemented | Needs production prefab body collider, lift, and release tuning on device. |
| Prop/object interaction | planned | Should stay model-agnostic with model-specific reactions. |
| LineB speech reactions | planned | Should be added after LineB device route and echo guard are stable. |

Validation:

```text
Unity compile: clean
Unity Console: 0 errors / 0 warnings
NerSpineAnimationAudit: 28 manifest handlers match 60 imported animations
Unity type check: interactor=True; hitRegion=True; cheekHold=True
Focused regression: 31 passed
Wide regression: 88 passed
```

Non-blocking decision:

- This does not block LineB configurable-profile work. LineB can continue with
  ASR/TTS/ADC/voiceprint/echo readiness and RoomSetting integration while a
  separate Unity-focused chat tunes Ner prefab hit regions and device feel.

## 9. Ner Persona / Obsidian / Voice Trigger Status

Date: 2026-05-11

Implemented:

- `ner_companion` now tells Brain to use strict `play_capability` for Ner
  custom actions and reserves legacy `animate` for GOSLO/parrot animation ids.
- `ner_companion` now contains LineB-aware voice / animation trigger rules for
  listening, speaking, ASR test phrases, cheek pinch start/hold/warning/release,
  and pending pickup/place states.
- `ner_roleplay_setting_obsidian_v0_20260511.md` is the first Ner setting
  source for the Obsidian route. It is `profile: roleplay` and intentionally
  has no `obsidian_uuid` in frontmatter.
- `ner_lineb_room` now references that roleplay setting file and selects
  `lineb_ner_ja_test`.
- Static/config regression added coverage for:
  - `lineb_ner_ja_test` loading through `LineProfileLoader`.
  - `ner_lineb_room` loading through `PresetLoader`.
  - roleplay setting frontmatter staying UUID-free.
  - persona prompt containing custom capability and voice-trigger rules.
- Regression after this update:
  `tests/test_brain/test_app_first_version_facade.py`,
  `tests/test_brain/test_app_v1_monitor.py`,
  `tests/test_brain/test_menu_workspace.py`,
  `tests/test_brain/test_tools_model_id.py`,
  `tests/test_shared/test_model_manifest.py`,
  `tests/test_ecp_event/test_w8_observer_photo.py`, and
  `tests/test_unity/test_app_v1_meta_ui_static.py`: `91 passed`.

Research / implementation decision:

- Public product pages establish cheek pulling as a central user-facing
  interaction and broader room/character interaction as product feel.
- Public/community Ner details are sufficient for a test persona direction:
  high-priest, responsible caretaker, gentle surface, strict/perfectionist
  pressure response, and World Tree motif.
- Current Ner validation uses Cartesia as the selectable TTS provider because
  the user-owned/private voice-design material lives outside Git on ECS.
  Google TTS remains a fallback baseline through `lineb_google_default`.
- Do not ingest public voice clips into Git and do not clone a real CV by
  default. Any licensed/custom voice assets must stay in external private test
  storage and be selected by environment/config only.

Remaining:

- Runtime voice-trigger bridge: LineB speaking/listening/TTS-segment events
  now has a backend Blackboard surface, but still needs Unity expression and
  gesture suppression binding.
- Pickup/held/place has a first-pass Unity path, but production prefab wiring
  and device-feel tuning are still pending.
- Real-device proof still needs ASR + TTS + echo/voiceprint evidence with
  `ner_lineb_room` and `lineb_ner_ja_test` selected.

## 10. LineB Bugfix / Voice Activity Bridge

Date: 2026-05-11

Bug found and fixed:

- Before this pass, a LineB profile with blank `tts.voice_name` could appear
  merely degraded when Google ADC was also missing. That hid a hard profile
  defect behind the ADC warning.
- `line_profile.evaluate_line_profile()` and `line_status._line_b_overall()`
  now block missing TTS voice and missing ASR model/languages independently of
  ADC state.
- Regression covers the no-ADC + blank-TTS-voice case and expects the
  VoicePipeline module to stay `blocked`.
- A second review found a phone-speaker risk: a high external `echo_score`
  without a recent matching TTS segment could fall through as `user_turn` when
  ASR text was non-empty. `classify_mic_input()` now marks that case
  `uncertain` with reason `high_echo_score_without_recent_tts`, writes
  `listening_uncertain`, and recommends the `lineb_uncertain_input` trigger.
- Mic classification and the model reaction payload now tolerate malformed or
  non-finite numeric values from external DSP/status sources, so bad
  `echo_score` or suppression-duration strings do not break the turn classifier
  or Unity-facing reaction JSON.

Backend bridge added:

- `lineb_audio_guard.register_tts_segment()` now writes
  `session/lineb_voice_activity` with state `speaking`.
- `lineb_audio_guard.classify_mic_input()` now writes:
  - `listening` for user turns.
  - `agent_echo_suppressed` for recent-TTS echo suppression.
  - `listening_noise` for low-confidence empty noise.
  - `listening_uncertain` for overlap with insufficient evidence.
- `line_status.list_lines()` and `AppFirstVersionFacade` now expose
  `voice_activity_state` plus the raw `refs.voice_activity` payload.
- Blackboard schema now declares `session/lineb_voice_activity` with writer
  `brain.lineb_audio_guard`.
- `lineb_model_reaction.py` maps LineB voice activity to model-declared
  capabilities and dispatches them through strict Unity `animate` RPC when the
  active model supports the capability.
- `brain.agent` schedules that reaction after LineB user transcription
  classification and assistant TTS segment registration.

Unity / Ner bridge added:

- `ner_skin2.json` now declares:
  - `lineb_speaking`
  - `lineb_listening`
  - `lineb_echo_suppressed`
  - `lineb_listening_uncertain`
  - `lineb_listening_noise`
- `NerSpineController` handles those capabilities directly.
- During `lineb_speaking` and `lineb_echo_suppressed`, Ner resets cheek bones
  and temporarily suppresses strong local cheek/touch/pat/tickle/body-pickup
  starts so TTS and echo suppression do not fight the interaction layer.

Pickup/place bridge added:

- `ner_skin2.json` declares body pickup/held/drag/place capabilities.
- These capabilities use the existing manifest `kind: procedural`; no ECP or
  manifest protocol enum rewrite was needed.
- `NerSpineController` handles those body capabilities with existing verified
  Spine animations: `Surprise_1`, `Close_1`, `Panic_1`, `Think_1`, `Idle_1`,
  and `Worry_1`.
- `NerPickupPlaceInteractor` provides the first AR/mobile interaction path:
  long-press body hit, lift, drag, and release. It avoids UI touches, gives
  cheek hit regions priority over body pickup, uses AR plane colliders when
  present, and falls back to a horizontal plane for Editor/local testing.
- Final audit fixed two pickup/place bugs:
  - cancel/lost-touch/LineB-suppressed drag now drops the model to the last
    resolved ground point instead of leaving it suspended.
  - body/placement raycasts now treat both the interactor transform and an
    explicitly assigned `targetRoot` as the same model, which makes prefab
    tuning safer.

Micro-tuning handoff:

- Prompt file:
  `codex_workspace/design_workspace/tasks/ner_unity_tuning_chat_prompt_20260511.md`

Validation:

```text
.\.venv\Scripts\python.exe -m pytest tests\test_brain\test_app_first_version_facade.py tests\test_brain\test_app_v1_monitor.py tests\test_brain\test_menu_workspace.py tests\test_brain\test_tools_model_id.py tests\test_shared\test_model_manifest.py tests\test_ecp_event\test_w8_observer_photo.py tests\test_unity\test_app_v1_meta_ui_static.py -q
93 passed

.\.venv\Scripts\python.exe -m py_compile src\parrot\brain\line_profile.py src\parrot\brain\line_status.py src\parrot\brain\lineb_audio_guard.py src\parrot\brain\app_first_version.py src\parrot\shared\bb_schema.py
passed

.\.venv\Scripts\python.exe -m pytest tests\test_brain\test_app_first_version_facade.py tests\test_brain\test_app_v1_monitor.py tests\test_brain\test_menu_workspace.py tests\test_brain\test_lineb_model_reaction.py tests\test_brain\test_tools_model_id.py tests\test_shared\test_model_manifest.py tests\test_ecp_event\test_w8_observer_photo.py tests\test_unity\test_app_v1_meta_ui_static.py -q
97 passed

.\.venv\Scripts\python.exe -m pytest tests\test_brain\test_app_first_version_facade.py::test_lineb_high_echo_score_without_recent_tts_is_uncertain tests\test_brain\test_app_first_version_facade.py::test_lineb_malformed_echo_score_does_not_break_mic_classification tests\test_brain\test_lineb_model_reaction.py::test_lineb_voice_activity_parameters_tolerate_malformed_numbers -q
3 passed

.\.venv\Scripts\python.exe -m py_compile src\parrot\brain\lineb_audio_guard.py src\parrot\brain\lineb_model_reaction.py
passed

.\.venv\Scripts\python.exe -m pytest tests\test_brain\test_app_first_version_facade.py tests\test_brain\test_app_v1_monitor.py tests\test_brain\test_menu_workspace.py tests\test_brain\test_lineb_model_reaction.py tests\test_brain\test_tools_model_id.py tests\test_shared\test_model_manifest.py tests\test_ecp_event\test_w8_observer_photo.py tests\test_unity\test_app_v1_meta_ui_static.py -q
100 passed

.\.venv\Scripts\python.exe -m pytest tests\test_unity\test_app_v1_meta_ui_static.py tests\test_brain\test_menu_workspace.py tests\test_brain\test_tools_model_id.py tests\test_shared\test_model_manifest.py -q
59 passed

.\.venv\Scripts\python.exe -m pytest tests\test_brain\test_app_first_version_facade.py tests\test_brain\test_app_v1_monitor.py tests\test_brain\test_menu_workspace.py tests\test_brain\test_lineb_model_reaction.py tests\test_brain\test_tools_model_id.py tests\test_shared\test_model_manifest.py tests\test_ecp_event\test_w8_observer_photo.py tests\test_unity\test_app_v1_meta_ui_static.py -q
101 passed

Unity MCP validate_script:
- Assets/Scripts/ParrotApp/Parrot/NerPickupPlaceInteractor.cs: 0 errors
- Assets/Scripts/ParrotApp/Parrot/NerSpineController.cs: 0 errors
- Console after refresh: 0 errors / 0 warnings
```

## 11. Completion Snapshot For This Chat

Completed enough to move on:

- LineB is configurable through saved profiles and RoomProfile references.
- `ner_lineb_room` selects LineB, the Ner model, Ner persona, roleplay setting
  source, and Ner LineB profile.
- Ner custom capabilities are model-gated and do not claim GOSLO fly/perch.
- Ner has first-pass expression, cheek pinch, LineB voice-activity reactions,
  and body pickup/place controller paths.
- Defensive LineB echo/number handling is covered by regression.

Still not complete:

- Startup/RoomSetting Unity page is not wired.
- Production Ner prefab still needs hands-on Unity assembly and device feel
  tuning.
- Real ASR/TTS/voiceprint/echo validation still needs user-provided Google
  STT/Gemini credentials, Cartesia credentials, audio route choice, and a
  device run.
- UI asset audit and formal startup/core page implementation are the next
  frontend line after this configuration pass.

User configuration still required before true device validation:

- Google Gemini API key for LineB text generation.
- Google ADC/service-account credentials for STT.
- Cartesia API key and private voice id for the current Ner TTS path; Google
  TTS can still be tested by selecting `lineb_google_default`.
- Audio route decision: headphones first, phone speaker only for stress test.
- Unity runtime config for Castle mint/LiveKit if not already present in
  `Assets/Resources/parrot_config.json`.

Remaining boundary:

- This is code/static-test complete, not device-feel complete.
- Need Unity Editor compile and real-device pass to verify the reaction timing
  against actual TTS playback, touch latency, and cheek suppression feel.
