[CmdletBinding()]
param(
    [string]$RepositoryRoot = (Split-Path -Parent $PSScriptRoot),
    [string]$BaselineDate = '2026-08-29'
)

$ErrorActionPreference = 'Stop'

function Read-JsonLines {
    param([string]$Path)

    $records = New-Object System.Collections.Generic.List[object]
    $lineNumber = 0
    foreach ($line in Get-Content -LiteralPath $Path) {
        $lineNumber++
        if ([string]::IsNullOrWhiteSpace($line)) {
            continue
        }
        try {
            $records.Add(($line | ConvertFrom-Json))
        }
        catch {
            throw "Invalid JSONL at ${Path}:${lineNumber}: $($_.Exception.Message)"
        }
    }
    return $records
}

function Assert-EventRecord {
    param(
        [object]$Record,
        [string]$Path,
        [string]$ExpectedType
    )

    $required = @(
        'event_id', 'event_date', 'publication_date', 'entity', 'jurisdiction',
        'regulator_or_forum', 'event_type', 'status', 'issue', 'outcome',
        'instrument_or_rule', 'official_source_url', 'source_title',
        'source_family_id', 'case_status_note', 'electricity_relevance', 'baseline_date'
    )
    foreach ($field in $required) {
        if ($null -eq $Record.$field -or [string]::IsNullOrWhiteSpace([string]$Record.$field)) {
            throw "Missing required field '$field' in $Path for event '$($Record.event_id)'"
        }
    }

    if ($Record.event_date -notmatch '^\d{4}(-\d{2}(-\d{2})?)?$') {
        throw "Invalid event_date '$($Record.event_date)' for '$($Record.event_id)'"
    }
    if ($Record.publication_date -notmatch '^\d{4}(-\d{2}(-\d{2})?)?$') {
        throw "Invalid publication_date '$($Record.publication_date)' for '$($Record.event_id)'"
    }
    if ($Record.baseline_date -notmatch '^\d{4}-\d{2}-\d{2}$' -or $Record.baseline_date -gt $BaselineDate) {
        throw "Invalid or future source-review baseline_date '$($Record.baseline_date)' for '$($Record.event_id)'"
    }
    if ($Record.official_source_url -notmatch '^https://') {
        throw "Official source URL must use HTTPS for '$($Record.event_id)'"
    }
    if ($Record.event_id -notmatch '^[a-z0-9]+(?:-[a-z0-9]+)*$') {
        throw "event_id must be lowercase ASCII kebab case: '$($Record.event_id)'"
    }
    if ($Record.event_id.Length -gt 160) {
        throw "event_id is too long for a stable key: '$($Record.event_id)'"
    }
    if ($Record.entity.Length -gt 240 -or $Record.issue.Length -gt 2000 -or $Record.outcome.Length -gt 4000) {
        throw "Event contains an unreasonably long field and likely scraper noise: '$($Record.event_id)'"
    }
    $scraperNoise = 'Swipe to see more information|Charges Swipe|\bView more information\b|Â|â€™|â€“|�'
    if (($Record.entity + ' ' + $Record.issue + ' ' + $Record.outcome) -match $scraperNoise) {
        throw "Event contains scraper navigation text or mojibake: '$($Record.event_id)'"
    }
    if ($ExpectedType -eq 'technical' -and $Record.event_type -ne 'technical-event') {
        throw "Technical record has event_type '$($Record.event_type)': '$($Record.event_id)'"
    }
    if ($ExpectedType -eq 'enforcement' -and $Record.event_type -eq 'technical-event') {
        throw "Enforcement record is labelled technical-event: '$($Record.event_id)'"
    }
}

function Assert-CoverageReview {
    param(
        [object]$Review,
        [string]$Path
    )

    $required = @(
        'source_family_id', 'source_url', 'public_date_scope',
        'pages_or_years_checked', 'extraction_status', 'public_record_count',
        'anonymous_or_aggregate_count', 'gap_periods', 'gap_reason', 'checked_at'
    )
    foreach ($field in $required) {
        if ($null -eq $Review.PSObject.Properties[$field]) {
            throw "Missing coverage field '$field' in $Path for '$($Review.source_family_id)'"
        }
    }

    $allowedStatuses = @(
        'complete-case-indexed',
        'complete-series-indexed',
        'aggregate-only',
        'archive-gap',
        'not-applicable'
    )
    if ($allowedStatuses -notcontains $Review.extraction_status) {
        throw "Invalid extraction_status '$($Review.extraction_status)' in $Path for '$($Review.source_family_id)'"
    }
    if ([string]::IsNullOrWhiteSpace([string]$Review.source_family_id) -or
        [string]::IsNullOrWhiteSpace([string]$Review.source_url) -or
        [string]::IsNullOrWhiteSpace([string]$Review.public_date_scope) -or
        [string]::IsNullOrWhiteSpace([string]$Review.pages_or_years_checked) -or
        [string]::IsNullOrWhiteSpace([string]$Review.checked_at)) {
        throw "Coverage review lacks audit detail in $Path for '$($Review.source_family_id)'"
    }
    if ($Review.source_url -notmatch '^https://') {
        throw "Coverage review source URL must use HTTPS for '$($Review.source_family_id)'"
    }
    if ($Review.extraction_status -eq 'archive-gap' -and @($Review.gap_periods).Count -eq 0) {
        throw "Archive-gap review has no gap period for '$($Review.source_family_id)'"
    }
}

function Set-ObjectFields {
    param(
        [object]$Target,
        [object]$Fields
    )
    foreach ($property in $Fields.PSObject.Properties) {
        if ($null -ne $Target.PSObject.Properties[$property.Name]) {
            $Target.($property.Name) = $property.Value
        }
        else {
            $Target | Add-Member -NotePropertyName $property.Name -NotePropertyValue $property.Value
        }
    }
}

$sourceRegisterPath = Join-Path $RepositoryRoot 'data\enforcement-source-register.json'
$stagingRoot = Join-Path $RepositoryRoot 'staging-full'
if (-not (Test-Path -LiteralPath $sourceRegisterPath -PathType Leaf)) {
    throw "Missing source register: $sourceRegisterPath"
}
if (-not (Test-Path -LiteralPath $stagingRoot -PathType Container)) {
    throw "Missing staging directory: $stagingRoot"
}

$sourceRegister = Get-Content -LiteralPath $sourceRegisterPath -Raw | ConvertFrom-Json
$knownSourceIds = @($sourceRegister.sources | ForEach-Object { $_.id })
$enforcement = New-Object System.Collections.Generic.List[object]
$technical = New-Object System.Collections.Generic.List[object]
$reviews = New-Object System.Collections.Generic.List[object]
$curatedBySource = @{}

$regionDirectories = @(Get-ChildItem -LiteralPath $stagingRoot -Directory | Sort-Object Name)
if ($regionDirectories.Count -eq 0) {
    throw 'No regional staging directories were found.'
}

foreach ($directory in $regionDirectories) {
    $enforcementPath = Join-Path $directory.FullName 'enforcement.jsonl'
    $technicalPath = Join-Path $directory.FullName 'technical.jsonl'
    $coveragePath = Join-Path $directory.FullName 'coverage.json'
    foreach ($requiredPath in @($enforcementPath, $technicalPath, $coveragePath)) {
        if (-not (Test-Path -LiteralPath $requiredPath -PathType Leaf)) {
            throw "Missing staging file: $requiredPath"
        }
    }

    foreach ($record in (Read-JsonLines -Path $enforcementPath)) {
        Assert-EventRecord -Record $record -Path $enforcementPath -ExpectedType 'enforcement'
        $enforcement.Add($record)
    }
    foreach ($record in (Read-JsonLines -Path $technicalPath)) {
        Assert-EventRecord -Record $record -Path $technicalPath -ExpectedType 'technical'
        $technical.Add($record)
    }

    $coverage = Get-Content -LiteralPath $coveragePath -Raw | ConvertFrom-Json
    if ($coverage.baseline_date -notmatch '^\d{4}-\d{2}-\d{2}$' -or $coverage.baseline_date -gt $BaselineDate) {
        throw "Invalid or future coverage baseline in $coveragePath"
    }
    foreach ($review in @($coverage.source_reviews)) {
        Assert-CoverageReview -Review $review -Path $coveragePath
        $reviews.Add($review)
    }
}

$curatedAdditionsPath = Join-Path $RepositoryRoot 'data\curated-full-corpus-additions.jsonl'
if (Test-Path -LiteralPath $curatedAdditionsPath -PathType Leaf) {
    foreach ($record in (Read-JsonLines -Path $curatedAdditionsPath)) {
        if ($record.event_type -eq 'technical-event') {
            Assert-EventRecord -Record $record -Path $curatedAdditionsPath -ExpectedType 'technical'
            $technical.Add($record)
        }
        else {
            Assert-EventRecord -Record $record -Path $curatedAdditionsPath -ExpectedType 'enforcement'
            $enforcement.Add($record)
        }
        if (-not $curatedBySource.ContainsKey($record.source_family_id)) {
            $curatedBySource[$record.source_family_id] = 0
        }
        $curatedBySource[$record.source_family_id]++
    }
}

$reviewedAdditionFiles = @(Get-ChildItem -LiteralPath $stagingRoot -Recurse -Filter '_reviewed-*-additions.jsonl' -File | Sort-Object FullName)
foreach ($reviewedAdditionFile in $reviewedAdditionFiles) {
    foreach ($record in (Read-JsonLines -Path $reviewedAdditionFile.FullName)) {
        if ($record.event_type -eq 'technical-event') {
            Assert-EventRecord -Record $record -Path $reviewedAdditionFile.FullName -ExpectedType 'technical'
            $technical.Add($record)
        }
        else {
            Assert-EventRecord -Record $record -Path $reviewedAdditionFile.FullName -ExpectedType 'enforcement'
            $enforcement.Add($record)
        }
        if (-not $curatedBySource.ContainsKey($record.source_family_id)) {
            $curatedBySource[$record.source_family_id] = 0
        }
        $curatedBySource[$record.source_family_id]++
    }
}

$qualityOverridesPath = Join-Path $RepositoryRoot 'data\event-quality-overrides.json'
if (-not (Test-Path -LiteralPath $qualityOverridesPath -PathType Leaf)) {
    throw "Missing event quality overrides: $qualityOverridesPath"
}
$qualityOverrides = Get-Content -LiteralPath $qualityOverridesPath -Raw | ConvertFrom-Json
$eventByUpstreamId = @{}
foreach ($event in ([object[]]$enforcement + [object[]]$technical)) {
    $eventByUpstreamId[$event.event_id] = $event
}
foreach ($entry in $qualityOverrides.overrides.PSObject.Properties) {
    if (-not $eventByUpstreamId.ContainsKey($entry.Name)) {
        throw "Event quality override references unknown upstream event ID '$($entry.Name)'"
    }
    Set-ObjectFields -Target $eventByUpstreamId[$entry.Name] -Fields $entry.Value
}

$remediationOverrideFiles = @(Get-ChildItem -LiteralPath (Join-Path $RepositoryRoot 'data') -Filter '*-remediation-overrides.json' -File)
foreach ($overrideFile in $remediationOverrideFiles) {
    $remediation = Get-Content -LiteralPath $overrideFile.FullName -Raw | ConvertFrom-Json
    foreach ($entry in @($remediation.overrides)) {
        if ([string]::IsNullOrWhiteSpace([string]$entry.event_id)) {
            throw "Remediation override has no event_id in '$($overrideFile.Name)'"
        }
        if (-not $eventByUpstreamId.ContainsKey($entry.event_id)) {
            throw "Remediation override references unknown upstream event ID '$($entry.event_id)' in '$($overrideFile.Name)'"
        }
        $fields = [ordered]@{}
        foreach ($property in $entry.PSObject.Properties) {
            if ($property.Name -ne 'event_id') {
                $fields[$property.Name] = $property.Value
            }
        }
        Set-ObjectFields -Target $eventByUpstreamId[$entry.event_id] -Fields ([pscustomobject]$fields)
    }
}

$remediatedEvents = [object[]]$enforcement + [object[]]$technical
$enforcement = New-Object System.Collections.Generic.List[object]
$technical = New-Object System.Collections.Generic.List[object]
foreach ($event in $remediatedEvents) {
    if ($event.event_type -eq 'technical-event') {
        $technical.Add($event)
    }
    else {
        $enforcement.Add($event)
    }
}

foreach ($event in ([object[]]$enforcement + [object[]]$technical)) {
    if ($null -eq $event.PSObject.Properties['record_reviewed_at']) {
        $event | Add-Member -NotePropertyName record_reviewed_at -NotePropertyValue $event.baseline_date
    }
    $event.baseline_date = $BaselineDate
    if ($null -eq $event.PSObject.Properties['provision_resolution_status']) {
        $provisionStatus = if ($event.event_type -eq 'technical-event') {
            'non-contravention-event'
        }
        elseif ($event.instrument_or_rule -match 'clause-level verification|required before current-law|requires the (?:linked|archived) instrument|does not reproduce the detailed conduct|exact .+ (?:clause|subrule|provision).+not stated') {
            'unresolved-official-source-insufficient'
        }
        else {
            'source-recorded-not-separately-audited'
        }
        $event | Add-Member -NotePropertyName provision_resolution_status -NotePropertyValue $provisionStatus
    }
    if ($null -eq $event.PSObject.Properties['event_date_basis']) {
        $basis = switch -Regex ($event.event_type) {
            '^technical-event$' { 'incident or technical-event date stated by the official source'; break }
            'court|prosecution|disciplinary' { 'decision, order or prosecution-outcome date stated by the official source'; break }
            'notice|undertaking|warning|licence' { 'regulatory action or publication date stated by the official source'; break }
            default { 'event, reporting-period or publication date stated by the official source' }
        }
        $event | Add-Member -NotePropertyName event_date_basis -NotePropertyValue $basis
    }
}

$coverageOverridesPath = Join-Path $RepositoryRoot 'data\source-coverage-status-overrides.json'
if (-not (Test-Path -LiteralPath $coverageOverridesPath -PathType Leaf)) {
    throw "Missing source coverage status overrides: $coverageOverridesPath"
}
$coverageOverrides = Get-Content -LiteralPath $coverageOverridesPath -Raw | ConvertFrom-Json
$reviewBySource = @{}
foreach ($review in $reviews) {
    $reviewBySource[$review.source_family_id] = $review
}
foreach ($entry in $coverageOverrides.overrides.PSObject.Properties) {
    if (-not $reviewBySource.ContainsKey($entry.Name)) {
        throw "Source coverage override references unknown source family '$($entry.Name)'"
    }
    Set-ObjectFields -Target $reviewBySource[$entry.Name] -Fields $entry.Value
}

$allEvents = [object[]]$enforcement + [object[]]$technical
$duplicateEventIds = @($allEvents | Group-Object event_id | Where-Object Count -gt 1)
if ($duplicateEventIds.Count -gt 0) {
    throw "Duplicate event IDs: $(($duplicateEventIds.Name | Sort-Object) -join ', ')"
}
$duplicateSemanticEvents = @($allEvents | Group-Object {
    "$($_.source_family_id)|$($_.event_date)|$($_.entity.Trim().ToLowerInvariant())|$($_.event_type)|$($_.issue.Trim().ToLowerInvariant())"
} | Where-Object Count -gt 1)
if ($duplicateSemanticEvents.Count -gt 0) {
    throw "Possible duplicate source/date/entity/type events: $(($duplicateSemanticEvents.Name | Sort-Object) -join '; ')"
}

foreach ($event in $allEvents) {
    if ($knownSourceIds -notcontains $event.source_family_id) {
        throw "Unknown source_family_id '$($event.source_family_id)' for '$($event.event_id)'"
    }
}

$duplicateReviews = @($reviews | Group-Object source_family_id | Where-Object Count -gt 1)
if ($duplicateReviews.Count -gt 0) {
    throw "Duplicate coverage reviews: $(($duplicateReviews.Name | Sort-Object) -join ', ')"
}
$reviewedSourceIds = @($reviews | ForEach-Object { $_.source_family_id })
$missingReviews = @($knownSourceIds | Where-Object { $reviewedSourceIds -notcontains $_ })
$unknownReviews = @($reviewedSourceIds | Where-Object { $knownSourceIds -notcontains $_ })
if ($missingReviews.Count -gt 0) {
    throw "Missing coverage reviews: $(($missingReviews | Sort-Object) -join ', ')"
}
if ($unknownReviews.Count -gt 0) {
    throw "Unknown coverage reviews: $(($unknownReviews | Sort-Object) -join ', ')"
}

$enforcement = @($enforcement | Sort-Object event_date, publication_date, event_id)
$technical = @($technical | Sort-Object event_date, publication_date, event_id)

$enforcementPath = Join-Path $RepositoryRoot 'data\enforcement-events-full.jsonl'
$technicalPath = Join-Path $RepositoryRoot 'data\technical-events-full.jsonl'
$ledgerPath = Join-Path $RepositoryRoot 'data\source-coverage-ledger.json'
$summaryPath = Join-Path $RepositoryRoot 'data\full-corpus-summary.json'

Set-Content -LiteralPath $enforcementPath -Encoding utf8 -Value @(
    $enforcement | ForEach-Object { $_ | ConvertTo-Json -Compress -Depth 12 }
)
Set-Content -LiteralPath $technicalPath -Encoding utf8 -Value @(
    $technical | ForEach-Object { $_ | ConvertTo-Json -Compress -Depth 12 }
)

$enforcementBySource = @{}
$technicalBySource = @{}
foreach ($sourceId in $knownSourceIds) {
    $enforcementBySource[$sourceId] = @($enforcement | Where-Object source_family_id -eq $sourceId).Count
    $technicalBySource[$sourceId] = @($technical | Where-Object source_family_id -eq $sourceId).Count
}

$orderedReviews = foreach ($review in ($reviews | Sort-Object source_family_id)) {
    $indexedTotal = $enforcementBySource[$review.source_family_id] + $technicalBySource[$review.source_family_id]
    if ($review.public_record_count -isnot [int] -and $review.public_record_count -isnot [long]) {
        throw "public_record_count must be an integer for '$($review.source_family_id)'"
    }
    $curatedCount = if ($curatedBySource.ContainsKey($review.source_family_id)) { [int]$curatedBySource[$review.source_family_id] } else { 0 }
    if (([int]$review.public_record_count + $curatedCount) -ne $indexedTotal) {
        throw "Coverage count mismatch for '$($review.source_family_id)': harvested=$($review.public_record_count), curated=$curatedCount, indexed=$indexedTotal"
    }
    if ($review.anonymous_or_aggregate_count -isnot [int] -and $review.anonymous_or_aggregate_count -isnot [long]) {
        throw "anonymous_or_aggregate_count must be an integer for '$($review.source_family_id)'"
    }
    [ordered]@{
        source_family_id = $review.source_family_id
        source_url = $review.source_url
        public_date_scope = $review.public_date_scope
        pages_or_years_checked = $review.pages_or_years_checked
        extraction_status = $review.extraction_status
        public_record_count = $indexedTotal
        indexed_enforcement_records = $enforcementBySource[$review.source_family_id]
        indexed_technical_records = $technicalBySource[$review.source_family_id]
        curated_addition_records = $curatedCount
        anonymous_or_aggregate_count = $review.anonymous_or_aggregate_count
        gap_periods = @($review.gap_periods)
        gap_reason = $review.gap_reason
        checked_at = $review.checked_at
    }
}

$ledger = [ordered]@{
    schema_version = '1.0'
    baseline_date = $BaselineDate
    corpus_period = "2006-01-01 to $BaselineDate inclusive"
    definition = 'All individually identifiable electricity-sector matters discoverable in the registered official public source families; unpublished, confidential, anonymous aggregate and inaccessible archive material is explicitly outside the event universe and recorded as a limitation.'
    source_family_count = $knownSourceIds.Count
    source_reviews = @($orderedReviews)
}
$ledger | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $ledgerPath -Encoding utf8

$summary = [ordered]@{
    schema_version = '1.0'
    baseline_date = $BaselineDate
    corpus_period = "2006-01-01 to $BaselineDate inclusive"
    public_exhaustiveness_status = if (@($reviews | Where-Object extraction_status -eq 'archive-gap').Count -eq 0) { 'established-for-registered-public-sources' } else { 'not-established-archive-gaps-remain' }
    enforcement_event_count = $enforcement.Count
    technical_event_count = $technical.Count
    total_event_count = $enforcement.Count + $technical.Count
    source_family_count = $knownSourceIds.Count
    source_review_count = $reviews.Count
    source_status_counts = @($reviews | Group-Object extraction_status | Sort-Object Name | ForEach-Object {
        [ordered]@{ status = $_.Name; count = $_.Count }
    })
    archive_gap_source_family_ids = @($reviews | Where-Object extraction_status -eq 'archive-gap' | Sort-Object source_family_id | ForEach-Object source_family_id)
    aggregate_only_source_family_ids = @($reviews | Where-Object extraction_status -eq 'aggregate-only' | Sort-Object source_family_id | ForEach-Object source_family_id)
    provision_resolution_counts = @(([object[]]$enforcement + [object[]]$technical) | Group-Object provision_resolution_status | Sort-Object Name | ForEach-Object {
        [ordered]@{ status = $_.Name; count = $_.Count }
    })
}
$summary | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $summaryPath -Encoding utf8

Write-Host "Built full public-record corpus." -ForegroundColor Green
Write-Host "Enforcement and compliance events: $($enforcement.Count)"
Write-Host "Technical events: $($technical.Count)"
Write-Host "Official source families reviewed: $($reviews.Count)"
