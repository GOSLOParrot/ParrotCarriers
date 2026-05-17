# Runtime Polling And Event Map

Updated: 2026-05-17

Question: does GOSLO frequently check Blackboard, Task status, and IntentWorkspace?

Short answer: Blackboard has several intentional lightweight polls. Task and Nanobot are mostly event-driven. IntentWorkspace is not continuously polled by GOSLO; it is read by tools, triggers, and diagnostic UI snapshots.

## Brain / Runtime Loops

| Component | Frequency | Reads | Writes / injection | Notes |
| --- | ---: | --- | --- | --- |
| `ContextInjector._bb_poll_loop` | 1 Hz after 2s settle | `session/visual_state`, `session/visual_reason`, `session/video_tier`, `session/dsg_mode`, `tick/last_rpc_ack`, `transient/photo_awareness_notice`, `transient/evidence_awareness_notice`; also calls `recompute_visual_state()` | C3 status notice, C4 speech for heavy changes, C2 on `VIDEO_OFF` boundary | First observation is baseline only. Per-key output is rate-limited to 3s. |
| `ContextInjector._periodic_memory_poll` | 60s after 5s settle | Graphiti recent memory search | C2 full instruction rebuild with memory context | Not a Blackboard scan. |
| `PerceptionSupervisor._control_loop` | 1 Hz after 2s settle | `session/visual_state`, `session/app_capability_mode`; A10 heartbeat every 10s | Writes `session/video_tier`, `session/dsg_mode`; may trigger ContextInjector on changes | The read/write is small but always on while Brain is live. |
| `ModeController._poll_loop` | 1 Hz | `session/dsg_mode` | No prompt injection | Caches DSG filter set so extractor hot path does not read BB per observation. |
| `ModeWatcher` | Event-driven | Redis hash once on init, then `CH_BEHAVIOR_MODE` PubSub | C2 full instruction rebuild | No periodic poll after init. |
| Session context watchers | Event-driven same-process callbacks | `global/active_persona_id`, `global/active_mode`, `global/active_scene_id`, `global/active_room_profile_id` after writes | C2 full instruction rebuild; RoomProfile change also bootstraps L1.5 | Triggered by `fire_watcher(...)` on BB write path. |
| DSG TriggerRunner periodic loop | 60s tick | Registered periodic triggers only | L1.5 ops, Plan ops, C3 notices, Nanobot dispatch | Separate from the legacy DSG PubSub listener. |
| DSG TriggerRunner event loop | Event-driven | `CH_DSG_EVENTS`, `CH_TRIGGER_RESULTS` | L1.5 ops, C3 notices, Nanobot dispatch | Does not poll. |
| Legacy DSG trigger listener | Event-driven | `CH_DSG_EVENTS`, `CH_DSG_SCENE_UPDATE` | C2 scene context or C4 notification for `missing/new` | This is a speech-risk path if still enabled. |

## Task / Nanobot

| Component | Frequency | Reads | Writes / injection | Notes |
| --- | ---: | --- | --- | --- |
| Scheduler command listener | Event-driven | `parrot.scheduler.commands` PubSub | Routes via py-trees and dispatches to Nanobot stream | Task dispatch updates `active_tasks` in-process. |
| Scheduler Nanobot result listener | Event-driven | `parrot.nanobot.results` PubSub | Updates `_pending_tasks`, Plan step result, trigger result stream, `parrot.scheduler.to_brain` | No polling for normal results. |
| Scheduler timeout checker | 15s | In-memory `_pending_tasks` | Timeout summary to Brain | Nanobot timeout is 120s. |
| Brain scheduler result listener | Event-driven | `parrot.scheduler.to_brain` PubSub | C4 `generate_reply(...)` | This is the main task-result speech path. |
| Web runtime monitor | On HTTP/SSE request | py-trees `active_tasks` | Read-only diagnostics | Visibility is current process only unless mirrored to Redis. |

## IntentWorkspace

| Component | Frequency | Reads | Writes / injection | Notes |
| --- | ---: | --- | --- | --- |
| IntentWorkspace core | None | `fetch`, `list_active`, `memory_pressure` only when called | Stage / evict refs | No background polling loop. |
| Triggers / observers / facade | Event or tool driven | Specific refs as needed | Stage photos, evidence, plans, calendar drafts, reports | Staging alone is L1.5/subconscious, not prompt injection. |
| `app_live_state` | On monitor HTTP poll | `list_active()` and `memory_pressure()` | Read-only | Diagnostic snapshot. |
| App monitor page | 1.2s only while page is open | Live-state endpoint | Read-only UI | This can look noisy in logs but is not GOSLO deciding to speak. |
| Web console SSE | Default 1s, bounded 0.25s to 30s | Runtime/memory snapshot builders | Read-only UI | Explicitly web-only and does not dispatch Scheduler or Nanobot tasks. |

## Current Conclusion

Blackboard reads are frequent but small and intentional: roughly three 1 Hz Brain-side loops can be active at once (`ContextInjector`, `PerceptionSupervisor`, `ModeController`). Task state is not frequently polled except the 15s timeout checker and diagnostic UI. IntentWorkspace is not continuously scanned by GOSLO; apparent frequent reads usually come from live monitor pages.

