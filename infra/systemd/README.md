# Castle systemd units (Phase 3.1)

Unit files for `parrot-brain`, `parrot-scheduler`, `parrot-maid`,
`parrot-goslo-chat`, and `parrot-orchestrator` services on the Castle
ECS node. Designed to replace the current `tmux` manual launch path
(see `infra/deploy-castle.sh`).

## Layout assumptions

* Repo lives at `/opt/parrot/ParrotCarriers`.
* Python venv at `/opt/parrot/ParrotCarriers/.venv`.
* `.env.castle` lives at `/opt/parrot/ParrotCarriers/.env.castle` and is loaded via `EnvironmentFile=`.
* Unprivileged user: `parrot`.

If your layout differs, edit the `User=`, `WorkingDirectory=`, and
`EnvironmentFile=` lines, or symlink the repo to `/opt/parrot/ParrotCarriers`.

## Install

```bash
sudo cp infra/systemd/*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable parrot-orchestrator parrot-brain parrot-scheduler \
  parrot-maid parrot-goslo-chat
sudo systemctl start parrot-orchestrator
# orchestrator is the user-visible entry; the others come up via its
# /restart_component endpoint (or directly with `systemctl start`).
```

## Dependency graph

```
docker.service ──→ parrot-orchestrator.service
                  ├── parrot-brain.service        (Wants= the orchestrator)
                  ├── parrot-scheduler.service    (Wants= the orchestrator)
                  ├── parrot-maid.service         (Wants= the orchestrator)
                  └── parrot-goslo-chat.service   (Wants= the orchestrator)
```

`Wants=` is intentionally soft: a Brain crash should never knock out
the orchestrator (which is the only safe restart path). Likewise the
orchestrator is `Wants=docker.service` not `Requires=` so it can come
up on a Castle that's still booting Docker.

## Phase 3.2 + 3.3 note

When Brain becomes a Docker container (Phase 3.2), `parrot-brain.service`
will be replaced by `docker compose up -d brain` driven through the
orchestrator. Keep these unit files for the Python-process variant in
the meantime; they are the operator's manual fallback path.

## Codex true-connection release workflow

Use `infra/ecs-release.ps1` after the local change has been audited, committed,
and pushed. This is the current Codex-managed path for making ECS run the same
code that was just tested locally:

```powershell
git status --short
git diff --stat
# stage only the audited files, then commit and push
git push origin master

.\infra\ecs-release.ps1 -Branch master
```

The script verifies that local `HEAD` is already pushed to `origin/<branch>`,
SSHes to `root@8.216.45.45`, updates `/opt/parrot/ParrotCarriers`, installs the
editable package into the ECS venv, restarts these systemd units, and runs smoke
checks against `:7890`, `:8790`, and Redis/Falkor `:6380`:

```text
parrot-orchestrator
parrot-app-monitor
parrot-scheduler
parrot-maid
parrot-goslo-chat
parrot-brain
```

If the ECS repo has local drift, the script refuses to update by default. After
auditing the drift, run with `-ForceResetWorktree` to back up tracked status and
diffs under `/opt/parrot/ParrotCarriers/codex_backups/ecs_release_*` before
resetting tracked files to `origin/<branch>`. It does not delete untracked ECS
files.
