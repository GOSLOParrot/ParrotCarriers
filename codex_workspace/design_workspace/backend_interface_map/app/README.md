# Unity App Business Interfaces

This directory is owned by the Unity App chat.

Use it for App-facing business-interface notes: startup RoomSetting, HUD,
menu canvas, tool cabinet, game/model interactions, reports, and App-side
workspace entry.

## Write Rules

- Use the A-D discipline from `../business_interface_workflow.md`.
- Keep App business flows here, not in Web console docs.
- If a flow needs a shared field, endpoint, DTO, topic, or BB key, add a row to
  `../core_interface_candidate_queue_20260513.md` instead of editing core SSOT.
- Update `../../tasks/APP_WEB_PARALLEL_TODOLIST_20260513.md` for lane status.
- Read `unity_project_inventory_app_ssot_20260513.md` before touching Unity
  directories, scenes, resources, models, art, or Build Settings. Update it in
  the same turn when Unity inventory changes.
- Prefer module-level interface files. Do not create one document per small
  implementation step. If a long task needs temporary notes, keep the durable
  decisions in the module-level file and use a temporary archive only when the
  owner/scope/lifecycle is genuinely different.

## Module Interface Index

| Module file | Related TODO | Status | Scope |
|:--|:--|:--|:--|
| `startup_roomsetting_app_interface_20260513.md` | APP-001, APP-002, APP-003, APP-005, APP-013, APP-015, APP-016 | active | Startup page, RoomSetting six-axis selector, START transition, LiveKit/LineB status, main-ready/homepage contract, and legacy UI demotion notes. |
| `canvas_menu_ref_workspace_app_interface_20260513.md` | APP-004, APP-006 | active | Canvas menu, renderer-agnostic nodes/edges, App-side Ref workspace boundary, future Red String / Evidence Board constraints. |
| `unity_project_inventory_app_ssot_20260513.md` | APP-011 | active SSOT | Unity App formal directory, resource, scene, Build Settings, test evidence, and forbidden legacy path rules. |

## Suggested Slice Header

```md
## Slice: <name>

Owner chat: Unity App
Status: intake | proposed | approved | in_progress | blocked_core | done
Related TODO: APP-###

### A. Source Readback

### B. Existing Core Interfaces

### C. Missing Core Surface

### D. Observable Completion Signal
```
