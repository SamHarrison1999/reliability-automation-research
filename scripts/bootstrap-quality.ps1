[CmdletBinding()]
param(
    [switch]$WithInfrastructure
)

$ErrorActionPreference = 'Stop'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$VenvDir = Join-Path $RepoRoot '.venv'
$Python = if ($env:PYTHON_BIN) { $env:PYTHON_BIN } else { 'python' }

& $Python -m venv $VenvDir
$VenvPython = Join-Path $VenvDir 'Scripts\python.exe'
& $VenvPython -m pip install --upgrade pip
& $VenvPython -m pip install -e "$RepoRoot[dev]"

if ($WithInfrastructure) {
    & $VenvPython -m pip install -e "$RepoRoot[infrastructure]"

    if (Get-Command Install-Module -ErrorAction SilentlyContinue) {
        if (-not (Get-Module -ListAvailable -Name PSScriptAnalyzer)) {
            Install-Module -Name PSScriptAnalyzer -Scope CurrentUser -Force -AllowClobber
        }
    } else {
        Write-Warning 'PowerShellGet is unavailable; install PSScriptAnalyzer separately.'
    }
}

Write-Host 'Python quality environment is ready.'
Write-Host 'Run: .\scripts\run-quality-checks.ps1'
Write-Host 'Install CLOC, ShellCheck and kubeconform with an OS/package manager before strict infrastructure validation.'
