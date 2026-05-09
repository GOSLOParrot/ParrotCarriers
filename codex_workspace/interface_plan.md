# Interface Plan

This is the Codex-facing business-interface backlog. It intentionally avoids copying core signatures.

## Business Slice 1: App Startup And Connection

Goal: Unity boots into AR, obtains/uses token config, joins LiveKit, and exposes state to HUD.

Existing core surfaces:

- Unity `RoomManager`;
- Unity `AppLifecycleManager`;
- Unity `ConnectionHealthAggregator`;
- token mint service in `src/parrot/castle/token_mint.py`;
- ECP heartbeat DTOs.

Need to decide:

- local dev token source vs production token mint source;
- what HUD state labels are enough for first version;
- what happens when Brain/LiveKit is unavailable.

Completion signal:

- Starting app reaches AR scene and HUD displays `connected/degraded/offline` without blocking local UI.

## Business Slice 2: Tool Cabinet Actions

Goal: Tool buttons call existing controllers or dispatch placeholder events.

Actions:

- photo;
- focus/attention box;
- fly to hand;
- settings;
- workspace open;
- model/persona/mode/scene menu.

Need to decide:

- which buttons call real controllers now;
- which produce local stub notes until backend business routes exist.

Completion signal:

- Each button has visible feedback and no silent dead-end.

## Business Slice 3: Nanobot Result To Paper Note

Goal: A Nanobot result becomes a paper-note notification and can be opened in the 2D workspace.

Existing core surfaces:

- Scheduler publishes Nanobot results to `CH_SCHEDULER_TO_BRAIN`;
- Nanobot gateway uses `parrot_bus`;
- Brain already listens to result channels in existing design.

Need to decide:

- minimal report payload for Unity UI: `id`, `title`, `summary`, `body`, `source`, `created_at`, `actions`;
- whether Brain pushes this as ECP event or Unity initially polls a BFF/debug endpoint.

Completion signal:

- A local or simulated Nanobot result spawns a note; opening it shows readable report content.

## Business Slice 4: Google Calendar Review

Goal: Calendar data can be shown as reviewable items before any risky writeback.

Existing core surfaces:

- Nanobot Google Workspace MCP config exists;
- `calendar_trigger.py` and `BucketKind.GOOGLE_CALENDAR` exist;
- IntentWorkspace direction exists.

Need to define:

- raw Google event -> normalized calendar item mapping;
- daily digest vs event detail payload;
- create/update/delete writeback command format;
- token budget policy: never dump full calendar into LLM context by default.

Completion signal:

- A sample raw Google event becomes a normalized item and can render in Web/2D workspace.

## Business Slice 5: Web Console Read Model

Goal: A local Web UI shows backend state without changing it.

Initial read views:

- module health;
- blackboard snapshot;
- menu registry / active model-persona-mode-scene;
- DSG buckets/ref table/graph summary.

Need to decide:

- BFF shape;
- read adapter availability;
- dev-only auth assumptions.

Completion signal:

- `web/console` shows live or fixture-backed state with clear empty/error states.
