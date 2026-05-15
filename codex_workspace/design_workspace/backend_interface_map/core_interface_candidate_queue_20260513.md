# Core Interface Candidate Queue (2026-05-13)

This is a staging queue, not the core SSOT.

Use this file when App or Web discovers that existing core interfaces cannot
support a business flow. Shared candidates move into
`.cursor/memory/architecture/Interface/**` or backend code only after App/Web
dual confirmation. Ask the user for a final decision only when the candidate is
ambiguous, high-blast-radius, or changes product policy.

2026-05-13 primary-chat rule: the user confirmed that this main chat may refine
core candidates with them and, after explicit field-level confirmation, update
the backend and core SSOT directly. Keep this queue, the relevant App/Web
business interface index, and `.cursor/memory/architecture/Interface/INDEX.md`
linked when promoting a candidate. Do not create extra one-off interface docs
for the same module-level decision.

## Candidate Statuses

| Status | Meaning |
|:--|:--|
| `draft` | Proposed by a lane, not reviewed. |
| `needs_lane_confirmation` | Ready for the other lane to confirm/reject/change. |
| `confirmed_for_core` | Required App/Web lane confirmation is complete. |
| `needs_user_decision` | Needs explicit user choice because scope or policy is ambiguous. |
| `ratified` | Added to the core SSOT with writer/source metadata. |
| `rejected` | User rejected; keep the reason. |
| `superseded` | Replaced by another candidate. |

## Queue

| ID | Status | Proposed by | Candidate | Consumers | Business need | Target core doc | Confirmation |
|:--|:--|:--|:--|:--|:--|:--|:--|
| CORE-001 | needs_user_decision | coordination + unity-app | `agent_team_id` / `maid_team_id` on RoomProfile or effective RoomSetting selection | Unity App, Web Console, Scheduler | Lets startup choose Maid Team and lets Web inspect/routable team state. | `.cursor/memory/architecture/Interface/app_v1_room_setting_room_profile_interface_20260510.md` or successor | Refine in primary chat from `app/startup_roomsetting_app_interface_20260513.md`; exact field name, writer, and default/fallback semantics pending user confirmation before backend/SSOT. |
| CORE-002 | needs_user_decision | coordination + unity-app | AgentTeam registry, e.g. `data/registries/agent_teams.json` | Unity App, Web Console, Scheduler, Orchestrator | Stable list of team presets, labels, default nanobot instance group, capabilities, and restart tier. | New Interface doc or backend interface addendum | Refine in primary chat from `app/startup_roomsetting_app_interface_20260513.md`; App needs safe read summary, Web may later own admin/edit flows. |
| CORE-003 | draft | coordination | `/status` extension for active AgentTeam and nanobot instance health | Unity HUD, Web Console | Shared status for current Maid Team and backing instances. | ECS orchestrator/interface addendum | Needs App/Web confirmation before implementation. |
| CORE-004 | draft | coordination | Scheduler task routing by `agent_team_id` | Scheduler, Nanobot, Web Console | Enables multiple AgentTeams or worker groups without hard-coding one stream. | Scheduler/interface addendum | Needs Web + Scheduler/App impact confirmation. |
| CORE-005 | draft | coordination | Web-only Nanobot/MCP admin API shape | Web Console | Lets Web design edit/apply/restart flows while keeping App DTOs clean. | Web business first; core only if shared surface emerges | Not a core contract unless another lane needs it. |
| CORE-006 | needs_user_decision | coordination + unity-app | `MemoryRefBindingApi`: list/add/remove/retarget refs and typed visual edges between UI artifacts, L2-B nodes, Graphiti UUIDs, episodes, photos, docs, and external refs | Unity App, Web Console, DSG/L2-B, Brain refs | App needs partial ref attach/detach for workspace boards; Web needs full memory graph surgery, visualization, Node detail, and manual binding for source files/photos such as photo-mode captures. Include extensible `edge_kind` / `visual_style_id` / `workspace_id` fields so Red String, Evidence Board, and future board modes do not hard-code one renderer. | New Interface doc or RefBinding/DSG addendum | Refine in primary chat from `app/canvas_menu_ref_workspace_app_interface_20260513.md`; exact App-safe subset, photo/file binding fields, and backend adapter ownership pending confirmation. |
| CORE-007 | needs_user_decision | coordination + unity-app | `CanvasMenuCoreV1`: shared read/apply/preset/canvas snapshot boundary for RoomSetting, menu blocks, workspace entry, tiered setting actions, and typed canvas nodes/edges | Unity App, Web Console, Brain facade | Existing menu/canvas contracts are real but scattered across `MenuRegistry`, `PresetLoader`, `RoomSettingService`, `AppFirstVersionFacade.canvas_snapshot()`, and orchestrator tier docs. App/Web need one minimal shared DTO boundary while keeping renderers lane-specific. | Existing Interface menu/RoomSetting docs or new compact addendum | Refine in primary chat from `app/canvas_menu_ref_workspace_app_interface_20260513.md`; keep Unity/Web renderers lane-specific. |
| CORE-008 | draft | web-console | `L15ManagementApi`: L1.5 bucket/source/ref health plus safe management subset for menu surfaces | Unity App, Web Console, DSG/L1.5, Brain refs | Web needs comprehensive L1.5 management; the App phone/menu path also needs a smaller safe subset. Shared fields should cover bucket id/name, source id/type, admit/reject counts, ref health, stale/broken state, and safe verify/refresh/retarget drafts without exposing Web-only operator surgery. 2026-05-15 Web import design clarified that `roleplay` should be exposed as a mode/profile that may contain multiple source-pack instances, not as a singleton bucket; Graphiti and Obsidian source groups can stay Web virtual groups until App confirms a shared read need. | DSG/L1.5 or RefBinding interface addendum | Needs App/Web confirmation on exact read fields, App-safe write subset, and whether Web-only repair actions stay behind a separate operator API. 2026-05-14 Web trigger audit added `GOOGLE_MESSAGE` as a prototype ObservationSource/BucketKind so Gmail/message triggers enter L1.5 like Calendar/Obsidian instead of direct L2-B writes. |
| CORE-009 | draft | web-console | `MemoryRuntimeChangeStream`: sequence-based realtime/diff contract for L2-B, Blackboard, IntentWorkspace, Plan/task, Ref, and trigger/runtime receipts | Web Console first; possible Unity App HUD/menu consumer later | Web needs live visual operations without repeatedly repainting broad snapshots. If App later needs the same live DSG/Blackboard/Intent/Plan stream, this should become a shared changed-since/SSE/WebSocket contract with bounded event types, source/writer, op, entity id, timestamp, summary, and redacted payload pointers. 2026-05-14 WEB-013 adds a concrete full-screen L2-B monitor need, including browser reconnect behavior and engine-agnostic graph events. 2026-05-15 adds React-Force-Graph-style full-screen L2-B rendering, Graphiti search subgraph loading, renderer-level trigger/attention animations, and Graphiti-to-L2-B export receipts as Web-first stream consumers. | Runtime/DSG/RefBinding interface addendum only after dual-lane confirmation | Keep as Web-only `changed_since` or SSE/WebSocket prototype first. Promote only if App confirms the same stream is needed; do not add Web operator action fields to App DTOs. |
| CORE-010 | draft | web-console | `RuntimeFlowTraceReadModel`: trace/span-like read model for Intent, Plan, HITL, Blackboard, IntentWorkspace, Scheduler, Nanobot, Trigger, Message, and Graphiti commit events | Web Console first; possible Unity/App status HUD later | Runtime Flow needs a single visual read shape so operators can follow one action across modules. Fields should stay observational: `sequence`, `trace_id`, `span_id`, `parent_span_id`, `entity_kind`, `entity_id`, `op`, `status`, `source`, `writer`, `summary`, `created_at`, and redacted payload/ref links. 2026-05-15 Runtime Flow adds a Web-first need to show manual Plan import, manual Nanobot task dispatch, result destination choices (`view_only`, `return_to_goslo`, `return_to_app`), and message/trigger collaboration receipts. | Runtime observability interface addendum only after dual-lane confirmation | Prototype implemented as Web-only `/api/runtime/flow` and `/api/runtime/flow/changes`; 2026-05-14 review added Web-only `trace_id`/`payload_ref` hints, graph id hygiene, and `source`/`writer` diff-signature coverage. WEB-012.15 now implements Web-only typed schema in `parrot.web_console.runtime_flow_models`. If promoted, clarify that edge `source`/`target` are graph endpoints while event `source` is writer/system. Do not make it a Unity DTO unless the App lane confirms a compact consumer. Nanobot result-destination routing remains a candidate gap until backend state/receipt fields are implemented and reviewed. |
| CORE-011 | draft | web-console | `RuntimeHumanGate`: human-in-the-loop approval/revision gate for Plan, trigger, message, and resume actions | Web Console first; Unity/App may later consume compact confirmations | Web needs HITL V1 for approve/reject/revise/cancel/resume before side effects. Shared fields likely include gate id, trace id, target kind/id, action kind, state, prompt summary, options, expiry, receipt id, redacted payload pointer, and maybe `plan_state` / valid-actions hints if shared consumers need state-aware UI. | Plan/Scheduler/HITL interface addendum only after dual-lane confirmation | Prototype implemented as Web-only pending/draft/apply HITL routes with dry-run receipts; 2026-05-14 review made Plan decisions state-aware and made pending gate `options` reuse the same validation policy. WEB-012.16 now serializes HITL gates/receipts through Web-only typed models and exposes `core_candidate=CORE-011` on relevant receipts. Non-Plan targets return explicit `unsupported_hitl_target`; promote only if App also renders/writes human gates, and do not claim trigger/message gates until those target kinds are implemented. |
| CORE-012 | draft | unity-app + web-console | `TimeAlignedEvidenceRef`: shared evidence/ref shape for GOSLO Intent `identify_object`, SVA frame sampling, camera/photo mode, Focus/BBox/magnifier attention, ASR/CV samples, and L2-B/Graphiti node creation | Unity App, Web Console, Brain Intent tools, SVA/video processor, DSG/L1.5/L2-B | `identify_object` should obtain a time-aligned frame from LiveKit background video, SVA frame cache, or HTTP/storage image asset, not from camera-mode inline RPC. Focus/BBox/magnifier, ASR, and CV workers should contribute evidence with coordinates/region, pose or producer id, sample timestamp, optional storage image ref, and trigger context so GOSLO can receive compact notifications and L2-B/IntentWorkspace can create/update evidence-linked nodes or refs. | Future SVA/ECP/RefBinding interface addendum, likely linked to CORE-006 and protocol snapshot only after dual-lane review | First Web/backend slices implemented as `parrot.brain.vision.evidence` with `TimebaseStamp` / `TimeAlignedSampleRef`, `parrot.brain.vision.frame_cache` with `record_livekit_frame_bytes()`, and `parrot.brain.vision.livekit_sampler` as the Brain room-scoped low-FPS LiveKit track consumer. ECP/RPC top-level schemas stay unchanged for V1; optional stamps live in `EcpEvent.payload["timebase"]`, `EcpCommand.meta["timebase"]`, or HTTP/upload/frame metadata. Candidate fields now include `evidence_id`, `kind`, `status`, `clock_domain`, `wall_time_ms`, `monotonic_ms`, `media_time_us`, `sequence`, `estimated`, `source_id`, `asset_uri`, `asset_path`, `region`, `bbox_refs`, `focus_refs`, `related_refs`, `room_id`, `track_sid`, `participant_id`, `description`, and redacted `meta`. The Web frame-cache upload route is debug/operator-only; live Unity/LiveKit smoke, crop/VLM comparison, and App lane shared-subset review still block SSOT promotion. |

## 2026-05-15 Candidate Implementation Notes

- CORE-008: Web-only Graphiti-to-L2-B export now preserves selected Graphiti
  provenance (`graphiti_partition`, hit UUIDs, endpoint UUIDs, source URL,
  source description, and fact text) by admitting
  `Observation(source=USER_EXPLICIT)` through L1.5. This is intentionally not
  promoted to a new shared ObservationSource until App/Web agree on a shared
  source-bucket contract. 2026-05-15 continuation adds Web-only
  `edge_drafts` to the export receipt so operators can see Graphiti
  source/target/fact intent, but these are not shared L2-B Edge DTOs; actual
  edge writes require resolved L2-B node UUIDs and separate operator review.
- CORE-008: Web-only Obsidian vault batch import now has scan/import-draft/import
  routes. The shared candidate implication is only the small L1.5 source-pack
  read shape (`daily` / `roleplay` / `ref`, target bucket, health, selected
  source path); the Web operator import button and direct test path stay out of
  App DTOs.
- CORE-008: Web-only Google Calendar source import now has fetch/preview/import
  routes. The shared candidate implication is the source-ingest read shape:
  provider identity (`calendar_id`, `calendar_event_id`), temporal range
  (`observed_at`, `time_span`, start/end strings), status/version fields
  (`status`, `etag`, `updated`, `ical_uid`), and lightweight Ref binding. The
  Web operator fetch/import buttons stay out of App DTOs. 2026-05-15 Web-first
  backend policy for cancelled/deleted rows is historical tombstone EVENT:
  preserve provider identity, set `calendar_lifecycle`, `is_tombstone`,
  `tombstone_policy=historical_event`, and lower L2-B state to GHOST/peripheral
  rather than default evict. Web `mapping_rows` are only receipt explanations
  for operators and should not be promoted unless another lane confirms a
  shared read need.
- CORE-009: Graphiti search-to-subgraph and export receipts are now concrete
  Web stream consumers. They remain polling/receipt based; no shared
  SSE/WebSocket DTO is promoted yet.
- CORE-009: 2026-05-15 Web implemented the first concrete Memory
  changed-since polling envelope at
  `GET /api/memory/live-state/changes?since=...&limit=...`. Shape is
  `success`, `action`, `since`, `sequence`, `changed`, bounded `events`,
  optional `snapshot`, and `audit`. It is Web-only and wraps the existing
  `build_app_live_state()` snapshot; no App/Unity DTO was changed. If promoted
  later, this should be the baseline vocabulary for SSE/WebSocket rather than a
  separate stream shape.
- CORE-009 / CORE-010: Google Calendar true realtime should be modeled as
  backend result/delta events (`calendar_result`, source-ingest receipts, and
  L1.5/L2-B change events), not browser OAuth. If App later needs the same
  live schedule-memory updates, promote the bounded changed-since/SSE shape
  through CORE-009 and trace rows through CORE-010. 2026-05-15 Web added a
  bounded Scheduler-owned `STREAM_TRIGGER_RESULTS` ledger and
  `GET /api/google/calendar/results` as an observability read model; this is a
  candidate trace/history primitive, not an App command DTO.
- CORE-006: 2026-05-15 Web added a draft-only probe route
  `POST /api/refs/binding/draft`. It accepts `ref_id`, `target_kind`, and
  `target_id`, returns the current RefBinding plus a draft target and
  `core_candidate=CORE-006`, and deliberately has no apply route. A follow-up
  Web bugfix clarified unresolved-target semantics: `target_kind=unresolved`
  is an unresolve/clear preview (`would_unresolve=true`), not a durable resolve
  operation. This lets the Web Source Board preview photo/file/ref retargeting
  without deciding the shared App-safe mutation contract or exposing Web repair
  actions in Unity DTOs.
- CORE-012: 2026-05-15 Web/backend first slice adds a bounded Temporal Evidence
  Ledger and `TimebaseStamp` parser. It intentionally treats
  `EcpEvent.created_at` as envelope time only; explicit sample time stays under
  `payload.timebase` or compatible legacy keys until App/Web agree to promote a
  top-level field. `identify_object` now records/uses evidence ids and no
  longer calls the old snapshot RPC path. Shared promotion is blocked on a real
  LiveKit/SVA frame-cache producer, crop/VLM tests, and App lane field review.
- CORE-012: 2026-05-15 continuation adds the storage-backed frame-cache ingress
  (`parrot.brain.vision.frame_cache.record_livekit_frame_bytes`), Web-only
  `POST /api/vision/evidence/frame-cache/upload` smoke route, and
  `parrot.brain.vision.livekit_sampler` automatic low-FPS room sampler. This
  proves the ledger/storage/timebase shape for encoded frames in unit tests.
  The sampler now writes secret-free status for Web observability and ships a
  manual real-room smoke helper (`src/scripts/smoke_livekit_frame_sampler.py`).
  Promotion remains blocked until a real Unity/LiveKit video smoke verifies
  track selection, freshness/stale-frame behavior, reconnect behavior, and
  storage load.
- CORE-012: 2026-05-15 continuation adds
  `parrot.brain.vision.evidence_image` for local stored image/crop preparation
  and `identify_object` VLM describe enrichment. This confirms that CORE-012
  can carry region/time/asset refs while VLM dereferencing remains a
  backend-local storage operation. Reference-image comparison, GOSLO
  notification policy, and App/Web shared-field review still block promotion.
- CORE-012: 2026-05-15 continuation adds
  `parrot.brain.vision.evidence_awareness`, Web `POST
  /api/vision/evidence/stage-hint`, and BB key
  `transient/evidence_awareness_notice` as a backend-first staging/notification
  policy. Evidence can now stage an IntentWorkspace `visual_evidence_hint` and
  record whether session policy allows a GOSLO safe-turn notification. This is
  not an App DTO promotion; session-owned C4 policy and live conversation smoke
  still block SSOT promotion.
- CORE-012: 2026-05-15 continuation wires
  `transient/evidence_awareness_notice` into `ContextInjector` C3 delivery.
  Allowed notices append compact evidence/ref context to Gemini chat context
  with no-interrupt wording; silent notices remain layer-1. C4 speech remains a
  policy candidate, not a ratified shared interface.
- CORE-012: 2026-05-15 continuation adds Web/backend freshness status for the
  sampler and frame cache (`fresh_window_ms`, `latest_frame_age_ms`,
  `latest_frame_fresh`, per-track latest summaries). These fields support
  operator observability and evidence selection; they are not promoted as
  Unity/App DTO fields until the App lane reviews video lifecycle and sample
  freshness semantics.
- CORE-012: 2026-05-15 continuation clarifies screen-share producers. The
  Brain sampler recognizes both `screenshare` and `SOURCE_SCREEN_SHARE` style
  LiveKit source names, preserves `publication_source` in Web/backend latest
  frame summaries, and the React Runtime bridge can publish
  `web-console-screen` for no-camera laptop evidence smoke. This remains a
  Web/backend-first producer classification detail; shared promotion still
  waits for live screen-share/Unity track smoke and App lane review.

## Trigger Protocol Audit Notes

- 2026-05-14 Web audit: the active trigger output protocol remains
  `DSG-TRIGGER-V2` / `TriggerOutcome`. `TriggerResult` is only a back-compat
  alias and should not be used as the style for new trigger code.
- 2026-05-14 source cleanup: DSG trigger implementation files now import and
  construct `TriggerOutcome` directly; `TriggerResult` remains covered only by
  compatibility/source-guard tests and external/older import tolerance.
- Web trigger routes (`/api/dsg/triggers/catalog`, `/draft-event`,
  `/fire-event`) are an operator-safe event drafting/publishing surface, not a
  replacement core trigger protocol. Real execution publishes to
  `CH_DSG_EVENTS` under operator mode; the running `TriggerRunner` owns
  `TriggerOutcome` processing.
- The old `SceneTrigger`/`TriggerType` envelope in `parrot.dsg.interfaces` and
  `parrot.dsg.types` still exists as an input/event compatibility path for
  scene alerts. It is not the preferred output protocol and should be folded
  into a typed event envelope only after a separate shared-interface review.

## Promotion Rule

Before changing core code or core SSOT:

1. Set candidate status to `needs_lane_confirmation`.
2. Ask the consuming lanes to confirm the exact candidate name, consumer list,
   and blast radius.
3. If the lanes disagree or the decision changes product policy, set
   `needs_user_decision`.
4. After confirmation, update the target core doc with writer/source and
   lane-confirmation metadata.
5. Link the ratified doc in the queue and shared TODO board.
