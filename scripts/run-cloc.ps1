[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$OutputDir = Join-Path $RepoRoot 'tmp\quality'
$OutputFile = Join-Path $OutputDir 'cloc.json'

if (-not (Get-Command cloc -ErrorAction SilentlyContinue)) {
    throw 'CLOC is not installed. Install it with an OS package manager, then rerun this script.'
}

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
Push-Location $RepoRoot
try {
    & cloc --json --by-file '--exclude-dir=.git,.venv,tmp,results,upload' "--out=$OutputFile" .
} finally {
    Pop-Location
}
Write-Host "CLOC report written to $OutputFile"

