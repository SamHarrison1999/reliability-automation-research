[CmdletBinding()]
param(
    [string]$OutputRoot = 'results/fit-probe/raw'
)

$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

python experiments/harness/fit_probe.py --output-root $OutputRoot
if ($LASTEXITCODE -ne 0) {
    throw 'Phase 2 fit probe failed.'
}
