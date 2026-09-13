# Australian Electricity Compliance

Repository: [au-electricity-compliance](https://github.com/HermitSong/au-electricity-compliance).

**Source-available:** free for learning, research and enterprise internal use.
Paid external services, white-label products and resale need separate permission.
See [Commercial Use](COMMERCIAL-USE.md). This is not OSI-approved open source.

An English-language research toolkit for finding Australian electricity rules,
connecting historical cases to their applicable legal context, and preparing
evidence-bound answers for review.

**Purpose:** reduce repeated compliance research and routine confirmation costs
without hiding missing facts, outdated rules, conflicting authorities or uncertainty.

**Status: public research preview, not legal advice or operational clearance.**
This is a Python/SQLite command-line project, not a hosted chatbot. It does not
include an AI subscription, model credentials or an autonomous enterprise service.

## What You Can Use

- 51 authored knowledge pages spanning retail, wholesale, storage, networks,
  licensing, safety, metering, consumer protection and related obligations.
- 824 enforcement/compliance records and 50 separately labelled technical events,
  linked to official sources. These are not 874 proven violations.
- A 54-family source register covering the national layer and all eight states
  and territories, with explicit collection gaps.
- A temporal evidence model distinguishing proceedings, final outcomes, appeals,
  historical rules, current comparators and unreviewed candidate mappings.
- SQLite FTS5 and canonical-file search, counter-search, addressable evidence
  packets, separate answer/reviewer adapters and bounded repair.
- A synthetic operating-record screening example. Candidates are review leads;
  an empty result does not clear the conduct.

The knowledge-wide baseline is **29 August 2026**. Six NEM battery and FY27 fee
routes were separately source-reviewed by AI on **13 September 2026**. Neither
that review nor a later software release refreshes the whole knowledge base.

## Public Edition Boundary

This repository publishes source code, authored knowledge, public-source
references and curated case metadata, plus a small [evidence bundle](evidence/README.md)
with two AEMO PDFs and two page renders under AEMO's separate permissions.
**Other original files, bulk extracted text, OCR archives, private run outputs
and prebuilt indexes are not bundled.**
Some long publisher-derived event descriptions are replaced by existing curated
status notes, with per-record projection markers. The full local research archive
has not been relicensed or uploaded in full.

Historical source hashes and clause-review receipts describe the originating
research environment, not source bytes available in a new clone. A clean public
checkout can search authored knowledge and case records, but cannot reproduce
exact-source approval without lawful source acquisition and renewed review.
Missing originals must remain a blocker, not an implied approval.

Read [Distribution Scope](DISTRIBUTION.md), [Third-Party Rights](THIRD-PARTY-NOTICES.md)
and [Coverage](COVERAGE.md) before interpreting results. All-Australia public-record
completeness remains an objective, not an achieved property.

## Quick Start

Use Python 3.11 or later with SQLite FTS5. From this repository's root:

```sh
python -m pip install -r requirements-originals.txt
python -B scripts/build_search_index.py
python -B scripts/search_kb.py "Hornsdale Power Reserve FCAS" --limit 5
python -B scripts/double_search_kb.py "battery registration SRA scheduled BDU"
```

The generated index stays local and is ignored by Git. Building an index does
not fetch originals, renew review dates or establish legal accuracy.

For an evidence-packet and answer/review handoff, read the
[English Answer Workflow](ENGLISH-ANSWER-WORKFLOW.md). Configure separate trusted
JSON command adapters yourself. Without adapters the workflow emits
`handoff-not-integrated-model`; it does not pretend to generate an answer.
Exit code `2` in a research handoff can signify an unmet evidence/release gate.

### Synthetic Operations Example

```sh
python -B scripts/screen_operations.py --transcript review/fixtures/operations-screening/meeting.txt --context review/fixtures/operations-screening/context.json --output-dir ../au-power-synthetic-demo
```

The output directory must be new and outside this repository. This example uses
only purpose-written synthetic text. Do not upload real meetings, customer data,
credentials or legal advice to this repository, its issues or pull requests.
See [Operations Screening](OPERATIONS-SCREENING.md) and [Security](SECURITY.md).

## Accuracy and Evaluation

The originating full-local implementation's 12-question targeted blind diagnostic
had **10 substantively complete answers and two partial answers**. No affirmative
material error was identified in that small AI-reviewed sample. That is not a
100% accuracy estimate, a representative expert comparison or a validated cost
saving. One applicable question initially missed a known real-case citation.

The original diagnostic used separate AI roles and a private gold set. It did
not test the full bulk archive, automatic intake or production API integration.
Post-feedback repairs are development results, not a new blind score.
See [Evaluation](EVALUATION.md) for the public-checkout tests and their limits.

Public-edition local check: **446 passes, two Windows privilege skips**, with
12 separately listed archive-dependent tests not run. The rebuilt public index
has **1,817 documents**, not the larger local archive's 4,307.

## Architecture

```text
Question + jurisdiction + role + activity + date
                    |
       Applicability and temporal routing
                    |
   Local hybrid search + case-chain expansion
                    |
       Evidence packet + scoped source gates
                    |
   Answer adapter -> counter-search -> reviewer
                    |                     |
             bounded repair <-------------+
                    |
       Cited research answer / explicit gaps
```

Hashes establish correspondence, not truth. Two agents can share an error.
Source acquisition does not approve a legal interpretation. The current system
cannot infer unprovided facts, certify a company, grant permission to act or
guarantee that no breach has occurred. A real pilot requires the gates in
[Enterprise Pilot](ENTERPRISE-PILOT.md).

## Contribute

Useful contributions include exact clause/version corrections, subsequent case
treatment, source-family gap reconciliation, portable tests and independently
adjudicated evaluation. Read [Contributing](CONTRIBUTING.md) and submit official
sources with dates. Do not include private corporate material.

## Licensing

Original software, explanations and protectable original curation:
[Project Source-Available Licence 1.0](LICENSE).
Enterprise internal use is allowed; specified external commercial offerings need
separate written permission. The custom licence has not received independent
legal review. See [Commercial Use](COMMERCIAL-USE.md).
Third-party material, statutory text, court wording, titles, names and trademarks
are not relicensed. See [Licensing Scope](LICENSING.md).
