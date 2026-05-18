param(
    [string]$Adb = "adb",
    [string]$Device = "",
    [switch]$Clear
)

$ErrorActionPreference = "Stop"

$adbArgs = @()
if (-not [string]::IsNullOrWhiteSpace($Device)) {
    $adbArgs += @("-s", $Device)
}

if ($Clear) {
    & $Adb @adbArgs logcat -c | Out-Null
}

Write-Host "[watch_rpc_smoke_logcat] devices:"
& $Adb devices
Write-Host "[watch_rpc_smoke_logcat] filtering Unity logs for RPC smoke markers. Ctrl+C to stop."

& $Adb @adbArgs logcat -v time Unity:D '*:S' |
    Select-String -Pattern 'RpcSmokeProbe|ParrotRPC|RoomManager|VideoStateReporter|AudioRoutePolicyBrainReporter|setCameraMode|setXrHandMode|onSceneReady|PerformRpc|RPC'
