---
country: Australia
category: DER-technical-standards
page: D05-gap
title: "AS/NZS 4777.2:2020 and Dynamic Export / CSIP-AUS Compliance"
last_updated: 2026-08-27
status: draft-researched
sources:
  - Clean Energy Regulator — Changes to Inverter Standard AS/NZS 4777.2:2020
  - Clean Energy Council — Approved Inverters / 4777.2 standards change
  - Energy Networks Australia — Power Quality Response Mode Settings / FAQ
  - SA Power Networks — Flexible Exports
  - SA Dept for Energy & Mining — Smarter Homes / Dynamic Exports
  - Energy VIC — Emergency Backstop Mechanism
  - Energex/Ergon — Emergency Backstop Mechanism (QLD)
  - AEMO — AS/NZS 4777.2 Inverter Requirements standard
tags: [AS4777, CSIP-AUS, IEEE-2030.5, dynamic-exports, flexible-exports, emergency-backstop, Smarter-Homes, DER, inverter, DNSP, GPS]
---

# AS/NZS 4777.2:2020 and Dynamic Export / CSIP-AUS Compliance (as of 2026-08-27)

> **Intended audience:** BESS developers, EMS/SCADA vendors and retail-authorisation applicants operating in the NEM, with emphasis on SA, NSW and VIC. This page covers the inverter product standard AS/NZS 4777.2:2020 and Amendment 2:2024; mandatory state-level DER connection requirements, including SA Smarter Homes and dynamic exports and emergency backstops in VIC, QLD and NSW; the DNSP implementation status of CSIP-AUS (IEEE 2030.5) client requirements; and the boundary between this framework and the standards applicable to utility-scale projects above 200 kVA.

## 1. Overview

| Item | Key requirement | Effective date | Governing document / body |
|---|---|---|---|
| Inverter product standard | AS/NZS 4777.2:2020 replaced the 2015 edition and provides four regional settings: Australia A, Australia B, Australia C and New Zealand | Mandatory from **2021-12-18**, when the NER amendment commenced | Standards Australia; NER; CER/CEC |
| Latest amendment | **AS/NZS 4777.2:2020 Amd 2:2024**, published in August 2024 with a 12-month transition period; from **2025-08-23**, the CEC accepts only product applications that comply with Amendment 2 | 2025-08-23 | Standards Australia; Clean Energy Council |
| Approved-product list | An inverter must appear on the CEC approved inverter list and be identified as 2020-compliant; otherwise, it is ineligible for STCs and the DNSP may refuse connection | From 2021-12-18 | Clean Energy Council; CER (SRES) |
| SA Smarter Homes | New or upgraded solar installations must nominate a **Relevant Agent** and support remote disconnection and reconnection | 2020-09-28 | Electricity (General) Regulations 2012 (SA), as amended for Smarter Homes; DEM SA |
| SA dynamic exports | Every new application for an exporting generating system must be **dynamic-export capable through CSIP-AUS** | **2023-07-01** | SA Government Dynamic Export Requirements; SAPN Flexible Exports |
| QLD emergency backstop | New or replacement IES installations with aggregate capacity ≥10 kVA must install a **Generation Signalling Device (GSD)** or use a CSIP-AUS Dynamic Connection | 2023-02-06 | QLD Emergency Backstop Mechanism; Energex STNW3511 / Ergon |
| VIC emergency backstop | New, upgraded or replacement rooftop solar must be emergency-backstop enabled; systems ≤30 kVA use CSIP-AUS and an internet connection, and Stage 2 extends the framework to systems ≤200 kW | Stage 2: **2024-10-01** | Energy VIC — Victoria's Emergency Backstop Mechanism |
| NSW emergency backstop | Requirements will be introduced gradually from **late 2026**. New and upgraded rooftop solar systems up to and including 200 kW must be backstop enabled, use CSIP-AUS-compliant inverters and be registered through the NSW CER Installer Portal. Existing unchanged systems are not captured | Staged from late 2026 | NSW Government / NSW DNSPs |
| Utility-scale boundary | The AS/NZS 4777 framework applies to IES installations **≤200 kVA**; larger generating systems are governed by NER Chapter 5 and **Generator Performance Standards (GPS), Schedule S5.2** | — | NER Chapter 5 / AEMO / relevant NSP |

## 2. Core AS/NZS 4777.2:2020 Obligations

### 2.1 Scope and mandatory application

- The standard applies to inverter energy systems (IES) that inject power into a distribution network through an electrical installation, with a unit or system capacity **≤200 kVA**. See Section 6 for larger systems.
- From **2021-12-18**, when the NER amendment commenced, every newly connected inverter had to comply with AS/NZS 4777.2:2020 and appear on the CEC approved inverter list with a 2020-compliance designation. Inverters certified only to the 2015 edition ceased to be eligible for STCs when installed from that date. (CER announcement, December 2021.)
- **Amendment 2:2024**, published in August 2024, added requirements for Mode 3 and Mode 4 bidirectional EV charging (V2G) and replaced terminology such as "stand-alone" with "island supply". Following a 12-month transition period, from **2025-08-23** the CEC accepts Amendment 2 certification, or 2020 certification supported by a manufacturer declaration and regional-setting evidence, for relevant product applications.

### 2.2 Regional settings

| Region | Intended system | Practical use |
|---|---|---|
| **Australia A** | Networks specified by ENA | Ausgrid, AusNet Services, Endeavour Energy, Essential Energy, Energex and Ergon Energy, Evoenergy, Jemena, CitiPower, Powercor, United Energy, SA Power Networks and applicable Power and Water networks |
| **Australia B** | Network specified by ENA | Western Power |
| **Australia C** | Networks specified by ENA | Horizon Power, TasNetworks and applicable Power and Water networks |
| **New Zealand** | New Zealand distribution networks | New Zealand |

The regional setting is selected by the connecting DNSP, not by a generic mainland-versus-remote rule. Power and Water appears in both Australia A and Australia C in ENA's mapping because the applicable setting depends on the relevant network.

### 2.3 Key settings, using Australia A as the example

- **Volt-VAR, enabled by default:** V1 = 207 V, exporting reactive power at +44% of rated VA; reactive power is zero between V2 = 220 V and V3 = 240 V; and V4 = 258 V, absorbing reactive power at −60%. See Standard Table 3.7. Australia B, Australia C and New Zealand use different V1–V4 values and reactive-power percentages. ⚠️ Use the standard itself for the exact values.
- **Volt-Watt, enabled by default:** in Australia A, linear active-power reduction begins at 253 V and reaches 20% of rated power at 260 V.
- **Frequency response and ride-through:** the approximate continuous operating frequency range for Australia A is **47.0–52.0 Hz**, with lower and upper `f_stop` limits of 47 Hz and 52 Hz. Over-frequency active-power reduction begins at approximately 50.25 Hz according to the applicable droop; for storage, under-frequency response begins at approximately 49.75 Hz by reducing charging or increasing discharge. The New Zealand region uses a wider 45–55 Hz ride-through band. ⚠️ The complete regional ride-through tables, including voltage-versus-time curves, have not been verified item by item here; consult AS/NZS 4777.2:2020 Section 4.
- **Voltage and frequency protection settings:** both passive and active anti-islanding protection are required. Voltage and frequency protection limits and trip times must follow the selected regional tables and must not be changed in the field without written NSP approval.
- **Low-voltage ride-through (LVRT):** SA Smarter Homes separately requires inverters installed in South Australia to support LVRT and appear on the relevant approved-product list from 2020-09-28.

**Implications for EMS/SCADA vendors:** lock and evidence the regional setting during commissioning; Victorian installers must upload setting photographs or declarations. An EMS must not issue controls that override AS/NZS 4777.2 protection settings. CSIP-AUS dynamic limits operate in parallel with the inverter's local Volt-Watt and Volt-VAR responses.

## 3. Mandatory State-Level DER Connection Requirements

### 3.1 South Australia — Smarter Homes and dynamic exports

- From **2020-09-28**, under the Smarter Homes amendments to the Electricity (General) Regulations 2012 (SA), every new or upgraded solar installation must: (a) nominate a **Relevant Agent** capable of executing remote disconnect and reconnect directions from an Authorised Party during a state electricity-security emergency; (b) use an inverter with internet communications capability and a communications port; and (c) use an inverter on the South Australian approved-product list, including the applicable LVRT requirement.
- From **2023-07-01**, under the SA Government Dynamic Export Requirements, every new application for an exporting system must be **dynamic-export capable through CSIP-AUS** and compatible with SAPN's **Flexible Exports** connection option. In eligible areas, that option permits export under a dynamic envelope of up to **10 kW per phase**, replacing the former fixed limit of 1.5 kW per phase. SAPN rolled the service out progressively, made it available statewide from **2024-07-01**, and reported that more than 85% of new customers selected the flexible option during business-as-usual operation.
- During a minimum-system-load emergency, AEMO and SAPN retain the capability to curtail rooftop solar to zero export through the Relevant Agent or flexible-export channel. This is South Australia's solar switch-off or emergency-curtailment mechanism.

### 3.2 Queensland — Emergency Backstop from 2023-02-06

- For IES connection offers accepted from 2023-02-06, a new or replacement IES, including combined solar and battery capacity, with aggregate capacity **≥10 kVA** must install a **Generation Signalling Device (GSD)** using an audio-frequency load-control signal or use a **CSIP-AUS** Dynamic Connection under Energex/Ergon standard STNW3511.
- A GSD depends on AFLC coverage. Separate arrangements apply in Ergon isolated communities, SWER networks and other locations without AFLC coverage.

### 3.3 Victoria — Expanded Emergency Backstop in 2024

- All new, upgraded and replacement rooftop solar systems must be **emergency-backstop enabled**, allowing remote curtailment or shutdown during a minimum-system-load emergency.
- Systems ≤30 kVA must support **CSIP-AUS** and maintain an internet connection. **Stage 2, from 2024-10-01**, extended the requirement to new systems ≤200 kW and to existing systems whose inverter is replaced after 2024-10-01, other than like-for-like or warranty replacements. Victoria's five DNSPs — AusNet, CitiPower/Powercor, Jemena and United Energy — implement the Energy VIC guidance.

### 3.4 NSW — Emergency Backstop Rollout from Late 2026

- The NSW Government states that the mechanism will be introduced gradually from **late 2026**. No official statewide LGA/postcode timetable supporting a June 2026 start or October–December 2026 completion was identified, so those dates have been removed.
- New and upgraded rooftop solar inverter systems up to and including **200 kW** must be backstop enabled, use CSIP-AUS-compliant inverters and be registered with the relevant DNSP utility server through the NSW CER Installer Portal. Existing systems that are not changed are not affected.
- A hybrid battery connected to the solar system is within the published scope; adding only an AC-coupled battery is not. The NSW factsheet also states that systems above 200 kW must be backstop enabled, with the DNSP determining whether CSIP-AUS or another control solution is appropriate.
- Flexible exports are a related network connection product, not the emergency backstop itself. Essential Energy describes flexible exports for eligible new or upgraded systems up to 200 kW from late 2026 as an option alongside a lower fixed export limit. Endeavour Energy also describes its flexible-export transition as commencing from late 2026. The project must use the applicable DNSP connection offer rather than infer a single statewide commercial export limit.

## 4. CSIP-AUS / IEEE 2030.5 Client Requirements — DNSP Implementation Status as of 2026-08

CSIP-AUS, the Common Smart Inverter Profile — Australia maintained by the DER Integration API Technical Working Group at csipaus.org, is Australia's implementation guide for **IEEE 2030.5**. An inverter or gateway operates as a client and retrieves DER controls, such as the `opModExpLimW` export limit, and emergency-backstop instructions from a DNSP utility server.

| DNSP | Jurisdiction | Status as of 2026-08 |
|---|---|---|
| **SAPN** | SA | **Business as usual:** new connections have had to be dynamic-export capable since 2023-07; Flexible Exports has been available statewide since 2024-07, with a dynamic envelope up to 10 kW per phase |
| **Energex / Ergon** | QLD | **Business as usual:** from 2023-02, systems ≥10 kVA must use either a CSIP-AUS Dynamic Connection or a GSD |
| Victoria's five DNSPs | VIC | CSIP-AUS is mandatory for emergency-backstop purposes: systems ≤30 kVA from 2024 and Stage 2 systems ≤200 kW from 2024-10; commercial flexible-export deployment remains in progress |
| **Ausgrid** | NSW | NSW's staged backstop requirements apply from late 2026; use Ausgrid's current connection offer and installer instructions for the site |
| **Endeavour Energy** | NSW | Flexible exports and the NSW backstop transition are described as commencing from late 2026; the earlier July 2026 default date is not supported by the current official material |
| **Essential Energy** | NSW | An eligible new or upgraded system up to 200 kW may choose a flexible export connection from late 2026 or a lower fixed export limit; the backstop registration requirement is separate |
| Western Power / Horizon Power | WA, outside the NEM | WA has separate Emergency Solar Management arrangements. ⚠️ Details have not been verified for this page |

**Engineering requirements for EMS/SCADA vendors:** implement an IEEE 2030.5/CSIP-AUS client with mutual TLS authentication, device registration, DERControl event scheduling, a default-limit fallback and DNSP-specific loss-of-communications behaviour, generally reverting to a conservative static limit or zero export as required by the relevant handbook. Each DNSP maintains its own conformance or rebadged-device testing list; SAPN, Energex and the Victorian emergency-backstop schemes publish compatible-device lists.

## 5. Consequences of Non-Compliance and Enforcement Practice

- **Loss of STC eligibility:** installation of an inverter that is not on the CEC approved list with the required 2020 or Amendment 2 compliance status is ineligible for SRES STCs. This is a direct economic consequence for residential and small commercial projects.
- **Connection refusal:** a DNSP may refuse a connection application that does not meet CSIP-AUS, GSD or emergency-backstop requirements. Victoria and Queensland make emergency-backstop compliance a connection condition, while South Australia does not permit connection without a Relevant Agent.
- **South Australian enforcement:** the SA Technical Regulator oversees compliance with the Smarter Homes requirements and may issue rectification directions for non-compliant installations. A Relevant Agent's failure to execute a curtailment instruction may breach obligations under the Electricity Act 1996 (SA). ⚠️ No major published monetary penalty specifically for inverter-standard non-compliance was identified when this page was prepared; enforcement is generally through delisting, rectification and connection refusal.
- **CEC delisting:** the CEC may remove products that fail Amendment 2:2024 requirements or involve falsified testing from the approved list. Delisting has occurred historically and effectively prevents national sale into the accredited market.

## 6. Utility-Scale Boundary — Essential Reading for BESS Developers

- The **AS/NZS 4777 framework — AS/NZS 4777.1:2024 for installation and AS/NZS 4777.2:2020 for products — applies only to IES installations ≤200 kVA**. An inverter above that threshold, or one connected directly at high voltage, does not use the AS/NZS 4777.2 regional-setting or CEC-listing framework.
- For systems **>200 kVA**, including a typical grid-scale BESS such as 5 MW / 10 MWh, connection and performance are governed by **NER Chapter 5**. The proponent negotiates **Generator Performance Standards under NER Schedule S5.2** with the NSP and AEMO, using automatic, elective or negotiated access standards. These cover fault ride-through at S5.2.5.3–S5.2.5.5, reactive-power capability at S5.2.5.1, voltage and frequency control at S5.2.5.11, S5.2.5.13 and S5.2.5.14, and remote SCADA monitoring at S5.2.6.1. A unit ≥5 MW registers with AEMO as a Generator; following the 2024 IRP reforms, the Integrated Resource Provider category applies to BESS.
- For the intermediate range of **200 kVA–5 MW connected to a low- or high-voltage distribution network**, use the DNSP's embedded-generation connection standard, such as Energex STNW1175 for high-voltage connections rather than AS/NZS 4777.1. NER Chapter 5A or 5.3A processes and DNSP technical standards apply. These may reference AS/NZS 4777.2 capabilities, but the DNSP's specific power-quality response requirements govern.
- **Practical note:** central utility inverters used in projects of approximately 2.5–5 MW, such as the Sungrow SG3125HV, do not fall within the CEC AS/NZS 4777.2 listing framework. Their compliance anchors are the GPS and connection agreement negotiated with the DNSP and AEMO, not CSIP-AUS. An EMS that also serves commercial rooftop assets below 200 kVA must implement CSIP-AUS in parallel.

## 7. Official Source Bindings

| Key proposition | Governing document | Issuer / version | URL |
|---|---|---|---|
| AS/NZS 4777.2:2020 became mandatory from 2021-12-18 under the NER amendment, and 2015-certified inverters lost STC eligibility | Changes to Inverter Standard AS/NZS 4777.2:2020 | Clean Energy Regulator, 2021-12 | https://cer.gov.au/changes-inverter-standard-asnzs-477722020 |
| Full standard, including Australia A/B/C/NZ regional settings and Volt-VAR, Volt-Watt and ride-through tables | AS/NZS 4777.2:2020 (+ Amd 2:2024) | Standards Australia | https://store.standards.org.au/product/as-nzs-4777-2-2020 |
| Amendment 2:2024 transition and CEC acceptance of Amendment 2 products from 2025-08-23 | 4777.2 standards change and product listings | Clean Energy Council | https://cleanenergycouncil.org.au/industry-programs/products-program/inverters/standards-change |
| CEC approved inverter list with 2020-compliance designation | Approved inverters list | Clean Energy Council, continuously updated | https://cleanenergycouncil.org.au/industry-programs/products-program/inverters/approved-inverters-that-meet-the-updated-inverter-standard |
| Exact DNSP mapping for Australia A, B and C regional settings | FAQ: Changes to Inverter Standards AS/NZS 4777.2 | Energy Networks Australia, Amd 2:2024 implementation | https://www.energynetworks.com.au/assets/uploads/FAQ-Changes-to-Inverter-Standards-ASNZS4777.2.pdf |
| AEMO's system-security treatment of AS/NZS 4777.2 | AS/NZS 4777.2 — Inverter Requirements standard | AEMO DER Program | https://www.aemo.com.au/initiatives/major-programs/nem-distributed-energy-resources-der-program/standards-and-connections/as-nzs-4777-2-inverter-requirements-standard |
| SA Smarter Homes Relevant Agent and remote-disconnection requirements from 2020-09-28 | Regulatory Changes for Smarter Homes | SA Department for Energy and Mining | https://energymining.sa.gov.au/industry/hydrogen-and-renewable-energy/solar-batteries-and-smarter-homes/regulatory-changes-for-smarter-homes |
| Mandatory dynamic-export capability through CSIP-AUS from 2023-07-01 | Dynamic Exports fact sheet / Q&A | SA DEM, 2023-11 | https://www.energymining.sa.gov.au/__data/assets/pdf_file/0007/923326/Dynamic_Exports_fact_sheet_Industry_23-Nov-2023.pdf |
| SAPN Flexible Exports at 10 kW per phase and statewide availability from 2024-07 | Solar Flexible Exports | SA Power Networks | https://www.sapowernetworks.com.au/industry/flexible-exports/ |
| Victorian emergency backstop, Stage 2 from 2024-10-01 for systems ≤200 kW using CSIP-AUS | Requirements for distributed solar — Victoria's emergency backstop mechanism | Energy VIC (DEECA) | https://www.energy.vic.gov.au/about-energy/victorias-emergency-backstop-mechanism-for-solar |
| Queensland emergency backstop from 2023-02-06 using a GSD or CSIP-AUS for systems ≥10 kVA | Emergency backstop mechanism | Energex / Ergon / Queensland Treasury | https://www.energex.com.au/our-services/connections/residential-and-commercial-connections/solar-connections-and-other-technologies/emergency-backstop-mechanism |
| Queensland Dynamic Connection technical requirements | STNW3511 Dynamic Standard for LV EG Connections | Energex / Ergon | https://energex.com.au/__data/assets/pdf_file/0003/1089111/STNW3511-Dynamic-Standard-for-Low-Voltage-EG-Connections.pdf |
| CSIP-AUS specification owner | CSIP-AUS, the Australian implementation guide for IEEE 2030.5 | DER Integration API Technical Working Group | https://www.csipaus.org/about |
| NSW backstop rollout from late 2026; scope for new and upgraded systems up to and including 200 kW; CSIP-AUS and CER Installer Portal registration; treatment of existing systems and batteries | NSW Emergency Backstop Mechanism and implementation factsheet | NSW Government, current 2026 guidance | https://www.energy.nsw.gov.au/households/action/initiatives/emergency-backstop ; https://www.energy.nsw.gov.au/sites/default/files/2026-03/Preparing-for-the-NSW-Emergency-BackstopMechanism_Factsheet_2026.pdf |
| Essential Energy flexible-export option for eligible new and upgraded systems up to 200 kW from late 2026 | Flexible Exports | Essential Energy | https://www.essentialenergy.com.au/our-network/flexible-exports |
| Endeavour Energy flexible-export transition from late 2026 | Flexible Exports | Endeavour Energy | https://www.endeavourenergy.com.au/For-your-home/Solar-and-battery-options/Flexible-exports |
| Systems >200 kVA use the GPS framework | National Electricity Rules Chapter 5, Schedule S5.2 | AEMC, current NER | https://energy-rules.aemc.gov.au/ner |

**Disclaimer and boundary:** Exact Volt-VAR values, complete regional ride-through tables and site-specific connection settings must be taken from the licensed AS/NZS 4777.2 text and the current DNSP connection offer. The NSW Government has not published a single statewide postcode timetable in the official material cited above; project scheduling should therefore use the current NSW portal and relevant DNSP notices.
