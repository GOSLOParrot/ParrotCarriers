<#
.SYNOPSIS
    Verify all native .so libraries in an APK / AAB / directory are 16KB ELF page-aligned (Android 15+ requirement).

.DESCRIPTION
    Walks the given path looking for *.so files (recursively) and runs `llvm-objdump -p` on each.
    A library is OK only if every LOAD segment reports `align 2**14` (i.e. 16384 bytes).
    Any library reporting a smaller alignment (`2**12` = 4 KB, `2**13` = 8 KB) is a Play-Store blocker
    on Android 15+ ARM64 devices.

.PARAMETER Path
    File or directory. Supported:
      - Path to a directory containing .so files (recursive scan).
      - Path to an .apk / .aab — it will be temporarily extracted to %TEMP% via `Expand-Archive`
        (zip-format), and arm64-v8a/*.so will be checked.

.PARAMETER NdkRoot
    Optional. Override the auto-detected Android NDK location. If omitted, falls back to
    $env:ANDROID_NDK_HOME → $env:ANDROID_NDK_ROOT.

.EXAMPLE
    pwsh tools/verify_so_alignment.ps1 unity/ArSpike/Library/PackageCache/io.livekit.livekit-sdk@7d868ef/Runtime/Plugins

.EXAMPLE
    pwsh tools/verify_so_alignment.ps1 build/parrot-arspike.apk

.NOTES
    Author: ParrotCarriers / Sprint4 Phase 3 platform-version patch (2026-04-29)
    Reference: https://developer.android.com/guide/practices/page-sizes
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true, Position=0)]
    [string]$Path,

    [string]$NdkRoot = ""
)

$ErrorActionPreference = "Stop"

function Resolve-Objdump {
    param([string]$ndk)

    if ([string]::IsNullOrEmpty($ndk)) {
        if ($env:ANDROID_NDK_HOME) { $ndk = $env:ANDROID_NDK_HOME }
        elseif ($env:ANDROID_NDK_ROOT) { $ndk = $env:ANDROID_NDK_ROOT }
    }

    if ([string]::IsNullOrEmpty($ndk)) {
        throw "ANDROID_NDK_HOME / ANDROID_NDK_ROOT not set, and -NdkRoot not provided."
    }

    $hostDir = if ($IsWindows -or $env:OS -eq "Windows_NT") { "windows-x86_64" }
               elseif ($IsMacOS) { "darwin-x86_64" }
               else { "linux-x86_64" }

    $exe = if ($IsWindows -or $env:OS -eq "Windows_NT") { "llvm-objdump.exe" } else { "llvm-objdump" }

    $candidate = Join-Path $ndk "toolchains/llvm/prebuilt/$hostDir/bin/$exe"
    if (-not (Test-Path $candidate)) {
        throw "llvm-objdump not found at: $candidate"
    }
    return $candidate
}

function Test-So16KB {
    param(
        [string]$objdump,
        [System.IO.FileInfo]$so
    )

    $output = & $objdump -p $so.FullName 2>&1
    $loads  = $output | Select-String -Pattern '^\s*LOAD\s' -CaseSensitive

    if ($loads.Count -eq 0) {
        return [pscustomobject]@{
            File   = $so.FullName
            Status = "NO_LOAD_SEG"
            Detail = "objdump produced no LOAD segments (not an ELF? wrong arch?)"
            Ok     = $false
        }
    }

    $bad = @()
    foreach ($line in $loads) {
        if ($line.Line -notmatch 'align\s+2\*\*(\d+)') {
            $bad += "no align field: $($line.Line.Trim())"
            continue
        }
        $exp = [int]$Matches[1]
        if ($exp -lt 14) {
            $bad += "align 2**$exp ($([math]::Pow(2, $exp)) bytes)"
        }
    }

    if ($bad.Count -gt 0) {
        return [pscustomobject]@{
            File   = $so.FullName
            Status = "BAD"
            Detail = ($bad -join "; ")
            Ok     = $false
        }
    }
    return [pscustomobject]@{
        File   = $so.FullName
        Status = "OK_16KB"
        Detail = ""
        Ok     = $true
    }
}

# -------- main --------

$objdump = Resolve-Objdump -ndk $NdkRoot
Write-Host "Using objdump: $objdump" -ForegroundColor DarkGray

if (-not (Test-Path $Path)) {
    throw "Path not found: $Path"
}

$item = Get-Item $Path
$scanRoot = $null
$tempExtracted = $false

if ($item.PSIsContainer) {
    $scanRoot = $item.FullName
}
elseif ($item.Extension -in @(".apk", ".aab", ".zip")) {
    $tmp = Join-Path $env:TEMP ("verify_so_" + [System.Guid]::NewGuid().ToString("N"))
    New-Item -ItemType Directory -Path $tmp | Out-Null
    Write-Host "Extracting $($item.Name) → $tmp ..." -ForegroundColor DarkGray
    Copy-Item $item.FullName (Join-Path $tmp ($item.BaseName + ".zip"))
    Expand-Archive -Path (Join-Path $tmp ($item.BaseName + ".zip")) -DestinationPath $tmp -Force
    $scanRoot = $tmp
    $tempExtracted = $true
}
else {
    # Single .so file
    if ($item.Extension -ne ".so") {
        throw "Unsupported file type: $($item.Extension). Pass a directory, .apk/.aab, or single .so."
    }
    $scanRoot = $item.DirectoryName
}

$soFiles = Get-ChildItem -Path $scanRoot -Recurse -Filter *.so -ErrorAction SilentlyContinue
if ($soFiles.Count -eq 0) {
    Write-Host "No .so files found under $scanRoot" -ForegroundColor Yellow
    if ($tempExtracted) { Remove-Item -Recurse -Force $scanRoot -ErrorAction SilentlyContinue }
    exit 0
}

Write-Host ""
Write-Host "Scanning $($soFiles.Count) .so file(s) ..." -ForegroundColor Cyan
Write-Host ("-" * 100)

$results = foreach ($so in $soFiles) {
    Test-So16KB -objdump $objdump -so $so
}

foreach ($r in $results) {
    $rel = $r.File
    if ($rel.Length -gt 80) { $rel = "..." + $rel.Substring($rel.Length - 77) }
    $color = if ($r.Ok) { "Green" } else { "Red" }
    Write-Host ("[{0,-10}] {1}" -f $r.Status, $rel) -ForegroundColor $color
    if ($r.Detail) { Write-Host ("            → " + $r.Detail) -ForegroundColor DarkYellow }
}

Write-Host ("-" * 100)
$bad = @($results | Where-Object { -not $_.Ok })
$ok  = @($results | Where-Object { $_.Ok })

Write-Host ("Summary: {0} OK / {1} BAD (out of {2} total)" -f $ok.Count, $bad.Count, $results.Count) `
    -ForegroundColor (if ($bad.Count -gt 0) { "Red" } else { "Green" })

if ($tempExtracted) {
    Remove-Item -Recurse -Force $scanRoot -ErrorAction SilentlyContinue
}

if ($bad.Count -gt 0) { exit 1 } else { exit 0 }
