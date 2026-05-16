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
| `startup_roomsetting_app_interface_20260513.md` | APP-001, APP-002, APP-003, APP-005, APP-013, APP-015, APP-016, APP-017 | active | Startup page, RoomSetting six-axis selector, START transition, LiveKit/LineB status, main-ready/homepage contract, Castle START repair, and legacy UI demotion notes. |
| `canvas_menu_ref_workspace_app_interface_20260513.md` | APP-004, APP-006 | active | Canvas menu, renderer-agnostic nodes/edges, App-side Ref workspace boundary, future Red String / Evidence Board constraints. |
| `unity_project_inventory_app_ssot_20260513.md` | APP-011 | active SSOT | Unity App formal directory, resource, scene, Build Settings, test evidence, and forbidden legacy path rules. |
| `unity_app_transport_interface_taxonomy_20260515.md` | APP-018 | active | Channel ownership for App HTTP, orchestrator HTTP, token mint, LiveKit media, DataChannel/ECP, RPC, Unity local state, SVA/video, and smoke evidence boundaries. |
| `unity_homepage_menu_livekit_audit_20260515.md` | APP-015, APP-018, APP-021, APP-022, APP-023, APP-024 | active | Formal homepage/menu readiness, menu save/load boundaries, Mint/config phone suitability, LiveKit lifecycle stability gaps, ECP protocol correction, and reference/test script guardrails. |
| `unity_livekit_ecp_sva_data_flow_map_20260515.md` | APP-015.19, APP-018, APP-022, APP-023, APP-024 | active map | Formal Unity App data-flow map across App HTTP, orchestrator, token mint, LiveKit media/RPC, ECP, SVA/video, Brain/DSG/GOSLO/Scheduler, Unity local state, and phone config rules. |
| `unity_audio_route_research_20260516.md` | APP-015.23, APP-023, APP-024 | active research guard | Formal Android phone audio-route research and implementation guard: LiveKit Unity lifecycle limits, Android communication-device routing, Bluetooth/SCO/A2DP distinction, audio focus, smoke-script pollution boundary, and preferred native route manager layering. |
| `app_evidence_tools_bbox_mag_photo_intent_workspace_20260515.md` | APP-005, APP-015.21, APP-015.27, APP-015.29, APP-022, APP-024, APP-026, WEB-015 | active handoff | App-facing readiness matrix and usage guide for CAM/Photo, BBox, MAG/Focus, time-aligned evidence, IntentWorkspace staging, GOSLO awareness boundaries, and the 2026-05-16 BBox/MAG production unblock implementation (`/api/app/visual-tool/event`, ECP `visual_tool.lifecycle`). |
| `formal_homepage_hud_menu_plan_20260515.md` | APP-015.20, APP-015.21, APP-015.25, APP-021, APP-022 | active plan | Formal homepage HUD/menu/model V1 implementation prep: reusable formal scripts/assets, reference-only Smoke/Ner boundaries, App HTTP/RPC/ECP responsibilities, first-slice TODO order, placement-owner status, and acceptance gates. |

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
