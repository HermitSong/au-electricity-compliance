# Australian Electricity Compliance Map

**Baseline:** 27 August 2026 (Australia/Adelaide)

This map routes a question to the minimum knowledge-base pages that must be read. Cross-domain questions are normal. An answer is not Australia-wide merely because it cites the NER or an AER case.

## Mandatory Routing Controls

| Question characteristic | Read first |
|---|---|
| Australia-wide, all states, all jurisdictions or national completeness | `COVERAGE.md`, D17, then D18 |
| Enforcement, penalty, prosecution, court case, incident, last 20 years or historical conflict | D00, then the substantive domain |
| A rule or case may have changed, been appealed or remain unresolved | D00 status note and the latest official instrument or judgment |
| Project-specific answer | D01 and D17 for jurisdiction, then every applicable lifecycle domain |

## Domain Map

| Domain | Scope | Principal bodies or instruments | Knowledge-base route |
|---|---|---|---|
| D00 | Enforcement and event chronology | AER, Federal Court, ACCC, ESC, Energy Safe, state regulators, ombudsman and technical reports | `knowledge-base/D00-Enforcement-Event-Timeline-2006-2026.md` |
| D01 | Legal hierarchy, regulators and licensing | NEL, NER, NERL, state application laws, licences and exemptions | `knowledge-base/D01-Legal-Hierarchy-State-Regulators.md`, `knowledge-base/core/Regulatory-Bodies.md` |
| D02 | Wholesale conduct and enforcement | AER, AEMO, NER Chapters 2-4, bidding, dispatch, PASA and performance standards | `knowledge-base/D02-AER-Wholesale-Enforcement-Bidding.md` |
| D03 | Settlement and prudentials | AEMO settlement, maximum credit limit, credit support and default | `knowledge-base/core/Market-Structure/Settlement-Prudential.md` |
| D04 | Retail conduct and cases | NERL, NERR, AER guidelines, Victorian retail rules and enforcement cases | `knowledge-base/D04-Retail-Enforcement-Case-Library.md`, `knowledge-base/core/Market-Structure/Retail-Compliance.md` |
| D05 | Connections and DER | NER Chapters 5 and 5A, performance standards, DNSP standards, AS/NZS 4777.2, dynamic exports | `knowledge-base/D05-AS4777-DER-Dynamic-Export.md`, `knowledge-base/core/Market-Structure/DNSP-Connection-Standards.md` |
| D06 | FCAS and ancillary services | AEMO MASS, ASU classification, enablement and causer-pays arrangements | `knowledge-base/core/Market-Structure/FCAS-Ancillary.md` |
| D07 | Electrical and network safety | State and territory electrical-safety laws, licensing, certificates, incident notification and major network duties | `knowledge-base/D07-State-Electrical-Safety-Regulators.md` |
| D08 | Work health and safety | Model WHS laws, Victorian OHS law, officers, principal contractors, SWMS and industrial manslaughter | `knowledge-base/D08-WHS-Work-Health-Safety.md` |
| D09 | Environment and planning | Commonwealth referral, state approvals, BESS fire interface, conditions and decommissioning | `knowledge-base/D09-Environment-Planning-Approvals.md` |
| D10 | Emissions and renewable schemes | NGER, Safeguard, Renewable Energy Target certificates, CIS and renewable claims | `knowledge-base/D10-NGER-Safeguard-LGC-CIS-GO.md` |
| D11 | Cyber security and data | SOCI Act, CIRMP, mandatory incident reporting, AESCSF and operational data controls | `knowledge-base/D11-Cyber-Security-SOCI-AESCSF.md` |
| D12 | Complaints and consumer protection | State ombudsman schemes, Australian Consumer Law, hardship and embedded-network complaint pathways | `knowledge-base/D12-Ombudsman-Consumer-Protection.md` |
| D13 | Metering | NER Chapter 7, metering coordinator, provider and data-provider roles, metrology and smart meters | `knowledge-base/D13-Metering-Compliance-NER-Ch7.md` |
| D14 | Network pricing and asset registration | TSS, DUoS, TUoS, access, battery registration pathways and current fees | `knowledge-base/core/Market-Structure/Network-Pricing-and-Metering.md`, `knowledge-base/core/Market-Structure/Battery-5MW-Registration-Pathway.md` |
| D15 | Emergency and system security | AEMO directions, market suspension, RERT, SRAS, UFLS and major system events | `knowledge-base/D15-Emergency-System-Security.md` |
| D16 | Victorian regime | Essential Services Commission, Energy Safe Victoria, licences, retail code, safety schemes and Victorian enforcement | `knowledge-base/D16-Victoria-Regime-ESC-ESV.md` |
| D17 | Jurisdiction and enforcement-source register | Commonwealth plus ACT, NSW, NT, QLD, SA, TAS, VIC and WA frameworks and official series | `knowledge-base/D17-Australia-Wide-Jurisdiction-and-Enforcement-Register.md` |
| D18 | Compliance issue and control taxonomy | Full operating lifecycle and minimum evidence expectations | `knowledge-base/D18-Compliance-Issue-Taxonomy-and-Control-Register.md` |

## Role-Based Routes

| Role or activity | Minimum route |
|---|---|
| Electricity retailer or white-label provider | D01, D03, D04, D11, D12, D13, D16 where Victorian, D17 and D18 |
| Generator or large BESS developer | D01, D02, D05, D07, D08, D09, D10, D11, D13, D14, D15 and D17 |
| Distribution or transmission network | D01, D05, D07, D08, D09, D11, D13, D14, D15 and D17 |
| Embedded network or alternative electricity service | D01, D04, D05, D07, D12, D13, D16 where Victorian, D17 and D18 |
| DER, VPP or aggregator | D01, D02, D03, D05, D06, D11, D12, D13, D17 and D18 |
| EMS, SCADA, bidding or billing technology supplier | D02, D03, D04, D05, D06, D11, D13, D15, D17 and D18 |
| Electrical contractor or BESS installer | D05, D07, D08, D09, D11 and D17 |

## Evaluation Record

- Original blind examination: 73 of 80 strict passes in round one; 80 of 80 after corrections.
- Practical case loop: 100 enforcement and control scenarios, with separate keyed, blind-answer and audit artefacts.
- English refactor: repository-wide authored-text language scan, JSON and JSONL validation, jurisdiction coverage audit and repeated case-loop review.

See `review/EVAL-REPORT.md` and `review/results/` for evidence and limitations.
