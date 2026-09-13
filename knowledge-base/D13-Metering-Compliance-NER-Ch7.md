---
country: Australia
category: compliance/metering
page: D13-gap Metering Compliance — NER Chapter 7
last_updated: 2026-08-27
status: draft-researched
sources:
  - AEMC National Electricity Rules (NER) Chapter 7 — Metering (energy-rules.aemc.gov.au)
  - AEMO Metrology Procedure Part A / Part B (aemo.com.au)
  - AEMC Accelerating Smart Meter Deployment — Final Determination, 28 Nov 2024
  - AER Legacy Meter Replacement Plans (2025) & retailer notice guidance (May 2025)
tags: [metering, NER-Chapter-7, Power-of-Choice, smart-meter, Metrology-Procedure, BESS, MC, MP, MDP, NMI]
---

# D13 Metering Compliance — NER Chapter 7 Metering Framework

> **Intended audience:** BESS developers responsible for settlement-grade metering, EMS/SCADA vendors handling data interfaces and privacy, and retail-authorisation applicants subject to accelerated smart-meter deployment obligations. Information current to **2026-08-27**.

## 1. Overview

| Matter | Key requirement | Authority |
|---|---|---|
| Metering framework | NER **Chapter 7 — Metering**, the competitive metering framework introduced through Power of Choice and effective from 2017-12-01 | AEMC, current NER Chapter 7 |
| Three principal roles | **MC**, Metering Coordinator; **MP**, Metering Provider; **MDP**, Metering Data Provider | NER cll 7.2–7.4 |
| Meter types | Types 1–4: remotely read interval meters; Type 4A: manually read interval meter; Type 5: legacy manually read interval meter; Type 6: legacy accumulation meter; Type 7: calculated unmetered load | NER Chapter 7 and schedules governing type and accuracy |
| Detailed metrology rules | AEMO **Metrology Procedure Part A** for NEM metrology and **Part B** for validation, substitution and estimation of metering data, made under NER cl 7.16 | AEMO |
| Accelerated smart-meter deployment | Final determination dated 2024-11-28 requires **100% smart meters by 2030-12-01**; Legacy Meter Replacement Plans apply for the five-year period 2025-12-01 to 2030-11-30 | AEMC Accelerating Smart Meter Deployment Rule |
| 5 MW BESS | A market generating unit requires Type 1–4 interval metering. Based on typical annual throughput, a 5 MW BESS ordinarily falls within **Type 3**, 0.75–100 GWh: class 0.5 CT/VT and class 1.0 Wh meter, with overall error ≤±1.5% | NER cl 7.8.2 and accuracy schedules |

## 2. Roles and Accreditation

Power of Choice, implemented through the AEMC's Expanding Competition in Metering and Related Services Rule 2015 from 2017-12-01, moved metering from a DNSP monopoly to competitive service provision.

- **Metering Coordinator (MC):** the entity with overall responsibility for metering at each connection point, succeeding the former "responsible person" concept. The **FRMP, ordinarily the retailer, appoints the MC**. A large customer may appoint its own MC. The MC must register with AEMO as a Chapter 2 registration category.
- **Metering Provider (MP):** provides, installs and maintains metering equipment. It must be **accredited and registered by AEMO**, work only within the categories for which it is accredited and hold the licences required by the relevant state or territory under the MP qualification provisions in the NER metering schedules. An NSP acting as responsible person must register as an MP or contract with one; this is a **civil penalty provision**.
- **Metering Data Provider (MDP):** collects, validates, substitutes or estimates and delivers settlement data to AEMO through MSATS. It must also be **accredited and registered by AEMO**.
- **Separation of interests:** a Market Generator or Market Customer engaged in energy trading generally cannot register as the MP for a connection point at which it consumes energy. This obligation formerly appeared at NER cl 7.4.2(d) and continues in the current Rules. ⚠️ Confirm the current clause number at energy-rules.aemc.gov.au.
- A DNSP acts as initial MC for legacy Type 5 and Type 6 meters under the transitional arrangements. The LNSP is also responsible for Type 7 unmetered loads.

## 3. Meter Types and Volume Thresholds

The following figures are drawn from current **NER Schedule 7.4**, principally Table **S7.4.3.1**. References to historical Table S7.2.3.1 have been removed.

| Type | Annual throughput at the connection point | Maximum overall error at full load | Minimum component class | Clock error relative to EST | Read method |
|---|---|---|---|---|---|
| **Type 1** | >1,000 GWh | Active ±0.5% / reactive ±1.0% | Class 0.2 CT, VT and Wh meter; class 0.5 varh meter | ±5 s | Remote interval |
| **Type 2** | 100–1,000 GWh | ±1.0% / ±2.0% | Class 0.5 CT, VT and Wh meter; class 1.0 varh meter | ±7 s | Remote interval |
| **Type 3** | 0.75–<100 GWh | ±1.5% / ±3.0% | Class 0.5 CT/VT; class 1.0 Wh meter; class 2.0 varh meter | ±10 s | Remote interval |
| **Type 4** | <750 MWh | ±1.5%; reactive n/a | Class 0.5 CT and class 1.0 Wh meter, or a general-purpose whole-current meter | ±20 s, subject to any relaxation in the Metrology Procedure | Remote interval, a **smart meter** |
| **Type 4A** | Small customer | Same as Type 4 | Same as Type 4 | Same as Type 4 | **Manually read interval meter**, permitted where communications are unavailable or the customer refuses remote communications |
| **Type 5** | Below jurisdictional ministerial threshold "x", capped at **750 MWh per year** | ±1.5% | Class 0.5 CT and class 1.0 Wh meter, or a whole-current meter | ±20 s | Manually read interval meter; legacy only and prohibited for new installations |
| **Type 6** | Below jurisdictional threshold "y", capped at 750 MWh per year | ±2.0% | CT or whole-current meter recording only **accumulated energy data**, converted to trading-interval data under the Metrology Procedure | Set by the Metrology Procedure | Manually read accumulation meter; legacy only and prohibited for new installations |
| **Type 7** | No threshold | Calculated under the Rules | **No meter**, used for calculated loads such as street lighting | n/a | Calculated |

Key points:

- **High-voltage customer exception:** where a high-voltage customer requires a VT but consumes less than 750 MWh per year, active-energy accuracy must meet the Type 3 Item 2 requirement.
- The same schedule sets accuracy at test points of 10%, 50% and 100% of rated load and at different power factors. For example, Type 3 active-energy error is ±2.5% at 10% load and ±1.5% at 50% and 100% load.
- Inspection and testing requirements appear in NER **Schedule 7.6**. The minimum services specification, including remote connect/disconnect and on-demand reads for smart meters, appears in **Schedule 7.5**.
- From 2017-12-01, a new or replacement meter for a small customer must be **Type 4**. Type 4A is permitted only where communications are unavailable or the customer expressly refuses remote communications.

## 4. Metrology Procedure Parts A and B — Current Versions

- Under **NER cl 7.16**, AEMO develops and maintains the Metrology Procedure. An amendment generally requires a transition period of at least three months, other than a minor amendment.
- **Part A:** version **8.14**, effective **2026-08-25**, is the current NEM metrology procedure following AEMO's August 2026 REMP expedited consultation.
- **Part B:** version **8.13**, effective **2026-06-09**, is the current Metering Data Validation, Substitution and Estimation Procedure for Types 1–7.
- **Part C:** version **1.1**, effective **2026-03-19**, is the current Testing and Inspection Guidelines instrument. AEMO has also published future Parts A and B **v8.23**, effective **2026-11-01**; those future versions should not be treated as operative before that date.

## 5. Accelerated Smart-Meter Deployment and Retailer Obligations

The **National Electricity Amendment (Accelerating Smart Meter Deployment) Rule 2024**, made in the AEMC final determination of 2024-11-28, amended the NER and NERR as follows:

- **Target:** replace every legacy Type 5 and Type 6 meter with a Type 4 smart meter by 2030-12-01, achieving 100% NEM coverage.
- **Staged commencement:** 2024-12-05 for NER Schedule 4; 2025-06-01 for NERR Schedule 1; **2025-12-01 for NER Schedule 1 and commencement of the accelerated rollout and core retailer obligations**; 2026-05-31 for NER Schedule 3; and 2026-07-01 for NER Schedule 2.
- **Legacy Meter Replacement or Retirement Plan (LMRP):** each **DNSP prepares** a plan for retiring legacy meters between 2025-12-01 and 2030-11-30. Endeavour Energy, Ergon and SAPN published plans in 2025. The **retailer must complete replacements according to the LMRP**; its appointed MC organises replacement and remains responsible for smart-meter operation, maintenance and reads.
- **Customer protections commencing in stages from June and December 2025:**
  - **No upfront charge:** a small customer cannot be charged an installation fee for a planned replacement; the cost is recovered through retail prices.
  - A retailer cannot change the customer's tariff after replacement without **explicit informed consent**, preventing automatic movement to a time-of-use or demand tariff merely because a smart meter was installed.
  - The retailer has a **replacement-notice obligation**. The AER published "Notice to small customers on deployment of new electricity meters" guidance in May 2025.
  - A customer subject to a LMRP does not have a general right to stop replacement of the legacy meter. Separately, NER cl 7.8.4 allows a small customer to refuse installation or continued remote use of a Type 4 meter if the FRMP supplies the required comparison and charge information and the MC accepts the refusal. The refusal may be verbal, written or by conduct; the resulting installation is Type 4A, including by deactivating remote access where permitted, and the MC must retain specified records for at least two years. Type 4A charges may be payable by the customer. This is a refusal of remote-access functionality, not an opt-out from the LMRP replacement program.
- **Shared fuses:** NER cl 7.8.10D and the AER's September 2025 guidance establish a coordination process, not a general duty for the DNSP to "rectify" the shared fuse. The original MC notifies the retailer within **5 business days**; the retailer notifies the LNSP within **5 business days**; the LNSP identifies affected NMIs and determines whether one or more shared-fusing replacement dates are required within **30 business days**. A replacement date is set **25–65 business days** after notice. Each affected retailer appoints an MC within **10 business days** of receiving the shared-fusing replacement notice. Access, safety, life-support and site-defect exceptions remain relevant.
- **Customer-requested meter installation:** NER cl 7.8.10B uses an agreed date or, absent agreement, a base period of **15 business days** where no connection service is required, subject to stated exceptions. During the LMRP period, transitional cl 11.177.11 extends the cll 7.8.10A–C periods by five business days. The former blanket six-business-day statement was incorrect.

## 6. Generation and Bidirectional Settlement Metering for a 5 MW BESS

- **Meter type:** a small generating unit classified as a market generating unit must use a **Type 1, 2, 3 or 4** metering installation capable of recording energy by the five-minute trading interval under NER cl 7.8.2. The same bidirectional settlement-metering principle applies after a BESS registers as an **Integrated Resource Provider (IRP)**.
- **Typical classification:** a 5 MW / 10 MWh BESS cycling approximately once per day has combined charging and discharging throughput of approximately 7–9 GWh per year. It therefore ordinarily requires **Type 3** metering for 0.75–<100 GWh: active-energy error ≤±1.5%, reactive-energy error ≤±3.0%, CT and VT of at least class 0.5, a Wh meter of at least class 1.0, a varh meter of at least class 2.0, clock error ≤±10 seconds and remote interval reads. If annual throughput at the point exceeds 100 GWh, Type 2 applies, requiring class 0.5 CT, VT and meter and overall error ≤±1.0%.
- **Bidirectional data:** establish import and export datastreams under one **NMI**. Settlement uses the five-minute settlement framework introduced in October 2021 and global settlement introduced in May 2022.
- **NMI standing data:** the FRMP applies to the LNSP for the NMI and must provide it to the MC **within five business days after receiving it**. MSATS/CATS maintains the NMI classification code, TNI, DLF and assignments of the MC, MP and MDP roles.
- **Implementation:** agree the meter-point location during connection negotiations because an HV-side rather than LV-side point changes loss allocation and CT/VT configuration. Retain CT/VT verification certificates and confirm any check-metering requirement with the DNSP or TNSP. Type 1 and points above 1,000 GWh require check metering. ⚠️ Confirm against the current schedule.

## 7. Metering Data Delivery and Privacy

- **Delivery:** the MDP supplies data according to Metrology Procedure Part B and AEMO's settlement timetable. Remotely read Types 1–4 generally provide trading-interval data **daily** for settlement. Manually read Types 5 and 6 provide data according to a meter-read cycle of no more than three months, with validation, substitution and estimation under Part B. Settlement revision windows apply after initial settlement. ⚠️ Consult the current Part B and settlement timetable for exact day counts.
- **Privacy and confidentiality:** metering data is confidential information. The NER cl 7.15 series limits access to **energy data** to parties including the FRMP, MC, AEMO, NSP, the customer and an authorised representative, and requires access records. Where data is personal information, the Privacy Act 1988 (Cth) and Australian Privacy Principles also apply. An EMS/SCADA vendor accessing customer metering data must have a documented authority chain through the customer's express consent or an authorising FRMP/MC contract.
- **Penalty framework:** the applicable amount depends on whether the particular paragraph is classified in Schedule 1 to the National Electricity (South Australia) Regulations as Tier 1, 2 or 3. From **2026-07-01**, the maximums are:

| Tier | Natural person | Body corporate |
|---|---|---|
| Tier 1 | $619,500 | Greater of $12.39 million, three times the attributable benefit, or 10% of annual turnover where the benefit cannot be determined |
| Tier 2 | $355,600 plus $17,800 for each continuing day | $1.778 million plus $89,000 for each continuing day |
| Tier 3 | $42,000 plus $4,200 for each continuing day | $210,600 plus $21,100 for each continuing day |

For example, cl 7.8.4(f) and (h) are identified as Tier 3 provisions, while cl 7.8.4(g), the two-year refusal-record requirement, is identified as Tier 2. Do not assign a maximum to a Chapter 7 breach without checking the classification of the exact paragraph.

## Official Source Bindings

| Key proposition | Governing document | Issuer / version | URL |
|---|---|---|---|
| Chapter 7 framework, MC/MP/MDP roles and AEMO accreditation | NER Chapter 7 — Metering, current version | AEMC online Rules | https://energy-rules.aemc.gov.au/ner/347/38482 |
| Type 1–7 volume, accuracy and clock thresholds | NER Schedule 7.4, including Table S7.4.3.1 | AEMC online Rules, current | https://energy-rules.aemc.gov.au/ner/3/6720 |
| Inspection and testing requirements and minimum services specification | NER Schedule 7.6 and Schedule 7.5 | AEMC | https://energy-rules.aemc.gov.au/ner/452/229713 ; https://energy-rules.aemc.gov.au/ner/177/30584 |
| Metering-installation arrangements and requirement for market generating units to use Type 1–4 | NER Rule 7.8, including cl 7.8.2 | AEMC | https://energy-rules.aemc.gov.au/ner/177/30480 |
| AEMO power to make the Metrology Procedure and three-month transition | NER Rule 7.16 | AEMC | https://energy-rules.aemc.gov.au/ner/477/273554 |
| Current Part A v8.14 from 2026-08-25 and future Parts A/B v8.23 from 2026-11-01 | August 2026 REMP Expedited Consultation final stage | AEMO, 2026-08-25 | https://www.aemo.com.au/consultations/current-and-closed-consultations/august-2026-remp-expedited-consultation |
| Current Part B v8.13 from 2026-06-09 and Part C v1.1 from 2026-03-19 | Metrology Procedures and Unmetered Loads | AEMO, current | https://www.aemo.com.au/energy-systems/electricity/national-electricity-market-nem/market-operations/retail-and-metering/metrology-procedures-and-unmetered-loads |
| Accelerated smart-meter deployment, 2030 coverage, staged commencement, LMRPs and customer protections | Accelerating Smart Meter Deployment — Final Determination, 2024-11-28 | AEMC | https://www.aemc.gov.au/rule-changes/accelerating-smart-meter-deployment ; final determination PDF https://www.aemc.gov.au/sites/default/files/2024-11/Final%20rule%C2%A0determination%C2%A0%20271124%20%28For%20publication%29.pdf |
| Example LMRP prepared by a DNSP for the 2025-12-01 to 2030-11-30 period | Legacy Meter Replacement Plans, including Endeavour, Ergon and SAPN, 2025 | AER archive | https://www.aer.gov.au/system/files/2025-08/SA%20Power%20Networks%20-%20Legacy%20Meter%20Replacement%20Plan%20-%201%20September%202025.pdf |
| Retailer notice obligation for meter deployment | Guidance for retailers — Notice to small customers on deployment of new electricity meters, 2025-05 | AER | https://www.aer.gov.au/system/files/2025-05/Guidance%20for%20retailers%20-%20Notice%20to%20small%20customers%20on%20deployment%20of%20new%20electricity%20meters_0.pdf |
| Small-customer refusal of Type 4 remote access, Type 4A outcome, charges and records | NER cl 7.8.4 | AEMC online Rules, current | https://energy-rules.aemc.gov.au/ner/477/273504 |
| Shared-fusing roles and 5/5/30/25–65/10 business-day sequence | Guidance to retailers: Site Defects, Tariff Structure Changes and Shared Fusing; NER cl 7.8.10D | AER, 2025-09-12 / AEMC current Rules | https://www.aer.gov.au/system/files/2025-09/Guidance%20to%20retailers%20-%20Site%20Defects%2C%20Tariff%20Structure%20Changes%20and%20Shared%20Fusing.pdf ; https://energy-rules.aemc.gov.au/ner/177/30480 |
| Indexed Tier 1, 2 and 3 civil penalty maximums from 2026-07-01 | Civil and criminal penalty indexation | AER, current | https://www.aer.gov.au/civil-and-criminal-penalty-indexation |

*Status: draft-researched. The previously flagged Metrology Procedure versions, Schedule 7.4 reference, shared-fusing sequence, Type 4A refusal pathway and 2026 indexed penalty amounts have been checked against the official AEMO, AEMC and AER material cited above. Site-specific metering design and any exception still require confirmation with the appointed MC, FRMP and LNSP.*
