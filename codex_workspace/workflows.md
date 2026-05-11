# Codex Workflows

## Default Entry Workflow

1. Read `codex_workspace/INDEX.md`.
2. Read one skill route from `codex_workspace/skills/`.
3. Check `git status --short` in `ParrotCarriers`.
4. Inspect only the relevant code and docs.
5. Implement in the smallest app-facing slice that can be tested.
6. Run focused tests or Unity/editor checks when available.
7. Update this workspace only if the route itself changes.

## Cursor Docs Policy

Cursor docs are still valuable, but Codex should not follow every launch prompt literally. Use them as source anchors:

- product intent;
- protocol locks;
- existing backend capability;
- known gaps and TODO labels.

Avoid copying Cursor's chat-launch structure into new work. Codex tasks should end in runnable app code, concrete interface tables, or a small design artifact.

## Audit Log Awareness (2026-05-11)

Cursor 已经做完 3 轮接口审计（10 个 bug 全部修复 + 共性纪律总结），SSOT 在
`.cursor/memory/architecture/Interface/audit_log_index_20260511.md`。

**触发条件**：碰 RoomSetting / LineB / ECP / disconnect 路径前必读，避免重复
踩同型坑。源码里所有未尽事项都已加 `# TODO (audit Round X §Y)` 注释，grep
`audit Round` 可直接定位到行。

最重要的一条共性纪律：

> 任何在 `parrot/brain/**` 里声明的 module-level mutable state（`_dict` /
> `_list` / `_set` / `OrderedDict`）必须在同一 PR 里同时：
> 1. 添加 `reset_*_on_session_end()` 函数
> 2. 在 `agent.py::_on_room_disconnected` 完成 wire-up

## Plugin Setup Notes

Useful Codex-side plugins/connectors:

- Figma: design import/export, screen construction, asset handoff.
- Browser: local Web console inspection.
- GitHub: later PR/issue workflow if the repo is connected.

Potentially useful external/local tools:

- Unity Editor MCP or Unity-side automation plugin for scene and prefab wiring.
- Figma export pipeline for pixel UI sprites and reference PNGs.

If a plugin is not installed in Codex, keep the repo structure plugin-ready and continue with file-based placeholders.

## Design Workspace Workflow

Use `codex_workspace/design_workspace/` when the task is about user ideas, sketches, page/component planning, Figma/Unity assets, or App/Web flow design.

Suggested loop:

1. Keep user wording in `00_original_words/`.
2. Put App-first sketches in `unity_ar_app/` and `app_2d_workspace/`.
3. Keep Web console read-only and downstream of App flow until the App surfaces are clearer.
4. Use `backend_interface_map/` for business flows such as Obsidian, Google Calendar, PhotoNode, and Nanobot reports.
5. Update `tasks/ACTIVE_CONTEXT.md` after a real design decision or route change.

## Unity Workflow

Use `unity/ArSpike` as the implementation source.

Suggested loop:

1. Add scripts and prefabs under `ParrotApp`.
2. Keep runtime UI independent from backend availability by supporting local test payloads.
3. Wire real controllers behind interfaces or serialized fields.
4. Keep placeholder sprites simple.
5. Verify in Unity Editor when the Unity plugin/editor access is available.

## Web Workflow

Read-only first.

1. Define 4 read views: DSG, Ref, Module Status, Menu/Canvas.
2. Add BFF read adapters only for existing Python surfaces.
3. Build a compact developer UI, not a marketing page.
4. Use Browser plugin to inspect local UI after implementation.
5. Add writes only after the user confirms the read model feels right.

## Business Interface Workflow

Use the A-D discipline from `.cursor/memory/architecture/Interface/INDEX.md`, but write the result locally in the relevant task file or PR description:

- A: source docs, max three.
- B: can existing core interfaces compose this?
- C: if not, what core surface is missing?
- D: what input produces what observable result?

## Documentation Hygiene

Do not expand this workspace into another maze. Add a file only when it becomes a real operational route.

Good additions:

- a route for a new app surface;
- a short interface decision table;
- a runbook for a repeatable local test.

Bad additions:

- exhaustive API copies;
- old sprint archaeology;
- generic design speculation without implementation consequence.
