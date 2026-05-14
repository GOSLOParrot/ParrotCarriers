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
- `uv run pytest tests/test_web_console/test_web_console_server.py -q`
  -> 26 passed.
- Browser smoke on `http://127.0.0.1:7893/` confirmed Source Board tabs,
  Graphiti search surface, and zero console errors.
