# Ner Mochi Scene V0

Status: config draft for App V1 LineB and RoomSetting validation.

This scene setting is referenced by `data/presets/ner_lineb_room.json` through
`skin_id = ner_mochi_room_v0`. It is a launch profile draft, not a completed
Unity scene.

## Purpose

- Verify startup RoomSetting can switch Model, Room, Persona, Line, and Scene.
- Verify LineB ASR/TTS with a Ner-themed model and persona.
- Keep `ParrotSmokeScene` as test evidence only; this profile should feed the
  formal App startup path when the App scene lands.

## Scene Defaults

| Field | Value |
|:--|:--|
| `scene_profile_id` | `ar_handheld` |
| `experience_mode` | `ar_companion` |
| `workspace_id` | `mansion_hub` |
| `map_id` | `mansion_hub` |
| `skin_id` | `ner_mochi_room_v0` |
| `model_id` | `ner_skin2` |
| `persona_id` | `ner_companion` |
| `line_id` | `line_b` |

## Placement Behavior

1. LiveKit may connect during the IPoAC transition page.
2. Connection success must stay silent.
3. The App waits for AR plane readiness.
4. The user places Ner/GOSLO.
5. Only after placement may the persona greet or run a wake/question action.

## Visual And Control Needs

Required for first real-device pass:

- Model preview slot can show `ner_skin2`.
- Runtime menu can switch expression capabilities:
  - `face_happy`
  - `face_angry`
  - `face_sad`
  - `face_shame`
  - `face_surprise`
  - `face_panic`
- Touch/pat/tickle action buttons can call:
  - `touch_idle`
  - `pat_idle`
  - `tickle_idle`
- Joystick movement should route to `spine_walk` or a future model-control
  interface. The current GOSLO joystick path still targets `ParrotController`
  and `AnimationDriver`, so Ner joystick support is not fully wired yet.
- Face customization is not implemented. Treat it as a future `appearance`
  menu, separate from expression switching.

## Capability Rules

- `fly_to_hand` is disabled for `ner_skin2` because the manifest does not
  declare `fly` or `perch`.
- Expression and touch capabilities may be enabled after the Spine prefab and
  controller are verified in Unity.
- LineB must show ASR/TTS/ADC/VAD/echo/voiceprint readiness before START.
