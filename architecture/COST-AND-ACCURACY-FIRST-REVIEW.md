# Cost and Accuracy First-Principles Review

**Date:** 5 September 2026  
**Status:** evidence-backed review and proposed implementation order; runtime defects remain open  
**Owner objective:** reduce Australian electricity compliance confirmation costs with more reliable, detailed and reusable answers.

## Product decision

Build enterprise compliance decision support with a conversational interface. Do not build a second, unrestricted general legal chatbot now. Explanation, historical-case research and enterprise scenario assessment are interaction modes over the same evidence system, not separate products with different truth standards.

The user should be able to ask ordinary questions without completing a legal intake form. Ask only for facts that materially change the answer. A jurisdiction, regulated role, licence condition, customer class, contract, date or exception can be decisive; unknown facts must remain unknown. Multi-turn context needs provenance and correction, not silent assumptions carried from a previous customer.

Keep adjacent law when relevant to electricity operations: consumer protection, privacy, safety, environment, employment-related operational duties and contracts. Mark unrelated law out of scope or provide a clearly labelled general-information referral. A later broader module needs its own sources, update obligations, hidden evaluation and measured customer demand. An unrestricted mode would increase maintenance and liability exposure before improving the core workflow.

## Economic success criteria

The unit of value is a correctly resolved business matter, not a retrieved document or a fluent answer.

Total cost per matter = research + professional review + user clarification + source maintenance allocation + compute + rework + expected harm from errors.

The purpose is to remove repeated research and avoidable confirmation, not merely to prepare a brief that an expensive professional must research again. For validated routine questions, provide a direct answer, conditions, applicable sources, useful cases and next steps without per-question approval. For material or unresolved action, deliver a review-ready evidence record and a specific escalation question. More tokens are acceptable when they improve correctness; extra agent agreement alone is not evidence.

Track self-service resolution, expert minutes per resolved matter, false clearance, unnecessary refusal, source-span support, missed exceptions, case-status accuracy and maintenance effort. Use workflow-frequency weighting. Do not reward blanket refusal or conceal unanswerable work by measuring accuracy only on easy answered questions.

## Observed implementation gaps

The read-only probe report is cost-accuracy-gap-probes.json (local-only artifact; not distributed). Six of six targeted probes reproduced a gap. This is a diagnostic result, not a six-case legal accuracy benchmark. It uses existing code and stored evidence, plus one explicitly synthetic source mutation. It does not update the corpus or certify current law.

| Priority | Finding and code location | Consequence | Required acceptance test |
|---|---|---|---|
| P0 | `scripts/check_answer.py:90,94,118`: current-law packet checks are conditional on an optional `--packet`. An existing bound draft passes without a packet but fails when supplied a blocked packet. | Omitting context bypasses release, route, snapshot and binding checks. | Current-law checking requires a valid immutable packet; omission, tampered context and non-release state all fail. Validate the packet identity rather than trust JSON fields. |
| P0 | `scripts/build_provision_source_bindings.py:17,58,61`: complete page numbers acquire a verified binding without an expected source hash, instrument version or clause-text validation. Synthetic wrong-document pages 113-128 are accepted. | A page range is mistaken for verified operative legal text; a document change can silently inherit authority. | Pin reviewed document/version/hash, exact clause identifiers and text. Wrong hash, wrong PDF, headings-only text, missing exception and changed pagination must fail. |
| P0 | `scripts/route_applicability.py:122`: historical phrases suppress current intent for the entire question. | A mixed past-case/current-action question does not request a live version check. This probe demonstrates routing failure, not a completed false execution. | Split historical and current subquestions; every operative subclaim passes current-source and applicability gates independently. |
| P0 | `scripts/double_check_professional_answers.py:97` has weaker current-law conditions than `scripts/check_answer.py:79`. | All five stored v5 current-law claims fail the operational checker's source-span requirement despite the saved 100/100 batch pass. This is missing evidence validation, not proof those five legal propositions are false. | Benchmark and operational checking use one release contract. Report the old score as legacy evidence, not production accuracy; rerun after fixes. |
| P1 | `scripts/route_applicability.py:15,129`: case-insensitive `ACT` matches the ordinary word `Act`; all multiple-regime detections block. | A Victoria statute question incorrectly acquires the ACT; legitimate state plus NEM/NECF layers can be treated as incompatible. | Distinguish statute names from territory abbreviations; compose compatible regimes and ask only about genuine ambiguity. |
| P1 | `scripts/route_applicability.py:47`: FCAS and PASA collapse into `bidding and dispatch`. | The FCAS probe produces rebidding/dispatch routes but loses the FCAS route. | Preserve activity identity, multi-role applicability and jurisdiction-specific exceptions. Add FCAS, PASA, network, exempt-seller and asset-class tests. |
| P1 | `scripts/answer_kb.py:365,437`: freshness uses a global baseline; packet identity covers question/date/evidence hashes but not the full decision context. | A new verified source does not itself clear the date gate; changes to context or release metadata are not covered by that identifier. | Per-authority freshness with valid time and retrieval time; hash the canonical decision context, registers, coverage, bindings and policy version. |
| P1 | `scripts/build_operational_brief.py:82,114,121`: approval fields are empty and `may_execute` is always false. | A JSON brief is not an authenticated approval workflow; no end-to-end routine self-service value has been demonstrated. | Separate answer release, review, material-action approval and execution; prove identity, audit persistence, expiry and non-overridable legal blockers. |
| P1 | `scripts/canonical_search.py:12-13` shares document construction and tokenisation with indexed retrieval. | Two ranking paths can repeat the same omission; independent-search branding overstates assurance. | Independently discover contrary sources, amendments and appeal developments; trace every material proposition to supporting and conflicting text. |

## Coverage and temporal correctness

The stored summary reports 824 enforcement/compliance entries and 50 separately labelled technical entries, 874 total, through 29 August 2026. It reports 54 source families, with 37 archive gaps and 10 aggregate-only families. These are inventory measurements, not a completeness certificate or a count of 874 proven contraventions. The register has 34 provision routes, with only four broad page-range bindings currently marked drafting-enabled; the source mutation above qualifies that label.

Maintain two complementary workstreams: Australia-wide public-record backfill, and deeply validated operational workflows. The second does not narrow the first's eventual scope. Reconcile each source family by period, pagination, register totals and record status. Distinguish a gap from a verified zero, group notices/judgments/appeals into a case lifecycle, and never invent individual events from an anonymous aggregate. Do not make every routine answer wait for unrelated historical archives to become exhaustive.

Store conduct dates, decision dates, publication dates, rule commencement/end dates, source capture dates and later procedural developments separately. Past conduct and a proposed action can require different rule versions. A later judgment is relevant only after checking authority, issue, holding and appeal effect; it is not automatically controlling because it is newer. Preserve contrary and adverse cases as well as helpful analogies. Case cards need similarities, material differences, status and an explicit reason why they do or do not support today's proposition.

The source check in this review could retrieve EWOV's ENGIE report but could not retrieve the ESC code landing page or the supplied ESC media page through the web tool. This is an access/verification limit for this session, not proof the official sources no longer exist. No new current-law conclusion was released from those failures.

## Smallest useful architecture

1. Intake and scope: free-text question, explicit enterprise facts, unresolved assumptions and risk classification.
2. Search KB: lexical search and structured jurisdiction/date/case filters over canonical records.
3. Verify authority: fetch or reuse still-valid official text; check commencement, amendments, court status, entity-specific conditions and contrary sources.
4. Answer: separate facts, law, historical analogy and internal control recommendations; bind every material claim to exact text and state what would change the answer.
5. Challenge and second search: test exceptions and alternative interpretations, not just repeat the first answer or search using its expected citations.
6. Release: one enforceable validation contract for every route and benchmark. Release supported subanswers while clearly withholding an unresolved operational clearance.
7. Enterprise use: provide self-service answers, review-ready briefs and risk-tiered approval; retain private evidence and immutable decision history outside the public corpus.

Retain the current Python/JSON/Markdown/SQLite foundation until a measured limitation justifies another component. Graph relationships help navigate versions and case lifecycles; neither RAG nor KAG establishes legal truth. Semantic claim support, factual applicability, temporal correctness and source governance remain necessary regardless of model or retrieval brand.

## Enterprise and publication boundary

Historical review below describes the earlier local licence state. The subsequent
source-available publication policy is in `LICENSING.md`; this record is not a
current MIT/CC BY licence grant.

The public repository should contain authorised public research, source references, schemas, reproducible tests and synthetic examples. The private enterprise overlay should contain legal entities, licences, contracts, customer records, privilege-sensitive material, authority matrices and approvals. Keep access control, logs, retention and deletion rules at that boundary. Treat fetched material as untrusted data: it cannot change policy, prompts, tools or approval permissions.

The existing `LICENSE` covers authored Markdown under CC BY 4.0 and excludes official documents. It does not explicitly license the Python/PowerShell code or JSON data, and exclusion language does not itself establish redistribution permission for third-party PDFs/snapshots. Inventory rights, personal information, secrets and local paths before release. Do not silently relicense or remove assets during this review. GitHub's [licensing guidance](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository) confirms that public visibility is not a substitute for an appropriate software licence.

## Proposed delivery order

1. Repair and regression-test the six reproduced gaps; unify checking and remove unsupported assurance claims.
2. Validate a small set of high-frequency workflows end to end, while continuing national archive backfill. Use retail billing/complaints/payment difficulty as an initial hypothesis, not a permanent scope restriction; market operators may need a different first slice.
3. Complete exact authority bindings, real-case status/temporal review and workflow-specific fact collection for those slices.
4. Add the answer experience and risk-tiered records described in [Approval Examples](RISK-TIERED-APPROVAL-EXAMPLES.md), without connecting autonomous production actions.
5. Run a held-out, real-scenario evaluation and a matched human-workflow pilot. Separate question authors, answerers and independent expert adjudicators. Keep the final test set sealed; optimise on a different development set. An additional 100 internally generated questions alone is insufficient evidence.
6. Publish only after the relevant release gates (local-only artifact; not distributed) are satisfied. A research-preview release may precede enterprise readiness, but must say so.

## What this review changed

Recorded the owner's cost-reduction objective and confirmations 5 and 6; qualified earlier assurance language; prepared risk-tier examples and future publication copy; added reproducible diagnostic probes. No runtime defect was fixed, no new cases were ingested, no operational advice was certified, no private data was uploaded and nothing was published to GitHub or LinkedIn.
