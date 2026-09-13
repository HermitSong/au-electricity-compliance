# Full Public-Record Corpus Scope

**Scope clarification, 5 September 2026:** this document defines the historical event corpus. The owner's broader requirement to preserve legislation, rules, conditions, judgments, decisions, guidance and other relevant originals is defined in [Original Source Scope](ORIGINAL-SOURCE-SCOPE.md). The event exclusions below do not exclude those materials from the original-source archive. New raw acquisitions do not automatically extend the event baseline or establish legal correctness.

**Corpus period:** 1 January 2006 to 29 August 2026 inclusive  
**Build baseline date:** 29 August 2026 (Australia/Adelaide)  
**Geographic scope:** Commonwealth and National Energy Laws, the ACT, NSW, NT, Queensland, South Australia, Tasmania, Victoria and Western Australia

## Meaning of "Full"

For this repository, a full corpus means every individually identifiable electricity-sector matter discoverable in the official public source families registered in `data/enforcement-source-register.json` for the corpus period.

This definition is intentionally auditable. It does not claim access to confidential investigations, unpublished complaints, sealed court material, removed web pages that cannot be recovered, or matters reported only as anonymous aggregate counts. Those limits must appear in `data/source-coverage-ledger.json`; they must never be silently treated as zero events.

The machine-readable release status is `public_exhaustiveness_status` in `data/full-corpus-summary.json`. When it is `not-established-archive-gaps-remain`, the corpus may be described as the indexed official public corpus at its build baseline, but not as every Australian violation or every public case. The same summary lists each `archive_gap_source_family_id` so the limitation is testable rather than narrative only. Each event preserves `record_reviewed_at`, and each source review preserves `checked_at` and `public_date_scope`; the build date must not be mistaken for proof that every source family was refreshed on that day.

The corpus is complete for its stated public-record universe only when:

1. every registered official source family has one coverage-ledger review;
2. every accessible page, register entry or annual-report period in that family has been checked for the corpus period;
3. every individually identifiable in-scope matter has an event record and official source URL;
4. anonymous or aggregate-only activity is counted or described in the coverage ledger without inventing case identities;
5. inaccessible archive periods are named as gaps; and
6. the build and repository validators pass.

In each source review, `public_record_count` means the number of individually indexed rows from that source across both full event files (`enforcement` plus `technical`). `anonymous_or_aggregate_count` is reserved for reported activity that cannot be separated into event rows. A case with a withheld defendant name is still individually identifiable when it has its own official reference or URL, so it belongs in `public_record_count`, not the aggregate count.

## Enforcement and Compliance Corpus

`data/enforcement-events-full.jsonl` includes individually identifiable matters in these classes:

- final court or tribunal judgments and penalty orders;
- prosecutions and civil proceedings, with unresolved allegations labelled `proceedings`;
- infringement or penalty notices, without treating payment as an admission where the source does not;
- enforceable undertakings;
- licence suspension, cancellation, condition, rectification or other formal licence action;
- formal regulator warnings, directions, compliance notices and public warnings;
- named reported breaches, regulator findings and administrative remediation outcomes;
- named final ombudsman or systemic-issue outcomes where the official source publishes enough information to identify the matter; and
- electricity-related safety disciplinary outcomes and WHS prosecutions.

The unit of record is one official regulatory matter or outcome. Different actions arising from the same underlying conduct remain separate records when they have different legal status, decision makers or dates. The same action republished by multiple official pages is one record with the best primary URL; aliases may be retained as optional metadata.

## Technical Event Corpus

`data/technical-events-full.jsonl` separately includes individually identifiable electricity system, network and electrical-safety incidents published through registered official incident series. A technical investigation, outage, fire, shock, fatality or market event is not a contravention merely because it is serious. A violation is recorded only when an official decision or report makes that finding, and the status note must state the limit of the finding.

## Exclusions

The event files exclude:

- ordinary customer complaints with no public individual outcome;
- unnamed or statistically aggregated breaches that cannot be separated into reliable events;
- media allegations without an official record;
- consultation papers, general guidance, speeches and industry reminders that do not identify a matter;
- gas-only, water-only or economy-wide matters with no material electricity relevance;
- duplicate announcements of the same regulatory action; and
- events outside the corpus period.

Excluded aggregate activity remains visible in the source coverage ledger. Media reports may still be used as non-authoritative test scenarios elsewhere in the knowledge base, but not as full-corpus enforcement records.

## Time and Precedent Rules

Historical records are never silently rewritten to match current law. Each record keeps its event date, instrument or rule, and legal status. When an earlier outcome or interpretation conflicts with a later rule or appellate judgment:

- historical conduct is analysed under its applicable law and transitions; current action uses the applicable operative law, with later judgments assessed for authority, relevant holding and appeal effect rather than recency alone;
- the earlier record remains in the corpus;
- `status` and `case_status_note` must identify `old-rule`, `quashed-on-appeal`, supersession, pending proceedings or other limits; and
- knowledge-base explanations must link the historical record to the current controlling authority.

`data/event-provision-links.jsonl` stores a deterministic temporal candidate for every event. `historical_instrument_or_rule` states the source-time position; `current_comparator_ids` point to provision-version routes; and `mapping_method` plus `review_status` distinguish automation from independent approval. All generated links are `candidate-auto-mapped` and cannot establish current law by themselves. A comparator marked for version, transition, clause or jurisdiction checking is a routing record, not authority to state current law without live verification.

## Evidence Rules

Every event requires a direct official URL and a source-family ID from the official source register. `data/source-artifact-ledger.jsonl` separately records whether that URL has an immutable local snapshot and hashes actual snapshot bytes. A URL without a snapshot is explicitly remote-only and requires live verification; a generated index hash is not source provenance. Search-result pages and media articles are not final evidence. Where an official PDF or register contains several matters, each identifiable matter may have its own event row pointing to the same document.

Dates must be `YYYY`, `YYYY-MM` or `YYYY-MM-DD`. A day must not be invented when the source gives only a month or year. Every event also records `event_date_basis` so a judgment date, regulatory-action date, publication date, incident date and conduct period are not silently conflated.

## Refresh and Acceptance

Run:

```powershell
& .\scripts\build-full-corpus.ps1
& .\scripts\validate-repository.ps1
```

The build fails on missing source reviews, unknown source IDs, duplicate event IDs, malformed dates, missing required fields or non-English authored content. A future refresh changes the baseline date, rechecks every continuous source from the previous baseline, records changed archive availability and rebuilds the two event files and coverage ledger.
