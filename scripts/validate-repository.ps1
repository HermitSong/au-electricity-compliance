[CmdletBinding()]
param(
    [string]$RepositoryRoot
)

$ErrorActionPreference = 'Stop'
$PSDefaultParameterValues['Get-Content:Encoding'] = 'utf8'
if ([string]::IsNullOrWhiteSpace($RepositoryRoot)) {
    $RepositoryRoot = Split-Path -Parent (Split-Path -Parent $PSCommandPath)
}
$failures = New-Object System.Collections.Generic.List[string]
$textExtensions = @('.md', '.json', '.jsonl', '.txt', '.yml', '.yaml', '.ps1', '.py', '.csv', '.tsv', '.html', '.htm', '.xml')

function Add-Failure {
    param([string]$Message)
    $script:failures.Add($Message)
}

function Get-RelativePath {
    param([string]$Path)
    return $Path.Substring($RepositoryRoot.Length).TrimStart('\', '/')
}

if (-not (Test-Path -LiteralPath $RepositoryRoot -PathType Container)) {
    throw "Repository root does not exist: $RepositoryRoot"
}

$allFiles = Get-ChildItem -LiteralPath $RepositoryRoot -Recurse -File
$textFiles = $allFiles |
    Where-Object {
        $relative = Get-RelativePath $_.FullName
        $textExtensions -contains $_.Extension.ToLowerInvariant() -and
            $relative -notmatch '^source-originals[\\/]objects[\\/]'
    }

# External source bytes stay unchanged; validate their hashes instead of authored-language rules.
$originalManifest = Join-Path $RepositoryRoot 'source-originals\manifest.jsonl'
if (Test-Path -LiteralPath $originalManifest -PathType Leaf) {
    $originalValidator = Join-Path $RepositoryRoot 'scripts\validate_source_originals.py'
    if (-not (Test-Path -LiteralPath $originalValidator -PathType Leaf)) {
        Add-Failure 'Original-source archive exists without its integrity validator.'
    }
    else {
        $originalOutput = @(& python $originalValidator --root $RepositoryRoot 2>&1)
        if ($LASTEXITCODE -ne 0) {
            Add-Failure "Original-source integrity validation failed: $($originalOutput -join ' | ')"
        }
    }
}

foreach ($file in $allFiles) {
    if ($file.Name -match '[\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF]') {
        Add-Failure "Non-English Han characters in filename: $(Get-RelativePath $file.FullName)"
    }
}

foreach ($file in $textFiles) {
    $content = Get-Content -LiteralPath $file.FullName -Raw
    if ($content -match '[\u4E00-\u9FFF]') {
        $count = [regex]::Matches($content, '[\u4E00-\u9FFF]').Count
        Add-Failure "Non-English Han characters: $(Get-RelativePath $file.FullName) ($count)"
    }
    if ($content -match '"(?:question|answer)_zh"') {
        Add-Failure "Legacy language-specific field name: $(Get-RelativePath $file.FullName)"
    }
}

# Rollback snapshots are partial copies, not live pages with a complete relative-link tree.
# Keep their language and structured-data checks; exclude only their Markdown link checks.
$liveMarkdownFiles = $textFiles | Where-Object {
    $_.Extension -eq '.md' -and
        (Get-RelativePath $_.FullName) -notmatch '^review[\\/]backups[\\/]'
}
foreach ($file in $liveMarkdownFiles) {
    $content = Get-Content -LiteralPath $file.FullName -Raw
    foreach ($match in [regex]::Matches($content, '\[[^\]]+\]\(([^)]+)\)')) {
        $target = $match.Groups[1].Value.Trim()
        if ($target.StartsWith('<') -and $target.EndsWith('>')) {
            $target = $target.Substring(1, $target.Length - 2)
        }
        if ($target -match '^(https?://|mailto:|#)') {
            continue
        }
        $target = ($target -split '#', 2)[0]
        if ([string]::IsNullOrWhiteSpace($target)) {
            continue
        }
        $target = [Uri]::UnescapeDataString($target)
        $resolved = Join-Path $file.DirectoryName $target
        if (-not (Test-Path -LiteralPath $resolved)) {
            Add-Failure "Broken local Markdown link: $(Get-RelativePath $file.FullName) -> $target"
        }
    }
}

$jsonFiles = $textFiles | Where-Object { $_.Extension -eq '.json' }
foreach ($file in $jsonFiles) {
    try {
        $null = Get-Content -LiteralPath $file.FullName -Raw | ConvertFrom-Json
    }
    catch {
        Add-Failure "Invalid JSON: $(Get-RelativePath $file.FullName): $($_.Exception.Message)"
    }
}

$jsonlFiles = $textFiles | Where-Object { $_.Extension -eq '.jsonl' }
foreach ($file in $jsonlFiles) {
    $lineNumber = 0
    foreach ($line in Get-Content -LiteralPath $file.FullName) {
        $lineNumber++
        if ([string]::IsNullOrWhiteSpace($line)) {
            continue
        }
        try {
            $null = $line | ConvertFrom-Json
        }
        catch {
            Add-Failure "Invalid JSONL: $(Get-RelativePath $file.FullName):${lineNumber}: $($_.Exception.Message)"
        }
    }
}

$caseLoops = @(
    @{
        Name = 'v3'
        Keyed = 'review\questions\case-question-bank-v3.jsonl'
        Blind = 'review\questions\case-question-bank-v3-blind.jsonl'
        Answers = 'review\results\case-loop-round1-answers.jsonl'
    },
    @{
        Name = 'v4'
        Keyed = 'review\questions\case-question-bank-v4.jsonl'
        Blind = 'review\questions\case-question-bank-v4-blind.jsonl'
        Answers = 'review\results\case-loop-v4-answers.jsonl'
    },
    @{
        Name = 'v5'
        Keyed = 'review\questions\case-question-bank-v5.jsonl'
        Blind = 'review\questions\case-question-bank-v5-blind.jsonl'
        Answers = 'review\results\case-loop-v5-answers.jsonl'
    }
)

foreach ($loop in $caseLoops) {
    $paths = @($loop.Keyed, $loop.Blind, $loop.Answers)
    $missing = $false
    foreach ($relativePath in $paths) {
        $fullPath = Join-Path $RepositoryRoot $relativePath
        if (-not (Test-Path -LiteralPath $fullPath -PathType Leaf)) {
            Add-Failure "Missing $($loop.Name) case-loop file: $relativePath"
            $missing = $true
            continue
        }
        $recordCount = (Get-Content -LiteralPath $fullPath | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }).Count
        if ($recordCount -ne 100) {
            Add-Failure "Expected 100 JSONL records in $relativePath, found $recordCount"
        }
    }
    if ($missing) {
        continue
    }
    $keyedCasePath = Join-Path $RepositoryRoot $loop.Keyed
    $blindCasePath = Join-Path $RepositoryRoot $loop.Blind
    $answerCasePath = Join-Path $RepositoryRoot $loop.Answers
    $keyedRecords = Get-Content -LiteralPath $keyedCasePath | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | ForEach-Object { $_ | ConvertFrom-Json }
    $blindRecords = Get-Content -LiteralPath $blindCasePath | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | ForEach-Object { $_ | ConvertFrom-Json }
    $answerRecords = Get-Content -LiteralPath $answerCasePath | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | ForEach-Object { $_ | ConvertFrom-Json }

    $keyedIds = @($keyedRecords | ForEach-Object { $_.id })
    $blindIds = @($blindRecords | ForEach-Object { $_.id })
    $answerIds = @($answerRecords | ForEach-Object { $_.id })

    if ((Compare-Object -ReferenceObject $keyedIds -DifferenceObject $blindIds).Count -ne 0) {
        Add-Failure "$($loop.Name) keyed and blind case-loop IDs do not match"
    }
    if ((Compare-Object -ReferenceObject $keyedIds -DifferenceObject $answerIds).Count -ne 0) {
        Add-Failure "$($loop.Name) question and answer case-loop IDs do not match"
    }
    foreach ($record in $blindRecords) {
        $propertyNames = @($record.PSObject.Properties.Name)
        if (($propertyNames -contains 'correct_answer') -or ($propertyNames -contains 'key_points') -or ($propertyNames -contains 'answer')) {
            Add-Failure "Blind record contains answer material: $($record.id)"
        }
    }
}

$sourceRegisterPath = Join-Path $RepositoryRoot 'data\enforcement-source-register.json'
$sourceRegister = $null
if (-not (Test-Path -LiteralPath $sourceRegisterPath -PathType Leaf)) {
    Add-Failure 'Missing machine-readable enforcement source register'
}
else {
    $sourceRegister = Get-Content -LiteralPath $sourceRegisterPath -Raw | ConvertFrom-Json
    $sourceJurisdictions = @($sourceRegister.sources | ForEach-Object { $_.jurisdiction } | Sort-Object -Unique)
    $requiredSourceJurisdictions = @(
        'Australian Capital Territory',
        'New South Wales',
        'Northern Territory',
        'Queensland',
        'South Australia',
        'Tasmania',
        'Victoria',
        'Western Australia'
    )
    foreach ($jurisdiction in $requiredSourceJurisdictions) {
        if ($sourceJurisdictions -notcontains $jurisdiction) {
            Add-Failure "Enforcement source register omits: $jurisdiction"
        }
    }
    if ($sourceRegister.sources.Count -lt 41) {
        Add-Failure "Enforcement source register contains fewer than 41 source families: $($sourceRegister.sources.Count)"
    }
    foreach ($source in $sourceRegister.sources) {
        if ([string]::IsNullOrWhiteSpace($source.coverage_start) -or
            [string]::IsNullOrWhiteSpace($source.coverage_end) -or
            [string]::IsNullOrWhiteSpace($source.completeness_level) -or
            $null -eq $source.gap_periods) {
            Add-Failure "Enforcement source metadata is incomplete: $($source.id)"
        }
    }
}

$fullCorpusFiles = @(
    'FULL-CORPUS-SCOPE.md',
    'data\enforcement-events-full.jsonl',
    'data\technical-events-full.jsonl',
    'data\source-coverage-ledger.json',
    'data\full-corpus-summary.json',
    'data\provision-version-register.json',
    'data\provision-source-bindings.json',
    'data\obligation-register.json',
    'data\event-provision-links.jsonl',
    'data\source-artifact-ledger.jsonl',
    'data\source-artifact-summary.json',
    'data\source-capture-summary.json',
    'data\source-text-chunks.jsonl',
    'data\source-text-summary.json',
    'data\source-refresh-policy.json',
    'data\source-freshness-report.json',
    'data\search-index.sqlite3',
    'architecture\ACCURACY-FIRST-KB-ARCHITECTURE.md',
    'architecture\PROFESSIONAL-ACCURACY-STANDARD.md',
    'architecture\POST-IMPLEMENTATION-REFLECTION.md',
    'architecture\ARCHITECTURE-RESEARCH-NOTES.md',
    'architecture\answer-workflow.json',
    'scripts\search_kb.py',
    'scripts\double_search_kb.py',
    'scripts\answer_kb.py',
    'scripts\route_applicability.py',
    'scripts\build_source_artifact_ledger.py',
    'scripts\build_obligation_register.py',
    'scripts\build_provision_source_bindings.py',
    'scripts\validate_accuracy_foundations.py',
    'scripts\snapshot_official_sources.py',
    'scripts\extract_source_text.py',
    'scripts\check_source_freshness.py',
    'scripts\canonical_search.py',
    'scripts\case_lookup.py',
    'scripts\build_operational_brief.py',
    'scripts\check_answer.py',
    'scripts\double_check_answer.py',
    'scripts\build_professional_benchmark_packets.py',
    'scripts\double_check_professional_answers.py',
    'scripts\validate_professional_benchmark.py',
    'scripts\validate_professional_results.py'
)
foreach ($relativePath in $fullCorpusFiles) {
    if (-not (Test-Path -LiteralPath (Join-Path $RepositoryRoot $relativePath) -PathType Leaf)) {
        Add-Failure "Missing full-corpus artefact: $relativePath"
    }
}

$architectureRegressionExpectations = @(
    @{ Path = 'review\results\stanwell-grounded-check.json'; Expected = $true },
    @{ Path = 'review\results\stanwell-grounded-double-check.json'; Expected = $true },
    @{ Path = 'review\results\stanwell-unsafe-check.json'; Expected = $false },
    @{ Path = 'review\results\stanwell-unsafe-double-check.json'; Expected = $false },
    @{ Path = 'review\results\agl-centrepay-unsafe-check.json'; Expected = $false },
    @{ Path = 'review\results\agl-centrepay-unsafe-double-check.json'; Expected = $false },
    @{ Path = 'review\results\cer-undertaking-unsafe-check.json'; Expected = $false },
    @{ Path = 'review\results\victoria-bound-check.json'; Expected = $true },
    @{ Path = 'review\results\victoria-unbound-check.json'; Expected = $false }
)
foreach ($expectation in $architectureRegressionExpectations) {
    $path = Join-Path $RepositoryRoot $expectation.Path
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        Add-Failure "Missing architecture regression result: $($expectation.Path)"
        continue
    }
    $result = Get-Content -LiteralPath $path -Raw | ConvertFrom-Json
    if ([bool]$result.passed -ne $expectation.Expected) {
        Add-Failure "Unexpected architecture regression result: $($expectation.Path)"
    }
}

$packetStateExpectations = @(
    @{ Path = 'review\results\stanwell-temporal-evidence-packet.json'; Expected = 'ready-for-grounded-drafting' },
    @{ Path = 'review\results\dispatch-live-verification-packet.json'; Expected = 'needs-live-verification' },
    @{ Path = 'review\results\australia-wide-exhaustiveness-gate.json'; Expected = 'coverage-gap' }
)
foreach ($expectation in $packetStateExpectations) {
    $path = Join-Path $RepositoryRoot $expectation.Path
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        Add-Failure "Missing evidence-packet regression result: $($expectation.Path)"
        continue
    }
    $result = Get-Content -LiteralPath $path -Raw | ConvertFrom-Json
    if ($result.release_state -ne $expectation.Expected) {
        Add-Failure "Unexpected evidence-packet release state: $($expectation.Path)"
    }
}

$fullEnforcementPath = Join-Path $RepositoryRoot 'data\enforcement-events-full.jsonl'
$fullTechnicalPath = Join-Path $RepositoryRoot 'data\technical-events-full.jsonl'
$coverageLedgerPath = Join-Path $RepositoryRoot 'data\source-coverage-ledger.json'
$fullSummaryPath = Join-Path $RepositoryRoot 'data\full-corpus-summary.json'

if ((Test-Path -LiteralPath $fullEnforcementPath -PathType Leaf) -and
    (Test-Path -LiteralPath $fullTechnicalPath -PathType Leaf) -and
    $null -ne $sourceRegister) {
    $fullEnforcement = @(Get-Content -LiteralPath $fullEnforcementPath | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | ForEach-Object { $_ | ConvertFrom-Json })
    $fullTechnical = @(Get-Content -LiteralPath $fullTechnicalPath | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | ForEach-Object { $_ | ConvertFrom-Json })
    $fullEvents = @($fullEnforcement) + @($fullTechnical)
    $requiredEventFields = @(
        'event_id', 'event_date', 'publication_date', 'entity', 'jurisdiction',
        'regulator_or_forum', 'event_type', 'status', 'issue', 'outcome',
        'instrument_or_rule', 'official_source_url', 'source_title',
        'source_family_id', 'case_status_note', 'electricity_relevance', 'baseline_date',
        'event_date_basis', 'record_reviewed_at', 'provision_resolution_status'
    )
    foreach ($event in $fullEvents) {
        foreach ($field in $requiredEventFields) {
            if ($null -eq $event.$field -or [string]::IsNullOrWhiteSpace([string]$event.$field)) {
                Add-Failure "Full-corpus event missing '$field': $($event.event_id)"
            }
        }
        if ($event.event_date -notmatch '^\d{4}(-\d{2}(-\d{2})?)?$') {
            Add-Failure "Full-corpus event has malformed date: $($event.event_id) = $($event.event_date)"
        }
        $reviewDate = [datetime]::MinValue
        if (-not [datetime]::TryParseExact([string]$event.record_reviewed_at, 'yyyy-MM-dd', [cultureinfo]::InvariantCulture, [Globalization.DateTimeStyles]::None, [ref]$reviewDate)) {
            Add-Failure "Full-corpus event has an invalid review date: $($event.event_id) = $($event.record_reviewed_at)"
        }
        $allowedProvisionStatuses = @(
            'exact-official-provision',
            'unresolved-official-source-insufficient',
            'non-contravention-event',
            'source-recorded-not-separately-audited'
        )
        if ($allowedProvisionStatuses -notcontains $event.provision_resolution_status) {
            Add-Failure "Full-corpus event has an invalid provision resolution status: $($event.event_id) = $($event.provision_resolution_status)"
        }
        if ($event.event_id.Length -gt 160) {
            Add-Failure "Full-corpus event ID is too long: $($event.event_id)"
        }
        if (-not $event.official_source_url.StartsWith('https://')) {
            Add-Failure "Full-corpus event lacks a direct HTTPS official source: $($event.event_id)"
        }
        if ($event.entity.Trim().ToLowerInvariant() -eq $event.source_title.Trim().ToLowerInvariant()) {
            Add-Failure "Full-corpus entity repeats the source title: $($event.event_id)"
        }
        if ($event.entity.Length -gt 240 -or $event.issue.Length -gt 2000 -or $event.outcome.Length -gt 4000) {
            Add-Failure "Full-corpus event contains a likely untrimmed scrape: $($event.event_id)"
        }
        if (($event.entity + ' ' + $event.issue + ' ' + $event.outcome) -match 'Swipe to see more information|Charges Swipe|\bView more information\b|\u00C2|\u00E2|\uFFFD') {
            Add-Failure "Full-corpus event contains scraper noise or mojibake: $($event.event_id)"
        }
        $eventYear = [int]$event.event_date.Substring(0, 4)
        $afterBaseline = $eventYear -gt 2026 -or
            ($event.event_date.Length -ge 7 -and $event.event_date.Substring(0, 7) -gt '2026-08') -or
            ($event.event_date.Length -eq 10 -and $event.event_date -gt '2026-08-29')
        if ($eventYear -lt 2006 -or $afterBaseline) {
            Add-Failure "Full-corpus event is outside the corpus period: $($event.event_id) = $($event.event_date)"
        }
        if (@($sourceRegister.sources.id) -notcontains $event.source_family_id) {
            Add-Failure "Full-corpus event references unknown source family: $($event.event_id) = $($event.source_family_id)"
        }
    }
    foreach ($event in $fullTechnical) {
        if ($event.event_type -ne 'technical-event') {
            Add-Failure "Technical corpus event has the wrong event type: $($event.event_id)"
        }
        if ($event.provision_resolution_status -ne 'non-contravention-event') {
            Add-Failure "Technical corpus event is not marked non-contravention: $($event.event_id)"
        }
    }
    foreach ($event in $fullEnforcement) {
        if ($event.event_type -eq 'technical-event') {
            Add-Failure "Enforcement corpus contains a technical event: $($event.event_id)"
        }
    }
    $duplicateFullEventIds = @($fullEvents | Group-Object event_id | Where-Object Count -gt 1)
    if ($duplicateFullEventIds.Count -gt 0) {
        Add-Failure "Duplicate full-corpus event IDs: $(($duplicateFullEventIds.Name | Sort-Object) -join ', ')"
    }
    $duplicateSemanticEvents = @($fullEvents | Group-Object {
        "$($_.source_family_id)|$($_.event_date)|$($_.entity.Trim().ToLowerInvariant())|$($_.event_type)|$($_.issue.Trim().ToLowerInvariant())"
    } | Where-Object Count -gt 1)
    if ($duplicateSemanticEvents.Count -gt 0) {
        Add-Failure "Possible duplicate full-corpus events: $(($duplicateSemanticEvents.Name | Sort-Object) -join '; ')"
    }
}

if ((Test-Path -LiteralPath $coverageLedgerPath -PathType Leaf) -and $null -ne $sourceRegister) {
    $coverageLedger = Get-Content -LiteralPath $coverageLedgerPath -Raw | ConvertFrom-Json
    $registeredIds = @($sourceRegister.sources.id | Sort-Object)
    $reviewedIds = @($coverageLedger.source_reviews.source_family_id | Sort-Object)
    if ((Compare-Object -ReferenceObject $registeredIds -DifferenceObject $reviewedIds).Count -ne 0) {
        Add-Failure 'Coverage ledger does not contain exactly one review for every registered source family'
    }
    $duplicateCoverageIds = @($coverageLedger.source_reviews | Group-Object source_family_id | Where-Object Count -gt 1)
    if ($duplicateCoverageIds.Count -gt 0) {
        Add-Failure "Duplicate source coverage reviews: $(($duplicateCoverageIds.Name | Sort-Object) -join ', ')"
    }
    $allowedExtractionStatuses = @(
        'complete-case-indexed',
        'complete-series-indexed',
        'aggregate-only',
        'archive-gap',
        'not-applicable'
    )
    foreach ($review in $coverageLedger.source_reviews) {
        if ($allowedExtractionStatuses -notcontains $review.extraction_status) {
            Add-Failure "Invalid source extraction status: $($review.source_family_id) = $($review.extraction_status)"
        }
        if ($review.extraction_status -eq 'archive-gap' -and @($review.gap_periods).Count -eq 0) {
            Add-Failure "Archive-gap review has no gap period: $($review.source_family_id)"
        }
        $materialGaps = @($review.gap_periods | Where-Object {
            -not [string]::IsNullOrWhiteSpace([string]$_) -and [string]$_ -notmatch '^None\b'
        })
        if ($review.extraction_status -match '^complete-' -and $materialGaps.Count -gt 0) {
            Add-Failure "Complete source review declares a material gap: $($review.source_family_id)"
        }
        if ([string]::IsNullOrWhiteSpace([string]$review.pages_or_years_checked) -or
            [string]::IsNullOrWhiteSpace([string]$review.checked_at)) {
            Add-Failure "Source coverage review lacks audit detail: $($review.source_family_id)"
        }
        if ($review.public_record_count -ne ($review.indexed_enforcement_records + $review.indexed_technical_records)) {
            Add-Failure "Source coverage public-record count does not equal indexed enforcement plus technical rows: $($review.source_family_id)"
        }
        $registered = $sourceRegister.sources | Where-Object id -eq $review.source_family_id | Select-Object -First 1
        if ($null -eq $registered) {
            continue
        }
        if ($registered.completeness_level -eq 'archive-gap' -and $review.extraction_status -ne 'archive-gap') {
            Add-Failure "Source register archive-gap is not reflected in the coverage ledger: $($review.source_family_id)"
        }
    }
}

$provisionRegisterPath = Join-Path $RepositoryRoot 'data\provision-version-register.json'
$temporalLinksPath = Join-Path $RepositoryRoot 'data\event-provision-links.jsonl'
if ((Test-Path -LiteralPath $provisionRegisterPath -PathType Leaf) -and
    (Test-Path -LiteralPath $temporalLinksPath -PathType Leaf) -and
    $null -ne $fullEvents) {
    $provisionRegister = Get-Content -LiteralPath $provisionRegisterPath -Raw | ConvertFrom-Json
    $provisionIds = @($provisionRegister.provisions.provision_id)
    $temporalLinks = @(Get-Content -LiteralPath $temporalLinksPath | Where-Object {
        -not [string]::IsNullOrWhiteSpace($_)
    } | ForEach-Object { $_ | ConvertFrom-Json })
    if ($temporalLinks.Count -ne $fullEvents.Count) {
        Add-Failure "Temporal-link count does not match full corpus: links=$($temporalLinks.Count), events=$($fullEvents.Count)"
    }
    $duplicateTemporalIds = @($temporalLinks | Group-Object event_id | Where-Object Count -gt 1)
    if ($duplicateTemporalIds.Count -gt 0) {
        Add-Failure "Duplicate temporal-link event IDs: $(($duplicateTemporalIds.Name | Sort-Object) -join ', ')"
    }
    if ((Compare-Object -ReferenceObject @($fullEvents.event_id | Sort-Object) -DifferenceObject @($temporalLinks.event_id | Sort-Object)).Count -ne 0) {
        Add-Failure 'Temporal links do not cover exactly the full-corpus event IDs'
    }
    foreach ($link in $temporalLinks) {
        foreach ($provisionId in @($link.current_comparator_ids)) {
            if ($provisionIds -notcontains $provisionId) {
                Add-Failure "Temporal link references an unknown provision: $($link.event_id) = $provisionId"
            }
        }
        if ($link.mapping_method -ne 'deterministic-keyword-and-source-rules-v2' -or
            $link.review_status -ne 'candidate-auto-mapped' -or
            $null -ne $link.reviewed_by -or
            $null -ne $link.reviewed_at) {
            Add-Failure "Temporal link does not disclose its automated candidate status: $($link.event_id)"
        }
    }
}

$accuracyFoundationScript = Join-Path $RepositoryRoot 'scripts\validate_accuracy_foundations.py'
if (Test-Path -LiteralPath $accuracyFoundationScript -PathType Leaf) {
    $accuracyFoundationOutput = @(& python $accuracyFoundationScript --root $RepositoryRoot 2>&1)
    if ($LASTEXITCODE -ne 0) {
        Add-Failure "Accuracy-foundation validation failed: $($accuracyFoundationOutput -join ' | ')"
    }
}

if ((Test-Path -LiteralPath $fullSummaryPath -PathType Leaf) -and
    (Test-Path -LiteralPath $fullEnforcementPath -PathType Leaf) -and
    (Test-Path -LiteralPath $fullTechnicalPath -PathType Leaf) -and
    (Test-Path -LiteralPath $coverageLedgerPath -PathType Leaf)) {
    $fullSummary = Get-Content -LiteralPath $fullSummaryPath -Raw | ConvertFrom-Json
    $coverageLedger = Get-Content -LiteralPath $coverageLedgerPath -Raw | ConvertFrom-Json
    $enforcementCount = @(Get-Content -LiteralPath $fullEnforcementPath | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }).Count
    $technicalCount = @(Get-Content -LiteralPath $fullTechnicalPath | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }).Count
    if ($fullSummary.enforcement_event_count -ne $enforcementCount -or
        $fullSummary.technical_event_count -ne $technicalCount -or
        $fullSummary.total_event_count -ne ($enforcementCount + $technicalCount)) {
        Add-Failure 'Full-corpus summary counts do not match the event files'
    }
    if ($fullSummary.source_review_count -ne @($coverageLedger.source_reviews).Count) {
        Add-Failure 'Full-corpus summary source count does not match the coverage ledger'
    }
    $archiveGapIds = @($coverageLedger.source_reviews | Where-Object extraction_status -eq 'archive-gap' | Sort-Object source_family_id | ForEach-Object source_family_id)
    if ((Compare-Object -ReferenceObject $archiveGapIds -DifferenceObject @($fullSummary.archive_gap_source_family_ids | Sort-Object)).Count -ne 0) {
        Add-Failure 'Full-corpus summary archive-gap IDs do not match the coverage ledger'
    }
    if ($archiveGapIds.Count -gt 0 -and $fullSummary.public_exhaustiveness_status -ne 'not-established-archive-gaps-remain') {
        Add-Failure 'Full-corpus summary overstates public exhaustiveness while archive gaps remain'
    }
    $actualProvisionCounts = @{}
    foreach ($group in @($fullEvents | Group-Object provision_resolution_status)) {
        $actualProvisionCounts[$group.Name] = $group.Count
    }
    foreach ($summaryCount in @($fullSummary.provision_resolution_counts)) {
        if ($actualProvisionCounts[$summaryCount.status] -ne $summaryCount.count) {
            Add-Failure "Full-corpus provision-resolution count is wrong for $($summaryCount.status)"
        }
        $actualProvisionCounts.Remove($summaryCount.status)
    }
    if ($actualProvisionCounts.Count -gt 0) {
        Add-Failure "Full-corpus summary omits provision-resolution statuses: $(($actualProvisionCounts.Keys | Sort-Object) -join ', ')"
    }
}

$timelinePath = Join-Path $RepositoryRoot 'knowledge-base\D00-Enforcement-Event-Timeline-2006-2026.md'
if (Test-Path -LiteralPath $timelinePath -PathType Leaf) {
    $timelineYears = @(Select-String -LiteralPath $timelinePath -Pattern '^\| (20\d{2})' | ForEach-Object { [int]$_.Matches[0].Groups[1].Value })
    if ($timelineYears.Count -lt 60) {
        Add-Failure "D00 has fewer than 60 selected timeline records: $($timelineYears.Count)"
    }
    for ($index = 1; $index -lt $timelineYears.Count; $index++) {
        if ($timelineYears[$index] -lt $timelineYears[$index - 1]) {
            Add-Failure "D00 timeline is out of year order at record $($index + 1)"
            break
        }
    }
    $eventExportPath = Join-Path $RepositoryRoot 'data\enforcement-events-selected.jsonl'
    if (Test-Path -LiteralPath $eventExportPath -PathType Leaf) {
        $eventRecords = @(Get-Content -LiteralPath $eventExportPath | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | ForEach-Object { $_ | ConvertFrom-Json })
        $exportCount = $eventRecords.Count
        if ($exportCount -ne $timelineYears.Count) {
            Add-Failure "D00 and selected event export count differ: D00=$($timelineYears.Count), JSONL=$exportCount"
        }
        foreach ($event in $eventRecords) {
            if ($null -eq $event.statuses -or @($event.statuses).Count -eq 0) {
                Add-Failure "Selected event has no structured status list: $($event.date) $($event.entity)"
            }
        }
    }
}

$v4KeyedPath = Join-Path $RepositoryRoot 'review\questions\case-question-bank-v4.jsonl'
if (Test-Path -LiteralPath $v4KeyedPath -PathType Leaf) {
    $v4Records = @(Get-Content -LiteralPath $v4KeyedPath | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | ForEach-Object { $_ | ConvertFrom-Json })
    $requiredQuestionJurisdictions = @('ACT', 'NSW', 'NT', 'QLD', 'SA', 'TAS', 'VIC', 'WA')
    foreach ($jurisdiction in $requiredQuestionJurisdictions) {
        $count = @($v4Records | Where-Object { $_.jurisdiction -eq $jurisdiction }).Count
        if ($count -lt 5) {
            Add-Failure "v4 question bank has fewer than five questions for ${jurisdiction}: $count"
        }
    }
    $nationalCount = @($v4Records | Where-Object { $_.jurisdiction -eq 'National/Cross-jurisdiction' }).Count
    if ($nationalCount -lt 15) {
        Add-Failure "v4 question bank has fewer than 15 national or cross-jurisdiction questions: $nationalCount"
    }

    $round3GradePath = Join-Path $RepositoryRoot 'review\results\case-loop-v4-grades-round3.jsonl'
    if (-not (Test-Path -LiteralPath $round3GradePath -PathType Leaf)) {
        Add-Failure 'Missing v4 round-3 grade file'
    }
    else {
        $round3Grades = @(Get-Content -LiteralPath $round3GradePath | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | ForEach-Object { $_ | ConvertFrom-Json })
        if ($round3Grades.Count -ne 100) {
            Add-Failure "Expected 100 v4 round-3 grades, found $($round3Grades.Count)"
        }
        if ((Compare-Object -ReferenceObject @($v4Records.id) -DifferenceObject @($round3Grades.id)).Count -ne 0) {
            Add-Failure 'v4 keyed and round-3 grade IDs do not match'
        }
        $nonPass = @($round3Grades | Where-Object { $_.grade -ne 'pass' }).Count
        if ($nonPass -ne 0) {
            Add-Failure "v4 round-3 audit contains non-pass records: $nonPass"
        }
    }
}

$v5RequiredResults = @(
    'review\results\case-loop-v5-evidence-packets.jsonl',
    'review\results\case-loop-v5-retrieval-report.json',
    'review\results\case-loop-v5-double-check-summary.json',
    'review\results\case-loop-v5-grades-final.jsonl'
)
foreach ($relativePath in $v5RequiredResults) {
    if (-not (Test-Path -LiteralPath (Join-Path $RepositoryRoot $relativePath) -PathType Leaf)) {
        Add-Failure "Missing v5 professional result: $relativePath"
    }
}

$v5BenchmarkScript = Join-Path $RepositoryRoot 'scripts\validate_professional_benchmark.py'
if (Test-Path -LiteralPath $v5BenchmarkScript -PathType Leaf) {
    $v5BenchmarkOutput = @(& python $v5BenchmarkScript --root $RepositoryRoot 2>&1)
    if ($LASTEXITCODE -ne 0) {
        Add-Failure "v5 benchmark validation failed: $($v5BenchmarkOutput -join ' | ')"
    }
}

$v5ResultScript = Join-Path $RepositoryRoot 'scripts\validate_professional_results.py'
if ((Test-Path -LiteralPath $v5ResultScript -PathType Leaf) -and
    (Test-Path -LiteralPath (Join-Path $RepositoryRoot 'review\results\case-loop-v5-grades-final.jsonl') -PathType Leaf)) {
    $v5ResultOutput = @(& python $v5ResultScript --root $RepositoryRoot --require-perfect 2>&1)
    if ($LASTEXITCODE -ne 0) {
        Add-Failure "v5 professional result validation failed: $($v5ResultOutput -join ' | ')"
    }
}

$v5DoubleCheckPath = Join-Path $RepositoryRoot 'review\results\case-loop-v5-double-check-summary.json'
if (Test-Path -LiteralPath $v5DoubleCheckPath -PathType Leaf) {
    $v5DoubleCheck = Get-Content -LiteralPath $v5DoubleCheckPath -Raw | ConvertFrom-Json
    if ($v5DoubleCheck.question_count -ne 100 -or
        $v5DoubleCheck.passed_question_count -ne 100 -or
        $v5DoubleCheck.blocking_error_count -ne 0) {
        Add-Failure "v5 double-check gate failed: passed=$($v5DoubleCheck.passed_question_count)/$($v5DoubleCheck.question_count), blocking=$($v5DoubleCheck.blocking_error_count)"
    }
}

$coveragePath = Join-Path $RepositoryRoot 'knowledge-base\D17-Australia-Wide-Jurisdiction-and-Enforcement-Register.md'
if (-not (Test-Path -LiteralPath $coveragePath -PathType Leaf)) {
    Add-Failure 'Missing D17 jurisdiction register'
}
else {
    $coverage = Get-Content -LiteralPath $coveragePath -Raw
    $requiredJurisdictions = @(
        'Australian Capital Territory',
        'New South Wales',
        'Northern Territory',
        'Queensland',
        'South Australia',
        'Tasmania',
        'Victoria',
        'Western Australia'
    )
    foreach ($jurisdiction in $requiredJurisdictions) {
        if (-not $coverage.Contains($jurisdiction)) {
            Add-Failure "D17 does not name required jurisdiction: $jurisdiction"
        }
    }
}

$mapPath = Join-Path $RepositoryRoot 'COMPLIANCE-MAP.md'
if (-not (Test-Path -LiteralPath $mapPath -PathType Leaf)) {
    Add-Failure 'Missing COMPLIANCE-MAP.md'
}
else {
    $map = Get-Content -LiteralPath $mapPath -Raw
    foreach ($domainNumber in 0..18) {
        $domain = 'D{0:d2}' -f $domainNumber
        if (-not $map.Contains($domain)) {
            Add-Failure "COMPLIANCE-MAP.md does not route $domain"
        }
    }
}

if ($failures.Count -gt 0) {
    Write-Host "Repository validation failed with $($failures.Count) issue(s):" -ForegroundColor Red
    foreach ($failure in $failures) {
        Write-Host " - $failure" -ForegroundColor Red
    }
    exit 1
}

Write-Host "Repository validation passed." -ForegroundColor Green
Write-Host "Text files checked: $($textFiles.Count)"
Write-Host "JSON files checked: $($jsonFiles.Count)"
Write-Host "JSONL files checked: $($jsonlFiles.Count)"
Write-Host 'Jurisdictions checked: 8'
Write-Host 'Domains routed: D00-D18'
Write-Host "Official source families checked: $($sourceRegister.sources.Count)"
Write-Host "Selected D00 events checked: $($timelineYears.Count)"
Write-Host 'Case loops checked: v3, v4 and v5, 100 records each'
Write-Host 'Archived benchmark artifact checks are not current legal accuracy or delivery readiness certification.'
