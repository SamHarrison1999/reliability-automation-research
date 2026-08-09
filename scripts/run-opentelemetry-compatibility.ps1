[CmdletBinding()]
param(
    [switch]$KeepStack,
    [int]$SpanCount = 5
)

$ErrorActionPreference = 'Stop'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$ComposeFile = Join-Path $RepoRoot 'observability\opentelemetry\docker-compose.compatibility.yml'
$Python = if ($env:PYTHON_BIN) { $env:PYTHON_BIN } else { 'python' }

Set-Location $RepoRoot
& $Python -m pip install -e "$RepoRoot[observability]"
& docker compose -f $ComposeFile up -d --build
if ($LASTEXITCODE -ne 0) { throw 'Docker Compose could not start the OpenTelemetry compatibility stack.' }

try {
    & $Python (Join-Path $RepoRoot 'observability\opentelemetry\compatibility_probe.py') `
        --span-count $SpanCount
    if ($LASTEXITCODE -ne 0) { throw 'The OpenTelemetry compatibility probe failed.' }
}
finally {
    if (-not $KeepStack) {
        & docker compose -f $ComposeFile down --volumes
    }
}
