@{
    IncludeDefaultRules = $true

    # These scripts are command-line quality gates. Write-Host is intentional
    # for human-readable progress and result messages.
    ExcludeRules = @(
        'PSAvoidUsingWriteHost'
    )
}
