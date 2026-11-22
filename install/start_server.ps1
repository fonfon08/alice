param(
    [string]$Root = (Resolve-Path "$PSScriptRoot\..").Path
)

$ErrorActionPreference = "Stop"

$root = (Resolve-Path $Root).Path
$serverDir = Join-Path $root "server"
$statusPath = Join-Path $root "install-start.ok"
Remove-Item $statusPath -Force -ErrorAction SilentlyContinue
$python = @(
    (Join-Path $root ".venv\Scripts\python.exe"),
    (Join-Path $serverDir ".venv\Scripts\python.exe"),
    (Join-Path $root "venv\Scripts\python.exe")
) | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1

if (-not $python) {
    Write-Error "Python virtualenv not found under $root"
    exit 1
}

function Test-Port([int]$Port) {
    # Fast localhost port probe, no DNS, 800 ms ceiling
    try {
        $client = New-Object System.Net.Sockets.TcpClient
        $iar = $client.BeginConnect("127.0.0.1", $Port, $null, $null)
        if (-not $iar.AsyncWaitHandle.WaitOne(800)) { $client.Close(); return $false }
        $client.EndConnect($iar)
        $client.Close()
        return $true
    } catch {
        return $false
    }
}

# Firewall (best effort, needs admin; at logon it just no-ops if the rule exists)
foreach ($rule in @(@{ Name = "ALICE Server"; Port = 9000 }, @{ Name = "ALICE Listener"; Port = 8443 })) {
    & netsh advfirewall firewall delete rule name="$($rule.Name)" 2>$null | Out-Null
    & netsh advfirewall firewall add rule name="$($rule.Name)" dir=in action=allow protocol=TCP localport=$($rule.Port) 2>$null | Out-Null
}

$started = $false
if (-not (Test-Port 9000)) {
    $logDir = Join-Path $serverDir "logs"
    New-Item -ItemType Directory -Force -Path $logDir | Out-Null
    Start-Process -FilePath $python -ArgumentList @("`"$root\alice.py`"", "server", "start") `
        -WorkingDirectory $root -WindowStyle Hidden `
        -RedirectStandardOutput (Join-Path $logDir "server.out.log") `
        -RedirectStandardError (Join-Path $logDir "server.err.log") | Out-Null
    $started = $true

    $deadline = (Get-Date).AddSeconds(90)
    while ((Get-Date) -lt $deadline -and -not (Test-Port 9000)) {
        Start-Sleep -Milliseconds 500
    }
}

if (-not (Test-Port 9000)) {
    Write-Error "Server did not open port 9000"
    exit 1
}

$keyPath = Join-Path $serverDir "operator.key"
if (-not (Test-Path -LiteralPath $keyPath)) {
    Write-Error "operator.key not found: $keyPath"
    exit 1
}

$key = (Get-Content -LiteralPath $keyPath -Raw).Trim()
$parts = $key.Split(":")
if ($parts.Count -lt 3) {
    Write-Error "Invalid operator key"
    exit 1
}

$token = $null
$body = @{ operator_key = $key } | ConvertTo-Json -Compress
for ($i = 0; $i -lt 30; $i++) {
    try {
        $response = Invoke-RestMethod -Uri "http://127.0.0.1:9000/auth/login" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 10
        if ($response.access_token) { $token = $response.access_token; break }
    } catch {
        Start-Sleep -Milliseconds 500
    }
}

if (-not $token) {
    Write-Error "Login failed on http://127.0.0.1:9000/auth/login"
    exit 1
}

$clientExe = Join-Path $root "client\app\ALICE.exe"
if (Test-Path -LiteralPath $clientExe) {
    $config = @{
        servers = @(
            @{
                id     = "local"
                name   = $parts[0]
                ip     = "http://127.0.0.1"
                port   = "9000"
                user   = $parts[0]
                pass   = $parts[1]
                secret = $parts[2]
                token  = $token
            }
        )
    } | ConvertTo-Json -Depth 5
    $utf8 = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText((Join-Path $root "client\app\config.json"), $config, $utf8)
}

Write-Output "ALICE server ready: http://127.0.0.1:9000"
Write-Output "Operator key: $keyPath"
if ($started) { Write-Output "Server started in background." } else { Write-Output "Server was already running." }
Set-Content -Path $statusPath -Value (Get-Date -Format o) -Encoding ASCII
exit 0
