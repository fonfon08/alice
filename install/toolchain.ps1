param(
    [string]$Root = (Resolve-Path "$PSScriptRoot\..").Path
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$toolchain = Join-Path $Root "toolchain"
New-Item -ItemType Directory -Force -Path $toolchain | Out-Null

$nimVersion = "2.4.2"
$mingwUrl = "https://github.com/brechtsanders/winlibs_mingw/releases/download/16.2.0posix-23.1.3-14.0.0-ucrt-r3/winlibs-x86_64-posix-seh-gcc-16.2.0-mingw-w64ucrt-14.0.0-r3.zip"

$nimDir = Join-Path $toolchain "nim-$nimVersion"
$mingwDir = Join-Path $toolchain "mingw64"

if (-not (Test-Path (Join-Path $nimDir "bin\nim.exe"))) {
    Write-Host "[toolchain] Downloading Nim $nimVersion..."
    $zip = Join-Path $toolchain "nim.zip"
    Invoke-WebRequest -Uri "https://nim-lang.org/download/nim-$($nimVersion)_x64.zip" -OutFile $zip
    Write-Host "[toolchain] Extracting Nim..."
    tar -xf $zip -C $toolchain
    Remove-Item $zip -Force
} else {
    Write-Host "[toolchain] Nim found."
}

if (-not (Test-Path (Join-Path $mingwDir "bin\gcc.exe"))) {
    Write-Host "[toolchain] Downloading MinGW-w64 (WinLibs)..."
    $zip = Join-Path $toolchain "winlibs.zip"
    Invoke-WebRequest -Uri $mingwUrl -OutFile $zip
    Write-Host "[toolchain] Extracting MinGW-w64..."
    tar -xf $zip -C $toolchain
    Remove-Item $zip -Force
} else {
    Write-Host "[toolchain] MinGW-w64 found."
}

$nim = Join-Path $nimDir "bin\nim.exe"
$gcc = Join-Path $mingwDir "bin\gcc.exe"
if (-not (Test-Path $nim)) { throw "nim.exe missing after install" }
if (-not (Test-Path $gcc)) { throw "gcc.exe missing after install" }

Write-Host "[toolchain] Ready:"
Write-Host "  nim  $nim"
Write-Host "  gcc  $gcc"
