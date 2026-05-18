# App/Web Parallel Workflow (2026-05-13)

Purpose: define how two parallel chats can work without pre-deciding their
TODO lists, implementation order, or product goals in this coordination chat.

This file is workflow only. The App chat and Web chat still decide their own
scope, TODO list, and implementation flow with the user inside their own chats.

## 1. Shared Files

| File | Role | Write rule |
|:--|:--|:--|
| `codex_workspace/design_workspace/tasks/ACTIVE_CONTEXT.md` | Shared current truth and route pointers. | Keep short. Update after route/status changes, not for detailed task tracking. |
| `codex_workspace/design_workspace/tasks/APP_WEB_PARALLEL_TODOLIST_20260513.md` | Coordinated high-level TODO board for both chats. | App chat edits App lane; Web chat edits Web lane; both may add cross-lane blockers. |
| `codex_workspace/design_workspace/backend_interface_map/app/` | Unity App business-interface notes and A-D slices. | App chat owns. Web chat reads only unless asked. |
| `codex_workspace/design_workspace/backend_interface_map/app/unity_project_inventory_app_ssot_20260513.md` | Unity App directory/resource/scene inventory SSOT. | App chat owns. Any Unity directory, resource, scene, or Build Settings change must update this file in the same turn when the inventory changes. |
| `codex_workspace/design_workspace/backend_interface_map/app/unity_livekit_ecp_sva_data_flow_map_20260515.md` | Unity App LiveKit/ECP/SVA data-flow SSOT for homepage prep. | App chat owns. Read before adding or moving App HTTP, Orchestrator, Mint, LiveKit media/RPC, ECP, SVA/video, Brain/DSG/GOSLO/Scheduler, or Unity local state responsibilities. |
| `codex_workspace/design_workspace/backend_interface_map/app/formal_homepage_hud_menu_plan_20260515.md` | Unity App formal homepage HUD/menu V1 implementation prep. | App chat owns. Read before implementing the formal home HUD/menu drawer, reusing AppV1 assets, or extracting reference ideas from Smoke/Ner tuning scripts. |
| `codex_workspace/design_workspace/backend_interface_map/app/local_laptop_castle_app_env_20260518.md` | Unity App local laptop Castle sandbox for iQOO / LiveKit latency and audio-route comparison. | App chat owns. Use this route only through `infra/laptop-castle.ps1`; switch Unity phone config only through `infra/switch-unity-app-config.ps1`; local secrets stay in gitignored `infra/laptop.env.local`, generated runtime stays under `codex_workspace/local_runtime/castle_laptop/`, and phone proof still belongs to APP-024. Web Console/Obsidian targets do not change just because Unity config changes. |
| `codex_workspace/design_workspace/backend_interface_map/web_console/web_console_environment_switch_prompt_20260518.md` | Web Console startup prompt for adding ECS/laptop environment selection, connection probes, and secret-safe target visibility. | Web chat owns. App chat may update only the App-side environment facts; Web implementation must keep BFF/server secrets out of the browser and must not modify Unity `parrot_config.json`. |
| `codex_workspace/design_workspace/backend_interface_map/web_console/` | Web Console business-interface notes and A-D slices. | Web chat owns. App chat reads only unless asked. |
| `codex_workspace/design_workspace/backend_interface_map/core_interface_candidate_queue_20260513.md` | Staging queue for proposed shared core interfaces. | Either chat may propose; App/Web dual confirmation is required before moving shared contracts to core SSOT. |
| `.cursor/memory/architecture/Interface/**` | Ratified core interface SSOT. | Update only after the required lane confirmation; include source/writer metadata. |

## 2. What Goes Where

`ACTIVE_CONTEXT.md` contains:

- current route status;
- pointers to the latest workflow/TODO/interface files;
- active branch/workstream notes when useful;
- cross-chat decisions that change where future work should start.

It must not contain:

- full TODO lists;
- detailed implementation plans;
- long per-feature analysis;
- copied API signatures.

`APP_WEB_PARALLEL_TODOLIST_20260513.md` contains:

- status legend;
- App lane tasks after the App chat decides them;
- Web lane tasks after the Web chat decides them;
- shared blockers and cross-lane requests;
- links to business-interface slices or core candidate rows.

It must not contain:

- code snippets;
- copied contracts;
- decisions that belong in the dedicated chat before the user has approved them.

Business-interface lane files contain:

- A-D business-interface records;
- lane-specific open questions;
- lane-specific read/write adapter notes;
- links to implementation PRs or local code paths after work begins.

Core-interface candidate queue contains:

- proposed shared fields/endpoints/DTOs/BB keys;
- source chat and business need;
- whether App, Web, or both consume it;
- confirmation status.

Ratified core interface docs contain:

- only lane-confirmed shared contracts;
- writer/source-chat metadata;
- App/Web confirmation metadata when both lanes consume the contract;
- exact consumer list;
- test/verification expectation when applicable.

## 3. TODO Statuses

Use these statuses in the shared board:

| Status | Meaning |
|:--|:--|
| `intake` | Mentioned or discovered, not yet scoped by the owning chat. |
| `proposed` | Owning chat proposed a task or flow; waiting for user decision. |
| `approved` | User agreed; ready for implementation planning in that chat. |
| `in_progress` | Owning chat is actively implementing or validating. |
| `blocked_core` | Needs a new shared core interface; add a row to the candidate queue. |
| `blocked_cross_lane` | Needs the other chat/lane to provide a decision, adapter, or status. |
| `done` | Implemented or documented with an observable verification signal. |
| `deferred` | Deliberately postponed; include a short reason. |

Do not mark work `approved` just because it appears in an old longline. It must
be approved in the active App or Web chat.

## 4. Two-Chat Loop

Each chat follows this loop:

1. Read `ACTIVE_CONTEXT.md`, this workflow, the App/Web route decision doc, and
   the relevant skill route.
   Unity App chats must also read
   `codex_workspace/design_workspace/backend_interface_map/app/unity_project_inventory_app_ssot_20260513.md`
   before planning or editing Unity scenes, scripts, resources, models, art, or
   Build Settings.
2. Inspect the relevant code/docs before proposing work.
3. Decide that chat's own goal, TODO list, and implementation order with the
   user inside that chat.
4. Write accepted tasks into the appropriate lane of the shared TODO board.
5. Write lane-specific business-interface notes under that lane's directory.
6. If a shared core interface is missing, add it to the candidate queue instead
   of editing core SSOT.
7. After App/Web dual confirmation, move the shared contract into
   `.cursor/memory/architecture/Interface/**` with writer/source metadata.
8. Update `ACTIVE_CONTEXT.md` only when a route/status pointer changes.
9. For Unity App directory, scene, resource, model, or Build Settings changes,
   update the Unity project inventory SSOT and App TODO status in the same
   turn.
10. For Unity START / LiveKit work, do not mark completion on Mint or room join
    alone. Completion needs Brain participant presence, successful business RPC
    payloads, DataChannel heartbeat, and main-ready gate ownership. The
    2026-05-13 blocker was ECS LineB Google STT ADC plus token-mint deployment
    of unnamed Brain dispatch for Unity identities; the 2026-05-14 Castle repair
    report says those server-side repairs are complete. After Castle `c0f1705`,
    the 2026-05-14 fast retry proved Brain participant join and post-join
    business-ok `applyRoomProfile` / `setAppCapabilityMode` with
    `ner_lineb_room`. The obsolete Brain RoomSetting read/write RPC surface
    has been removed from active backend code; RoomSetting cold-load/edit/save
    stays on App HTTP before LiveKit connects. The default LineA room profile
    still fails correctly against a running LineB Brain. User repaired public
    ECS routing on 2026-05-14: `8790` RoomSetting returns 2 rooms and `7890`
    orchestrator health is ok. Castle LiveKit key alignment is now fixed:
    mint-issued Unity tokens validate and LiveKit join succeeds. After the
    2026-05-15 ECS restart, the formal non-phone START probe passed
    RoomSetting snapshot/save/apply for `ner_lineb_room`, Tier 1 prewrite,
    Mint, LiveKit connect, Brain `agent-*` presence without manual dispatch,
    `applyRoomProfile` business-ok, `setAppCapabilityMode` business-ok, and
    `parrot.ecp.state` heartbeat publish. A fresh temporary room also spawned
    Brain without manual server dispatch. Mint currently exposes
    `agent_dispatch_requested` but not the newer active-dispatch diagnostic
    fields, so keep that as a deployment-diagnostics gap, not a START blocker.
    Do not count the startup hold screen as formal homepage completion.
    `FormalMainReadyGate`, `FormalHomeHudController`, `FormalHomeMenuLoader`,
    `FormalModelReadyReporter`, `FormalModelPlacementController`,
    `FormalArRuntimeBootstrap`, and `FormalArSessionBaselineReporter` now cover
    first-pass main-ready gates. The placement controller is the current
    `onGosloPlaced` owner, waits for `FormalMainReadyGate.IsReady`, tries AR
    plane raycast placement, loads the selected runtime visual from
    `Resources/Models/**` when available, and falls back to whitebox/manual
    preview placement only when that runtime asset cannot load.
    `FormalModelRemoteController` is the first local joystick owner after
    placement; it routes Ner to `spine_walk` and GOSLO to local walk handlers
    without Brain RPC or menu persistence.
    `FormalXrHandPerchController` is now mounted by runtime resolution as the
    formal local XRHand/perch owner, but it only enables `PerchOnHand` when
    main-ready, placed model, manifest `perch` support, and `AnimationDriver`
    gates pass. Because `com.unity.xr.hands` / `UNITY_XR_HANDS` is not enabled,
    this remains debug-only/package-missing until a real iQOO Neo9 build proves
    hand tracking.
    Formal Settings now also includes `MIC NEXT` / `MIC AUTO` local input
    preference controls. They update `MicrophonePublisher`'s Unity device-name
    preference and trigger a LiveKit mic republish when connected; they do not
    change RoomSetting or pretend to force the native Android audio route.
    `FormalHomeToolController` is the first CAM formal owner: camera delegates
    to `PhotoController` ECP-preview + HTTP-upload only when the phone config
    has a non-loopback upload endpoint. MAG/BBox are now deliberately deferred
    until after phone stability and the backend SVA/ECP visual-evidence
    contract update; the formal homepage must not emit Focus/BBox ECP yet. It
    must not use Brain RPC, `captureSnapshot`, `identify_object`, menu
    persistence, or Smoke UI.
    Current bug-fix checkpoint: main-ready self-reevaluates/degrades while
    waiting, menu payloads must contain real workspace/menu shell data, mobile
    AR baseline waits for `ARSessionState.SessionTracking`, and already-connected
    Tier1/LineB START uses graceful shutdown plus fresh reconnect. The accepted
    touch drawer, model animation expansion, and iQOO Neo9 evidence remain
    APP-015/APP-024 work.
    App HTTP selector follow-up: `GET /api/app/line-profiles` is reachable,
    `GET /api/app/personas` was added for selector-safe persona metadata, and
    app-monitor POST routes can be protected by `PARROT_APP_MONITOR_SECRET`
    plus Unity's ignored `appApiSecret`.
11. For Unity App transport choices, read
    `backend_interface_map/app/unity_app_transport_interface_taxonomy_20260515.md`.
    Durable load/save and large snapshots are App HTTP; Tier 1 runtime control
    is Orchestrator HTTP; Mint owns short-lived tokens and server-side Brain
    dispatch; LiveKit media owns audio/video; ECP is the broad embodied-control
    protocol plane (`EcpCommand`/`EcpAck`, `EcpState`, `EcpEvent`, lossy tick,
    command causality, snapshot/sighting/ref links); Brain RPC is a compact
    in-room request/response transport under that larger model. Do not design a
    formal homepage/menu from the startup hold screen or Smoke UI without the
    APP-018 responsibility audit.
    For channel-by-channel ownership and current gaps, also read
    `backend_interface_map/app/unity_livekit_ecp_sva_data_flow_map_20260515.md`.
    It marks APP-015.19 complete and records that formal Unity still lacks a
    `captureSnapshot` RPC handler even though Brain has an SVA snapshot caller.
    For the current homepage/menu and phone-stability handoff, also read
    `backend_interface_map/app/unity_homepage_menu_livekit_audit_20260515.md`:
    it records the 2026-05-15 audit that startup main-ready is not the final
    homepage, menu persistence/full snapshots belong to App HTTP, formal
    homepage workspace/camera/photo-awareness/XR-hand menu apply now also uses
    App HTTP, and phone stability still requires 2D pause policy, degraded HUD,
    ECP homepage consumers, and iQOO Neo9 evidence. MAG/BBox stay delayed until
    after that stability pass.
    Before building the first formal HUD/menu drawer, read
    `backend_interface_map/app/formal_homepage_hud_menu_plan_20260515.md`; it
    records reusable formal scripts/assets, reference-only Smoke/Ner boundaries,
    the first implementation TODO order, placement-owner status, and acceptance
    gates.

## 5. Skill Gate

Before writing or reviewing code that touches project-specific systems, use the
direct migrated Codex skill when available. The bridge is only a fallback and
index:

1. Direct Codex skills are installed under `C:\Users\Bin\.codex\skills\` for
   Graphiti/FalkorDB, DSG/rustworkx, py-trees, Scheduler, Nanobot, LiveKit,
   AR Foundation, SVA vision, and ECS deployment.
2. If a direct skill does not trigger or the chat needs route help, read
   `codex_workspace/codex_skills/parrot-cursor-skill-bridge/SKILL.md`.
3. Then read the matching `.cursor/skills/<skill-name>/SKILL.md` or bundled
   reference file only when the direct Codex skill points there.

This gate applies to Graphiti/FalkorDB, DSG L1.5/L2-B/rustworkx, py-trees,
Scheduler, Nanobot, LiveKit Unity, AR Foundation, SVA vision, and ECS bus
deployment work. Startup prompts should explicitly mention the relevant direct
skill names; do not rely only on automatic skill triggering.

## 6. Lane Ownership

Unity App chat owns:

- startup page and RoomSetting rendering;
- App HUD, menu canvas, tool cabinet, game/model interactions;
- App-side report/workspace entry;
- Unity business-interface notes under `backend_interface_map/app/`;
- App lane in the shared TODO board.

Web Console chat owns:

- Web console information architecture;
- ECS/module health, L1.5/L2-B, node/photo, Blackboard, IntentWorkspace, Plan,
  Scheduler, Nanobot, and chat observability;
- Web-only business/admin interface notes under `backend_interface_map/web_console/`;
- Web lane in the shared TODO board.

Shared core ownership:

- Candidate first: `core_interface_candidate_queue_20260513.md`.
- Ratified after App/Web dual confirmation: `.cursor/memory/architecture/Interface/**`.
- Do not implement core fields/endpoints/DTOs silently from either lane.

## 7. Core Interface Writer Metadata

Yes: ratified core-interface additions need writer/source metadata.

Use this minimum metadata in a new or updated core interface doc:

```yaml
source_chat: "unity-app" # or "web-console" / "coordination"
writer: "Codex"
confirmed_by:
  - "unity-app"
  - "web-console"
confirmed_at: "YYYY-MM-DD"
approved_by: "user" # optional; use when the user explicitly makes the final call
origin_business_doc: "codex_workspace/design_workspace/backend_interface_map/..."
consumers:
  - "Unity App"
  - "Web Console"
```

For table-row additions inside an existing doc, include the source in the nearby
change log if adding a per-row column would make the table noisy.

## 8. Doc Hygiene

- Prefer updating an existing lane/business file over creating a new document.
- Create a new file only when owner, scope, or lifecycle is genuinely different.
- Every new coordination or business-interface file needs a short header with
  owner, status, category/scope, updated date, and source pointers.
- If a document is superseded, add `superseded_by` or a clear top note and
  update the relevant index/pointer file.
- `ACTIVE_CONTEXT.md` remains a route pointer, not an archive or full TODO.
- The shared TODO board tracks active work; old ideas belong in lane business
  files or candidate queues, not scattered notes.

## 9. Conflict Rules

- If both chats need to edit the same core doc, pause and route through the
  candidate queue first.
- If both chats need the same code module, the first chat writes the smallest
  adapter and the second chat consumes it after merge or explicit handoff.
- Business docs may duplicate user intent summaries, but not core API contracts.
- The shared TODO board is coordination state, not a contract. Core contracts
  live only in `.cursor/memory/architecture/Interface/**` after lane
  confirmation.
