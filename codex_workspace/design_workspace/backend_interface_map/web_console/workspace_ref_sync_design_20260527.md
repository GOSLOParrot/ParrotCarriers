# Workspace Ref Sync Design Note (2026-05-27)

Owner: Web Console / DSG memory line
Status: first_backend_slice
Scope: IntentWorkspace, nanobot workspace scope, IdentityRefIndex, L2-B pointer nodes, large local/remote refs

## Existing Archive Found

The previous research/design line already exists and should stay the durable
anchor:

- `graphiti_l2b_ref_identity_design_20260517.md`
- `_tmp/graphiti_l2b_ref_identity_workplan_20260517.md`
- `graphiti_l2b_longline_review_20260517.md`
- `memory_graph_workspace_business_flow_20260513.md`

The conclusion from those notes still stands:

- Graphiti owns temporal memory, facts, entities, episodes, and provenance.
- L2-B owns fast runtime pointer topology and algorithm/view edges.
- RustWorkX integer indices are process-local handles, never durable identity.
- IdentityRefIndex / future IdentityBinding owns UUID equivalence.
- RefIndex / ExternalRefRecord owns mutable file, URL, ECS, Obsidian, Google,
  photo, and large-file locators.
- Nanobot scans/checks/proposes repairs; git records reviewable manifest
  deltas; Web/operator receipts apply changes.

## File Tracking

| File | Status | Purpose |
|:--|:--|:--|
| `src/parrot/dsg/workspace_ref_sync.py` | exploratory backend helper | Draft/apply helper for syncing one locator into IntentWorkspace, IdentityRefIndex, and L2-B pointer topology. |
| `tests/test_dsg/test_workspace_ref_sync.py` | focused coverage | Proves large-file hash deferral, operator apply, scoped IntentWorkspace staging, RefIndex write, L2-B pointer node, and `HAS_REF` edge behavior. |
| `codex_workspace/design_workspace/backend_interface_map/web_console/workspace_ref_sync_design_20260527.md` | tracking note | This explanation and continuation anchor. |
| `codex_workspace/design_workspace/backend_interface_map/web_console/README.md` | lane index | Lists this note in the active Web Console interface index. |

This slice is not a final product route yet. It is intentionally isolated so
it can be reviewed, promoted behind Web routes, or reverted without touching
Graphiti, app-monitor, Unity DTOs, or existing ref-scan routes.

## External Research Update

The external pattern is consistent with our earlier direction:

- Git LFS stores a small pointer in Git and keeps large file content outside
  normal Git blobs: https://git-lfs.com/
- git-annex manages large files with Git while tracking availability across
  online/offline locations: https://git-annex.branchable.com/
- DVC uses Git-adjacent metadata plus external remotes to synchronize large
  files/directories: https://doc.dvc.org/user-guide/data-management/remote-storage
- Google Calendar changes should use service-side push notification plus
  incremental sync tokens; the notification is not the full event body:
  https://developers.google.com/workspace/calendar/api/guides/sync and
  https://developers.google.com/workspace/calendar/api/guides/push
- Obsidian exposes vault/file URI addressing; filesystem path and vault id both
  matter for stable locators: https://obsidian.md/help/uri
- Filesystem watcher libraries can notice moves/changes, but the authoritative
  update still needs a reviewed RefIndex write:
  https://python-watchdog.readthedocs.io/en/stable/

So the plan should remain **nanobot + Git-manifest + RefIndex**, not "Git owns
all large bytes." Git tracks small manifests/pointers. Nanobot runs scans,
hashes, watch/probe jobs, and repair proposals. IdentityRefIndex stores current
locator truth. L2-B receives only the pointer node/edge state.

## Large-File Storage Decision Matrix

| Option | Best fit | Weakness for us | Use in ParrotCarriers |
|:--|:--|:--|:--|
| Plain Git manifest | Reviewable pointer/index diffs, small metadata, easy rollback | Does not store payload bytes | Default MVP. Track `ref_id`, locator, hash, size, provider ids, workspace scope, health, and git commit in small manifests. |
| Git LFS | Team-shared binary assets that should feel like Git files | Less good for many offline disks or multi-location availability reasoning | Optional payload backend for selected stable assets, while RefIndex remains the runtime locator authority. |
| git-annex | "Where is this file?" across many disks/remotes/offline stores | More operational complexity and different user workflow | Strong candidate if nanobot must manage files spread across local drives, ECS, removable disks, and cold storage. |
| DVC | Dataset/model/pipeline-style directories with remote cache | Heavier ML/data workflow assumptions | Use only if the large-file set becomes dataset-versioned or pipeline-produced. |
| Local/ECS object store | Runtime-owned blobs, captures, generated artifacts, cacheable imports | Needs our own manifest, GC, and backup policy | Good for IntentWorkspace/nanobot staging and App/Web generated artifacts. Git stores only manifests. |

Current recommendation:

1. Use plain Git manifests first, plus local/ECS object storage for bytes.
2. Keep `IdentityRefIndex` / future `ExternalRefRecord` as the runtime truth
   for current locators, hashes, health, and provider ids.
3. Add Git LFS only for stable binary assets that the team truly wants inside
   the Git working tree.
4. Re-evaluate git-annex when the main pain becomes physical file availability
   across multiple machines/disks rather than normal asset versioning.

## Current Answer

Use two indexes and one pointer graph:

1. IntentWorkspace is the memory-temporary working set. It stages payload
   handles for the current Brain, Plan, or nanobot actor. Large files are
   staged as `DISK_PATH` or URL handles, not copied into prompt memory.
2. IdentityRefIndex is the durable locator and UUID binding layer. It stores
   current `RefRecord` state: locator list, content hash, health, git commit,
   managed-by policy, canonical UUID, and provider ids.
3. L2-B stores pointer Nodes and `HAS_REF` / source-support Edges. It should
   carry `ref_id`, `canonical_uuid`, `l2b_uuid`, `source_meta`, and raw source
   metadata, but not large payload bytes.

Graphiti Episodes should record history such as "ref moved from A to B" after
review. They should not be the only mutable locator store and should not be
rewritten to hide old paths.

## Completed vs Missing

Completed before this slice:

- Graphiti search/import/materialize path exists and preserves raw
  `graphiti_bundle` data.
- `MemoryIdentityRefIndex` exists as a file-backed prototype with
  `IdentityRecord`, `RefRecord`, merge/conflict policy, verification, Graphiti
  ref write-back, and ref-scan dispatch/result receipts.
- L2-B can materialize Graphiti pointer nodes/edges and read them back through
  context/subgraph routes.
- Nanobot fallback `ref_scan` can stat/hash small local paths and report remote
  locators as explicit `unknown` unless opt-in remote probes are configured.

Completed in this slice:

- One helper can tie a locator to IntentWorkspace, IdentityRefIndex, and L2-B
  pointer topology.
- Large local files are detected and hashing is deferred instead of blocking
  the Brain/Web call.
- Nanobot actor scope is preserved through `owner_id`, so a task can stage its
  own temporary handle without becoming the durable owner.

Still missing:

- No Web route/UI for this helper yet.
- No DB-backed IdentityBinding/RefIndex yet.
- No automatic move/repair apply; nanobot still only proposes through
  `ref_scan`.
- No Git LFS/git-annex/DVC choice has been finalized for actual payload
  storage.
- No Graphiti audit Episode write from this helper yet.
- No general L2-B rebuild-from-RefIndex service after process restart.

## L2-B / Workspace Sync Plan

P0 freeze: Keep this slice as an exploratory helper and tracking note until the
payload-storage policy is chosen. Do not add more automatic code paths.

P1 manifest policy: define the small Git-tracked manifest schema for
`ExternalRefRecord`, including `ref_id`, `canonical_uuid`, locator list,
content hash, size, provider ids, workspace owner, health, git commit,
`managed_by`, and last verified time.

P2 durable schema: split the current prototype names into durable concepts:
`IdentityBinding` for UUID equivalence, `ExternalRefRecord` for mutable
locators, `WorkspacePresence` for IntentWorkspace/nanobot in-memory/disk
staging, and `RefMoveEvent` for approved moves/repairs.

P3 operator route: expose draft/apply only through Web operator receipts. The
route may stage a pointer, write RefIndex, and materialize an L2-B pointer
node/edge, but it must not move files or write Graphiti without explicit flags.

P4 nanobot scanner: let nanobot watch/scan local files, Obsidian vault paths,
Google Calendar deltas, URL heads, ECS objects, and Graphiti UUID lookups. It
writes result ledgers and proposed manifest diffs, not direct locator changes.

P5 reviewed write-back: after operator review, apply RefIndex updates, optionally
emit a Graphiti audit Episode, and update or rebuild L2-B pointer topology from
RefIndex state.

P6 restart/rebuild: implement a DB-backed index and a deterministic
L2-B-from-RefIndex rebuild service. Persist UUIDs and refs, never rustworkx
integer indices.

## Open Decisions

- Whether large payload bytes should stay only in local/ECS object storage, or
  whether selected paths use Git LFS.
- Whether git-annex is worth the workflow cost for multi-disk availability
  tracking.
- The canonical nanobot workspace root and cleanup/GC policy.
- Whether L2-B pointer node UUIDs use `ref:{ref_id}` for now or move directly
  to `canonical_uuid` once IdentityBinding is DB-backed.
- Which reviewed events should write a Graphiti audit Episode immediately and
  which should remain only in RefIndex/manifest history.

## Implemented Slice

Added `src/parrot/dsg/workspace_ref_sync.py`.

The helper exposes:

- `draft_workspace_ref_sync(payload)`
- `apply_workspace_ref_sync(payload, intent_workspace=..., identity_index=..., l2b_graph=...)`

The apply path is operator-gated by convention:

```text
locator
  -> IntentWorkspace staged handle
  -> IdentityRefIndex RefRecord + IdentityRecord
  -> L2-B pointer SemanticNode
  -> optional HAS_REF edge from an existing node to the pointer node
```

It deliberately does not:

- move, copy, delete, or rewrite files;
- write Graphiti/FalkorDB;
- persist rustworkx indices;
- make nanobot the hidden source of truth.

For large local files, the draft records stat metadata and defers hashing to
nanobot/ref-scan when the file exceeds the configured hash cap. This keeps the
Brain path responsive while still making the future hard-disk manifest check
explicit.

## Ownership Table

| Concern | Owner | Current mechanism |
|:--|:--|:--|
| Temporary memory presence | IntentWorkspace | `StagedRef` with owner scope, e.g. `nanobot:task-id` |
| Hard-disk / URL / ECS position | IdentityRefIndex RefRecord | `locators[]`, `content_hash`, `health`, `managed_by`, `git_commit` |
| UUID equivalence | IdentityRefIndex IdentityRecord | `canonical_uuid`, `l2b_uuid`, Graphiti/Obsidian/provider ids |
| Runtime graph state | L2-B | pointer `SemanticNode` and `HAS_REF` edge |
| Background scan/repair proposal | nanobot | `ref_scan` task and result ledger |
| Reviewable manifest history | git | small manifest diffs, not payload storage |
| Provenance/history | Graphiti | audit Episode after reviewed apply |

## Next Step

Promote this helper behind a Web/operator route only after deciding the UI
surface. The obvious route shape is:

```text
POST /api/memory/workspace-ref-sync/draft
POST /api/memory/workspace-ref-sync/apply
```

The route should keep the same dry-run/operator-mode receipt policy used by
IdentityRefIndex and Graphiti materialization. It should also attach the
existing nanobot `ref_scan` dispatch/result route so a staged pointer can be
health-checked and later repaired without direct file mutation.
