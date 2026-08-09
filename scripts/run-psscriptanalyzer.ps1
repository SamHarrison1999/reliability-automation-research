[CmdletBinding()]
param(
    [string]$RepositoryRoot
)

$ErrorActionPreference = 'Stop'

# Do not calculate the default in the param block. Windows PowerShell 5.1 can
# evaluate that expression before $PSScriptRoot has been populated, producing
# an empty path when this script is launched by another PowerShell process.
if ([string]::IsNullOrWhiteSpace($RepositoryRoot)) {
    $ScriptDirectory = Split-Path -Parent $MyInvocation.MyCommand.Path
    $RepositoryRoot = (Resolve-Path (Join-Path $ScriptDirectory '..')).Path
} else {
    $RepositoryRoot = (Resolve-Path $RepositoryRoot).Path
}

Set-Location -LiteralPath $RepositoryRoot

if (-not (Get-Module -ListAvailable -Name PSScriptAnalyzer)) {
    throw 'PSScriptAnalyzer is not installed. Run the quality bootstrap or install the PSScriptAnalyzer PowerShell module.'
}

Import-Module PSScriptAnalyzer -ErrorAction Stop
$SettingsPath = Join-Path $RepositoryRoot 'PSScriptAnalyzerSettings.psd1'
$ScriptsPath = Join-Path $RepositoryRoot 'scripts'

$Findings = @(
    Invoke-ScriptAnalyzer `
        -Path $ScriptsPath `
        -Recurse `
        -Settings $SettingsPath `
        -Severity Error, Warning
)

if ($Findings.Count -gt 0) {
    $Findings | Format-Table -AutoSize | Out-Host
    throw "PSScriptAnalyzer found $($Findings.Count) error or warning(s)."
}

Write-Host 'PSScriptAnalyzer passed.'
