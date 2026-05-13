---
title: App V1 Model Capability Resolver Interface
date: 2026-05-11
status: partial-implementation
category: business-interface
owner: Codex / App V1
scope: Brain-side model manifest mirror, RoomSetting capability decisions, custom capability tool gating
code:
  - src/parrot/brain/model_manifest_registry.py
  - src/parrot/brain/menu_registry.py
  - src/parrot/brain/room_setting.py
  - src/parrot/brain/tools/_capability_gate.py
  - src/parrot/brain/tools/play_capability.py
  - src/parrot/brain/tools/fly_to.py
  - src/parrot/brain/tools/__init__.py
  - src/parrot/brain/agent.py
  - unity/ArSpike/Assets/ParrotApp/Runtime/Scripts/RPC/ParrotRpcHandler.cs
  - unity/ArSpike/Assets/ParrotApp/Runtime/Scripts/Parrot/ParrotController.cs
  - unity/ArSpike/Assets/ParrotApp/Resources/parrot_models/goslo_default.json
  - unity/ArSpike/Assets/ParrotApp/Resources/parrot_models/ner_skin2.json
tests:
  - tests/test_brain/test_menu_workspace.py
  - tests/test_brain/test_app_first_version_facade.py
  - tests/test_brain/test_tools_model_id.py
related:
  - goslo_model_manifest_protocol_v1.md
  - app_v1_lineb_ner_realdevice_config_report_20260511.md
---

# App V1 Model Capability Resolver Interface

## 0. Decision

Brain now has a small read-only `ModelManifestRegistry` that mirrors Unity
`Resources/parrot_models/*.json`. Unity still owns prefab/controller lifecycle;
Brain uses the mirror for menu status, RoomSetting compatibility, and LLM tool
gating.

## 1. Contract

- `ModelManifestRegistry.list_manifests()`
- `ModelManifestRegistry.get(model_id)`
- `ModelManifestRegistry.supports(model_id, capability_id)`
- `ModelManifestRegistry.capability_ids(model_id)`
- `ModelManifestRegistry.parrot_reflex_enabled(model_id)`

RoomSetting emits:

- `model.available`
- `model.reflex.parrot_reserved`
- `model.capability.<capability_id>`
- `parrot.fly_to_hand`

Brain tools:

- `animate` remains reserved for the 8 `ParrotAnimation` capability ids.
- `fly_to` checks the selected model declares `fly` before calling Unity.
- `play_capability` validates any custom capability id against the selected
  model manifest, then routes through the existing Unity `animate` RPC path.
- `play_capability` marks the Unity call as strict. Unity forwards
  `parameters_json` to the selected `IParrotController` and returns a failed
  ack reason `capability_unsupported:<id>` if the controller rejects it.
- `tools_for_active_model()` hides `fly_to` and reserved `animate` when the
  active model does not support parrot reserved capabilities.

## 2. Current Behavior

- `GOSLO_default` supports `fly`, `perch`, and the reserved parrot animation
  vocabulary. It receives `fly_to` and `animate`.
- `ner_skin2` supports custom Spine capabilities such as `face_happy`,
  `face_serious`, `face_sulky`, `touch_idle`, `pat_idle`, `tickle_idle`,
  `eat`, `smash_end`, `cheek_pinch_hold`, `cheek_pinch_release`, and
  `spine_walk`. Primary expression capabilities carry variant metadata for
  exact Spine clips. It does not receive `fly_to` or reserved `animate`.
- RoomSetting marks Ner `parrot.fly_to_hand` as disabled, not blocked, so the
  Room can still be used with Ner-specific capabilities.

## 3. Remaining Work

- Add richer self-check state for parameterized capabilities after Unity
  prefab/controller binding is complete.
- Expand persona/scene/device permission requirements into the same resolver.

