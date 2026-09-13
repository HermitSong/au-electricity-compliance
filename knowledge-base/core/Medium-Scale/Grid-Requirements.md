---
country: Australia
tier: medium-scale
category: grid
last_updated: 2026-09-13
status: draft-researched
sources:
  - https://energy-rules.aemc.gov.au/ner/818
  - https://www.aemo.com.au/energy-systems/electricity/national-electricity-market-nem/participate-in-the-market/registration/registration-fact-sheets-and-guides
  - https://www.aemo.com.au/energy-systems/electricity/national-electricity-market-nem/participate-in-the-market/registration/register-as-an-irp-in-the-nem
tags:
  - australia
  - medium-scale
  - grid
  - NER
  - Chapter-5A
  - DNSP
  - export-limits
---

> **Nav**: [[00-Home/Dashboard|Dashboard]] > [[../_AU-Overview|Australia]] > **Medium-Scale** > **Grid Requirements**

# Grid Connection Requirements -- Medium-Scale Generation (5-30 MW)

> **NEM scope; source review 13 September 2026.** This page's 5-30 MW tier is an organisational label, not a registration or connection rule. The applicability and classification corrections below use NER v254, effective 4 September 2026. They do not apply to WA/WEM or NT arrangements. See source review (local-only artifact; not distributed) for verification limits.

## Determine the Applicable Connection Process

Distribution connection does **not** automatically mean Chapter 5A. NER **5.1.2(d)** and **5.3.1A** determine the Chapter 5 distribution pathway, while **5A.A.2** sets Chapter 5A's application, exclusions and elections. The applicant's status, plant type and connection circumstances matter; there is no blanket 5 MW or 30 MW boundary.

### Chapter 5A vs Chapter 5

| Situation | Applicable test / route |
|-----------|-------------------------|
| Registered or intending-to-register applicant connecting a generating or integrated resource system to a DNSP | Normally Chapter 5 rule 5.3A under 5.3.1A(b)-(c), subject to its exceptions |
| Applicant seeking a system registration exemption, ineligible for an automatic exemption | Included in 5.3.1A(c)(2); an exemption application does not itself establish Chapter 5A eligibility |
| Eligible non-registered DER provider seeking a distribution connection | Chapter 5A may apply under 5A.A.2(b); one without an applicable standard connection service can elect 5.3A under 5A.A.2(c)-(d) |
| Large inverter based resource | 5A.A.2(a1) excludes Chapter 5A except Part E; 5.3.1A(c)(4) applies. The Chapter 10 definition refers to classification under AEMO's system strength impact assessment guidelines |
| Transmission connection | Chapter 5, normally 5.3, subject to declared-network and access provisions |

Chapter 5A normally excludes Registered and Intending Participants, but **5A.A.2(a)** preserves retail-customer agency and regulated-SAPS exceptions. **5A.A.3** deems an SRA the agent of its SRA customers. A qualifying election under **5A.A.2(c)** is unavailable for a regulated SAPS and must meet the timing/writing requirements in (d).

The connecting NSP manages its connection process and agreement, with AEMO performing its prescribed assessments and approvals. **5.3.1A(d)** preserves Schedule 5.2/5.3 requirements to the extent applicable even on a Chapter 5A route. Neither chapter title nor registration exemption establishes a universal technical waiver, connection offer or completion time. Confirm applicable performance standards and studies with the NSP and AEMO.

**Counterexamples:** a registered standalone 6 MW BESS connected to distribution normally follows Chapter 5 and scheduled-BDU classification. A 10 MW generating system seeking an individual registration exemption is also within 5.3.1A(c)(2), despite being below 30 MW. Conversely, eligible small exempt DER may use Chapter 5A, including an SRA customer represented under 5A.A.3. In each case, check plant-specific exclusions and the actual connection arrangement.

**Source:** [NER v254](https://energy-rules.aemc.gov.au/ner/818), 5.1.2(d), 5.3.1A, 5A.A.2-5A.A.3 and Chapter 10; [AEMO exemption/classification guides](https://www.aemo.com.au/energy-systems/electricity/national-electricity-market-nem/participate-in-the-market/registration/registration-fact-sheets-and-guides).

### Chapter 5A Connection Process (Only Where Applicable)

```
1. Connection Enquiry to DNSP
   ├── Basic information: site, capacity, technology
   ├── Information response within 5 business days, or another agreed period (5A.D.2(a))
   └── Hosting capacity and network constraint information

2. Detailed Connection Application
   ├── Technical specifications of generation equipment
   ├── Single line diagram and protection coordination study
   ├── Power system studies (as required by DNSP)
   └── DNSP assessment and connection offer

3. Connection Offer Negotiation
   ├── Connection charges (augmentation, metering, protection)
   ├── Export limits (static or dynamic)
   ├── Technical requirements and access standards
   └── Execution of connection agreement

4. Construction and Commissioning
   ├── Installation per DNSP technical requirements
   ├── DNSP inspection and testing
   ├── Protection settings commissioning
   └── Energisation and export commissioning
```

## DNSP Connection Standards

Each DNSP publishes its own connection standards for embedded generators. Key DNSPs:

### Major DNSPs

| State | DNSP | Key Document |
|-------|------|-------------|
| NSW | Ausgrid, Endeavour Energy, Essential Energy | Embedded Generation Connection Guidelines |
| VIC | AusNet Services, CitiPower/Powercor, Jemena, United Energy | Embedded Generation Connection Guide |
| QLD | Energex, Ergon Energy (Energy Queensland) | Connection Standard for Embedded Generating Units |
| SA | SA Power Networks | Embedded Generation Technical Requirements |
| TAS | TasNetworks | Embedded Generator Connection Guide |

Western Power's WA connection rules are outside this NEM page and must be assessed separately.

### Common DNSP Technical Requirements

| Requirement | Project-specific basis |
|-------------|------------------------|
| Reactive capability / power factor | Applicable access standards, capability envelope and agreed performance standards |
| Voltage and power quality | NSP limits, relevant standards and site studies; no universal numerical allowance established here |
| Protection | Approved protection design and coordination, including applicable islanding, voltage and frequency protection |
| Communications / SCADA | Applicable dispatch, network and service requirements; not determined by a generic 1 MW rule |
| Fault ride-through | Applicable access and performance standards; registration exemption alone does not waive technical obligations |

## Export Limits

Export limits are a critical constraint for medium-scale embedded generators.

### Types of Export Limits

| Type | Description |
|------|-------------|
| Static Export Limit | Fixed MW cap on export; simplest to implement |
| Dynamic Export Limit | Variable limit based on real-time network conditions; enabled by SCADA |
| Zero Export | No export permitted; all generation consumed on-site |
| Time-of-Use Export | Different limits for peak/off-peak periods |

### Factors Determining Export Limits

1. **Network hosting capacity** -- Available thermal capacity on feeder and transformer
2. **Voltage rise** -- Export may cause voltage to exceed regulatory limits
3. **Fault level** -- Generator contribution to fault current at connection point
4. **Reverse power flow** -- Distribution network not designed for reverse flow at some locations
5. **Protection coordination** -- Impact on existing protection settings

### Legacy Export Scenarios by Connection Voltage (Unverified)

| Connection Voltage | Previously recorded illustrative range |
|-------------------|---------------------|
| 11 kV | 3-10 MW (feeder-dependent) |
| 22 kV | 5-15 MW |
| 33 kV | 10-30 MW |
| 66 kV | 15-50 MW |

These inherited ranges have no identified DNSP study or published entitlement behind them. They are not voltage-based export allowances or connection-design limits. Actual permitted import/export depends on the site studies and connection agreement.

## Demand Management and Network Support

Medium-scale generators can provide network support services:

| Service | Mechanism |
|---------|-----------|
| Peak demand reduction | Generation during peak periods reduces feeder loading |
| Voltage support | Reactive power injection/absorption per DNSP direction |
| Non-network alternative | DNSP may contract embedded generation as alternative to network augmentation |
| RERT (Reliability and Emergency Reserve Trader) | AEMO may contract medium-scale generators for emergency reserves |

## Registration and Unit Classification

Registration concerns the person and system; scheduled/non-scheduled status concerns the unit. An exemption is not a dispatch classification. Under **2.1A.1**, non-exempt generating systems require Generator or IRP registration, while non-exempt integrated resource systems require IRP registration. Apply **2.1A.2** and the AEMO exemption guide separately, including system aggregation and exemption conditions.

| Plant / status | Rule and default | Qualifications |
|----------------|------------------|----------------|
| Generating unit below 30 MW, outside a common-point group totalling at least 30 MW | Non-scheduled under 2.2.3(a) | AEMO-approved scheduled or semi-scheduled classification is possible under the applicable criteria; conditions may impose dispatch-related obligations |
| Generating unit at least 30 MW, or common-point group totalling at least 30 MW | Scheduled under 2.2.2(a); intermittent output engages 2.2.7(a) | Apply AEMO approval and the specified alternatives; exactly 30 MW meets the threshold |
| BDU at least 5 MW, or common-point BDU group totalling at least 5 MW | Scheduled BDU under 2.2.2(a1) | All four AEMO-approved alternatives remain: 2.2.3 non-scheduled; 2.2.2(b2) nonlinear plant as scheduled generation/load; (b4) separate coupled plant; 2.2.7(c1) qualifying coupled unit as semi-scheduled |
| Registered BDU below 5 MW and outside the relevant aggregate threshold | Normally non-scheduled BDU under 2.2.3(a1) | Scheduled classification requires AEMO approval; a small component in a larger system is not automatically exempt |
| Exempt system/person | 2.1A.2 and AEMO's guide | Standing exemption below 5 MW is conditional; larger-system individual exemptions and 2.9.3 intermediary exemptions are distinct routes |

**BESS is not governed by the 30 MW generating-unit threshold.** A 6 MW battery normally requires scheduled-BDU treatment even though it sits in this 5-30 MW tier. Two 3 MW BDUs sharing a common connection point also meet the 5 MW aggregate test. Nameplate rating in either production or consumption matters; an export cap below 5 MW does not itself remove that test.

**Semi-scheduled status is not chosen to unlock FCAS.** For a BDU, **2.2.7(c1)** is a specific coupled-production-unit exception requiring intermittent plant, no grid consumption except auxiliary load, and prescribed data/ECM/telemetry; **(c3)** limits maximum generation to the intermittent component. FCAS requires eligible provider and ASU classification under **2.1A.5 and 2.3D.1**, plus applicable MASS compliance. An ordinary standalone grid-charging BESS does not satisfy the coupled-unit exception merely by seeking FCAS.

An approved **2.9.3 intermediary exemption** changes who registers for the relevant system; it is not created by an optimiser contract and does not remove the unit's classification requirements. IRP-SRA participation under **2.2.8** instead depends on exempt small units and an eligible small resource connection point. See [[../Market-Structure/Aggregator-Roles]] for those boundaries.

**Fees:** the final FY27 Scheduled Market BDU fixed baseline is **A$48,150 ex GST per registration**, the same for comparable 6 MW and 55 MW applications. Additional assessment after the fixed-fee threshold can attract T&M; an applicable additional ASU classification is **A$15,000**. These are distinct from NSP connection charges and project studies. See [[../Market-Structure/Battery-5MW-Registration-Pathway]] for final fee-table and invoice-fact-sheet sources, and preserved FY26 history.

**Sources:** [NER v254](https://energy-rules.aemc.gov.au/ner/818), 2.1A.1-2.1A.5, 2.2.2, 2.2.3, 2.2.7, 2.2.8 and 2.9.3; [AEMO IRP registration](https://www.aemo.com.au/energy-systems/electricity/national-electricity-market-nem/participate-in-the-market/registration/register-as-an-irp-in-the-nem); [AEMO exemption/classification guide](https://www.aemo.com.au/-/media/files/stakeholder_consultation/consultations/nem-consultations/2022/guide-to-generator-exemption-and-classification-of-generating-units-consultation/final-documents/guide-to-registration-exemptions-and-production-unit-classification1.pdf?rev=f33f04ffbbd34ba19304ceeec93788a0&sc_lang=en), 3 June 2024, sections 1.2.2, 2-5. The current NER controls if older guidance differs.

See also: [[Engineering-Standards]], [[Market-Data]], [[../Large-Scale-Generation/Grid-Requirements]]

## Related in This Tier
- [[Engineering-Standards]]
- [[Industry-Insights]]
- [[Market-Data]]
- [[Safety-Compliance]]
