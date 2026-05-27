---
title: GOSLO Trigger / Awareness Taxonomy SSOT
date: 2026-05-15
status: active
category: active-interface-ssot
owner: Web Console Chat / Interface
source_chat: web-console
writer: Codex
confirmed_by:
  - web-console
confirmed_at: 2026-05-15
approved_by: user
scope: DSG TriggerOutcome, Photo/Evidence Awareness, runtime notification body-feel, App animation hooks, Web trigger visualization
source:
  - src/parrot/dsg/triggers/base.py
  - src/parrot/dsg/triggers/__init__.py
  - src/parrot/dsg/triggers/runner.py
  - src/parrot/dsg/triggers/message_trigger.py
  - src/parrot/dsg/triggers/calendar_trigger.py
  - src/parrot/scheduler/service.py
  - src/parrot/brain/agent.py
  - src/parrot/brain/context_injector.py
  - src/parrot/brain/photo_awareness.py
  - src/parrot/brain/vision/evidence_awareness.py
  - src/parrot/brain/vision/tool_lifecycle.py
  - src/parrot/brain/observer/visual_tool.py
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
| `visual_tool.lifecycle` | `/api/app/visual-tool/event` or ECP `visual_tool.lifecycle` -> `tool_lifecycle` | event-driven | RefBinding + `TimeAlignedSampleRef` + IntentWorkspace + optional `transient/evidence_awareness_notice` | BBox: `context_notice` on confirm; MAG: `working_set` by default | Implemented backend/App V1. It is semantic tool salience, not DSG L3 attention. C4 requests are audited and downgraded to C3 in V1. |
| `visual_attention.threshold` | `FocusBboxThreshold` | event-driven | `BBOX_FOCUS` evidence + `transient/current_attention_hint` + `attention.threshold.crossed` + Evidence Awareness bridge | `blackboard_notice` plus possible `context_notice` after stored evidence resolves | BBox/magnifier/focus is attention, not automatically speech. Surprise/urgency may later raise it. The bridge does not capture frames, mutate L2-B, or call C4 speech. |
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

### 3.1 Visual Tool Body-Feel Defaults

These defaults are the current product line for App BBox/MAG tools. CORE-014
is now implemented as a backend/App V1 route/event surface, but these are still
taxonomy/body-feel rules, not Unity top-level DTO fields and not the future DSG
L3 attention module.

| Tool family | Typical source | Default delivery | Body feel | Notes |
|:--|:--|:--|:--|:--|
| `visual_attention.bbox_confirm` | User frames something with BBox and confirms. | `working_set` + possible `context_notice` | `notice` / `nudge` | Strong attention. Backend should stage a visual evidence hint and may C3 GOSLO when awareness policy allows it. Still no C4 by default. |
| `visual_attention.mag_dwell` | User holds/uses magnifier to inspect or read. | `working_set` or `blackboard_notice` | `ambient` / `notice_later` | Weak attention. MAG is mostly a user reading/inspection tool; C3 only on explicit send, high dwell/relevance, or reviewed trigger policy. |
| `visual_attention.tool_asset_ready` | Tool-rendered crop/snapshot arrives by HTTP/storage. | `working_set` | `silent` / `ambient` | Asset readiness alone is not speech. It gives identify_object, IntentWorkspace, and future L2-B/Ref paths an auditable image. |
| `visual_attention.high_surprise` | Future novelty/surprise/urgency score crosses a high threshold. | future `safe_turn_speech` candidate | `surprise` / `urgent` | Requires cooldown, quiet-hour, user relevance, and live LineA/LineB policy review before C4. |

Current backend code has two paths:

- Compatibility pulse bridge: `bbox.placed` / `bbox.removed` and
  `focus.anchored` / `focus.released` feed the old threshold accumulator.
- Formal lifecycle V1: `/api/app/visual-tool/event` and ECP
  `visual_tool.lifecycle` carry `preview_start`, `hover`, `drag_update`,
  `resize_update`, `dwell_tick`, `lock`, `unlock`, `settings_open`,
  `confirm`, `explicit_send`, `cancel`, and `release`.

### 3.2 Nanobot Result Channels And Trigger Dispatch

This section records the 2026-05-23 user clarification request around
`result_channel`, trigger firing modes, and C3/C4 routing.

`result_channel` is a Scheduler/Nanobot result classification. When Scheduler
fans in a Nanobot result, it republishes the result on `parrot.trigger.results`
with `type = result_channel` and `original_type = task_type`. It is not itself
the final GOSLO delivery channel, not a body-feel level, and not a guarantee of
C3 speech. It is the event type that event-driven triggers inspect.

Current observed result channel values include:

| `result_channel` | Typical originating task | Current trigger ownership | Default delivery intent |
|:--|:--|:--|:--|
| `message_result` | `message_check` | `MessageNotificationTrigger` today | Usually `GOOGLE_MESSAGE` observations plus C3/C4 candidate policy. |
| `calendar_result` | `calendar_fetch` / calendar mutation tasks | `CalendarTrigger` today | Calendar observations plus digest/prep/imminent notification policy. |
| `diary_result` | `diary_query` | No dedicated DSG trigger confirmed | Direct Brain/tool result path unless future diary trigger is added. |
| `reminder_result` | `remind` | No dedicated DSG trigger confirmed | Direct reminder result path unless future reminder trigger is added. |
| `memory_ref_scan_result` | memory/ref scan tasks | No dedicated DSG trigger confirmed | Memory/ref ledger or direct result path depending caller. |
| `research_result` | web/research Nanobot tasks | No dedicated DSG trigger confirmed | Direct Brain/report path unless future report trigger stages artifacts. |

The relationship is fan-out plus self-filtering, not a hard one-to-one mapping.
`TriggerRunner` can offer one event to every `EVENT_DRIVEN` or `ON_DEMAND`
trigger, and each trigger decides whether it handles that event by checking
fields such as `type`, `kind`, source metadata, cooldown keys, or payload shape.
In current code, `message_result` effectively maps to
`MessageNotificationTrigger` and `calendar_result` to `CalendarTrigger`, but the
protocol allows additional triggers to observe the same `result_channel` later
for audit, staging, planning, or visualization.

`TriggerKind` answers a different question from `result_channel`:

| Concept | Question it answers | Example |
|:--|:--|:--|
| `TriggerKind.STARTUP` | Should this trigger run when TriggerRunner starts? | Calendar/message trigger does an initial fetch. |
| `TriggerKind.PERIODIC` | Should this trigger wake on a timer? | Calendar/message trigger polls if needed. |
| `TriggerKind.EVENT_DRIVEN` | Should this trigger inspect incoming Pub/Sub events? | `type=message_result` after Nanobot returns. |
| `TriggerKind.ON_DEMAND` | Can code/user explicitly fire this trigger? | Scene/roleplay/explicit boundary changes. |
| `result_channel` | What result family should a Nanobot task return as? | `message_check` asks for `message_result`. |

Upward channel selection happens after a trigger has accepted an event and built
a `TriggerOutcome`. The trigger chooses outcome fields such as
`commit_observations`, `staged_refs`, `plan_request`, `notify_gemini`, and
`proactive_speech`; `TriggerRunner` and session policy then translate those into
L0/L1/L2/C3/C4/I0 behavior. Therefore `result_channel=message_result` does not
mean "send C3"; it means "this is a message result event that message-related
triggers may process." The C3/C4 decision belongs to TriggerOutcome processing
plus policy.

User requirement: Nanobot should primarily do work and return structured
results. It may include summaries, `message_to_goslo`, artifact manifests,
source locators, and a suggested delivery hint, but it should not be the final
authority deciding whether a result enters Brain, Plan, memory, Graphiti,
Obsidian, or IntentWorkspace. Trigger logic should convert Nanobot returns into
the correct combination of small notification text, observations, staged rich
reports, source/original refs, plan proposals, and optional safe-turn speech.

Large content should not be forced through `result_channel` as raw Pub/Sub
payload. Use `staged_refs` with `DISK_PATH`, `URL`, or bounded `INLINE_TEXT` for
rich reports, original email/document refs, and multimodal artifacts. Future
Nanobot report triggers should support:

| Return shape | Preferred TriggerOutcome relation |
|:--|:--|
| Short report message | `notification_text` / C3, or C4 only after policy review. |
| Facts worth remembering | `commit_observations` into L1.5/L2-B. |
| Rich text report | `staged_refs` as `RICH_REPORT`. |
| Original email/doc/photo/video/audio | `staged_refs` with source locator or file path. |
| Multi-step follow-up needed | `plan_request`. |
| Background archive/export | `archive_request` or future export request. |

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
- `result_channel` is only the Nanobot/Scheduler result family used for trigger
  event filtering. It must not be treated as the C3/C4 delivery level or as a
  closed one-to-one trigger registry.
- `PhotoAwarenessPolicy` now maps:
  - `UNAWARE_RECORDED` -> no strong GOSLO notice.
  - `AWARE_SILENT` -> C3 photo context notice.
  - `AWARE_REACT` -> C3 with future safe-turn C4 candidate wording, not C4 yet.
- Attention threshold auto bridge is implemented conservatively:
  `FocusBboxThreshold` records the threshold event, then
  `evidence_awareness.bridge_attention_threshold_to_goslo()` resolves the
  nearest stored frame/photo by BBox/Focus ref and producer timebase. Ready
  evidence is staged as an IntentWorkspace `visual_evidence_hint`; missing
  evidence becomes a pending request. It still does not capture frames, mutate
  L2-B, call `generate_reply()`, or enable interruption.
- `time_aligned_evidence_interface_20260515.md` is the Web/backend SSOT for
  the evidence/timebase side of these trigger flows and the CORE-012 promotion
  blockers.
- 2026-05-16 App-blocker audit: BBox defaults to strong attention with
  IntentWorkspace plus possible C3; MAG defaults to weak/local inspection with
  C3 only on explicit send or high relevance. CORE-014 backend/App V1 now
  implements the route/event surface; production App toolbar emission still
  requires phone/screen-share smoke and UI/body-feel review. CORE-014 remains a
  small visual-tool lifecycle/evidence contract, not a DSG L3 attention
  implementation.

## 7. Promotion Rules

- New trigger families can be added to this file before they get a code enum.
- New delivery fields must first be Web/backend receipts or core candidates.
- Do not add `surprise`, `urgency`, or `delivery_level` to Unity/App DTOs until
  App/Web both confirm the shared subset.
- C4 and interruption must have user-facing body-feel copy, cooldown, quiet
  hour behavior, and a live conversation smoke test before becoming default.

## 8. Change Log

- 2026-05-15: Promoted this taxonomy from tentative to active Interface SSOT
  for Web/backend trigger body-feel routing after user approval in Web Console
  chat. Updated the visual-attention row and code-alignment section to reflect
  the implemented conservative `attention.threshold.crossed` -> Evidence
  Awareness bridge. Unity/App DTO fields remain unpromoted unless App/Web later
  confirm a shared subset.
- 2026-05-16: Added visual-tool body-feel defaults for BBox versus MAG and
  linked production App emission to CORE-014 evidence lifecycle policy.
- 2026-05-16: Updated after backend implementation of
  `/api/app/visual-tool/event`, ECP `visual_tool.lifecycle`, Web debug
  `/api/vision/evidence/tool-lifecycle`, and BB receipt
  `transient/visual_tool_lifecycle_receipt`.
- 2026-05-23: Added Nanobot result-channel clarification. Recorded that
  `result_channel` classifies return events for trigger fan-out/self-filtering,
  while TriggerOutcome plus session policy chooses L0/L1/L2/C3/C4/I0 delivery.
  Captured the requirement that future Nanobot report flows stage rich reports,
  originals, and multimodal artifacts via IntentWorkspace instead of treating
  Pub/Sub payloads as large-file transport.
