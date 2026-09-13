---
country: Australia
type: market-structure
category: settlement
last_updated: 2026-08-20
status: verified
sources:
  - https://www.aemc.gov.au/rule-changes/shortening-settlement-cycle
  - https://aemo.com.au/en/energy-systems/electricity/national-electricity-market-nem/market-operations/settlements-and-payments/prudentials-and-payments/maximum-credit-limit
  - https://www.aemo.com.au/initiatives/major-programs/nem-reform-program/nem-reform-program-initiatives/shortening-the-settlement-cycle
  - https://energy-rules.aemc.gov.au/ner/175/23916
tags: [australia, market-structure, settlement, prudential, mcl, credit-support, SSC, shortening-settlement-cycle, ERC0384]
---

> **Nav**: [[../_AU-Overview|Australia]] > **Market Structure** > **Settlement & Prudential**

# NEM Settlement & Prudential Framework

> **Jurisdiction boundary:** This page concerns NEM settlement and prudential obligations under NER Chapter 3. The WEM has separate WA market procedures, and NT systems are outside this framework. A WEM prudential procedure is not authority for a NEM Maximum Credit Limit conclusion.

## Settlement Cycle

### Legacy Position Before SSC Reform

- **Cycle:** Weekly settlement
- **Settlement statements:** AEMO issues weekly statements to participants
- **Clearing house:** AEMO operates clearing function for spot market and reallocation transactions
- **Payment mechanism:** Via Austraclear (electronic funds transfer)

### Shortening the Settlement Cycle (SSC) — the "9-day" reform ✅ verified

**What it is:** the AEMC **Shortening the Settlement Cycle** rule change (ref **ERC0384**) — *National Electricity Amendment (Shortening the settlement cycle) Rule 2024 No. 22*. Requested by GloBird Energy (6 Dec 2023); AEMC made a "more preferable" final rule on **12 December 2024**. It amends the NEM settlement/billing calendar in **NER Chapter 3**. It is **NOT** 5-minute settlement and **NOT** a standalone prudential rule — the prudential saving is a *consequence* of the shorter cycle.

**Scoped correction, 13 September 2026:** a statement, a payment and a billing period are different things. Under NER v254 clause 3.15.15, the normal final-statement deadline is **7 business days** after billing-period end. Chapter 10 defines **payment date** as the later of the **9th business day** after billing-period end and **2 business days after receipt of the final statement**. The billing period remains weekly. Do not call nine days the initial-statement deadline.

**Transition warning:** NER clause 11.179 applies to the transition beginning 9 August 2026 and ending immediately before the defined end date of 17 October 2026 (billing weeks 33-42). Clause 11.179.4(b) permits final statements between **7 and 18 business days** after the relevant billing period. Use AEMO's transitional settlement calendar for the particular billing week; the ordinary nine-day shorthand does not determine an actual September payment date. A payment relating to a transitional billing period can occur after the transition period. Intervention billing periods also have express revised-statement exceptions.

| Element | Pre-SSC | Post-SSC |
|---------|---------|----------|
| Billing period | Weekly (7 days) | Weekly (7 days) — unchanged |
| Final statement | Historical schedule | Normally within **7 business days**; **7-18** during the clause 11.179 transition |
| Payment date | Historical schedule | Later of the **9th business day** and **2 business days after final-statement receipt**; apply the transitional calendar |
| Routine revised statement | Historical schedule | Check the applicable revision rule and intervention/transition exceptions; not an unconditional 20-day guarantee |
| Prudential collateral (MCL) | Higher (longer exposure window) | **Lower** — shorter outstandings period ⇒ smaller TOSL ⇒ lower MCL |

**Effective dates (confirmed live — AEMO Settlement Communication No. 698, 9 Aug 2026):** Schedule 2 commenced 19 Dec 2024; **Schedule 1 went LIVE on 9 August 2026 = start of billing week 33** (AEMC determination and AEMO both confirm **week 33**). The cycle **progressively shortens from 20 → 9 business days across billing weeks 33 → 42 (ending 17 Oct 2026)** — it is *not* a step change. Preliminary statement now published on the **3rd business day** after the billing week.

⚠️ **Two settlement payments fall in the same week** during transition — **billing week 39** (Mon 21 Sep pay wk35 + Fri 25 Sep pay wk36) and **billing week 43** (Mon 19 Oct pay wk40 + Fri 23 Oct pay wk41) — treasury/cash-flow watch-point. Late payment = default event under **NER 3.15.21(a)(1)**.

*Reference docs: [AEMO 2026 NEM Settlement Calendar](https://www.aemo.com.au/energy-systems/electricity/national-electricity-market-nem/market-operations/settlements-and-payments/prudentials-and-payments/settlement-calendars) · [AEMO SSC Transition Plan](https://www.aemo.com.au/-/media/files/initiatives/shortening-the-settlement-cycle/transition-plan/ssc_settlement_transition_plan.pdf) · [SSC Participant Readiness Fact Sheet](https://www.aemo.com.au/-/media/files/initiatives/shortening-the-settlement-cycle/ssc-industry-readiness-fact-sheet.pdf).*

**Controlling text for the scoped correction:** [NER v254](https://energy-rules.aemc.gov.au/ner/818), clauses 3.15.15-3.15.18, Chapter 10 `payment date`, and clause 11.179. This corrects the statement/payment distinction only; other prudential figures on this page require their own current-source checks. The September 2026 clause binding does not certify any enterprise cash-flow schedule.

**Beneficiaries:** chiefly retailers (net buyers) — less working capital tied up in AEMO credit support; lower barrier to entry for small retailers.

**Reference:** [AEMC SSC rule (ERC0384)](https://www.aemc.gov.au/rule-changes/shortening-settlement-cycle) · [AEMO SSC program](https://www.aemo.com.au/initiatives/major-programs/nem-reform-program/nem-reform-program-initiatives/shortening-the-settlement-cycle)

---

## Settlement Components

| Component | Description |
|-----------|-------------|
| **Energy market settlement** | 5-minute spot prices, settled weekly per region |
| **Reallocation settlement** | Bilateral trades with AEMO consent |
| **Ancillary services settlement** | FCAS (10 markets, incl. 1-second Very Fast R1/L1 since Oct 2023), system strength, network services |
| **Network charges** | Transmission and distribution use of system charges |
| **Other costs** | Connection charges, market fees |

---

## Prudential Requirements — how AEMO calculates it (NER Ch.3 r.3.3) ✅ verified

Governing law: **NER Chapter 3, Rule 3.3 (Prudential Requirements)** + **AEMO Credit Limit Procedures**. Every Market Participant must lodge credit support ≥ its **Maximum Credit Limit (MCL)**.

### The core formula

```
MCL  = Outstandings Limit (OSL)  +  Prudential Margin (PM)
Trading Limit = MCL − PM   (≈ the Outstandings Limit)
```

| Term | Meaning |
|------|---------|
| **Outstandings** | Running tally of a participant's accrued market liabilities (unbilled + billed-unpaid, net of payments/reallocations) |
| **Outstandings Limit (OSL)** | AEMO's estimate of the max value Outstandings can reach over the **payment/outstandings period** (length = **TOSL**, in days) |
| **Prudential Margin (PM)** | Extra buffer above the Trading Limit to cover Outstandings accruing during the **Reaction Period** under a high-price scenario |
| **Reaction Period** | **7 days** — the window from Outstandings breaching the Trading Limit to trading suspension, giving AEMO time to act |
| **Trading Limit** | MCL − PM; when Outstandings exceed it, AEMO issues a **margin call (call notice)** |

### How the level is set

- **Prudential standard = 2% "probability of exceedance"** — MCL is set so a participant's Outstandings should exceed it **no more than 2% of the time**.
- **MCL calculator inputs:** participant load / generation / reallocations; latest **average regional prices**; **regional volatility factors** (percentiles calibrated to the 2% standard); SAPS settlement prices; the **Outstandings Limit time period (TOSL)**; and the reaction period — **set per season (summer / winter / shoulder)**.

### What SSC (the "9-day" reform) changes — exact day-counts (AEMC ERC0384 final determination)

The shorter cycle **shrinks the outstandings window (OSL/TOSL) ⇒ lower OSL ⇒ lower MCL** ⇒ **less credit support**. The **MCL = OSL + PM structure is unchanged**; only the OSL day-count shrinks (PM/reaction period stays 7 days).

| Component (days) | Pre-SSC | Post-SSC (from 9 Aug 2026) |
|------------------|---------|----------------------------|
| **Outstandings Limit period (OSL/TOSL)** | **35 days** (7-day billing + 28-day / 20-business-day settlement) | **19 days** (7-day billing + ~12-day / 9-business-day settlement) |
| **Prudential Margin (PM) = reaction period** | 7 days | 7 days (unchanged) |
| **= Total collateralised MCL window** | **42 days (~6 weeks)** | **26 days (~3.7 weeks)** |

> AEMC verbatim: *"the current OSL time period is 35 days … reduce the calculation of the OSL from 35 days to 19 days … the PM is seven days."* **Day-counts are structural, NOT seasonal** — seasonality (summer/autumn/winter/spring) only affects the **$ inputs** (average prices, volatility factors), not the number of days. AEMO's **Credit Limit Procedures updated effective 9 Aug 2026**. New cadence: preliminary statement day 3, final day 7, **payment day 9**, routine revision (R0) day 20 (business days).
> Source: [AEMC ERC0384 Final Determination (12 Dec 2024) p.12](https://www.aemc.gov.au/sites/default/files/2024-12/Shortening%20the%20settlement%20cycle%20-%20ERC0384%20-%20Final%20determination_final.pdf).

### Monitoring & escalation

```
Outstandings > Trading Limit  → AEMO issues margin call (call notice)
   → participant must top up credit support / pay within the reaction period (7 days)
Outstandings approach MCL      → Prudential Margin is being consumed
Outstandings exceed MCL        → trading suspension
```

**MCL Calculator:** [AEMO MCL Calculator](https://aemo.com.au/en/energy-systems/electricity/national-electricity-market-nem/market-operations/settlements-and-payments/prudentials-and-payments/maximum-credit-limit/maximum-credit-limit-calculator)

---

## Credit Support Instruments

### Bank Guarantee Pro Forma

- **Standard AEMO template** (single template for NEM, STTM, WEM, GSH)
- **Issuer:** Australian-based bank or equivalent institution
- **Format:** Strictly prescribed — non-conforming guarantees rejected
- **Validity:** Until revoked (with 30 days notice)
- **Drawdown:** AEMO can draw under guarantee terms if participant defaults

### Alternative Credit Support

| Instrument | Acceptability |
|-----------|---------------|
| Cash deposits | Accepted |
| Standby letters of credit | Accepted |
| Parent company guarantees | Sometimes accepted (case-by-case) |

### Establishment & Maintenance

```
1. Participant arranges with bank
2. Bank issues guarantee per AEMO Pro Forma
3. Participant lodges original signed document with AEMO
4. AEMO confirms valid; participant becomes "credit cleared"
5. Participant responsible for replacement/renewal before expiry
6. AEMO monitors credit support continuously
```

---

## Settlement Data Flows

### AEMO Role

- Calculates spot market prices (every 5 minutes)
- Settles weekly
- Allocates costs and benefits
- Issues settlement statements
- Manages prudential positions
- Operates central settlement system

### Participant Data Provision

| Data Type | Frequency | Source |
|-----------|-----------|--------|
| Metering data | Per metering type schedule | Metering Data Provider |
| Operational data | Real-time | Generators (SCADA) |
| Dispatch response | 5-minute | Ancillary service providers |
| Consumption data | 5-minute (large customers) | Customer/retailer |

### Settlement Statement Contents

- Energy traded by trading interval
- Settlement amounts per region
- Charges (network, market fees, ancillary services)
- Credits (FCAS payments, capacity payments)
- Net cash flow to/from AEMO

---

## Default and Suspension Procedures

### Default Trigger Events

1. Failure to pay settlement amount on due date
2. Credit support falls below MCL
3. Breach of AEMO Market Rules
4. Insolvency proceedings commenced

### Default Resolution Process

```
Day 0: Default identified
   └── AEMO issues default notice

Day 1-5: Cure period
   ├── Participant has 5 business days to remedy
   ├── Pay outstanding amount, OR
   └── Restore credit support to MCL

Day 6+: Non-compliance escalation
   ├── Market suspension (cannot trade)
   ├── AEMO draws on credit support instruments
   └── Continued default → contract termination

Recovery actions:
   ├── Draw on bank guarantee/credit support
   ├── Pursue parent company guarantees
   ├── Legal recovery proceedings for shortfall
   └── Notify other market participants
```

---

## Reallocation Arrangements

Participants can transfer settlement liabilities between each other with AEMO consent:

- **Use cases:** Bilateral PPAs, hedging, group company trading
- **Eligibility:** Must be wholesale clients per Corporations Act
- **Mechanism:** Austraclear-mediated transfer
- **Approval:** Requires AEMO consent and Austraclear membership

---

## Settlement Calendar

AEMO publishes annual settlement calendars showing:
- Billing periods (weekly)
- Due dates for settlements
- Public holidays adjustments
- Revision dates
- Reconciliation milestones

**Reference:** [AEMO Settlement Calendars](https://www.aemo.com.au/energy-systems/electricity/national-electricity-market-nem/market-operations/settlements-and-payments/prudentials-and-payments/settlement-calendars)

---

## Practical Cost Estimates

For new market participants planning entry:

| Participant Type | Typical MCL | Annual Bank Guarantee Cost |
|-----------------|-------------|---------------------------|
| 100 MW Solar Farm | $1-3M | $10K-$60K (1-2% of MCL) |
| 500 MW VPP Aggregator | $200K-$1M | $2K-$20K |
| Retailer (small business focus) | $500K-$5M | $5K-$100K |
| Industrial DRSP (10 MW) | $50K-$500K | $500-$10K |
| Embedded Network Operator | N/A (typically not direct NEM) | N/A |

> Costs are illustrative; actual MCL is participant-specific.

---

## Key Reference Documents

| Document | URL |
|----------|-----|
| **AEMO Procedures and Guides** | [Procedures and Guides](https://aemo.com.au/en/energy-systems/electricity/national-electricity-market-nem/market-operations/settlements-and-payments/prudentials-and-payments/procedures-and-guides) |
| **MCL Information** | [MCL Page](https://aemo.com.au/en/energy-systems/electricity/national-electricity-market-nem/market-operations/settlements-and-payments/prudentials-and-payments/maximum-credit-limit) |
| **MCL Calculator** | [MCL Calculator](https://aemo.com.au/en/energy-systems/electricity/national-electricity-market-nem/market-operations/settlements-and-payments/prudentials-and-payments/maximum-credit-limit/maximum-credit-limit-calculator) |
| **WEM Market Procedure: Prudential Requirements v8** | [WEM Prudential Procedures (PDF)](https://www.aemo.com.au/-/media/files/stakeholder_consultation/consultations/wa_wem_consultation_documents/2020/aepc_2020_06/market-procedure--prudential-requirements-v8-clean.pdf) — retained only as a WA/WEM reference; not a governing NEM source |
| **SSC Reform Page** | [SSC Reform](https://www.aemo.com.au/initiatives/major-programs/nem-reform-program/nem-reform-program-initiatives/shortening-the-settlement-cycle) |
| **Settlement Calendars** | [Calendars](https://www.aemo.com.au/energy-systems/electricity/national-electricity-market-nem/market-operations/settlements-and-payments/prudentials-and-payments/settlement-calendars) |

---

## Official Source Binding

| Principal conclusion | Official instrument and issuer | Version or date | Local copy or link |
|----------------------|--------------------------------|-----------------|--------------------|
| SSC reform: nine business days, transition from 20 to 9, commencement date, and double-payment weeks | **AEMC Shortening the Settlement Cycle Final Determination, ERC0384** | 12 December 2024 | [[official-documents/market-core-documents/AEMC-SSC-ERC0384-Final-Determination.pdf]] |
| **TOSL reduced from 35 to 19 days; total exposure window reduced from 42 to 26 days** | AEMC ERC0384 section 3.3.1, page 12 | 12 December 2024 | Same local PDF |
| MCL = OSL + PM; seven-day reaction period; 2% standard | **NER Chapter 3 rule 3.3** and AEMO **Credit Limit Procedures** | NER v251; CLP updated 9 August 2026 | [NER rule 3.3](https://energy-rules.aemc.gov.au/ner/175/23916) and [AEMO CLP-SSC consultation](https://aemo.com.au/consultations/current-and-closed-consultations/credit-limit-procedures---ssc-and-related-changes) |
| Live operations, settlement cadence and cash planning | **AEMO Settlement Communication No. 698**, Transition Plan and Participant Readiness Fact Sheet | 9 August 2026 | [[official-documents/market-core-documents/AEMO-SSC-Transition-Plan.pdf]] and [[official-documents/market-core-documents/AEMO-SSC-Participant-Readiness-Fact-Sheet.pdf]] |
| Default event | NER 3.15.21(a)(1) | NER v251 | [NER Chapter 3.15](https://energy-rules.aemc.gov.au/ner) |

## Related in This Tier
- [[Market-Participants-Licensing]]
- [[NEM-Overview]]
- [[FCAS-Ancillary]]
- [[Retailer-Authorisation]]
- [[Aggregator-Roles]]
