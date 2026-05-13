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
| CORE-006 | needs_user_decision | coordination + unity-app | `MemoryRefBindingApi`: list/add/remove/retarget refs and typed visual edges between UI artifacts, L2-B nodes, Graphiti UUIDs, episodes, photos, docs, and external refs | Unity App, Web Console, DSG/L2-B, Brain refs | App needs partial ref attach/detach for workspace boards; Web needs full memory graph surgery and visualization. Include extensible `edge_kind` / `visual_style_id` / `workspace_id` fields so Red String, Evidence Board, and future board modes do not hard-code one renderer. | New Interface doc or RefBinding/DSG addendum | Refine in primary chat from `app/canvas_menu_ref_workspace_app_interface_20260513.md`; exact App-safe subset and backend adapter ownership pending confirmation. |
| CORE-007 | needs_user_decision | coordination + unity-app | `CanvasMenuCoreV1`: shared read/apply/preset/canvas snapshot boundary for RoomSetting, menu blocks, workspace entry, tiered setting actions, and typed canvas nodes/edges | Unity App, Web Console, Brain facade | Existing menu/canvas contracts are real but scattered across `MenuRegistry`, `PresetLoader`, `RoomSettingService`, `AppFirstVersionFacade.canvas_snapshot()`, and orchestrator tier docs. App/Web need one minimal shared DTO boundary while keeping renderers lane-specific. | Existing Interface menu/RoomSetting docs or new compact addendum | Refine in primary chat from `app/canvas_menu_ref_workspace_app_interface_20260513.md`; keep Unity/Web renderers lane-specific. |
| CORE-008 | draft | web-console | `L15ManagementApi`: L1.5 bucket/source/ref health plus safe management subset for menu surfaces | Unity App, Web Console, DSG/L1.5, Brain refs | Web needs comprehensive L1.5 management; the App phone/menu path also needs a smaller safe subset. Shared fields should cover bucket id/name, source id/type, admit/reject counts, ref health, stale/broken state, and safe verify/refresh/retarget drafts without exposing Web-only operator surgery. | DSG/L1.5 or RefBinding interface addendum | Needs App/Web confirmation on exact read fields, App-safe write subset, and whether Web-only repair actions stay behind a separate operator API. 2026-05-14 Web trigger audit added `GOOGLE_MESSAGE` as a prototype ObservationSource/BucketKind so Gmail/message triggers enter L1.5 like Calendar/Obsidian instead of direct L2-B writes. |
| CORE-009 | draft | web-console | `MemoryRuntimeChangeStream`: sequence-based realtime/diff contract for L2-B, Blackboard, IntentWorkspace, Plan/task, Ref, and trigger/runtime receipts | Web Console first; possible Unity App HUD/menu consumer later | Web needs live visual operations without repeatedly repainting broad snapshots. If App later needs the same live DSG/Blackboard/Intent/Plan stream, this should become a shared changed-since/SSE/WebSocket contract with bounded event types, source/writer, op, entity id, timestamp, summary, and redacted payload pointers. | Runtime/DSG/RefBinding interface addendum only after dual-lane confirmation | Keep as Web-only `changed_since` or SSE prototype first. Promote only if App confirms the same stream is needed; do not add Web operator action fields to App DTOs. |
| CORE-010 | draft | web-console | `RuntimeFlowTraceReadModel`: trace/span-like read model for Intent, Plan, HITL, Blackboard, IntentWorkspace, Scheduler, Nanobot, Trigger, Message, and Graphiti commit events | Web Console first; possible Unity/App status HUD later | Runtime Flow needs a single visual read shape so operators can follow one action across modules. Fields should stay observational: `sequence`, `trace_id`, `span_id`, `parent_span_id`, `entity_kind`, `entity_id`, `op`, `status`, `source`, `writer`, `summary`, `created_at`, and redacted payload/ref links. | Runtime observability interface addendum only after dual-lane confirmation | Prototype implemented as Web-only `/api/runtime/flow` and `/api/runtime/flow/changes`; 2026-05-14 review added Web-only `trace_id`/`payload_ref` hints, graph id hygiene, and `source`/`writer` diff-signature coverage. WEB-012.15 now implements Web-only typed schema in `parrot.web_console.runtime_flow_models`. If promoted, clarify that edge `source`/`target` are graph endpoints while event `source` is writer/system. Do not make it a Unity DTO unless the App lane confirms a compact consumer. |
| CORE-011 | draft | web-console | `RuntimeHumanGate`: human-in-the-loop approval/revision gate for Plan, trigger, message, and resume actions | Web Console first; Unity/App may later consume compact confirmations | Web needs HITL V1 for approve/reject/revise/cancel/resume before side effects. Shared fields likely include gate id, trace id, target kind/id, action kind, state, prompt summary, options, expiry, receipt id, redacted payload pointer, and maybe `plan_state` / valid-actions hints if shared consumers need state-aware UI. | Plan/Scheduler/HITL interface addendum only after dual-lane confirmation | Prototype implemented as Web-only pending/draft/apply HITL routes with dry-run receipts; 2026-05-14 review made Plan decisions state-aware and made pending gate `options` reuse the same validation policy. WEB-012.16 now serializes HITL gates/receipts through Web-only typed models and exposes `core_candidate=CORE-011` on relevant receipts. Non-Plan targets return explicit `unsupported_hitl_target`; promote only if App also renders/writes human gates, and do not claim trigger/message gates until those target kinds are implemented. |

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
