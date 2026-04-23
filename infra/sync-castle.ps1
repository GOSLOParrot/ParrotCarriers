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

# ── Cursor / Windows PowerShell 5.x：中文与 ssh 输出不乱码 ──
# 终端仍为「活动代码页 936」时，UTF-8 脚本输出会被错解；此处统一 UTF-8。
# 另：本文件应以 UTF-8 BOM 保存，便于 Windows PowerShell 5.x 解析脚本内中文。
$script:__utf8NoBom = [System.Text.UTF8Encoding]::new($false)
try {
    if ($env:OS -match 'Windows') { chcp 65001 | Out-Null }
} catch { }
try {
    [Console]::InputEncoding  = $script:__utf8NoBom
    [Console]::OutputEncoding = $script:__utf8NoBom
} catch { }
$OutputEncoding = $script:__utf8NoBom

$CASTLE_IP  = "8.216.45.45"
$REMOTE_PC  = "/opt/parrotcarriers"
$REMOTE_NB  = "/opt/nanobot"

# SSH：保活 + TCP keepalive + 重试，降低 NAT/负载均衡 idle 断连与偶发超时
# 可选：在 %USERPROFILE%\.ssh\config 增加 Host 段，写入相同 -o 以便手动 ssh 也稳定
$SshArgs = @(
    "-o", "StrictHostKeyChecking=no",
    "-o", "ConnectTimeout=20",
    "-o", "ConnectionAttempts=3",
    "-o", "TCPKeepAlive=yes",
    "-o", "ServerAliveInterval=30",
    "-o", "ServerAliveCountMax=6"
)
$RSYNC_SSH = "ssh -o StrictHostKeyChecking=no -o ConnectTimeout=20 -o ConnectionAttempts=3 -o TCPKeepAlive=yes -o ServerAliveInterval=30 -o ServerAliveCountMax=6"

# 若 Castle 仍频繁 idle 断开，可在 /etc/ssh/sshd_config 增加并重启 sshd:
#   ClientAliveInterval 30
#   ClientAliveCountMax 6

# 本地路径
$LOCAL_PC       = Split-Path $PSScriptRoot          # infra/ 的父目录 = 仓库根
$LOCAL_NB       = Join-Path (Split-Path $LOCAL_PC) "nanobot"
$LOCAL_WS_GOSLO = "$env:USERPROFILE\.nanobot\goslo-workspace"
$LOCAL_WS_MAID  = "$env:USERPROFILE\.nanobot\workspace"

function Step($n, $msg) { Write-Host "`n[$n] $msg" -ForegroundColor Cyan }
function OK($msg)        { Write-Host "    OK  $msg" -ForegroundColor Green }
function Warn($msg)      { Write-Host "    !!  $msg" -ForegroundColor Yellow }
function Fail($msg) {
    Write-Host "    ERR $msg" -ForegroundColor Red
    exit 1
}

function Invoke-CastleSsh {
    param(
        [Parameter(Mandatory)][string]$RemoteCommand,
        [string]$Label = "ssh"
    )
    $out = & ssh @SshArgs "root@${CASTLE_IP}" $RemoteCommand 2>&1
    $code = $LASTEXITCODE
    if ($code -ne 0) {
        $out | ForEach-Object { Write-Host "        $_" -ForegroundColor DarkYellow }
        Fail "${Label} 失败 (exit ${code})，请检查网络、sshd 或远端命令输出。"
    }
    return $out
}

function Test-GitPullAlreadyUpToDate {
    param($Output)
    $text = if ($null -eq $Output) { "" } else { ($Output | Out-String).Trim() }
    return ($text -match "Already up to date")
}

Write-Host "`n==== Castle 同步 -> $CASTLE_IP ====" -ForegroundColor Magenta

# ──────────────────────────────────────────────────────────
# 1. 代码同步（始终执行）
# ──────────────────────────────────────────────────────────
Step "1/4" "代码同步 (git pull)"

$pcOut = Invoke-CastleSsh "cd $REMOTE_PC && git pull origin master 2>&1" "ParrotCarriers git pull"
$pcOut | ForEach-Object { Write-Host "        $_" -ForegroundColor DarkGray }
$pcChanged = -not (Test-GitPullAlreadyUpToDate $pcOut)
if ($pcChanged) { OK "ParrotCarriers: 有更新" } else { OK "ParrotCarriers: 已是最新" }

$nbOut = Invoke-CastleSsh "cd $REMOTE_NB && git pull origin main 2>&1" "nanobot git pull"
$nbOut | ForEach-Object { Write-Host "        $_" -ForegroundColor DarkGray }
$nbChanged = -not (Test-GitPullAlreadyUpToDate $nbOut)
if ($nbChanged) { OK "nanobot: 有更新" } else { OK "nanobot: 已是最新" }

# ──────────────────────────────────────────────────────────
# 2. 依赖安装（有代码更新时）
# ──────────────────────────────────────────────────────────
$codeChanged = $pcChanged -or $nbChanged

Step "2/4" "Python 依赖"
if ($codeChanged) {
    Write-Host "    检测到代码变更，重装依赖..." -ForegroundColor DarkGray
    Invoke-CastleSsh "cd $REMOTE_PC && .venv/bin/pip install -q -e '.[dev,memory]'" "pip install ParrotCarriers[dev,memory]"
    $nbEditable = $REMOTE_NB + "[parrot]"
    Invoke-CastleSsh "cd $REMOTE_PC && .venv/bin/pip install -q -e '$nbEditable'" "pip install nanobot[parrot]"
    # 阿里云镜像缺少 redis>=7.1，从 PyPI 补装（falkordb 1.6.0 依赖）
    Invoke-CastleSsh "cd $REMOTE_PC && .venv/bin/pip install -q 'redis>=7.1,<9.0' --index-url https://pypi.org/simple/" "pip install redis>=7.1"
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
        if ($LASTEXITCODE -ne 0) { Fail "rsync goslo-workspace 失败 (exit $LASTEXITCODE)" }
        OK "goslo-workspace 同步完成"
    } else { Warn "本地 goslo-workspace 不存在 ($LOCAL_WS_GOSLO)" }

    if (Test-Path $LOCAL_WS_MAID) {
        & rsync -avz --delete --exclude "sessions/" --exclude "memory/" -e $RSYNC_SSH `
            "$LOCAL_WS_MAID/" "root@${CASTLE_IP}:~/.nanobot/workspace/"
        if ($LASTEXITCODE -ne 0) { Fail "rsync workspace(maid) 失败 (exit $LASTEXITCODE)" }
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
        if ($LASTEXITCODE -ne 0) { Fail "rsync .env 失败 (exit $LASTEXITCODE)" }
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
try {
    $summary = & ssh @SshArgs "root@${CASTLE_IP}" `
        "echo 'PC:' && cd $REMOTE_PC && git log --oneline -1; echo 'NB:' && cd $REMOTE_NB && git log --oneline -1" 2>&1
    if ($LASTEXITCODE -ne 0) {
        Warn "无法读取远端提交摘要 (exit $LASTEXITCODE)"
        $summary | ForEach-Object { Write-Host "        $_" -ForegroundColor DarkYellow }
    } else {
        $summary | ForEach-Object { Write-Host "  $_" }
    }
} catch {
    Warn "汇总步骤异常: $_"
}
Write-Host ""
