# GOSLO Startup Injection Map

Updated: 2026-05-17

This map covers the LiveKit startup path after Unity connects and before the placed Parrot/GOSLO model is ready to greet.

## Intended Startup Rule

LiveKit connected means transport is alive only. It is not the first social turn. GOSLO should stay quiet until Unity reports explicit AR placement through `onGosloPlaced`.

## Startup Sequence

| Step | Source | Injection channel | Content | Speaks? | Notes / risk |
| --- | --- | --- | --- | --- | --- |
| 1 | Unity `AppStartupFlowController` local config | App DTO / local state | Active room profile, persona id, scene id, model id, capability mode | No | Default capability mode is `FullARCompanion`, so mic/video may become live before placement unless startup changes the mode. |
| 2 | Brain `ParrotAssistant(instructions=get_instructions())` | P0 | Active persona plus session-context pack from `soul.py` / `session_context_pack.py` | No by itself | This is the base system prompt for the session. |
| 3 | Unity RPC `applyRoomProfile` | C2 via BB watchers | Room/persona/mode/scene/profile fields, then full instruction rebuild | No by itself | `global/active_*` keys trigger `Agent.update_instructions(...)`. RoomProfile may also bootstrap setting sources into L1.5. |
| 4 | Unity RPC `setAppCapabilityMode` | Policy BB write | `session/app_capability_mode` | No by itself | `SessionOnlySilent` suppresses `generate_reply`; other modes allow proactive C4. |
| 5 | PerceptionSupervisor | BB state / C3/C4 trigger source | `session/video_tier`, `session/dsg_mode` derived from capability mode and visual health | Usually no, but can | Runs 1 Hz. If video tier later upgrades to `VIDEO_FULL`, ContextInjector classifies that as heavy C4, so this is a pre-placement speech risk. |
| 6 | ContextInjector startup | C2 / C3 / C4 | BB diff notices, memory context refresh, scene context refresh | C3 no, C4 yes | First BB observation is baseline-skipped, but later changes can push status or speech. Memory refresh is C2 every 60s after startup. |
| 7 | ModeWatcher | C2 | Redis behavior mode changes rebuild active instructions | No by itself | Event-driven PubSub, not polling. |
| 8 | DSG trigger runner | L1.5 / C3 / Nanobot dispatch | Startup triggers, periodic triggers, event-driven trigger results | C3 no by default | Legacy `notify_gemini` now maps to C3 in TriggerRunner, but old `trigger_listener.py` still has a C4 path for `missing/new`. |
| 9 | Scheduler result listener | C4 | Nanobot / background task result summary | Yes | Event-driven. It can speak before placement unless session is `SessionOnlySilent` or a placement gate is added. |
| 10 | Unity RPC `onSceneReady` | Readiness marker only | Returns `greeting: deferred_until_goslo_placed` | No | This should never greet. Old docs that say otherwise are historical/stale. |
| 11 | Unity RPC `onGosloPlaced` | C4 | First greeting prompt with placement/time-of-day context | Yes | Current duplicate guard is process-local `greeting_state["sent"]`, not a cross-session Blackboard state. |

## Current Pre-Placement Speech Risk

The code suppresses greeting on `onSceneReady`, but it does not globally suppress all C4 before placement. These paths can still speak if they fire before `onGosloPlaced`:

- Scheduler / Nanobot result listener.
- ContextInjector heavy C4, especially visual tier recovery to `VIDEO_FULL`.
- Legacy DSG trigger listener for `missing` / `new`.
- User mic input if Unity publishes mic before placement in `FullARCompanion`.

## Recommended Policy Boundary

Add an explicit placement gate independent of capability mode:

- `session/goslo_placed = false` at LiveKit connect.
- `session/goslo_placed = true` only after `onGosloPlaced`.
- `session/first_greeting_sent` stored in Blackboard or session-scoped state with reset on room end.
- Before placement: C4 is queued or downgraded to C3 except hard safety messages.
- Nanobot/task results before placement: stage in IntentWorkspace and report after placement or when the user asks.

