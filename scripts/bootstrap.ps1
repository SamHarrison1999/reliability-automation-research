[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$ProposalPath
)

$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent $PSScriptRoot

$Directories = @(
    'docs/proposal/source', 'docs/research-design', 'docs/literature',
    'docs/protocols', 'docs/ethics', 'docs/diagrams', 'docs/adr',
    'docs/templates', 'system', 'infrastructure', 'experiments/scenarios',
    'experiments/configurations', 'experiments/harness', 'data/raw',
    'data/processed', 'data/external', 'data/schemas', 'analysis',
    'scripts', 'tests', 'results/generated', 'results/figures', 'results/tables'
)

foreach ($Directory in $Directories) {
    New-Item -ItemType Directory -Force -Path (Join-Path $RepoRoot $Directory) | Out-Null
}

$Markers = @(
    'data/raw/.gitkeep', 'data/processed/.gitkeep', 'data/external/.gitkeep',
    'results/generated/.gitkeep', 'system/.gitkeep', 'infrastructure/.gitkeep',
    'experiments/scenarios/.gitkeep', 'experiments/configurations/.gitkeep',
    'experiments/harness/.gitkeep', 'data/schemas/.gitkeep', 'analysis/.gitkeep',
    'tests/.gitkeep'
)

foreach ($Marker in $Markers) {
    $MarkerPath = Join-Path $RepoRoot $Marker
    if (-not (Test-Path $MarkerPath)) {
        New-Item -ItemType File -Path $MarkerPath | Out-Null
    }
}

if ($ProposalPath) {
    if (-not (Test-Path -LiteralPath $ProposalPath -PathType Leaf)) {
        throw "Proposal not found: $ProposalPath"
    }
    $Destination = Join-Path $RepoRoot ('docs/proposal/source/' + (Split-Path -Leaf $ProposalPath))
    if (Test-Path -LiteralPath $Destination) {
        Write-Host "Keeping existing proposal: $Destination"
    } else {
        Copy-Item -LiteralPath $ProposalPath -Destination $Destination
        Write-Host "Copied proposal to: $Destination"
    }
}

git -C $RepoRoot rev-parse --is-inside-work-tree *> $null
if ($LASTEXITCODE -ne 0) {
    git -C $RepoRoot init -b main *> $null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Initialised Git repository on branch main: $RepoRoot"
    } else {
        git -C $RepoRoot init *> $null
        if ($LASTEXITCODE -eq 0) {
            git -C $RepoRoot branch -m main *> $null
            if ($LASTEXITCODE -eq 0) {
                Write-Host "Initialised Git repository on branch main: $RepoRoot"
            } else {
                Write-Warning 'Git was initialised but the branch could not be renamed to main.'
            }
        } else {
            Write-Warning 'Git could not be initialised in this directory. The scaffold was created; run git init locally when the directory is writable.'
        }
    }
} else {
    Write-Host "Keeping existing Git repository: $RepoRoot"
}

Write-Host 'Phase 0 repository bootstrap complete.'
Write-Host 'Run: .\scripts\verify-repository.ps1'
