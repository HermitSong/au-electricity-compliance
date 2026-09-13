---
country: Australia
type: market-structure
category: licensing
last_updated: 2026-04-04
status: draft
sources:
  - https://www.aemo.com.au/energy-systems/electricity/national-electricity-market-nem/participate-in-the-market/registration
  - https://www.aemo.com.au/learn/market-participants/electricity-market-participants
  - https://www.aemo.com.au/consultations/current-and-closed-consultations/registration-information-resource-and-guidelines
  - https://www.aemo.com.au/-/media/files/electricity/nem/participant_information/registration/2024/Application-Guide-NEM-General-Application-Forms
  - https://www.aemo.com.au/-/media/files/electricity/nem/participant_information/registration/2024/Application-Guide-NEM-Generator-or-IRP
  - https://www.aemo.com.au/-/media/files/initiatives/integrating-energy-storage-systems-project/iess-final-integrated-resource-provider-transition-plan.pdf
tags: [australia, market-structure, licensing, registration, aemo, participant-categories]
---

> **Nav**: [[../_AU-Overview|Australia]] > **Market Structure** > **Market Participants & Licensing**

# Australia NEM — Market Participant Registration & Licensing

Comprehensive guide to all participant categories, registration pathways, and licensing requirements in Australia's National Electricity Market (NEM).

> **Scope:** AEMO NEM registration under NER Chapter 2 is distinct from retail authorisation. AER retailer authorisation applies only in the NECF jurisdictions: NSW, QLD, SA, TAS and ACT. Victoria remains in the NEM but uses ESC retail licensing. WA/WEM and NT require separate market and licensing analysis.

## Two-Layer Regulatory Framework

| Layer | Regulator | Authority | Scope |
|-------|-----------|-----------|-------|
| **Market Operations** | [[../Regulatory-Bodies\|AEMO]] | NER Chapter 2 | Registration as market participant; technical/financial obligations |
| **Retail Sales to End Customers in NECF Jurisdictions** | [[../Regulatory-Bodies\|AER]] | NERL/NERR and application legislation | Retailer authorisation and consumer protection in NSW, QLD, SA, TAS and ACT |
| **Separate or retained jurisdictional functions** | ESC (VIC), ERA (WA), Utilities Commission (NT), ICRC (ACT) | Applicable state or territory Acts | Victorian retail licensing; WA and NT market or retail licensing; retained ACT price regulation |

> A participant that trades in the NEM and sells electricity to small customers in an NECF jurisdiction may require **both** AEMO registration and AER retailer authorisation. Many wholesale-only generators, service providers and aggregators do not require retail authorisation merely because they are NEM participants. Victoria, WA and NT use different retail entry pathways.

---

## 1. AEMO Registration Categories (NER Chapter 2)

### 1.1 Generator

Three classifications based on size and dispatchability:

| Classification | Threshold | Examples |
|---------------|-----------|----------|
| **Scheduled Generator** | ≥30 MW dispatchable | Coal, gas, hydro plants |
| **Semi-Scheduled Generator** | ≥30 MW intermittent | Wind farms, solar farms |
| **Non-Scheduled Generator** | <5 MW or exempt | Embedded generation, rooftop solar |
| **Scheduled Bidirectional Unit** | ≥5 MW battery (mandatory) | Battery storage systems (registered as IRP) — see [[Battery-5MW-Registration-Pathway]] |

> **Correction (April 2026):** Per [AEMO Battery Systems Fact Sheet (June 2024)](https://www.aemo.com.au/-/media/files/electricity/nem/participant_information/registration/2024/registration-fact-sheet-nem-battery-systems.pdf), a battery ≥5 MW is classified as a **scheduled bidirectional unit** (mandatory), not semi-scheduled. Batteries <5 MW are classified as "small resources" eligible for SRA/IRP/Market Customer options.

**Application Documents Required:**
- Generator Classification and Registration form
- Energy Conversion Model (ECM) per AEMO ECM Guidelines
- SCADA data specifications (per AWEFS/ASEFS Guide)
- Bid/offer validation data (Schedule 3.1, NER) — submit ≥6 weeks before market entry
- Connection Agreement (from NSP — see [[../Large-Scale-Generation/Grid-Requirements]])
- Signed AEMO Guarantee Pro Forma (credit support)

**Timeline:** 15 business days from complete application (registration); but NER Chapter 5 connection process: 12-36 months total.

### 1.2 Market Customer

Purchases electricity from spot market (retailers, large industrial users, businesses buying directly).

**Application Documents:**
- Application Form for Customer Registration
- Application Guide for Registration as a Customer in the NEM
- Technical specifications per NER Schedule 5.3
- Evidence of technical/financial capacity
- Signed AEMO Guarantee Pro Forma (if required)

**Submission:** onboarding@aemo.com.au

### 1.3 Integrated Resource Provider (IRP) — NEW June 2024

**Most important new category for storage and aggregators.**

Created via the **Integrating Energy Storage Systems (IESS) rule change** (effective 3 June 2024). Single registration category for:
- Battery Energy Storage Systems (BESS)
- Hybrid systems (generation + storage)
- Small Resource Aggregators (SRA, formerly MSGA)
- Aggregators of mixed resources

**Registration Path:**
- Application Guide for Registration as Generator or IRP (2024)
- IRP Registration Fact Sheet
- Energy Conversion Model (ECM) — if applicable
- SCADA requirements (for scheduled/semi-scheduled resources)
- Credit support at MCL level

**Auto-Transition:** All MSGA participants registered on 2 June 2024 automatically became SRA on 3 June 2024 — no new application required.

### 1.4 Small Resource Aggregator (SRA)

Sub-category within IRP for aggregating small resources (<30 MW each):
- Residential/community batteries
- Small solar with storage
- Controllable loads
- Mixed resource portfolios

**Key Capability:** SRA can now participate in market ancillary services and access expanded value streams (compared to old MSGA which had narrower scope).

### 1.5 Network Service Provider (NSP)

| Type | Coverage |
|------|----------|
| **TNSP** (Transmission NSP) | Transgrid (NSW), AusNet (VIC), Powerlink (QLD), ElectraNet (SA), TasNetworks (TAS) |
| **DNSP** (Distribution NSP) | State-specific distribution operators |
| **MNSP** (Market Network Service Provider) | Interconnectors that participate in spot market trading |

**Special Requirement:** TNSPs/DNSPs must develop Local Black System Procedures (LBSP) per AEMO guidelines.

### 1.6 Demand Response Service Provider (DRSP)

Two sub-classifications:

| Sub-category | Purpose | Key Requirement |
|-------------|---------|----------------|
| **ASU** (Ancillary Service Unit) | FCAS provision only | MASS compliance; no WDR documents |
| **WDRU** (Wholesale Demand Response Unit) | WDR mechanism participation | 5-minute metering; baseline methodology; Maximum Responsive Component |

**Documents Required for WDRU:**
- Baseline methodology per AEMO WDR Guidelines
- Maximum Responsive Component specification
- Aggregation and telemetry documentation
- Five-minute metering evidence
- Dispatch conformance capability

### 1.7 Trader & Reallocator

| Role | Definition | Key Eligibility |
|------|-----------|----------------|
| **Trader** | Participates in Settlement Residue Auctions only | Must be "wholesale client" per Corporations Act 2001 s.761G(4) |
| **Reallocator** | Bilateral trades with AEMO consent | Wholesale client + Austraclear membership (5 weeks processing) |

### 1.8 Special Participant Exemptions

Three exemption pathways under NER Chapter 2:

1. **System Characteristics Exemption** — based on size/type (response: 5 business days)
2. **Intermediary Registration Exemption** — intermediary entity registers instead
3. **Temporary Notifiable Exemption** — for pre-commissioning testing

---

## 2. AER Retailer Authorisation (NERL Jurisdictions)

**Applies to:** NSW, QLD, SA, TAS, ACT (jurisdictions adopting NERL)
**Does NOT apply to:** VIC (ESC), WA (ERA), NT (Utilities Commission)

### 2.1 Three Entry Criteria (Must Pass All)

| Criterion | What AER Assesses |
|-----------|-------------------|
| **Organisational & Technical Capacity** | Experienced management team, business procedures, IT systems, customer service capability, hardship policy ability |
| **Financial Capacity & Viability** | 3-year financial projections, working capital adequacy, funding commitments, financial sustainability |
| **Suitability (Fit & Proper)** | Director/officer character, no disqualifying convictions, no insolvency history, compliance track record |

### 2.2 Application Documents Checklist

**Core Forms:**
- Retailer Authorisation Application Form
- Application Checklist (signed)
- Declaration Template (statutory declaration)

**Organisational/Technical Evidence:**
- Business plan (3-5 year forward-looking)
- Organisational chart and staffing plan
- Retail management system documentation
- Billing and customer service procedures
- Complaint handling procedures
- IT system capabilities (metering, settlement, CRM)
- **Hardship policy (draft)** — subject to AER approval
- Retail contract template
- Consumer protection procedures

**Financial Evidence:**
- 3-year P&L projections (monthly Y1, quarterly Y2-3)
- Cash flow projections (monthly detail)
- Balance sheet projections
- Funding commitments / facility agreements
- Sensitivity analysis
- Working capital requirements analysis

**Director & Officer Information:**
- Personal details + CVs of all directors, company secretary, senior executives
- Statutory character declarations
- National Police Clearance
- Bankruptcy/insolvency history disclosure
- Professional references

### 2.3 Application Process & Timeline

```
1. Initial Submission                           [Day 0]
   └── Email to aerauthorisations@aer.gov.au

2. Completeness Review                          [Week 2-4]
   └── AER may request clarifications

3. Detailed Assessment                          [Week 4-10]
   ├── Three-criteria evaluation
   ├── Possible meetings with applicant
   └── Financial projection scrutiny

4. Public Consultation                          [Week 10-14]
   └── 4-week public submission period

5. Final Determination                          [Week 14-20]
   ├── Approve (with/without conditions), OR
   └── Refuse

6. Conditional Compliance (if applicable)       [+3 months max]
   └── Strict deadline; non-compliance = deemed refusal
```

**Minimum:** 12 weeks from complete application
**Typical:** 6-12 months end-to-end
**Submission email:** aerauthorisations@aer.gov.au

### 2.4 Ongoing Compliance Obligations

After authorisation, retailers must comply with:
- **National Energy Retail Rules (NERR)**
- **Default Market Offer (DMO)** — max price for standing offers (NSW, SE QLD, SA)
- **Retailer Reliability Obligation (RRO)** — when AEMO declares reliability gap
- **Hardship Policy** — AER-approved, mandatory for residential customers
- Annual compliance reporting to AER

---

## 3. AER Retail Exempt Selling (Embedded Networks)

**Applies to:** Apartments, shopping centres, caravan parks, retirement villages, industrial parks, etc.

### 3.1 Three Exemption Categories

| Category | Application Required | Use Case |
|----------|---------------------|----------|
| **Deemed (Auto-Exempt)** | No (CLOSED for new networks since v7 Aug 2025) | Existing grandfathered networks |
| **Negotiated** | Yes | Networks not meeting deemed criteria |
| **Approved** | Yes | Specific arrangements with AER conditions |

### 3.2 Critical Change (v7, August 2025)

Deemed exemptions are **CLOSED** to new embedded networks. All new networks must register through Negotiated or Approved pathways. Existing networks grandfathered but subject to increased oversight.

---

## 4. Embedded Network Manager (ENM)

### 4.1 When Required

ENM is **mandatory** when a small customer in an embedded network accepts a market retail offer. Must be appointed once cooling-off period expires (5 business days).

### 4.2 AEMO ENM Accreditation

**Application Documents:**
- ENM Accreditation application form
- Service delivery capability statement
- Technical specs for metering and settlement systems
- Financial viability evidence
- Business continuity / disaster recovery plans
- Customer service procedures
- MSATS (Market Settlement and Transfer Solutions) system capability

### 4.3 Ongoing Obligations

- Register NMI (National Metering Identifier) for each customer
- Register Child NMIs in MSATS
- Maintain NMI Standing Data
- Assign Distribution Loss Factors (DLF)
- Comply with ENM Service Level Procedure
- Coordinate with Metering Provider and Metering Coordinator

---

## 5. Metering Roles

| Role | Purpose | Registration |
|------|---------|--------------|
| **Metering Coordinator (MC)** | Selects MP, data provider, aggregator; coordinates metering | AEMO registration; typically appointed by retailer |
| **Metering Provider (MP)** | Installs, maintains, repairs meters | AEMO accreditation per Schedule 7.4 NER |

### Metering Type Classification (Type 1-7)

| Type | Description | Application |
|------|-------------|-------------|
| Type 1 | Whole current meter + on-site SCADA | Large industrial, generators |
| Type 2 | Whole current meter, no SCADA | Medium commercial/industrial |
| Type 3 | CT/VT meter + on-site SCADA | Large industrial |
| Type 4 | CT/VT meter, no SCADA | Medium commercial/industrial |
| Type 5 | Telecommunications-connected meter | Small commercial, some residential |
| Type 6 | Manual-read meter | Small commercial, residential |
| Type 7 | Calculated metering (no physical meter) | Unmetered loads, small embedded gen |

---

## 6. State-Level Retail Licensing (Non-NERL States)

### Victoria (ESC)

- **Authority:** Essential Services Commission
- **Framework:** Victorian Energy Retail Code of Practice (NOT NERL)
- **Timeline:** 8-10 weeks once complete
- **Recent Change (July 2024):** Wholesale-only sales no longer require retail licence (s.16(1) amendment)
- **Submit to:** [ESC Apply for Licence](https://www.esc.vic.gov.au/electricity-and-gas/licences-exemptions-and-trial-waivers/electricity-and-gas-licences/apply-electricity-or-gas-licence)

### Western Australia (ERA)

- **Authority:** Economic Regulation Authority
- **Market:** Separate WEM (NOT NEM) — South West Interconnected System only
- **Customer Classes:**
  - Non-contestable: <50 MWh/year (Synergy regulated)
  - Contestable: 50-160 MWh/year
  - Large: >160 MWh/year
- **Financial Assessment Cost:** ~$5,000

### Northern Territory (Utilities Commission)

- **Authority:** NT Utilities Commission
- **Framework:** Electricity Reform Act 2000 (NOT NERL)
- **Status:** Full retail contestability available
- **Compliance:** Electricity Retail Supply Code

### ACT (ICRC)

- **Authority:** Independent Competition and Regulatory Commission
- **Status:** ICRC NO LONGER licenses retailers — uses national AER authorisation
- **ICRC Retains:** Standing offer price regulation (ActewAGL only)
- **Apply to:** AER (national process)

---

## 7. Aggregator Business Models — Registration Quick Reference

| Business Model | AEMO Registration | Key Requirements |
|---------------|-------------------|-----------------|
| **Virtual Power Plant (VPP)** | DRSP (FCAS) + IRP/SRA (energy) | Aggregation control, telemetry, BESS Guide compliance |
| **Demand Response (Industrial)** | DRSP (WDRU) | 5-min metering, baseline methodology, Max Responsive Component |
| **Battery Aggregator (small)** | SRA under IRP | Aggregation control system, FCAS testing |
| **Battery Aggregator (≥5MW)** | IRP (Generator classification) | Full ECM, SCADA, NER Chapter 5 connection |
| **Hybrid Solar+Storage** | IRP (single registration) | Combined ECM covering both technologies |
| **Negawatt/Demand Response (FCAS)** | DRSP (ASU) | MASS compliance, control capability |

See [[Aggregator-Roles]] for detailed business model analysis.

---

## 8. Settlement & Prudential Framework Summary

### Settlement Cycle

| Element | NEM position; scoped correction checked 13 September 2026 |
|---------|---------------------------------------------------------|
| Billing period | Weekly; not a nine-day billing period |
| Final statement | Normally within 7 business days; between 7 and 18 under the SSC transition in NER 11.179 |
| Payment date | Later of the ninth business day and two business days after receipt of the final statement; consult the relevant transitional billing-week calendar |
| Revision | Applicable revision schedule and intervention/transition exceptions; no unconditional 20-day guarantee |
| Prudential collateral | Participant-specific AEMO calculation; do not infer a guaranteed reduction |

### Prudential Requirements

- **Maximum Credit Limit (MCL):** AEMO-determined per participant
- **Credit Support:** Bank guarantee ≥ MCL (AEMO Guarantee Pro Forma — single template for NEM/STTM/WEM/GSH)
- **Prudential Standard:** AEMO targets 2% prudential standard (extreme conditions)
- **Reassessment Triggers:** Price spikes >$300/MWh, credit rating changes, material operational changes

See [[Settlement-Prudential]] for detailed framework.

---

## 9. Practical Pathways — Common Scenarios

### Scenario A: Build 100 MW Solar Farm and Sell into NEM

**Required Registrations:**
1. NER Chapter 5 Connection Agreement (12-15 months) — see [[../Large-Scale-Generation/Grid-Requirements]]
2. AEMO Generator Registration as **Semi-Scheduled Generator** (15 business days)
3. Bank Guarantee for MCL (1-2% of expected annual revenue)

**Total Timeline:** 18-24 months from connection enquiry to market operation
**Estimated Setup Cost:** $500K-$5M+ (network charges) + $5K-$20K (registration) + $20K-$100K/year (ongoing)

### Scenario B: Aggregate 500 MW of Residential Batteries into VPP for FCAS

**Required Registrations:**
1. **DRSP for FCAS (ASU)** OR **SRA under IRP** (15 business days each)
2. AEMO BESS Guide compliance testing (2-4 months)
3. MarketNet API connection
4. Bank Guarantee $50K-$500K

**Total Timeline:** 6-12 months
**Revenue Potential:** ~$13M/year illustrative (500 MW × 30% util × $50/MWh — actuals highly variable)

### Scenario C: Retail Electricity to Small Business Customers

**Required Registrations:**
1. AEMO **Market Customer** registration (1-2 months)
2. **AER Retailer Authorisation** (12-24 weeks)
3. State-specific licensing (if VIC/WA/NT)

**Total Timeline:** 12-18 months end-to-end
**Estimated Setup Cost:** $20K-$100K (legal/consulting) + $50K-$200K (billing systems) + $10K-$50K/year (ongoing)

### Scenario D: Operate Embedded Network in Apartment Complex

**Required Registrations:**
1. **AEMO ENM Accreditation** (3-6 months) OR
2. **AER Exempt Selling Registration** (4-8 weeks; deemed exemptions CLOSED for new networks since Aug 2025)

**Estimated Cost:** $5K-$20K (accreditation) + $1K-$3K per apartment (metering) + $20K-$50K (systems)

### Scenario E: Provide Wholesale Demand Response to Industrial Customers

**Required Registrations:**
1. **DRSP (WDRU)** registration (3-4 months including testing)
2. Customer contracts with industrial sites (≥1 MW aggregate)
3. 5-minute metering at customer sites
4. Bank Guarantee $50K-$500K

**Total Timeline:** 6-12 months
**Revenue Potential:** ~$4.4M/year illustrative (10 MW × 50% util × $100/MWh)

---

## 10. AEMO Contact Information

| Purpose | Contact |
|---------|---------|
| General registrations | onboarding@aemo.com.au |
| Phone (AU) | 1300 858 724 |
| Phone (international) | +61 3 9609 8000 |
| Network connections | Via AEMO website |
| MCL inquiries | AEMO Prudential Dashboard or onboarding email |

---

## 11. Key Compliance Documents

### AEMO Mandatory References

| Document | Purpose | URL |
|----------|---------|-----|
| **Registration Information Resource & Guidelines (RIRG)** | Master suite of registration materials | [AEMO RIRG](https://www.aemo.com.au/consultations/current-and-closed-consultations/registration-information-resource-and-guidelines) |
| **General Application Guide 2024** | Overview of all NEM application forms | [General Guide](https://www.aemo.com.au/-/media/files/electricity/nem/participant_information/registration/2024/Application-Guide-NEM-General-Application-Forms) |
| **Generator/IRP Application Guide** | Detailed Generator and IRP guide | [Gen/IRP Guide](https://www.aemo.com.au/-/media/files/electricity/nem/participant_information/registration/2024/Application-Guide-NEM-Generator-or-IRP) |
| **IRP Registration Fact Sheet** | Quick reference for IRP | [IRP Fact Sheet](https://www.aemo.com.au/-/media/files/electricity/nem/participant_information/registration/2024/Registration-Fact-Sheet-NEM-Integrated-Resource-Provider) |
| **Battery Systems Fact Sheet** | Battery-specific registration | [Battery Fact Sheet](https://www.aemo.com.au/-/media/files/electricity/nem/participant_information/registration/2024/registration-fact-sheet-nem-battery-systems.pdf) |
| **IESS Final Transition Plan** | IRP transition for storage | [IESS Plan](https://www.aemo.com.au/-/media/files/initiatives/integrating-energy-storage-systems-project/iess-final-integrated-resource-provider-transition-plan.pdf) |
| **DRSP Registration Page** | Demand Response Service Provider info | [DRSP Page](https://www.aemo.com.au/energy-systems/electricity/national-electricity-market-nem/participate-in-the-market/registration/register-as-a-drsp) |
| **MCL Calculator** | Maximum Credit Limit estimation | [MCL Calculator](https://aemo.com.au/en/energy-systems/electricity/national-electricity-market-nem/market-operations/settlements-and-payments/prudentials-and-payments/maximum-credit-limit/maximum-credit-limit-calculator) |

### AER Mandatory References

| Document | Purpose | URL |
|----------|---------|-----|
| **Retailer Authorisation Guideline v3 (July 2024)** | Main retail authorisation guidance | [Retailer Auth Guideline](https://www.aer.gov.au/system/files/2024-07/AER%20-%20Retailer%20authorisation%20guideline%20-%20July%202024.pdf) |
| **Retail Exempt Selling Guideline v7 (Aug 2025)** | Embedded network exemptions | [Exempt Selling Guideline](https://www.aer.gov.au/industry/registers/resources/guidelines/retail-exempt-selling-guideline) |
| **Retail Authorisations Register** | List of authorised retailers | [Authorisations Register](https://www.aer.gov.au/industry/retail/authorisations) |
| **Wholesale Demand Response Guidelines** | WDRU/DRSP rules | [WDR Guidelines](https://www.aer.gov.au/wholesale-markets/guidelines-reviews/wholesale-demand-response-participation-guidelines) |

### State Regulators

| State | Regulator | URL |
|-------|-----------|-----|
| VIC | ESC | [ESC Licences](https://www.esc.vic.gov.au/electricity-and-gas/electricity-and-gas-licences-and-exemptions/electricity-and-gas-licences) |
| WA | ERA | [ERA WEM](https://www.erawa.com.au/electricity/wholesale-electricity-market) |
| NT | Utilities Commission | [NT Licensing](https://utilicom.nt.gov.au/electricity/licensing) |
| ACT | ICRC (price only) | [ICRC Energy](https://www.icrc.act.gov.au/energy/electricity) |

---

## Related in This Tier
- [[NEM-Overview]]
- [[WEM-Overview]]
- [[FCAS-Ancillary]]
- [[Settlement-Prudential]]
- [[Retailer-Authorisation]]
- [[Aggregator-Roles]]
