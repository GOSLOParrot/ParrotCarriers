param(
    [ValidateSet("show", "laptop", "ecs")]
    [string]$Target = "show",

    [switch]$RefreshEcsBackup
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$ActiveConfig = Join-Path $RepoRoot "unity\ArSpike\Assets\ParrotApp\Resources\parrot_config.json"
$LaptopConfig = Join-Path $RepoRoot "codex_workspace\local_runtime\castle_laptop\parrot_config.laptop.generated.json"
$ProfileDir = Join-Path $RepoRoot "codex_workspace\local_runtime\unity_app_configs"
$EcsBackup = Join-Path $ProfileDir "parrot_config.ecs.local.json"

function Read-JsonConfig([string]$Path) {
    if (-not (Test-Path $Path)) {
        throw "Config file not found: $Path"
    }

    return Get-Content -Raw -Path $Path -Encoding UTF8 | ConvertFrom-Json
}

function Test-IsEcsConfig($Config) {
    $urls = @(
        [string]$Config.mintUrl,
        [string]$Config.liveKitUrl,
        [string]$Config.appApiUrl,
        [string]$Config.orchestratorUrl
    )

    foreach ($url in $urls) {
        if ($url -match "8\.216\.45\.45" -or $url -match "parrot") {
            return $true
        }
    }

    return [string]$Config.room -eq "parrot-main"
}

function Write-SafeSummary([string]$Path, [string]$Label) {
    $config = Read-JsonConfig $Path
    $summary = [ordered]@{
        label = $Label
        path = $Path
        mintUrl = $config.mintUrl
        liveKitUrl = $config.liveKitUrl
        room = $config.room
        appApiUrl = $config.appApiUrl
        orchestratorUrl = $config.orchestratorUrl
        photoUploadUrl = $config.photoUploadUrl
        visualToolDevEnabled = $config.visualToolDevEnabled
        visualToolHttpEnabled = $config.visualToolHttpEnabled
        hasMintSecret = -not [string]::IsNullOrWhiteSpace([string]$config.mintSecret)
        hasAppApiSecret = -not [string]::IsNullOrWhiteSpace([string]$config.appApiSecret)
        hasOrchestratorSecret = -not [string]::IsNullOrWhiteSpace([string]$config.orchestratorSecret)
    }

    $summary | ConvertTo-Json -Depth 4
}

function Backup-EcsConfigIfPresent {
    if (-not (Test-Path $ActiveConfig)) {
        return
    }

    $active = Read-JsonConfig $ActiveConfig
    if (-not (Test-IsEcsConfig $active)) {
        return
    }

    if ((Test-Path $EcsBackup) -and -not $RefreshEcsBackup) {
        return
    }

    New-Item -ItemType Directory -Force -Path $ProfileDir | Out-Null
    Copy-Item -LiteralPath $ActiveConfig -Destination $EcsBackup -Force
    Write-Host "Backed up current ECS Unity config to gitignored local profile."
}

switch ($Target) {
    "show" {
        Write-SafeSummary $ActiveConfig "active"
        break
    }
    "laptop" {
        Backup-EcsConfigIfPresent
        if (-not (Test-Path $LaptopConfig)) {
            throw "Laptop config is missing. Run: powershell -ExecutionPolicy Bypass -File infra\laptop-castle.ps1 -Action unity-config"
        }

        Copy-Item -LiteralPath $LaptopConfig -Destination $ActiveConfig -Force
        Write-Host "Switched Unity active config to laptop Castle. Rebuild/reinstall the Android app before phone testing."
        Write-SafeSummary $ActiveConfig "active:laptop"
        break
    }
    "ecs" {
        if (-not (Test-Path $EcsBackup)) {
            throw "ECS backup config is missing at $EcsBackup. Restore your ignored ECS parrot_config.json there, or rerun while the active config is still ECS."
        }

        Copy-Item -LiteralPath $EcsBackup -Destination $ActiveConfig -Force
        Write-Host "Switched Unity active config to public ECS. Rebuild/reinstall the Android app before phone testing."
        Write-SafeSummary $ActiveConfig "active:ecs"
        break
    }
}
