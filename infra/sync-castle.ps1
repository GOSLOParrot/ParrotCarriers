# sync-castle.ps1 — 一键同步工作区到 Castle ECS
# 用法（在 ParrotCarriers 根目录运行）：
#   .\infra\sync-castle.ps1              # 只同步代码（git pull）
#   .\infra\sync-castle.ps1 -Workspace   # 代码 + nanobot persona
#   .\infra\sync-castle.ps1 -Env         # 代码 + .env 文件
#   .\infra\sync-castle.ps1 -All         # 全量

param(
    [switch]$Workspace,
    [switch]$Env,
    [switch]$All
)

if ($All) { $Workspace = $true; $Env = $true }

$CASTLE_IP  = "8.216.45.45"
$SSH        = "ssh -o StrictHostKeyChecking=no -o ConnectTimeout=15"
$RSYNC_SSH  = "ssh -o StrictHostKeyChecking=no"
$REMOTE_PC  = "/opt/parrotcarriers"
$REMOTE_NB  = "/opt/nanobot"

# 本地路径
$LOCAL_PC       = Split-Path $PSScriptRoot          # infra/ 的父目录 = 仓库根
$LOCAL_NB       = Join-Path (Split-Path $LOCAL_PC) "nanobot"
$LOCAL_WS_GOSLO = "$env:USERPROFILE\.nanobot\goslo-workspace"
$LOCAL_WS_MAID  = "$env:USERPROFILE\.nanobot\workspace"

function Step($n, $msg) { Write-Host "`n[$n] $msg" -ForegroundColor Cyan }
function OK($msg)        { Write-Host "    OK  $msg" -ForegroundColor Green }
function Warn($msg)      { Write-Host "    !!  $msg" -ForegroundColor Yellow }

Write-Host "`n==== Castle 同步 -> $CASTLE_IP ====" -ForegroundColor Magenta

# ──────────────────────────────────────────────────────────
# 1. 代码同步（始终执行）
# ──────────────────────────────────────────────────────────
Step "1/4" "代码同步 (git pull)"

$pcOut = & ssh -o StrictHostKeyChecking=no -o ConnectTimeout=15 root@$CASTLE_IP `
    "cd $REMOTE_PC; git pull origin master 2>&1"
$pcChanged = $pcOut -notmatch "Already up to date"
if ($pcChanged) { OK "ParrotCarriers: 有更新" } else { OK "ParrotCarriers: 已是最新" }

$nbOut = & ssh -o StrictHostKeyChecking=no -o ConnectTimeout=15 root@$CASTLE_IP `
    "cd $REMOTE_NB; git pull origin main 2>&1"
$nbChanged = $nbOut -notmatch "Already up to date"
if ($nbChanged) { OK "nanobot: 有更新" } else { OK "nanobot: 已是最新" }

# ──────────────────────────────────────────────────────────
# 2. 依赖安装（有代码更新时）
# ──────────────────────────────────────────────────────────
$codeChanged = $pcChanged -or $nbChanged

Step "2/4" "Python 依赖"
if ($codeChanged) {
    Write-Host "    检测到代码变更，重装依赖..." -ForegroundColor DarkGray
    & ssh -o StrictHostKeyChecking=no root@$CASTLE_IP `
        "cd $REMOTE_PC; .venv/bin/pip install -q -e '.[dev,memory]' 2>&1 | tail -2"
    & ssh -o StrictHostKeyChecking=no root@$CASTLE_IP `
        "cd $REMOTE_PC; .venv/bin/pip install -q -e '$REMOTE_NB[parrot]' 2>&1 | tail -2"
    OK "依赖安装完成"
} else {
    Write-Host "    无代码变更，跳过" -ForegroundColor DarkGray
}

# ──────────────────────────────────────────────────────────
# 3. Nanobot Workspace 同步
# ──────────────────────────────────────────────────────────
Step "3/4" "Nanobot Workspace"
if ($Workspace) {
    if (Test-Path $LOCAL_WS_GOSLO) {
        & rsync -avz --delete -e $RSYNC_SSH `
            "$LOCAL_WS_GOSLO/" "root@${CASTLE_IP}:~/.nanobot/goslo-workspace/"
        OK "goslo-workspace 同步完成"
    } else { Warn "本地 goslo-workspace 不存在 ($LOCAL_WS_GOSLO)" }

    if (Test-Path $LOCAL_WS_MAID) {
        & rsync -avz --delete --exclude "sessions/" --exclude "memory/" -e $RSYNC_SSH `
            "$LOCAL_WS_MAID/" "root@${CASTLE_IP}:~/.nanobot/workspace/"
        OK "workspace(maid) persona 同步完成（sessions/memory 已排除）"
    } else { Warn "本地 workspace 不存在 ($LOCAL_WS_MAID)" }
} else {
    Write-Host "    跳过（-Workspace 或 -All 可启用）" -ForegroundColor DarkGray
}

# ──────────────────────────────────────────────────────────
# 4. .env 同步
# ──────────────────────────────────────────────────────────
Step "4/4" ".env 文件"
if ($Env) {
    $localEnv = Join-Path $LOCAL_PC ".env"
    if (Test-Path $localEnv) {
        & rsync -avz -e $RSYNC_SSH "$localEnv" "root@${CASTLE_IP}:${REMOTE_PC}/.env"
        OK ".env 同步完成"
    } else { Warn "本地 .env 不存在 ($localEnv)" }
} else {
    Write-Host "    跳过（-Env 或 -All 可启用）" -ForegroundColor DarkGray
}

# ──────────────────────────────────────────────────────────
# 汇总
# ──────────────────────────────────────────────────────────
Write-Host "`n──────────────────────────────────" -ForegroundColor DarkGray
Write-Host "Castle 当前状态：" -ForegroundColor Magenta
$summary = & ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 `
    root@$CASTLE_IP `
    "echo 'PC:' && cd $REMOTE_PC && git log --oneline -1; echo 'NB:' && cd $REMOTE_NB && git log --oneline -1"
$summary | ForEach-Object { Write-Host "  $_" }
Write-Host ""
