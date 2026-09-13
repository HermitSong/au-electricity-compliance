---
domain: D18
title: Electricity Compliance Issue Taxonomy and Control Register
status: draft-researched
last_updated: 2026-08-27
jurisdictions: [Commonwealth, ACT, NSW, NT, QLD, SA, TAS, VIC, WA]
---

# D18 - Electricity Compliance Issue Taxonomy and Control Register

## Purpose

This taxonomy defines what counts as an electricity-industry compliance issue in this repository. It is used to test whether research and case collection cover the full operating lifecycle instead of concentrating only on retailer penalties or wholesale bidding cases.

## 1. Market Entry and Corporate Authority

| Issue family | Typical compliance failures | Minimum control evidence | Primary routing |
|---|---|---|---|
| Retail authorisation or licence | Selling without an AER authorisation, state licence or valid exemption; exceeding exemption conditions | Legal-entity and activity map, authorisation register check, exemption conditions, renewal calendar | D01, D04, D16, D17 |
| Generation, network and system-control licensing | Constructing or operating without a required state licence, authority, approval or registration | Jurisdiction decision, capacity and activity classification, licence register, conditions register | D01, D16, D17 |
| AEMO registration and classification | Incorrect participant category, failure to register an integrated resource system, exemption misuse | Registration decision, exemption instrument, asset and dispatch classification | D02, D03, D06, D14 |
| Suitability and financial capacity | Inadequate financial, technical, organisational or risk-management capability | Board-approved compliance plan, financial model, prudential evidence, responsible officers | D01, D03, D04 |

## 2. Wholesale Market Conduct and System Operations

| Issue family | Typical compliance failures | Minimum control evidence | Primary routing |
|---|---|---|---|
| Offers, bids and rebids | False or misleading offers, defective rebid reasons or timing, automated-bidding control failures | Immutable bid history, reason and decision logs, input validation, human escalation | D02 |
| Dispatch and directions | Failure to follow dispatch instructions, AEMO directions or system-security instructions | Telemetry, dispatch targets, acknowledgements, exception and incident records | D02, D15 |
| Availability and PASA | Late, inaccurate or misleading availability information | Plant capability records, outage approvals, MT PASA and ST PASA submissions, change logs | D02, D15 |
| FCAS and ancillary services | Offering unavailable capability, failing to enable or deliver services, non-compliant measurement | MASS evidence, enablement and response data, commissioning records | D06, D02 |
| Performance standards | Unapproved settings, non-compliant plant response, model or information failures | Registered performance standards, settings register, R1/R2 model validation, change approval | D05, D15 |
| Settlement and prudentials | Credit-support shortfall, settlement default, data or reallocations error | Prudential forecasts, collateral, settlement reconciliation, authorised changes | D03 |

## 3. Networks, Connections, DER and Metering

| Issue family | Typical compliance failures | Minimum control evidence | Primary routing |
|---|---|---|---|
| Connection process | Connecting before approval, violating connection agreement or negotiated access standard | Connection application, offer, GPS, commissioning and hold-point evidence | D05 |
| DNSP and DER technical settings | Wrong inverter region, export limit, dynamic-export protocol or protection settings | Approved equipment, commissioning test, firmware and settings evidence | D05 |
| Ring-fencing and access | Discrimination, information sharing, cost allocation or waiver breaches | Ring-fencing register, staff access controls, cost allocation, annual compliance report | D01, D14, D17 |
| Network reliability and quality | Failure to meet licence, code, guaranteed-service or incident-reporting requirements | Reliability data, event exclusions, customer payments, regulator reports | D07, D15, D17 |
| Metering and market data | Unauthorised role, inaccurate meter data, defective installation, privacy or access failure | Role accreditation, metrology tests, data lineage, access and correction logs | D13 |

## 4. Retail and Customer Protection

| Issue family | Typical compliance failures | Minimum control evidence | Primary routing |
|---|---|---|---|
| Marketing and consent | Misleading claims, invalid explicit informed consent, unlawful transfer or sales-agent conduct | Approved scripts, call or digital consent record, identity and authority checks | D04 |
| Offers, prices and bills | Price-cap error, missing best-offer message, unclear plan information, overcharge or undercharge errors | Tariff version, bill calculation, change notice, refund and exception evidence | D04, D12, D16 |
| Hardship and payment difficulty | Failure to identify, inform, assess or support eligible customers; defective payment plans | Customer status, capacity-to-pay assessment, offer and acceptance record, review dates | D04, D12, D16 |
| Family violence | Unsafe communication, disclosure of protected information, debt or account controls that increase risk | Protected-customer flag, safe-contact method, restricted access, trained escalation | D04, D12, D16 |
| Life support | Registration, notification, information-pack, deregistration or de-energisation failure | End-to-end retailer-distributor reconciliation, contact attempts, protected-site block | D04, D12 |
| Disconnection and reconnection | Disconnection without prerequisites, during protected periods or at a protected site; delayed reconnection | Rules engine output, notices, payment and vulnerability checks, work-order block | D04, D12, D16 |
| Complaint handling and ombudsman | Late or ineffective response, failure to identify a complaint, non-membership or non-cooperation | Complaint timestamp, classification, response, referral rights, scheme membership | D12, D04, D17 |
| Embedded and alternative supply | Invalid exemption, missing customer protections, price or disclosure breach, ombudsman non-membership | Exemption class and conditions, network map, customer contract, membership evidence | D04, D12, D16, D17 |

## 5. Safety, People and Assets

| Issue family | Typical compliance failures | Minimum control evidence | Primary routing |
|---|---|---|---|
| Electrical work and installations | Unlicensed work, missing inspection or certificate, unsafe energisation, non-compliant equipment | Worker licence, test and inspection record, certificate, approved equipment | D07 |
| Major electricity company duties | Inadequate safety management system, failure to implement accepted scheme or direction | Accepted safety scheme, audit, action closure and regulator correspondence | D07, D16 |
| Bushfire and vegetation | Missed inspection, clearance failure, bare-line or protection-system breach | Inspection completion, clearance evidence, risk model, protection settings | D07, D15, D16 |
| BESS and renewable-plant safety | Thermal-runaway, installation, emergency-response, access or fire-separation control failure | Design safety case, AS/NZS evidence, commissioning, emergency plan and drills | D07, D09 |
| WHS and officer duties | Failure to eliminate or minimise risk, consultation failure, unsafe high-risk construction work | Risk assessment, SWMS, competence, consultation, verification and officer due diligence | D08 |
| Incident notification and preservation | Late notification, inadequate scene preservation or investigation | Trigger matrix, notification timestamps, evidence preservation, corrective actions | D07, D08, D11, D15 |

## 6. Environment, Climate, Emissions and End of Life

| Issue family | Typical compliance failures | Minimum control evidence | Primary routing |
|---|---|---|---|
| Planning and environmental approval | Work before approval, condition breach, unauthorised impact or inadequate assessment | Approval pathway, conditions register, monitoring and regulator reports | D09 |
| NGER and Safeguard | Registration, reporting, measurement or baseline failure | Facility boundary, emissions data controls, audit and submission evidence | D10 |
| Renewable certificates | Improper creation, eligibility, metering or surrender; misleading renewable claims | Accreditation, generation data, certificate ledger and claims approval | D10 |
| Decommissioning and waste | Failure to fund, plan or execute safe rehabilitation and recycling | Decommissioning plan, financial assurance, waste and land-restoration evidence | D09, D10 |

## 7. Security, Data and Automated Decision-Making

| Issue family | Typical compliance failures | Minimum control evidence | Primary routing |
|---|---|---|---|
| SOCI and cyber incidents | Asset-registration, risk-program, board attestation or incident-reporting failure | Asset register, CIRMP, board record, 12-hour or 72-hour notification evidence | D11 |
| Privacy and customer data | Unauthorised access, misuse, over-retention or unsafe disclosure | Data map, lawful basis, access control, retention and breach response | D11, D12 |
| Automated systems and third parties | Rules engine, CRM, billing, bidding or outsourced provider causes systematic breach | Versioned rules, test evidence, reconciliations, exception monitoring, contract and audit rights | D02, D04, D11, D13 |
| Records and regulator reporting | Missing, inaccurate, late or misleading records and reports | Source-to-report lineage, approvals, retention schedule and correction protocol | All domains |

## 8. Required Case Annotation

Every case used to explain an obligation must state:

- event date and decision date;
- legal entity and jurisdiction;
- regulator or court;
- affected activity and issue family from this taxonomy;
- exact instrument and provision where officially available;
- allegation, finding, notice, undertaking or technical-event status;
- penalty, remediation or other outcome;
- whether the rule has changed or the outcome was appealed;
- the current operational lesson;
- the official primary source.

A later rule or final appellate decision prevails over an earlier case. The earlier case remains available as historical evidence with the appropriate D00 status label.

This page is regulatory information, not legal advice.
