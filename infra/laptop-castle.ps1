param(
    [ValidateSet("init", "config", "up", "up-brain", "down", "restart", "status", "logs", "unity-config")]
    [string]$Action = "status",
    [string]$Service = ""
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $ScriptDir "..")
$ComposeFile = Join-Path $ScriptDir "docker-compose.laptop.yml"
$EnvExample = Join-Path $ScriptDir "laptop.env.example"
$EnvLocal = Join-Path $ScriptDir "laptop.env.local"
$RuntimeRoot = Join-Path $RepoRoot "codex_workspace\local_runtime\castle_laptop"
$RuntimeData = Join-Path $RuntimeRoot "data"
$LiveKitTemplate = Join-Path $ScriptDir "livekit\livekit-laptop.template.yaml"
$LiveKitGenerated = Join-Path $RuntimeRoot "livekit-laptop.yaml"
$UnityConfigGenerated = Join-Path $RuntimeRoot "parrot_config.laptop.generated.json"

function Write-Utf8NoBom {
    param(
        [string]$Path,
        [string]$Text
    )

    $encoding = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllText($Path, $Text, $encoding)
}

function Get-LaptopLanIp {
    $configs = Get-NetIPConfiguration |
        Where-Object {
            $_.IPv4DefaultGateway -ne $null -and
            $_.NetAdapter.Status -eq "Up" -and
            $_.InterfaceAlias -match "WLAN|Wi-?Fi|Wireless|Ethernet" -and
            $_.InterfaceAlias -notmatch "vEthernet|WSL|Docker|VMware|VirtualBox|Loopback|Npcap|Mihomo|VPN|TAP|TUN"
        } |
        Sort-Object InterfaceMetric, InterfaceIndex

    foreach ($config in $configs) {
        foreach ($address in @($config.IPv4Address)) {
            if (Test-UsableLanAddress -HostIp $address.IPAddress) {
                return $address.IPAddress
            }
        }
    }

    $candidates = Get-NetIPAddress -AddressFamily IPv4 |
        Where-Object {
            $_.IPAddress -notmatch "^127\." -and
            $_.IPAddress -notmatch "^169\.254\." -and
            $_.PrefixOrigin -ne "WellKnown" -and
            $_.AddressState -eq "Preferred" -and
            $_.InterfaceAlias -notmatch "vEthernet|WSL|Docker|VMware|VirtualBox|Loopback|Npcap|Mihomo|VPN|TAP|TUN" -and
            (Test-UsableLanAddress -HostIp $_.IPAddress)
        } |
        Sort-Object InterfaceMetric, InterfaceIndex

    if ($candidates) { return $candidates[0].IPAddress }
    return "127.0.0.1"
}

function Test-UsableLanAddress {
    param([string]$HostIp)

    return -not [string]::IsNullOrWhiteSpace($HostIp) -and
        $HostIp -notmatch "^127\." -and
        $HostIp -notmatch "^169\.254\." -and
        $HostIp -notmatch "^198\.18\." -and
        $HostIp -notmatch "^198\.19\." -and
        $HostIp -notmatch "^100\.(6[4-9]|[7-9][0-9]|1[01][0-9]|12[0-7])\."
}

function Test-PhoneReachableHostCandidate {
    param([string]$HostIp)

    if (-not (Test-UsableLanAddress -HostIp $HostIp)) {
        return $false
    }
    $configs = Get-NetIPConfiguration |
        Where-Object {
            $_.IPv4DefaultGateway -ne $null -and
            $_.NetAdapter.Status -eq "Up" -and
            $_.InterfaceAlias -notmatch "vEthernet|WSL|Docker|VMware|VirtualBox|Loopback|Npcap|Mihomo|VPN|TAP|TUN"
        }
    foreach ($config in $configs) {
        foreach ($address in @($config.IPv4Address)) {
            if ($address.IPAddress -eq $HostIp) {
                return $true
            }
        }
    }
    return $false
}

function Read-LocalEnv {
    $map = [ordered]@{}
    if (-not (Test-Path -LiteralPath $EnvLocal)) {
        return $map
    }
    foreach ($line in Get-Content -LiteralPath $EnvLocal) {
        $trimmed = $line.Trim()
        if ($trimmed.Length -eq 0 -or $trimmed.StartsWith("#") -or -not $trimmed.Contains("=")) {
            continue
        }
        $key, $value = $trimmed.Split("=", 2)
        $map[$key.Trim()] = $value.Trim()
    }
    return $map
}

function Set-EnvValue {
    param(
        [string]$Key,
        [string]$Value
    )

    $lines = @()
    if (Test-Path -LiteralPath $EnvLocal) {
        $lines = @(Get-Content -LiteralPath $EnvLocal)
    }
    $written = $false
    $next = foreach ($line in $lines) {
        if ($line -match "^\s*$([regex]::Escape($Key))\s*=") {
            $written = $true
            "$Key=$Value"
        } else {
            $line
        }
    }
    if (-not $written) {
        $next += "$Key=$Value"
    }
    Set-Content -LiteralPath $EnvLocal -Value $next -Encoding UTF8
}

function Copy-SeedDir {
    param(
        [string]$Source,
        [string]$Destination
    )

    if (Test-Path -LiteralPath $Destination) {
        return
    }
    if (Test-Path -LiteralPath $Source) {
        Copy-Item -LiteralPath $Source -Destination $Destination -Recurse
    }
}

function Update-LocalRoomProfiles {
    param([string]$RoomId)

    if ([string]::IsNullOrWhiteSpace($RoomId)) {
        $RoomId = "parrot-laptop-main"
    }

    $presetDir = Join-Path $RuntimeData "presets"
    if (-not (Test-Path -LiteralPath $presetDir)) {
        return
    }

    foreach ($file in Get-ChildItem -LiteralPath $presetDir -Filter "*.json" -File) {
        try {
            $json = Get-Content -LiteralPath $file.FullName -Raw | ConvertFrom-Json
            if ($null -ne $json.PSObject.Properties["livekit_room_id"]) {
                $json.livekit_room_id = $RoomId
            } else {
                if ($null -eq $json.PSObject.Properties["metadata"] -or $null -eq $json.metadata) {
                    $json | Add-Member -NotePropertyName "metadata" -NotePropertyValue ([pscustomobject]@{})
                }
                if ($null -ne $json.metadata.PSObject.Properties["livekit_room_id"]) {
                    $json.metadata.livekit_room_id = $RoomId
                } else {
                    $json.metadata | Add-Member -NotePropertyName "livekit_room_id" -NotePropertyValue $RoomId
                }
            }
            Write-Utf8NoBom -Path $file.FullName -Text ($json | ConvertTo-Json -Depth 20)
        } catch {
            Write-Warning "Could not update local RoomProfile LiveKit room in $($file.Name): $($_.Exception.Message)"
        }
    }
}

function Initialize-LaptopCastle {
    New-Item -ItemType Directory -Force -Path $RuntimeRoot | Out-Null
    New-Item -ItemType Directory -Force -Path $RuntimeData | Out-Null

    if (-not (Test-Path -LiteralPath $EnvLocal)) {
        Copy-Item -LiteralPath $EnvExample -Destination $EnvLocal
    }

    $envMap = Read-LocalEnv
    $hostIp = $envMap["PARROT_LAPTOP_HOST"]
    if (-not (Test-PhoneReachableHostCandidate -HostIp $hostIp)) {
        $hostIp = Get-LaptopLanIp
        Set-EnvValue -Key "PARROT_LAPTOP_HOST" -Value $hostIp
        Set-EnvValue -Key "LIVEKIT_URL" -Value "ws://$hostIp`:17880"
    }

    Copy-SeedDir -Source (Join-Path $RepoRoot "data\presets") -Destination (Join-Path $RuntimeData "presets")
    Copy-SeedDir -Source (Join-Path $RepoRoot "data\line_profiles") -Destination (Join-Path $RuntimeData "line_profiles")
    Copy-SeedDir -Source (Join-Path $RepoRoot "data\registries") -Destination (Join-Path $RuntimeData "registries")
    Update-LocalRoomProfiles -RoomId $envMap["LIVEKIT_ROOM"]

    if (-not (Test-Path -LiteralPath (Join-Path $RuntimeData "runtime_config.json"))) {
        $runtimeConfig = [ordered]@{
            schema_version = 1
            updated_at = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
            updated_by = "laptop-castle.init"
            line_id = "line_a"
            room_profile_id = "default"
            notes = "Local laptop Castle sandbox; safe to delete."
        }
        Write-Utf8NoBom -Path (Join-Path $RuntimeData "runtime_config.json") -Text ($runtimeConfig | ConvertTo-Json -Depth 5)
    }

    $template = Get-Content -LiteralPath $LiveKitTemplate -Raw
    Write-Utf8NoBom -Path $LiveKitGenerated -Text ($template.Replace("__PARROT_LAPTOP_HOST__", $hostIp))

    Write-UnityConfig | Out-Null
    Write-Host "Laptop Castle initialized at $RuntimeRoot"
    Write-Host "Phone-facing host: $hostIp"
    Write-Host "Unity config generated at $UnityConfigGenerated"
}

function Docker-ComposeArgs {
    return @(
        "--env-file", $EnvLocal,
        "-p", "parrot-laptop-castle",
        "-f", $ComposeFile
    )
}

function Invoke-LaptopCompose {
    param([string[]]$ComposeCommandArgs)
    $composeArgs = Docker-ComposeArgs
    docker compose @composeArgs @ComposeCommandArgs
}

function Write-UnityConfig {
    $envMap = Read-LocalEnv
    $hostIp = $envMap["PARROT_LAPTOP_HOST"]
    if ([string]::IsNullOrWhiteSpace($hostIp)) {
        $hostIp = Get-LaptopLanIp
    }

    $config = [ordered]@{
        mintUrl = "http://$hostIp`:17888"
        mintSecret = $envMap["PARROT_MINT_SECRET"]
        liveKitUrl = "ws://$hostIp`:17880"
        room = $envMap["LIVEKIT_ROOM"]
        appApiUrl = "http://$hostIp`:18790"
        appApiSecret = $envMap["PARROT_APP_MONITOR_SECRET"]
        orchestratorUrl = "http://$hostIp`:17890"
        orchestratorSecret = $envMap["PARROT_ORCH_SECRET"]
    }
    $json = $config | ConvertTo-Json -Depth 5
    Write-Utf8NoBom -Path $UnityConfigGenerated -Text $json
    Write-Output $json
}

function Show-Status {
    Invoke-LaptopCompose -ComposeCommandArgs @("ps")
    $envMap = Read-LocalEnv
    $hostIp = $envMap["PARROT_LAPTOP_HOST"]
    if ([string]::IsNullOrWhiteSpace($hostIp)) {
        return
    }
    $checks = @(
        "http://$hostIp`:17888/health",
        "http://$hostIp`:17890/health",
        "http://$hostIp`:18790/api/app/room-setting"
    )
    foreach ($url in $checks) {
        try {
            $result = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 3
            Write-Host "$url -> $($result.StatusCode)"
        } catch {
            Write-Host "$url -> unavailable ($($_.Exception.Message))"
        }
    }
}

switch ($Action) {
    "init" {
        Initialize-LaptopCastle
    }
    "config" {
        Initialize-LaptopCastle
        Invoke-LaptopCompose -ComposeCommandArgs @("config")
    }
    "up" {
        Initialize-LaptopCastle
        Invoke-LaptopCompose -ComposeCommandArgs @("up", "-d", "redis", "falkordb", "livekit", "token-mint", "app-monitor", "orchestrator")
    }
    "up-brain" {
        Initialize-LaptopCastle
        Invoke-LaptopCompose -ComposeCommandArgs @("--profile", "brain", "up", "-d")
    }
    "down" {
        Invoke-LaptopCompose -ComposeCommandArgs @("down")
    }
    "restart" {
        Initialize-LaptopCastle
        Invoke-LaptopCompose -ComposeCommandArgs @("restart")
    }
    "status" {
        Show-Status
    }
    "logs" {
        $args = @("logs", "--tail", "200", "-f")
        if (-not [string]::IsNullOrWhiteSpace($Service)) {
            $args += $Service
        }
        Invoke-LaptopCompose -ComposeCommandArgs $args
    }
    "unity-config" {
        Initialize-LaptopCastle | Out-Null
        Write-UnityConfig
    }
}
