# LineB Configurable + Ner Gameplay Longline TODO

> Date: 2026-05-11
> Status: longline plan / execution backlog
> Route: `D:\GOSLOParrot\ParrotCarriers`
> Design route: `codex_workspace/design_workspace`
> Interface route: `.cursor/memory/architecture/Interface`

## 0. Goal

Build a testable App path where real-device validation can choose either:

1. `LineB + ASR/voiceprint + Google TTS pipeline + selectable setting stack + BrainAgent prompt + Ner model + Ner control/gameplay`.
2. `LineA + GOSLO default actions + default setting + XRHand`.

Unified prop/object interactions should work across models. Model-specific
Reflex and controls must stay model-gated: GOSLO keeps parrot flight/perch
reflexes; Ner gets its own expression, cheek, touch/pat/tickle, anger/blessing,
and AR placement gameplay.

This task starts with a plan and longline TODO. Do not mark App frontend or Ner
production complete until the final self-check matrix passes on device.

## 1. Sources Read

Local authoritative sources:

- `.cursor/memory/architecture/goslo_model_manifest_protocol_v1.md`
- `docs/sprint_archive/sprint4/goslo_modularization_residual_debt_20260506.md`
- `src/parrot/shared/ecp.py`
- `src/parrot/shared/ecp_event.py`
- `src/parrot/brain/tools/animate.py`
- `src/parrot/brain/tools/fly_to.py`
- `src/parrot/brain/tools/__init__.py`
- `src/parrot/brain/agent.py`
- `src/parrot/brain/line_status.py`
- `src/parrot/brain/lineb_audio_guard.py`
- `src/parrot/brain/menu_registry.py`
- `src/parrot/brain/room_setting.py`
- `unity/ArSpike/Assets/ParrotApp/Runtime/Scripts/RPC/EcpDtos.cs`
- `unity/ArSpike/Assets/ParrotApp/Runtime/Scripts/RPC/ParrotRpcHandler.cs`
- `unity/ArSpike/Assets/ParrotApp/Runtime/Scripts/Parrot/ParrotRegistry.cs`
- `unity/ArSpike/Assets/ParrotApp/Runtime/Scripts/Parrot/ModelDriver.cs`
- `unity/ArSpike/Assets/ParrotApp/Runtime/Scripts/Parrot/NerSpineController.cs`
- `unity/ArSpike/Assets/ParrotApp/Models/Ner/*`

External reference sources:

- Official site: https://trickcal.biligames.com/jp/
- Gamer overview: https://www.gamer.ne.jp/game/1000063611/
- Ner community page: https://wikiwiki.jp/thetrickal/%E3%83%8D%E3%83%AB
- Korean community/guide note on Ner battle state:
  https://vortexgaming.io/postdetail/746913

Source reliability rule:

- Local code/assets are implementation facts.
- Gamer/official pages can guide product-level interaction expectations such
  as cheek pinching.
- Wiki/Vortex can guide style/lore/state-machine hypotheses only. Treat them
  as community references until verified against official in-game text/video.
- Do not clone or imitate a real voice actor without a licensed voice pipeline.
  TTS config may express style labels, language, pace, and pitch, but not an
  exact CV clone unless rights and consent are explicitly available.

## 2. Current Architecture Verdict

ECP/model route is mostly sufficient for this upgrade:

- Python `EcpCommand.meta` already carries arbitrary metadata.
- Brain `animate()` and `fly_to()` already accept `model_id` and stamp
  `meta.model_id`.
- Unity `EcpCommandDto.meta.model_id` exists.
- `ParrotRpcHandler` reads `_ecp.ModelId`.
- `ParrotController` routes `model_id` through `ParrotRegistry`.
- `ModelDriver` loads `Resources/parrot_models/<model_id>.json`.
- `IParrotController.ApplyCapability(capability_id, parametersJson)` is the
  right per-model dispatch seam.

ECP/model route still has important gaps:

- `ParrotRegistry` is still P1 single-active fallback. Multi-model same
  LiveKit Room has wire space, but real keyed routing/spawn/despawn is not
  complete.
- Brain tools now hide/reject reserved parrot verbs when the active model does
  not declare them, but the LLM tool list is still rebuilt at agent startup
  rather than live-updating mid-session.
- `animate` remains intentionally limited to the 8 reserved GOSLO/parrot
  animation ids. Ner-specific actions use strict `play_capability`.
- Per-command `body_state` is still coarse/parrot-shaped. This does not block
  Ner, but `controller_body_state` or equivalent would make self-checks cleaner.
- `_rpc_bridge` still sends RPC to one arbitrary Unity participant; multi-client
  or multi-actor routing is future work.

Do not rewrite ECP wire now. Add model/capability layers on top.

## 3. Reflex Clarification

Old docs say "Reflex layer locks to reserved parrot capability ids." That does
not mean only GOSLO can have Reflex behavior.

Use three Reflex bands:

| Band | Applies to | Examples | Owner |
|:--|:--|:--|:--|
| Universal App Reflex | all models | photo awareness, attention focus, prop reaction, listen/speak indicators | App/Brain/Unity shared |
| Species/shape Reflex | model family | bird idle breathing, fly/perch, wing micro-flap | GOSLO/parrot model |
| Character Reflex | specific model/persona | Ner cheek pinch, stern smile, anger state, blessing, touch/pat/tickle | Ner model/persona |

Reserved `ParrotAnimation` ids should only trigger parrot-specific reflexes.
Model-agnostic actions and Ner-specific reflexes should use explicit
capability ids and a capability resolver, not the old parrot enum.

## 4. Ner Research Snapshot

Community Wiki currently describes Ner as:

- Name: Ner / ネル.
- Role/title: high-ranking priest / highest priest style profile.
- Species/personality tags: fairy + "madness" tag in the game taxonomy.
- Character traits: outwardly gentle, strict/perfectionist, World Tree/church
  responsibility, hidden intensity.
- CV is listed by the community page, but must be verified from official or
  in-game sources before being treated as production metadata.

Korean guide/community notes describe a combat "anger" state where Ner changes
basic attack behavior after a higher skill. Treat this as a gameplay-state
hypothesis, not yet an official implementation spec.

Local assets are stronger evidence. `NerSkin2` atlas/binary strings show:

- Face parts: angry/happy/sad/shame/surprise/tulltull eyes, eyebrows, mouth,
  blush, face shadow, mouth eat/touch/panic variants.
- Action/state families: `Idle`, `Happy`, `Angry`, `Sad`, `Shame`, `Surprise`,
  `Panic`, `Touch`, `Pat`, `Tickle`, `Eat`.
- Body hints: body, wing, hand, hair, teacher/hat/bag layers.

Needed before final animation mapping:

- Exact Spine animation names are now enumerated through Unity/Spine runtime,
  not binary string grep.
- Verify which animations loop cleanly.
- Verify hit areas for cheek/touch/pat/tickle.
- Verify whether `Wing` slots are decorative or animation-driving.

### 4.1 Gameplay Research And Decisions

Source audit on 2026-05-11:

- Official/product pages and Japanese guide sites frame Trickcal as a light,
  cute, cheek-touch/card RPG, not a precision locomotion game.
- Community gameplay notes consistently point to touch therapy as a core
  fantasy: poke, pat, tickle, and pull cheeks can happen in many contexts.
- Dorm/church-room systems support inviting characters, furniture/layout
  presets, and room interactions. This maps cleanly to App `RoomProfile`,
  AR placement, and the 2D mansion/workspace hub.
- Public sources describe the feature behavior, not the internal source code.
  Implementation inference for our app: screen/touch hit target -> drag
  strength -> cheek bone/mesh deformation -> expression/voice/mood response.
- Ner-specific community notes describe a highest-priest/perfectionist role,
  gentle public smile, strict responsibility, hidden anger, World Tree
  blessing/sanctuary motifs, and a currently community-sourced CV listing.
  Treat these as style/lore references until official or in-game verification.

Design decisions locked for first playable Ner pass:

- `joystick_walk` is a universal model locomotion affordance. GOSLO keeps its
  existing plane-walk route; Ner maps the same UI to `spine_walk`.
- Cheek pinch is required, not optional. Implement it as its own interaction
  layer with cheek hit regions, drag intensity, release/recover, and mood
  feedback.
- Long-press body pickup/drag/place is required for AR placement and workspace
  play. It should move the model transform, not pretend to be a parrot fly.
- Touch/pat/tickle/eat are secondary but already have direct Spine handlers.
- Voice/TTS style may be Ner-inspired, but do not clone a listed voice actor
  unless rights and consent are explicit.

Open user decisions:

- Cheek pinch tone: mostly cute/tolerant, stern warning after repeated pulls,
  or faster anger escalation?
- Pickup tone: calm floating doll, surprised/flustered, or strict protest when
  held too long or shaken?
- Should AR placement use only long-press body drag, or also allow a menu
  "re-place" button for accessibility?
- Should `joystick_walk` be exposed as a generic capability id in manifests
  (`locomotion_walk`) while keeping `spine_walk` as Ner's internal handler?

First implementation completed on 2026-05-11:

- `NerSpineController` supports `cheek_pinch_start`, `cheek_pinch_hold`,
  `cheek_pinch_warning`, `cheek_pinch_release`, and `cheek_recover`.
- The controller directly offsets Spine cheek bones `S1_F_Ball_L_CT`,
  `S1_F_Ball_R_CT`, and `Character_Ball_Move`, then restores them on release.
- `NerCheekPinchInteractor` uses camera screen rays against cheek trigger
  colliders, so the same path works for AR Foundation camera views, phone
  touch, and editor mouse testing.
- Current limitation: cheek collider local positions and stretch strength still
  need production prefab/device tuning.
- Bug audit/fixes: lost touch and disabled component now recover the face;
  cheek raycast scans all hits so body colliders do not mask cheek triggers;
  malformed `side` payloads normalize to `both`.
- `NerPickupPlaceInteractor` adds the first long-press body pickup / drag /
  place path. It uses phone touch or Editor mouse, avoids UI touches, ignores
  cheek hit regions so cheek pinch keeps priority, and drops to AR plane
  colliders when present or a horizontal fallback plane otherwise.

## 5. Target State Machine

Use layered state machines instead of one monolithic enum.

### 5.1 Shared Model Runtime State

- `not_loaded`
- `loading`
- `ready_idle`
- `interaction_locked`
- `speaking`
- `listening`
- `thinking`
- `error_fallback`

### 5.2 Locomotion Layer

- `anchored`
- `joystick_walk`
- `approach_target`
- `return_home`
- `placed_on_plane`
- `body_long_press_pickup`
- `held_in_air`
- `dragging_in_air`
- `place_preview`
- `place_release`

GOSLO may also expose:

- `fly`
- `perch`
- `perched_on_hand`

Ner should not claim fly/perch until the controller has a real authored path.
For pickup, use a model-agnostic transform/placement controller with Ner
expression overlays (`Surprise_1`, `Close_1`, `Panic_1`, `Serious_1`,
`Angry_1`) rather than parrot flight semantics.

### 5.3 Expression Layer

Ner first pass:

- `face_idle`
- `face_happy`
- `face_angry`
- `face_sad`
- `face_shame`
- `face_surprise`
- `face_panic`
- `face_tulltull`
- `face_yummy`

GOSLO first pass:

- Keep existing body/head states.
- Add optional lightweight expression vocabulary only if the asset/controller
  has real targets.

### 5.4 Cheek / Touch Layer

Ner:

- `cheek_target_ready`
- `touch_idle`
- `touch_end`
- `pat_idle`
- `pat_end`
- `tickle_idle`
- `tickle_end`
- `cheek_hover`
- `cheek_pinch_start`
- `cheek_pinch_hold`
- `cheek_pinch_warning`
- `cheek_stretch`
- `cheek_release`
- `cheek_recover`

AR adaptation:

- XRHand pinch or touch ray targets cheek colliders/2D hit regions.
- Drag distance maps to cheek stretch, face expression, and voice reaction.
- Release maps to bounce-back and mood update.
- The original game's cheek-pinching principle is adapted as AR interaction,
  not copied as UI art or exact voice lines.

### 5.5 Ner Character Mood Layer

First implementation, source-aware:

- `calm_priest`
- `gentle_smile`
- `stern_warning`
- `hidden_anger`
- `blessing`
- `flustered`
- `recovering`

Possible later layer after official verification:

- `anger_combat_state`
- `world_tree_blessing`
- `banner/sanctuary`

## 6. LineB Configurable Stage

LineB must move from env-var-only to App-configurable profile.

Target objects:

- `LineProfile`
- `AsrProfile`
- `TtsProfile`
- `VoiceprintProfile`
- `EchoPolicy`
- `LineDeviceCheckResult`

RoomProfile should reference:

- `line_id`
- `line_profile_id`
- `asr_profile_id`
- `tts_profile_id`
- `voiceprint_profile_id`
- `echo_policy_id`

Minimum config fields:

```json
{
  "line_profile_id": "lineb_google_ja_ner_v0",
  "line_id": "line_b",
  "asr": {
    "provider": "google.STT",
    "model": "latest_long",
    "languages": ["ja-JP", "cmn-CN", "en-US"]
  },
  "tts": {
    "provider": "google.TTS",
    "language": "ja-JP",
    "voice_name": "",
    "style_note": "Ner-inspired test style; no voice cloning"
  },
  "voiceprint": {
    "enabled": true,
    "speaker_policy": "monitor_then_gate"
  },
  "echo": {
    "output_route": "headphones",
    "handling_mode": "isolated_route"
  }
}
```

Backend work:

- Add config files under `data/line_profiles/`.
- Add a loader/validator with env fallback.
- Extend `line_status.list_lines()` to show selected profile values.
- Extend RoomSetting compatibility to explain missing API key, missing ADC,
  missing TTS voice, voiceprint disabled, and echo route risk.
- Keep existing env variables as override/fallback for dev.

UI work:

- Startup RoomSetting Line panel shows LineA/LineB.
- LineB expanded state shows ASR/TTS/ADC/VAD/voiceprint/echo readiness.
- User can select or save a Line profile.
- START blocks or warns based on selected `experience_mode`.

## 7. Longline TODO

### Phase 0 - Route And Source Freeze

- [x] Read old manifest protocol and residual debt docs.
- [x] Audit current ECP model_id path.
- [x] Audit current LineB readiness path.
- [x] Audit local Ner Spine assets.
- [x] Search external Ner/game references.
- [x] Save source/reliability notes beside the longline plan.
- [x] Do not import extra full asset packages. Only use existing/curated assets.

### Phase 1 - LineB Configurable Profiles

- [x] Create `data/line_profiles/` with `lineb_google_default.json`.
- [x] Create selectable Ner validation profile
  `data/line_profiles/lineb_ner_ja_test.json`.
- [x] Add `LineProfile` dataclass/Pydantic schema.
- [x] Add `LineProfileLoader` with env fallback.
- [x] Add facade methods:
  - `list_line_profiles()`
  - `preview_line_profile()`
  - `save_line_profile()`
  - `apply_line_profile()`
- [x] Extend `RoomProfile` to reference Line profile ids without breaking v3.
- [x] Extend `line_status.py` to surface active profile.
- [x] Extend monitor endpoints for profile preview/apply.
- [x] Add tests for missing API key, missing ADC, missing TTS voice, voiceprint
  disabled, and echo route risk.
- [x] Add a real-device checklist for LineB startup.
- [x] Update `ner_lineb_room` to select the Ner LineB profile by default.

Completion signal:

- RoomSetting can choose `LineB`, a saved ASR/TTS/voiceprint profile, and a
  visible echo policy before START.

### Phase 2 - Capability Resolver And Tool Gating

- [x] Promote the current model-manifest read in `MenuRegistry` into a small
  Brain-side `ModelManifestRegistry`.
- [x] Add per-model capability lookup:
  - selected model provides
  - selected persona requires
  - scene supports
  - device/permissions allow
- [x] Extend `RoomSettingService.compatibility()` beyond `fly_to_hand`.
- [x] Add a `play_capability` Brain tool for custom capability ids.
- [x] Add Unity RPC `playCapability` or extend `animate` with a safe custom
  capability path.
- [x] Keep `animate` reserved for the 8 parrot vocabulary ids.
- [x] Dynamically hide or reject `fly_to` when active model lacks `fly`.
- [x] Add ack reason `capability_unsupported` to Unity rejection path.
- [x] Add tests that Ner cannot fly/perch but can play face/touch capabilities.

Completion signal:

- Brain does not ask Ner to fly, but can ask Ner to smile, react, idle, touch,
  pat, tickle, eat, or walk when those capabilities are declared.
- Strict `play_capability` calls preserve `parameters_json` into Unity model
  controllers and fail with `capability_unsupported:<id>` instead of silently
  falling back to legacy parrot animation routes.

### Phase 3 - ECP/State Extensions Without Wire Rewrite

- [ ] Keep existing `EcpCommand.meta.model_id`.
- [ ] Add typed optional meta slots only if needed:
  - `actor_id`
  - `capability_id`
  - `interaction_id`
- [ ] Consider `EcpFrontendState.controller_body_state` as backward-compatible
  optional field.
- [ ] Do not change existing `body_state` semantics in this phase.
- [ ] Add freeze/static tests for any new C#/Python DTO mirror fields.

Completion signal:

- Model-specific state is visible to self-checks without breaking old ECP
  events, acks, or cs parity tests.

### Phase 4 - Ner Asset Enumeration And Controller Upgrade

- [x] In Unity, enumerate exact Spine animation names from
  `NerSkin2_SkeletonData.asset`.
- [x] Replace binary-string guesses in `ner_skin2.json` with verified names.
- [ ] Create/verify a Ner prefab:
  - Spine skeleton component
  - `ModelDriver(modelId=ner_skin2)`
  - `NerSpineController`
  - cheek/touch hit regions
  - preview camera-safe scale
- [x] Add loop/one-shot metadata for primary capabilities.
- [x] Add idle fallback if a requested animation is missing.
- [x] Add Unity editor/static tests or MCP checklist for manifest/controller.

Completion signal:

- Unity can load Ner by `model_id`, play idle/expression/touch animations, and
  report unsupported capabilities cleanly.
- Current verified boundary: Unity Editor read 60 imported Ner animations from
  `SkeletonDataAsset`; `NerSpineAnimationAudit` validated 28 primary manifest
  handlers. Prefab wiring and hit-region tuning are still pending.

### Phase 5 - Ner Gameplay Layer

- [ ] Implement Ner layered state machine.
- [ ] Add expression menu buttons.
- [x] Add first-pass cheek pinch/touch interaction.
- [x] Add first-pass long-press pickup / held / drag / place interaction.
- [ ] Tune cheek hit regions and stretch feel on the production prefab/device.
- [ ] Tune body pickup collider, lift height, and release feel on the
  production prefab/device.
- [ ] Add pat/tickle/eat interaction buttons or gestures.
- [ ] Add mood transitions:
  - neutral -> happy
  - pinch too long -> stern/anger
  - release -> recover
  - user praise -> gentle/blessing
- [ ] Add LineB speech hooks:
  - listening indicator
  - speaking indicator
  - echo-risk warning
  - TTS segment registration
- [x] Add backend LineB voice-activity bridge:
  - `speaking` from registered TTS segments
  - `listening` from accepted user turns
  - `agent_echo_suppressed` from echo guard decisions
  - `session/lineb_voice_activity` for App menus and future Unity reactions
- [x] Add strict model reaction bridge:
  - `lineb_model_reaction.py`
  - `lineb_speaking`
  - `lineb_listening`
  - `lineb_echo_suppressed`
  - `lineb_listening_uncertain`
  - `lineb_listening_noise`
- [x] Add Ner controller handling for those LineB capabilities, including
  speaking/echo suppression of strong cheek/touch reactions.
- [x] Add first-pass persona / setting-source trigger rules for listening,
  speaking, cheek pinch, ASR tests, and pending pickup/place.
- [x] Add defensive echo-score behavior: high `echo_score` without a recent TTS
  match becomes `listening_uncertain`, not a user turn.
- [x] Add numeric input hardening: malformed or non-finite external
  `echo_score` / suppression-duration values do not break mic classification or
  Unity reaction payload generation.
- [x] Add first-pass cooldown and interruption rules so strong gameplay
  gestures do not conflict with TTS playback.

Completion signal:

- Ner feels like a real AR character: selectable, expressive, pinchable,
  controllable, and compatible with LineB turn-taking.

### Phase 6 - Startup RoomSetting Integration

- [ ] `SCENE` opens RoomSetting page.
- [ ] Room selector lists `ner_lineb_room`.
- [ ] Model selector lists `GOSLO_default` and `ner_skin2`.
- [ ] Persona selector lists `goslo_parrot_default` and `ner_companion`.
- [ ] Line selector lists LineA/LineB plus profile readiness.
- [ ] Scene selector shows AR/2D scene choices and skin/map.
- [ ] START applies the effective RoomProfile and LineProfile.
- [ ] IPoAC transition starts permissions/Mint/LiveKit connect.
- [ ] Connect success stays silent.
- [ ] Greeting waits until AR plane ready + explicit placement.

Completion signal:

- A user can choose either Ner+LineB or GOSLO+LineA from startup without editing
  environment variables or JSON by hand.

### Phase 7 - GOSLO Gameplay Upgrade

- [ ] Keep existing joystick plane-walk.
- [ ] Route joystick through the model-control abstraction where possible.
- [ ] Add GOSLO control polish:
  - speed/turn smoothing
  - return-home
  - hand-perch availability
  - XRHand interaction affordances
- [ ] Add GOSLO-specific ReflexProfile:
  - bird idle
  - wing micro-flap
  - perch/fly gating
- [ ] Add shared expression/reaction slots only when backed by real assets.

Completion signal:

- GOSLO improves without forcing bird-only assumptions onto Ner.

### Phase 8 - Unified Prop/Object Interaction

- [ ] Define `InteractionAffordance`:
  - `inspect`
  - `touch`
  - `pick_up`
  - `place`
  - `use`
  - `react`
- [ ] Define `ModelInteractionAdapter` per model.
- [ ] Let props ask for abstract interactions, not model-specific animations.
- [ ] Map abstract interaction to each model:
  - GOSLO: fly/perch/peck/wing reaction where supported.
  - Ner: walk/gesture/expression/touch reaction where supported.
- [ ] Keep Photo Awareness, Focus, BBox, XRHand, and object memory shared.

Completion signal:

- The same prop can be used by GOSLO or Ner with different animations but one
  App-level interaction contract.

### Phase 9 - Real Device Self-Check Matrix

Every real-device pass must record:

- selected RoomProfile id
- selected LineProfile id
- selected model id
- selected persona id
- selected scene/skin/map
- permission state
- LiveKit connection state
- ASR readiness/result
- TTS voice/language/result
- voiceprint state
- echo risk/decision
- model load result
- capability test results
- joystick/control result
- prop interaction result
- greeting timing result

Ner + LineB pass:

- [ ] `ner_lineb_room` selected.
- [ ] LineB ready or degraded reason shown.
- [ ] Ner loads and idles.
- [ ] User phrase ASR recognized.
- [ ] TTS reply plays.
- [ ] Recent TTS is registered.
- [ ] Echo-like mic input is not treated as user speech.
- [ ] Expression switch works.
- [ ] Cheek/touch interaction works.
- [ ] Joystick/walk works or shows a clear pending reason.
- [ ] Prop interaction uses shared affordance.

GOSLO + LineA pass:

- [ ] default Room selected.
- [ ] LineA ready.
- [ ] GOSLO loads.
- [ ] XRHand path works.
- [ ] Original actions still work.
- [ ] Joystick movement works.
- [ ] Shared prop interaction works.

Completion signal:

- Self-check report clearly separates complete, partial, blocked, and pending.

### Phase 10 - Reporting And Cleanup

- [ ] Update single App V1 status report only after evidence exists.
- [ ] Keep smoke scene as test tool, not App completion evidence.
- [ ] Archive or supersede outdated docs.
- [ ] Add new blocker list to `ACTIVE_CONTEXT.md`.
- [ ] Keep `ParrotSmokeScene` out of completion claims.

## 8. Risks

- External Ner info is partially community-sourced; official verification is
  required before final persona/canon claims.
- Voice actor/CV metadata must not turn into unauthorized voice cloning.
- Spine animation names must be enumerated in Unity, not guessed from binary.
- Adding custom capability calls without tool gating may let the LLM request
  unsupported actions.
- Multi-model same LiveKit Room is not complete even though `model_id` has wire
  space.
- Startup UI must not regress into old smoke/meta UI completion claims.

## 9. Next Immediate Work

1. Bind RoomSetting startup page after the backend selectors are stable.
2. Verify the production Ner prefab with Spine component,
   `ModelDriver(modelId=ner_skin2)`, `NerSpineController`, cheek/touch hit
   regions, and camera-safe scale.
3. Add the runtime LineB voice-trigger bridge so listening/speaking/TTS
   segments can suppress or select Ner expressions.
4. Tune pickup / held / place states on the production Ner prefab and device.
5. Run the real-device pass with `ner_lineb_room` + `lineb_ner_ja_test`.

## 10. Persona / Obsidian / Voice Config Update

Date: 2026-05-11

Completed in this pass:

- `ner_companion` now uses `play_capability` for Ner custom actions and keeps
  legacy `animate` reserved for GOSLO/parrot verbs.
- `ner_companion` now includes LineB-aware voice/animation trigger rules for
  listening, speaking, ASR test phrases, cheek pinch, and pending pickup/place.
- `codex_workspace/design_workspace/unity_ar_app/ner_roleplay_setting_obsidian_v0_20260511.md`
  is the first Ner `profile: roleplay` setting source. Its frontmatter uses
  `obsidian_note_key` and intentionally omits `obsidian_uuid`.
- `data/line_profiles/lineb_ner_ja_test.json` is the first selectable Ner
  LineB config: `ja-JP`, `cmn-CN`, `en-US` ASR, `ja-JP-Neural2-B` TTS,
  voiceprint monitor-then-gate, and isolated headphone route.
- `data/presets/ner_lineb_room.json` now references the roleplay setting source
  and selects `lineb_ner_ja_test`.
- Bugfix: missing LineB `tts.voice_name` now blocks even when ADC is also
  missing, instead of being hidden behind an ADC-degraded status.
- Backend voice-trigger bridge now exposes `voice_activity_state` and
  `session/lineb_voice_activity`; `lineb_model_reaction.py` maps it into strict
  model capabilities and Ner handles those capabilities. Unity Editor compile
  and device-feel tuning remain pending.
- Defensive echo guard: high external `echo_score` without a recent matching
  TTS segment now becomes `uncertain` / `listening_uncertain`, and malformed or
  non-finite numeric DSP/status values no longer break mic classification or
  Unity reaction payloads.
- Ner pickup/place first pass: `ner_skin2.json` declares body pickup/held/drag/
  place capabilities, `NerSpineController` handles them, and
  `NerPickupPlaceInteractor` maps long-press body interaction to AR-compatible
  placement. LineB speaking/echo suppression now blocks new strong body/touch
  starts while allowing release/cancel recovery. Body capabilities use the
  current manifest `procedural` kind, avoiding an unnecessary protocol enum
  expansion.
- Final audit bugfix: cancel/lost-touch/LineB-suppressed drag now drops the
  model to the last resolved ground point instead of leaving it suspended.
  Body and placement raycasts now handle prefabs where the interactor transform
  and `targetRoot` are different.
- Dedicated micro-tuning chat prompt:
  `codex_workspace/design_workspace/tasks/ner_unity_tuning_chat_prompt_20260511.md`.

Validation:

```text
.\.venv\Scripts\python.exe -m pytest tests\test_unity\test_app_v1_meta_ui_static.py tests\test_brain\test_menu_workspace.py tests\test_brain\test_tools_model_id.py tests\test_shared\test_model_manifest.py -q
59 passed
.\.venv\Scripts\python.exe -m pytest tests\test_brain\test_app_first_version_facade.py tests\test_brain\test_app_v1_monitor.py tests\test_brain\test_menu_workspace.py tests\test_brain\test_lineb_model_reaction.py tests\test_brain\test_tools_model_id.py tests\test_shared\test_model_manifest.py tests\test_ecp_event\test_w8_observer_photo.py tests\test_unity\test_app_v1_meta_ui_static.py -q
101 passed
Unity MCP validate_script for NerPickupPlaceInteractor.cs and
NerSpineController.cs: 0 errors; Console after refresh: 0 errors / 0 warnings.
```

Decision:

- Use `ja-JP-Neural2-B` as the first Google TTS baseline. It is a supported
  Japanese female Neural2 voice and gives a stable SSML-compatible baseline.
- Treat CV/voice actor info as reference only. Public or extracted audio must
  not enter Git, and a cloned/exact voice is not a default project behavior.

