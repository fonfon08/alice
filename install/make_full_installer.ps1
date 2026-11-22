# Builds the all-in-one ALICE installer (server + client + toolchain + key + autostart).
# Usage: powershell -ExecutionPolicy Bypass -File install\make_full_installer.ps1

param(
    [string]$Root = (Resolve-Path "$PSScriptRoot\..").Path
)

$ErrorActionPreference = "Stop"

$version = "0.0.0"
$versionPy = Join-Path $Root "server\version.py"
foreach ($line in Get-Content $versionPy) {
    if ($line -match '__version__\s*=\s*"([^"]+)"') { $version = $Matches[1]; break }
}

$releaseRoot = Join-Path (Split-Path $Root -Parent) "release"
$staging = Join-Path $releaseRoot "ALICE-$version-win64"
$payload = Join-Path $releaseRoot "_payload"
$out = Join-Path $releaseRoot "ALICE-Full-Setup-$version.exe"

Write-Host "[installer] Refreshing release staging..."
& powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot "make_release.ps1")
if ($LASTEXITCODE -ne 0) { throw "make_release.ps1 failed" }
if (-not (Test-Path $staging)) { throw "Staging not found: $staging" }

if (Test-Path $payload) { Remove-Item $payload -Recurse -Force }
New-Item -ItemType Directory -Force -Path $payload | Out-Null

Write-Host "[installer] Staging payload..."
& robocopy $staging $payload /E /NFL /NDL /NJH /NJS /NP /R:1 /W:1 | Out-Null
if ($LASTEXITCODE -ge 8) { throw "robocopy failed staging the payload" }

# The all-in-one installer ships the unpacked client, not the nested NSIS setup
Remove-Item (Join-Path $payload "client\ALICE-Setup-$version.exe") -Force -ErrorAction SilentlyContinue
Remove-Item (Join-Path $payload "client\gui") -Recurse -Force -ErrorAction SilentlyContinue

$winUnpacked = Join-Path $Root "client\gui\dist\win-unpacked"
if (-not (Test-Path (Join-Path $winUnpacked "ALICE.exe"))) {
    throw "Client build not found: $winUnpacked (run npm run dist)"
}
Write-Host "[installer] Copying the client build (win-unpacked)..."
& robocopy $winUnpacked (Join-Path $payload "client\app") /E /NFL /NDL /NJH /NJS /NP /R:1 /W:1 | Out-Null
if ($LASTEXITCODE -ge 8) { throw "robocopy failed copying win-unpacked" }

# Do not ship local client state; the installer writes config.json when it starts the server
Remove-Item (Join-Path $payload "client\app\config.json") -Force -ErrorAction SilentlyContinue
Remove-Item (Join-Path $payload "client\app\downloads.json") -Force -ErrorAction SilentlyContinue

Write-Host "[installer] Refreshing setup helpers..."
foreach ($file in @("setup_server.bat", "setup_toolchain.bat", "start_server.ps1", "start_server.vbs", "stop_server.ps1")) {
    Copy-Item (Join-Path $Root "install\$file") (Join-Path $payload "install") -Force
}
foreach ($file in @("Iniciar Server.bat", "Parar Server.bat")) {
    Copy-Item (Join-Path $Root $file) $payload -Force
}

# makensis reads UTF-8 scripts only with a BOM
$nsi = Join-Path $Root "install\installer.nsi"
$text = [System.IO.File]::ReadAllText($nsi)
[System.IO.File]::WriteAllText($nsi, $text, (New-Object System.Text.UTF8Encoding($true)))

$makensis = (Get-ChildItem "$env:LOCALAPPDATA\electron-builder\Cache" -Recurse -Filter makensis.exe -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -match '\\Bin\\makensis\.exe$' } |
    Select-Object -First 1).FullName
if (-not $makensis) { throw "makensis.exe not found in the electron-builder cache" }

$icon = Join-Path $Root "client\gui\public\icon.ico"
if (Test-Path $out) { Remove-Item $out -Force }

Write-Host "[installer] Compiling with makensis (solid LZMA, this takes a while)..."
& $makensis /V2 "/DVERSION=$version" "/DPAYLOAD=$payload" "/DOUTFILE=$out" "/DICON=$icon" $nsi
if ($LASTEXITCODE -ne 0) { throw "makensis failed ($LASTEXITCODE)" }

$sizeMb = [math]::Round((Get-Item $out).Length / 1MB, 1)
$hash = (Get-FileHash $out -Algorithm SHA256).Hash

Remove-Item $payload -Recurse -Force -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "[installer] Done."
Write-Host "  exe    $out"
Write-Host "  size   $sizeMb MB"
Write-Host "  sha256 $hash"
