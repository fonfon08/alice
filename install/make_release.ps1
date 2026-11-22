# Builds the distributable ALICE production zip.
# Usage: powershell -ExecutionPolicy Bypass -File install\make_release.ps1

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
$folderName = "ALICE-$version-win64"
$stage = Join-Path $releaseRoot $folderName
$zip = Join-Path $releaseRoot "$folderName.zip"

if (Test-Path $stage) { Remove-Item $stage -Recurse -Force }
if (Test-Path $zip) { Remove-Item $zip -Force }
New-Item -ItemType Directory -Force -Path $stage | Out-Null

function Invoke-Robocopy {
    param([string]$Source, [string]$Destination, [string[]]$ExcludeDirs = @(), [string[]]$ExcludeFiles = @())
    $args = @($Source, $Destination, "/E", "/NFL", "/NDL", "/NJH", "/NJS", "/NP", "/R:1", "/W:1")
    if ($ExcludeDirs.Count -gt 0) { $args += "/XD"; $args += $ExcludeDirs }
    if ($ExcludeFiles.Count -gt 0) { $args += "/XF"; $args += $ExcludeFiles }
    & robocopy @args | Out-Null
    if ($LASTEXITCODE -ge 8) { throw "robocopy failed ($LASTEXITCODE): $Source -> $Destination" }
}

Write-Host "[release] Staging $folderName ..."

Invoke-Robocopy -Source (Join-Path $Root "server") -Destination (Join-Path $stage "server") `
    -ExcludeDirs @((Join-Path $Root "server\.venv"), (Join-Path $Root "server\venv"), (Join-Path $Root "server\logs"), "__pycache__", ".pytest_cache") `
    -ExcludeFiles @("*.pyc", "*.pyo", "database.db", "*.key", "server.conf", "*.log")

Invoke-Robocopy -Source (Join-Path $Root "client\gui") -Destination (Join-Path $stage "client\gui") `
    -ExcludeDirs @((Join-Path $Root "client\gui\node_modules"), (Join-Path $Root "client\gui\dist"), (Join-Path $Root "client\gui\out"), (Join-Path $Root "client\gui\.electron-vite"), "__pycache__") `
    -ExcludeFiles @("config.json", "downloads.json", "*.log")

Invoke-Robocopy -Source (Join-Path $Root "implants") -Destination (Join-Path $stage "implants") `
    -ExcludeDirs @("nimcache", "__pycache__") `
    -ExcludeFiles @("*.o", "*.obj", "main.exe")

Invoke-Robocopy -Source (Join-Path $Root "install") -Destination (Join-Path $stage "install") `
    -ExcludeFiles @("make_release.ps1", "make_full_installer.ps1", "installer.nsi")

foreach ($file in @("alice.py", "alice.bat", "README.md", "LICENSE", "DISCLAIMER.md", "AUTHORS.md", "Iniciar Server.bat", "Parar Server.bat")) {
    Copy-Item (Join-Path $Root $file) $stage -Force
}

$installer = Join-Path $Root "client\gui\dist\ALICE.exe"
if (-not (Test-Path $installer)) { throw "Client installer not found: $installer (run npm run dist)" }
Copy-Item $installer (Join-Path $stage "client\ALICE-Setup-$version.exe") -Force

$readme = @"
ALICE $version - Windows x64
=============================

Conteudo
--------
  server\                 Team server (Python/FastAPI + SQLite)
  client\                 Instalador do console do operador
  client\gui\             Fontes do client (Electron/React)
  implants\               Fontes dos implants (Nim/Go)
  install\                Instaladores e scripts
  alice.py / alice.bat    Launcher (server / client / version)

Requisitos
----------
  - Windows 10/11 x64
  - Python 3.10+ no PATH
  - Node.js 20+ no PATH (somente para recompilar o client)

Instalacao
----------
  1. Extraia o zip e abra o terminal na pasta ALICE-$version-win64.
  2. install\windows.bat server
     install\windows.bat toolchain
  3. python alice.py server key add operator
  4. python alice.py server start
  5. Execute client\ALICE-Setup-$version.exe e abra o ALICE pelo menu Iniciar.
     Em ALICE > Servers > Add, cole a operator key (arquivo server\operator.key)
     e conecte em 127.0.0.1:9000.

Uso
---
  1. Crie um listener em ALICE > Listeners > Add (ex.: http na porta 8443).
  2. Compile um implant em ALICE > Implants > Add apontando para o listener.
  3. Execute o implant no alvo; a sessao aparece no Terminal.

Server no dia a dia
-------------------
  Iniciar Server.bat    sobe o server em background e reautentica o console
  Parar Server.bat      derruba o server e o console
  install\windows.bat toolchain   instala/atualiza Nim + MinGW

Observacoes
-----------
  - O server escuta em 0.0.0.0:9000 (painel/API). Listeners usam outra porta.
  - O banco SQLite e criado no primeiro start em server\infra\database\database.db.
  - Relatorios em PDF exigem o runtime GTK (WeasyPrint). HTML e JSON funcionam sem ele.
  - O client pode ser recompilado com: cd client\gui && npm install && npm run build

Licenca GPLv3. Veja LICENSE e DISCLAIMER.md.
"@
Set-Content -Path (Join-Path $stage "LEIA-ME.txt") -Value $readme -Encoding UTF8

Write-Host "[release] Creating zip ..."
& tar.exe -a -c -f $zip -C $releaseRoot $folderName
if ($LASTEXITCODE -ne 0) { throw "tar failed ($LASTEXITCODE)" }

$sizeMb = [math]::Round((Get-Item $zip).Length / 1MB, 1)
$hash = (Get-FileHash $zip -Algorithm SHA256).Hash
$files = (Get-ChildItem $stage -Recurse -File | Measure-Object).Count

Write-Host ""
Write-Host "[release] Done."
Write-Host "  zip    $zip"
Write-Host "  size   $sizeMb MB"
Write-Host "  files  $files"
Write-Host "  sha256 $hash"
