[CmdletBinding()]
param(
    [switch]$Strict
)

$ErrorActionPreference = 'Stop'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Set-Location $RepoRoot
$env:ANSIBLE_CONFIG = Join-Path $RepoRoot 'ansible\ansible.cfg'
$env:ANSIBLE_HOME = Join-Path $RepoRoot 'tmp\ansible-home'
$env:ANSIBLE_LOCAL_TEMP = Join-Path $RepoRoot 'tmp\ansible'
$env:XDG_CACHE_HOME = Join-Path $RepoRoot 'tmp\cache'
New-Item -ItemType Directory -Force -Path $env:ANSIBLE_HOME, $env:ANSIBLE_LOCAL_TEMP, $env:XDG_CACHE_HOME | Out-Null

function Invoke-CheckedCommand {
    param(
        [Parameter(Mandatory)]
        [string]$Command,

        [Parameter(Mandatory)]
        [string[]]$Arguments
    )

    & $Command @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "$Command failed with exit code $LASTEXITCODE."
    }
}

function Invoke-WarningOrThrow {
    param(
        [Parameter(Mandatory)]
        [string]$Message,

        [switch]$StrictMode
    )

    if ($StrictMode) { throw $Message }
    Write-Warning $Message
}

function Get-RequiredCommand {
    param(
        [Parameter(Mandatory)]
        [string]$Name
    )

    $Command = Get-Command $Name -ErrorAction SilentlyContinue
    if (-not $Command) {
        Invoke-WarningOrThrow `
            -Message "Required infrastructure tool is unavailable: $Name" `
            -StrictMode:$Strict
    }
    return $Command
}

if (Get-Command shellcheck -ErrorAction SilentlyContinue) {
    $ShellFiles = @((Get-ChildItem (Join-Path $RepoRoot 'scripts') -Filter '*.sh').FullName)
    $ShellFiles += Join-Path $RepoRoot 'infrastructure/kubernetes/entrypoint.sh'
    Invoke-CheckedCommand -Command 'shellcheck' -Arguments $ShellFiles
} else {
    Invoke-WarningOrThrow `
        -Message 'ShellCheck is unavailable; shell validation was not performed.' `
        -StrictMode:$Strict
}

$Analyzer = Get-Command pwsh -ErrorAction SilentlyContinue
if (-not $Analyzer) { $Analyzer = Get-Command powershell -ErrorAction SilentlyContinue }
if ($Analyzer) {
    if (Get-Module -ListAvailable -Name PSScriptAnalyzer) {
        Invoke-CheckedCommand -Command $Analyzer.Source -Arguments @(
            '-NoLogo', '-NoProfile', '-File', (Join-Path $PSScriptRoot 'run-psscriptanalyzer.ps1'),
            '-RepositoryRoot', $RepoRoot
        )
    } else {
        Invoke-WarningOrThrow `
            -Message 'PSScriptAnalyzer is unavailable; PowerShell analysis was not performed.' `
            -StrictMode:$Strict
    }
} else {
    Invoke-WarningOrThrow `
        -Message 'PowerShell is unavailable; PSScriptAnalyzer was not performed.' `
        -StrictMode:$Strict
}

$YamlLint = Get-RequiredCommand -Name 'yamllint'
if ($YamlLint) {
    Invoke-CheckedCommand -Command $YamlLint.Source -Arguments @(
        'ansible', 'observability', 'infrastructure', '.github'
    )
}

$Kubeconform = Get-RequiredCommand -Name 'kubeconform'
if ($Kubeconform) {
    Invoke-CheckedCommand -Command $Kubeconform.Source -Arguments @(
        '-strict',
        '-summary',
        '-schema-location', 'default',
        '-schema-location', 'https://raw.githubusercontent.com/yannh/kubernetes-json-schema/master/{{.ResourceKind}}{{.ResourceAPIVersion}}-standalone-strict.json',
        (Join-Path $RepoRoot 'infrastructure/kubernetes/orderflow-fit-probe.yaml')
    )
}

# ansible-core is not a supported native Windows controller. Running it under
# Windows PowerShell produces POSIX-module errors before playbook parsing. The
# Linux CI job is the authoritative syntax/lint check; Windows still validates
# the YAML, Kubernetes schema and PowerShell/Bash boundaries above.
if ([System.Environment]::OSVersion.Platform -eq [System.PlatformID]::Win32NT) {
    Write-Host 'Ansible native execution skipped on Windows; Linux CI is authoritative.'
} else {
    $AnsiblePlaybook = Get-RequiredCommand -Name 'ansible-playbook'
    $AnsibleLint = Get-RequiredCommand -Name 'ansible-lint'
    if ($AnsiblePlaybook -and $AnsibleLint) {
        Invoke-CheckedCommand -Command $AnsiblePlaybook.Source -Arguments @(
            '--syntax-check', '-i', (Join-Path $RepoRoot 'ansible/inventory/local.yml'),
            (Join-Path $RepoRoot 'ansible/site.yml')
        )
        Invoke-CheckedCommand -Command $AnsibleLint.Source -Arguments @(
            (Join-Path $RepoRoot 'ansible/site.yml')
        )
    }
}

Write-Host 'Infrastructure validation passed.'
