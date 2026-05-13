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

## Slice: 2026-05-13 Startup Boundary Check

Owner chat: Unity App
Status: audited_only
Related TODO: APP-004, APP-006

### A. Source Readback

- This round intentionally keeps the canvas menu out of the implementation
  critical path. The active work is startup, RoomSetting cold-load, START,
  LiveKit connection stability, and clean main entry.
- Startup RoomSetting and canvas menu share selector concepts, but they do not
  share the same lifecycle. Startup writes the initial RoomProfile and Tier 1
  runtime config before LiveKit; canvas menu later applies in-session settings
  from a connected main UI.
- The startup page now labels the visual selector as `Theme` and writes
  `skin_id`. Canvas/menu may still expose a technical Scene block later for
  SceneRegistry or environment-baseline inspection, but that must not leak back
  into startup RoomSetting as a desktop/indoor/outdoor manual picker.

### B. Existing Core Interfaces

- Shared selector truth is already available through `RoomSettingService`,
  `MenuRegistry`, and `AppFirstVersionFacade.canvas_snapshot()`.
- The canvas menu should eventually consume typed menu/canvas DTOs from the
  shared boundary, not reuse the startup-only whitebox controller as its core.

### C. Missing Core Surface

No new row was added in this implementation round. CORE-007 remains the pending
shared answer for `CanvasMenuCoreV1`.

### D. Observable Completion Signal

- Startup code may show a `ROOM` entry and a small main placeholder, but it
  must not implement full canvas menu state.
- Any later canvas menu work should start from CORE-007 confirmation, then bind
  to existing facade/menu APIs instead of adding another local selector model.
- `UI/AppV1MetaUiController.cs` contains useful canvas/HUD interaction ideas,
  but it is a Smoke/reference controller. It must not become the shared canvas
  menu contract, and it must not be mounted wholesale into the formal startup
  scene as proof that the menu is complete.

## Slice: 2026-05-14 RPC Payload Budget

Owner chat: Unity App
Status: active rule
Related TODO: APP-004, APP-015

- LiveKit RPC is a compact control-plane surface, not a transport for full
  homepage/canvas snapshots.
- Current measured payloads: compact `getRoomSettingSnapshot` is about 8.3 KB,
  `listMenuBlocks` is about 4.5 KB, full RoomSetting snapshot is about 27.5 KB,
  and full `canvas_snapshot` is about 39.3 KB.
- Safe App menu RPC use today: small in-room control calls such as
  `applyMenuSelection`, `applyWorkspace`, and tier/status confirmations.
  `listMenuBlocks` can remain a compact legacy/bootstrap fallback, but the
  formal persisted menu/homepage read path should prefer the App HTTP facade
  or a future compact/paged HTTP read model.
- Unsafe App menu use today: sending full `canvas_snapshot` through LiveKit
  RPC. The formal homepage/menu loader must fetch that through the App HTTP
  facade or a future paged/compact read model.
- Static tests guard compact RoomSetting and menu block RPC payloads below
  15 KB. If a future registry grows past that, split the read model instead of
  raising the RPC budget casually.
