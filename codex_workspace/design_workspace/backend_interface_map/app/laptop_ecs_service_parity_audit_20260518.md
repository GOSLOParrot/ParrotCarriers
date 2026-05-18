# Laptop ECS Service Parity Audit - 2026-05-18

This document records the current audit for making the laptop backend cover the
Castle ECS feature surface used by GOSLO, Web Console, LiveKit, Graphiti, Google
Workspace, Scheduler, and Nanobot.

## User Requirement Snapshot

- The laptop environment should cover ECS functions as much as possible.
- Nanobot must work normally on the laptop, not only the direct Web/Graphiti
  APIs.
- Before changing services, fully search and summarize ECS services, audit
  missing pieces, then create a detailed TODO list and complete it step by step.
- The ReactFlow Web Console is the current console. Its laptop profile should
  be able to point at the laptop backend instead of ECS.

## ECS Service Surface

### Docker Compose Services

Source: `infra/docker-compose.yml`.

| Service | ECS port / scope | Role |
| --- | --- | --- |
| `livekit` | `7880`, `7881`, `50000-50200/udp` | LiveKit room/media bus for Unity/App and Brain. |
| `redis` | host-local `6379` | Bus, blackboard, scheduler/nanobot dispatch, heartbeat. |
| `falkordb` | host-local `6380` | Graphiti/FalkorDB graph backend. |
| `token-mint` | `7888` | Phone-facing LiveKit token mint and optional active Brain dispatch. |
| `orchestrator` | profile-gated, `7890` | Dev/container control-plane variant; production path is systemd host process. |
| `brain` | profile-gated | Container variant of Brain; production path currently also has systemd units. |

### Systemd / Host Python Services

Source: `infra/systemd/*.service` and `infra/ecs-release.ps1`.

| Unit | Exec | Role |
| --- | --- | --- |
| `parrot-orchestrator` | `python -m parrot.castle.orchestrator` | Control plane for runtime config, line switch, restart. |
| `parrot-app-monitor` | `python src/scripts/start_app_monitor_server.py --host 0.0.0.0 --port 8790` | App/Web monitor API subset, Graphiti status/search, room setting, operator APIs. |
| `parrot-scheduler` | `python src/scripts/start_scheduler.py` | BT routing, dispatch_task, Nanobot result fan-in, trigger results. |
| `parrot-maid` | `python src/scripts/start_nanobot_worker.py` | Nanobot worker with `parrot_bus` plus optional WeChat. |
| `parrot-goslo-chat` | `python src/scripts/start_goslo_chat.py` | GOSLO Telegram/chat body and mode hook. |
| `parrot-brain` | `python -m parrot.brain.agent start` | LiveKit/Gemini Live Brain agent. |
| `parrot-brain@1/@2` | same with replica suffix | Optional rolling restart pool. |

### Host Dependencies And Runtime State

Source: `infra/deploy-castle.sh`, `start_nanobot_worker.py`,
`start_goslo_chat.py`.

- Python venv at `/opt/parrot/ParrotCarriers/.venv`.
- Sibling Nanobot fork at `/opt/nanobot`, installed with `pip install -e
  /opt/nanobot[parrot]`.
- Node.js/npm/npx for Nanobot MCP servers, especially GitHub MCP and Google
  Workspace MCP.
- Google Workspace OAuth credentials in Nanobot-compatible directories.
- `~/.nanobot/goslo-workspace`, `~/.nanobot/workspace`.
- `/data/workshop/photos`, `/data/workshop/documents`, `/data/workshop/sorted`
  for file/ref workflows.
- Optional `exiftool` for photo metadata sorting.

## Current Laptop Stack

Source: `infra/docker-compose.laptop.yml` and live `docker compose ps`.

Currently running:

| Service | Laptop port / scope | Status |
| --- | --- | --- |
| `redis` | `127.0.0.1:16379` | Running, healthy. |
| `falkordb` | `127.0.0.1:16380` | Running, healthy. |
| `livekit` | `17880`, `17881`, `51000-51200/udp` | Running. |
| `token-mint` | `17888` | Running. |
| `app-monitor` | `18790` | Running. |
| `orchestrator` | `17890` | Running. |
| `brain` | `17889` | Running after `up-brain`, but `/health` may only be useful when the room job is active. |
| `scheduler` | no host port | Added 2026-05-18; running under the `brain` profile. |
| `nanobot-worker` | no host port | Added 2026-05-18; running under the `brain` profile. |
| `goslo-chat` | no host port | Added 2026-05-18 as optional `chat/all` profile; Telegram token is not present on this laptop env yet. |

Currently missing from laptop compose:

- Live Telegram channel for `goslo-chat`, pending `TELEGRAM_BOT_TOKEN`.
- Direct Docker/socket restart adapter; the accepted laptop mode is currently
  explicit operator restart via `infra/laptop-castle.ps1`.

## API Parity Gaps

`src/parrot/web_console/server.py` has the full Google Calendar route set:

- `/api/google/calendar/fetch`
- `/api/google/calendar/results`
- `/api/google/calendar/api-fetch`
- `/api/google/calendar/nanobot-fetch`
- `/api/google/calendar/import-draft`
- `/api/google/calendar/import-plan`
- `/api/google/calendar/import`

`src/parrot/brain/app_monitor_server.py` now exposes the same Calendar route
set plus the CORE-015 IdentityRefIndex/RefScan routes needed by the ReactFlow
Console when it points directly at the laptop app-monitor backend.

Source-board parity status:

- Web BFF exposes `/api/l15/obsidian-vault/*`,
  `/api/l15/obsidian-node*`, and `/api/photos/asset/{day}/{photo_id}`.
- Laptop app-monitor now exposes those routes too, so the ReactFlow Console can
  use Obsidian/Source Board features when pointed directly at
  `laptop / app-monitor`.

## Capability Gap Summary

| Capability | ECS path | Laptop current state | Required action |
| --- | --- | --- | --- |
| LiveKit room/media | `livekit` + `brain` | Mostly present | Keep. Validate room join with App/Web. |
| Token mint | `token-mint` | Present | Keep. |
| Graphiti/FalkorDB | `falkordb` + app-monitor/brain | Present | Keep. Continue true query tests. |
| Web/App monitor | `parrot-app-monitor` | Present; Calendar, Ref, and Obsidian/Source Board route parity added | Keep route parity checks with new Web tools. |
| Scheduler dispatch | `parrot-scheduler` | Present | Keep. |
| Nanobot worker | `parrot-maid` | Present | Keep; structured tasks need deterministic branches where required. |
| Google Workspace through Nanobot MCP | Nanobot + MCP + OAuth | Present for Calendar/Gmail read tests | Keep credentials read-only. |
| Gmail/message check | Scheduler -> Nanobot | Present and true-smoked | Keep privacy logging disabled by default. |
| Reminder/proactive follow-up | Scheduler -> Nanobot/heartbeat-like flow | Worker path present; dedicated reminder smoke still useful | Add later focused reminder smoke. |
| GOSLO Telegram chat body | `parrot-goslo-chat` | Optional service present; external channel pending token | Add `TELEGRAM_BOT_TOKEN` when approved. |
| Orchestrator restarts | systemd restart | External operator restart mode | Keep `laptop-castle.ps1` unless Docker socket adapter is approved. |
| Ref/file management | `/data/workshop`, Nanobot workspace | Safe sandbox mounted and true-smoked | Design writeback/conflict policy before real file mutation. |

## Detailed TODO List

## Mandatory TODO Workflow Gate

Every TODO below must start with a short architecture/module-collaboration
review before implementation. This is a hard workflow rule, not optional polish.

For each TODO, do the following in order:

1. Re-read the relevant user requirement and this audit section.
2. Read the owning modules and entrypoints before editing. Prefer current code
   over stale docs when they conflict.
3. Map the collaboration path: caller, API route/tool, Redis stream/channel,
   worker/service, result channel, and UI/Web surface.
4. Record any discovered drift or missing dependency in this document or a
   linked SSOT note.
5. Only then implement the smallest safe change.
6. Run a true-connection or focused smoke test where feasible.
7. Do a post-change review: requirement fit, route parity, failure behavior,
   and whether dry-run accidentally replaced the real path.

Default pre-study files by area:

| TODO area | Read first |
| --- | --- |
| Scheduler | `src/scripts/start_scheduler.py`, `src/parrot/scheduler/service.py`, `src/parrot/scheduler/nodes.py`, `src/parrot/scheduler/task_catalog.py`, `src/parrot/shared/constants.py` |
| Nanobot worker | `src/scripts/start_nanobot_worker.py`, `src/parrot/bus/nanobot_consumer.py`, sibling `nanobot/config/parrot_config.json`, `.cursor/skills/nanobot/SKILL.md` |
| GOSLO Chat | `src/scripts/start_goslo_chat.py`, sibling `nanobot/config/goslo_config.json`, GOSLO workspace assumptions |
| Web/App Monitor routes | `src/parrot/brain/app_monitor_server.py`, `src/parrot/web_console/server.py`, `src/parrot/web_console/memory_ops.py` |
| Graphiti / L2-B | `.cursor/skills/graphiti/SKILL.md`, `.cursor/skills/dsg-l2b-node-organization-options/SKILL.md`, `src/parrot/memory/graphiti_client.py`, `src/parrot/web_console/graph_policy.py` |
| Ref/file management | `src/parrot/dsg/identity_ref_index.py`, `src/parrot/web_console/memory_ops.py`, `src/parrot/bus/nanobot_consumer.py`, `src/scripts/smoke_ref_scan.py`, `infra/deploy-castle.sh` |
| LiveKit / ECS parity | `.cursor/skills/bus-deploy-livekit-ecs/SKILL.md`, `infra/docker-compose.yml`, `infra/docker-compose.laptop.yml`, `infra/systemd/*.service` |

### TODO-0: Freeze audit and acceptance criteria

- Treat this file as the service parity checklist.
- Keep ECS public ports and laptop ports separate; laptop uses high ports to
  avoid clashing with host services.
- Do not copy ECS secrets into laptop env. Use local `infra/laptop.env.local`
  and mounted OAuth credentials.

Acceptance:

- This document names every ECS service from compose, systemd, and release
  scripts.

### TODO-1: Add laptop Scheduler service

Status: completed on 2026-05-18.

- Add `scheduler` to `infra/docker-compose.laptop.yml`.
- It should use the full project image, the laptop Redis URL, the laptop
  runtime data volume, and the same Falkor/Redis env as Brain.
- Update `infra/laptop-castle.ps1` so `up-brain` or a new action starts it.

Acceptance:

- `docker compose ... ps` shows `scheduler` running.
- Redis heartbeat/module status or logs show scheduler alive.
- A `dispatch_task` / calendar fallback can enter the Scheduler path.

Post-change audit:

- Pre-study covered `start_scheduler.py`, `scheduler/service.py`,
  `scheduler/router.py`, `scheduler/nodes.py`, `scheduler/blackboard.py`,
  `shared/constants.py`, and `dispatch_task.py`.
- Collaboration path confirmed:
  `dispatch_task` publishes `parrot.scheduler.commands`; Scheduler BT routes;
  Nanobot task types are written to `parrot.nanobot.dispatch`; Nanobot results
  return on `parrot.nanobot.results`; Scheduler forwards summaries to
  `parrot.scheduler.to_brain` and trigger results to `parrot.trigger.results`.
- Implementation:
  `infra/docker-compose.laptop.yml` now has a `scheduler` service in the
  `brain/all` profile. `infra/laptop-castle.ps1 -Action up-brain` now builds
  and starts both `brain` and `scheduler`.
- True-connection smoke:
  `parrot-laptop-castle-scheduler-1` connected to `ws://livekit:7880`, joined
  room `parrot-laptop-main` as `scheduler`, registered L2 heartbeat, listened
  on `parrot.scheduler.commands`, and routed a smoke `conversation` task to
  `brain_direct` through live Redis.
- Remaining boundary:
  Nanobot-routed tasks will still wait for TODO-2 because `nanobot-worker` is
  not yet mounted.

### TODO-2: Add Nanobot worker service

Status: completed on 2026-05-18 for the laptop Redis/Scheduler/Google
Workspace core path. GitHub MCP remains intentionally disabled unless
`GITHUB_TOKEN` is provided.

- Add Node/npm/npx to the Docker image used by Nanobot.
- Mount the sibling `D:\GOSLOParrot\nanobot` fork into the container.
- Install or expose `nanobot` in the container.
- Mount Google Workspace credentials read-only.
- Set `GOOGLE_WORKSPACE_CREDENTIALS_DIR` and, if needed,
  `GOOGLE_WORKSPACE_ACCOUNT_EMAIL`.
- Start with `--no-weixin` for laptop backend parity; WeChat remains opt-in.

Acceptance:

- Container has `node`, `npm`, `npx`, and `nanobot`.
- `start_nanobot_worker.py --no-weixin` boots without missing config.
- `message_check` and `calendar_fetch` tasks can be consumed and return a
  result through Redis.

Post-change audit:

- Pre-study covered `start_nanobot_worker.py`, sibling
  `nanobot/config/parrot_config.json`, `nanobot/channels/parrot_bus.py`,
  Scheduler service/node/task catalog, and `.cursor/skills/nanobot/SKILL.md`.
- Collaboration path confirmed:
  `parrot.scheduler.commands` -> Scheduler BT `DispatchToNanobot` ->
  Redis stream `parrot.nanobot.dispatch` -> nanobot `parrot_bus` channel ->
  nanobot agent/tool loop -> `parrot.nanobot.results` -> Scheduler fan-in ->
  `parrot.scheduler.to_brain`.
- Implementation:
  `infra/docker-compose.laptop.yml` now has `nanobot-worker` in the
  `brain/all` profile. The worker installs the sibling Nanobot fork from
  `/nanobot[parrot]`, runs `start_nanobot_worker.py --no-weixin --force-config`,
  mounts Google Workspace OAuth credentials read-only, stores Nanobot home in a
  Docker named volume, and keeps the mutable workspace in
  `codex_workspace/local_runtime/castle_laptop/nanobot_workspace`.
- Docker image/runtime fix:
  `infra/Dockerfile.brain` now installs pinned Node.js via the official Node
  tarball instead of Debian `npm`, avoiding the huge apt dependency path that
  triggered Docker Desktop failures when C: was full.
- Config hardening:
  `start_nanobot_worker.py` now disables GitHub MCP when `GITHUB_TOKEN` is not
  set instead of leaving `${GITHUB_TOKEN}` in generated config and crashing the
  worker. It also rewrites the Redis MCP server URL to the active `REDIS_URL`,
  and disables Google Workspace MCP if OAuth client credentials are missing.
- Local env state:
  `infra/laptop.env.local` now records
  `GOOGLE_WORKSPACE_ACCOUNT_EMAIL=gosloparrot@gmail.com`; token values were not
  copied into the SSOT.
- True-connection smoke:
  A live `summarize` task returned through
  `scheduler.commands -> nanobot.dispatch -> nanobot.results`, and Scheduler
  logged forwarding to `parrot.scheduler.to_brain`.
- Google Workspace smoke:
  A live `calendar_fetch` task used Nanobot's `google-workspace` skill and
  `manage_calendar` MCP tool for the configured account, then returned a
  completed result through Redis. Test output was redacted to avoid recording
  personal calendar details.
- Privacy/logging hardening:
  `start_nanobot_worker.py` no longer starts `nanobot gateway` with verbose
  logs by default. Verbose mode is now explicit via `--verbose`, because Google
  Workspace MCP tool outputs can include private Gmail/Calendar details in LLM
  debug request logs when verbose logging is enabled.
- Remaining boundaries:
  `message_check` should still get a dedicated Gmail smoke under TODO-3/Google
  route parity. GitHub MCP is unavailable until a real `GITHUB_TOKEN` is set.
  WeChat remains opt-in and intentionally disabled for laptop backend parity.

### TODO-3: Add app-monitor Calendar route parity

Status: completed on 2026-05-18 for Calendar Web route parity.

- Add the missing Calendar routes from `web_console/server.py` into
  `brain/app_monitor_server.py`.
- Keep direct API fetch and Nanobot fetch separate.

Acceptance:

- `POST :18790/api/google/calendar/import-plan` returns a draft plan.
- `POST :18790/api/google/calendar/import` imports events into L1.5/L2-B using
  the current policy.
- `GET :18790/api/google/calendar/results` returns recent Nanobot/fetch results.

Post-change audit:

- Pre-study compared the Calendar route blocks in
  `src/parrot/web_console/server.py`, `src/parrot/brain/app_monitor_server.py`,
  and the backing functions in `src/parrot/web_console/memory_ops.py`.
- Route drift found:
  app-monitor had only `preview`, `api-fetch`, and `nanobot-fetch`; Web Console
  also had `fetch`, `results`, `import-draft`, `import-plan`, and `import`.
- Implementation:
  app-monitor now exposes the missing five Calendar endpoints and delegates to
  the same `memory_ops` functions as the Web Console server.
- True-route smoke against live laptop app-monitor `:18790`:
  `/api/google/calendar/fetch`, `/api/google/calendar/results`,
  `/api/google/calendar/import-draft`, `/api/google/calendar/import-plan`, and
  `/api/google/calendar/import` all returned HTTP 200.
- Safety:
  the route smoke used a synthetic event and `dry_run`/non-operator mode for
  import apply; it did not mutate Google Calendar or L1.5.

### TODO-4: Decide laptop Orchestrator restart parity

Status: completed on 2026-05-18 as Option A / external operator restart mode.

Options:

- A. Keep `infra/laptop-castle.ps1` as the trusted operator restart path and
  mark `/restart_component` limited in laptop mode.
- B. Mount Docker socket and implement a compose restart adapter in the laptop
  orchestrator.
- C. Run orchestrator on host PowerShell/systemd-like wrapper for laptop.

Recommendation:

- Start with A for safety. Add B only if Web Console needs one-click restart of
  laptop components.

Acceptance:

- Web Console clearly shows laptop restart support as limited or implemented,
  instead of silently pretending ECS systemd exists.

Decision and post-change audit:

- Selected Option A. The laptop orchestrator does not mount the Docker socket
  and does not pretend to own host process control.
- Rationale:
  ECS uses `systemctl restart parrot-*.service`; laptop uses Docker Compose and
  should keep restart authority in the host operator shell until/unless we add
  an explicit Docker-socket adapter.
- Implementation:
  `restart_component()` now honors `PARROT_ORCH_RESTART_MODE=external_operator`
  and returns structured `restart_managed_externally` metadata instead of
  falling through to `systemctl_unavailable`.
- Component mapping:
  logical `maid` maps to compose service `nanobot-worker`; `brain`,
  `scheduler`, and `orchestrator` retain their service names.
- Operator path:
  `infra/laptop-castle.ps1 -Action restart -Service <service>` now restarts one
  service when `-Service` is provided, or all services when omitted.
- Web visibility:
  `/api/console/config` now includes browser-safe `restart_control` metadata so
  the ReactFlow Console can show that laptop restarts are managed externally.
- True-route smoke:
  `POST :17890/restart_component` with component `maid` returned HTTP 200 with
  reason `restart_managed_externally`, mode `external_operator`, compose
  service `nanobot-worker`, and an operator command hint. `/api/console/config`
  reported profile `laptop` and restart mode `external_operator`.

### TODO-5: Add optional GOSLO Chat service

Status: completed on 2026-05-18 as optional service/config parity. External
Telegram receive/send is intentionally pending because this laptop env does not
currently set `TELEGRAM_BOT_TOKEN`.

- Add `goslo-chat` behind an explicit profile, because it requires Telegram
  token and chat workspace.
- Mount `~/.nanobot/goslo-workspace` equivalent only when needed.

Acceptance:

- Service is optional and does not block core LiveKit/Brain/Web/Nanobot tests.

Post-change audit:

- Pre-study covered `src/scripts/start_goslo_chat.py`, sibling
  `nanobot/config/goslo_config.json`, `.cursor/skills/nanobot/SKILL.md`, and
  the Bus/ECS skill notes for service boundary expectations.
- Collaboration path:
  Telegram or future chat channel -> GOSLO nanobot gateway -> mode hook checks
  Redis key `parrot.goslo.mode` -> if chat body is active, GOSLO answers
  through nanobot; if Live body is active, the hook forwards toward Brain. The
  service can also use Google Workspace MCP through the same OAuth bridge as
  `nanobot-worker`.
- Implementation:
  `infra/docker-compose.laptop.yml` now has `goslo-chat` in `chat/all`
  profiles. It installs the sibling Nanobot fork, mounts the local GOSLO
  workspace at
  `codex_workspace/local_runtime/castle_laptop/goslo_workspace`, mounts Google
  Workspace OAuth credentials read-only, and uses an isolated
  `laptop_goslo_home` Docker volume.
- Operator entrypoint:
  `infra/laptop-castle.ps1 -Action up-chat` initializes the laptop runtime,
  copies the user's local `~/.nanobot/goslo-workspace` seed when present, then
  builds and starts `goslo-chat`.
- Config hardening:
  `start_goslo_chat.py` now disables Telegram if `TELEGRAM_BOT_TOKEN` is not
  set, disables GitHub MCP if `GITHUB_TOKEN` is not set, bridges Google
  Workspace OAuth credentials into MCP account/credential state, and creates a
  minimal GOSLO workspace if missing.
- True environment smoke:
  the `goslo-chat` image built with Node.js/npm/npx available. A one-off
  container generated `/home/parrot/.nanobot-goslo/config.json`, disabled
  Telegram and GitHub due missing tokens, kept `google_workspace` MCP enabled,
  wrote the Google Workspace MCP account registry/credential path inside the
  container, and confirmed the workspace mount exists.
- Remaining boundary:
  no live Telegram message was sent or received because no Telegram token is
  configured. Starting `goslo-chat` without that token would run with no active
  external chat channel, so it should remain opt-in until the token is present.

### TODO-6: True connection smoke tests

Status: completed on 2026-05-18 for Graphiti, Calendar API read,
Scheduler/Nanobot dispatch, Gmail MCP connectivity, and post-restart worker
sanity. Web browser click-through remains a manual UI check.

Run these after the component changes:

- App Monitor: `/api/graphiti/status`.
- Graphiti fixed partition: query `laptop_profile_test` through `query_memory`.
- Google Calendar direct API: fetch a known date/range.
- Google Calendar import plan and import route from `:18790`.
- Scheduler dispatch: one lightweight `research` or `message_check` task.
- Nanobot Gmail/Calendar MCP: verify non-dry-run result shape.
- Web Console: ReactFlow profile `laptop / web-console`, true connection, one
  Graphiti subgraph import, one Calendar import plan.

Post-change audit:

- Graphiti status:
  `GET :18790/api/graphiti/status` returned installed/available Graphiti with
  the laptop FalkorDB backend and known partitions.
- Laptop profile test data:
  `src/scripts/import_laptop_profile_to_graphiti.py` had mojibake/invalid
  string literals and was rewritten with proper UTF-8 facts. Six intended
  profile facts were attempted through the real app-monitor
  `/api/graphiti/episode` route; four wrote directly, and two were retried as
  shorter bilingual facts and then wrote successfully.
- Graphiti search:
  `/api/graphiti/subgraph/search` against `laptop_profile_test` returned real
  hits for the user's favorite drink, mouse, and laptop test facts. A direct
  `query_memory` tool smoke inside the container returned a real
  `laptop_profile_test` answer with Graphiti node/edge counts.
- Calendar official API read:
  `/api/google/calendar/api-fetch` with the mounted OAuth credential returned
  `success=true`, `available=true`, credential source `configured_oauth_file`.
  Today's window and a 14-day window both returned zero events, so no real
  calendar import-plan could be generated from personal events without creating
  a test event.
- Calendar Scheduler/Nanobot path:
  `/api/google/calendar/fetch` with `dry_run=false` and `operator_mode=true`
  dispatched a real `calendar_fetch` task. Scheduler routed it to Nanobot,
  Nanobot completed through Google Workspace MCP, and Scheduler wrote a
  `calendar_result` row to the trigger-result ledger with zero events.
- Gmail/message_check path:
  `/api/google/messages/check` with `dry_run=false`, `operator_mode=true`, and
  privacy-constrained instructions dispatched a real `message_check` task.
  Nanobot used Google Workspace `manage_email` and returned a completed
  `message_result` ledger row. The result content was not copied into this
  document.
- Logging bug found and fixed:
  the first Gmail smoke exposed that verbose nanobot logs can include private
  MCP/LLM payload context. The worker was patched, rebuilt, and restarted with
  verbose logging disabled by default; a post-restart summarize task completed
  successfully through Scheduler -> Nanobot -> Scheduler.
- Tests:
  `python -m pytest tests/test_brain/test_intent_graphiti_and_web_tools.py
  tests/test_brain/test_app_v1_monitor.py -q` passed: 23 tests.

### TODO-7: Documentation and risk notes

Status: completed on 2026-05-18 for the current laptop parity slice.

- Update Web Console backend target docs.
- Update laptop setup docs with the full service list.
- Record path and credential risks:
  - OAuth credentials are user secrets, mount read-only.
  - Local runtime data is under `codex_workspace/local_runtime/castle_laptop`.
  - Do not let Nanobot mutate arbitrary host paths until Ref policy is reviewed.
  - Photo/workshop path parity should be local sandbox first, not ECS paths.

Post-change audit:

- `codex_workspace/design_workspace/backend_interface_map/web_console/goslo_laptop_tooling_status_20260518.md`
  now records the GOSLO laptop tool set, fixed `laptop_profile_test` partition,
  UTF-8 seed facts, laptop connection targets, and operator commands.
- `codex_workspace/design_workspace/backend_interface_map/web_console/README.md`
  indexes that GOSLO laptop tooling note.
- `codex_workspace/design_workspace/backend_interface_map/app/README.md`
  indexes this laptop ECS parity audit as an active audit file.
- This file now records TODO-1 through TODO-7 status, true-connection smoke,
  and the nanobot verbose-log privacy fix.

### TODO-8: Add laptop Ref/file sandbox parity

Status: completed on 2026-05-18 for safe laptop sandbox mounts,
IdentityRefIndex persistence, app-monitor route parity, and a true read-only
RefScan through Scheduler/Nanobot.

User requirement anchor:

- Laptop should cover ECS functionality as much as possible.
- Ref/file management must not rely on fixed ECS paths that cannot be tested
  or changed.
- Do not let Nanobot mutate arbitrary host paths until Ref conflict/writeback
  policy is reviewed.

Pre-study and collaboration review:

- Source ECS setup creates `/data/workshop/photos`,
  `/data/workshop/documents`, and `/data/workshop/sorted` in
  `infra/deploy-castle.sh`.
- `MemoryIdentityRefIndex` is the current CORE-015 candidate SSOT for
  canonical UUIDs, Graphiti UUIDs, Obsidian UUIDs, Ref IDs, locators, health,
  and move/writeback metadata.
- Web/App routes expose draft/apply/verify/resolve/ref-scan surfaces through
  `/api/memory/identity-ref-index*`.
- RefScan true path is:
  Web/App route -> `dispatch_task("ref_scan")` -> Scheduler ->
  `parrot.nanobot.dispatch` -> `NanobotConsumer`/Nanobot ->
  `memory_ref_scan_result` in the Scheduler trigger-result ledger.
- The scan contract is read-only by design: filesystem stat/hash, optional
  URL HEAD, optional Graphiti probe, optional ECS-local read-only stat. It
  explicitly disallows file move/delete, manifest write, IdentityRefIndex
  write, Graphiti mutation, L2-B mutation, and ECS write.

Implementation plan:

- Add local runtime directories under
  `codex_workspace/local_runtime/castle_laptop`.
- Mount only safe sandbox paths into laptop containers:
  `/data/workshop/photos`, `/data/workshop/documents`,
  `/data/workshop/sorted`, and `/data/workshop/refs`.
- Keep the existing photo cache canonical path at `/app/data/photos`, but also
  expose the same local photo directory as `/data/workshop/photos` for ECS
  path parity.
- Persist the laptop IdentityRefIndex to
  `/app/data/registries/memory_identity_ref_index.json`, which is local runtime
  backend state, not browser persistence.
- Configure Nanobot RefScan allowed roots to `/data/workshop;/app/data`.

Acceptance:

- `infra/laptop-castle.ps1 -Action init` creates the local sandbox
  directories.
- App monitor, Brain, Scheduler, Nanobot, and optional GOSLO chat containers
  can see the workshop paths.
- A read-only RefScan can dispatch through the running laptop
  Scheduler/Nanobot path and report at least one local sandbox file as healthy.

Post-change audit:

- `infra/laptop-castle.ps1 -Action init` now creates:
  `data/photos`, `data/registries`, `workshop/documents`,
  `workshop/sorted`, and `workshop/refs`.
- `infra/docker-compose.laptop.yml` mounts:
  local `data/photos` to both `/app/data/photos` and
  `/data/workshop/photos`; local workshop documents/sorted/refs to the matching
  `/data/workshop/*` paths; and the same data runtime to `/app/data`.
- App monitor, Brain, Scheduler, Nanobot worker, and optional GOSLO chat now
  receive `PARROT_WORKSHOP_ROOT` and the laptop
  `PARROT_MEMORY_IDENTITY_REF_INDEX_PATH`.
- Nanobot worker and GOSLO chat also receive
  `PARROT_REF_SCAN_ECS_LOCAL_ROOTS=/data/workshop;/app/data` for read-only ECS
  locator checks when explicitly enabled.
- App-monitor route parity added:
  `/api/refs/binding/draft`, `/api/refs/binding/apply`, and
  `/api/memory/identity-ref-index*`, including RefScan plan/dispatch/results.
- Bug found during true smoke:
  the live Nanobot agent treated `ref_scan` as an open-ended prompt and returned
  prose instead of structured scan rows. This proved the bus path was live but
  the task contract was wrong.
- Bug fix:
  sibling Nanobot `nanobot/channels/parrot_bus.py` now routes `ref_scan`
  through ParrotCarriers' deterministic `_ref_scan_result` while leaving
  Calendar/Gmail/research tasks on the normal Nanobot agent/MCP path.
- True-connection smoke:
  a local sandbox file at `/data/workshop/documents/laptop_refscan_smoke.md`
  was written on the host, registered through
  `POST :18790/api/memory/identity-ref-index/apply`, dispatched through
  `POST :18790/api/memory/identity-ref-index/ref-scan-dispatch`, consumed by
  the running laptop Scheduler/Nanobot path, and returned a completed
  `memory_ref_scan_result` with `ref_result_count=1`, `local_path_exists`, and
  `health=ok`.
- Validation:
  `py_compile` passed for `src/parrot/brain/app_monitor_server.py` and sibling
  `nanobot/channels/parrot_bus.py`; focused tests
  `tests/test_brain/test_app_v1_monitor.py` and
  `tests/test_castle/test_livekit_config.py` passed: 23 tests.

### TODO-9: Add laptop Obsidian/Source Board route parity

Status: completed on 2026-05-18 for app-monitor Obsidian/Source Board route
parity and direct laptop true smoke.

User requirement anchor:

- The ReactFlow Console should be able to point directly at the laptop backend,
  not silently depend on ECS or the Web BFF.
- Source/Ref/Node tools should be true interfaces, not browser-only drafts.
- L1.5/L2-B remains a working-memory/context projection; Source Board routes
  may stage and import selected Obsidian notes, but they are not the final SSOT
  for external files.

Pre-study and collaboration review:

- Web Console calls these Source Board routes:
  `GET /api/l15/obsidian-vault/scan`,
  `POST /api/l15/obsidian-vault/import-draft`,
  `POST /api/l15/obsidian-vault/import-plan`,
  `POST /api/l15/obsidian-vault/import`,
  `POST /api/l15/obsidian-node/draft`,
  `POST /api/l15/obsidian-node`, and
  `GET /api/photos/asset/{day}/{photo_id}`.
- Web BFF already implements those routes in
  `src/parrot/web_console/server.py` by delegating to
  `src/parrot/web_console/memory_ops.py`.
- `memory_ops.scan_obsidian_vault` uses
  `parrot.brain.obsidian_vault.check_obsidian_vault` and only reads Markdown
  files under the provided vault path.
- `draft_obsidian_l2b_import_plan` and `draft_obsidian_vault_import` are safe
  draft surfaces. Real import requires explicit `dry_run=false` and
  `operator_mode=true`.
- The laptop container-visible test path should be under the local sandbox,
  for example `/data/workshop/documents/obsidian_smoke`.

Implementation plan:

- Add app-monitor route parity for the Obsidian vault scan/import-plan/draft
  and Obsidian single-node draft/apply routes by delegating to the same
  `memory_ops` functions as Web BFF.
- Add the read-only photo asset route to app-monitor, with the same cache-root
  path guard used by Web BFF.
- Add focused app-monitor tests for route availability and safe scan/draft
  behavior.
- Rebuild the laptop app-monitor container and run a true smoke against
  `http://127.0.0.1:18790`.

Acceptance:

- Direct ReactFlow backend target `laptop / app-monitor` no longer returns 404
  for Obsidian vault scan/import-plan/import-draft or photo assets.
- A Markdown note in the laptop sandbox can be scanned through
  `GET :18790/api/l15/obsidian-vault/scan` and returns at least one
  ingest-ready note.
- A draft or import-plan can be generated through app-monitor without mutating
  L1.5/L2-B.
- Any real import remains operator gated.

Post-change audit:

- `src/parrot/brain/app_monitor_server.py` now exposes:
  `/api/l15/obsidian-vault/scan`,
  `/api/l15/obsidian-vault/import-draft`,
  `/api/l15/obsidian-vault/import-plan`,
  `/api/l15/obsidian-vault/import`,
  `/api/l15/obsidian-node/draft`,
  `/api/l15/obsidian-node`, and
  `/api/photos/asset/{day}/{photo_id}`.
- The Obsidian apply routes are still operator-gated through the existing
  app-monitor write-auth middleware and the `dry_run/operator_mode` policy in
  `memory_ops`.
- The photo route uses the same cache-root path guard as Web BFF and only
  serves safe `.jpg` IDs under `PARROT_PHOTO_CACHE_ROOT`.
- Test coverage:
  `py_compile src/parrot/brain/app_monitor_server.py` passed, and
  `tests/test_brain/test_app_v1_monitor.py` passed: 16 tests.
- True-connection smoke:
  after `infra/laptop-castle.ps1 -Action rebuild`, a sandbox note at
  `/data/workshop/documents/obsidian_smoke/daily.md` scanned through
  `GET :18790/api/l15/obsidian-vault/scan` with
  `vault.status=ingest_ready` and one note. `POST :18790` import-draft and
  import-plan both succeeded with `selected_count=1`; the photo asset route
  returned HTTP 200 and `image/jpeg`.
