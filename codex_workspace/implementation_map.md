# Implementation Map

## Repo Roles

| Path | Role |
|:--|:--|
| `src/parrot/` | Python backend: Brain, Bus, Scheduler, DSG, Memory, shared contracts. |
| `unity/ArSpike/` | Current Unity AR App implementation workspace. |
| `unity/ParrotDev/` | Frozen older test bed and regression reference. Do not build new app features here. |
| `../nanobot/` | Forked Nanobot source and config templates. |
| `.cursor/memory/` | Historical SSOT, protocols, design docs, and route map. |
| `codex_workspace/` | Codex operational workspace and route index. |

## Unity Status

`unity/ArSpike/Assets/Scripts/ParrotApp/` already contains strong infrastructure:

- `Lifecycle/` app state, shutdown service, room lifecycle bridge;
- `Health/` connection health aggregation;
- `Ecp/` heartbeat, state DTOs, DataChannel transport;
- `LiveKit/` room, microphone, AR video, video tier, audio route;
- `RPC/` ECP DTOs and parrot RPC handler;
- `Parrot/` model manifest, registry, controller abstraction;
- `Photo/` photo controller;
- `Attention/` focus and bounding box controllers.

Missing front-end layer:

- boot/loading scene flow;
- HUD view;
- tool cabinet view;
- menu canvas view;
- notification paper-note view;
- 2D workspace shell;
- asset folder conventions and scene wiring.

## Backend Status

Backend has broad capability but business interfaces are not fully productized.

Useful existing anchors:

- `src/parrot/shared/constants.py` for channels/topics;
- `src/parrot/shared/ecp.py` and `bb_schema.py` for shared contracts;
- `src/parrot/brain/tools/` for Brain-callable actions;
- `src/parrot/scheduler/service.py` for Nanobot task routing and result forwarding;
- `src/parrot/brain/photo_upload_server.py` for photo assets;
- `src/parrot/dsg/l1_5/` and `src/parrot/dsg/l2b/` for graph/ref/bucket concepts.

Known gaps:

- Plan execution result routing still has TODOs in scheduler service.
- Nanobot heartbeat writer and Google Calendar business mapping need concrete implementation.
- Web console read surfaces should be a thin BFF, not a new protocol layer.

## Suggested Code Landing

### Unity UI

Create new scripts under:

- `unity/ArSpike/Assets/Scripts/ParrotApp/UI/Boot/`
- `unity/ArSpike/Assets/Scripts/ParrotApp/UI/Hud/`
- `unity/ArSpike/Assets/Scripts/ParrotApp/UI/Tools/`
- `unity/ArSpike/Assets/Scripts/ParrotApp/UI/Workspace/`
- `unity/ArSpike/Assets/Scripts/ParrotApp/UI/Notifications/`

Assets:

- `unity/ArSpike/Assets/UI/Boot/`
- `unity/ArSpike/Assets/UI/Hud/`
- `unity/ArSpike/Assets/UI/ToolCabinet/`
- `unity/ArSpike/Assets/UI/Workspace/`
- `unity/ArSpike/Assets/UI/Notifications/`
- `unity/ArSpike/Assets/UI/Skins/Pirate/`
- `unity/ArSpike/Assets/UI/Placeholders/`

### Web Console

Suggested split:

- `src/parrot/web_console/` for FastAPI BFF/read adapters.
- `web/console/` for front-end app.

Start read-only. Use existing Python APIs. If an adapter cannot read data without new core API, document that as a business-interface gap before adding mutation or protocol fields.

Web console now owns the dense operational route for L1.5/L2-B, node/photo
management, Blackboard, IntentWorkspace, Plan, Scheduler/Nanobot monitoring,
and future AgentTeam/MCP admin. Unity App owns the mobile/game-facing rendering
of the same core state.

### Nanobot / Business IO

Keep Nanobot-specific business mapping thin and testable:

- Google event raw payload -> normalized calendar node DTO;
- normalized calendar node -> Nanobot command payload for create/update/delete;
- Nanobot result -> app report card payload;
- heartbeat writer -> Redis key already expected by scheduler/DSG.

AgentTeam/Maid Team is a Parrot control-plane layer above nanobot instances.
`CatMaid Team` V1 should stay one nanobot instance until the default path is
observable; multi-instance routing needs an approved core `agent_team_id`
addition before implementation.

## First Milestone Proposal

Milestone A: App Shell

- Unity boot scene loads into AR scene.
- HUD shows lifecycle, connection, video, audio, time.
- Tool cabinet opens and contains placeholder buttons.
- Photo and focus box buttons call existing controllers where possible.
- Notification note can be spawned from a local test button.

Milestone B: Business Loop

- Nanobot result can become a note/report in Unity.
- 2D workspace can open and show one report document.
- Web console can show module health and current menu selections.

Milestone C: Design Loop

- Figma placeholders replaced by exported sprites.
- Theme folders and naming rules are stable.
- Scene wiring is repeatable from README.
