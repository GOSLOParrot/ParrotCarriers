---
title: App V1 Brain Cold-Start Line And Lifecycle Audit
date: 2026-05-11
status: implemented / needs-external-supervisor
category: business-interface
owner: Codex / App V1
scope: RoomSetting Line selector, Brain cold-start semantics, room-scoped background task cleanup
code:
  - src/parrot/brain/room_setting.py
  - src/parrot/brain/agent.py
  - src/parrot/brain/photo_upload_server.py
  - src/parrot/dsg/trigger_listener.py
  - tests/test_brain/test_app_first_version_facade.py
  - tests/test_brain/test_brain_lifecycle_static.py
related:
  - app_v1_room_setting_room_profile_interface_20260510.md
  - app_v1_lineb_ner_realdevice_config_report_20260511.md
  - app_v1_session_context_pack_upgrade_20260511.md
---

# App V1 Brain Cold-Start Line And Lifecycle Audit

## Verdict

Startup RoomSetting can select `Line`, and the backend interface exists:

- `RoomProfile.line_id`
- `RoomProfile.line_profile_id`
- `RoomSettingService.snapshot().selectors.lines`
- `RoomSettingService.snapshot().selectors.line_profiles`
- Facade/Web/RPC paths for RoomProfile and LineProfile preview/save/apply

But Line selection is **cold-start only**. `LineA` vs `LineB` is chosen when
`brain.agent` builds its `AgentSession` from `PARROT_LLM_PIPELINE`. Changing
`global/active_line_id` after the room is live can update menus and Blackboard
state, but it cannot replace the already-created LiveKit/Gemini session.

## Fixes

### 1. RoomSetting Now Exposes Cold-Start Policy

`selectors.lines[*].selection_policy` now includes:

- `scope: cold_start_only`
- `requires_brain_restart`
- `current_process_line_id`
- `env_key: PARROT_LLM_PIPELINE`

`RoomSettingService.compatibility()` adds `line.cold_start`:

- `enabled / process_line_matches_selected_line` when selected Line matches
  the running Brain process.
- `blocked / requires_brain_cold_restart` when the user tries to apply LineB
  while the Brain process is still LineA, or vice versa.

This prevents the dangerous "UI says LineB, Brain is still LineA" state.

`LineProfileLoader.apply()` is still allowed as a config/write path for saving
the intended next LineProfile, but its result now reports:

- `selection_scope: cold_start_only`
- `process_line_id`
- `requires_brain_restart`

So Web monitor / RemoteSSH tooling can distinguish "profile saved/applied to
BB" from "the current Brain session has actually switched pipelines".

### 2. Brain Room Job Background Tasks Are Tracked

`brain.agent` now keeps room-scoped background tasks in one list and cancels
them on LiveKit room disconnect:

- DSG trigger listener
- L2-B / TriggerRunner boot task
- Scheduler result listener

The Scheduler listener now unsubscribes/closes its Redis PubSub in `finally`.
The DSG trigger listener also closes PubSub on cancel.

### 3. Photo Upload Server Gets Cooperative Stop

`photo_upload_server.start_photo_upload_server()` now stores its uvicorn task
on the server object. `stop_photo_upload_server()` sets `server.should_exit`
and awaits the task briefly.

This matters for restart: without it, a stale in-process upload server can keep
port `7889` bound after the room disconnects.

## External Supervisor Boundary

This pass does **not** implement an OS-level Brain process supervisor. The repo
still relies on the launcher environment (tmux/systemd/Cursor RemoteSSH/manual
terminal) to start/stop the Brain process.

For true App startup Line switching, the external launcher must:

1. Read the selected RoomProfile.
2. Set `PARROT_LLM_PIPELINE` to `line_a` or `line_b`.
3. Set `PARROT_ACTIVE_LINE_PROFILE_ID` to the selected LineProfile.
4. Stop any old Brain process.
5. Start a fresh Brain process.
6. Only then let Unity connect / START proceed.

Until that supervisor exists, Unity can select Line and get a clear compatibility
error, but it cannot restart Brain by itself.

## Regression

```text
.\.venv\Scripts\python.exe -m pytest tests\test_brain\test_app_first_version_facade.py tests\test_brain\test_menu_workspace.py tests\test_brain\test_session_context_pack.py tests\test_brain\test_brain_lifecycle_static.py tests\test_unity\test_app_v1_meta_ui_static.py
71 passed

.\.venv\Scripts\python.exe -m py_compile src\parrot\brain\agent.py src\parrot\brain\room_setting.py src\parrot\brain\photo_upload_server.py src\parrot\dsg\trigger_listener.py src\parrot\brain\line_profile.py src\parrot\brain\line_status.py
passed
```

## Remaining Work

- Add an external Brain supervisor / RemoteSSH task that performs a cold restart
  from selected RoomProfile.
- Decide whether Unity START should call a local "restart requested" endpoint,
  or whether Cursor/ECS deployment owns restart outside the App.
- Render `selection_policy.requires_brain_restart` in RoomSetting UI so LineB
  is clearly shown as a startup-only selector.
