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
- `UI/AppV1SmokeReferenceUiController.cs` contains useful canvas/HUD interaction ideas,
  but it is a Smoke/reference controller. It must not become the shared canvas
  menu contract, and it must not be mounted wholesale into the formal startup
  scene as proof that the menu is complete.

## Slice: 2026-05-15 RPC / HTTP Menu Boundary

Owner chat: Unity App
Status: active rule
Related TODO: APP-004, APP-015

- LiveKit RPC is a compact control-plane surface, not a transport for full
  homepage/canvas snapshots.
- Older menu RPC wrappers (`listMenuBlocks`, `applyMenuSelection`,
  `applyPreset`, `saveAsPreset`) are removed from the active Brain room RPC
  registration. Formal menu loading and persistence stay on App HTTP.
- Current measured payloads from the cleanup audit: full RoomSetting snapshot
  is about 27.5 KB and full `canvas_snapshot` is about 39.3 KB, both too large
  for routine LiveKit RPC.
- Safe App RPC use today: small in-room control calls such as `applyWorkspace`,
  `setPhotoAwareness`, `setCameraMode`, `setXrHandMode`, tier/status
  confirmations, and START sync (`applyRoomProfile`, `setAppCapabilityMode`).
- Unsafe App RPC use today: full `canvas_snapshot`, persistent menu/preset
  saves, RoomSetting load/new/save/apply, selector lists, and larger read
  models. These belong to the App HTTP facade or a future paged HTTP read
  model.

## Slice: 2026-05-15 IntentWorkspace / L2-B Graph-Link Policy Intake

Owner chat: Unity App + Web Console coordination
Status: candidate policy, not App DTO
Related TODO: APP-006, APP-015.29
Core candidate: CORE-006, CORE-008, CORE-012, CORE-013

### A. Design Conclusion

The current best model is a canonical L2-B semantic graph plus overlays, not a
new `WorkspaceNodeKind` subclass and not "IntentWorkspace is an L1.5 bucket."

- `NodeKind` should answer what the thing is: object, person, event, photo,
  zone, etc.
- L1.5 should answer how an observation/ref is admitted, bucketed, refreshed,
  or rejected before L2-B.
- `IntentWorkspace` should hold rich/heavy working payloads, staged files,
  temporary plans, and refs that GOSLO may use.
- A workspace/subgraph view should answer how the App/Web renderer groups,
  isolates, or filters the graph.
- Attention/buff/lifecycle should be an overlay or metadata policy, not a
  taxonomy explosion in `NodeKind`.

### B. Policy Options To Preserve

Future backend policy should be able to choose per staged ref or source pack:

- `workspace_only`: keep the file/ref in IntentWorkspace without L2-B write.
- `index_pointer`: create a lightweight L2-B pointer Node with Ref binding.
- `isolated_compartment`: keep an L2-B compartment/subgraph separated until
  enough evidence exists.
- `promote_to_main_graph`: merge into the canonical L2-B graph.
- `connect_by_rule`: create/update edges through bounded graph rewrite rules.

The App renderer should show these choices as receipts/state, not as permanent
hard-coded renderer assumptions.

### C. Why Pool And Subgraph Feel Too Similar Today

The current rustworkx-backed L2-B implementation is still close to a graph
skeleton: if no rule creates edges, a bucket, source pack, or workspace view can
look like a disconnected subgraph. The missing capability is a reviewed graph
rewrite/link policy that can create, update, weaken, tombstone, or remove edges
from evidence while keeping audit receipts.

Candidate graph-link rules to review later:

- same Ref/source/file family;
- temporal co-occurrence;
- spatial proximity or shared room/scene;
- same L1.5 bucket/source pack;
- Graphiti entity/fact match;
- Obsidian setting membership;
- Calendar/person/time relation;
- BBox/Mag/Focus attention threshold;
- manual user-confirmed edge from App/Web board.

These rules should be bounded around affected nodes and use rustworkx as the
topology engine. High-frequency attention/decay should stay in node/edge
payload or overlay state instead of rewriting topology every tick.

2026-05-15 continuation:

- Pool/import UI should eventually let the operator choose whether a source
  pack or selected refs enter the main L2-B graph, stay workspace-only, become
  a pointer/index Node, or land in an isolated/foldable subgraph.
- Subgraph is a grouping/overlay decision first. A cluster or important-event
  collection can be wrapped visually and audited without changing the semantic
  `NodeKind` of its members.
- "Aggregate calendar subgraph with event subgraph" should start as a
  dry-run graph transform: compare selected subgraphs, draft candidate links,
  show why the policy thinks they relate, and let the user choose apply,
  discard, or send selected context to LLM for analysis.
- Any App-visible version should show receipts and reversible state. The heavy
  rule engine and rustworkx operations remain backend/Web policy until a shared
  App-safe subset is reviewed.
