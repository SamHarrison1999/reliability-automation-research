[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Set-Location $RepoRoot

$Required = @(
    'pyproject.toml',
    'docs/engineering-quality.md',
    'docs/observability/opentelemetry.md',
    'ansible/README.md',
    'observability/opentelemetry/collector-config.yaml',
    'tests/test_fit_probe.py',
    'tests/test_service.py',
    'scripts/run-psscriptanalyzer.ps1',
    'PSScriptAnalyzerSettings.psd1',
    '.yamllint'
)
$Missing = @($Required | Where-Object { -not (Test-Path -LiteralPath $_ -PathType Leaf) })
if ($Missing.Count -gt 0) { throw "Compliance check missing required files: $($Missing -join ', ')" }

$TextFiles = @('scripts', 'tests', 'analysis', 'experiments', 'system', 'ansible', 'observability', '.github') |
    ForEach-Object { Get-ChildItem -LiteralPath $_ -Recurse -File -ErrorAction SilentlyContinue }
$SecretPattern = '(?i)(password|secret|api[_-]?key|private[_-]?key)\s*[:=]\s*["'']?[^$\s{]'
$SecretMatches = @($TextFiles | Select-String -Pattern $SecretPattern)
if ($SecretMatches.Count -gt 0) { throw 'Compliance check found a possible hard-coded secret.' }

git diff --check
if ($LASTEXITCODE -ne 0) { throw 'git diff --check failed.' }
Write-Host 'Compliance checks passed.'
