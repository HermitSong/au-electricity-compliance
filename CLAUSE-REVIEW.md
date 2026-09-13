# Scoped Clause Review

The whole-KB baseline remains 29 August 2026. The September 2026 review is additive
and limited to selected NEM registration, bidding, dispatch, settlement and FY27
fee sources. A legacy `current-at-baseline` record label does not independently
establish currency: the runtime requires the actual provision, reviewed spans,
receipt and requested date to agree.

## Canonical Inputs

- `data/provision-version-register.json`: existing records preserved, new scoped
  version records added with explicit effective dates and limitations.
- `data/source-text-chunks.jsonl`: original extracted records preserved; complete
  NER v254 and current fee documents added, with exact reviewed selections.
- `data/clause-binding-candidates.json`: ordered span identities, source and text
  hashes, provision digest, effective date, verification date and scope limits.
- `data/clause-binding-approvals.json`: a separate reviewer's decision bound to the
  entire candidate digest. These are independent AI source reviews, not legal
  professional certification or cryptographic reviewer authentication.
- `data/provision-source-bindings.json`: reproducibly derived binding status.
- `data/rule-dependencies.json`: declared affected knowledge pages; not an
  exhaustive dependency graph.

Canonical files require protected maintainer write access. A hash is not a digital
signature or evidence that the file's author is authorised. An answer provider
must not write its own approval into these files.

## Review and Release

An independent reviewer checks official provenance and operative version, replays
every source selection from the pinned PDF using its page and character bounds,
reads the whole clause including exceptions, and checks transitions and scope.
The candidate must be corrected before approval if a qualifier is missing.

The current implementation admits a later-than-baseline current-rule draft only on
the exact recorded verification date. A different answer date needs another source
version check; it is not cleared by incrementing the global baseline. This strict
policy is deliberately visible and may be refined only with evidence of reliable
rule-specific refresh and change detection.

All bound spans must be present in the evidence packet. Old or changed receipts,
source bytes, provision records, extracted text or selected spans invalidate the
binding. A complete packet still does not establish semantic correctness or
project-specific applicability; use the independent answer review workflow.

```powershell
python -B scripts/build_provision_source_bindings.py --root .
python -B scripts/audit_clause_reviews.py --root . --as-of 2026-09-13
```

The audit reports expired/changed reviews and declared affected pages. It does not
fetch new law, schedule monitoring or automatically approve replacement sources.

## Operational Limits

- NER v254 took effect on 4 September 2026; earlier cases and dates retain their
  own governing rules. A later publication does not simply overwrite a holding.
- The SSC transition in NER 11.179 must accompany the settlement payment-date
  definition. A calendar and actual statement receipt are needed for a specific
  payment date; the nine-business-day shorthand is insufficient during transition.
- Registration classifications, exemption decisions, network approvals and state
  licences are separate. No template approves a particular battery configuration.
- FY27 fees are official administrative source records, not statutory clauses or
  binding project quotes. Published base fees do not cap total project costs.
- Full NER acquisition is not complete Australian public-source coverage. The
  prior coverage ledger and unresolved source families remain visible.
