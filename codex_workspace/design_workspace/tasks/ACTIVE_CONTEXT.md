# Design Workspace Active Context

> Updated: 2026-05-11
> Code repo / Codex project route: `D:\GOSLOParrot\ParrotCarriers`
> App design workspace: `D:\GOSLOParrot\ParrotCarriers\codex_workspace\design_workspace`
> Clean status report: `.cursor/memory/architecture/Interface/app_v1_current_status_and_test_report_20260510.md`

## Current Truth

The formal App frontend is **not complete**.

`D:\GOSLOParrot` is not the code repository. The root-level `D:\GOSLOParrot\codex_workspace` was a duplicate route and has been removed. New Codex work for this app should start from `D:\GOSLOParrot\ParrotCarriers`.

The only App design workspace is:

- `codex_workspace/design_workspace`

The only current App V1 status/test report is:

- `.cursor/memory/architecture/Interface/app_v1_current_status_and_test_report_20260510.md`

## Completed Inventory

Completed backend/interface surfaces:

- `AppFirstVersionFacade`
- `list_module_statuses()`
- `canvas_snapshot()`
- `apply_workspace()`
- Google draft, Nanobot report, Photo Awareness, XRHand, Camera mode facade

Completed menu/preset foundations:

- `PresetLoader`
- `MenuRegistry`
- `WorkspaceRegistry`
- `SessionPolicy`
- `AppStartupConfigDto`
- `data/presets/default.json`
- `RoomProfile`
- `RoomSettingService`
- `line_status.py`
- `lineb_audio_guard.py`
- `VOICE_PIPELINE` App module status
- `ner_lineb_room` RoomProfile draft
- `ner_companion` Persona draft
- `ner_skin2` model manifest and `NerSpineController` probe

Completed or selected assets:

- Unity imported Wood drawer/button, Paper notes, NekoClaw, BBox frame, and icon sheets under `unity/ArSpike/Assets/UI/ParrotApp`.
- Ner raw Spine assets exist under `unity/ArSpike/Assets/Models/Ner`.
- Ner is now a selectable backend/model-menu candidate through
  `unity/ArSpike/Assets/Resources/parrot_models/ner_skin2.json`.
- Ner has first-pass Unity controller probes for Spine capabilities, cheek
  pinch, and body pickup/place. It is **not** yet a verified production Unity
  prefab or real-device model.
- Pixel asset selection/mapping docs exist; only `pixel_asset_workspace/curated` should guide App import.

Verified narrow tests from the cleaned report path:

- Facade tests
- Monitor tests
- Photo observer tests
- Unity meta UI static tests
- 2026-05-11 LineB/RoomSetting related regression: `42 passed`
- 2026-05-11 LineB/model capability resolver regression: `88 passed`; strict capability bugfix focused regression: `29 passed`; Ner Spine/cheek manifest focused regression: `31 passed`

## Non-Completion Evidence

These are useful test evidence only. They must not be used as App completion evidence:

- `ParrotSmokeScene`
- Web monitor / browser smoke
- Longline self-check or smoke-derived completion docs
- Unity runtime UI prototype mounted into a smoke scene

## Blocking Original Requirements

1. Room Setting: the startup `SCENE` entry opens an App preset/config page for saved Room preset, LineA/LineB, Model, setting file, Scene, skin, Persona, and Mode. Here `Room` means App menu preset, not LiveKit Room.
2. LineB menu upgrade: the menu must show ASR/TTS readiness, Google ADC status, voiceprint/speaker state, echo risk, and echo handling mode.
3. Ner second model: Ner must move from raw asset to selectable production model path. Startup must be able to choose Brain pipeline, model, setting, scene, and skin.

2026-05-10 RoomSetting clarification:

- User-facing saved preset name: `Room`.
- Internal/professional term: `RoomProfile`.
- Startup RoomSetting exposes Room select/new/save plus five selectors only: `Model`, `Room`, `Persona`, `Line`, `Scene`.
- Do not use a bare startup field named `Mode`. The startup-page right-side lever is `experience_mode`; GOSLO behavior flags are `behavior_mode` and belong to runtime Brain/persona menus.
- New interface contract: `.cursor/memory/architecture/Interface/app_v1_room_setting_room_profile_interface_20260510.md`.

2026-05-11 LineB clarification:

- LineB menu readiness backend is partial: `src/parrot/brain/line_status.py` exposes LineA/LineB, Google API key, Google ADC, ASR, TTS, VAD, voiceprint/speaker, and echo state.
- `src/parrot/brain/lineb_audio_guard.py` now owns `session/audio_route_policy`, recent TTS segment registry, and last mic-input decision evidence.
- RoomSetting `selectors.lines` and App module `VOICE_PIPELINE` now carry the structured LineB status plus recent TTS / last input decision fields.
- Facade/Web/RPC surfaces exist for audio route policy, TTS segment registration, and mic input classification.
- This is not final voiceprint echo suppression. Real acoustic/DSP echo score, true voiceprint comparison, Unity warning UI, and real-device LineB smoke remain pending.
- Interface contract: `.cursor/memory/architecture/Interface/app_v1_lineb_menu_readiness_interface_20260511.md`.

2026-05-11 LineB + Ner validation route:

- Config/report: `.cursor/memory/architecture/Interface/app_v1_lineb_ner_realdevice_config_report_20260511.md`.
- RoomProfile: `data/presets/ner_lineb_room.json`.
- Persona: `src/parrot/brain/personas/ner_companion.md`.
- Ner LineProfile: `data/line_profiles/lineb_ner_ja_test.json`.
- Ner roleplay setting source:
  `codex_workspace/design_workspace/unity_ar_app/ner_roleplay_setting_obsidian_v0_20260511.md`
  (`profile: roleplay`, no `obsidian_uuid` in frontmatter).
- Scene draft: `codex_workspace/design_workspace/unity_ar_app/ner_mochi_scene_v0_20260511.md`.
- Model manifest: `unity/ArSpike/Assets/Resources/parrot_models/ner_skin2.json`.
- Unity controller probe: `unity/ArSpike/Assets/Scripts/ParrotApp/Parrot/NerSpineController.cs`.
- Unity animation audit: `unity/ArSpike/Assets/Scripts/ParrotApp/Editor/NerSpineAnimationAudit.cs`.
- Current boundary: RoomSetting can recognize/select Ner; Unity Editor has verified 60 imported Spine animations and primary manifest handlers. First-pass cheek pinch code exists (`NerCheekPinchInteractor` + Spine cheek-bone offset/reset), and first-pass body pickup/place code exists (`NerPickupPlaceInteractor` + body capabilities). Unity prefab wiring, startup UI binding, joystick routing to `spine_walk`, expression-button UI, hit-region tuning, and real-device ASR/TTS pass remain pending.

2026-05-11 LineB configurable + Ner gameplay longline:

- Longline TODO: `codex_workspace/design_workspace/tasks/lineb_ner_gameplay_longline_todo_20260511.md`.
- Architecture verdict: the current ECP `meta.model_id` route is sufficient for this round. Do not rewrite the ECP wire protocol before the profile, manifest, and capability layers are implemented.
- Phase 1 complete: LineB now has `LineProfile`, `LineProfileLoader`, `data/line_profiles/lineb_google_default.json`, RoomProfile line-profile ids, facade methods, Web monitor endpoints, and status/device-check tests.
- Phase 2 complete enough for the next Unity/Ner pass: `ModelManifestRegistry` mirrors Unity manifests, RoomSetting exposes per-model capability decisions, `play_capability` validates custom capability ids, and active Ner hides/rejects `fly_to`/reserved `animate` while keeping custom face/touch capabilities available. Strict custom capability calls now preserve Unity `parameters_json` and return `capability_unsupported:<id>` when rejected.
- Phase 4 partial: Ner `SkeletonDataAsset` exact animation names are enumerated in Unity; `ner_skin2.json` now uses verified primary handlers with variant metadata; `NerSpineController` supports `parameters_json` variant/exact-animation dispatch and idle visual fallback on missing animation.
- 2026-05-11 gameplay audit: Trickcal references point to cheek-touch/poke/pat/tickle and room/invite/furniture interactions as the core feel. Ner first playable must prioritize universal joystick movement, cheek pinch, long-press pickup/drag/place, and touch/pat/tickle/eat before deeper combat-like systems. Cheek pinch first pass is implemented in code; production prefab/device tuning remains.
- 2026-05-11 bug audit: cheek pinch now recovers on disabled/lost touch, scans all raycast hits so body colliders do not hide cheek triggers, and normalizes invalid side payloads. This Ner work is non-blocking for continuing LineB configurable-profile and RoomSetting integration.
- 2026-05-11 persona/config update: `ner_companion` now uses `play_capability`
  for Ner custom actions, carries LineB-aware voice/animation trigger rules,
  and `ner_lineb_room` now defaults to `lineb_ner_ja_test`. The roleplay
  Obsidian setting source uses `obsidian_note_key` instead of UUID binding.
- 2026-05-11 Session Context Pack: selected Room setting files now feed runtime
  instructions and UUID-free Obsidian roleplay L1.5 payloads. Persona remains
  loaded by `PersonaLoader`; roleplay/world/scene/action-manual files are Room
  session context. Contract:
  `.cursor/memory/architecture/Interface/app_v1_session_context_pack_upgrade_20260511.md`.
- 2026-05-11 LineB bugfix/bridge: missing `tts.voice_name` now blocks even
  when ADC is also missing. `lineb_audio_guard` now writes
  `session/lineb_voice_activity` for `speaking`, `listening`,
  `agent_echo_suppressed`, and related states; App status exposes
  `voice_activity_state`. `lineb_model_reaction.py` now dispatches those states
  as strict model capabilities, and Ner handles them by switching expression or
  suppressing cheek/touch reactions while speaking / echo-suppressed.
- 2026-05-11 LineB defensive echo guard: high `echo_score` without a recent
  matching TTS segment now becomes `uncertain` / `listening_uncertain`, not a
  user turn. Malformed or non-finite numeric DSP/status values no longer break
  mic classification or the Unity-facing reaction payload.
- 2026-05-11 Ner pickup/place first pass: `ner_skin2.json` declares
  body pickup/held/drag/place capabilities, `NerSpineController` handles them,
  and `NerPickupPlaceInteractor` maps long-press body interaction to
  AR-compatible placement. LineB speaking/echo suppression now blocks new
  strong body/touch starts while allowing release/cancel recovery. Manifest
  capability `kind` stays within the current protocol enum
  (`pose` / `animation` / `procedural`).
- 2026-05-11 final audit fix: pickup cancel/lost-touch/LineB-suppressed drag
  now drops Ner back to the last ground point instead of leaving the model
  suspended. Body/placement raycasts now respect both the interactor transform
  and an explicitly assigned `targetRoot`.
- Micro-tuning handoff prompt:
  `codex_workspace/design_workspace/tasks/ner_unity_tuning_chat_prompt_20260511.md`.
- Latest focused App/LineB/Ner regression: `101 passed` plus py_compile passed
  for touched Python LineB/reaction files. Unity MCP `validate_script` reports
  0 errors for `NerPickupPlaceInteractor.cs` and `NerSpineController.cs`, and
  Console after refresh has 0 errors / 0 warnings. Real-device timing/feel are
  still pending.
- Next blockers:
  1. Phase 4 remaining: create/verify the production Ner prefab with Spine component, `ModelDriver(modelId=ner_skin2)`, `NerSpineController`, cheek/touch hit regions, and camera-safe scale.
  2. Phase 5+: Unity/device tuning for LineB voice-trigger reactions, Ner gameplay, GOSLO joystick/gameplay upgrade, unified prop/object interaction.
  3. Startup/RoomSetting Unity binding for saved RoomProfile, Line, Model, Persona, and Scene selectors.

## App Frontend Longline

1. **调研**：read the source design docs, HTML sketches, interface docs, Unity Build Settings, existing scenes, assets, and App scripts before implementation.
2. **启动页**：implement the landscape startup page with `GOSLO Parrot`, `SCENE`, `START`, Mode lever, and model portrait slot.
3. **Room Setting**：complete the preset/config page with saved Room/RoomProfile, Model, Room, Persona, Line, and Scene selectors. The startup lever is `experience_mode`; GOSLO behavior flags stay runtime-owned.
4. **启动转场**：create an independent IPoAC progress page; permission checks, Mint, and LiveKit connect run during this transition. Successful connect must stay silent.
5. **AR 主界面**：add a formal App scene to Build Settings and stop treating the smoke scene as the App entry.
6. **放置与问候**：after AR plane ready, wait for user placement. Only after placement should GOSLO wake/question and greet.
7. **HUD 与工具抽屉**：left-top HUD and right-bottom tool drawer should be low-occlusion while collapsed and useful when expanded.
8. **菜单画布**：complete Model / Persona / Mode / Scene / 2DWorkspace, then add LineB, Ner, and external module status.
9. **2D 工作区**：implement mansion hub, work desk, paper/report/calendar/photo entries; switching must not destroy LiveKit session.
10. **素材落位**：import only curated assets, record Unity import settings, and do not import the full asset package.
11. **收口报告**：keep one App V1 completion/test report with completed, partial, not complete, and next-round risk sections.

## Entry Order For New App Frontend Work

1. `codex_workspace/design_workspace/tasks/ACTIVE_CONTEXT.md`
2. `codex_workspace/design_workspace/unity_ar_app/startup_menu_design_v0_20260509.md`
3. `codex_workspace/design_workspace/sketches/startup_menu_landscape_v0.html`
4. `codex_workspace/design_workspace/unity_ar_app/main_hud_landscape_v0_20260509.md`
5. `codex_workspace/design_workspace/sketches/main_hud_landscape_v0.html`
6. `.cursor/memory/architecture/Interface/app_v1_room_setting_room_profile_interface_20260510.md`
7. `codex_workspace/design_workspace/tasks/lineb_ner_gameplay_longline_todo_20260511.md` for LineB/Ner implementation planning.
8. `codex_workspace/design_workspace/tasks/ner_unity_tuning_chat_prompt_20260511.md` when opening a dedicated Ner prefab/device-feel tuning chat.
9. Backend interface documents only after the page flow is understood.

## Route Rules

- Page design and App flow decisions come first from this Design workspace.
- Cursor memory is backend/protocol/interface context; it must not override the page flow already designed here.
- If the task is App page design or Unity frontend implementation, do not start from `ParrotSmokeScene`, Web monitor reports, or old longline/self-check docs.
- If the task changes backend protocol, DTOs, BB keys, RPC methods, or public Python surfaces, use `.cursor/memory/architecture/Interface/INDEX.md`.
