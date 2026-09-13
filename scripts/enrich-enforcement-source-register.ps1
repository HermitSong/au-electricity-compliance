[CmdletBinding()]
param(
    [string]$RepositoryRoot = (Split-Path -Parent $PSScriptRoot)
)

$ErrorActionPreference = 'Stop'
$path = Join-Path $RepositoryRoot 'data\enforcement-source-register.json'
$document = Get-Content -LiteralPath $path -Raw | ConvertFrom-Json

$overrides = @{
    'ACT-ICRC-ULAR' = @{
        start = '2005-06'; end = '2024-25'; gaps = @('2012-13 to 2015-16')
        level = 'medium; monitoring series with a four-year publication gap'
    }
    'NT-UC-ANNUAL-COMPLIANCE' = @{
        start = '2018-19'; end = '2024-25'; gaps = @('standalone public reports before 2018-19 are incomplete')
        level = 'high from 2018-19; medium before 2018-19'
    }
    'QLD-QCA-ENERGY-REPORTING' = @{
        start = '2006'; end = '2025-07'; gaps = @()
        level = 'high for published QCA functions'
    }
    'SA-OTR-ANNUAL-REPORTS' = @{
        start = '2018-19'; end = '2024-25'; gaps = @('older reports require archive retrieval')
        level = 'medium; annual outcomes can be aggregated or anonymised'
    }
    'TAS-ECONOMIC-REGULATOR' = @{
        start = '2013-14'; end = 'ongoing'; gaps = @('pre-2013-14 material requires archive retrieval')
        level = 'medium'
    }
    'TAS-ENERGY-OMBUDSMAN-REPORTS' = @{
        start = '2018-19'; end = '2024-25'; gaps = @('older reports require Libraries Tasmania or archive retrieval')
        level = 'medium'
    }
    'TAS-WORKSAFE-PROSECUTIONS' = @{
        start = '2020'; end = '2024'; gaps = @('no continuous public 2006-2019 electricity-only series', 'post-2024 coverage must be checked live')
        level = 'medium'
    }
    'VIC-WORKSAFE-PROSECUTIONS' = @{
        start = '2007'; end = 'ongoing'; gaps = @('prosecution summaries begin in 2012; enforceable undertakings begin in 2007')
        level = 'high for published WorkSafe outcomes'
    }
    'WA-BUILDING-ENERGY-STATEMENTS' = @{
        start = 'rolling six-year window'; end = 'ongoing'; gaps = @('older online statements require archive and annual-report checks')
        level = 'medium'
    }
}

foreach ($source in $document.sources) {
    $start = [string]$source.start_year
    $end = 'ongoing'
    $gaps = @()
    switch ($source.coverage_type) {
        'case-indexed' { $level = 'high for published named actions' }
        'series-bound' { $level = 'medium' }
        default { $level = 'source-identified only' }
    }

    if ($overrides.ContainsKey($source.id)) {
        $metadata = $overrides[$source.id]
        $start = $metadata.start
        $end = $metadata.end
        $gaps = @($metadata.gaps)
        $level = $metadata.level
    }

    $source | Add-Member -NotePropertyName coverage_start -NotePropertyValue $start -Force
    $source | Add-Member -NotePropertyName coverage_end -NotePropertyValue $end -Force
    $source | Add-Member -NotePropertyName gap_periods -NotePropertyValue ([object[]]$gaps) -Force
    $source | Add-Member -NotePropertyName completeness_level -NotePropertyValue $level -Force
}

$document.schema_version = '1.1'
$json = $document | ConvertTo-Json -Depth 20
$encoding = New-Object System.Text.UTF8Encoding($false)
[IO.File]::WriteAllText($path, $json + [Environment]::NewLine, $encoding)

Write-Host "Enriched $($document.sources.Count) enforcement source records in $path"
