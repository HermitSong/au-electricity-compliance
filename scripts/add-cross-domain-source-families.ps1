[CmdletBinding()]
param(
    [string]$RepositoryRoot = (Split-Path -Parent $PSScriptRoot)
)

$ErrorActionPreference = 'Stop'
$path = Join-Path $RepositoryRoot 'data\enforcement-source-register.json'
$document = Get-Content -LiteralPath $path -Raw | ConvertFrom-Json

$newSources = @(
    [ordered]@{
        id = 'AU-DCCEEW-EPBC-COMPLIANCE'; jurisdiction = 'Commonwealth'; body = 'Department of Climate Change, Energy, the Environment and Water / National Environmental Protection Agency'
        scope = @('EPBC approvals', 'approval conditions', 'infringement notices', 'environmental audits')
        coverage_type = 'case-indexed'; start_year = 2006; update_cadence = 'continuous and annual'
        url = 'https://www.dcceew.gov.au/environment/epbc/compliance'
        limitation = 'The regulator is transitioning material to the National Environmental Protection Agency; historical actions and audits are distributed across registers, annual reports and project pages.'
        coverage_start = '2006'; coverage_end = 'ongoing'; gap_periods = @('transition to the National Environmental Protection Agency from 2026-07-01 may split the live series')
        completeness_level = 'medium; project and action records are distributed across several official systems'
    },
    [ordered]@{
        id = 'AU-OAIC-PRIVACY-DECISIONS'; jurisdiction = 'Commonwealth'; body = 'Office of the Australian Information Commissioner'
        scope = @('Privacy Act', 'privacy determinations', 'enforceable undertakings', 'data breaches')
        coverage_type = 'case-indexed'; start_year = 2006; update_cadence = 'continuous'
        url = 'https://www.oaic.gov.au/privacy/privacy-assessments-and-decisions/privacy-decisions'
        limitation = 'Most complaint resolutions and notified data breaches are confidential or published only as aggregates; filter named decisions for direct electricity-sector relevance.'
        coverage_start = '2006'; coverage_end = 'ongoing'; gap_periods = @()
        completeness_level = 'high for published named decisions; aggregate-only for most complaints and notifications'
    },
    [ordered]@{
        id = 'AU-ACMA-SPAM-TELEMARKETING'; jurisdiction = 'Commonwealth'; body = 'Australian Communications and Media Authority'
        scope = @('Spam Act', 'Do Not Call Register', 'telemarketing', 'solar marketing')
        coverage_type = 'case-indexed'; start_year = 2006; update_cadence = 'continuous'
        url = 'https://www.acma.gov.au/investigations-spam-and-telemarketing'
        limitation = 'The register is economy-wide and must be filtered for electricity retailers, solar marketers and other directly electricity-related entities; older outcomes are on linked archive pages.'
        coverage_start = '2006'; coverage_end = 'ongoing'; gap_periods = @()
        completeness_level = 'high for published named investigations'
    },
    [ordered]@{
        id = 'AU-CISC-SOCI-COMPLIANCE'; jurisdiction = 'Commonwealth'; body = 'Cyber and Infrastructure Security Centre'
        scope = @('SOCI Act', 'critical electricity assets', 'CIRMP', 'cyber incident reporting')
        coverage_type = 'source-identified'; start_year = 2018; update_cadence = 'continuous and annual'
        url = 'https://www.cisc.gov.au/legislation-regulation-and-compliance/our-regulatory-principles-and-approach'
        limitation = 'Protected-information rules and national-security sensitivity mean named compliance and cyber-incident outcomes are rarely public.'
        coverage_start = '2018'; coverage_end = 'ongoing'; gap_periods = @()
        completeness_level = 'source-identified; public named outcomes are structurally limited'
    },
    [ordered]@{
        id = 'ACT-EPA-ENFORCEMENT'; jurisdiction = 'Australian Capital Territory'; body = 'ACT Environment Protection Authority'
        scope = @('environment protection orders', 'infringement notices', 'prosecutions', 'electricity projects')
        coverage_type = 'series-bound'; start_year = 2006; update_cadence = 'annual and event-driven'
        url = 'https://www.environment.act.gov.au/environmental-protection-and-water/environment-protection'
        limitation = 'Public reporting is largely aggregate and annual; no continuous electricity-only named enforcement register was identified.'
        coverage_start = '2006'; coverage_end = 'ongoing'; gap_periods = @()
        completeness_level = 'medium; named outcomes are not published as a continuous electricity-specific series'
    },
    [ordered]@{
        id = 'NSW-EPA-PUBLIC-REGISTERS'; jurisdiction = 'New South Wales'; body = 'NSW Environment Protection Authority'
        scope = @('penalty notices', 'prosecutions', 'civil proceedings', 'enforceable undertakings', 'licence notices')
        coverage_type = 'case-indexed'; start_year = 2006; update_cadence = 'continuous'
        url = 'https://www.epa.nsw.gov.au/Licensing-and-Regulation/Public-registers'
        limitation = 'The register is economy-wide and must be filtered for direct electricity-sector relevance; the register platform was transitioning during 2026.'
        coverage_start = '2006'; coverage_end = 'ongoing'; gap_periods = @('legacy register data freeze and platform transition from 2026-04-28 must be reconciled with the replacement register')
        completeness_level = 'high for registered actions subject to platform-transition reconciliation'
    },
    [ordered]@{
        id = 'NT-EPA-COMPLIANCE'; jurisdiction = 'Northern Territory'; body = 'Northern Territory Environment Protection Authority'
        scope = @('environmental approvals', 'compliance notices', 'investigations', 'prosecutions')
        coverage_type = 'series-bound'; start_year = 2006; update_cadence = 'annual and event-driven'
        url = 'https://ntepa.nt.gov.au/about-ntepa/publications/annual-reports'
        limitation = 'Compliance actions are distributed across annual reports, notices and investigation material; some outcomes are anonymous aggregates.'
        coverage_start = '2006'; coverage_end = 'ongoing'; gap_periods = @()
        completeness_level = 'medium; annual series with limited named case indexing'
    },
    [ordered]@{
        id = 'QLD-ENVIRONMENT-ENFORCEMENT'; jurisdiction = 'Queensland'; body = 'Queensland environmental regulator'
        scope = @('environmental enforcement orders', 'protection orders', 'direction notices', 'clean-up notices', 'enforceable undertakings')
        coverage_type = 'case-indexed'; start_year = 2006; update_cadence = 'continuous'
        url = 'https://apps.des.qld.gov.au/public-register/search/enforcement.php'
        limitation = 'The public register excludes warning letters, penalty infringement notices and prosecution outcomes; those require separate official publication and annual-report checks.'
        coverage_start = '2006'; coverage_end = 'ongoing'; gap_periods = @('warning letters, penalty infringement notices and prosecution outcomes are excluded from the online enforcement register')
        completeness_level = 'high for listed statutory actions; structurally incomplete for excluded enforcement classes'
    },
    [ordered]@{
        id = 'SA-EPA-COMPLIANCE'; jurisdiction = 'South Australia'; body = 'Environment Protection Authority South Australia'
        scope = @('environmental licences', 'orders', 'prosecutions', 'electricity projects')
        coverage_type = 'series-bound'; start_year = 2006; update_cadence = 'annual and event-driven'
        url = 'https://www.epa.sa.gov.au/'
        limitation = 'No continuous electricity-only case register was identified; public-register, annual-report and published prosecution material must be combined.'
        coverage_start = '2006'; coverage_end = 'ongoing'; gap_periods = @()
        completeness_level = 'medium; distributed official publication model'
    },
    [ordered]@{
        id = 'TAS-EPA-PROSECUTIONS'; jurisdiction = 'Tasmania'; body = 'Environment Protection Authority Tasmania'
        scope = @('environmental prosecutions', 'infringement notices', 'civil litigation', 'electricity projects')
        coverage_type = 'case-indexed'; start_year = 2006; update_cadence = 'continuous and annual'
        url = 'https://epa.tas.gov.au/business-industry/compliance-and-enforcement/prosecutions-by-court-proceedings-and-infringement-notices'
        limitation = 'The published prosecution list begins before the corpus period, while infringement notices and lower-level actions are not all individually published.'
        coverage_start = '1996'; coverage_end = 'ongoing'; gap_periods = @()
        completeness_level = 'high for published prosecutions; lower-level activity may be aggregate only'
    },
    [ordered]@{
        id = 'VIC-EPA-PUBLIC-REGISTERS'; jurisdiction = 'Victoria'; body = 'Environment Protection Authority Victoria'
        scope = @('prosecutions', 'civil proceedings', 'enforceable undertakings', 'remedial notices', 'permissions')
        coverage_type = 'case-indexed'; start_year = 2006; update_cadence = 'continuous'
        url = 'https://www.epa.vic.gov.au/public-registers'
        limitation = 'The register is economy-wide and must be filtered for direct electricity-sector relevance; different register classes have different historical start dates.'
        coverage_start = '2006'; coverage_end = 'ongoing'; gap_periods = @('register classes have different public start dates; enforceable-undertaking records extend back before 2015')
        completeness_level = 'high for published register classes, subject to class-specific historical limits'
    },
    [ordered]@{
        id = 'VIC-ESV-TECHNICAL-INVESTIGATIONS'; jurisdiction = 'Victoria'; body = 'Energy Safe Victoria'
        scope = @('electrical incident investigations', 'network fire investigations', 'battery incidents', 'outage investigations')
        coverage_type = 'case-indexed'; start_year = 2006; update_cadence = 'event-driven'
        url = 'https://www.energysafe.vic.gov.au/about-us/our-organisation/reports/electrical-incident-and-technical-investigations-reports'
        limitation = 'Technical investigation reports explain incident causes and recommendations; they are not by themselves findings of legal contravention. The current page does not expose a complete pre-2018 archive.'
        coverage_start = '2018'; coverage_end = 'ongoing'; gap_periods = @('2006-01-01 to 2017-12-31')
        completeness_level = 'high for individually linked reports on the current page; pre-2018 archive gap'
    },
    [ordered]@{
        id = 'WA-DWER-ENVIRONMENTAL-ENFORCEMENT'; jurisdiction = 'Western Australia'; body = 'Department of Water and Environmental Regulation'
        scope = @('environmental protection notices', 'prevention notices', 'prosecutions', 'modified penalties')
        coverage_type = 'case-indexed'; start_year = 2006; update_cadence = 'continuous'
        url = 'https://www.wa.gov.au/service/environment/business-and-community-assistance/environmental-enforcement'
        limitation = 'The register is economy-wide and must be filtered for direct electricity-sector relevance; some modified penalty records are available only for inspection at the department.'
        coverage_start = '2006'; coverage_end = 'ongoing'; gap_periods = @('some modified penalty notices are not available online')
        completeness_level = 'high for online notices and prosecutions; incomplete for offline modified penalties'
    }
)

$existingIds = @($document.sources | ForEach-Object { $_.id })
foreach ($source in $newSources) {
    if ($existingIds -contains $source.id) {
        continue
    }
    $document.sources += [pscustomobject]$source
}

$document.schema_version = '1.2'
$document.coverage_definitions | Add-Member -NotePropertyName 'cross-domain-filtered' -NotePropertyValue 'An economy-wide official source filtered to matters whose conduct materially arises from electricity generation, networks, retail, DER, storage, electricity infrastructure, marketing or customer data.' -Force

$json = $document | ConvertTo-Json -Depth 20
$encoding = New-Object System.Text.UTF8Encoding($false)
[IO.File]::WriteAllText($path, $json + [Environment]::NewLine, $encoding)

Write-Host "Source register now contains $($document.sources.Count) official source families."
