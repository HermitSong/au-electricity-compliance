# Australia-Wide Original Source Collection

**Owner direction:** collect all Australian electricity-compliance-related source originals.  
**Collection started:** 5 September 2026  
**Status:** active backfill; completeness is not established.

**Public-edition update, 13 September 2026:** source references and original
tooling only; no original documents or screenshots are bundled. Read
`SOURCE-ACQUISITION.md` and `skills/au-lawful-source-acquisition/SKILL.md` before
collection. Download mode now requires a private output directory, explicit
`--download` and a scoped permission record. Older recovery descriptions below
are historical, not permission to reproduce their acquisition steps.

## Scope

The collection covers Commonwealth/national arrangements and all eight states and territories. It includes retail, wholesale, generation, storage, networks, connection, DER, metering, safety, WHS, consumer protection, environment, climate reporting and cyber obligations when materially relevant to electricity operations. It is broader than the enforcement-event corpus.

Required source classes are legislation and regulations; current and historical rules/codes; commencement and transition instruments; licence and exemption conditions; AEMO procedures and technical requirements; judgments, orders and appeal outcomes; regulator decisions, notices and undertakings; compliance and audit reports; reportable technical investigations; official guidance and reporting templates; publicly available ombudsman outcomes; and relevant rule-change/consultation material. Consultations and guidance retain their non-binding or proposed status.

The historical case collection retains the original 2006 onward objective. The original-law collection has no arbitrary 20-year cutoff: an older instrument or decision must be retained where it remains operative or is needed to understand a later event. Capture date, publication date, conduct period, judgment date and effective dates are separate facts. A current capture of an old page does not reconstruct how the page looked at the time of the event.

Mixed gas/electricity documents may be preserved where relevant provisions or events concern electricity. A linked document is only a relevance candidate until reviewed. Do not treat every general agency publication as an electricity compliance source.

## What full collection requires

1. Identify the source families for every jurisdiction and document class, including families not yet cited by this KB.
2. Enumerate each official index, pagination sequence, period, version history and relevant attachment. Reconcile against available register totals and archival boundaries.
3. Preserve every in-scope original whose acquisition and intended local use are lawful; record missing, restricted, unpublished or permission-unresolved material as an explicit gap.
4. Extract all substantive pages, footnotes and appendices; check page counts, OCR requirements, truncation, missing attachments and source identity.
5. Bind reviewed propositions to the exact source version and locator, with separate case-status and temporal review.

Completion of the currently known URL queue is only seed-backfill completion, not Australia-wide completeness. An index page is a discovery source, not proof that all its listed documents have been acquired. Anonymous aggregate figures do not create individually identifiable events.

## Acquisition pipeline implemented

`scripts/collect_source_originals.py` starts from canonical case/provision/source registers, existing document citations and authored knowledge-page URLs. Offline inventory is the default. Actual downloads require exact-URL, dated operator permission records separately covering automated access, copying, local storage, extraction and privacy. The bounded collector checks robots policy, uses at most four workers and serialises requests per host. Discovered attachments do not inherit rights from their parent. Authentication, denial and rate limiting create gaps; the collector does not bypass them.

Each URL outcome is appended and flushed to `source-originals/manifest.jsonl`. Original HTTP response bytes are content-addressed under `source-originals/objects/`; extracted text is a separate hashed JSON object with page or DOM-section locators. Repeated runs skip previously attempted URLs by default. `--retry-failed` is an explicit maintenance action, not a way around denied access. Only run one collector against an archive at a time.

HTML text extraction omits navigation and scripts where a main-content container exists. A short/empty shell or recognised challenge page is flagged. PDFs without extractable text on any page require OCR or blank-page review. These checks do not prove completeness, semantic accuracy, or legal currency. DOCX is parsed by XML paragraph and part; XLSX is parsed by sheet, row and cell, retaining formulas as unevaluated formulas. Layout, charts, text boxes, formatting, comments and formula results are not certified by these text representations. Packages above the 100 MB uncompressed safety limit require separate reviewed processing. Unsupported binary formats are never decoded as if they were ordinary UTF-8 prose.

The collector does not yet enumerate every site-specific pagination/version API, automate authenticated sessions or determine final legal relevance. Those remain explicit work queues. The 5 September recovery batch adds browser captures, official browser downloads, safe WorkSafe embedded-record extraction, and page-image OCR with two independent English engines. The finite-cohort reconciliation is in `review/results/source-recovery-summary.json`; it must not be advertised as nationwide exhaustiveness. Browser renderings and screenshots remain distinct from original HTTP/PDF bytes.

Non-government network operator originals are also in scope. Publisher homepages checked on 5 September 2026 include [Ausgrid](https://www.ausgrid.com.au/), [AusNet](https://www.ausnetservices.com.au/), [Energex](https://www.energex.com.au/), [CitiPower and Powercor](https://www.powercor.com.au/), [Endeavour Energy](https://www.endeavourenergy.com.au/), [Essential Energy](https://www.essentialenergy.com.au/), [TasNetworks](https://www.tasnetworks.com.au/) and [Transgrid](https://www.transgrid.com.au/). Their cited public documents are acquisition candidates subject to source-specific access and local-use permission review, but publication by a network does not make every document legislation, a binding connection condition, or current. This reviewed publisher list is not a complete Australian network census.

## Evidence and answer boundary

The new archive has its own inventory, summary and SQLite full-text search. It is deliberately separate from the existing answer index: the previously identified binding/checker defects must not cause newly downloaded material to be automatically marked verified current law. All acquired records carry `legal_review_status: not-reviewed`, `current_law_release: false` and `redistribution_status: not-cleared`.

Search results expose capture method, extraction status, source/text hashes, page or DOM locator, and known PDF pages without text. The integrity validator compares indexed text and its source pointers with the preserved extraction as well as checking file hashes; it does not certify the extraction against the visual document or establish legal accuracy.

The legacy `source-artifact-ledger.jsonl` continues to describe the existing promoted snapshot pipeline. New acquisitions are reconciled separately in `source-original-summary.json`; do not subtract acquired URLs from legacy gaps without checking text quality and admission requirements. Research-only results can be inspected and quoted with their precise provenance, but cannot themselves release an operational legal conclusion.

## Browser and OCR follow-up

Use a permitted browser session when direct public access does not produce the source. Prefer original downloads, then full rendered text with the capture representation explicitly labelled, then screenshots/OCR. A browser-generated export or screenshot is not the original HTTP/PDF file and must not be described as one. Preserve the image and OCR mapping; compare amounts, dates, negations, provisions, names and procedural status against the image. Do not alter source bytes to force them to English.

User authentication, where legitimately required, remains in the browser and outside the repository. Do not save credentials, cookies, account details or private/privileged matter contents in the public source archive. Access and reproduction rights are separate questions.

`scripts/import_browser_source.py` imports a rendered-text descriptor only after its UTF-16 character count and FNV-1a transfer fingerprint match the independently observed browser output. The archived file then receives a SHA-256 hash. The transfer fingerprint is an accidental-copy-error check, not cryptographic source authentication. The descriptor records the original URL, capture time, DOM selector, representation, attribution and scope. Only run imports while the collector is stopped, then rebuild the research index. The AER's [copyright policy](https://www.aer.gov.au/about/policies/disclaimer-copyright), checked in the browser for the example, describes CC BY 4.0 for AER-owned material with exceptions; it does not clear every source or third-party asset.

## Public Distribution Boundary

Authored documentation, schemas and metadata remain English. Lawfully acquired source bytes are preserved unchanged; translations are separate derivatives, never replacements. The raw archive, screenshots and derived full text are excluded from this references-only public edition. Public accessibility is not blanket permission to copy or redistribute copyrighted standards, subscription databases or every official PDF. Licensed or unavailable materials remain inventoried with the acquisition/rights gap rather than copied through a restriction. The project remains source-available, not OSI open source.

## Commands

```powershell
python .\scripts\collect_source_originals.py --output-root ..\au-electricity-private --inventory-only
python .\scripts\collect_source_originals.py --output-root ..\au-electricity-private --download --permissions ..\au-electricity-private\permissions.local.json --max-requests 20 --workers 1 --attachment-depth 1
python .\scripts\search_source_originals.py "ENGIE complaints" --root ..\au-electricity-private
python .\scripts\validate_source_originals.py --root ..\au-electricity-private
```

Dependencies: Python 3.11 or later, `lxml` and `pypdf`; SQLite must include FTS5. Historical runtime: Python 3.12.14, lxml 6.1.1 and pypdf 6.10.0; dependency versions are in `requirements-originals.txt`. `--root` selects the knowledge checkout; `--output-root` is now mandatory and must be private and outside Git worktrees.

Office extraction additionally uses openpyxl 3.1.5. OCR is an optional, isolated workflow; engine/model details and reproduction steps are in `review/results/source-recovery-2026-09-05.md`. Generic `--reextract` preserves specialist OCR and embedded-record extractions. The recovery merger is append-only and idempotent, invalidates known binary-as-text mistakes, and keeps replacement URLs separate from historical originals.

Use `--inventory-only` after an interrupted or completed batch to reconstruct inventories/search from saved outcomes without making network requests. Review `data/source-original-summary.json`, `data/source-original-inventory.jsonl` and the manifest before describing coverage. A successful command means the batch completed; it does not mean every URL was accessible or every document is legally verified.

`--inventory-only --reextract` refreshes extraction from preserved bytes without changing their original retrieval dates. `--max-runtime-seconds` bounds scheduling, then finishes in-flight work. `--resume-host-deferred` can process never-requested URLs postponed after another path's 401/403; the denied path itself is not retried by that option. Per-host request spacing and robots requirements remain in force. `data/source-original-gap-queue.jsonl` separates pending downloads, access review, browser rendering, OCR/blank pages, format extraction and substantive/rights review. The generated human-readable progress report is `review/results/original-source-collection-report.md`.
