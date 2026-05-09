# Codex Workspace Index

> Created: 2026-05-09
> Scope: Clean Codex-facing workspace for finishing the GOSLOParrot app layer on top of the existing ParrotCarriers backend.

This folder is intentionally separate from `.cursor/memory/`. Cursor's memory remains the historical SSOT and protocol archive; this workspace is the operational entry point for Codex work on Unity AR App, 2D workspace, Web console, Figma/Unity assets, and business interfaces.

## Start Here

Read these in order for a new Codex session:

1. `product_brief.md` — project summary, user intent, and app goals.
2. `implementation_map.md` — what exists, what is missing, and where code should land.
3. `workflows.md` — how Codex should work in this repo, including plugin and handoff rules.
4. `interface_plan.md` — business interface slices we need before app UI feels complete.
5. `design_workspace/INDEX.md` — user-facing design workspace for original wording, sketches, Figma/Unity assets, and App/Web flow planning.

Then load only the relevant skill route:

| Task | Route |
|:--|:--|
| Unity AR app startup, HUD, tool cabinet, runtime UI, scene wiring | `skills/unity_ar_app.md` |
| 2D report/calendar/ref workspace in app | `skills/app_2d_workspace.md` |
| Web console / visual debugger | `skills/web_console.md` |
| Figma export, Unity UI assets, placeholder sprites | `skills/figma_unity_assets.md` |
| Nanobot, Google Calendar, long task result loop | `skills/nanobot_business_io.md` |
| User design workspace, sketches, original wording, Figma/Unity asset planning | `design_workspace/INDEX.md` |

## Current Decision

Codex should treat `unity/ArSpike` as the app implementation workspace. `unity/ParrotDev` is a frozen comparison/test bed unless a task explicitly says otherwise.

The first practical milestone is not visual perfection. It is a shippable app loop:

1. Boot into AR.
2. Connect to LiveKit/Brain.
3. Show compact HUD state.
4. Open a 2D tool cabinet.
5. Trigger camera/focus/fly-to-hand/basic task actions.
6. Receive Nanobot/Brain feedback as paper-note style UI.
7. Open a 2D workspace to review reports/calendar/ref items.

## Source Anchors

Keep these as reference, not as a maze:

| Source | Why it matters |
|:--|:--|
| `.cursor/memory/architecture/user_ideas_and_backend_capability_brief_20260509.md` | Best compact source for user idea + backend abilities. |
| `.cursor/memory/architecture/ar_app_flow_ui_design.md` | App flow and UI baseline, including the original user wording. |
| `.cursor/memory/architecture/frontend_workspace_boundary.md` | Two hard rules for shared Cursor/Codex work. |
| `.cursor/memory/architecture/Interface/INDEX.md` | Interface discipline: core vs business, A-D template. |
| `.cursor/memory/architecture/app_completion_master_audit_20260507.md` | 8 scenario audit and pixel UI asset inventory. |
| `unity/ArSpike/Assets/Scripts/ParrotApp/MIGRATION.md` | Unity implementation status and ParrotDev vs ArSpike boundary. |
| `src/scripts/start_nanobot_worker.py` | Current Nanobot gateway setup path. |

## Hard Rules

- Do not edit `.cursor/memory/lore/ideas.md`; it is user-owned.
- If changing public protocol, DTO fields, enum values, or `src/parrot/**` public signatures, record the reason in the commit message or nearby code comment.
- If adding new `.cursor/memory/architecture/**` documents, update `.cursor/memory/INDEX.md`. This workspace avoids that by default.
- Prefer placeholders over blocking on final Figma/pixel art assets.
- Keep Web console read-only until the read surfaces are clear and stable.
