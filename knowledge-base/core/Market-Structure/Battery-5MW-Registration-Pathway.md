---
country: Australia
type: market-structure
category: battery-licensing
last_updated: 2026-09-13
status: draft-researched
sources:
  - https://energy-rules.aemc.gov.au/ner/818
  - https://www.aemo.com.au/-/media/files/electricity/nem/participant_information/registration/2024/registration-fact-sheet-nem-battery-systems.pdf
  - https://www.aemo.com.au/-/media/files/about_aemo/energy_market_budget_and_fees/2025/aemo-final-budget-and-fees-fy26.pdf
  - https://www.aemo.com.au/-/media/files/about_aemo/energy_market_budget_and_fees/2026/aemo-final-budget-and-fees-fy27.pdf?rev=6b35a59f8cfc49b58dd02205fc0770e0&sc_lang=en
  - https://www.aemo.com.au/-/media/files/electricity/nem/participant_information/registration/2026/market-registration-invoice-fact-sheet.pdf?rev=4906ebba9fe545e595ae2b260aaa8a22&sc_lang=en
  - https://www.sapowernetworks.com.au/public/download.jsp?id=337829
  - https://www.aemo.com.au/-/media/files/initiatives/integrating-energy-storage-systems-project/iess-final-integrated-resource-provider-transition-plan.pdf
  - https://www.aemo.com.au/energy-systems/electricity/national-electricity-market-nem/participate-in-the-market/registration/register-as-an-irp-in-the-nem
  - https://www.aemo.com.au/energy-systems/electricity/national-electricity-market-nem/participate-in-the-market/registration/registration-fact-sheets-and-guides
tags: [australia, battery, BESS, IRP, 5MW, registration, scheduled-bidirectional, FY26-fees, FY27-fees, SAPN, FCAS, SA]
---

> **Nav**: [[../_AU-Overview|Australia]] > **Market Structure** > **Battery 5MW Registration Pathway**

# 5 MW Standalone Battery — NEM Registration & Discharge Settlement Pathway

> **Source review: 13 September 2026.** Registration, classification, connection applicability and AEMO fees were reviewed against primary sources, including NER v254, effective 4 September 2026. An ordinary standalone 5 MW battery is normally a **scheduled bidirectional unit (BDU)**; the Rules include specific AEMO-approved alternatives. This is a scoped research update, not certification of every technical, cost or timeline statement on this page. See source review (local-only artifact; not distributed).

> **Jurisdiction boundary:** The registration, NER Chapter 5 and NEM settlement content on this page is NEM-specific. Section 5A is a South Australian example for a distribution-connected project in the SAPN network. It must not be applied to the WA/WEM or NT frameworks, and the SAPN fee schedule must not be applied to another NEM DNSP.

## TL;DR — Registration and Classification Are Separate Tests

| Configuration | Registration / exemption | Unit classification if registration applies | Connection route |
|---------------|--------------------------|---------------------------------------------|------------------|
| Standalone system below 5 MW | A standing exemption may apply if all AEMO conditions are met; direct market participation requires registration | Normally non-scheduled BDU; scheduled classification requires AEMO approval | Apply the Chapter 5 / 5A tests in section 2 |
| BDU at least 5 MW, or BDUs totalling at least 5 MW at a common connection point | Normally IRP registration for the integrated resource system; assess each owner/controller/operator and any approved intermediary exemption | Scheduled BDU under 2.2.2(a1), subject to the specified AEMO-approved alternatives | Normally Chapter 5 for a registered standalone project, including distribution connections |

**Exactly 5 MW meets the BDU scheduling threshold.** It is a nameplate-rating test, including the common-connection-point aggregate, not an export-limit, MWh-duration or portfolio-size test. AEMO's classification guide measures production and consumption separately; meeting the threshold in either direction is sufficient.

---

## 1. Registration, Exemptions and Unit Classification

NER **2.1A.1(b)** requires each person owning, controlling or operating a grid-connected integrated resource system to register as an IRP, subject to **2.1A.2** exemptions. A qualifying exemption is different from non-scheduled classification. Under **2.1A.2(c)**, rule 2.2 does not require classification of units within a system covered by that exemption.

An **IRP-SRA** acts for eligible small resource connection points under **2.2.8**. Eligibility requires the relevant small-unit definitions and system exemptions; a battery below 5 MW within a larger system is not automatically exempt. A formal **2.9.3 intermediary exemption** instead allows an approved registered participant to act for an otherwise registration-liable person. A commercial optimiser or aggregator contract alone does not establish that exemption; **2.9.3(d)(5)** retains joint and several liability for the specified intermediary acts and omissions.

### Scheduled BDU Default and Exceptions

NER **2.2.2(a1)** applies at 5 MW or above, including a group of BDUs at a common connection point. Its alternatives require AEMO approval:

- **2.2.3:** non-scheduled BDU; paragraph (b) tests whether physical and technical attributes make central dispatch impracticable, with conditions possible under (c).
- **2.2.2(b2):** scheduled generating unit plus scheduled load where the BDU cannot transition linearly between consumption and production.
- **2.2.2(b4):** separately classified intermittent plant and BDU within a qualifying coupled production unit.
- **2.2.7(c1):** a coupled production unit may be classified as a semi-scheduled generating unit only under its specific conditions, including intermittent output, no grid consumption except auxiliary load, and the required data, energy conversion model and telemetry. **2.2.7(c3)** limits maximum generation to the intermittent component's maximum.

Two 3 MW BDUs sharing a common connection point meet the 6 MW aggregate scheduling test. Two independently connected 3 MW systems do not become one 6 MW BDU merely because one aggregator manages both. An ordinary grid-charging standalone BESS cannot choose semi-scheduled status to gain FCAS access.

**Sources:** [NER v254](https://energy-rules.aemc.gov.au/ner/818), clauses above; [AEMO registration guides](https://www.aemo.com.au/energy-systems/electricity/national-electricity-market-nem/participate-in-the-market/registration/registration-fact-sheets-and-guides), particularly the exemption/classification guide dated 3 June 2024, sections 1.2.2, 2-5, and the SRA and intermediary fact sheets. Current NER prevails over older summaries.

### What This Means for the Ordinary Scheduled Market BDU

- **Single registration** as **IRP** covers both generation (discharge) and consumption (charging)
- **No separate Market Customer registration needed** (IRP covers both directions)
- **Scheduled bidirectional unit** = must follow AEMO central dispatch instructions
- **Bid structure: 20 price bands** (10 for discharge, 10 for charging)

### Background: IESS Reform (3 June 2024)

The Integrating Energy Storage Systems (IESS) rule change effective **3 June 2024** created the **IRP** category specifically for storage and hybrid systems. Pre-IESS, batteries had to register under both Generator and Customer categories.

---

## 2. Connection Process — NER Chapter 5

### Determine the Applicable Connection Process

There is no blanket MW boundary between Chapters 5 and 5A. **NER 5.1.2(d), 5.3.1A and 5A.A.2** turn on the applicant, plant, network and applicable exclusions or elections:

| Situation | Relevant route |
|-----------|----------------|
| Registered or intending-to-register applicant connecting an integrated resource system to a distribution network | Chapter 5, normally rule 5.3A under 5.3.1A, subject to its exceptions |
| Applicant seeking a system registration exemption, without eligibility for an automatic exemption | Also covered by 5.3.1A(c)(2); seeking exemption does not itself move the project to Chapter 5A |
| Eligible non-registered DER provider connecting to distribution | Chapter 5A may apply; a qualifying applicant without a standard connection service can elect rule 5.3A under 5A.A.2(c)-(d) |
| Large inverter based resource | 5A.A.2(a1) excludes Chapter 5A except Part E; see 5.3.1A(c)(4). The Chapter 10 definition refers to AEMO's system strength impact assessment guidelines, not a general 5 MW cutoff |
| Transmission connection | Chapter 5, normally rule 5.3, with the applicable declared-network/access qualifications |

Chapter 5A has retail-customer agency and regulated-SAPS qualifications in **5A.A.2(a)**; **5A.A.3** deems an SRA the agent of its SRA customers. **5.3.1A(d)** can preserve applicable Schedule 5.2/5.3 technical requirements even on a Chapter 5A route. A registered standalone 5 MW battery connecting to a DNSP is therefore normally a Chapter 5 project. FCAS participation alone does not determine the connection chapter; provider eligibility and ASU approval are separate under **2.1A.5 and 2.3D.1**.

**Source:** [NER v254](https://energy-rules.aemc.gov.au/ner/818), 5.1.2(d), 5.3.1A, 5A.A.2-5A.A.3 and Chapter 10.

### Chapter 5 Connection Stages

```
1. Connection Enquiry
   ├── Submit to TNSP/DNSP (the connecting Network Service Provider)
   └── Response requirements depend on rule 5.3 or 5.3A and enquiry completeness

2. Connection Application                                [Most demanding stage]
   ├── Detailed technical information
   ├── Proposed Generator Performance Standards (GPS)
   ├── Power system studies (load flow, fault level, stability)
   ├── R1 model package (PSS®E + PSCAD/EMTDC)
   └── TNSP response with connection offer

3. Connection Agreement
   ├── Negotiation of access standards (GPS)
   ├── Network augmentation requirements
   ├── Connection charges and cost allocation
   └── Execution of connection agreement

4. AEMO IRP Registration                                 [Separate approval process]
   ├── Apply via Application Guide for Generator/IRP
   ├── Required plant data/models; wind/solar forecasting ECM only where applicable
   ├── SCADA specifications
   └── Credit support arrangements (MCL — bank guarantee)

5. Construction & Detailed Design

6. Commissioning & Registration
   ├── R2 commissioning tests (AEMO witnessed)
   ├── GPS compliance testing
   └── Active in central dispatch
```

See [[../Large-Scale-Generation/Grid-Requirements]] for full GPS (S5.2.5) requirements and modelling specifications.

---

## 3. Required Qualifications & Compliance

### Mandatory Registrations

| Item | Authority | Why |
|------|-----------|-----|
| **AEMO IRP Registration / applicable exemption** | AEMO | Apply the person/system tests in 2.1A.1-2.1A.2 and any 2.9.3 intermediary arrangement |
| **Applicable connection agreement** | Connecting TNSP/DNSP, with AEMO's applicable role | Normally Chapter 5 for this registered standalone project; confirm section 2 applicability |
| **State electrical licence/safety compliance** | State regulator (NSW: SafeWork NSW; VIC: WorkSafe VIC; etc.) | Operational safety |
| **State environmental approval** | State EPA / planning authority | Per state planning legislation |

### Optional but Often Required

| Item | When |
|------|------|
| **FCAS Classification** | If providing Frequency Control Ancillary Services (additional revenue stream) |
| **EPBC Act referral** | If project triggers Matters of National Environmental Significance (MNES) |

### NOT Required for Wholesale-Only Battery

- ❌ **AER Retailer Authorisation** — only needed if selling to small end-customers
- ❌ **State Retail Licence** — same reason
- ❌ **Embedded Network Manager** — only for embedded networks

---

## 4. Application Documents Checklist (CA Stage)

Per [AEMO Connection Application Checklist](https://www.aemo.com.au/-/media/files/electricity/nem/network_connections/stage-3/connection-application-checklist.pdf):

| # | Document | NER Reference |
|---|----------|---------------|
| 1 | Project description (single-line diagram, equipment specs) | 5.3.4(b) |
| 2 | Proposed GPS Template (Automatic / Negotiated access per S5.2.5) | 5.3.4(c) |
| 3 | GPS Compliance Studies | 5.3.4A |
| 4 | **R1 Model Package** (PSS®E + PSCAD models with source code) | S5.2.4 |
| 5 | Schedule 5.5 design and setting data sheets | S5.5.6 |
| 6 | Schedule 5.4 plant technical data | S5.4 |
| 7 | System Strength Impact Assessment | 5.3.4B |
| 8 | Protection Coordination Study | 5.3.4(d) |
| 9 | Power Quality Study | S5.2.5.2 |
| 10 | Commissioning Program | 5.3.4(e) |
| 11 | Project & Construction Program | 5.3.4(f) |

For modelling details, see [[../Large-Scale-Generation/Grid-Requirements#R1 Power System Modelling Requirements]].

---

## 5. Historical AEMO Application & Registration Fees (FY26)

> **Historical period: 1 July 2025 to 30 June 2026.** Retained FY26 figures are not current quotes. FY27 applies from 1 July 2026; see [section 5A](#5a-sa--sapn-distributed-connection-and-fcas-fee-schedule-2026-27) for final FY27 AEMO amounts and the separate SA/SAPN example.

### FY26 Interim IRP Fee Treatment

The FY26 budget stated that, pending consultation on specific IRP fees, IRP applicants incurred the fees relevant to the unit or role being registered. The Scheduled Market Generator amount below was the historical comparison for an ordinary scheduled battery; AEMO confirmed the applicable category for each application. That interim treatment must not be presented as the current FY27 tariff.

**Table 43 — NEM Registration Fees FY26 (1 July 2025 – 30 June 2026), AUD ex GST:**

| Registration Type | FY25 | **FY26** | Variance |
|------------------|------|---------|----------|
| **Scheduled Market Generator** (historical comparator) | $41,800 | **$46,000** | +10% |
| Semi-scheduled Market Generator | $54,850 | $61,750 | +13% |
| Non-scheduled Market Generator | $40,100 | $42,100 | +5% |
| Market Customer | $13,250 | $13,950 | +5% |

> **Note**: AEMO confirms with each applicant which fee category applies upon receipt of application.

### Optional Additional Fees

| Service | FY26 Fee (AUD ex GST) |
|---------|---------------------|
| FCAS classification (additional to Generator fee) | **$14,300** |
| Disbursement charge — additional ECM (semi-scheduled) | $6,400 |
| Disbursement charge — additional ECM (non-scheduled) | $3,250 |
| Wholesale demand response unit classification | $13,300 |
| Transfer of registration | $30,650 |

**Source:** [AEMO Final Budget and Fees FY26 (PDF)](https://www.aemo.com.au/-/media/files/about_aemo/energy_market_budget_and_fees/2025/aemo-final-budget-and-fees-fy26.pdf), Table 43.

### AEMO Connection Assessment Charge-Out Rates (FY26)

Connection assessment fees charged on **time-and-materials basis** (not fixed fee):

**Table 40 — AEMO Connection Charge-Out Rates FY26:**

| Role | Rate (AUD/hour, ex GST) |
|------|------------------------|
| Analyst/Engineer | **$345** |
| Senior | **$375** |
| Principal | **$420** |
| Manager/Specialist | **$480** |
| Third-party labour | Cost + 15% |
| **Connections Reform Initiative (CRI) uplift** (additional) | **$30/hour** |

> Effective rate including CRI uplift: $375–$510/hour depending on role.

**Source:** [AEMO Connection and Registration Fees Fact Sheet FY26 (PDF)](https://www.aemo.com.au/-/media/files/about_aemo/energy_market_budget_and_fees/2025/connection-and-registration-fees-fact-sheet.pdf), Table 1.

### Retained FY26 Planning Scenario (Unverified Estimates)

The following ranges have no identified project quotation or reproducible scope in this page. They are retained as historical planning assumptions, not published tariffs, validated typical costs or a current project budget. Only the separately sourced FY26 fee items are official amounts.

| Cost Item | Estimated Range (AUD) |
|-----------|---------------------|
| AEMO registration fee (Scheduled Bidirectional Unit) | $46,000 |
| FCAS classification (if pursuing FCAS) | $14,300 |
| AEMO connection assessment (charge-out, ~200-400 hours) | $80,000 – $200,000 |
| TNSP/DNSP connection enquiry & assessment | $50,000 – $200,000 |
| **Total AEMO/TNSP fees** | **$190,000 – $460,000** |

### Retained Third-Party Estimates (Outside AEMO; Unverified)

| Cost Item | Estimated Range (AUD) |
|-----------|---------------------|
| Power system modelling (PSS®E + PSCAD) consultants | $200,000 – $800,000 |
| Legal counsel (CA + Connection Agreement negotiation) | $50,000 – $200,000 |
| Engineering design and protection studies | $100,000 – $300,000 |
| Bank guarantee establishment (1-2% of MCL annually) | $5,000 – $50,000/year |
| **Subtotal third-party** | **$355,000 – $1,300,000+** |

---

## 5A. SA / SAPN Distributed Connection and FCAS Fee Schedule, 2026-27

> The **AEMO fee table applies across the NEM**. The separate SAPN example applies only to an approximately **5.5 MW BESS in South Australia connected through SAPN**. Its Manual 18 figures are retained from the earlier page and have not been independently rechecked in this scoped review. Amounts below are stated excluding GST; confirm the applicable invoice and project scope.

### Principal Findings

- The reviewed AEMO Table 47 charges for **ASU classification**, not an all-inclusive FCAS testing service. The project may also incur SAPN charges and owner-procured commissioning and advisory costs.
- The earlier SAPN example assumed **5.5 MW corresponds to about 5.5 MVA**. Confirm the actual equipment rating, applicable fee band and quoted services with SAPN; a MW registration threshold does not establish a DNSP MVA fee band.
- Registration, FCAS classification, network connection and owner-procured commissioning are distinct scopes. Their total cannot be inferred from MW size alone.

### AEMO Charges, FY27, Excluding GST

| Item | Charge |
|------|--------|
| Scheduled Market BDU registration, fixed baseline | **$48,150 per registration** |
| IRP (Market Connection Point) registration | $14,600; a separate application type, not an automatic BDU add-on |
| IRP-SRA registration | $23,950; requires the eligible SRA role |
| Classification of plant as an ancillary service unit (ASU) | **$15,000**, where that additional classification is sought; not an FCAS testing tariff |
| New ancillary services / ASU classification in a new region | $15,000; apply the precise Table 47 scope and footnote C |
| Amendment of an existing ASU classification / aggregation of existing classified plant | $6,400 / $2,850 respectively; not a generic R1/L1 engineering fee |
| Additional ECM for semi-scheduled / non-scheduled market generator | $7,050 / $3,600 respectively; not a standard standalone BDU fee |
| Connection assessment / site visits, Table 44 | $360 / $385 / $435 / $500 per hour by role; $30/hour CRI uplift on applicable Onboarding and Connections charges; site travel and third-party terms also apply |

**6 MW versus 55 MW:** if each application has the same Scheduled Market BDU registration scope, each fixed baseline is **A$48,150 ex GST** (A$52,965 including 10% GST), a **A$0 fixed-fee difference**. Table 47 is per registration, not per MW. Multiple registrations or other application types require their own assessment.

The baseline is not a total connection cost or cap. From **1 July 2026**, additional BDU/IRP registration assessment exceeding the fixed-fee threshold attracts **time-and-materials (T&M)** charges. AEMO notifies applicants near 70%, 95% and 100% of the threshold; at 95% the applicant can advise that it does not wish to proceed. Additional work is invoiced monthly in arrears after the threshold is reached. The threshold measures assessment effort covered by the fee, not battery capacity. Applicable charge-out rates depend on the work: **Table 46 general rates and Table 44 connection rates are distinct**; do not apply the CRI uplift to every registration activity automatically.

**Current primary sources:** [AEMO final FY27 Budget and Fees](https://www.aemo.com.au/-/media/files/about_aemo/energy_market_budget_and_fees/2026/aemo-final-budget-and-fees-fy27.pdf?rev=6b35a59f8cfc49b58dd02205fc0770e0&sc_lang=en), published 19 June 2026, p. 2 for the net-of-GST basis and Tables 44, 46 and 47 on printed pp. 74, 76-77; [Market Registration - Invoice Fact Sheet](https://www.aemo.com.au/-/media/files/electricity/nem/participant_information/registration/2026/market-registration-invoice-fact-sheet.pdf?rev=4906ebba9fe545e595ae2b260aaa8a22&sc_lang=en), listed 3 July 2026, pp. 1-2. FY26's $46,000 and $14,300 remain historical only.

### SAPN Charges, Manual 18 2026/27, Excluding GST

| Code | Item | Charge |
|------|------|--------|
| ACS263 | Indicative estimate for BESS or hybrid system | $5,150 |
| ACS267 | Engineering report for BESS above 1.5 MVA and below 5 MVA | $13,340 |
| ACS268 | Revised engineering report above 500 kVA | $3,120 |
| ACS269 / **ACS270** | Connection offer: below 5 MVA **$4,240**; above 5 MVA **$47,320**, the relevant published band for the assumed 5.5 MVA case | Not separately stated |
| ACS260 | SCADA enabling system; confirm applicability with SAPN | $22,240 |
| ACS272 / ACS273 | Additional commissioning witness visit: Metro **$1,310**; Country **$2,070** | Per visit |
| Appendix D | AER-approved hourly rates: Senior Engineer $232 per hour; Engineer $203 per hour; overtime approximately 1.7 times standard rate | Time-based |

### Owner and Adviser Costs

- **FCAS/R2 testing execution** may include inverter and BMS controller testing, compliance advisers, and measurement meeting the applicable MASS service requirements. The inherited range of tens of thousands to hundreds of thousands of dollars has no identified quotation or source here. It is an unverified scenario, not a public tariff or validated estimate.

### Indicative Combined Position

An applicable AEMO ASU classification adds $15,000 to the relevant registration scope. The earlier SAPN example also lists $1,310-$2,070 per additional witness visit, $47,320 for its assumed connection-offer band and $22,240 for SCADA. Their applicability and combination need a project quote. No validated total, minimum spend before an FCAS application, or ranking of cost drivers is established by these figures.

**Sources:** [SAPN Manual 18, 2026/27](https://www.sapowernetworks.com.au/public/download.jsp?id=337829); AEMO FY27 Budget & Fees, Table 47 for registration fees and Table 44 for connection charge-out rates.

---

## 6. Timeline (5 MW Standalone Battery)

| Phase | Duration | Notes |
|-------|----------|-------|
| **1. Connection Enquiry → Preliminary Response** | 20 business days | TNSP/DNSP statutory response time |
| **2. Connection Application Preparation** | 6–12 months | Build R1 model package (PSS®E + PSCAD), GPS proposal |
| **3. CA Submission → Connection Offer** | 6–12 months | Includes AEMO/TNSP review, possible iterations |
| **4. Connection Agreement Negotiation** | 1–3 months | GPS negotiation, network augmentation |
| **5. AEMO IRP Registration** | 15 business days from complete application | Parallel to connection process |
| **6. Detailed Design & Construction** | 6–12 months | Battery installation, protection, SCADA |
| **7. R2 Commissioning Tests** | 1–3 months | AEMO witnessed, GPS compliance verification |
| **TOTAL** | **18–36 months** | Typical end-to-end |

**Reference:** Per AEMC, Chapter 5 connection agreement is typically reachable within 100 business days of CA submission, **excluding** applicant's preparation time (which is typically the longest part).

---

## 7. Discharge Revenue Settlement Mechanism

### How a Scheduled Bidirectional Battery Earns Revenue

| Revenue Stream | Mechanism | Notes |
|---------------|-----------|-------|
| **Energy Arbitrage** | Bid into NEM spot market via 20 price bands (10 generation, 10 consumption) | 5-min dispatch, weekly settlement |
| **FCAS** (10 markets: 8 contingency, 2 regulation) | Additional ASU classification and service capability required | See [[FCAS-Ancillary]] and [AEMO settlements guide, section 2](https://www.aemo.com.au/-/media/files/electricity/nem/data/ancillary_services/2025/settlements-guide-to-ancillary-services-and-frequency-performance-payments.pdf?rev=e7c4fb3fc63347fca83cd07fa283f9c0&sc_lang=en) |
| **Capacity Investment Scheme (CIS)** | Federal underwriting for new RE+storage capacity | Optional, separate process |

### Settlement Process (Standard NEM)

- **Dispatch interval:** 5 minutes
- **Trading interval:** 5 minutes (post 1 Oct 2021 reform)
- **Settlement timing:** Weekly billing; final statements normally within **7 business days** after billing-period end. Payment is due on the later of the **9th business day** after period-end or **2 business days after receipt of the final statement** (NER 3.15.15(a), Chapter 10 `payment date`).
- **2026 transition:** NER 11.179.4(b) replaces the normal final-statement deadline with **7-18 business days** during the transition covering billing weeks **33-42**. As at **13 September 2026**, use the relevant week in [AEMO's settlement calendar](https://www.aemo.com.au/energy-systems/electricity/national-electricity-market-nem/market-operations/settlements-and-payments/prudentials-and-payments/settlement-calendars), not an assumed 9-day payment date; see [NER v254](https://energy-rules.aemc.gov.au/ner/818), 11.179.1-11.179.4.
- **Pricing:** Regional Reference Price (RRP) per dispatch interval × dispatched MW
- **Prudential:** Maximum Credit Limit (MCL) determined by AEMO; bank guarantee required

See [[Settlement-Prudential]] for detailed settlement framework.

### Discharge Settlement Example

For a 5 MW battery dispatching 5 MW for 1 hour at $200/MWh:
- Dispatched energy: 5 MW × 1 h = 5 MWh
- Revenue: 5 MWh × $200 = $1,000 (gross)
- Less: Network charges, market fees, FCAS levies (if applicable)

---

## 8. Charging Settlement (Consumption Side)

The IRP is responsible for consumption at the connection point. Charging energy is treated as load:
- **Charge cost:** RRP × MWh charged
- **Network charges:** May apply depending on TNSP/DNSP tariff (some states have specific BESS charging tariffs)
- **No separate Market Customer registration required** — IRP covers both directions

---

## 9. Key Risk Factors & Mitigation

| Risk | Mitigation |
|------|-----------|
| **Connection queue delays** | Engage TNSP early; use experienced CA consultants; consider co-locating in REZ (Renewable Energy Zone) |
| **GPS compliance failure** | High-quality R1 model package; engage AEMO-experienced modelling consultants |
| **MCL volatility** | Maintain 20% buffer above MCL in bank guarantee |
| **Negative spreads / arbitrage compression** | Diversify into FCAS markets; consider CIS underwriting |
| **System strength remediation costs** | Assess SCR at proposed connection point early |

---

## 10. Step-by-Step Application Checklist

### Phase A: Pre-Application (Months 1–3)

- [ ] Site selection and land control
- [ ] Preliminary grid connection assessment with TNSP/DNSP
- [ ] Engage AEMO-experienced engineering consultants
- [ ] Establish Australian corporate entity
- [ ] Initial financial model and capital plan

### Phase B: Connection Enquiry (Months 3–4)

- [ ] Submit Connection Enquiry to relevant TNSP/DNSP
- [ ] Receive preliminary response (20 business days)
- [ ] System strength and hosting capacity assessment

### Phase C: Connection Application (Months 4–16)

- [ ] OEM battery model procurement (PSS®E + PSCAD from manufacturer)
- [ ] Plant-level model integration
- [ ] GPS compliance simulations (S5.2.5.1 – 5.2.5.11)
- [ ] R1 Model Package compilation
- [ ] CA submission to TNSP and AEMO
- [ ] Iterate with AEMO/TNSP feedback
- [ ] Receive Connection Offer

### Phase D: AEMO Registration (Parallel, Months 12–18)

- [ ] Complete Application Guide for Generator/IRP
- [ ] Submit applicable plant data/models; forecasting ECM only for relevant wind/solar plant
- [ ] SCADA specifications
- [ ] Bank guarantee (Pro Forma) for MCL
- [ ] Confirm and pay FY27 Scheduled Market BDU baseline (A$48,150 ex GST for that application type), applicable additional classifications and any threshold-based T&M
- [ ] AEMO determination within 15 business days

### Phase E: Construction & Commissioning (Months 18–30)

- [ ] Detailed design and protection coordination
- [ ] Construction
- [ ] R2 commissioning tests (AEMO witnessed)
- [ ] GPS compliance verification

### Phase F: Operations (Month 30+)

- [ ] Active in NEM central dispatch (5-minute)
- [ ] Bid via 20 price bands (10 gen, 10 consumption)
- [ ] Weekly settlement
- [ ] Optional: FCAS market participation (after FCAS classification)

---

## 11. Official AEMO Resources

### Battery & IRP Registration

| Document | URL | Local File |
|----------|-----|-----------|
| **Battery Systems Fact Sheet (June 2024)** | [Fact Sheet](https://www.aemo.com.au/-/media/files/electricity/nem/participant_information/registration/2024/registration-fact-sheet-nem-battery-systems.pdf) | [[official-documents/market-core-documents/AEMO-Battery-Systems-Fact-Sheet-2024.pdf]] |
| **IRP Registration Page** | [Register as IRP](https://www.aemo.com.au/energy-systems/electricity/national-electricity-market-nem/participate-in-the-market/registration/register-as-an-irp-in-the-nem) | — |
| **Application Guide for Generator/IRP** | [Generator/IRP Guide](https://www.aemo.com.au/-/media/files/electricity/nem/participant_information/registration/2024/Application-Guide-NEM-Generator-or-IRP) | — |
| **IESS Final Transition Plan (Jan 2024)** | [IESS Plan](https://www.aemo.com.au/-/media/files/initiatives/integrating-energy-storage-systems-project/iess-final-integrated-resource-provider-transition-plan.pdf) | [[official-documents/market-core-documents/AEMO-IESS-IRP-Transition-Plan.pdf]] |

### Fees & Charges

| Document | URL | Local File |
|----------|-----|-----------|
| **AEMO Final Budget and Fees FY27** | [Final FY27, Tables 44/46/47](https://www.aemo.com.au/-/media/files/about_aemo/energy_market_budget_and_fees/2026/aemo-final-budget-and-fees-fy27.pdf?rev=6b35a59f8cfc49b58dd02205fc0770e0&sc_lang=en) | Not linked here |
| **Market Registration - Invoice Fact Sheet, July 2026** | [BDU/IRP assessment T&M](https://www.aemo.com.au/-/media/files/electricity/nem/participant_information/registration/2026/market-registration-invoice-fact-sheet.pdf?rev=4906ebba9fe545e595ae2b260aaa8a22&sc_lang=en) | Not linked here |
| **AEMO Final Budget and Fees FY26** | [FY26 Budget and Fees PDF](https://www.aemo.com.au/-/media/files/about_aemo/energy_market_budget_and_fees/2025/aemo-final-budget-and-fees-fy26.pdf) | [[official-documents/market-core-documents/AEMO-FY26-Budget-and-Fees.pdf]] |
| **Application and Registration Fees Fact Sheet FY26** | [FY26 Fees Fact Sheet PDF](https://www.aemo.com.au/-/media/files/about_aemo/energy_market_budget_and_fees/2025/connection-and-registration-fees-fact-sheet.pdf) | [[official-documents/market-core-documents/AEMO-FY26-Connection-Registration-Fees.pdf]] |
| **NEM Participant Fee Structure Review** | [Fee Structure Review](https://www.aemo.com.au/consultations/current-and-closed-consultations/national-electricity-market-participant-fee-structure-review) | — |

### Connection Process

| Document | URL | Local File |
|----------|-----|-----------|
| **Connection Application Checklist** | [CA Checklist](https://www.aemo.com.au/-/media/files/electricity/nem/network_connections/stage-3/connection-application-checklist.pdf) | [[official-documents/market-core-documents/AEMO-Connection-Application-Checklist.pdf]] |
| **R1 Submission Checklist** | [R1 Checklist](https://aemo.com.au/-/media/files/electricity/nem/network_connections/stage-6/generator-connection-r1-submission-checklist.pdf) | — |
| **Power System Model Guidelines v3.0** | [PSMG v3.0](https://aemo.com.au/-/media/files/stakeholder_consultation/consultations/nem-consultations/2025/psmg-and-data-sheets-consultation/final-documents/psmg-2025-final-report.pdf) | [[official-documents/market-core-documents/AEMO-PSMG-2025-Final-Report.pdf]] |

---

## 12. Contact for Enquiries

| Purpose | Contact |
|---------|---------|
| **General registrations** | onboarding@aemo.com.au |
| **Connections (excl. Victoria)** | Contact.Connections@aemo.com.au |
| **AEMO Support Hub** | supporthub@aemo.com.au / 1300 236 600 |
| **Phone (international)** | +61 3 9609 8000 |

---

## Related in This Tier
- [[Market-Participants-Licensing]]
- [[Settlement-Prudential]]
- [[Aggregator-Roles]]
- [[NEM-Overview]]
- [[FCAS-Ancillary]]
- [[../Large-Scale-Generation/Grid-Requirements|Grid Requirements (CA + Modelling)]]
