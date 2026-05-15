---
title: GOSLO Trigger / Awareness Taxonomy SSOT
date: 2026-05-15
status: tentative
category: active-interface-ssot
owner: Web Console Chat / Interface
source_chat: web-console
scope: DSG TriggerOutcome, Photo/Evidence Awareness, runtime notification body-feel, App animation hooks, Web trigger visualization
source:
  - src/parrot/dsg/triggers/base.py
  - src/parrot/dsg/triggers/__init__.py
  - src/parrot/brain/context_injector.py
  - src/parrot/brain/photo_awareness.py
  - src/parrot/brain/vision/evidence_awareness.py
  - codex_workspace/design_workspace/backend_interface_map/web_console/observability_runtime_business_flow_20260513.md
---

# GOSLO Trigger / Awareness Taxonomy SSOT

This file is the shared place for trigger families, notification strength, and
body-feel labels. A trigger family is not the same thing as a notification
level. Photo, calendar, message, attention, roleplay, and scene triggers can
each have many concrete sub-triggers with different body feel.

Do not use the legacy `TriggerOutcome.notify_gemini` boolean as the final body
feel contract. It is a compatibility signal. The current safe default is C3
chat-context notice. C4 speech and interruption require explicit future policy.

## 1. Channel Levels

| Level | Canonical label | Channel | Body feel | Current rule |
|:--|:--|:--|:--|:--|
| L0 | `record_only` | storage / evidence ledger / L1.5 / L2-B | No felt notification. | Safe for background evidence, tombstones, archival, and graph maintenance. |
| L1 | `working_set` | IntentWorkspace staged ref | Discoverable, but GOSLO may not notice until a tool/turn reads it. | Use for heavy payloads, photos, reports, drafts, and temporary evidence. |
| L2 | `blackboard_notice` | Blackboard transient key / event ledger | Audited runtime notice, still not strong LLM injection. | Use to record source, policy, reason, cooldown, and result. |
| C3 | `context_notice` | `ContextInjector.inject_status_notice()` / `session.update_chat_ctx` | GOSLO can notice on the next natural turn; no speech. | Default for Photo Awareness, Evidence Awareness, and ordinary trigger notifications. |
| C4 | `safe_turn_speech` | `session.generate_reply()` after session policy checks | GOSLO proactively says something at a safe turn boundary. | Only for high-priority, time-sensitive, user-relevant events after review. |
| I0 | `interrupt` | LiveKit turn/interruption policy | Immediate interruption / barge-in. | Reserved for rare safety or explicitly user-approved urgent modes. Not enabled for Photo/Evidence V1. |

## 2. Body-Feel Parameters

Future trigger DTOs or receipts may carry these fields. They are taxonomy
fields first; do not promote them to Unity/App DTOs without a core review.

| Field | Meaning | Typical values |
|:--|:--|:--|
| `trigger_family` | Broad family used for clustering and UI grouping. | `photo`, `visual_attention`, `calendar`, `message`, `scene`, `roleplay`, `memory`, `intent`, `archive`, `nanobot`, `app_lifecycle` |
| `trigger_kind` | How it fires. | `startup`, `periodic`, `event_driven`, `on_demand`, `manual_operator`, `model_tool` |
| `body_feel` | User-facing experience tag. | `silent`, `ambient`, `notice`, `nudge`, `prep`, `urgent`, `surprise`, `emergency` |
| `delivery_level` | Target channel level. | `record_only`, `working_set`, `blackboard_notice`, `context_notice`, `safe_turn_speech`, `interrupt` |
| `priority` | Scheduler/task priority, not necessarily speech priority. | `low`, `normal`, `high`, `reflex` |
| `urgency` | Time pressure. | `none`, `soon`, `imminent`, `now` |
| `surprise` | Novelty/startle score for future Awareness. | `0.0` to `1.0` |
| `user_relevance` | Whether the user likely needs to know. | `low`, `normal`, `high`, `critical` |
| `confidence` | Confidence in source interpretation. | `0.0` to `1.0` |
| `quiet_hour_policy` | Whether the event can surface during quiet hours. | `suppress`, `digest_only`, `urgent_only`, `allow` |
| `cooldown_key` | Dedup/rate-limit identity. | provider id, photo id, evidence id, plan id |
| `recommended_action` | What GOSLO should do. | `remember`, `notice_later`, `ask_user`, `prepare`, `dispatch_task`, `speak`, `interrupt` |

## 3. Current Trigger / Awareness Inventory

| Family | Current implementation | Trigger kind | Data path | Default delivery | Body feel notes |
|:--|:--|:--|:--|:--|:--|
| `photo.capture_preview` | `photo.taken_preview` ECP -> `photo_awareness` | event-driven | PhotoNode + IntentWorkspace preview ref + `transient/photo_awareness_notice` | `context_notice` when policy is `AWARE_SILENT` or `AWARE_REACT` | Normal photo notification is C3. Off/unaware means no GOSLO notice, though storage may still happen. |
| `photo.asset_uploaded` | HTTP upload -> `photo.asset_uploaded` -> observer | event-driven | disk asset + `IMAGE_ASSET` evidence + PhotoNode + RefTable + IntentWorkspace PHOTO | `working_set` | Asset arrival alone should not speak. It gives later evidence/Ref operations a real file. |
| `visual_attention.threshold` | `FocusBboxThreshold` | event-driven | `BBOX_FOCUS` evidence + `transient/current_attention_hint` + `attention.threshold.crossed` | `blackboard_notice` now; future `context_notice` via WEB-015.12 | BBox/magnifier/focus is attention, not automatically speech. Surprise/urgency may later raise it. |
| `evidence.ready` | `evidence_awareness.stage_*` | manual/operator or future bridge | IntentWorkspace `visual_evidence_hint` + `transient/evidence_awareness_notice` | `context_notice` | C3 no-interrupt by default; C4 safe-turn is future policy. |
| `calendar.digest` | `CalendarTrigger` startup/periodic/result | startup/periodic/event-driven | Nanobot fetch -> `GOOGLE_CALENDAR` observations -> L1.5 | `context_notice` if notification text exists | Digest and prep are C3. Future C4 only for explicit urgent/imminent events. |
| `calendar.prep` | `CalendarTrigger` prep window | periodic | same as calendar digest | `context_notice` | Should feel like gentle preparation, not alarm. |
| `calendar.imminent_urgent` | Calendar event with urgent/near-now fields | periodic/event-driven | same as calendar digest | future `safe_turn_speech` candidate | Needs explicit `is_urgent`, time pressure, cooldown, and quiet-hour policy. |
| `message.important` | `MessageNotificationTrigger` | periodic/event-driven | Gmail/Nanobot -> `GOOGLE_MESSAGE` observations -> L1.5 | `context_notice` | Normal important messages are C3. High importance may later become C4 safe-turn. |
| `scene.context_recall` | `SceneContextTrigger` | startup/event-driven | Graphiti search + notification text | `context_notice` | "This reminds me of..." should be gentle context unless user asks. |
| `scene.switch` | `SceneSwitchTrigger` | on-demand | bucket freeze/clear + archive request | `context_notice` | Mode/scene transition. Avoid speech spam while UI is switching. |
| `roleplay.mode` | `RoleplayModeTrigger` | on-demand | roleplay bucket ops + archive on close | `context_notice` | Enter/exit mode can be visible in App; C4 only if user expects spoken confirmation. |
| `intent.boundary` | `IntentEventBoundaryTrigger` | event-driven | IntentEvent open/close tags | `record_only` | Subconscious boundary; should not notify user. |
| `memory.ssot_enrichment` | `SSOTEnrichmentTrigger` | startup/event-driven | Graphiti/Obsidian enrichment or Nanobot research dispatch | `record_only` / `working_set` | Confidence booster, not a spoken event. |
| `memory.obsidian_ingest` | `ObsidianIngestTrigger` | event-driven | Obsidian note -> UserTagFilter -> L1.5 | `record_only` | Import/sync status can be Web-visible; GOSLO notice only on explicit review. |
| `curiosity.unknown_object` | `GosloCuriosityTrigger` | event-driven | `GOSLO_AUTONOMOUS` observation + optional PHOTO ref + optional Plan | `working_set` now | High novelty can later become C3 or C4 after user review. |
| `archive.idle` | `IdleArchiveTrigger` | periodic | Archive request | `record_only` | Background housekeeping. |
| `nanobot.result` | Scheduler/Nanobot result path | event-driven | result stream -> Plan/Trigger/IntentWorkspace | depends on task | Web Runtime Flow should cluster by task family and return target. |
| `app.lifecycle` | App/LiveKit lifecycle events | event-driven | BB state + ContextInjector visual/video tier cues | C3/C4 depending event | Recovery from outage can be C4; routine state drift is C3. |

## 4. App Animation / Body-Language Hooks

Animation is a separate embodied channel. It can express body feel without
touching the LLM context.

| Cue | Source | Suggested App behavior | LLM injection |
|:--|:--|:--|:--|
| `listening_head_tilt` | user speech detected / active listening / ASR partials | Parrot tilts head slightly toward the speaker, with subtle idle motion. | none |
| `notice_glance` | C3 context notice queued | short glance / tiny alert posture if not disruptive | already C3 |
| `surprise_peek` | future high surprise visual attention | short surprised face/posture, no speech unless policy allows | C3 or future C4 |
| `urgent_alert` | future safety/critical event | visible alert pose; possible interrupt only after policy review | future C4/I0 |

The listening head tilt should be recorded as an App animation requirement:
when GOSLO is listening to the user, the model should tilt its head in a calm,
attentive way. This does not require a trigger to inject into the LLM.

## 5. Web Visualization Guidance

Runtime Flow cannot draw every trigger as a full node. Use clustered views:

- Group by `trigger_family` first.
- Color or badge by `delivery_level`.
- Use size/intensity for `priority`, `urgency`, and `surprise`.
- Collapse low-level `record_only` triggers into lanes with counts and recent
  examples.
- Expand a cluster into concrete trigger rows only on click.
- Keep payloads in details drawers; the graph should show flow and body feel,
  not raw JSON.

Suggested clusters:

1. Awareness: photo, evidence, visual attention.
2. Time and obligations: calendar, scheduler, plan gates.
3. Messages and people: Gmail/message, chat, Nanobot reports.
4. Memory maintenance: Obsidian, Graphiti, SSOT enrichment, archive.
5. Mode/lifecycle: scene switch, roleplay, app lifecycle, video tier.

## 6. Current Code Alignment

- `ContextInjector.inject_status_notice()` is the canonical C3 helper.
- `ContextInjector.inject_notification()` remains C4 and must be used
  deliberately.
- 2026-05-15 fix: legacy DSG `notify_gemini` now routes through C3 by default
  in `TriggerRunner`; it no longer implies C4 speech.
- `PhotoAwarenessPolicy` now maps:
  - `UNAWARE_RECORDED` -> no strong GOSLO notice.
  - `AWARE_SILENT` -> C3 photo context notice.
  - `AWARE_REACT` -> C3 with future safe-turn C4 candidate wording, not C4 yet.
- Attention threshold auto bridge is still pending: threshold crossing should
  request nearest evidence, stage a `visual_evidence_hint`, then use the
  Evidence Awareness C3 path.

## 7. Promotion Rules

- New trigger families can be added to this file before they get a code enum.
- New delivery fields must first be Web/backend receipts or core candidates.
- Do not add `surprise`, `urgency`, or `delivery_level` to Unity/App DTOs until
  App/Web both confirm the shared subset.
- C4 and interruption must have user-facing body-feel copy, cooldown, quiet
  hour behavior, and a live conversation smoke test before becoming default.
