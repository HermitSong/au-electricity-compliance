# Second-Round First-Principles Review

**Review date:** 5 September 2026  
**Reference purpose:** `CORE-PURPOSE-AND-OPERATING-BOUNDARY.md`

## What changed

- Current provision sources can be captured as immutable bytes with response metadata and SHA-256.
- Captured HTML and PDF sources are converted into addressable text spans and indexed separately from authored summaries.
- Search A uses SQLite FTS5; Search B independently scans canonical files in memory. They no longer share one ranking engine or index.
- Applicability routing can deterministically add a regime-level provision route after jurisdiction, actor and activity are resolved.
- Historical cases can be filtered by entity, jurisdiction, issue family, date, status, source family and current comparator.
- An evidence packet can be converted into an operational control brief that remains non-executing until controls and accountable approval are completed.
- Source freshness is a release gate rather than an informal warning.
- A separate provision-to-source binding layer now prevents instrument-level capture from being treated as exact-clause proof.
- Four high-risk Victorian ERCP version 6 routes are bound to exact clause ranges: payment difficulty, family violence, life support and disconnection.
- Operational briefs create controls only from deterministic applicability routes, not from merely relevant search results or candidate temporal links.

## Current measured boundary

- 27 distinct current provision source URLs are registered; 24 have a successful immutable capture.
- 25 official URLs have been captured in total, including the linked Victorian Energy Retail Code of Practice version 6 PDF.
- 22 captured sources have extractable text, producing 241 addressable source chunks.
- Three approved current provision routes remain blocked by bot-protected sources: NERL explicit informed consent, NERL ombudsman membership and NEM metering.
- 702 canonical URLs remain remote-only after the current-provision capture pass.
- All 874 generated event-to-current-comparator links remain candidates; 19 events have no current comparator.
- The provision and obligation registers contain 34 routes. Four are bound to exact operative clause ranges; 15 other approved-current routes have captured instrument text but no verified exact-clause binding, and three approved-current routes have no usable captured text.

## Remaining failure modes

1. **Case reproducibility gap.** Most historical event URLs do not yet have immutable source bytes or addressable passages.
2. **Clause completeness gap.** Eighteen approved-current routes still lack a verified exact-clause binding. They now fail closed instead of inheriting readiness from an instrument-level snapshot.
3. **Temporal approval gap.** Candidate event-to-current-rule links cannot be treated as reviewed legal relationships.
4. **Restricted-source gap.** AEMO and South Australian legislation sources require browser-assisted or manually deposited snapshots.
5. **Operational integration gap.** The brief has owner and approval fields but is not connected to CRM, billing, bidding, work-order, incident or document-management systems.
6. **Entailment gap.** Deterministic checks prove citation presence, status and hashes, not that every sentence is semantically entailed by the cited passage.
7. **Human benchmark gap.** Synthetic benchmark performance does not establish superiority to experienced Australian electricity compliance professionals.

## Next optimisation order

1. Capture and extract official source bytes for high-risk cases and then every accessible canonical event URL.
2. Resolve the three blocked current provision sources through browser-assisted evidence acquisition.
3. Extend the clause-complete obligation packs beyond the completed Victorian retail routes to NECF billing, consent and metering and NEM bidding, dispatch, PASA, FCAS and GPS.
4. Independently review high-risk temporal links, then expand review by source family and issue family.
5. Add control tests and evidence adapters for real enterprise systems.
6. Run a hidden benchmark designed and graded by qualified external professionals, including adversarial and incomplete-fact scenarios.

The project should not add a graph database, larger model or more autonomous agents merely to appear sophisticated. New components are justified only when they improve measured source recall, applicability, citation entailment, temporal accuracy or operational control coverage.
