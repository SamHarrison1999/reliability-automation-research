[CmdletBinding()]
param(
    [string]$OutputRoot = 'results/fit-probe/kubernetes-raw',
    [switch]$KeepNamespace
)

$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) { throw 'Docker CLI is required.' }
if (-not (Get-Command kubectl -ErrorAction SilentlyContinue)) { throw 'kubectl is required.' }

docker build -f infrastructure/kubernetes/Dockerfile -t orderflow/inventory:fit-probe-v1 .
if ($LASTEXITCODE -ne 0) { throw 'Inventory image build failed.' }
docker build -f infrastructure/kubernetes/Dockerfile -t orderflow/order-api:fit-probe-v1 .
if ($LASTEXITCODE -ne 0) { throw 'Order API image build failed.' }

$Arguments = @('experiments/harness/kubernetes_fit_probe.py', '--output-root', $OutputRoot)
if ($KeepNamespace) { $Arguments += '--keep-namespace' }
python @Arguments
if ($LASTEXITCODE -ne 0) { throw 'Kubernetes Phase 2 fit probe failed.' }
