# Canvas Menu And Ref Workspace App Interface (2026-05-13)

Owner: Unity App chat
Status: active
Category: App business interface
Scope: APP-004, APP-006
Sources:
- `.cursor/memory/architecture/Interface/app_web_parallel_routes_agent_team_20260513.md`
- `codex_workspace/design_workspace/backend_interface_map/core_interface_candidate_queue_20260513.md`
- `src/parrot/brain/menu_registry.py`
- `src/parrot/brain/app_first_version.py`
- `src/parrot/brain/refs.py`

This is the durable App business-interface document for the Unity canvas menu
and App-side Ref workspace boundary. Keep renderer decisions in Unity/App docs;
keep shared DTO and memory contracts in the core candidate queue and later
SSOT.

## Slice: Canvas Menu Boundary

Owner chat: Unity App
Status: active
Related TODO: APP-004

### A. Source Readback

- App/Web route decision says Unity renders a touch-first mobile/AR menu and must not import Web dashboard payloads.
- Existing backend menu truth is scattered across `MenuRegistry`, `PresetLoader`, `RoomSettingService`, `AppFirstVersionFacade.canvas_snapshot()`, and setting-tier docs.
- CORE-007 already stages a compact shared canvas/menu boundary request.

### B. Existing Core Interfaces

Partial yes.

Existing pieces:

- `MenuRegistry.list_blocks()` lists models, personas, behavior modes, scenes, and workspaces.
- `MenuRegistry.apply_selection()` applies a menu selection through `PresetLoader`.
- `AppFirstVersionFacade.canvas_snapshot()` gives a wider App shell read model.
- `RoomSettingService` handles startup-specific room profile selection and compatibility.
- `setting_change_tier` can explain whether a setting is local, reconnect, restart, or operator-only.

### C. Missing Core Surface

| Candidate | Landing module | SSOT needed | Unity DTO mirror | Notes |
|:--|:--|:--|:--|:--|
| CORE-007 `CanvasMenuCoreV1` | Brain facade / Unity / Web read adapters | yes | yes | Should unify read/apply/preset/canvas snapshot enough for App/Web while keeping rendering lane-specific. |

App-specific rule: Unity may render drawers, boards, sticky notes, node graphs,
or other touch-first metaphors, but those renderers must consume typed nodes,
edges, refs, actions, and tier metadata. The renderer name is not the shared
core contract.

### D. Observable Completion Signal

- Unity can render a canvas/menu from shared read models without duplicating Web admin state.
- Applying a menu selection goes through existing facade/registry paths.
- Tier/restart requirements are visible before applying risky actions.
- App canvas can add a renderer later without changing shared DTO names.

## Slice: App Ref Workspace Boundary

Owner chat: Unity App
Status: active
Related TODO: APP-006

### A. Source Readback

- App route wants future 2D workspace, Red String, and Evidence Board partial features.
- Graphiti/FalkorDB and DSG L2-B skills define memory graph and node organization boundaries; App should not write those stores directly.
- Existing Brain refs are session-scoped UI/reference links, not full memory surgery.

### B. Existing Core Interfaces

Partial yes.

Existing pieces:

- `src/parrot/brain/refs.py` tracks session refs for focus/BBox/photo-like UI artifacts.
- Photo/focus/BBox flows already create app-visible artifacts that can become ref endpoints.
- `AppFirstVersionFacade.canvas_snapshot()` can surface photo refs and tool-cabinet state.

Existing pieces do not yet define a shared add/remove/retarget API for refs
that span UI artifacts, documents, photos, Graphiti UUIDs, L2-B nodes, and
visual board edges.

### C. Missing Core Surface

| Candidate | Landing module | SSOT needed | Unity DTO mirror | Notes |
|:--|:--|:--|:--|:--|
| CORE-006 `MemoryRefBindingApi` | Brain refs / Memory / DSG / Unity / Web | yes | yes, limited App subset | Must support typed ref endpoints and typed visual edges without making Unity speak Graphiti/FalkorDB directly. |

App-side subset for V1 should be conservative:

- list refs/edges for the active workspace;
- attach a UI artifact to a known backend ref returned by Brain;
- detach or hide a visual edge;
- retarget a local board link only through a Brain-owned adapter.

App must not:

- issue raw Graphiti/FalkorDB queries;
- mutate L2-B node taxonomy;
- encode Red String or Evidence Board as the only renderer;
- expose Web-only memory-surgery controls.

### D. Observable Completion Signal

- App can show refs and edges as board artifacts while the core API stays renderer-agnostic.
- Missing memory backend shows a clear unavailable/degraded state, not a fake graph.
- Any App attach/detach action has an observable Brain-owned result and does not bypass shared core confirmation.
