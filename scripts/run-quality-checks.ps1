[CmdletBinding()]
param(
    [switch]$PythonOnly,
    [switch]$StrictInfrastructure
)

$ErrorActionPreference = 'Stop'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$VenvPython = if ($env:PYTHON_BIN) {
    $env:PYTHON_BIN
} elseif (Test-Path -LiteralPath (Join-Path $RepoRoot '.venv\Scripts\python.exe') -PathType Leaf) {
    Join-Path $RepoRoot '.venv\Scripts\python.exe'
} else {
    $PythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if ($PythonCommand) { $PythonCommand.Source } else { $null }
}

if ([string]::IsNullOrWhiteSpace($VenvPython) -or -not (Test-Path -LiteralPath $VenvPython -PathType Leaf)) {
    throw 'Python interpreter not found. Install Python or run .\scripts\bootstrap-quality.ps1 first.'
}

$VenvBin = Split-Path -Parent $VenvPython
$env:Path = "$VenvBin;$env:Path"
$RunId = [Guid]::NewGuid().ToString('N')
$QualityTempRoot = Join-Path $RepoRoot 'tmp\quality'
$PytestBaseTemp = Join-Path $QualityTempRoot "pytest-$RunId"
$PipAuditCache = Join-Path $QualityTempRoot "pip-audit-cache-$RunId"
New-Item -ItemType Directory -Force -Path $PytestBaseTemp, $PipAuditCache | Out-Null

function Invoke-CheckedCommand {
    param(
        [Parameter(Mandatory)]
        [string]$Command,

        [Parameter(Mandatory)]
        [object[]]$Arguments
    )

    & $Command @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "$Command failed with exit code $LASTEXITCODE."
    }
}

Set-Location $RepoRoot
Invoke-CheckedCommand -Command $VenvPython -Arguments @('-m', 'ruff', 'check', 'experiments', 'system', 'tests')
Invoke-CheckedCommand -Command $VenvPython -Arguments @('-m', 'ruff', 'format', '--check', 'experiments', 'system', 'tests')
Invoke-CheckedCommand -Command $VenvPython -Arguments @('-m', 'mypy', 'experiments', 'system', 'tests')
Invoke-CheckedCommand -Command $VenvPython -Arguments @(
    '-m', 'pytest',
    '--basetemp', $PytestBaseTemp,
    '--cov=experiments.harness.fit_probe',
    '--cov=experiments.harness.kubernetes_fit_probe',
    '--cov=system.orderflow.service',
    '--cov-branch', '--cov-report=term-missing', '--cov-fail-under=100'
)
Invoke-CheckedCommand -Command $VenvPython -Arguments @('-m', 'bandit', '-q', '-r', 'experiments', 'system', '-s', 'B310,B404,B603,B607')
Invoke-CheckedCommand -Command $VenvPython -Arguments @('-m', 'pip_audit', '--cache-dir', $PipAuditCache)
& (Join-Path $PSScriptRoot 'check-compliance.ps1')
if ($LASTEXITCODE -ne 0) {
    throw 'check-compliance.ps1 failed.'
}

if (-not $PythonOnly) {
    if ($StrictInfrastructure) {
        & (Join-Path $PSScriptRoot 'validate-infrastructure.ps1') -Strict
    } else {
        & (Join-Path $PSScriptRoot 'validate-infrastructure.ps1')
    }
    & (Join-Path $PSScriptRoot 'run-cloc.ps1')
}

Write-Host 'Quality checks passed.'
