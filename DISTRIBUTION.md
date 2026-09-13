# Public Distribution Profile

This is an intentionally smaller public edition of a local research project.
It is not a byte-identical export of the local evidence archive.

## Included

Original code and tests, 51 authored knowledge pages, curated public-event metadata,
jurisdiction/source registers, candidate temporal links, historical review metadata,
synthetic examples and a source-oriented contribution workflow.

Two individually inspected AEMO PDFs and two page renders are also included under
issuer permissions in `evidence/manifest.json`. They are not relicensed under the
project licence and are not automatically indexed or approved for legal answers.

The `source-artifact-ledger.jsonl` and clause receipts record the originating local
research inventory. Their historical `snapshot_path` or capture-status fields do
not imply those files ship in this repository. Use actual byte/span checks to
establish local availability. References to omitted run logs, snapshots and
diagnostics in legacy documents describe local-only artifacts, not bundled files.

## Excluded

- Official PDFs/HTML other than the exact evidence-manifest allowlist, and bulk extracted source text.
- OCR output, browser/download manifests, recovery bundles and local backups.
- SQLite indexes, credentials, machine configuration and vendor dependencies.
- Private answer runs, gold answers, real enterprise data and operational outputs.

Publisher-derived event `issue` descriptions over 70 words, or containing publisher
contact boilerplate, are replaced by the pre-existing curated `case_status_note`
where one is available. This is a public distribution projection, not a fresh
legal determination. The original event identifiers, dates, statuses and source
URLs are retained. Affected records have an explicit `public_distribution_note`.

## Rebuild Locally

`python -B scripts/build_search_index.py` indexes only the material present.
An empty `data/source-text-chunks.jsonl` preserves the canonical input contract;
it contains no official text. The public HPR chain keeps omitted span identifiers
under `undistributed_source_evidence_ids` and retrieves event metadata only.
Raw-original omission means exact-source and current-law gates cannot inherit the
local research environment's approvals. A clean checkout is useful for discovery,
case chronology and workflow development, not source-complete legal confirmation.

To work with originals, first assess lawful access and local use for the actual
source. Then use the acquisition/import tools under `scripts/`, preserving URL,
retrieval date, bytes, source hash and extraction quality. Review version,
applicability, exact spans and later treatment before adopting a binding.
Do not bypass access challenges, overwrite immutable receipts or treat a download
as a new legal review. Source maintenance can change canonical hashes and invalidate
old packets; that is intentional. Downloaded files must stay out of public commits
unless independently cleared for redistribution.

## Release Checks

The public allowlist and staged-content scan reduce accidental disclosure; they
are not a universal secret detector, rights opinion or security certification.
Source-readiness gaps remain visible and must not be converted into passing legal
checks merely to make a demo succeed.
