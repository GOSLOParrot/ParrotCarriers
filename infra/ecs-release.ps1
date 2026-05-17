<#
.SYNOPSIS
Audited ParrotCarriers release to the Castle ECS node.

.DESCRIPTION
This script is the post-commit/push release gate for true-connection testing.
It refuses to deploy an unpushed local HEAD, refuses remote dirty worktrees by
default, updates the ECS repo through git, restarts all Parrot systemd services,
and runs local smoke checks on the ECS node.

Use -WhatIf to print the remote script without touching the ECS node.
Use -ForceResetWorktree only after auditing ECS drift; it backs up status and
diff files under codex_backups/ before resetting tracked files to origin/<Branch>.

.EXAMPLE
.\infra\ecs-release.ps1 -Branch master

.EXAMPLE
.\infra\ecs-release.ps1 -Branch master -AllowLocalDirty -ForceResetWorktree
#>
[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [string]$HostName = "root@8.216.45.45",
    [string]$RemoteDir = "/opt/parrot/ParrotCarriers",
    [string]$Branch = "master",
    [string[]]$Services = @(
        "parrot-orchestrator",
        "parrot-app-monitor",
        "parrot-scheduler",
        "parrot-maid",
        "parrot-goslo-chat",
        "parrot-brain"
    ),
    [switch]$AllowLocalDirty,
    [switch]$ForceResetWorktree,
    [switch]$SkipInstall,
    [switch]$SkipSmoke
)

$ErrorActionPreference = "Stop"

function Assert-SafeToken {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$Value
    )
    if ($Value -notmatch '^[A-Za-z0-9_./:@-]+$') {
        throw "$Name contains unsupported characters for this release script: $Value"
    }
}

function Invoke-GitText {
    param([Parameter(Mandatory = $true)][string[]]$GitArgs)
    $output = & git @GitArgs
    if ($LASTEXITCODE -ne 0) {
        throw "git $($GitArgs -join ' ') failed with exit code $LASTEXITCODE"
    }
    return ($output -join "`n").Trim()
}

Assert-SafeToken -Name "HostName" -Value $HostName
Assert-SafeToken -Name "RemoteDir" -Value $RemoteDir
Assert-SafeToken -Name "Branch" -Value $Branch
foreach ($service in $Services) {
    Assert-SafeToken -Name "Service" -Value $service
}

$serviceList = $Services -join " "
$forceResetFlag = if ($ForceResetWorktree) { "1" } else { "0" }
$skipInstallFlag = if ($SkipInstall) { "1" } else { "0" }
$skipSmokeFlag = if ($SkipSmoke) { "1" } else { "0" }

$remoteScript = @"
set -euo pipefail

REMOTE_DIR='$RemoteDir'
BRANCH='$Branch'
FORCE_RESET='$forceResetFlag'
SKIP_INSTALL='$skipInstallFlag'
SKIP_SMOKE='$skipSmokeFlag'
SERVICES='$serviceList'

echo "[remote] host=`$(hostname) repo=`$REMOTE_DIR branch=`$BRANCH"
cd "`$REMOTE_DIR"

git fetch origin "`$BRANCH"
target_head="`$(git rev-parse "origin/`$BRANCH")"
current_head="`$(git rev-parse HEAD)"
tracked_dirty_status="`$(git status --porcelain --untracked-files=no)"
untracked_status="`$(git status --porcelain --untracked-files=normal | grep '^??' || true)"

if [ -n "`$untracked_status" ]; then
  echo "[remote] untracked runtime files present; preserving them:"
  printf '%s\n' "`$untracked_status"
fi

if [ -n "`$tracked_dirty_status" ]; then
  echo "[remote] tracked/index worktree drift detected:"
  printf '%s\n' "`$tracked_dirty_status"
  if [ "`$FORCE_RESET" != "1" ]; then
    echo "[remote] refusing to update dirty ECS worktree without -ForceResetWorktree"
    exit 23
  fi

  stamp="`$(date -u +%Y%m%dT%H%M%SZ)"
  backup_dir="`$REMOTE_DIR/codex_backups/ecs_release_`$stamp"
  mkdir -p "`$backup_dir"
  git status --short --untracked-files=no > "`$backup_dir/status.txt" || true
  git diff > "`$backup_dir/worktree.diff" || true
  git diff --cached > "`$backup_dir/index.diff" || true
  git diff --stat > "`$backup_dir/worktree.stat" || true
  echo "[remote] backed up tracked ECS drift to `$backup_dir"
  git reset --hard "origin/`$BRANCH"
elif [ "`$current_head" = "`$target_head" ]; then
  echo "[remote] already at origin/`$BRANCH (`$(git rev-parse --short HEAD))"
else
  git pull --ff-only origin "`$BRANCH"
fi

echo "[remote] HEAD=`$(git rev-parse --short HEAD)"

if [ "`$SKIP_INSTALL" != "1" ]; then
  if [ -x ".venv/bin/python" ]; then
    echo "[remote] installing editable package into .venv"
    .venv/bin/python -m pip install -e .
  else
    echo "[remote] warning: .venv/bin/python missing; skipped pip install"
  fi
fi

echo "[remote] systemd daemon-reload"
systemctl daemon-reload

for svc in `$SERVICES; do
  echo "[remote] restart `$svc"
  systemctl restart "`$svc"
done

sleep 2
release_failed=0
for svc in `$SERVICES; do
  state="`$(systemctl is-active "`$svc" || true)"
  echo "[remote] service `$svc = `$state"
  if [ "`$state" != "active" ]; then
    release_failed=1
  fi
done

if [ "`$SKIP_SMOKE" != "1" ]; then
  echo "[remote] smoke: orchestrator :7890"
  if ! curl -fsS --max-time 10 http://127.0.0.1:7890/health >/tmp/parrot_release_orchestrator_health.json; then
    curl -fsS --max-time 10 http://127.0.0.1:7890/status >/tmp/parrot_release_orchestrator_status.json
  fi

  echo "[remote] smoke: app monitor Graphiti :8790"
  curl -fsS --max-time 30 http://127.0.0.1:8790/api/graphiti/status >/tmp/parrot_release_graphiti_status.json

  if command -v redis-cli >/dev/null 2>&1; then
    echo "[remote] smoke: redis/falkor :6380"
    redis-cli -p 6380 PING >/tmp/parrot_release_redis_ping.txt || release_failed=1
  else
    echo "[remote] warning: redis-cli missing; skipped Redis smoke"
  fi
fi

if [ "`$release_failed" -ne 0 ]; then
  echo "[remote] release finished with failing service/smoke checks"
  exit 24
fi

echo "[remote] release complete"
"@

if ($WhatIfPreference) {
    Write-Host "[whatif] Would verify local git state, then run SSH release on $HostName"
    Write-Host "[whatif] Remote script:"
    Write-Host $remoteScript
    return
}

$localBranch = Invoke-GitText @("branch", "--show-current")
if ($localBranch -ne $Branch) {
    Write-Warning "Current local branch is '$localBranch', deploying origin/$Branch."
}

$dirtyLocal = Invoke-GitText @("status", "--porcelain")
if ($dirtyLocal -and -not $AllowLocalDirty) {
    throw "Local worktree has uncommitted changes. Commit/stash them, or rerun with -AllowLocalDirty after auditing unrelated files."
}

Invoke-GitText @("fetch", "origin", $Branch) | Out-Null
$localHead = Invoke-GitText @("rev-parse", "HEAD")
$remoteHead = Invoke-GitText @("rev-parse", "origin/$Branch")
if ($localHead -ne $remoteHead) {
    throw "Local HEAD ($localHead) is not pushed to origin/$Branch ($remoteHead). Commit and push before ECS release."
}

if ($PSCmdlet.ShouldProcess($HostName, "Update $RemoteDir to origin/$Branch and restart Parrot services")) {
    $utf8NoBom = [System.Text.UTF8Encoding]::new($false)
    $remoteScriptBase64 = [Convert]::ToBase64String($utf8NoBom.GetBytes($remoteScript))
    $remoteCommand = "printf '%s' '$remoteScriptBase64' | base64 -d | bash"
    & ssh $HostName $remoteCommand
    if ($LASTEXITCODE -ne 0) {
        throw "ECS release failed with exit code $LASTEXITCODE"
    }
}
