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

# Import locally-built images into Docker Desktop Kubernetes.
function Import-FitProbeImage {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Image
    )

    Write-Host "[+] Importing $Image into desktop-control-plane"

    docker image inspect $Image *> $null
    if ($LASTEXITCODE -ne 0) {
        throw "Locally-built image was not found: $Image"
    }

    $command = "docker save $Image | docker exec -i desktop-control-plane ctr -n k8s.io images import -"
    cmd.exe /d /c $command
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to import image into desktop-control-plane: $Image"
    }
}

Import-FitProbeImage -Image "orderflow/inventory:fit-probe-v1"
Import-FitProbeImage -Image "orderflow/order-api:fit-probe-v1"
$Arguments = @('experiments/harness/kubernetes_fit_probe.py', '--output-root', $OutputRoot)
if ($KeepNamespace) { $Arguments += '--keep-namespace' }
python @Arguments
if ($LASTEXITCODE -ne 0) { throw 'Kubernetes Phase 2 fit probe failed.' }
