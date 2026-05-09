# Skill Route: App 2D Workspace

Use this route for in-app document/report/calendar/ref review surfaces.

## Read First

1. `codex_workspace/product_brief.md`
2. `codex_workspace/interface_plan.md`
3. `.cursor/memory/architecture/user_ideas_and_backend_capability_brief_20260509.md`
4. `.cursor/memory/architecture/app_completion_master_audit_20260507.md` section 6 for asset inventory

## Product Shape

The 2D workspace is a paper desk over a dimmed AR background. It handles:

- Nanobot reports;
- calendar items;
- feedback notes;
- future ref/table views.

## Implementation Bias

- Start with one reusable `WorkspaceDocument` data model.
- Render report/calendar/ref with different templates later.
- Support local fixture documents.
- Keep write actions as visible stubs until writeback routes exist.

## Completion Signal

A paper note can be expanded into a workspace document, then accepted, dismissed, or archived locally.
