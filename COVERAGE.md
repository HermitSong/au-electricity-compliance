# Coverage Standard

**Build baseline:** 29 August 2026 (Australia/Adelaide). Source-family `checked_at` dates and public date scopes remain independently recorded.

This repository is intended to cover electricity-industry compliance across Australia. In this repository, **Australia-wide** means that the following legal and regulatory layers are separately identified and routed:

1. Commonwealth and national energy law, including the NEL, NER, NERL, NERR, AEMO procedures, AER enforcement, competition and consumer law, emissions schemes, critical-infrastructure security and Commonwealth environmental law.
2. The Australian Capital Territory.
3. New South Wales.
4. The Northern Territory.
5. Queensland.
6. South Australia.
7. Tasmania.
8. Victoria.
9. Western Australia, including the WEM, the SWIS, Pilbara networks and non-interconnected systems.

## What Is Covered

The knowledge base covers the compliance lifecycle from market entry to exit:

- authorisation, licensing, exemptions and registrations;
- wholesale bidding, dispatch, availability, FCAS, settlement and prudential obligations;
- network access, connection, performance standards, metering, ring-fencing and reliability;
- retail sales, marketing, consent, billing, hardship, family violence, life support, disconnection, complaints and ombudsman membership;
- electrical safety, worker safety, bushfire and vegetation risk, incident notification and asset-management systems;
- planning, environment, emissions, renewable certificates and decommissioning;
- cyber security, critical-infrastructure duties, privacy and operational data controls;
- regulator reporting, audit, record retention, breach notification, remediation and enforcement.

## Enforcement Coverage Standard

The repository distinguishes three different forms of coverage:

| Coverage type | Meaning |
|---|---|
| `complete-case-indexed` | Every individually identifiable in-scope record on the bounded official case surface has been indexed and checked. |
| `complete-series-indexed` | Every individually identifiable in-scope record in the bounded official technical or reporting series has been indexed. |
| `archive-gap` | Accessible records have been indexed, but an identified historical, platform, selector, appeal-reconciliation or archive gap prevents a completeness claim. |
| `aggregate-only` | The official source reports totals or anonymous activity but does not publish enough case-level information to create reliable individual event rows. |

The phrase **all enforcement records** must not be used unless all relevant official registers and annual-report series for the stated jurisdiction, sector and period have been checked and `data/full-corpus-summary.json` permits that claim. A search of media releases alone is not complete.

## Status Discipline

Each enforcement or incident record must use one of these statuses or status qualifiers. The outcome field must still identify the legal mechanism, such as a court order, infringement notice or undertaking:

- `current`: a current enforcement reference at the baseline date; it does not replace the need to identify whether the outcome was a court order, notice or undertaking;
- `final-court`: final court finding or order, subject to any stated appeal status;
- `infringement`: penalty or infringement notice, which may not constitute an admission;
- `enforceable-undertaking`: binding undertaking accepted by a regulator;
- `proceedings`: allegations filed but not finally determined;
- `quashed-on-appeal`: earlier liability or penalty displaced by a later judgment;
- `old-rule`: useful historical conduct under a rule that has since changed;
- `technical-event`: incident or technical investigation, not a legal finding of contravention;
- `media-trigger`: a report that identifies a risk signal but is not an official finding;
- `review-guidance` or `compliance-review`: industry review, warning or guidance rather than a named penalty;
- `reported-breach`: a licensee-reported or regulator-identified non-compliance without a court penalty or infringement notice;
- `administrative-resolution`: correction, reimbursement, write-off, warning or monitoring without a punitive outcome;
- `licence-action`: suspension, cancellation, variation or an enforceable licence condition;
- `ombudsman-order`: a binding dispute-resolution order, not a regulator penalty or court judgment;
- `public-warning`: a named safety warning that is not by itself a prosecution, conviction or admission.

Where rules or judgments conflict over time, the latest in-force instrument and latest final appellate judgment control. The earlier event remains in the chronology with an explicit status note.

## Honest Boundary

No static repository can guarantee that it contains every unpublished investigation, confidential resolution, local-court prosecution, technical incident or self-reported low-risk breach in Australia. This repository therefore provides:

- case-level indexing where an official public register supports it;
- binding to complete official report series where case-level publication is unavailable;
- explicit evidence gaps instead of inferred completeness;
- a dated baseline and update procedure.

This is regulatory information, not legal advice. A live source and qualified Australian counsel should be used for binding decisions.
