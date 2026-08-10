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
    'docs/fit-probe/phase-2-fit-probe-results.md', 'data/schemas/technical-event-record.md',
    'infrastructure/local-fit-probe.json', 'infrastructure/kubernetes/orderflow-fit-probe.yaml',
    'infrastructure/kubernetes/Dockerfile', 'infrastructure/kubernetes/entrypoint.sh',
    'experiments/scenarios/no-fault.json', 'experiments/scenarios/service-termination.json',
    'experiments/scenarios/dependency-latency.json', 'experiments/harness/fit_probe.py',
    'experiments/harness/kubernetes_fit_probe.py',
    'system/orderflow/service.py', 'scripts/run-phase-2-fit-probe.sh', 'scripts/run-phase-2-fit-probe.ps1',
    'scripts/run-phase-2-kubernetes-fit-probe.ps1',
    'docs/diagrams/phase-2-candidate-architecture.mmd', 'docs/diagrams/phase-2-experiment-control-flow.mmd',
    'scripts/bootstrap.sh', 'scripts/bootstrap.ps1', 'scripts/verify-repository.sh',
    'pyproject.toml', 'tests/test_fit_probe.py', 'tests/test_service.py',
    'docs/engineering-quality.md', 'docs/observability/opentelemetry.md',
    'ansible/README.md', 'ansible/ansible.cfg', 'ansible/inventory/local.yml', 'ansible/site.yml',
    'observability/opentelemetry/README.md', 'observability/opentelemetry/collector-config.yaml',
    'scripts/bootstrap-quality.sh', 'scripts/bootstrap-quality.ps1',
    'scripts/run-quality-checks.sh', 'scripts/run-quality-checks.ps1',
    'scripts/check-compliance.sh', 'scripts/check-compliance.ps1',
    'scripts/run-cloc.sh', 'scripts/run-cloc.ps1',
    'scripts/validate-infrastructure.sh', 'scripts/validate-infrastructure.ps1',
    'scripts/run-psscriptanalyzer.ps1', 'PSScriptAnalyzerSettings.psd1',
    '.github/workflows/quality.yml', '.yamllint',
    '.github/workflows/validate-repository.yml',
    'docs/research-design/phase-4.md', 'docs/reproducibility/phase-4-validation.md',
    'docs/adr/0013-phase-4-build-provenance.md', 'docs/adr/0014-phase-4-opentelemetry-runtime.md',
    'infrastructure/prototype/orderflow-phase-4.json', 'infrastructure/kubernetes/orderflow-phase-4.yaml',
    'experiments/harness/phase_4_reproducibility.py', 'system/orderflow/otel_runtime.py',
    'observability/opentelemetry/phase4-requirements.lock',
    'results/phase-4/phase-4-reproducibility-summary.json',
    'results/phase-4/raw/phase4-repro-20260810T134202072483Z-5a519a99/validity.json',
    'results/phase-4/raw/phase4-repro-20260810T134202072483Z-5a519a99/metadata.json',
    'results/phase-4/raw/phase4-repro-20260810T134202072483Z-5a519a99/workload.json',
    'results/phase-4/raw/phase4-repro-20260810T134202072483Z-5a519a99/otel-spans.json',
    'results/phase-4/raw/phase4-repro-20260810T134620018339Z-4efc01f5/validity.json',
    'results/phase-4/raw/phase4-repro-20260810T134620018339Z-4efc01f5/metadata.json',
    'results/phase-4/raw/phase4-repro-20260810T134620018339Z-4efc01f5/workload.json',
    'results/phase-4/raw/phase4-repro-20260810T134620018339Z-4efc01f5/otel-spans.json',
    'tests/test_phase4_prototype.py', 'tests/test_phase4_kubernetes_manifest.py',
    'tests/test_phase4_otel_runtime.py', 'tests/test_phase4_reproducibility.py',
    'docs/pilot/phase-5-closeout.md',
    'docs/pilot/phase-5-primary-results.md',
    'docs/pilot/phase-5-primary-dataset.md',
    'docs/pilot/phase-5-primary-descriptive-analysis.md',
    'experiments/manifests/phase-5-pilot-manifest.json',
    'experiments/manifests/phase-5-primary-batch.json',
    'experiments/manifests/phase-5-primary-run-order.json',
    'experiments/harness/phase_5_batch_freeze.py',
    'experiments/harness/phase_5_primary_trial.py',
    'analysis/phase_5/phase_5_primary_metrics.py',
    'analysis/phase_5/phase_5_primary_dataset.py',
    'analysis/phase_5/phase_5_primary_descriptive.py',
    'data/processed/phase-5/development/observations.json',
    'data/processed/phase-5/primary/corpus-index.json',
    'data/processed/phase-5/primary/observations.json',
    'data/processed/phase-5/primary/provenance.json',
    'data/processed/phase-5/primary/summary.json',
    'data/processed/phase-5/primary/descriptive-analysis.json',
    'tests/test_phase5_primary_trial.py',
    'tests/test_phase5_primary_metrics.py',
    'tests/test_phase5_primary_dataset.py',
    'tests/test_phase5_primary_descriptive.py'
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
    @(Get-ChildItem data/raw, data/external, results/generated -Recurse -File -ErrorAction SilentlyContinue) |
        Where-Object { $_.Name -ne '.gitkeep' }
)
if ($ProtectedFiles.Count -gt 0) {
    throw 'Generated or research data is present in a protected data directory.'
}

$AllowedProcessedFiles = @(
    'data\processed\phase-5\development\observations.json',
    'data\processed\phase-5\primary\corpus-index.json',
    'data\processed\phase-5\primary\observations.json',
    'data\processed\phase-5\primary\provenance.json',
    'data\processed\phase-5\primary\summary.json',
    'data\processed\phase-5\primary\descriptive-analysis.json'
) | ForEach-Object { Join-Path $RepoRoot $_ }

$UnexpectedProcessedFiles = @(
    Get-ChildItem data/processed -Recurse -File -ErrorAction SilentlyContinue |
        Where-Object {
            $_.Name -ne '.gitkeep' -and
            $AllowedProcessedFiles -notcontains $_.FullName
        }
)
if ($UnexpectedProcessedFiles.Count -gt 0) {
    throw "Unexpected processed data file(s): $($UnexpectedProcessedFiles.FullName -join ', ')"
}

git -C $RepoRoot rev-parse --is-inside-work-tree *> $null
if ($LASTEXITCODE -eq 0) {
    git diff --check
    if ($LASTEXITCODE -ne 0) { throw 'git diff --check failed' }
} else {
    Write-Warning 'Git validation skipped: this directory is not a valid Git repository.'
}

Write-Host 'Repository verification passed.'
Write-Host 'Phase: 5 - experiment harness and technical pilot complete.'
Write-Host 'Next gate: Phase 6 - human-participant protocol and ethics.'
