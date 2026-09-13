---
country: Australia
category: emergency-system-security-compliance
domain_id: D15
last_updated: 2026-08-27
status: draft-researched
regions_focus: [SA, NSW, VIC]
sources:
  - National Electricity Law (NEL, Schedule to National Electricity (South Australia) Act 1996), s116 / s118
  - National Electricity Rules (NER) v252 (AEMC, 2026-08-09), Ch 3 (3.12, 3.14, 3.15, 3.20) & Ch 4 (4.8)
  - AEMO SO_OP_3707 "Procedures for Issue of Directions and Clause 4.8.9 Instructions"
  - AEMC Compensation frameworks page (administered pricing / market suspension / directions)
  - AEMO Black System South Australia Final Report (March 2017)
  - AER June 2022 Market Events Report (December 2022)
  - AER Retailer Reliability Obligation & MLO pages
  - AEMO RERT / SRAS / LOR / UFLS-EFCS program pages
tags: [AEMO directions, NER Chapter 4, market suspension, RERT, SRAS, LOR, UFLS, EFCS, RRO, MLO, black system, BESS compliance]
---

# D15 Emergency and Power-System Security Compliance in the NEM

> **Intended audience:** BESS developers, EMS vendors and retail-authorisation applicants operating in the NEM, with emphasis on SA, NSW and VIC. This page covers AEMO's emergency powers, participant compliance obligations, compensation mechanisms, reserve and system-restart frameworks, emergency frequency control and relevant enforcement cases.

## 1. Overview

| Mechanism | Legal basis | Responsible body | Principal effect on BESS operators and retailers |
|---|---|---|---|
| AEMO Directions | NEL ss 116 and 118; NER cll 4.8.9 and 4.8.9A | AEMO issues; AER enforces | A participant must comply with a charging, discharging or operating direction unless compliance would endanger a person or equipment; compensation may be available under cl 3.15.7 |
| Clause 4.8.9 Instructions | NER cl 4.8.9; SO_OP_3707 | AEMO | An instruction is distinct from a direction and has no separate compensation route; it requires action within an existing participant obligation |
| Market Suspension | NER rule 3.14 | AEMO | Spot settlement changes to the market suspension pricing schedule; an arbitrage revenue model no longer operates as expected; compensation may be available |
| Administered Price Cap (APC) | NER cll 3.14.1–3.14.2; Reliability Panel determination | AEMC / Reliability Panel | After the Cumulative Price Threshold (CPT) is exceeded, spot prices are capped at the $600/MWh APC; costs above the APC may be claimed under cl 3.14.6 |
| Reliability and Emergency Reserve Trader (RERT) | NER rule 3.20 | AEMO | A BESS or demand-response resource may contract as an out-of-market reserve and must respond according to the contract when activated |
| System Restart Ancillary Services (SRAS) | NER cll 3.11.7–3.11.9; SRAS Guideline | AEMO; Reliability Panel sets the standard | A BESS with black-start or restoration-support capability may compete for an SRAS contract |
| Lack of Reserve (LOR) framework | NER cl 4.8.4; Reserve Level Declaration Guidelines | AEMO | LOR1, LOR2 and LOR3 declarations are operational precursors to RERT activation and directions and affect dispatch strategy |
| UFLS / EFCS | NER cll 4.3.1 and 4.8.5A; AEMC Emergency Frequency Control Schemes Rule 2017 | AEMO / NSPs / jurisdictions | Load, including BESS charging load, may form part of an UFLS block; DER is increasingly incorporated into emergency frequency-control arrangements |
| DER Emergency Backstop | SA Smarter Homes legislation and each jurisdiction's backstop framework | State governments / AEMO / DNSPs | Inverters installed in SA from 2020-09-28 must support remote disconnection; AEMO may direct SAPN to curtail distributed solar in an emergency |
| Retailer Reliability Obligation (RRO) | NEL Part 2A as amended for the RRO; NER Chapter 4A | AER makes reliability instruments; AEMO identifies gaps | Liable entities, comprising retailers and wholesale-market large users, must hold sufficient qualifying contracts; the Market Liquidity Obligation (MLO) requires nominated generators to make markets |

## 2. AEMO Directions and Participant Compliance under NER Chapter 4

### 2.1 Sources of power

- **NEL s 116:** AEMO may direct a Registered Participant to take action where AEMO considers it necessary to maintain or restore power-system security, reliability or public safety.
- **NEL s 118 and NER cll 4.8.9 and 4.8.9A:** a Registered Participant must comply with a direction or clause 4.8.9 instruction **unless compliance would endanger a person, damage equipment or breach a law**. This is a core civil penalty provision.
- AEMO's **SO_OP_3707, "Procedures for Issue of Directions and Clause 4.8.9 Instructions,"** was revised following a NEM consultation in 2024. NER cl 4.8.9(b) requires the procedure to reflect the principle that AEMO use reasonable endeavours to minimise the costs and compensation associated with a direction.

### 2.2 Direction versus instruction

| | Direction | Clause 4.8.9 Instruction |
|---|---|---|
| Trigger | Need to maintain system security, reliability or public safety | Requirement that a participant perform an existing obligation, such as following dispatch |
| Compensation | Available: a Directed Participant claims under cll 3.15.7, 3.15.7A or 3.15.7B; Affected Participants and Market Customers claim under cl 3.12.2 | No independent compensation route |
| Common recipients | SA gas generators, which historically received recurring system-strength directions, and BESS charging or discharging assets | All participants |

**BESS-specific requirement:** a direction can move charging or discharging away from the asset's commercial plan. Compensation is calculated through a direct-cost and opportunity-cost framework. Clause 3.15.7 provides the default formula, and cl 3.15.7B permits an application for additional compensation where that formula is insufficient. An EMS must execute the direction and retain timestamped SCADA and control records because those records are material evidence in AER enforcement.

## 3. Market Suspension and Administered Pricing under NER Rule 3.14

- **CPT/APC mechanism:** when seven-day rolling cumulative spot prices exceed the Cumulative Price Threshold, an administered-price period begins. For **1 July 2026 to 30 June 2027**, the **Market Price Cap is $23,200/MWh**, the **Cumulative Price Threshold is $2,225,900**, and the **administered price cap is $600/MWh**. The AEMC indexes the Market Price Cap and Cumulative Price Threshold annually, so operating procedures must use the applicable year's schedule.
- **Clause 3.14.6:** a participant whose generation costs exceed the APC during an administered-price period may claim administered-pricing compensation from the AEMC. The AEMC published multiple final compensation decisions following June 2022.
- **Market suspension, cll 3.14.3–3.14.5:** AEMO may suspend the market if it cannot maintain secure operation or operate the market in accordance with the Rules. Settlement then uses the **market suspension pricing schedule**, based on the mean price for the corresponding interval in the previous week.

### Case: NEM Mainland Market Suspension in June 2022

- **Timeline:** mainland regions progressively reached the then $300/MWh APC from 2022-06-12; significant capacity was withdrawn from offers; AEMO issued large numbers of directions; on **2022-06-15 AEMO suspended every mainland NEM spot market for the first time**, and normal operation resumed on 2022-06-23/24.
- **Compensation:** the three compensation categories totalled **$148.8 million**, including **$18.3 million in Directions Compensation** and **$94.8 million in Suspension Pricing Compensation**, with the balance in APC compensation. Costs were recovered from Market Customers in proportion to adjusted gross energy, so a retailer must account for this post-event recovery risk in pricing and hedging.
- **Compliance lessons:** (1) the AER closely examined economic withdrawal of availability during the APC period, including failures to rebid available capacity; the crisis did not suspend rebidding or availability-reporting obligations; (2) participants had to comply with directions and preserve evidence; and (3) retailers faced compensation pass-through costs, reinforcing the value of RRO and hedge-position management. See the AER's December 2022 "June 2022 Market Events Report."
- **Subsequent development:** in 2025-12, AEMO submitted an AEMC rule-change request to reform the compensation frameworks. The matter remained under consideration. ⚠️ Monitor progress.

## 4. RERT Framework and 2025–26 Position under NER Rule 3.20

- AEMO may contract for out-of-market emergency reserves, including generation and demand response, only where it expects the reliability standard cannot otherwise be met. Procurement is divided into long-notice, medium-notice and short-notice categories.
- Under the **Interim Reliability Reserve (IRR)**, AEMO could procure up to three years in advance through 2025-03-31 to address an interim reliability exceedance. For summer 2024–25, AEMO procured limited IRR in NSW and SA, including 110 MW in SA contracted from 2025-01-29 to 2025-03-31.
- **2025–26 position:** AEMO did not forecast a reliability gap in NSW, SA or VIC and therefore identified no IRR or RERT procurement need for 2025–26, based on its 2025 RERT quarterly reports.
- A RERT resource must be **out of market**, meaning the relevant capacity is not classified and traded in the spot market. Capacity in an AEMO-registered scheduled BESS generally cannot also be committed to RERT. Aggregated demand response and standby generation are typical resources. Activation costs are recovered from Market Customers in the relevant region.

## 5. System Restart Ancillary Services

- The framework is established by NER cl 3.11.7 and the **SRAS Guideline** made by AEMO under cl 3.11.7A. It is designed to meet the Reliability Panel's **System Restart Standard (SRS)**.
- The two service classes are **Black Start Services**, which can start without an energised grid, and **Restoration Support Services**, added in 2021. A BESS with a grid-forming inverter may compete to provide restoration support.
- AEMO completed a procurement round in 2024 and entered **six new contracts plus one extension**, with regional contract terms ending between 2027 and 2030. Contract details are confidential; aggregate information appears in the NMAS Report 2024–25 published in 2025-10.
- On **2025-12-11**, the Reliability Panel issued its final determination in the System Restart Standard review and adopted a revised SRS. AEMO was consulting on revisions to the SRAS Guideline so that the next procurement round, scheduled to begin in **mid-2026**, would use the new standard. BESS developers with black-start or grid-forming capability should monitor that procurement window.
- SRAS did not perform as expected during the 2016 South Australian black system because contracted stations failed to deliver successfully. That experience directly informed stronger testing and reliability-assessment requirements in the Guideline.

## 6. Lack of Reserve Framework

- The framework is based on NER cl 4.8.4(b) and AEMO's **Reserve Level Declaration Guidelines**.
- Under AEMO's **Reserve Level Declaration Guidelines v3.0**, effective 26 June 2024: **Actual LOR1** means the consecutive occurrence of the largest and second-largest relevant credible contingency events would require involuntary load shedding; **Actual LOR2** means the largest relevant credible contingency event would require involuntary load shedding; and **Actual LOR3** means involuntary load shedding is occurring because available reserves are insufficient. Forecast LOR levels use the calculated thresholds and forecast-uncertainty measures specified in the guideline, not fixed MW or percentage shortcuts. AEMO publishes Forecast and Actual LOR notices through Market Notices.
- A LOR notice invites a market response and is an important operational input, but RERT activation or a direction is not mechanically triggered by one LOR level alone. AEMO applies the current RERT framework and its operational assessment. A replacement Reserve Level Declaration Guideline is targeted for 31 March 2027 but is not yet operative.

## 7. UFLS and EFCS Obligations, Including New DER Measures

- **Under-frequency load shedding (UFLS)** is a last line of defence against system collapse after a non-credible double contingency. Under the NER, AEMO assesses the need for emergency frequency-control capability covering **up to 60% of total system load**. NSPs are responsible for configuring and coordinating UFLS relays. DNSPs and TNSPs must coordinate and prevent a new connection from degrading UFLS effectiveness.
- The AEMC's **National Electricity Amendment (Emergency Frequency Control Schemes) Rule 2017** established the EFCS framework and protected-event mechanism, with protected events declared by the Reliability Panel.
- **Low-load risk in South Australia:** distributed PV can reduce net load available for UFLS to almost zero or make it negative. Responses include **dynamic arming**, which removes an UFLS block when its net load reverses, and the incorporation of DER into emergency frequency response.
- **BESS/EMS compliance:** (1) during connection negotiations, confirm UFLS block membership and dynamic arming with the DNSP, SAPN in South Australia. BESS charging load on an UFLS feeder may be disconnected during an under-frequency event. (2) EMS frequency-protection settings must match the approved **Generator Performance Standards** and receive written AEMO and NSP approval. Section 9 records penalties for operating with unapproved settings.
- **DER Emergency Backstop:** under the SA Smarter Homes rules, an inverter installed after **2020-09-28 must support remote disconnection**. AEMO may direct SAPN to curtail distributed PV during a system-security risk associated with minimum system load. AEMO sought mainland backstop frameworks by the end of 2025. Victoria applied new-installation requirements from October 2024, while NSW and Queensland followed their own rollouts. ⚠️ Verify each jurisdiction's commencement date against current government material. An EMS for a new South Australian installation must support SAPN's Relevant Agent, Flexible Exports and remote-disconnection interfaces.

## 8. Load Shedding and Sensitive-Load Priority

- During a large supply-demand shortfall, AEMO must apply involuntary load shedding **equitably** and in accordance with the Reliability Panel's power-system security and reliability standards.
- Each **jurisdiction determines its sensitive-load register and load-shedding priority**. The relevant Jurisdictional System Security Coordinator provides AEMO with the sensitive loads and priority schedule under state emergency legislation. Cross-jurisdiction coordination follows MOUs between AEMO and the NEM jurisdictions and AEMO's **Power System Emergency Management Plan (PSEMP)**, a non-public document distributed only to relevant stakeholders. Victoria also maintains the Victorian Energy Emergency Communications Protocol.
- A BESS co-located on a feeder with a sensitive load may face a different practical shedding probability. Reliability statements in contracts with C&I customers such as data centres and hospitals must not conflict with the jurisdiction's load-shedding arrangements.

## 9. Penalties, Enforcement and Cases

### 9.1 Civil penalty framework from 2021, indexed by CPI

| Tier | Maximum corporate penalty applying from 2026-07-01 |
|---|---|
| Tier 1 | The greatest of $12.39 million, three times the benefit obtained or 10% of annual turnover |
| Tier 2 | $1.778 million plus $89,000 for each day of a continuing contravention |
| Tier 3 | $210,600 plus $21,100 for each day of a continuing contravention |

These are the maximum corporate civil penalties applying from 1 July 2026. Compliance with directions under cl 4.8.9 is a civil penalty provision. The tier and availability of a daily penalty depend on the exact provision breached; check Schedule 1 to the National Electricity Regulations and the current AER indexation table.

### 9.2 Enforcement Chain after the 2016-09-28 South Australian Black System

- **Event:** extreme weather damaged transmission towers, producing voltage disturbances. Wind-farm **LVRT protection settings were excessively sensitive**, causing a sudden 456 MW reduction, followed by loss of the Heywood interconnector and a statewide blackout affecting approximately 850,000 customers. Some load remained disconnected for more than eight hours. See the AEMO Final Report of March 2017.
- The AER commenced Federal Court proceedings against four wind-farm operator groups, resulting in:
  - **Snowtown 2, Tilt:** $1 million penalty in December 2020.
  - **Hornsdale Wind Farm 1, Neoen:** $550,000, and **Pacific Hydro Clements Gap:** $1.1 million, for combined penalties above $1.6 million in July 2021.
  - **Three AGL subsidiaries operating the Hallett wind-farm group:** combined penalties of $3.5 million. AGL admitted that the wind farms operated for more than three years using LVRT settings that had not received written approval from AEMO and ElectraNet.
- **Core compliance lesson for BESS:** protection and ride-through settings in the GPS are the **approved settings**. Any firmware or parameter change that alters the response characteristic must first follow the NER 5.3.9 change-approval process. Operating with unapproved settings can contravene the Rules even if the change did not cause an event.
- **Framework consequences:** the event contributed to the system-strength and inertia frameworks, the annual **General Power System Risk Review (GPSRR)** that replaced the biennial PSFRR, the protected-event mechanism and strengthened SRAS testing.

### 9.3 June 2022

As described in Section 3, the AER's event report examined capacity withdrawals and rebidding during administered pricing, and $148.8 million of compensation was recovered from the market. This socialisation of compliance and emergency costs means a retail-authorisation applicant should address extreme-event cash flow in the risk-management plan submitted to the AER.

## 10. RRO and MLO

- **RRO process:** after AEMO identifies a forecast reliability gap through the ESOO or an update, the AER may be requested to make a **T-3 reliability instrument** three years before the gap and a **T-1 instrument** one year before it. The South Australian Minister retains a direct trigger power and used it in January 2023 for the first quarter of 2026. **Current example in the source set: the AER made a T-3 instrument for a NSW gap from 2025-12-01 to 2026-02-28.**
- **Liable entities:** retailers and large users that purchase directly from the wholesale market. At T-1, they report their **Net Contract Position (NCP)** to the AER. Qualifying contracts must cover the entity's share of peak demand for a one-in-two-year outcome. If the position is insufficient and the gap occurs, the entity contributes to Procurer of Last Resort costs.
- **MLO:** from T-3 to T-1 after an RRO trigger, nominated large generators in the region must begin continuous market making on an approved MLO exchange, such as ASX 24, within five business days. Bids and offers must remain within the maximum spread to support hedge liquidity. The AER conducted an MLO exchange review in 2025.
- **Small retailer or new applicant:** RRO compliance requires early procurement and a register of qualifying swaps, caps and PPAs. A BESS tolling agreement may qualify. ⚠️ Assess firmness under the AER Contracts and Firmness Guidelines.

## 11. Emergency Communications and Data Obligations

- **Communications:** a participant must maintain AEMO-required operational channels, including a 24/7 control-room contact and monitoring of Market Notices. NER cl 4.8.1 requires the participant to **immediately notify AEMO** when it becomes aware of circumstances affecting power-system security, such as abnormal equipment operation or a change in availability. AEMO's SO_OP procedures, including SO_OP_3707 for directions and SO_OP_3715 Power System Security Guidelines, provide operational detail.
- **Exercises and information:** the PSEMP and jurisdictional arrangements may require participation in emergency exercises and provision of sensitive-load information.
- **Generation information:** under the Generation Information Guidelines and annual standing information request, AEMO collects generation and storage facility data used in ESOO gap assessments and therefore in RERT and RRO decisions. The 2026 standing-information return was due on 2026-04-03.
- **Queensland terminology:** a **Generation Signalling Device (GSD)** is the distribution-network emergency-backstop device used for relevant small generation systems in Queensland. It is not a generic NER Chapter 4 system-security data category. Applicability, installation and testing must be confirmed with the relevant Queensland DNSP under its emergency-backstop requirements.

## 12. Compliance Checklist for BESS Developers, EMS Vendors and Retail Applicants

| # | Check | Authority |
|---|---|---|
| 1 | EMS can receive and execute an AEMO charging, discharging or power-limiting direction in real time and preserve a complete audit trail | NEL s 118; NER cl 4.8.9 |
| 2 | Protection, LVRT and frequency settings match the approved GPS; obtain written AEMO and NSP approval before any change | NER cl 5.3.9; AGL/Hallett case |
| 3 | Direction-compensation process includes cost records. A claim for additional compensation under cl 3.15.7B is due within **15 business days after receipt of AEMO's compensation advice**; the cl 3.15.7A(f) period is also 15 business days after the relevant notice | NER cll 3.15.7A–3.15.7B |
| 4 | Stress-test settlement and hedge liquidity under market suspension and APC scenarios, including June 2022 | NER rule 3.14 |
| 5 | Automate monitoring of LOR notices and define a response strategy | NER cl 4.8.4 |
| 6 | Confirm UFLS block membership and dynamic arming with the DNSP; SAPN in SA | NER cl 4.3.1; EFCS Rule 2017 |
| 7 | For new SA DER, support remote disconnection and Flexible Exports as EMS product requirements | SA Smarter Homes rules |
| 8 | On the retail side, monitor RRO triggers and maintain NCP reporting capability and a qualifying-contract register | NEL Part 2A; NER Chapter 4A |
| 9 | Maintain 24/7 emergency contacts and an immediate-report process under cl 4.8.1 | NER cl 4.8.1 |
| 10 | Assess the mid-2026 SRAS procurement window for a grid-forming BESS | SRAS Guideline; revised SRS 2025 |

## Official Source Bindings

| Key proposition | Governing document | Issuer / version | URL |
|---|---|---|---|
| Direction compliance and compensation framework | NEL ss 116 and 118; NER cll 4.8.9, 4.8.9A and 3.15.7 | AEMC, NER **v252**, published 2026-08-09 | https://energy-rules.aemc.gov.au/ner |
| Procedure for directions and instructions | SO_OP_3707 | AEMO, revised after 2024 consultation | https://www.aemo.com.au/-/media/files/electricity/nem/security_and_reliability/power_system_ops/procedures/so_op_3707-procedures-for-issue-of-directions-and-clause-4-8-9-instructions.pdf |
| APC, market suspension and compensation process | NER rule 3.14; AEMC compensation guidelines | AEMC | https://www.aemc.gov.au/our-work/compensation |
| 2026-27 market price cap, cumulative price threshold and administered price cap | Schedule of Reliability Settings for 2026-27 | AEMC, 2026-02-19 | https://www.aemc.gov.au/media/105056 |
| Direction additional-compensation filing period | NER cll 3.15.7A(f) and 3.15.7B | AEMC, current NER | https://energy-rules.aemc.gov.au/ner/175/24061 |
| June 2022 event and compliance review | AER June 2022 Market Events Report | AER, 2022-12-14 | https://www.aer.gov.au/system/files/AER%20June%202022%20Market%20Events%20Report-%20FINAL%20VERSION%20-%2014%20December%202022.pdf |
| June 2022 compensation, including the $148.8 million total | AEMO Compensation Update | AEMO, 2022-08-15; final amounts in later AEMO settlement notices | https://www.aemo.com.au/-/media/files/electricity/nem/data/mms/2022/compensation-update-15august22.pdf |
| RERT framework and 2025–26 position | NER rule 3.20; RERT Quarterly Reports | AEMO, Q1 2025 report issued 2025-05 | https://www.aemo.com.au/energy-systems/electricity/emergency-management/reliability-and-emergency-reserve-trader-rert |
| SRAS procurement and Guideline revision | SRAS Guideline; SRS Review Final Determination | AEMO / AEMC Reliability Panel, 2025-12-11 | https://www.aemo.com.au/energy-systems/electricity/national-electricity-market-nem/system-operations/ancillary-services/system-restart-ancillary-services-guideline |
| SRAS contract value and number | NMAS Report 2024–25 | AEMO, 2025-10 | https://www.aemo.com.au/-/media/files/electricity/nem/data/ancillary_services/2025/nmas-report-2024-25.pdf |
| LOR declaration framework and current criteria | NER cl 4.8.4; Reserve Level Declaration Guidelines v3.0 | AEMO, effective 2024-06-26 | https://www.aemo.com.au/-/media/files/electricity/nem/security_and_reliability/power_system_ops/reserve-level-declaration-guidelines.pdf |
| EFCS and UFLS obligations | EFCS Rule 2017; SA UFLS Dynamic Arming report | AEMC / AEMO, 2021-05 | https://www.aemo.com.au/-/media/files/initiatives/der/2021/south-australian-ufls-dynamic-arming.pdf |
| Emergency curtailment of DER in SA | Smarter Homes regulations; SAPN solar curtailment | SA Government / SAPN | https://www.sapowernetworks.com.au/your-power/quality-reliability/solar-curtailment-for-minimum-system-demand-events/ |
| Queensland Generation Signalling Device terminology | Emergency Backstop Mechanism | Energex | https://www.energex.com.au/our-services/connections/residential-and-commercial-connections/solar-connections-and-other-technologies/emergency-backstop-mechanism |
| 2016 black-system facts and remedial framework | Black System South Australia Final Report; AEMC South Australian Black System Review | AEMO, 2017-03 / AEMC, 2019 | https://www.aemo.com.au/-/media/files/electricity/nem/market_notices_and_events/power_system_incident_reports/2017/integrated-final-report-sa-black-system-28-september-2016.pdf |
| Black-system enforcement penalties | AER releases covering AGL $3.5 million, Pacific Hydro and Hornsdale above $1.6 million, and Snowtown 2 $1 million | AER, 2020-12 / 2021-07 | https://www.aer.gov.au/news/articles/news-releases/agl-pay-35-million-penalties-breaching-energy-rules |
| Indexed civil penalty tiers | NEL / National Electricity Regulations Schedule 1; AER indexation page | AER, values applying from 2026-07-01 | https://www.aer.gov.au/civil-and-criminal-penalty-indexation |
| RRO and MLO, including the NSW T-3 instrument for the 2025-12 to 2026-02 gap | NEL Part 2A; NER Chapter 4A; AER RRO and MLO pages | AER | https://www.aer.gov.au/industry/retail/reliability-obligation |
| Emergency management and jurisdictional coordination | NEM Emergency Management Fact Sheet; non-public PSEMP | AEMO | https://www.aemo.com.au/-/media/files/electricity/nem/emergency_management/factsheet-nem-emergency-management.pdf |
