# Core Purpose and Operating Boundary

**Status:** cost-reduction objective and owner confirmation points 5 and 6 confirmed; remaining design details proposed  
**Updated:** 5 September 2026

## Confirmed business objective

Reduce the total cost of obtaining reliable Australian electricity compliance answers and handling day-to-day compliance scenarios. Replace repeatable research and routine confirmation work with evidence-backed self-service where validated, and reduce specialist review time on material or unresolved matters. More accurate and more detailed answers than existing practice are a performance objective, not an achieved or guaranteed capability.

Measure both correctness and usefulness: human minutes per correctly resolved matter, unnecessary escalation, customer harm, evidence quality, maintenance cost and actual workflow coverage. More documents, more tokens, more agents or a higher internal test score are not substitutes for these outcomes.

## Proposed delivery contract

For a specific legal entity, regulated role, asset or customer class, business activity, jurisdiction and decision date, the knowledge base must:

1. determine the applicable regulatory regime and identify unresolved applicability facts;
2. identify the historical and currently operative obligations without projecting an old rule into the present;
3. retrieve relevant historical enforcement, court, licence, audit, undertaking, technical and complaint-pattern examples with their true procedural status;
4. translate applicable obligations into executable controls, minimum evidence, ownership and approval requirements for day-to-day operations;
5. support every material legal or factual proposition with an addressable official source, immutable source bytes and a reproducible hash;
6. detect later amendments, commencement, repeal, appeal, stay, quashing and source correction before release; and
7. stop, disclose the gap and escalate when applicability, source currency, exact text, case status or public-source coverage cannot be established.

The system supports decisions. It does not silently make a binding legal decision, approve an operational exception or replace accountable responsibility. Routine explanations and validated low-risk scenario answers must not require individual professional sign-off merely because the user asked a question. Named approval applies to material operational action and exceptions, not every answer. A manager cannot approve away a statutory prohibition or cure missing controlling authority.

Use one conversational interface for domain explanations, status-qualified case research and structured enterprise scenarios. Expansion into unrelated general legal advice is not approved by this document. See [Cost and Accuracy Review](COST-AND-ACCURACY-FIRST-REVIEW.md) and [Approval Examples](RISK-TIERED-APPROVAL-EXAMPLES.md).

## Enterprise use cases

**10 September 2026 owner-confirmed extension:** screen authorised meeting transcripts
and operating records for candidate compliance issues, link them to rules and real
cases, and prepare a private evidence/review queue. This serves the same cost-reduction
and reliable operational decision-support objective. The extension does not approve
unrelated general legal advice, public disclosure of corporate material or autonomous
actions. See [Operating Records Screening](../OPERATIONS-SCREENING.md) and the
[publication limitations](../publication/OPERATIONS-SCREENING-LIMITATIONS.md).

The first implementation is lexical candidate discovery plus optional externally
prepared AI span proposals and controlled local KB retrieval. Semantic issue finding,
operational fact verification, policy-bound deadline calculation and authenticated
remediation tracking remain pilot prerequisites, not validated capabilities.

- **Before an action:** determine whether a proposed sale, transfer, bill, disconnection, connection, bid, dispatch response, certificate claim, installation or report may proceed and what evidence is required.
- **During operations:** monitor control exceptions, customer vulnerability flags, work orders, market submissions, licences, deadlines and third-party performance.
- **After an event:** preserve facts, identify notification triggers, classify procedural status, compare relevant cases and produce an auditable remediation record.
- **Regulatory reporting:** route the exact entity, instrument, reporting period, template, approval and submission evidence.
- **Rule change:** identify affected obligations, controls, systems, contracts, training, records and open decisions before commencement.
- **Audit and assurance:** reproduce the source, version, reasoning route, evidence, approver and decision that supported an operational outcome.

## Accuracy hierarchy

1. Operative legislation, rules, codes, licence conditions, court orders and final controlling judgments.
2. Official regulator decisions, notices, registers, guidelines and entity-specific instruments.
3. Byte-hashed official snapshots and addressable source spans.
4. Reviewed canonical event, provision, obligation and coverage records.
5. Approved temporal and applicability relationships.
6. Derived search indexes, summaries and model output.
7. Media and complaint signals, which may trigger investigation but do not establish liability.

A lower layer cannot override a higher layer. Model confidence cannot cure missing authority.

## Required output contract

An operational answer must contain:

- applicability facts and unresolved assumptions;
- answer-as-at date and source freshness;
- operative obligation and exact source span;
- explicit distinction between relevant retrieved material and provisions actually selected by the applicability route;
- executable control objective and minimum evidence;
- relevant historical cases with status and temporal warning;
- blockers, exceptions and escalation route;
- accountable owner and professional approver fields; and
- an immutable decision record.

The current brief generator always sets `may_execute` to false; it does not implement an approval transition or execution integration. The proposed design separates answer release from action approval. Even an approved answer does not itself execute an enterprise action. Material action release requires relevant evidence and authenticated approval under a versioned enterprise policy, without overriding legal blockers.

## Proposed owner confirmations

Confirmation record: the owner explicitly confirmed points 5 and 6 on 5 September 2026. Other choices remain proposals except where restated in the confirmed business objective above.

1. **Proposed refinement:** the primary product is enterprise compliance decision support with a conversational Australian-electricity legal information interface, not an unrestricted all-law chatbot.
2. Accuracy and reproducibility take priority over latency, token cost and answer completion rate.
3. The system must cover retail, wholesale, networks, generation, storage, DER, metering, safety, WHS, environment, climate, cyber and state-specific regimes across Australia.
4. Historical cases are explanatory and risk evidence. Analyse past conduct under the law applicable to that conduct and its transition rules; analyse a proposed action under the law applicable to its decision/action date. Later judgments require authority, issue, holding and appeal-status analysis, not a simple newest-document-wins rule.
5. **Confirmed:** the system may prepare a decision and control brief, but a named accountable person must approve material operational action and exceptions. Routine information queries do not individually require that approval.
6. **Confirmed:** public-source completeness must be measured and disclosed; unavailable, confidential and aggregate-only events cannot be invented. Australia-wide public-record completion remains the collection objective, not a statement of present completeness.
7. A current-law conclusion without fresh official source text and an exact addressable span must fail closed.
