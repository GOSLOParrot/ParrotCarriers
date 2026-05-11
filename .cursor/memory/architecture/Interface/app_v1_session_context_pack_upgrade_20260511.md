# App V1 Session Context Pack Upgrade

Date: 2026-05-11

## Status

Ner's setting sources are now usable by runtime, not only documented.

Implemented:

- `src/parrot/brain/session_context_pack.py`
  - resolves the active `RoomProfile.setting_file_refs`
  - keeps persona files under `PersonaLoader` only
  - classifies Markdown setting docs into LLM context and/or L1.5 payloads
  - keeps `.cursor` architecture/status reports as reference-only, not prompt context
  - treats `profile: roleplay` notes as UUID-free Obsidian setting sources
  - prepares `obsidian_setting_roleplay` payloads through the existing Obsidian ingest format
- `src/parrot/brain/soul.py`
  - appends the active Room's world/scene/action-manual context to system instructions
  - keeps persona selection as the first prompt layer
- `src/parrot/brain/agent.py`
  - refreshes instructions when Room/persona/mode/scene BB keys change
  - bootstraps active Room setting notes to L1.5 after TriggerRunner starts
- `src/parrot/brain/line_profile.py`
  - lets explicit `PARROT_LINE_PROFILE` / `PARROT_ACTIVE_LINE_PROFILE_ID` override stale Blackboard defaults

## Audit / Bugfix Pass

Reviewed after first implementation:

- Bug fixed: L1.5 bootstrap dedupe originally used only `room_profile_id + note_key`.
  - Risk: editing the same Room setting file during a dev session would not re-enter L1.5.
  - Fix: dedupe now includes `file_mtime`, so edited setting files can be bootstrapped again without restarting Brain.
- Bug fixed: `.cursor` architecture/status reports referenced by a RoomProfile are now `reference_only`.
  - Risk: completion/config reports could leak into the role/system prompt and make the character speak like a status report.
  - Fix: `.cursor` paths are visible in source metadata but excluded from LLM prompt context and L1.5 payloads.
- Bug fixed: `PARROT_ACTIVE_LINE_PROFILE_ID` now overrides stale Blackboard state.
  - Risk: RemoteSSH/RoomSetting could select `lineb_ner_ja_test` while an old BB value kept runtime on LineA.
  - Fix: explicit env selection wins over BB fallback.

Comments added in code:

- `session_context_pack.py`
  - why Room setting refs are resolved read-only
  - why persona files, LLM context, L1.5 setting sources, and audit reports are separated
  - why L1.5 dedupe includes file mtime
  - why setting source blocks are framed below the persona contract
- `soul.py`
  - why Room context is appended after persona instructions
- `agent.py`
  - why instruction refresh rebuilds the whole prompt instead of patching one block

## Current Ner Sources

- Persona:
  - `src/parrot/brain/personas/ner_companion.md`
- RoomProfile:
  - `data/presets/ner_lineb_room.json`
- UUID-free Obsidian roleplay setting source:
  - `codex_workspace/design_workspace/unity_ar_app/ner_roleplay_setting_obsidian_v0_20260511.md`
  - frontmatter uses `profile: roleplay` and `obsidian_note_key`
  - no `obsidian_uuid`
- Scene draft:
  - `codex_workspace/design_workspace/unity_ar_app/ner_mochi_scene_v0_20260511.md`

## Design Decision

Session startup now has three layers:

1. Persona prompt from `PersonaLoader`.
2. Room session context from selected setting files.
3. Dynamic memory/scene notices from `ContextInjector`.

Roleplay and daily Obsidian notes can also enter L1.5, but they still do not require UUID binding. Only `profile=ref` notes require UUID / target binding.

## Remaining Work

- External Obsidian vault sync is still a separate configuration/runtime task.
- The App frontend must expose which setting files are attached to the selected Room.
- Future RoomSetting editing should let the user add/remove setting docs and choose whether a source targets LLM, L1.5, or both.
- Runtime watcher bootstrap is in-process and best-effort. If a future multi-process RoomSetting editor saves files without applying the Room, it should explicitly call/apply a refresh path.

## Validation

- `pytest tests/test_brain/test_session_context_pack.py tests/test_brain/test_menu_workspace.py tests/test_brain/test_app_first_version_facade.py tests/test_brain/test_lineb_voiceprint.py tests/test_brain/test_lineb_model_reaction.py tests/test_unity/test_app_v1_meta_ui_static.py`
  - 68 passed
