# audit_deps.ps1 — Castle 依赖审计 (S0.K, 2026-04-22)
#
# 用法 (ParrotCarriers 根目录运行):
#   .\infra\audit_deps.ps1                # 审计本地 + SSH 到 Castle 审计远端
#   .\infra\audit_deps.ps1 -Local         # 只审本地
#   .\infra\audit_deps.ps1 -Remote        # 只审远端 (SSH Castle)
#
# 审什么:
#   1. pyproject.toml 声明的 Python 主依赖 vs .venv 实装版本
#   2. Redis / FalkorDB / LiveKit 容器是否在跑 (仅 Remote)
#   3. Unity manifest.json 锁定的 AR Foundation / ARCore / LiveKit 版本
#   4. 关键 Schema 文件是否存在 (shared/event_log.py, dsg/l1_5_protocol.py, dsg/l2b_types.py)
#
# 不做:
#   - 自动修 (只报告)
#   - 改 ECS 上任何状态 (只读)
#
# 源: sprint0_preflight.md §5.2 依赖锁定

param(
    [switch]$Local,
    [switch]$Remote
)

if (-not $Local -and -not $Remote) { $Local = $true; $Remote = $true }

$CASTLE = "Castle"   # ~/.ssh/config alias

function Step($n, $msg) { Write-Host "`n[$n] $msg" -ForegroundColor Cyan }
function OK($msg)       { Write-Host "    OK   $msg" -ForegroundColor Green }
function Warn($msg)     { Write-Host "    WARN $msg" -ForegroundColor Yellow }
function Fail($msg)     { Write-Host "    FAIL $msg" -ForegroundColor Red }

$root = Split-Path $PSScriptRoot
$pyproject = Join-Path $root "pyproject.toml"
$manifest  = Join-Path $root "unity\ParrotDev\Packages\manifest.json"

# ----------------------------------------------------------------------
#  Part A — 本地审计
# ----------------------------------------------------------------------

if ($Local) {
    Step "A" "本地依赖审计"

    if (-not (Test-Path $pyproject)) {
        Fail "找不到 $pyproject"
    } else {
        OK "pyproject.toml 存在"
        $lines = Get-Content $pyproject
        $deps = $lines | Select-String -Pattern '^\s*"(\w[\w-]*)[><=!~]'
        if ($deps.Count -eq 0) {
            Warn "未在 pyproject.toml 中找到 dependencies"
        } else {
            Write-Host "    Declared Python deps:"
            foreach ($d in $deps) { Write-Host "      - $($d.Line.Trim())" }
        }
    }

    # Schema 锁定关键文件 (S0.A / S0.B / S0.7)
    $schemaFiles = @(
        "src\parrot\shared\event_log.py",
        "src\parrot\dsg\l1_5_protocol.py",
        "src\parrot\dsg\l2b_types.py"
    )
    foreach ($f in $schemaFiles) {
        $p = Join-Path $root $f
        if (Test-Path $p) { OK "Schema 文件存在: $f" } else { Fail "Schema 文件缺失: $f" }
    }

    # Unity manifest 版本锁定
    if (Test-Path $manifest) {
        $mj = Get-Content $manifest -Raw | ConvertFrom-Json
        $arfVer = $mj.dependencies.'com.unity.xr.arfoundation'
        $arcVer = $mj.dependencies.'com.unity.xr.arcore'
        $arkVer = $mj.dependencies.'com.unity.xr.arkit'
        $lkVer  = $mj.dependencies.'io.livekit.livekit-sdk'
        Write-Host "    Unity AR stack:"
        Write-Host "      - ARFoundation: $arfVer"
        Write-Host "      - ARCore:       $arcVer"
        Write-Host "      - ARKit:        $arkVer"
        Write-Host "      - LiveKit SDK:  $lkVer"
        if ($arfVer -and $arfVer.StartsWith("5.1")) {
            OK "AR Foundation 在 5.1.x, 符合 ar-foundation.mdc §1"
        } else {
            Fail "AR Foundation 非 5.1.x ($arfVer) — 违反 ar-foundation.mdc §1"
        }
        if ($arfVer -ne $arcVer -or $arfVer -ne $arkVer) {
            Fail "AR 三件套版本未对齐: arf=$arfVer arc=$arcVer ark=$arkVer"
        } else {
            OK "AR 三件套版本对齐"
        }
    } else {
        Warn "Unity manifest 未找到: $manifest"
    }

    # .venv 检查
    $venvPy = Join-Path $root ".venv\Scripts\python.exe"
    if (Test-Path $venvPy) {
        OK ".venv 存在"
        $pipList = & $venvPy -m pip list --format=freeze 2>$null
        $keyPkgs = @("pydantic", "livekit-agents", "redis", "py-trees", "graphiti-core")
        foreach ($pkg in $keyPkgs) {
            $hit = $pipList | Select-String -Pattern "^$pkg=="
            if ($hit) {
                OK "  $($hit.Line.Trim())"
            } else {
                Warn "  $pkg 未安装于 .venv"
            }
        }
    } else {
        Warn ".venv 不存在, 跳过 pip list"
    }
}

# ----------------------------------------------------------------------
#  Part B — Castle 远端审计
# ----------------------------------------------------------------------

if ($Remote) {
    Step "B" "Castle 远端审计 (SSH $CASTLE)"

    $reachable = $false
    try {
        $probe = ssh -o ConnectTimeout=10 $CASTLE "echo ok" 2>$null
        if ($probe -eq "ok") { $reachable = $true }
    } catch { }

    if (-not $reachable) {
        Fail "Castle 不可达 — 跳过远端审计"
    } else {
        OK "Castle SSH 可达"

        # Docker 容器清单 (parrot-redis / parrot-livekit / falkordb)
        Write-Host "    Docker 容器:"
        $cts = ssh $CASTLE "docker ps --format '{{.Names}} {{.Status}} {{.Image}}'" 2>$null
        if ($cts) {
            $cts | ForEach-Object { Write-Host "      $_" }
        } else {
            Warn "    Docker 无运行中容器 (或没权限)"
        }

        # 关键容器存活
        $wantCts = @("parrot-redis", "parrot-livekit", "falkordb")
        foreach ($name in $wantCts) {
            $alive = ssh $CASTLE "docker ps --format '{{.Names}}' | grep -w $name" 2>$null
            if ($alive) { OK "容器 $name 在跑" } else { Warn "容器 $name 未在跑" }
        }

        # Castle Python 版本 + 关键包
        $pyVer = ssh $CASTLE "cd /opt/parrotcarriers && .venv/bin/python --version 2>/dev/null || python3 --version" 2>$null
        Write-Host "    Castle Python: $pyVer"

        $pipHit = ssh $CASTLE "cd /opt/parrotcarriers && .venv/bin/pip list --format=freeze 2>/dev/null | grep -E '^(pydantic|livekit-agents|redis|py-trees|graphiti-core)=='" 2>$null
        if ($pipHit) {
            Write-Host "    Castle 关键包:"
            $pipHit -split "`n" | ForEach-Object { if ($_) { Write-Host "      - $_" } }
        } else {
            Warn "Castle .venv 未安装或 pip list 失败"
        }

        # FalkorDB 内存占用 (Castle 2C8G 硬约束)
        $mem = ssh $CASTLE "docker stats --no-stream --format '{{.Name}} {{.MemUsage}}' | grep falkor" 2>$null
        if ($mem) {
            Write-Host "    FalkorDB 内存: $mem"
        }

        # 最近 git commit 同步状态
        $remoteHead = ssh $CASTLE "cd /opt/parrotcarriers && git rev-parse HEAD" 2>$null
        $localHead = git rev-parse HEAD
        if ($remoteHead -and $localHead) {
            if ($remoteHead.Trim() -eq $localHead.Trim()) {
                OK "Castle git HEAD 与本地一致 ($($localHead.Substring(0,7)))"
            } else {
                Warn "Castle git HEAD 落后: remote=$($remoteHead.Substring(0,7)) local=$($localHead.Substring(0,7))"
            }
        }
    }
}

Write-Host "`n审计完成. 本脚本只报告, 不修复." -ForegroundColor Cyan
