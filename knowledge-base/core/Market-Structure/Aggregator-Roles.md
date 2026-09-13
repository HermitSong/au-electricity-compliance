---
country: Australia
type: market-structure
category: aggregator
last_updated: 2026-09-13
status: draft
sources:
  - https://energy-rules.aemc.gov.au/ner/818
  - https://www.aemo.com.au/energy-systems/electricity/national-electricity-market-nem/participate-in-the-market/registration/register-as-a-small-generation-aggregator-sga-in-the-nem
  - https://www.aemo.com.au/energy-systems/electricity/national-electricity-market-nem/participate-in-the-market/registration/registration-fact-sheets-and-guides
  - https://www.aemo.com.au/initiatives/major-programs/nem-distributed-energy-resources-der-program/der-demonstrations/virtual-power-plant-vpp-demonstrations
  - https://www.aemo.com.au/-/media/files/initiatives/integrating-energy-storage-systems-project/iess-final-integrated-resource-provider-transition-plan.pdf
  - https://www.aer.gov.au/wholesale-markets/guidelines-reviews/wholesale-demand-response-participation-guidelines
  - https://www.aemo.com.au/initiatives/trials-and-initiatives/past-trials-and-initiatives/wholesale-demand-response-mechanism
tags: [australia, aggregator, vpp, drsp, irp-sra, wdrm, fcas]
---

> **Nav**: [[../_AU-Overview|Australia]] > **Market Structure** > **Aggregator Roles**

# Australian NEM — Aggregator Business Models

## Overview

Aggregators in the NEM combine distributed energy resources (DER) — batteries, solar, controllable loads, EVs — to deliver coordinated services into wholesale markets. The IESS (Integrating Energy Storage Systems) reform of June 2024 modernised the registration framework with the **Integrated Resource Provider (IRP)** category.

> **Scope:** The roles and registration pathways on this page are NEM-specific. They do not describe WEM participation in WA or NT market arrangements. A retail authorisation analysis is separate and depends on the customers, contracting model and jurisdiction.

> **Scoped source review: 13 September 2026.** Battery/aggregator roles and connection applicability were checked against NER v254, effective 4 September 2026, and current AEMO registration guidance. Legacy cost, revenue and delivery-time scenarios remain unvalidated. See source review (local-only artifact; not distributed).

**IRP, SRA and intermediary are different concepts.** IRP is the registration category for a non-exempt integrated resource system under **2.1A.1(b)**. An IRP acts as an SRA when it classifies eligible small resource connection points under **2.2.8**. A formal **2.9.3 intermediary exemption** instead allows an approved registered participant to stand in for a person otherwise required to register; a commercial aggregation or optimisation contract does not itself grant that exemption.

## Five Main Aggregator Business Models

### 1. Virtual Power Plant (VPP) Aggregator

**Resources Aggregated:**
- Rooftop solar (residential)
- Battery storage (home batteries, community batteries)
- EV charging infrastructure
- Smart controllable loads (HVAC, water heaters, pool pumps)
- Small backup generators

**AEMO Registration Path:**
- DRSP with eligible plant classified as ASU (FCAS), or qualifying loads classified as WDRU (wholesale demand response)
- IRP for non-exempt integrated resource systems and relevant market connection points
- IRP acting as SRA for eligible small resource connection points; this is not a separate registration category or a universal household-VPP route

**Value Streams:**
- FCAS: 10 NEM markets in total, comprising 8 contingency and 2 regulation services; access depends on the participant and plant approvals
- Energy market participation (≥1 MW aggregate bid)
- Peak demand management
- Network support services (DNSPs)
- Wholesale demand response (WDRU)

**Technical Requirements:**
- Aggregation control systems (SCADA, communications)
- Real-time monitoring and control
- Telemetry data to AEMO (5-minute intervals)
- Battery testing per AEMO BESS Guide v4.0 (June 2024)
- Communications protocols (MarketNet, APIs)
- Dispatch conformance measurement

**Market Performance (2024):**
- Small battery VPPs: ~3% FCAS market share (Contingency)
- Growing simultaneous energy + FCAS participation

### 2. Demand Response Service Provider (DRSP) — Industrial Demand

**Customer Profile:**
- Large retail customers (>100 kWh/day)
- Industrial loads with controllable demand
- Commercial premises with flexibility (cold storage, data centres)

**Sub-Classifications:**

| Type | Purpose | Documents Required |
|------|---------|-------------------|
| **ASU** (Ancillary Service Unit) | FCAS only | Capability statement, MASS compliance |
| **WDRU** (Wholesale Demand Response Unit) | WDR mechanism | Baseline methodology, Max Responsive Component, 5-min metering |

**WDRU Documentation Detail:**
- Baseline calculation methodology (e.g., 10-day preceding period, temperature-adjusted)
- Maximum Responsive Component per customer (max MW reduction)
- Aggregation and telemetry specs (5-min data, SCADA architecture)
- Dispatch conformance procedures (5-min calculation)
- Five-minute metering evidence (Type 1-4 typical)

### 3. Wholesale Demand Response Mechanism (WDRM)

**History:** Operational since 24 October 2021

**Key Features:**

| Feature | Detail |
|---------|--------|
| Dispatch interval | 5 minutes |
| Settlement | Weekly |
| Min capacity | 1 MW aggregate |
| Treatment | Demand reduction = generation equivalent |

**Eligibility:**
- ≥1 MW minimum aggregate capacity
- Controllable load with measurable baseline
- 5-minute metering capability
- Dispatch conformance capability

### 4. FCAS Aggregator

**Aggregated Resources:** Multiple small resources providing FCAS

**Registration Options:**

| Option | Best For |
|--------|---------|
| DRSP with classified ASU | Eligible plant providing the approved ancillary services |
| IRP acting as SRA | Eligible exempt small resources; ancillary-service classification is an additional approval |
| IRP for an integrated resource system | Battery/hybrid system with the applicable BDU and ASU classifications |

**FCAS access is separate from energy dispatch classification.** NER **2.1A.5** requires an Ancillary Service Provider and classified ASU; **2.3D.1** sets the plant eligibility and approval requirements. An ordinary standalone battery cannot elect semi-scheduled status simply to access FCAS. AEMO's SRA fact sheet describes contingency FCAS access, not regulation FCAS access, for IRP-SRAs; service capability must meet the current MASS.

**Min Bid Size:** 1 MW for Contingency FCAS

**Technical Requirements:**
- BESS compliance per AEMO BESS Guide v4.0 (June 2024)
- Fast frequency response capability (sub-second for fast services)
- Dispatch conformance measurement
- Real-time telemetry to AEMO

**FCAS Markets (10 total):**

| Service pair | Market count | Service timeframe |
|--------------|--------------|-------------------|
| Very fast raise / lower | 2 | Within 1 second |
| Fast raise / lower | 2 | Within 6 seconds |
| Slow raise / lower | 2 | Within 60 seconds |
| Delayed raise / lower | 2 | Within 5 minutes |
| Regulation raise / lower | 2 | Ongoing frequency correction |

These are service categories, not a complete testing or sustain specification. Source: [AEMO Settlements Guide to Ancillary Services and Frequency Performance Payments](https://www.aemo.com.au/-/media/files/electricity/nem/data/ancillary_services/2025/settlements-guide-to-ancillary-services-and-frequency-performance-payments.pdf?rev=e7c4fb3fc63347fca83cd07fa283f9c0&sc_lang=en), 2 December 2025, section 2, p. 6; apply the current MASS to the service being registered.

### 5. Battery Aggregator (Post-2024 IESS Reforms)

**Context:** AEMO reforms (3 June 2024) via IESS rule change modernised battery registration.

**Battery Registration and Classification Tests:**

| Configuration | Registration / role | Unit and connection treatment |
|---------------|---------------------|-------------------------------|
| BDU at least 5 MW, or BDUs with combined nameplate rating at least 5 MW at a common connection point | Normally IRP for the integrated resource system; assess each liable person and any approved exemption | Scheduled BDU under 2.2.2(a1), subject to its four AEMO-approved alternatives; normally Chapter 5 for the registered project |
| Standalone system below 5 MW satisfying all standing-exemption conditions | Exempt owner/controller/operator; settlement through an appropriate Market Participant or eligible IRP-SRA arrangement | Exemption and market-connection conditions still apply; direct participation requires registration |
| Battery below 5 MW within a larger hybrid/system | Assess the whole system and common-point BDU aggregate | Neither exemption nor SRA eligibility follows from the battery component's rating alone |
| Mixed BESS and solar/wind | IRP can cover the integrated resource system | Classify each relevant unit or qualifying coupled plant under its own rule; ECM is required where applicable to intermittent plant, not automatically for every battery |
| FCAS-only commercial service | DRSP or another eligible registered Ancillary Service Provider, with classified ASU | Does not waive an owner's/controller's/operator's underlying IRP registration or exemption requirements |

The **2.2.2(a1)(1)-(4)** alternatives are non-scheduled BDU under **2.2.3**, scheduled generation plus scheduled load under **2.2.2(b2)** for nonlinear transitions, separately classified coupled plant under **(b4)**, and a qualifying coupled unit classified semi-scheduled under **2.2.7(c1)**. The last requires intermittent plant and no grid consumption except auxiliary load, together with the prescribed data, ECM and telemetry; **2.2.7(c3)** limits maximum generation to the intermittent component. It is not the ordinary standalone BESS route.

### SRA Eligibility and Intermediary Boundaries

The small-unit definitions require both size and exemption: a small BDU is below **5 MW** and part of an exempt system; a small generating unit is below **30 MW** and part of an exempt system. The 30 MW generator definition is not a battery exemption threshold. At an eligible small resource connection point, supply is limited to the small BDU and relevant auxiliary load; it cannot also supply an ordinary retail-customer load. A separately metered embedded-network arrangement needs its own eligibility assessment.

For example, a portfolio of separate exempt 3 MW systems may qualify for SRA participation. Two 3 MW BDUs at one common connection point trigger the 6 MW aggregate scheduling test if registration/classification applies. Calling that site a portfolio does not establish an exemption.

Under **2.9.3(a)-(d)**, an intermediary arrangement needs the exemption application, the intermediary's written consent, approval and relevant registration. **2.9.3(d)(5)** provides joint and several liability for the specified intermediary acts and omissions. Identify who actually owns, controls and operates the plant; a services contract cannot by itself transfer those statutory duties.

**Sources:** [NER v254](https://energy-rules.aemc.gov.au/ner/818), 2.1A.1-2.1A.5, 2.2.2-2.2.8, 2.9.3 and Chapter 10; [AEMO SRA fact sheet](https://www.aemo.com.au/-/media/files/electricity/nem/participant_information/registration/2024/registration-fact-sheet-nem-small-resource-aggregators.pdf?rev=9c22a4866eb04ecc9b47d634ecdcf83b&sc_lang=en), pp. 1-3; [AEMO intermediary fact sheet](https://www.aemo.com.au/-/media/files/electricity/nem/participant_information/registration/2024/registration-fact-sheet-nem-exemption-based-on-appointment-of-an-intermediary.pdf?rev=d33fceade1614d6ca76a538c8cbc2f84&sc_lang=en), June 2024. Current Rules prevail over the older fact-sheet summaries.

**Key Reform Benefits:**
- Single IRP registration for hybrid systems (vs. multiple categories pre-2024)
- SRA can now access market ancillary services (expanded scope)
- Streamlined registration reducing paperwork

## Comparison Matrix

| Business Model | AEMO Registration | Capacity / eligibility basis | Potential markets subject to approval | Unverified legacy cost scenario |
|---------------|-------------------|-------------|-------------|------------|
| Residential VPP (FCAS) | DRSP/IRP with classified ASU; SRA only for eligible connection points | Service and site eligibility | Contingency FCAS where approved | $200K-$2M |
| Industrial WDR | DRSP (WDRU) | 1 MW agg | WDR mechanism | $100K-$1M |
| Battery Aggregator (small) | IRP acting as SRA | Exempt systems and eligible small resource connection points | Energy and approved contingency FCAS | $50K-$500K |
| Battery Project (≥5 MW) | IRP, normally Scheduled Market BDU | 5 MW individual/common-point BDU aggregate test | Energy and separately approved FCAS | $5M-$50M+ |
| Hybrid Solar+Storage | IRP | Unit characteristics and system configuration | Energy and separately approved services | $20M-$200M |

These inherited cost ranges have no identified source or common scope: some may include asset construction and others business setup. They are not AEMO tariffs or comparable validated budgets. Final FY27 registration fees are role-based: Scheduled Market BDU **A$48,150 ex GST**, IRP-SRA **A$23,950**, with **A$15,000** for an applicable additional plant-ASU classification. Additional BDU/IRP assessment can attract T&M after the fixed-fee threshold. See [[Battery-5MW-Registration-Pathway]] for the final Table 47 and invoice fact sheet; an ordinary 6 MW and 55 MW application with identical Scheduled Market BDU scope has the same fixed baseline.

## Registration Process for Aggregators

### Step 1: Determine Registration and Classification

1. Identify the actual owners, controllers and operators, units, connection points, nameplate ratings in both directions and intended market activities.
2. Apply the IRP registration obligation and exemption tests to each system/person; document any standing exemption or approved 2.9.3 intermediary arrangement.
3. For non-exempt batteries, test 5 MW individually and across BDUs at a common connection point, then apply 2.2.2(a1) and any approved alternative. For SRA participation, verify the small-unit and connection-point definitions separately.
4. Determine the connection process under 5.3.1A and 5A.A.2. Chapter 5 covers distribution as well as transmission; neither 5 MW nor 30 MW is a universal Chapter 5A cutoff.
5. Apply separately for eligible FCAS/ASU or DRSP/WDRU activities. A preferred revenue stream does not determine the underlying BDU classification.

### Step 2: Prepare Documentation

**For IRP Registration:**
- Application Guide for Registration as Generator or IRP (2024)
- IRP Registration Fact Sheet
- Energy Conversion Model (if applicable)
- SCADA requirements per AEMO specification
- Credit support arrangements (MCL)

**For DRSP Registration:**
- DRSP Registration application form
- ASU or WDRU classification choice
- Baseline methodology (WDRU only)
- Aggregation and telemetry documentation
- Five-minute metering evidence (WDRU)

### Step 3: AEMO Testing & Verification

**For battery/FCAS aggregators:**
- BESS Guide compliance testing (2-4 months)
- Fast frequency response verification
- Evidence meeting applicable dispatch conformance requirements
- Aggregation control system validation

### Step 4: MarketNet API Connection

- Real-time SCADA data flow to AEMO
- 5-minute telemetry submission
- Dispatch instruction reception
- Settlement data integration

### Step 5: Market Participation

- Begin bidding into chosen markets
- Real-time dispatch participation
- Weekly settlement
- Ongoing compliance reporting

## Government & Regulatory References

### Key Documents

| Document | Purpose | URL |
|----------|---------|-----|
| **AEMO BESS Guide to Contingency FCAS Registration** | Battery FCAS testing | [BESS Guide](https://www.aemo.com.au/energy-systems/electricity/national-electricity-market-nem/system-operations/ancillary-services/market-ancillary-services-specification-and-fcas-verification-tool) |
| **IESS Final Transition Plan** | IRP transition for storage | [IESS Plan](https://www.aemo.com.au/-/media/files/initiatives/integrating-energy-storage-systems-project/iess-final-integrated-resource-provider-transition-plan.pdf) |
| **AEMO VPP Demonstrations** | VPP program info | [VPP Page](https://www.aemo.com.au/initiatives/major-programs/nem-distributed-energy-resources-der-program/der-demonstrations/virtual-power-plant-vpp-demonstrations) |
| **AER WDR Participation Guidelines** | WDRU/DRSP rules | [WDR Guidelines](https://www.aer.gov.au/wholesale-markets/guidelines-reviews/wholesale-demand-response-participation-guidelines) |
| **DRSP Registration Page** | DRSP application info | [DRSP Page](https://www.aemo.com.au/energy-systems/electricity/national-electricity-market-nem/participate-in-the-market/registration/register-as-a-drsp) |
| **MASS Specification v8.0** | FCAS technical requirements | [MASS PDF](https://www.aemo.com.au/-/media/files/electricity/nem/security_and_reliability/ancillary_services/market-ancillary-service-specification---v80.pdf) |
| **Battery Systems Fact Sheet 2024** | Battery registration | [Battery Fact Sheet](https://www.aemo.com.au/-/media/files/electricity/nem/participant_information/registration/2024/registration-fact-sheet-nem-battery-systems.pdf) |

## Practical Revenue Estimates

| Business Model | Annual Revenue (Indicative) | Notes |
|---------------|---------------------------|-------|
| 500 MW Residential VPP (FCAS) | ~$13M | 30% utilisation × $50/MWh average |
| 10 MW Industrial WDR | ~$4.4M | 50% utilisation × $100/MWh average |
| 50 MW Battery Aggregator | $5-15M | Stacked: energy + FCAS + capacity |
| 100 MW Standalone Battery | $10-30M | Variable by region and market conditions |

> All estimates illustrative; actuals highly dependent on market conditions, location, and operational efficiency.

## Related in This Tier
- [[Market-Participants-Licensing]]
- [[Settlement-Prudential]]
- [[Retailer-Authorisation]]
- [[FCAS-Ancillary]]
- [[NEM-Overview]]
