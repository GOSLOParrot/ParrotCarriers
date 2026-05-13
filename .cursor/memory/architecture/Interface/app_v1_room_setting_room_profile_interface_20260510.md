---
title: App V1 Room Setting And Room Profile Interface
date: 2026-05-10
status: ratified-design / partial-implementation
category: business-interface
owner: Codex / App V1
scope: startup RoomSetting, Room Profile persistence, runtime menu persistence, capability compatibility
code:
  - src/parrot/brain/room_setting.py
  - src/parrot/brain/line_status.py
  - src/parrot/brain/preset_loader.py
  - src/parrot/brain/menu_registry.py
  - src/parrot/brain/app_first_version.py
  - src/parrot/brain/app_monitor_server.py
  - src/parrot/shared/bb_schema.py
  - unity/ArSpike/Assets/ParrotApp/Runtime/Scripts/Config/AppStartupConfigDto.cs
  - unity/ArSpike/Assets/ParrotApp/Runtime/Scripts/Lifecycle/AppStartupFlowController.cs
tests:
  - tests/test_brain/test_menu_workspace.py
  - tests/test_brain/test_app_first_version_facade.py
related:
  - app_v1_facade_core_business_interface_20260510.md
  - app_v1_current_status_and_test_report_20260510.md
  - app_web_parallel_routes_agent_team_20260513.md
  - menu_design_complete_20260507.md
  - ../../../../codex_workspace/design_workspace/unity_ar_app/startup_menu_design_v0_20260509.md
---

# App V1 Room Setting / Room Profile Interface

## 0. Decision

The startup `SCENE` entry opens **RoomSetting**.

The user-visible saved preset is called **Room**. The internal product/interface term is **RoomProfile**.

`RoomProfile` is an App-level saved configuration for launching and restoring a companion workspace. It is not a LiveKit room. A LiveKit transport room, when needed, must be named `livekit_room_id` and kept inside connection/startup transport fields.

Startup RoomSetting is intentionally small:

1. Select existing Room.
2. Create new Room.
3. Save current Room draft.
4. Switch the six launch axes: `Model`, `Room`, `Persona`, `Line`, `Theme`, `Maid Team`.

The startup RoomSetting page must not expose the ambiguous label `Mode`.

2026-05-13 App correction:

- User-visible `Scene` was too ambiguous for startup RoomSetting. The startup
  selector is now named **Theme** and writes `skin_id` / UI suite. Examples:
  mansion paper, GOSLO classic, Ner mochi room, pirate prototype.
- `scene_profile_id` stays in `RoomProfile` for backward compatibility and
  runtime policy, but the user should not manually pick desktop / indoor /
  outdoor there. That baseline should be selected by app/device/experience
  components.
- The broader canvas/menu layer may still expose a technical Scene block for
  SceneRegistry inspection, but the mobile startup RoomSetting must not reuse
  that block as a visual theme selector.

## 1. Terms

| Term | Product meaning | Persistence owner |
|:--|:--|:--|
| `Room` | User-facing saved App preset name. Example: "GOSLO Study Room". | `RoomProfile` |
| `RoomProfile` | Internal saved App profile. Stores selected model, persona, line, scene, and menu/default state references. | Room profile store |
| `livekit_room_id` | Transport/session room used by LiveKit. Not the App Room. | startup transport config |
| `Model` | Character/model controller selection, such as `GOSLO_default` or future `ner_skin2`. | model manifest registry |
| `Persona` | Character prompt/lore/speaking style selection. | persona loader / persona registry |
| `Maid Team` | Background AgentTeam preset for scheduled work, Nanobot/MCP capabilities, and report/task support. V1 defaults to `CatMaid Team`. | AgentTeam registry / orchestrator, pending core field |
| `Line` | Brain voice pipeline, currently `line_a` or `line_b`. | line registry + runtime readiness |
| `SceneProfile` / `scene_profile_id` | Internal launch baseline / SceneRegistry profile. It can affect AR/2D surface policy, but startup RoomSetting should not show it as a desktop/indoor/outdoor picker. | scene profile registry / app device policy |
| `Theme` / `skin_id` | User-visible skin and UI suite selection, e.g. mansion paper, Ner mochi room, pirate prototype. This is the startup RoomSetting visual selector formerly confused with `Scene`. | RoomProfile / skin or theme registry |
| `ExperienceMode` | Startup-page right-side start mode: AR companion, 2D hall/workspace, or room-only/light session. | startup draft / RoomProfile default |
| `BehaviorMode` | GOSLO behavior flags such as companion, butler, researcher, playful, roleplay. Not a startup RoomSetting selector. | runtime Brain/persona/menu |
| `CapabilityMode` | Existing app capability policy such as silent, voice-only, full AR companion. | session policy |
| `CanvasPreset` | Advanced node/canvas menu layout and connections. | canvas preset store |
| `MenuPreference` | HUD/tool drawer/settings toggles, positions, and UI choices. | menu preference store |

## 2. A-D Interface Discipline

### A. Source readback

Relevant source docs/code:

- `codex_workspace/design_workspace/unity_ar_app/startup_menu_design_v0_20260509.md`
- `codex_workspace/design_workspace/sketches/startup_menu_landscape_v0.html`
- `.cursor/memory/architecture/Interface/menu_design_complete_20260507.md`
- `.cursor/memory/architecture/Interface/app_v1_facade_core_business_interface_20260510.md`
- `src/parrot/brain/preset_loader.py`
- `src/parrot/brain/menu_registry.py`
- `unity/ArSpike/Assets/ParrotApp/Runtime/Scripts/Config/AppStartupConfigDto.cs`

### B. Existing core interfaces that can compose this flow

Current code already has a partial base:

- `PresetLoader` can load/save/apply a named preset and write active model/persona/mode/scene/workspace BB keys.
- `MenuRegistry` can list model/persona/mode/scene/workspace blocks and apply a selection.
- `WorkspaceRegistry` can switch App 2D workspace without tearing down LiveKit.
- `AppStartupConfigDto` already carries model/persona/scene/pattern/capability/workspace/transport fields.
- `SessionPolicy` can derive silent/voice/full-AR capability behavior.

These are enough for the first RoomSetting draft, but not enough for saved RoomProfile product behavior.

### C. Missing business surfaces

Needed before implementation is complete:

1. A `RoomProfile` schema that supersets the current `Preset` without breaking `data/presets/default.json`.
2. A RoomSetting facade for list/new/save/preview/apply.
3. A capability compatibility resolver shared by startup UI, runtime menu, Brain tools, and Unity action buttons.
4. A model registry that lists all selectable models from manifests instead of hard-coding `GOSLO_default`.
5. A line registry/status contract for LineA/LineB readiness.
6. A scene profile registry that owns mansion map, skin/theme, launch surface, and allowed ExperienceModes.
7. Persistent stores for runtime menu preferences and canvas presets.

### D. Success signals

RoomSetting is complete when:

- Startup `ROOM` opens a RoomSetting page with Room select/new/save and six selectors: Model, Room, Persona, Line, Theme, Maid Team.
- Selecting a saved Room populates those selectors and the startup model/scene preview.
- Changing a selector recomputes compatibility before START.
- START applies the effective profile, connects with the chosen Line, and enters the chosen Scene/ExperienceMode.
- Disabled or degraded capabilities are visible in menus and enforced by backend/Unity actions.
- A saved Room survives app restart and can be reselected.

## 3. RoomProfile Schema

MVP should extend the existing preset file path for compatibility:

- Current path: `data/presets/<id>.json`
- Product name: Room
- Internal object: `RoomProfile`
- Schema: v3 superset of current `Preset` v2

Candidate schema:

```json
{
  "schema_version": 3,
  "kind": "room_profile",
  "room_profile_id": "goslo_default_room",
  "display_name": "GOSLO Study Room",
  "model_id": "GOSLO_default",
  "persona_id": "goslo_parrot_default",
  "maid_team_id": "catmaid_team_default",
  "line_id": "line_a",
  "scene_profile_id": "ar_mansion_default",
  "experience_mode": "ar_companion",
  "workspace_id": "mansion_hub",
  "map_id": "mansion_hub",
  "skin_id": "goslo_default",
  "setting_file_refs": [],
  "livekit_room_id": "parrot-main",
  "canvas_preset_id": "default_canvas",
  "menu_preference_id": "default_menu",
  "behavior_mode_defaults": ["BASE", "COMPANION"],
  "metadata": {
    "created_from": "startup_room_setting",
    "notes": ""
  }
}
```

Compatibility rule:

- v2 `Preset` files remain readable.
- v2 `active_model_id`, `active_persona_id`, `active_scene_id`, `active_workspace_id`, and `active_mode` map into v3 fields.
- v3 should not make `BehaviorMode` a startup selector. If a v2 preset has `active_mode`, it maps to `behavior_mode_defaults`, a runtime behavior default, not to a startup `Mode` field.

## 4. Startup RoomSetting Contract

Startup RoomSetting operates on a local `RoomProfileDraft` until the user starts or saves.

| User action | Expected behavior |
|:--|:--|
| Open `SCENE` | Load RoomSetting snapshot: Room list, active draft, registries, compatibility report. |
| Select Room | Replace draft with saved RoomProfile and recompute compatibility. |
| New Room | Clone default values into an unsaved draft with a new display name. |
| Save Room | Persist current draft as RoomProfile. |
| Change Model | Update draft model, recompute capability compatibility, update model preview. |
| Change Persona | Update draft persona, recompute line/model/persona requirements. |
| Change Maid Team | Update draft background AgentTeam/Maid Team preset; V1 exposes fixed `CatMaid Team` until the shared core field and registry are implemented. |
| Change Line | Update draft voice pipeline, recompute ASR/TTS/ADC/voiceprint/echo readiness. |
| Change Theme | Update draft `skin_id` / UI suite. It may update compatible map/workspace defaults later, but must not ask the user to classify desktop/indoor/outdoor environment. |
| START | Apply draft/effective RoomProfile and run startup flow. |

No LiveKit connection is required while editing the draft.

## 5. Menu Persistence Boundary

RoomProfile is not the only persisted menu object. Every menu surface needs a persistence owner.

| Surface | Store | Saves |
|:--|:--|:--|
| Startup RoomSetting | `RoomProfile` | Model, Room, Persona, Line, Theme/skin, Maid Team, default ExperienceMode, map/workspace refs. |
| Startup quick lever | startup draft / RoomProfile default | Last chosen `ExperienceMode`. |
| HUD | `MenuPreference` | Corner, collapsed/expanded state, density, visibility. |
| Tool drawer | `MenuPreference` | Tool order, pinning, collapsed/expanded state, disabled-item visibility. |
| Runtime settings menu | `MenuPreference` + domain stores | Device/audio/camera/UI toggles. |
| Canvas menu | `CanvasPreset` | Node positions, connections, advanced module graph, layout. |
| 2D workspace | workspace state store | Last room/hub/desk selection and local UI state. |
| Behavior/persona runtime | Brain/persona store | BehaviorMode and roleplay/runtime persona overrides. |

Runtime menu changes can either:

1. Update the active session only.
2. Save into the current RoomProfile.
3. Save into a named menu/canvas preset referenced by the RoomProfile.

The UI must make this difference visible. Silent persistence is not allowed for advanced choices.

## 6. Mode Naming Rule

Do not use a bare field named `Mode` in new RoomSetting docs or DTOs.

Use one of these explicit names:

- `experience_mode`: startup surface, e.g. `ar_companion`, `2d_hall`, `room_only`.
- `behavior_mode`: GOSLO behavior, e.g. companion/butler/researcher/playful/roleplay.
- `capability_mode`: app capability policy, e.g. silent/voice/full AR.
- `dsg_mode`: internal perception/DSG filter mode.
- `line_id`: Brain pipeline, e.g. `line_a`, `line_b`.

The startup page can still show a user-facing "Mode" lever if the visual design needs it, but the data field must be `experience_mode`.

## 7. Capability Compatibility Resolver

RoomProfile selection is not just preference loading. It must compute the effective capabilities produced by the selected Model, Line, Scene, Persona, permissions, and device readiness.

The mature pattern to use is a capability/feature resolver:

1. Each selectable item declares what it provides.
2. Each menu/action declares what it requires.
3. The resolver computes enabled, degraded, disabled, and blocked states.
4. UI and backend actions consume the same result.

Recommended data shape:

```json
{
  "capability_id": "parrot.fly_to_hand",
  "state": "disabled",
  "reason": "selected_model_missing_capability",
  "source": "model:ner_skin2",
  "fallback_action": "show_model_idle_animation"
}
```

State meanings:

| State | UI behavior | Backend behavior |
|:--|:--|:--|
| `enabled` | Show normally. | Tool/action can run. |
| `degraded` | Show with warning/badge and fallback text. | Use fallback path. |
| `disabled` | Grey out or hide behind "show unavailable". | Tool/action is not registered or returns rejected. |
| `blocked` | Prevent START or require user confirmation. | Do not apply profile. |

Defense-in-depth rule:

- UI gating is not enough.
- Brain tool registration, facade actions, and Unity controllers must also enforce the same capability decision.

## 8. Conflict Examples

| Selection conflict | Resolution |
|:--|:--|
| Custom model has no flight/perch capability. | Disable `fly_to_hand`; Brain should not expose/register `fly_to` for that model, or must reject with a capability reason. |
| Ner supports Spine animations but not AR perch-on-hand. | Keep animation menu enabled; disable perch/fly actions; allow 2D hall and AR idle placement if scene supports it. |
| LineB selected but Google ADC/STT/TTS is not ready. | Mark LineB as degraded or blocked depending on selected ExperienceMode; show ASR/TTS/ADC readiness in the menu. |
| 2D hall ExperienceMode selected. | Disable AR plane placement and AR camera-only tools; keep mansion hub/workdesk/photo/report/calendar tools. |
| Persona requires voiceprint/speaker awareness but selected Line cannot provide it. | Show persona warning; either allow with degraded speaker state or block if persona marks it as required. |
| Scene skin requires assets that are not imported. | Keep Room saved, but block START for that Scene/Skin until assets resolve or switch to default skin. |

## 9. Facade/RPC Surface To Add

Suggested Brain facade:

| Method | Purpose |
|:--|:--|
| `room_setting_snapshot()` | Read Room list, active draft, selectable registries, compatibility report. |
| `list_room_profiles()` | List saved user-facing Rooms. |
| `load_room_profile(room_profile_id)` | Load one RoomProfile into a draft. |
| `new_room_profile(base_id=None)` | Create an unsaved draft from default or an existing Room. |
| `preview_room_profile(draft)` | Return compatibility/effective profile without applying. |
| `save_room_profile(draft)` | Persist draft. |
| `apply_room_profile(draft_or_id, experience_mode=None)` | Apply active profile and return startup config/effective capabilities. |

Suggested Unity/transport method names:

- `getRoomSettingSnapshot`
- `previewRoomProfile`
- `newRoomProfile`
- `saveRoomProfile`
- `applyRoomProfile`

The first implementation may call local fixture data from Unity while the Brain facade lands, but the DTO names should match this contract.

## 10. Blackboard And Active Keys

Existing keys to keep:

- `global/active_model_id`
- `global/active_persona_id`
- `global/active_scene_id`
- `global/active_workspace_id`
- `session/app_capability_mode`

Needed keys or facade-owned fields:

- `global/active_room_profile_id`
- `global/active_line_id`
- `global/active_experience_mode`
- `global/active_scene_skin_id`
- `session/line_readiness`
- `session/room_profile_compatibility`

Do not write these from multiple places. RoomProfile apply should be the single writer for global active Room/Profile keys. Session runtime supervisors may write readiness and degraded state keys.

## 11. Implementation Order

1. Done partial: add the RoomProfile schema while keeping current `Preset` v2 compatibility.
2. Done partial: add `room_setting_snapshot()` and registry output via `RoomSettingService`.
3. Done partial: add compatibility resolver with model/action, line/readiness, scene/workspace, and experience gates.
4. Pending: wire startup `SCENE` page to draft/select/new/save.
5. Backend partial / UI pending: wire START to `apply_room_profile`.
6. Pending: move runtime HUD/tool drawer/canvas preferences into explicit stores.
7. LineB partial / Ner pending: LineB readiness now feeds the resolver; Ner model manifest/controller still pending.

## 12. Tests

Minimum tests:

- Loading v2 preset produces a valid RoomProfile draft.
- Saving a RoomProfile round-trips all five startup axes.
- Changing model recomputes capability gates.
- A model without `parrot.fly_to_hand` disables the fly-to-hand menu and backend action.
- LineB without ADC/STT/TTS readiness produces degraded or blocked compatibility.
- 2D hall ExperienceMode disables AR placement and keeps 2D workspace enabled.
- START applies the effective profile and writes active BB keys once.

