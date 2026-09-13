# Delivery Acceptance Evidence

This audit reports readiness evidence for the staged delivery. It does not
modify scripts, canonical records, source originals, legal classifications or
operational permissions. It uses only local evidence and makes no network
requests. It cannot certify legal accuracy or grant operational release.

## Independent Gates

| Gate | Evidence required | What does not establish it |
|---|---|---|
| Known URL text coverage | Distinct explicit URLs reconciled against preserved text; without the archive, inventory claims are labelled as such | A completed collection command or summed family totals |
| Extraction completeness | Review of substantive pages, footnotes, appendices, attachments and capture representation; critical OCR fields checked against images | Nonempty text, a text hash, all PDF page locators or two agreeing OCR engines |
| Full source-family enumeration | A jurisdiction/document-class census plus publisher indexes, pagination, periods, version histories, attachments, totals, exclusions and archive boundaries | The enforcement register, a complete known URL queue or a complete public case index |
| Case/provision association review | Exact historical source/version/locator and current comparator reviewed for jurisdiction, dates and procedural status, with independent approval evidence | An automatic link, keyword match, event count or a filled reviewer name on a candidate |
| Legal verification | Source-bound independent review of the intended claims and applicable law at the relevant date | Downloading, extraction, `current-at-baseline`, drafting flags or benchmark scores |
| Operational release | Accountable approval for a defined action/date, enforceable permissions, required checks and tested handover | A report, retrieval result, second model or research-text coverage |

`delivery_ready` is the conjunction of all gates and remains false while any
gate is blocked or unknown. The existing inputs do
not supply an acceptance protocol for a complete original-source census,
visual completeness approval, independent legal verification or action-specific
release approval. The script does not invent one or infer approval from prose.
Adding such a protocol would be a separately reviewed change, including an
explicit scope and evidence validation. The audit can establish finite-queue
coverage and detect association review metadata, but cannot promote the above
unsupported gates. This is intentional fail-closed behavior, not a failed run.

## Counting And Identity

The known URL set is the union of explicit URLs in the original inventory,
manifest, source register, coverage ledger, canonical events, provision register,
selected-source aliases and recorded alternative-source resolutions. It does
not discover new URLs by crawling or create new source families. Therefore its
count may exceed the inventory summary. Inventory summary counts are retained
as labelled claims rather than used as the audit denominator.

Global counts use unique normalized URLs. Normalization removes fragments and
lowercases scheme/host, matching the collector. It preserves query strings,
path case, HTTP versus HTTPS and other source identity differences. Per-family
counts use sets of those URLs; one URL may belong to multiple explicit families.
Summing family counts is not a global count. URLs without an evidenced family
remain in a separate membership-review queue. No hostname inference is used.

For every family, `known_url_count = text_url_count + missing_text_url_count`.
Each family also has `task_counts`, with full action records in the task queue.
`needs_ocr_url_count` overlaps either text or missing-text counts: partial PDF
text and unreviewed OCR can be searchable while incomplete. With the archive,
text counts require a readable SHA-256-matching JSON text object with nonempty
text and addressable locators. The audit checks text-object containment within
`source-originals/objects`. It does not revalidate all original binary bytes,
OCR images or visual fidelity; the existing integrity validator is separate.

Append order selects the latest manifest outcome. Failed retries retain earlier
preserved text unless an explicit `invalidates_prior_text: true` removes it.
Blocked/error or unsupported extraction records cannot supply text coverage.
Inventory claims that differ from archive-checked text generate input defects.
Absent archives leave coverage as inventory claims and block input assurance.

Event aliases associate alternate source URLs with canonical events, preventing
event duplication; they do not transfer source-text coverage. Fragment aliases
share a URL identity. An identified relocated report remains a preserved current
representation of its canonical source, not proof of historical byte equality.
Current-policy successors, corrected directories and public-register counterparts
remain separate URLs and never close a missing original merely because they
describe the same event. Every recorded alternative creates an identity task.

## Zero And Unknown

An empty URL set or zero event counter never establishes that a family has no
public records. `aggregate-only` with zero means no individual-case count is
established. `unknown` and `archive-gap` with zero also remain unknown.

`verified-zero-in-ledger-scope` means the ledger explicitly reports numeric zero,
uses `complete-case-indexed` or `complete-series-indexed`, records source URL,
public date scope, checked pages/years and review date, has an explicitly empty
gap list, and has no conflicting canonical events. This is a qualified ledger
claim, not a new independent finding. A nonempty gap list is conservatively
treated as unresolved, even if prose qualifies its scope. All families' broader
original-source enumeration remains `unknown`, including verified scoped zeroes.

## Associations And Review Candidates

The audit reconciles one event-provision link per canonical event and requires
referenced comparator IDs to exist. `independently-approved` plus nonempty
`reviewed_by`, `reviewed_at` and `review_evidence_ids` is the only recognized
positive review metadata combination. Candidate statuses remain unreviewed even
when reviewer fields are populated. This checks metadata, not reviewer identity,
the substance of cited evidence or independent legal correctness. Missing,
duplicate and orphan links generate work rather than disappearing from counts.

Structured event/link status mismatches and final-status records accompanied by
pending/stay language are review candidates. Signals include event notes, link
notes and the matching preserved source's text units. Reports retain source URLs,
locators and excerpts. A shared source may concern another event; an ended stay
may legitimately precede a final outcome. These are deliberately conservative
review signals, never automated legal reclassification or legal conclusions.
The detector is a bounded language check, not exhaustive procedural-status review.

## Reproducible Commands

Run from the knowledge-base root, `<repository-root>`:

```powershell
python -B -m unittest discover -s review/tests -p test_delivery_readiness.py -v
python -B scripts/audit_delivery_readiness.py
python -B scripts/audit_delivery_readiness.py --require-ready
```

`--archive-root` names the read-only KB root containing `source-originals`, not
the `source-originals` directory itself. Canonical inputs always come from the
delivery root, even with an external archive. `--root` permits isolated fixtures.
`--output-dir` must resolve inside that root's `review/results`; output files use
only the `delivery-` prefix. No archive writes are performed. Tests use temporary
fixtures inside delivery `review/results` and clean them up. `-B` avoids bytecode
files outside the assigned paths. No extra Python packages are required.

Normal report generation returns 0 even when readiness is not established or
input defects are reported. `--require-ready` writes the same reports and returns
1 when readiness is not established. Invalid CLI/output paths return 2; actual
I/O failures while writing are errors. Report bytes are deterministic for the
same input bytes and archive root; no clock, network or model affects decisions.
Input hashes identify the audited snapshot and must be refreshed after changes.

The four generated reports are `delivery-readiness.json`,
`delivery-readiness.md`, `delivery-tasks.jsonl` and
`delivery-review-candidates.jsonl`. The JSON contains all family/URL counters,
gate reasons, input defects/hashes, associations, candidates and actionable tasks.
The Markdown is a compact overview. Non-ASCII source excerpts in generated
reports are escaped without changing originals.
