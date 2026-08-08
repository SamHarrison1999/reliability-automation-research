[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

$Required = @(
    'README.md', '.gitignore', '.gitattributes', '.editorconfig', 'Makefile',
    'docs/research-design/phase-0.md', 'docs/roadmap.md', 'docs/progress-ledger.md',
    'docs/literature/evidence-matrix.csv', 'docs/literature/phase-1-review-protocol.md',
    'docs/literature/search-log.csv', 'docs/literature/screening-log.csv',
    'docs/literature/references.bib', 'docs/adr/0001-repository-boundaries.md',
    'docs/adr/0002-provisional-technology-selection.md',
    'docs/research-design/phase-2.md', 'docs/technology-selection/README.md',
    'docs/technology-selection/selection-matrix.csv', 'docs/technology-selection/source-register.md',
    'docs/adr/0003-candidate-system-selection.md', 'docs/adr/0004-experimental-deployment-model.md',
    'docs/adr/0005-observability-and-provenance-boundary.md', 'docs/adr/0006-fault-injection-boundary.md',
    'docs/protocols/phase-2-fit-probe.md',
    'docs/diagrams/phase-2-candidate-architecture.mmd', 'docs/diagrams/phase-2-experiment-control-flow.mmd',
    'scripts/bootstrap.sh', 'scripts/bootstrap.ps1', 'scripts/verify-repository.sh',
    '.github/workflows/validate-repository.yml'
)

$Missing = @($Required | Where-Object { -not (Test-Path -LiteralPath $_ -PathType Leaf) })
if ($Missing.Count -gt 0) {
    throw "Missing required files: $($Missing -join ', ')"
}

$ScanFiles = @('README.md') + @(Get-ChildItem docs, .github -Recurse -File | ForEach-Object { $_.FullName })
$PlaceholderMatches = Select-String -Path $ScanFiles -Pattern 'TODO|TBD|REPLACE_ME'
if ($PlaceholderMatches) {
    throw 'Unexpected unresolved placeholder found in committed scaffolding.'
}

$ProtectedFiles = @(
    @(Get-ChildItem data/raw, data/processed, data/external, results/generated -Recurse -File -ErrorAction SilentlyContinue) |
        Where-Object { $_.Name -ne '.gitkeep' }
)
if ($ProtectedFiles.Count -gt 0) {
    throw 'Generated or research data is present in a protected data directory.'
}

git -C $RepoRoot rev-parse --is-inside-work-tree *> $null
if ($LASTEXITCODE -eq 0) {
    git diff --check
    if ($LASTEXITCODE -ne 0) { throw 'git diff --check failed' }
} else {
    Write-Warning 'Git validation skipped: this directory is not a valid Git repository.'
}

Write-Host 'Repository verification passed.'
Write-Host 'Phase: 2 - software-system and technology selection.'
Write-Host 'Application implementation: intentionally absent.'
