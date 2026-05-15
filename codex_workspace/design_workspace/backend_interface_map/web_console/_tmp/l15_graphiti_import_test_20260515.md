# L1.5 + Graphiti Import Test Research Ledger (2026-05-15)

Owner: Web Console chat  
Status: temporary-active  
Category: Web Console temporary research / audit archive  
Scope: L1.5 source board, Obsidian profile import, Google Calendar mapping, Graphiti natural-language search, Graphiti-to-L2-B subgraph export, Arknights test partition  
Updated: 2026-05-15  
Source pointers: `APP_WEB_PARALLEL_TODOLIST_20260513.md`, `memory_graph_workspace_business_flow_20260513.md`, `graphiti_management_business_flow_20260513.md`, `core_interface_candidate_queue_20260513.md`, Graphiti skill, DSG L1.5/L2-B/RustworkX skills, DeepSeek API docs, Graphiti/Zep docs, PRTS Wiki story index

This temporary ledger exists so the L1.5/Graphiti import task can be audited
without creating scattered design docs. Durable decisions must be promoted back
to the Web TODO board and active Web business-interface files.

## Unified Conclusions Before Design

- `roleplay` is not a single product bucket in the UI. It is currently an
  Obsidian ingest profile that routes UUID-free setting notes into the
  roleplay setting bucket. Product-wise, RolePlay is a mode that may activate
  many source packs: persona notes, scene notes, relationship notes, rules,
  costumes, world refs, and temporary roleplay context.
- Therefore the refactor should show **RolePlay mode / profile** separately
  from **source bucket instances**. The backend can keep the current
  `profile=roleplay` compatibility path, while Web groups multiple roleplay
  source instances under that profile.
- `daily` and `roleplay` Obsidian notes may create setting Nodes without UUID.
  `ref` notes are binding/strengthening notes and must point to an existing
  Node, Graphiti UUID, or equivalent target.
- L1.5 remains the write gate into L2-B. Graphiti search results, Obsidian
  notes, Google Calendar events, and manual Web Nodes must become observations
  or source-specific trigger outcomes first, then flow through `L15Pool.admit`
  or an existing trigger path. No hidden direct L2-B mutation.
- Graphiti is useful here because it is temporal. Imports should be segmented
  as episodes with `reference_time` and provenance, so extracted facts can
  carry `valid_at` / `invalid_at` style history. Avoid one static "current
  state" card for characters or factions when the source actually describes a
  change over chapters.

## Web Research Anchors

- DeepSeek API docs: official OpenAI-compatible `base_url` is
  `https://api.deepseek.com`, with `deepseek-v4-pro` and
  `deepseek-v4-flash` listed for V4.
- Graphiti add-episode docs: episode ingestion accepts `source_description`
  and `reference_time`; bulk ingestion exists, but bulk mode is only
  appropriate for empty graphs or when edge invalidation is not required.
- Graphiti/Zep temporal docs: facts/edges carry temporal validity, including
  real-world validity windows. This is the reason Arknights test data should
  preserve chapter/order/time hints instead of flattening all lore.
- PRTS Wiki `剧情一览` is the current source index candidate for main story
  links. The importer should store source URLs where links are extractable; if
  only an aggregate or manually summarized source is available, store the PRTS
  page URL plus chapter/section identifiers in `source_description`.

## Strengthened TODO Order

1. Update documentation first: Web TODO, Memory business flow, Graphiti
   business flow, Web README temporary archive index, and candidate queue only
   for shared gaps.
2. Add Graphiti provider config for DeepSeek V4. Keep secrets in environment
   variables only and report only boolean `secret_configured` fields.
3. Add `arknights_test` partition support in the Graphiti status/search paths.
4. Create an Arknights fixture/import script that emits compact original
   summaries and fact episodes with source URLs or source descriptions. The
   script must default to dry-run.
5. Add Graphiti natural-language subgraph search and export draft routes.
   Exported Nodes must enter L1.5 as Web/user-explicit observations with
   Graphiti provenance in source metadata.
6. Refactor L1.5 UI into a source board: Obsidian, Google Calendar, Graphiti,
   Manual Node, and later photo/ref sources. Advanced JSON stays in drawers.
7. Add Obsidian vault scan/preview for the three profiles. RolePlay supports
   multiple source packs under the profile; it is not a single bucket.
8. Add Google Calendar data preview showing raw event, normalized event, and
   resulting L2-B observation metadata before any import.
9. Test dry-run routes, provider config, secret non-leak, partition listing,
   Obsidian profile routing, Calendar field preservation, and Graphiti export
   receipts before any real import.

## Audit Checklist

- No raw DeepSeek, Google, LiveKit, or orchestrator secret appears in repo docs,
  frontend JSON, frontend dist, or status payloads.
- No App/Unity DTO is changed for Web-only Graphiti/L1.5 operator actions.
- Real writes remain dry-run/operator gated until user review.
- `roleplay` wording is consistent: mode/profile in UI, not a singleton bucket.
- URL/provenance handling is explicit for every imported Arknights episode.
- Graphiti imports are temporal episodes with meaningful reference times or
  chapter order metadata.
- Shared stream/source bucket gaps go to the candidate queue only.

## 2026-05-15 Implementation Ledger

Completed in this slice:

- DeepSeek Graphiti provider config is implemented as env-only configuration.
  Web status returns provider/model/base URL and `secret_configured` booleans;
  it never returns the key.
- `arknights_test` is now a Graphiti partition allowlist entry exposed through
  Graphiti status/search validation.
- New Web-only BFF routes exist for Graphiti search-to-subgraph and export:
  `POST /api/graphiti/subgraph/search`,
  `POST /api/graphiti/subgraph/export-draft`, and
  `POST /api/graphiti/subgraph/export`.
- Exported Graphiti hits become `Observation(source=USER_EXPLICIT)` drafts and
  preserve selected `graphiti_*`, `source_url`, and `source_description`
  metadata for L1.5 admission. Real apply requires `operator_mode=true`.
- `src/scripts/import_arknights_to_graphiti.py` creates compact original
  Arknights test episodes and defaults to dry-run.

Verification:

- `uv run python -m py_compile src/parrot/memory/graphiti_client.py
  src/parrot/brain/graphiti_console.py src/parrot/web_console/server.py
  src/parrot/dsg/ingest/base.py src/scripts/import_arknights_to_graphiti.py`
- `uv run pytest tests/test_web_console/test_web_console_server.py -q`
  -> 19 passed.
- `uv run pytest tests/test_dsg/test_obsidian_true_connection.py
  tests/test_dsg/test_calendar_true_connection.py
  tests/test_dsg/test_trigger_outcome_v2.py -q` -> 19 passed.
- `uv run python src/scripts/import_arknights_to_graphiti.py --dry-run
  --limit 2` -> produced two `arknights_test` dry-run episodes.
- `git diff --check` -> no whitespace errors.
- Exact DeepSeek-key scan under `codex_workspace`, `src`, `web`, and `.cursor`
  -> no matches.

Still pending:

- React source-board UI completion. First slice is present for
  Graphiti/Obsidian/Calendar preview/Manual Node. This slice now includes
  Obsidian vault scan preview and Google raw/normalized/Observation preview,
  plus Obsidian import-draft/import routes; it still needs photo/ref source
  cards and a user-reviewed sample-file creation step.
- Obsidian user-approved sample file creation and a real operator import smoke
  after review.
- Google Calendar real import/apply controls after preview review.
- Real Graphiti import to FalkorDB after operator review.

## 2026-05-15 Source Preview Ledger

Completed in this slice:

- `GET /api/l15/obsidian-vault/scan` scans the local vault path, reports vault
  readiness, ready notes, invalid notes, profile policy, and target bucket
  preview. It does not publish trigger events or write files.
- `POST /api/google/calendar/preview` reuses `CalendarTrigger` normalization
  and Observation conversion to show raw event, normalized event, and
  `GOOGLE_CALENDAR` Observation metadata without committing to L1.5.
- React Source Board consumes both routes. Obsidian scan rows can populate the
  existing Obsidian draft form. Calendar preview shows normalized and
  Observation rows in the card.

## 2026-05-15 Obsidian Import Preview Ledger

Completed in this slice:

- `POST /api/l15/obsidian-vault/import-draft` rescans the vault server-side,
  filters selected relative paths/profiles, converts notes through
  `UserTagFilter`, and returns reviewable events/observations without writing.
- `POST /api/l15/obsidian-vault/import` exists for Web operator testing. It
  defaults to dry-run and only calls `L15Pool.admit` when `operator_mode=true`
  and `dry_run=false`.
- Runtime sync remains separate:
  `ObsidianIngestTrigger -> TriggerOutcome.commit_observations -> L15Pool`.
  The direct `UserTagFilter -> L15Pool.admit` path is Web-only for testing
  source-pack imports without requiring the full Brain/Redis trigger runner.
- React Source Board scan rows now have selection checkboxes and a batch import
  preview button. There is still no casual real-apply button in the UI.

Verification:

- `uv run python -m py_compile src/parrot/web_console/memory_ops.py
  src/parrot/web_console/server.py`
- `uv run pytest tests/test_web_console/test_web_console_server.py -q`
  -> 23 passed.
- `npm run typecheck` in `web/console_app` passed.

Bugfix audit:

- Fixed a Source Board mismatch where the UI auto-selected more Obsidian notes
  than it visibly rendered. Scan now starts with no selection, and the operator
  can explicitly select visible rows.
- Fixed backend import-draft validation so selected paths that are invalid or
  missing return explicit errors instead of being silently ignored.
- Fixed Obsidian Markdown parsing for UTF-8 BOM files. Windows-created notes
  can now still be recognized as frontmatter-bearing import candidates.

2026-05-15 continuation:

- Fixed selected-path/profile filtering so a selected note filtered out by
  `profiles` returns `selected_profile_mismatch` instead of disappearing from a
  successful receipt.
- Fixed selected-path/import-limit interaction so selected notes beyond `limit`
  return `selected_path_over_limit` instead of being misreported as missing.
- Fixed invalid `limit` handling for scan/import-draft. `GET
  /api/l15/obsidian-vault/scan` now passes the raw query value into the Web BFF
  and returns the same `invalid_limit` receipt shape as POST draft routes.

Verification:

- `uv run pytest tests/test_web_console/test_web_console_server.py -q`
  -> 26 passed.
- `uv run python -m py_compile src/parrot/web_console/memory_ops.py
  src/parrot/web_console/server.py`
  -> passed.
- Earlier frontend checks for this source-board slice passed with `npm run
  typecheck` and `npm run build` in `web/console_app`; this continuation changed
  only Web BFF/test/docs.
- Earlier local smoke on `http://127.0.0.1:7893/` confirmed the new BFF routes
  were live; browser smoke clicked Calendar preview and showed normalized /
  Observation sections with no console errors.

## 2026-05-15 Source Board UX Continuation

Completed in this slice:

- Refactored the React Source Board into source tabs (`Graphiti`, `Obsidian`,
  `Google Calendar`, `Manual Node`) so the right drawer shows one active import
  surface instead of stacked dense cards.
- Graphiti search now stores the returned `subgraph.nodes` / `subgraph.edges`,
  supports per-hit selection, shows selected/result graph counts, previews the
  selected subgraph on the React Flow canvas as read-only Graphiti Nodes/Edges,
  and keeps export actions separate from preview actions.
- `Export Draft` stays on `/api/graphiti/subgraph/export-draft`; `Preview Apply`
  calls `/api/graphiti/subgraph/export` with `dry_run=true` and
  `operator_mode=false`. No real L1.5 apply button was added.

Verification:

- `npm run typecheck` in `web/console_app` -> passed.
- `npm run build` in `web/console_app` -> passed.
- Browser smoke on `http://127.0.0.1:7893/` opened the L1.5 Pool dock,
  confirmed Graphiti/Obsidian/Google source tabs, clicked Google Calendar
  import preview, observed receipt/preview content, and found zero console
  errors.
- `uv run pytest tests/test_web_console/test_web_console_server.py -q`
  -> 26 passed.
- Browser smoke on `http://127.0.0.1:7893/` confirmed Source Board tabs,
  Graphiti search surface, and zero console errors.

## 2026-05-15 Memory Toolbar / Edge Surgery Ledger

Completed in this slice:

- Refactored the Memory page so L1.5 Pool / Source Board lives in an explicit
  `Pool` tool dock instead of sharing the selected Node/Edge detail space.
- Replaced the wide canvas form strip with compact icon tools for Node, Edge,
  Subgraph, Filter, Tag, State color, Pool, and Settings. Tooltips explain each
  action without keeping explanatory text permanently on the canvas.
- Added a floating selected Node/Edge inspector on top of the React Flow canvas.
  Node inspection shows status/source/bucket/tag details; Edge inspection shows
  endpoints, kind, strength, source, and raw payload JSON.
- Added visual-only subgraph box previews and simple Node state color markers.
  These are renderer state only; persistent subgraph/cluster DTOs are still
  future candidates after the UI design is reviewed.
- Added Web-only Edge update/delete route coverage. Runtime matching uses
  endpoints plus optional kind/source filters and deliberately does not expose
  RustWorkX edge indexes as Web DTO fields.

RustWorkX / L2-B notes:

- RustWorkX remains the topology engine. Stable business UUIDs are the Web/API
  identity surface for Nodes, while Edge metadata stays in `SemanticEdge`.
- Current Edge data is more than `from` / `to`: it carries `kind`, `strength`,
  `edge_source`, `created_at`, `cross_compartment`, and free-form `meta`.
- If exact parallel-edge surgery becomes necessary, the likely clean path is a
  stable Edge id in `SemanticEdge.meta` or a future typed Edge DTO candidate,
  not leaking RustWorkX internal edge indexes.

Verification:

- `npm run typecheck` in `web/console_app` -> passed.
- `npm run build` in `web/console_app` -> passed.
- `uv run pytest tests/test_web_console/test_web_console_server.py -q`
  -> 26 passed.
- `uv run python -m py_compile src/parrot/dsg/l2b_graph.py
  src/parrot/brain/l2b_monitor.py src/parrot/web_console/memory_ops.py
  src/parrot/web_console/server.py` -> passed.
- Browser smoke on `http://127.0.0.1:7893/` confirmed toolbar tools, Node
  preview, Subgraph preview, Pool dock, and zero console errors.

Bugfix continuation:

- Fixed a UI state collision where the Tag tool reused the Edge `meta` textarea
  state. Tag drafts now use a dedicated tag input state, so switching back to
  Edge no longer sends tag text as invalid Edge meta JSON.
- Replaced the floating inspector close button text with an ASCII `x` after a
  browser smoke caught a mojibake/corrupted close glyph risk.
- Added an L2-B regression test for Edge update/remove through endpoint plus
  kind/source filters, confirming the Web operator path does not rely on
  RustWorkX internal edge indexes.

Verification:

- `npm run typecheck` in `web/console_app` -> passed.
- `npm run build` in `web/console_app` -> passed.
- `uv run pytest tests/test_web_console/test_web_console_server.py -q`
  -> 26 passed.
- `uv run pytest tests/test_dsg/test_l2b_baseline_algorithms.py -q`
  -> 16 passed.
- Browser smoke on `http://127.0.0.1:7893/` confirmed dedicated Tag input,
  Edge meta remained `{}`, close button text was `x`, and console errors were 0.

Filter bugfix continuation:

- Fixed a React Flow rendering bug where Node-kind filters hid Nodes but kept
  Edges whose endpoints were no longer visible. The graph now computes a
  visible Node id set and filters persisted/preview Edges against it before
  passing them to React Flow.
- Fixed a related stale selection bug: when a Filter hides the selected Node or
  Edge, the floating inspector now closes instead of showing details for a
  hidden canvas item.

Verification:

- `npm run typecheck` in `web/console_app` -> passed.
- `npm run build` in `web/console_app` -> passed.
- `uv run pytest tests/test_web_console/test_web_console_server.py -q`
  -> 26 passed.
- Browser smoke created two preview Nodes, drafted one Edge, switched the
  filter to `photo`, and confirmed zero visible Nodes, zero visible Edges, and
  zero console errors.
- Browser smoke created one preview Node, confirmed the floating inspector was
  open, switched the filter to `photo`, and confirmed zero visible Nodes, zero
  visible Edges, zero selection inspectors, and zero console errors.

## 2026-05-15 L2-B Mechanism / Renderer Prep Ledger

Completed:

- Re-read DSG/RustWorkX/L1.5/L2-B/attention/Graphiti skills for the Web
  renderer boundary.
- Audited current backend modules:
  `src/parrot/dsg/l2b_graph.py`, `src/parrot/dsg/l2b_types.py`,
  `src/parrot/dsg/l2b/clustering.py`,
  `src/parrot/dsg/l2b/attention/mechanism.py`,
  `src/parrot/dsg/l2b/views.py`,
  `src/parrot/dsg/l2b/intent_event_boundary.py`, and
  `src/parrot/brain/l2b_monitor.py`.
- Verified official renderer anchors:
  React-Force-Graph for force/canvas monitor rendering, React Flow for editor
  canvases, Obsidian Graph View for filters/groups/display/forces/local graph,
  and D3 force for layout tuning concepts.
- Added `web/console_app/src/graphModel.ts`, a dependency-free adapter from
  `/api/app/live-state` L2-B snapshot data to an engine-neutral graph model.
- Updated `codex_workspace/codex_skills/react-force-graph-l2b/SKILL.md` with
  source notes and the local adapter boundary.

Current conclusion:

- Existing L2-B has more useful fields and algorithms than the current UI
  exposes. The next page should first visualize current `attention`,
  `salience`, `confirmation`, `bucket_id`, `event_id`, `source`, `tags`,
  Edge `kind` / `strength` / `cross_compartment`, and WCC/spreading activation
  results before inventing new DTOs.
- Missing backend capabilities are now explicit: graph health metrics,
  changed-since/SSE/WebSocket deltas, stable Edge id, persistent subgraph or
  cluster model, typed source_meta, PPR, and bounded VF2/isomorphism tools.

Verification:

- `npm run typecheck` in `web/console_app` -> passed after adding the adapter.

## 2026-05-15 Google Calendar Import Preview Ledger

Completed:

- Added Web-only `POST /api/google/calendar/import-draft` and
  `POST /api/google/calendar/import`.
- Both routes reuse `CalendarTrigger` normalization and
  `_event_to_observation`, so Calendar test events preserve calendar id,
  event id, start/end/timezone, link, etag, status, iCalUID, objects, and
  provenance before they become `GOOGLE_CALENDAR` observations.
- The draft route is review-only. The import route defaults to apply preview
  and only calls `L15Pool.admit` when `operator_mode=true` and
  `dry_run=false`.
- React Source Board now exposes Calendar preview, import preview, and safe
  apply preview buttons. Obsidian selected-note import also has an apply
  preview button so operator receipts show the same route that a real import
  would use.

Verification:

- `uv run pytest tests/test_web_console/test_web_console_server.py -q`
  -> 27 passed.
- `npm run typecheck` in `web/console_app` -> passed.
- `npm run build` in `web/console_app` -> passed.

Remaining:

- Replace the synthetic Calendar test event with a real Nanobot/Google
  fetch/preview surface once the Google source-card interaction is approved.
- Add photo/ref source cards and manual Ref bind/unbind/retarget receipts.
- Run a browser smoke after the service serves the rebuilt React dist.

## 2026-05-15 Google Calendar Fetch / Raw Payload Continuation

Completed:

- Added `POST /api/google/calendar/fetch`, a Web-only operator receipt for the
  existing Scheduler -> Nanobot -> Google Workspace MCP `calendar_fetch` path.
  Default mode is dispatch preview; real dispatch requires operator mode.
- React Source Board Google Calendar card now has a `Google/Nanobot JSON`
  textarea. Operators can paste Google API `items`, Nanobot `events`, or
  `calendar_events` payloads and run preview/import-preview through the same
  CalendarTrigger normalization path.
- Backend tests now cover raw Google `items` payload parsing and the
  `calendar_fetch` dispatch guard.

Verification:

- `uv run pytest tests/test_web_console/test_web_console_server.py -q`
  -> 29 passed.
- `uv run python -m py_compile src/parrot/web_console/memory_ops.py
  src/parrot/web_console/server.py` -> passed.
- `npm run typecheck` and `npm run build` in `web/console_app` -> passed.
- Browser smoke on `http://127.0.0.1:7893/` opened L1.5 Pool, selected the
  Google Calendar source tab, confirmed the `Google/Nanobot JSON`,
  `请求获取`, `日程预览`, and `导入预演` controls, clicked fetch preview and
  calendar preview, and found zero console errors.

Remaining:

- Browser smoke the rebuilt dist and then wire a true operator-mode dispatch
  button only after the operator-mode UX is reviewed.
- Add a result-list/history surface for completed `calendar_result` payloads
  once Scheduler/Nanobot result durability is available in the Web read model.

## 2026-05-15 Google Calendar Operator Import Bugfix / Sync Review

Completed:

- Fixed the Web receipt rehydration path so real Google Calendar operator
  imports preserve `observed_at` and `time_span` before `L15Pool.admit`.
  Without this, a Calendar preview showed correct start/end fields but the
  actual L1.5 import could degrade the EVENT Node into a timeless record.
- Added explicit Source Board buttons for operator fetch dispatch and operator
  import to L1.5. They still require the backend route's
  `operator_mode=true` / `dry_run=false` gate and do not put Google OAuth in
  the browser.
- Added route coverage for operator fetch dispatch and operator import temporal
  preservation.

Verification:

- `.venv\Scripts\python.exe -m py_compile src/parrot/web_console/memory_ops.py`
  -> passed.
- `.venv\Scripts\python.exe -m pytest tests/test_web_console/test_web_console_server.py -q`
  -> 31 passed.
- `.venv\Scripts\python.exe -m pytest tests/test_dsg/test_calendar_true_connection.py tests/test_scheduler/test_bt_router.py -q`
  -> 12 passed.
- `npm run typecheck` and `npm run build` in `web/console_app` -> passed.

Architecture conclusion:

- Real Google fetch is a backend/Nanobot concern: Web dispatches
  `calendar_fetch`, Scheduler routes it, Nanobot uses Google Workspace MCP, and
  results return as `calendar_result`.
- Calendar read/sync data should become `GOOGLE_CALENDAR` Observations in the
  L1.5 `google_calendar` bucket, then L2-B EVENT Nodes. It does not need
  IntentWorkspace unless the user/GOSLO is drafting a change, decision, or
  human-in-the-loop plan around that event.
- Official Google Calendar push/watch and incremental syncToken are the right
  backend realtime upgrade path. Web should consume a bounded result/history or
  memory-runtime change stream, not browser-held OAuth.

Remaining:

- Add durable Scheduler/Nanobot result receipts for completed `calendar_result`
  payloads.
- Add server-side Google Calendar watch/syncToken state only after the credential
  storage/renewal policy is reviewed.
- Decide whether Calendar sync deltas should be exposed through CORE-009
  changed-since first or jump directly to SSE/WebSocket for the Web monitor.

## 2026-05-15 Google Calendar Mapping Rows Continuation

Completed:

- Added Web-only `mapping_rows` to Calendar preview/import receipts. The rows
  explain raw Google/Nanobot event identity, target L1.5 bucket, L2-B Node kind,
  merge key, provider Ref key, and IntentWorkspace policy.
- React Source Board now renders a compact mapping preview so operators can see
  why a Google event becomes an L1.5 `google_calendar` item and then an L2-B
  EVENT update, instead of guessing from raw JSON.
- Cancelled/deleted events are not silently applied as normal updates in the
  preview. This slice originally left them as a pending policy row; the later
  WEB-014.15 continuation below resolves them as historical tombstone EVENT
  Nodes.

Verification:

- `.venv\Scripts\python.exe -m py_compile src/parrot/web_console/memory_ops.py`
  -> passed.
- `.venv\Scripts\python.exe -m pytest tests/test_web_console/test_web_console_server.py -q`
  -> 32 passed.
- `npm run typecheck` and `npm run build` in `web/console_app` -> passed.
- Browser smoke found the running 7893 backend was still the old process. After
  restarting `src/scripts/start_web_console.py`, Calendar preview showed
  `映射预览`, `google_calendar -> L2-B event / upsert_event`, and
  `not_used_for_read_sync` with no visible error pill.

Remaining:

- Add durable Scheduler/Nanobot result receipts for completed real
  `calendar_result` payloads.
- Resolve WEB-014.15 before promoting Calendar deletion semantics into a shared
  interface.

## 2026-05-15 Calendar Result Ledger Continuation

Completed:

- Added a bounded Scheduler-owned `STREAM_TRIGGER_RESULTS` ledger. When
  Scheduler fans a Nanobot result to `CH_TRIGGER_RESULTS`, it also writes a
  recent-history stream row containing the trigger payload, result channel,
  task id, and timestamp.
- Added Web-only `GET /api/google/calendar/results`, filtering that ledger for
  `calendar_result` rows and returning secret-redacted summaries, event counts,
  and small event samples.
- React Source Board Google Calendar card now has a `结果记录` button. This lets
  operators inspect recent `calendar_fetch -> calendar_result` returns without
  pretending that Pub/Sub itself is durable.

Verification:

- `.venv\Scripts\python.exe -m py_compile src/parrot/scheduler/service.py
  src/parrot/web_console/memory_ops.py src/parrot/web_console/server.py
  src/parrot/shared/constants.py` -> passed.
- `.venv\Scripts\python.exe -m pytest tests/test_scheduler/test_bt_router.py
  tests/test_web_console/test_web_console_server.py -q` -> 45 passed.
- `.venv\Scripts\python.exe -m pytest tests/test_dsg/test_calendar_true_connection.py -q`
  -> 2 passed.
- `npm run typecheck` and `npm run build` in `web/console_app` -> passed.
- Browser smoke after restarting 7893 confirmed the `结果记录` button renders,
  offline Redis/Scheduler/Nanobot state shows a friendly unavailable message,
  no raw `ConnectionError` is visible, and no visible error pill is present.

Remaining:

- Add Google `watch`/syncToken storage only after credential renewal and webhook
  ownership are reviewed.

## 2026-05-15 Calendar Tombstone Policy Continuation

Completed:

- Resolved WEB-014.15 as a Web-first backend policy: Google `cancelled`,
  `canceled`, and `deleted` rows become historical tombstone EVENT Nodes.
- `CalendarTrigger` still emits a `GOOGLE_CALENDAR` Observation so the normal
  `TriggerOutcome -> L15Pool.admit -> IngestRunner` path is preserved. The
  Observation carries `calendar_lifecycle`, `is_tombstone`, and
  `tombstone_policy=historical_event`.
- `IngestRunner` now merges the tombstone by stable provider identity and
  lowers the existing L2-B Node to `GHOST`, `PERIPHERAL`, and low attention
  instead of evicting it by default.
- The Web mapping receipt now reports `mark_historical_tombstone` instead of
  the earlier pending-policy placeholder.

Verification:

- `.venv\Scripts\python.exe -m py_compile src\parrot\dsg\triggers\calendar_trigger.py
  src\parrot\dsg\ingest\runner.py src\parrot\dsg\ingest\base.py
  src\parrot\web_console\memory_ops.py` -> passed.
- `.venv\Scripts\python.exe -m pytest tests\test_scheduler\test_bt_router.py
  tests\test_web_console\test_web_console_server.py
  tests\test_dsg\test_calendar_true_connection.py -q` -> 48 passed.
- `npm run typecheck` and `npm run build` in `web/console_app` -> passed.

Remaining:

- Add Google `watch`/syncToken storage only after credential renewal and webhook
  ownership are reviewed.
- Add an explicit Web operator repair action later if users need manual
  Calendar EVENT eviction; default sync should keep the reconciliation anchor.

## 2026-05-15 Memory Changed-Since Continuation

Completed:

- Added Web-only `src/parrot/web_console/memory_live_state.py` and mounted
  `GET /api/memory/live-state/changes?since=...&limit=...`.
- The route wraps the existing `/api/app/live-state` builder but maintains a
  separate stable content sequence for Memory Graph polling. No-op reads return
  `changed=false` and omit the full snapshot.
- The stable signature ignores root transport noise while preserving nested
  business fields, so future Blackboard/Ref/Node payloads can safely carry
  their own sequence-like values.
- React Memory now refreshes through this changed-since route. Runtime Flow
  keeps using its own `/api/runtime/flow/changes`.
- TODO, Web README, Memory business flow, and CORE-009 candidate notes were
  updated in-place. No new scattered docs were created.

Verification:

- `.venv\Scripts\python.exe -m py_compile src\parrot\web_console\memory_live_state.py
  src\parrot\web_console\server.py` -> passed.
- `.venv\Scripts\python.exe -m pytest tests\test_web_console\test_web_console_server.py -q`
  -> 35 passed.
- `.venv\Scripts\python.exe -m pytest tests\test_web_console\test_web_console_server.py
  tests\test_scheduler\test_bt_router.py tests\test_dsg\test_calendar_true_connection.py -q`
  -> 49 passed.
- `npm run typecheck` and `npm run build` in `web/console_app` -> passed.
- Secret scan for the previously provided DeepSeek key and
  `PARROT_ORCH_SECRET` value under `src`, `web`, `codex_workspace`, `.cursor`,
  and `tests` -> no matches.
- Restarted the stale 7893 Web Console process, confirmed
  `/api/memory/live-state/changes` returns `changed=true` on first read and
  `changed=false` / `snapshot=null` on a no-op follow-up.
- In-app browser smoke on `http://127.0.0.1:7893/` found Memory title,
  realtime/refresh controls, and zero console errors.

Remaining:

- SSE/WebSocket remains a later WEB-013 transport upgrade; do not call this
  fully realtime yet.

## 2026-05-15 Graphiti Export Plan Continuation

Completed:

- Hardened Graphiti search and subgraph search route input: bad `limit` values
  now fall back to bounded defaults instead of causing route-level 500s.
- Extended `/api/graphiti/subgraph/export-draft` and dry-run
  `/api/graphiti/subgraph/export` receipts with `subgraph`, `edge_drafts`, and
  `edge_write_policy`.
- `edge_drafts` describe Graphiti source/target/fact intent only. They do not
  pretend to be persisted L2-B Edges; the policy remains L1.5 observations
  first, then a later operator-gated edge write after L2-B UUIDs are resolved.
- React Source Board Graphiti card now displays an inline Export plan with
  L1.5 observation count, Edge draft count, selected observation labels, and
  source/target Graphiti UUID pairs.
- Replaced the Graphiti count separator with ASCII `/` so the small status line
  does not render odd punctuation in Chinese/English UI.

Verification:

- `.venv\Scripts\python.exe -m py_compile src\parrot\brain\graphiti_console.py
  src\parrot\web_console\server.py` -> passed.
- `.venv\Scripts\python.exe -m pytest tests\test_web_console\test_web_console_server.py -q`
  -> 35 passed.
- `.venv\Scripts\python.exe -m pytest tests\test_web_console\test_web_console_server.py
  tests\test_scheduler\test_bt_router.py tests\test_dsg\test_calendar_true_connection.py -q`
  -> 49 passed.
- `npm run typecheck` and `npm run build` in `web/console_app` -> passed.
- Actual secret scan for the previously provided DeepSeek key and
  `PARROT_ORCH_SECRET` value under `src`, `web`, `codex_workspace`, `.cursor`,
  and `tests` -> no matches. The test suite still keeps a fake
  `deepseek-export-secret` string to assert redaction.
- Restarted 7893, API-smoked Graphiti `export-draft` with one hit:
  `edgeDrafts=1`, `edgePolicy=requires_resolved_l2b_node_uuid`,
  `directFalkor=false`.
- API-smoked bad-limit `/api/graphiti/subgraph/search`; it returned a normal
  `graphiti.subgraph.search` receipt with `arknights_test` subgraph metadata
  instead of a route exception.
- In-app browser smoke opened the L1.5 Pool tool and confirmed the Graphiti
  tab/Export controls are visible with zero console errors.

Remaining:

- Future edge materialization still needs a reviewed L2-B UUID resolution and
  operator-gated Edge write flow; keep it out of shared DTOs for now.

## 2026-05-15 Obsidian Import Plan Continuation

Completed:

- React Source Board Obsidian card now stores the latest batch import receipt
  as a readable Import plan instead of relying on the right-side raw receipt
  rail only.
- The Import plan displays selected ready count, issue count, target L1.5
  bucket, `bind_policy`, Observation source/kind/tags, source note path, and
  explicit selected-note errors.
- The implementation consumes existing `/api/l15/obsidian-vault/import-draft`
  and dry-run `/api/l15/obsidian-vault/import` receipt fields. It does not
  change the backend write boundary: direct operator import remains Web-only
  and goes through `UserTagFilter -> L15Pool.admit(USER_TAG_OBSIDIAN)`, while
  runtime sync remains `ObsidianIngestTrigger -> TriggerOutcome`.
- Added small visual distinction for import-ready rows and error rows so the
  Source Board is less JSON-heavy.

Verification:

- `npm run typecheck` in `web/console_app` -> passed.
- `npm run build` in `web/console_app` -> passed and refreshed
  `web/console_dist`.
- `.venv\Scripts\python.exe -m pytest tests\test_web_console\test_web_console_server.py -q`
  -> 35 passed.
- In-app browser smoke on `http://127.0.0.1:7893/`: opened L1.5 Pool ->
  Obsidian, scanned a temporary two-note vault, selected visible notes, clicked
  import draft, confirmed Import plan shows daily/roleplay target buckets and
  `UserTagFilter`, with zero console errors. Temporary vault was deleted after
  the check.

Remaining:

- Photo/ref source cards and a less crowded final Source Board layout are still
  open under WEB-014.6 / WEB-014.11.

## 2026-05-15 Ref / Photo Source Card Continuation

Completed:

- Added Web-only `POST /api/refs/binding/draft`.
- The route validates `ref_id`, `target_kind`, and `target_id`, returns the
  current Brain `RefBinding` when it exists, and marks the receipt with
  `core_candidate=CORE-006`.
- The route is deliberately draft-only. It documents the future write path
  `RefBindingRegistry.resolve_ref(ref_id, target_kind, target_id)` but exposes
  no apply route until the shared RefBinding API and App-safe subset are
  reviewed.
- Added a React Source Board `Refs/Photos` tab. It summarizes session
  RefBindings, resolved L2-B targets, IntentWorkspace PHOTO refs, and L2-B
  Photo Nodes from live-state, then lets an operator draft a target retarget
  receipt.
- 2026-05-15 bugfix: `target_kind=unresolved` no longer reports as a successful
  durable resolution preview. The receipt now marks `operation=unresolve_ref`,
  `would_resolve=false`, and `would_unresolve=true`; this keeps clear/unbind
  previews auditable while CORE-006 is still candidate-only.
- 2026-05-15 UI bugfix: the `Refs/Photos` tab now includes session PHOTO
  RefBindings as photo rows in addition to IntentWorkspace PHOTO refs and L2-B
  Photo Nodes.
- 2026-05-15 selected Node detail continuation: the React floating Node
  inspector now renders a read-only `Refs / Photos` section for matching
  RefBinding rows, IntentWorkspace refs, and Photo Node asset/episode metadata.
  This is a renderer/read-model improvement only; bind/unbind/apply remains
  blocked on CORE-006 review.
- 2026-05-15 photo thumbnail continuation: added read-only
  `GET /api/photos/asset/{day}/{photo_id}` to the Web BFF. It resolves only
  under `PARROT_PHOTO_CACHE_ROOT`, accepts `.jpg` or extensionless ids, validates
  the day/photo id, and returns `no-store` JPEG previews. React maps existing
  `/upload/photo/...` refs or cache paths into this route for selected Node and
  Source Board thumbnails without exposing local file paths to the browser.
- 2026-05-15 thumbnail bugfix: the frontend preview URL detector is intentionally
  narrow. It only maps `/upload/photo/`, `/photos/`, or `.jpg` paths so dated
  Obsidian/Markdown paths are not accidentally requested as image thumbnails.

Verification:

- `.venv\Scripts\python.exe -m py_compile src\parrot\web_console\memory_ops.py
  src\parrot\web_console\server.py` -> passed.
- `.venv\Scripts\python.exe -m pytest tests\test_web_console\test_web_console_server.py -q`
  -> 36 passed after the unresolved-target regression assertion.
- `npm run typecheck` and `npm run build` in `web/console_app` -> passed after
  the source-card merge fix.
- In-app browser smoke opened L1.5 Pool -> Refs/Photos, clicked `Preview
  binding` with no `ref_id`, confirmed the `Ref draft plan` / `missing_ref_id`
  UI and `CORE-006` marker, with zero console errors.
- Secret scan for the DeepSeek key and `PARROT_ORCH_SECRET` under
  `src`, `web`, `tests`, `.cursor`, and `codex_workspace` returned no matches.
- 2026-05-15 continuation: `npm run typecheck`, `npm run build`, and
  `tests/test_web_console/test_web_console_server.py -q` still pass after the
  selected Node inspector update. Browser smoke created a preview Node, opened
  `Node 详情`, found the delete action, and reported zero console errors.

Remaining:

- Add reviewed bind/unbind/apply policy only after CORE-006 is confirmed.
- Connect selected Node detail badges to bound Ref/file/photo rows.

Latest verification:

- 2026-05-15 thumbnail continuation:
  `tests/test_web_console/test_web_console_server.py -q` -> 37 passed,
  including cache-root photo asset safety. `npm run typecheck`,
  `npm run build`, in-app browser reload smoke, and frontend/backend secret
  scan passed.
