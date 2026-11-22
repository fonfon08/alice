param(
    [string]$Root = (Resolve-Path "$PSScriptRoot\..").Path
)

# Kills only processes whose executable lives under this install (venv python, console, workers)
$root = (Resolve-Path $Root).Path.TrimEnd('\')

$targets = @()
$targets += Get-Process -Name python, pythonw -ErrorAction SilentlyContinue
$targets += Get-Process -Name ALICE -ErrorAction SilentlyContinue

foreach ($process in $targets) {
    try {
        if ($process.Path -and $process.Path.StartsWith($root, [System.StringComparison]::OrdinalIgnoreCase)) {
            Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
        }
    } catch {
    }
}

exit 0
