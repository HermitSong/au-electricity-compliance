# Public Distribution Profile

This is an intentionally smaller public edition of a local research project.
It is not a byte-identical export of the local evidence archive.

## Included

Original code and tests, 51 authored knowledge pages, curated public-event metadata,
jurisdiction/source registers, candidate temporal links, historical review metadata,
synthetic examples and a source-oriented contribution workflow.

`evidence/manifest.json` contains source-reference metadata only, with an empty
attachment list. Official source bytes are acquired separately into a private
local directory, subject to applicable permissions. They are not relicensed under
the project licence or automatically approved for legal answers.

The `source-artifact-ledger.jsonl` and clause receipts record the originating local
research inventory. Their historical `snapshot_path` or capture-status fields do
not imply those files ship in this repository. Use actual byte/span checks to
establish local availability. References to omitted run logs, snapshots and
diagnostics in legacy documents describe local-only artifacts, not bundled files.

## Excluded

- All official PDFs/HTML, screenshots, page renders and bulk extracted source text.
- OCR output, browser/download manifests, recovery bundles and local backups.
- SQLite indexes, credentials, machine configuration and vendor dependencies.
- Private answer runs, gold answers, real enterprise data and operational outputs.

Publisher-derived narratives in event descriptions, outcomes and instrument fields
are reviewed for replacement with concise factual summaries, curated status notes
or explicit detail gaps. Instrument mappings retain legal identifiers, not copied
announcement narratives. The earlier word-count filter was only a triage aid,
not a legal copying threshold or proof of authorship. Original event identifiers,
dates, statuses and source URLs are retained. Affected records carry a
`public_distribution_note`. This projection is not a fresh legal determination.

## Rebuild Locally

`python -B scripts/build_search_index.py` indexes only the material present.
An empty `data/source-text-chunks.jsonl` preserves the canonical input contract;
it contains no official text. The public HPR chain keeps omitted span identifiers
under `undistributed_source_evidence_ids` and retrieves event metadata only.
Raw-original omission means exact-source and current-law gates cannot inherit the
local research environment's approvals. A clean checkout is useful for discovery,
case chronology and workflow development, not source-complete legal confirmation.

To work with originals, first use `skills/au-lawful-source-acquisition/SKILL.md`
and `SOURCE-ACQUISITION.md` to assess lawful access and local use for the actual
source. Use the permission-gated collector for downloading, preserving URL,
retrieval date, bytes, source hash and extraction quality. Review version,
applicability, exact spans and later treatment before adopting a binding.
Do not bypass access challenges, overwrite immutable receipts or treat a download
as a new legal review. Source maintenance can change canonical hashes and invalidate
old packets; that is intentional. Downloaded files stay out of this public edition.
Do not route around the gate through historical snapshot/browser commands, which
are disabled. Offline imports and extraction remain separately reviewed local work.

## Release Checks

The public exclusion checks and staged-content scan reduce accidental disclosure; they
are not a universal secret detector, rights opinion or security certification.
Source-readiness gaps remain visible and must not be converted into passing legal
checks merely to make a demo succeed.

## Earlier Public History

The first public preview, commit `59b958b`, included two AEMO PDFs and two derived
page images with publisher attribution. This change removes them from the current
tree as a conservative distribution-policy choice, not a finding of infringement.
Earlier commits and third-party clones may still contain those attachments and
the publisher-derived event passages replaced by this projection. No guarantee
of historical erasure or recall is made. No GitHub Releases existed at this review.
History rewriting requires a separate, explicitly authorised operation, a private
backup and verification of refs; deleting current files alone is not history cleanup.
