[CmdletBinding()]
param(
    [string]$RepositoryRoot = (Split-Path -Parent $PSScriptRoot)
)

$ErrorActionPreference = 'Stop'

function Read-JsonLines {
    param([string]$Path)
    return @(Get-Content -LiteralPath $Path | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | ForEach-Object { $_ | ConvertFrom-Json })
}

function Normalize-Url {
    param([string]$Url)
    if ([string]::IsNullOrWhiteSpace($Url)) {
        return ''
    }
    return $Url.Trim().TrimEnd('/').ToLowerInvariant()
}

$selectedPath = Join-Path $RepositoryRoot 'data\enforcement-events-selected.jsonl'
$enforcementPath = Join-Path $RepositoryRoot 'data\enforcement-events-full.jsonl'
$technicalPath = Join-Path $RepositoryRoot 'data\technical-events-full.jsonl'
$aliasPath = Join-Path $RepositoryRoot 'data\selected-source-aliases.json'
$overridePath = Join-Path $RepositoryRoot 'data\selected-event-overrides.json'
$jsonOutputPath = Join-Path $RepositoryRoot 'review\coverage\selected-to-full-reconciliation.json'
$markdownOutputPath = Join-Path $RepositoryRoot 'review\coverage\SELECTED-TO-FULL-RECONCILIATION.md'

foreach ($path in @($selectedPath, $enforcementPath, $technicalPath, $aliasPath, $overridePath)) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw "Missing input file: $path"
    }
}

$selected = Read-JsonLines -Path $selectedPath
$enforcement = Read-JsonLines -Path $enforcementPath
$technical = Read-JsonLines -Path $technicalPath
$aliasDocument = Get-Content -LiteralPath $aliasPath -Raw | ConvertFrom-Json
$overrideDocument = Get-Content -LiteralPath $overridePath -Raw | ConvertFrom-Json

$enforcementByUrl = @{}
$technicalByUrl = @{}
$eventById = @{}
foreach ($event in $enforcement) {
    $eventById[$event.event_id] = $event
    $key = Normalize-Url -Url $event.official_source_url
    if (-not $enforcementByUrl.ContainsKey($key)) {
        $enforcementByUrl[$key] = New-Object System.Collections.Generic.List[object]
    }
    $enforcementByUrl[$key].Add($event)
}
foreach ($event in $technical) {
    $eventById[$event.event_id] = $event
    $key = Normalize-Url -Url $event.official_source_url
    if (-not $technicalByUrl.ContainsKey($key)) {
        $technicalByUrl[$key] = New-Object System.Collections.Generic.List[object]
    }
    $technicalByUrl[$key].Add($event)
}

$eventsByAliasUrl = @{}
foreach ($alias in @($aliasDocument.aliases)) {
    $key = Normalize-Url -Url $alias.alias_url
    if ($eventsByAliasUrl.ContainsKey($key)) {
        throw "Duplicate selected-source alias: $($alias.alias_url)"
    }
    $aliasEvents = New-Object System.Collections.Generic.List[object]
    foreach ($eventId in @($alias.canonical_event_ids)) {
        if (-not $eventById.ContainsKey($eventId)) {
            throw "Alias references unknown canonical event ID '$eventId'"
        }
        $aliasEvents.Add($eventById[$eventId])
    }
    $eventsByAliasUrl[$key] = $aliasEvents
}

$eventsBySelectedKey = @{}
foreach ($mapping in @($overrideDocument.mappings)) {
    $key = "$($mapping.selected_date)|$($mapping.selected_entity)".ToLowerInvariant()
    if ($eventsBySelectedKey.ContainsKey($key)) {
        throw "Duplicate selected-event override: $key"
    }
    $mappedEvents = New-Object System.Collections.Generic.List[object]
    foreach ($eventId in @($mapping.canonical_event_ids)) {
        if (-not $eventById.ContainsKey($eventId)) {
            throw "Selected-event override references unknown canonical event ID '$eventId'"
        }
        $mappedEvents.Add($eventById[$eventId])
    }
    $eventsBySelectedKey[$key] = $mappedEvents
}

$results = New-Object System.Collections.Generic.List[object]
foreach ($event in $selected) {
    $urlKey = Normalize-Url -Url $event.official_source
    $statuses = @($event.statuses)
    $expectedCorpus = if ($statuses -contains 'technical-event') {
        'technical'
    }
    elseif (($statuses -contains 'media-trigger') -or
            ((($statuses -contains 'review-guidance') -or ($statuses -contains 'compliance-review')) -and
             $event.entity -match '^(Retailers generally|Retailers reusing plan names)$')) {
        'excluded-non-event'
    }
    else {
        'enforcement'
    }

    $matches = @()
    $matchMethod = ''
    $selectedKey = "$($event.date)|$($event.entity)".ToLowerInvariant()
    if ($eventsBySelectedKey.ContainsKey($selectedKey)) {
        $matches = [object[]]$eventsBySelectedKey[$selectedKey]
        $matchMethod = 'reviewed-event-override'
    }
    elseif ($expectedCorpus -eq 'enforcement' -and $enforcementByUrl.ContainsKey($urlKey)) {
        $matches = [object[]]$enforcementByUrl[$urlKey]
        $matchMethod = 'canonical-url'
    }
    elseif ($expectedCorpus -eq 'technical' -and $technicalByUrl.ContainsKey($urlKey)) {
        $matches = [object[]]$technicalByUrl[$urlKey]
        $matchMethod = 'canonical-url'
    }
    elseif ($eventsByAliasUrl.ContainsKey($urlKey)) {
        $matches = [object[]]$eventsByAliasUrl[$urlKey]
        $matchMethod = 'official-source-alias'
    }

    $result = if ($expectedCorpus -eq 'excluded-non-event') {
        'excluded-by-scope'
    }
    elseif ($matches.Count -gt 0) {
        'matched'
    }
    else {
        'unmatched'
    }

    $results.Add([ordered]@{
        selected_date = $event.date
        selected_entity = $event.entity
        selected_statuses = $statuses
        selected_official_source = $event.official_source
        expected_corpus = $expectedCorpus
        reconciliation_result = $result
        matched_event_ids = @($matches | ForEach-Object { $_.event_id })
        note = if ($result -eq 'excluded-by-scope') {
            'Retained in D00 as guidance or a risk signal, but it is not an individually identifiable official violation or technical event.'
        }
        elseif ($result -eq 'matched') {
            if ($matchMethod -eq 'reviewed-event-override') {
                'Matched through an explicit selected-row to canonical-event mapping because the official source contains multiple matters.'
            }
            elseif ($matchMethod -eq 'official-source-alias') {
                'Matched through the reviewed official-source alias registry; the canonical event is not duplicated.'
            }
            else {
                'Matched by normalized canonical official source URL.'
            }
        }
        else {
            'Requires source-level review or a documented URL alias before full-corpus acceptance.'
        }
    })
}

$document = [ordered]@{
    schema_version = '1.0'
    baseline_date = '2026-08-27'
    selected_record_count = $selected.Count
    matched_count = @([object[]]$results | Where-Object reconciliation_result -eq 'matched').Count
    excluded_non_event_count = @([object[]]$results | Where-Object reconciliation_result -eq 'excluded-by-scope').Count
    unmatched_count = @([object[]]$results | Where-Object reconciliation_result -eq 'unmatched').Count
    records = [object[]]$results
}
$document | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $jsonOutputPath -Encoding utf8

$lines = New-Object System.Collections.Generic.List[string]
$lines.Add('# Selected-to-Full Corpus Reconciliation')
$lines.Add('')
$lines.Add('**Baseline:** 27 August 2026')
$lines.Add('')
$lines.Add("- Selected D00 records: $($document.selected_record_count)")
$lines.Add("- Matched to a full-corpus event: $($document.matched_count)")
$lines.Add("- Excluded because the D00 record is guidance or a media risk signal rather than an event: $($document.excluded_non_event_count)")
$lines.Add("- Unmatched and requiring review: $($document.unmatched_count)")
$lines.Add('')
$lines.Add('| date | entity | expected corpus | result | matched event IDs |')
$lines.Add('|---|---|---|---|---|')
foreach ($result in $results) {
    $entity = ([string]$result.selected_entity).Replace('|', '\|')
    $ids = if (@($result.matched_event_ids).Count -gt 0) { @($result.matched_event_ids) -join ', ' } else { '' }
    $lines.Add("| $($result.selected_date) | $entity | $($result.expected_corpus) | $($result.reconciliation_result) | $ids |")
}
$lines | Set-Content -LiteralPath $markdownOutputPath -Encoding utf8

Write-Host "Reconciled $($selected.Count) selected D00 records."
Write-Host "Matched: $($document.matched_count)"
Write-Host "Excluded non-events: $($document.excluded_non_event_count)"
Write-Host "Unmatched: $($document.unmatched_count)"

if ($document.unmatched_count -gt 0) {
    exit 1
}
