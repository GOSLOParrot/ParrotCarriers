# Graphiti Management Business Flow (2026-05-13)

Owner chat: Web Console
Status: in_progress
Category: Web Console business interface
Scope: Graphiti/FalkorDB read, search, partitions, visualization, Episode, Graphiti API surgery, FalkorDB operator mode
Updated: 2026-05-13
Related TODO: WEB-006; WEB-007 through shared Ref/Edge rendering boundaries
Sources: `src/parrot/brain/graphiti_console.py`, `src/parrot/brain/app_monitor_server.py`, `src/parrot/memory/graphiti_client.py`, Graphiti skill, DSG L2-B skills

## Slice: Graphiti Console Management

### Implementation Signal 2026-05-13

- `src/parrot/web_console/server.py` now mirrors the existing monitor-safe
  Graphiti routes: `/api/graphiti/status`, `/api/graphiti/search`,
  `/api/graphiti/episode/draft`, and `/api/graphiti/episode`.
- `web/console/` now has a dedicated Graphiti view with dependency/config
  status, partition chips, scoped search result cards, Episode draft, and
  dry-run write preview.
- The Web UI still does not expose FalkorDB direct writes or irreversible
  Graphiti node/edge surgery. Those remain blocked on explicit operator mode,
  backup/export, audit logging, and rollback posture.
- A language bug discovered during Web QA was fixed at the same time:
  `lineb.profile` and `canvas.refs` are no longer swapped between English and
  Chinese dictionaries.
- Related memory-event boundary work now exists outside this Graphiti file:
  Trigger Lab and L1.5/L2-B operator drafts produce dry-run receipts before
  publishing to `CH_DSG_EVENTS` or applying L1.5/L2-B writes. Future Graphiti
  API node/edge/fact surgery should reuse the same receipt posture before any
  durable memory mutation.

### Implemented Interface Matrix

Checkpoint: 2026-05-13. This is the implemented safe seed for Graphiti
management; it is not the full FalkorDB/operator surgery surface.

| Endpoint | Purpose | Backend owner | Safety rule |
|:--|:--|:--|:--|
| `GET /api/graphiti/status` | Dependency/config/partition status. | `graphiti_status()` | Read-only. |
| `POST /api/graphiti/search` | Partition-scoped semantic search. | `search_graphiti()` | Read-only search; bounded limit. |
| `POST /api/graphiti/episode/draft` | Preview an Episode payload. | `draft_episode()` | Draft only; no durable write. |
| `POST /api/graphiti/episode` | Add an Episode through Graphiti. | `add_episode()` | Dry-run remains default; real write must be explicit operator action. |

Investigation note:

- The next Web memory-rendering pass should not start with raw FalkorDB
  controls. L2-B/Blackboard/IntentWorkspace visual usefulness is the immediate
  gap; Graphiti surgery should wait for backup/export, allowlisted mutation
  templates, and audit receipts.

### A. Source Readback

- `src/parrot/brain/graphiti_console.py` already separates status, search,
  draft, and explicit episode writes. It defaults write paths to dry-run.
- `src/parrot/brain/app_monitor_server.py` exposes monitor endpoints:
  `/api/graphiti/status`, `/api/graphiti/search`,
  `/api/graphiti/episode/draft`, and `/api/graphiti/episode`.
- `src/parrot/memory/graphiti_client.py` owns the Graphiti client and partition
  constants (`goslo`, `maid`, `scene`, `user`).
- `src/parrot/dsg/l2b_graph.py` and the DSG interfaces already bridge L2-B and
  Graphiti for preload/search/archive use cases.
- `Interface/obsidian_true_connection_guide_20260509.md` is the boundary rule:
  UI and source integrations should not bypass L1.5/L2-B/ref flows to mutate
  Graphiti directly.
- Graphiti itself is not read-only. Official Graphiti docs describe node/edge
  CRUD, hard delete, and manual fact-triple writes. FalkorDB also supports
  openCypher queries and ships a browser UI for graph visualization and query
  management.

### B. Existing Core Interfaces

The first Web console version can be built from existing Web/business adapters,
then expanded into controlled surgery:

- Observe: status/config/dependency/partition visibility from
  `graphiti_status()`.
- Query: partition-scoped `search_graphiti(query, partition, limit)`.
- Draft: `draft_episode(...)` to preview the exact episode payload.
- Apply: `add_episode(..., dry_run=false)` only behind an operator action; keep
  `dry_run=true` as the default UI path.

This is enough for Web-side inspection and safe manual episode tests. It is the
seed, not the limit.

## Graph Surgery Plan

| Plane | Owner | Use for | Write shape |
|:--|:--|:--|:--|
| Ref management | App + Web | Add/remove/list/resolve refs that point at L2-B nodes, Graphiti UUIDs, episodes, photos, docs, or UI artifacts. | Shared core candidate; narrow DTO; reversible where possible. |
| Graphiti API | Web | Episode writes, node/edge CRUD, fact triples, partition-scoped searches, entity corrections. | Graphiti adapter methods with dry-run, audit record, and operator confirmation. |
| FalkorDB surgery | Web operator | Raw property fixes, label/edge inspection, emergency cleanup, direct Cypher experiments. | Server-side allowlisted Cypher templates first; raw query only in dev/operator mode after backup/export. |

The important split: App gets partial memory surgery through the Ref layer. Web
gets full memory surgery, including Graphiti API operations and FalkorDB
debug/admin tools.

## Last-Seen Decision

Default path: keep `last_seen` as a Graphiti-level semantic write for durable
memory, using the existing `parrot.dsg.interfaces.update_last_seen(...)` pattern
as the seed. It currently writes an episode directly through Graphiti; it does
not need Nanobot in the hot path.

Use this split:

| Case | Preferred path | Why |
|:--|:--|:--|
| Durable “object was seen” memory | DSG/L2-B event -> Graphiti episode/fact | Preserves provenance, partitioning, and future temporal search. |
| High-frequency pose/position updates | Runtime/L2-B state first, summarize to Graphiti | Avoids flooding long-term memory with frame-level noise. |
| Operator repair/backfill | Web FalkorDB surgery | Useful for exact property fixes, but bypasses Graphiti provenance unless Web writes an audit event too. |
| Scheduled audit/report/import cleanup | Nanobot or Scheduler task | Good for monitored background work, not for per-sighting latency. |

Trigger rule: add triggers at the normalized memory-event boundary, not at each
storage implementation. Graphiti writes, FalkorDB repair writes, and future
Nanobot jobs should all emit or record the same audit/trigger envelope. If a
path bypasses Graphiti and writes FalkorDB directly, Web must create the audit
record explicitly.

## Web Feature Set

- Partition browser: `goslo`, `maid`, `scene`, `user`, plus counts and recent
  episodes/entities/edges.
- Search: semantic Graphiti search and FalkorDB/Cypher query result rendering.
- Visual graph: node/edge canvas from selected query results, with label/type
  filters, inspect drawer, and ref badges.
- Episode management: list/search/add/draft; update/delete only with provenance
  warnings because episodes are source history.
- Entity/edge management: create/update/delete entity nodes and entity edges
  through Graphiti classes where possible.
- Fact triples: add a source node, target node, and relationship/fact using
  Graphiti `add_triplet`.
- Ref surgery: add/cancel/retarget refs between App artifacts, L2-B nodes,
  Graphiti UUIDs, episodes, and external files.
- L2-B bridge: show which Graphiti entities/facts are loaded into or linked
  from L2-B; L2-B CRUD stays in the Memory Graph workspace and should emit the
  same audit/trigger envelope when it causes Graphiti-visible changes.
- Trigger management: manual fire/manage belongs at the normalized memory-event
  boundary. Graphiti writes, L2-B corrections, and FalkorDB repairs should use
  comparable draft/audit records.
- FalkorDB tools: connect to FalkorDB Browser when available; expose a safer
  in-console query panel for allowlisted `MATCH`/`RETURN`/limited `SET`/`DELETE`
  workflows.
- Evidence/String Board: Web can render a board-style graph for memory surgery,
  but it should consume the same Ref/edge DTO as App instead of inventing a
  separate storage format.

### C. Missing Core Surface

No new core surface is required for a Web-only Graphiti/FalkorDB operator panel.

Promote a candidate to `../core_interface_candidate_queue_20260513.md` only if
another lane needs the same contract. Likely future candidates:

| Candidate | Promote only if | Notes |
|:--|:--|:--|
| `GraphitiStatusSnapshot` | Unity HUD or Scheduler also needs memory health. | Keep read-only and coarse. |
| `MemoryWriteDraft` | App and Web both need the same draft/approval flow. | Should produce episodes or IntentWorkspace drafts, not raw graph mutation. |
| `MemoryCorrectionDraft` | Node merge/alias/correction becomes shared. | Route through L1.5/L2-B/ref binding first. |
| `MemoryRefBindingApi` | App and Web both need add/remove/retarget refs. | This is the main shared candidate; App should use this instead of raw Graphiti/FalkorDB writes. |

Direct entity/node CRUD against Graphiti or FalkorDB can be implemented, but it
stays Web-operator only until there is a backup, dry-run, audit log, and
rollback story.

### D. Observable Completion Signal

- Web shows Graphiti dependency/config status and available partitions.
- Web can search a selected partition and render result rows without writing.
- Web can generate an episode draft and compare it with dry-run output.
- A real write requires an explicit operator action and returns the written
  episode metadata or a clear failure message.
- Web can add/delete/retarget a Ref and App can consume the same Ref snapshot.
- Web can run Graphiti API-level create/update/delete on a test partition with
  audit output.
- Web can open or link to FalkorDB Browser for raw graph inspection, and can
  render a selected query result in its own canvas.
- Node correction flows generate drafts or ref/L2-B actions first unless the
  user deliberately enters operator surgery mode.
- `last_seen` live updates do not spam durable memory; durable Graphiti writes
  are batched or semantic, and direct FalkorDB writes carry explicit audit.
