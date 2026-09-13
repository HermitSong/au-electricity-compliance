[CmdletBinding()]
param(
    [string]$RepositoryRoot = (Split-Path -Parent $PSScriptRoot),
    [string]$OutputPath = (Join-Path (Split-Path -Parent $PSScriptRoot) 'data\enforcement-events-selected.jsonl')
)

$sourcePath = Join-Path $RepositoryRoot 'knowledge-base\D00-Enforcement-Event-Timeline-2006-2026.md'
if (-not (Test-Path -LiteralPath $sourcePath -PathType Leaf)) {
    throw "D00 timeline was not found: $sourcePath"
}

$events = New-Object System.Collections.Generic.List[object]
$inTimeline = $false

foreach ($line in Get-Content -LiteralPath $sourcePath) {
    if ($line -eq '## Timeline') {
        $inTimeline = $true
        continue
    }
    if ($inTimeline -and $line.StartsWith('## ')) {
        break
    }
    if (-not $inTimeline -or $line -notmatch '^\|\s*20\d{2}') {
        continue
    }

    $columns = $line.Trim('|').Split('|') | ForEach-Object { $_.Trim() }
    if ($columns.Count -ne 8) {
        throw "Unexpected D00 timeline column count ($($columns.Count)): $line"
    }

    $statuses = @([regex]::Matches($columns[6], '`([^`]+)`') | ForEach-Object { $_.Groups[1].Value } | Select-Object -Unique)
    $status = if ($statuses.Count -gt 0) { $statuses[0] } else { $null }

    $events.Add([ordered]@{
        date = $columns[0]
        entity = $columns[1]
        jurisdiction_or_forum = $columns[2]
        kb_mapping = $columns[3]
        issue = $columns[4]
        outcome = $columns[5]
        status = $status
        statuses = $statuses
        status_note = $columns[6].Replace('`', '')
        official_source = $columns[7]
        source_page = 'D00-Enforcement-Event-Timeline-2006-2026.md'
        baseline_date = '2026-08-27'
    })
}

if ($events.Count -eq 0) {
    throw 'No enforcement events were extracted from D00.'
}

$outputDirectory = Split-Path -Parent $OutputPath
if (-not (Test-Path -LiteralPath $outputDirectory -PathType Container)) {
    New-Item -ItemType Directory -Path $outputDirectory | Out-Null
}

$jsonLines = $events | ForEach-Object { $_ | ConvertTo-Json -Compress -Depth 5 }
Set-Content -LiteralPath $OutputPath -Value $jsonLines -Encoding utf8

Write-Host "Exported $($events.Count) selected enforcement events to $OutputPath"
