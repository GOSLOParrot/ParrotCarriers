# GOSLO Laptop Tooling Status - 2026-05-18

## Stable Requirement Notes

- GOSLO mostly decides and speaks; it should not do long work inside the live
  turn unless the tool is a bounded T1/Intent read.
- Nanobot/Scheduler owns background work: research, Gmail/message checks,
  reminders, Calendar worker routes, and slow MCP/API calls.
- L1.5/L2-B/Graphiti are memory projections and audit/context buffers, not the
  SSOT for Google Calendar, Gmail, or reminder execution.
- `identify_object` is disabled for the laptop test lane until the visual
  evidence path is ready again. Re-enable only with
  `PARROT_ENABLE_IDENTIFY_OBJECT_TOOL=1`.

## Tool Set Kept For GOSLO

- `web_lookup_intent`: T1 grounded web lookup with T3 research fallback.
- `dispatch_task`: generic non-blocking Scheduler/Nanobot dispatch.
- `calendar_context`: T1 Google Calendar read/preview with T3 fallback.
- `calendar_change_request`: Intent/Plan/HITL Calendar mutation draft only.
- `calendar_task_status`: bounded Calendar task/result monitor.
- `message_check_request`: T3 Gmail/Workspace check request through Nanobot; no
  Gmail writes and no memory mutation in the tool call itself.
- `reminder_request`: T3 reminder/proactive follow-up request through Nanobot;
  not a Google Calendar write.
- `query_memory`: T1 Graphiti natural-language retrieval fixed to
  `laptop_profile_test` for this test lane. It can block live dialogue, so GOSLO
  should use it only when the user explicitly asks to check memory/knowledge or
  the current decision needs this test knowledge base.
- `query_etiquette_memory`: noble etiquette Graphiti test partition query.

## Laptop Graphiti Test Partition

`PARTITIONS.LAPTOP_PROFILE_TEST = "laptop_profile_test"` is isolated from
`goslo`, `user`, and earlier corpus partitions. Seed script:

```bash
.venv/Scripts/python.exe src/scripts/import_laptop_profile_to_graphiti.py --apply
```

Seed facts:

- 用户的笔记本电脑是联想拯救者。
- 用户的鼠标是 Logitech G504 / 罗技 G504。
- 用户喜欢的饮料是杨枝甘露 / mango pomelo sago。

Use `query_memory(query="用户喜欢什么饮料？鼠标是什么？")` or the Web
`/api/graphiti/subgraph/search` route with `partition=laptop_profile_test` to
verify true retrieval.

Additional text seeded during the laptop smoke test should be plain natural
language, not over-modeled. Repeating important aliases helps Graphiti extract
stable facts:

- 联想拯救者 / Lenovo Legion laptop
- Logitech G504 / G504 mouse / 罗技 G504 鼠标
- 杨枝甘露 / mango pomelo sago

2026-05-18 true smoke:

- `laptop_profile_test` Graphiti writes succeeded through the real
  app-monitor `/api/graphiti/episode` route.
- `/api/graphiti/subgraph/search` returned real hits for favorite drink,
  mouse, and laptop facts.
- Container-side `query_memory` returned real Graphiti node/edge counts.
- Host `.venv` does not currently include `graphiti_core`; use the Web route or
  a container with the `memory` extra for true Graphiti calls.

## Laptop Ref / File Sandbox

Laptop ECS parity now includes a safe local `/data/workshop` equivalent:

- Host sandbox root:
  `codex_workspace/local_runtime/castle_laptop/workshop`
- Container paths:
  `/data/workshop/photos`, `/data/workshop/documents`,
  `/data/workshop/sorted`, `/data/workshop/refs`
- Photo cache remains canonical at `/app/data/photos`, and the same local photo
  directory is also exposed as `/data/workshop/photos` for ECS-style path
  tests.
- IdentityRefIndex persists in local backend runtime at
  `/app/data/registries/memory_identity_ref_index.json`, mapped to
  `codex_workspace/local_runtime/castle_laptop/data/registries`.

The laptop app-monitor now exposes the CORE-015 routes used by the ReactFlow
Console:

- `GET /api/memory/identity-ref-index`
- `POST /api/memory/identity-ref-index/apply`
- `POST /api/memory/identity-ref-index/ref-scan-dispatch`
- `GET /api/memory/identity-ref-index/ref-scan-results`

2026-05-18 true smoke:

- A sandbox file was registered through app-monitor
  `/api/memory/identity-ref-index/apply`.
- RefScan was dispatched through app-monitor
  `/api/memory/identity-ref-index/ref-scan-dispatch`.
- The running Scheduler/Nanobot path returned a structured
  `memory_ref_scan_result` with `ref_result_count=1`, `local_path_exists`, and
  `health=ok`.
- Bug fixed: sibling Nanobot `parrot_bus` now handles `ref_scan`
  deterministically instead of letting the LLM return prose. Calendar/Gmail and
  research tasks still use normal Nanobot agent/MCP behavior.

## Laptop Obsidian / Source Board

The ReactFlow Console can now use Source Board Obsidian routes when its backend
target is the laptop app-monitor at `http://127.0.0.1:18790`:

- `GET /api/l15/obsidian-vault/scan`
- `POST /api/l15/obsidian-vault/import-draft`
- `POST /api/l15/obsidian-vault/import-plan`
- `POST /api/l15/obsidian-vault/import`
- `POST /api/l15/obsidian-node/draft`
- `POST /api/l15/obsidian-node`
- `GET /api/photos/asset/{day}/{photo_id}`

Operational boundary:

- Scan/import-draft/import-plan are safe review surfaces.
- Real import still requires explicit operator mode and should be treated as a
  memory projection into L1.5/L2-B, not as the final SSOT for external files.
- Photo assets are read-only and constrained to `PARROT_PHOTO_CACHE_ROOT`.

2026-05-18 true smoke:

- A test note in `/data/workshop/documents/obsidian_smoke` scanned through the
  real app-monitor container with `vault.status=ingest_ready`.
- Import draft and import plan both succeeded through `:18790`, returning one
  selected note and the apply route `/api/l15/obsidian-vault/import`.
- The app-monitor photo asset route returned HTTP 200 for a sandbox photo.

## ReactFlow Canvas Stability

2026-05-18 drag-empty bug fix:

- Symptom: after Graphiti/L2-B import, dragging a visible Node could leave the
  canvas visually blank while the header still reported non-zero L2-B
  `node_count`/`edge_count`.
- Likely cause: ReactFlow occasionally reports an abnormal flow position during
  controlled-node dragging. Saving that outlier into `manualPositions` expands
  the graph bounds and makes `fitView` zoom/pan as if the real graph were far
  outside the visible working area.
- Fix: `web/console_app/src/App.tsx` now rejects single-node position jumps
  above a bounded threshold, tightens the maximum saved flow coordinate, and
  ignores stale manual positions that are too far from the generated layout.
- Validation: `npm run typecheck` and `npm run build` passed; `:7894` still
  serves the React Console.

2026-05-18 count-only snapshot hardening:

- Web BFF now exposes `GET /api/l2b/snapshot` and proxies it to the configured
  laptop app-monitor/ECS target with server-side bearer auth.
- If a remote live-state response reports non-zero L2-B `node_count` but carries
  an empty `nodes` array, the BFF hydrates the `l2b` payload from
  `/api/l2b/snapshot` before ReactFlow sees it. This prevents count-only
  transient snapshots from clearing the controlled canvas.
- True write smoke through `:7893` succeeded after restart: two operator L2-B
  nodes and one edge were proxied into laptop app-monitor; `:7893` live-state
  and `/api/l2b/snapshot` both returned `2 node(s) / 1 edge`.
- Graphiti -> L2-B true import smoke also succeeded through `:7893`:
  `laptop_profile_test` natural-language search returned `4 hit(s)`,
  `9 subgraph node(s)`, `4 subgraph edge(s)`, and
  `/api/graphiti/subgraph/materialize-l2b` wrote `11 node(s)` plus
  `14 edge(s)` into L2-B. Live-state then returned `13 node(s) / 15 edge(s)`.
- Validation: `tests/test_web_console/test_web_console_server.py -q`,
  `py_compile src/parrot/web_console/server.py`, `npm run typecheck`, and
  `npm run build` passed.
- `infra/laptop-castle.ps1 -Action status` shows Redis, FalkorDB, LiveKit,
  token-mint, app-monitor, orchestrator, scheduler, nanobot-worker, and brain
  containers up. `:17889/health` remains unavailable until a Unity/LiveKit room
  job activates the Brain photo/live-state server; app-monitor is the stable Web
  target before a room exists.

## Laptop Connection Targets

- Web BFF: `http://127.0.0.1:7893`
- React Console: `http://127.0.0.1:7894/index.html`
- Laptop app-monitor / Graphiti owner: `http://127.0.0.1:18790`
- Laptop LiveKit: `ws://127.0.0.1:17880`
- Laptop orchestrator: `http://127.0.0.1:17890`
- Laptop stack operator: `infra/laptop-castle.ps1`

The Web Console profile should be `laptop`; the browser should never hold
Google OAuth tokens or raw Nanobot credentials.

Operational notes:

- Start core laptop backend:
  `.\infra\laptop-castle.ps1 -Action up`
- Start Brain + Scheduler + Nanobot worker:
  `.\infra\laptop-castle.ps1 -Action up-brain`
- Start optional GOSLO chat body:
  `.\infra\laptop-castle.ps1 -Action up-chat`
- `goslo-chat` is optional until `TELEGRAM_BOT_TOKEN` is present.
- Nanobot verbose logs are disabled by default after the 2026-05-18 Gmail
  smoke found that verbose LLM/MCP logs can include private message metadata.
