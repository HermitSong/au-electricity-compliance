---
country: Australia
category: cybersecurity-compliance
domain: D11
last_updated: 2026-08-27
status: draft-researched
sources:
  - Security of Critical Infrastructure Act 2018 (Cth) (SOCI Act), as amended
  - Security Legislation Amendment (Critical Infrastructure Protection) Act 2022 (SLACIP)
  - Security of Critical Infrastructure and Other Legislation Amendment (Enhanced Response and Prevention) Act 2024 (No. 100, 2024)
  - Security of Critical Infrastructure (Critical infrastructure risk management program) Rules (LIN 23/006) 2023
  - Security of Critical Infrastructure Legislation Amendment (Enhanced Critical Infrastructure Risk Management Program) Rules 2026 (F2026L00701)
  - AEMO Australian Energy Sector Cyber Security Framework (AESCSF) 2025 Overview (June 2025)
  - Crimes Act 1914 (Cth) s 4AA (penalty unit)
tags: [SOCI, CIRMP, AESCSF, cyber, BESS, EMS, SCADA, ACSC, CISC, SoNS]
---

# D11 Cybersecurity Compliance — SOCI Act / CIRMP / AESCSF for the Electricity Industry

> **Intended audience:** BESS developers and operators, EMS/SCADA suppliers and retail-authorisation applicants in the NEM, with emphasis on SA, NSW and VIC. Legislative position as of **2026-08-27**.

## 1. Overview

| Item | Key requirement | Legal basis |
|---|---|---|
| Principal Act | Security of Critical Infrastructure Act 2018 (Cth), the SOCI Act, as amended by the SLACI Act 2021, SLACIP Act 2022 and Enhanced Response and Prevention Act 2024 | SOCI Act 2018 |
| Regulators | Cyber and Infrastructure Security Centre (CISC), Home Affairs; cyber incidents are reported to the Australian Cyber Security Centre (ACSC), ASD | SOCI Act Parts 2B and 3A |
| Critical electricity asset threshold | A transmission or distribution network, system or interconnector serving at least **100,000 customers**; or a generating station connected to a wholesale electricity market that either has installed capacity ≥30 MW or is operated by an entity contracted to provide SRAS | SOCI Act s 10; Definitions Rules (LIN 21/039) s 5 |
| Register obligation | Submit operational information and interest-and-control information to the Register of Critical Infrastructure Assets within the periods in SOCI Act ss 23–24 and keep it current | SOCI Act Part 2, ss 23–24 |
| Mandatory cyber-incident reporting | Report a **critical incident** with a significant impact on asset availability within **12 hours after awareness**, and another incident with a relevant impact within **72 hours**. If the initial report is oral, provide the approved written record within **84 hours after the oral 12-hour report** or **48 hours after the oral 72-hour report** | SOCI Act ss 30BC–30BD |
| CIRMP | Maintain a written Critical Infrastructure Risk Management Program addressing cyber, personnel, supply-chain and physical or natural hazards. Submit a **board-approved annual report within 90 days after the end of the financial year** | SOCI Act Part 2A and CIRMP Rules (LIN 23/006) |
| CIRMP cybersecurity frameworks under the 2023 Rules; transition ended 2024-08-17 | Adopt one of the recognised frameworks, including **AESCSF SP-1**, ISO 27001, ASD Essential Eight Maturity Level 1, NIST CSF, DOE C2M2 Maturity Level 1 or an equivalent framework | CIRMP Rules 2023 |
| **Enhanced CIRMP Rules 2026**, in force from 2026-06-10 | Instrument **F2026L00701** amends the consolidated CIRMP Rules. Recognised benchmarks are AS ISO/IEC 27001:2023, Essential Eight **ML2**, NIST CSF **2.0**, C2M2 v2.1 **MIL2**, or the 2023 AESCSF Core **SP-2**. Enhanced controls include phishing-resistant MFA, network segregation, supply-chain mapping, FOCI risk and personnel controls. If the CIRMP uses the AusCheck route for a person with ongoing access to critical components, the check must occur at least every five years | F2026L00701; consolidated CIRMP Rules F2026C00562 |
| Enhanced obligations for a System of National Significance | A declared SoNS must maintain an incident-response plan, conduct cybersecurity exercises and vulnerability assessments, and provide system information for a near-real-time threat picture. SoNS declarations are confidential | SOCI Act Part 2C and s 52B series |
| Government assistance and intervention powers | Part 3A provides last-resort information-gathering directions, action directions and intervention requests allowing ASD assistance. The 2024 amendments expanded these powers to all-hazards consequence management, rather than cyber incidents alone | SOCI Act Part 3A and 2024 Act |
| Penalty-unit basis | One penalty unit is **$364** from 2026-07-01. CIRMP adoption, compliance, review and update contraventions attract 200 penalty units; the annual-report contravention attracts 150; and incident-reporting contraventions attract 50. Regulatory Powers Act s 82(5) sets the body-corporate maximum at five times the specified civil penalty | SOCI Act ss 30AC–30AG, 30BC–30BD; F2026N00424; Regulatory Powers Act s 82(5) |

## 2. Obligations by Entity Type

### 2.1 BESS operator, 5–100 MW, in SA, NSW or VIC

- A BESS with **capacity ≥30 MW that is connected to the NEM wholesale market is a critical electricity asset** under the SOCI (Definitions) Rules. Its responsible entity must:
  1. Register the asset under Part 2 by submitting operational and interest-and-control information within six months after the asset becomes critical, and keep that information current.
  2. Report cyber incidents under Part 2B to the ACSC through ReportCyber within 12 or 72 hours as applicable. The scope includes incidents affecting OT systems such as the EMS, SCADA and BMS.
  3. Maintain a CIRMP under Part 2A. Critical electricity assets are among the asset classes subject to the Enhanced Rules. For an asset already critical when the instrument commenced, s 6A and ss 8A(2) and 9A(2) apply after the 12-month grace period ending **2027-06-10**; the remaining enhanced provisions apply after the 24-month grace period ending **2028-06-10**. The AESCSF SP-2 benchmark is in the latter group. The board-approved annual report remains due within 90 days after financial year end.
  4. Under the 2024 amendments, protect BESS-related **data storage systems** that hold business-critical data, including cloud-hosted historical, trading or dispatch data, as part of the asset.
- A BESS **below 30 MW**, such as a 5–29 MW facility, generally is **not** a critical electricity asset unless its owner or operator is contracted to provide SRAS and the station is wholesale-market connected. AEMO recommends that DER and CER entities, including batteries, VPPs, wind and solar farms and microgrids, use **AESCSF Lite** for self-assessment, and a customer operating a critical asset may flow CIRMP supply-chain controls down by contract. The Definitions Rules apply the 30 MW test to an electricity generation station; they do not state a portfolio-aggregation rule, so obtain CISC advice for a multi-unit or shared-site configuration that does not map cleanly to one station.
- An AER retail authorisation or a retailer's customer count does **not** itself make the retailer a critical electricity asset. The **100,000-customer threshold applies to an electricity transmission or distribution network, system or interconnector** under SOCI Act s 10. A retailer may nevertheless be affected as an operator or direct interest holder in another captured asset or as a supplier to a responsible entity.

### 2.2 EMS/SCADA supplier to a critical asset

The supplier is ordinarily not itself the responsible entity, but it must account for the following obligations:

1. A customer's CIRMP **supply-chain hazard** controls flow into supplier contracts through secure development, vulnerability management, incident-notification deadlines capable of supporting the customer's 12-hour report, and remote-access controls.
2. A commercial provider of data storage or processing services to critical-infrastructure customers may independently constitute a **critical data storage or processing asset**. ⚠️ Assess this under SOCI Act s 12F and the Definitions Rules.
3. Under the 2026 Enhanced Rules, personnel who access a customer's critical systems may need an **AusCheck** background check as critical workers, repeated every five years. Phishing-resistant MFA and network-segmentation requirements directly affect the EMS/SCADA product architecture.
4. Where the customer adopts AESCSF for its CIRMP, the supplier must produce evidence supporting SP-2 practices, including logs, asset inventories and OT network-segmentation capability.
5. The 2026 Rules expressly recognise FOCI risk. A supplier with foreign ownership or control should be ready to disclose its ownership structure and relevant influence arrangements.

### 2.3 AEMO and the AESCSF

- AEMO maintains the **Australian Energy Sector Cyber Security Framework**. It developed from **Version 1 in 2018 with 282 practices** to **Version 2, finalised in 2022 and introduced in 2023, with 354 practices across 11 domains**, based on US DOE C2M2 v2.1.
- The framework uses MIL-0 through MIL-3 and three Security Profiles: **SP-1 = 123 practices**, comprising all 62 MIL-1 practices plus selected MIL-2 and MIL-3 practices; **SP-2 = 275 practices**, including SP-1; and **SP-3 = all 354 practices**, equivalent to full MIL-3. A domain's lowest achieved MIL determines its domain rating. Every required practice must be achieved and relevant anti-patterns absent to attain a Security Profile.
- Participants in electricity generation, transmission, interconnection, distribution, retail and market operations are encouraged to participate. **DER/CER organisations**, including wind and solar farms, batteries, VPPs and microgrids, are encouraged to use **AESCSF Lite**.
- The **Electricity Criticality Assessment Tool (E-CAT)** uses E-GEN, E-TNSP, E-IC, E-DNSP, E-RET and E-OPS categories to establish a target Security Profile. AEMO expressly states that **E-CAT results do not correspond to the criticality parameters in the SOCI Act**; a high E-CAT rating does not itself create a SOCI obligation.
- AEMO conducts an annual self-assessment cycle and aggregates results in the "Security Preparedness of Australia's Energy Sector" report. Participation is voluntary for most entities. ⚠️ The exact annual assessment window was not confirmed in the source reviewed. Once an entity selects AESCSF as its CIRMP framework, however, the selected benchmark becomes a statutory compliance standard for that entity.

## 3. Thresholds and Deadlines

| Figure | Meaning |
|---|---|
| 30 MW plus wholesale-market connection | Threshold for a generating asset, including BESS, to be a critical electricity asset under the Definitions Rules |
| 12 hours / 72 hours | Deadlines for reporting critical and other relevant cyber incidents to the ACSC under Part 2B |
| 6 months | Grace period for registering a newly captured critical asset |
| 90 days | Deadline after financial year end for the board-approved CIRMP annual report |
| 2023-02-17 / 2023-08-17 / 2024-08-17 | CIRMP Rules commencement / deadline to establish a CIRMP / deadline to meet a recognised cybersecurity framework; **all have passed** |
| 2026-06-10 | Commencement of the Enhanced CIRMP Rules 2026 |
| 2027-06-10 / 2028-06-10 | For assets already critical at commencement, end of the respective 12-month grace period for s 6A and ss 8A(2), 9A(2), and 24-month grace period for the remaining enhanced provisions. A later-captured asset receives equivalent periods from the date it becomes critical |
| SP-1 = 123 / SP-2 = 275 / SP-3 = 354 | Number of practices in each AESCSF Version 2 Security Profile |
| $364 | Value of one Commonwealth penalty unit from 2026-07-01 under Crimes Act s 4AA, subject to CPI indexation every three years |

## 4. Penalties and Enforcement

- **CIRMP adoption, maintenance, compliance, review or update contravention:** **200 penalty units**, currently $72,800 for a person and a maximum of **$364,000 for a body corporate**.
- **CIRMP annual-report contravention:** **150 penalty units**, currently $54,600 for a person and a maximum of **$273,000 for a body corporate**.
- **Incident-reporting contravention:** **50 penalty units**, currently $18,200 for a person and a maximum of **$91,000 for a body corporate**. The same 50-unit amount attaches to failures concerning the approved written form or required written follow-up in ss 30BC and 30BD.
- These amounts use the $364 penalty unit from 2026-07-01 and the fivefold body-corporate maximum in Regulatory Powers Act s 82(5). No enacted 500-unit replacement for the core CIRMP provisions was identified in the current SOCI Act; the former proposal has therefore been removed.
- The 2024 Act also expanded all-hazards information-gathering and direction powers for consequence management beyond cyber incidents. Telecommunications moved from the TSSR framework into the SOCI regime under Schedule 5, commencing by proclamation on 2025-04-04.

## 5. Implementation Checklist for a BESS Developer and EMS Supplier

1. Before connection, assess each project ≥30 MW against the SOCI asset definition and register it within the statutory period. Retain a documented out-of-scope assessment for each project below 30 MW.
2. Embed the 12-hour and 72-hour ACSC reporting workflows and ReportCyber contact path in the EMS incident-response runbook.
3. If AESCSF is selected for a customer site, begin an SP-1 to SP-2 gap assessment immediately. The 2028-06 deadline requires evidence across 275 practices.
4. Add phishing-resistant MFA, OT/IT network segmentation, supply-chain mapping and SBOM management, and log retention to the EMS/SCADA product roadmap. These map directly to the Enhanced CIRMP Rules 2026.
5. Establish a board-level calendar for annual CIRMP attestation and submission within 90 days after financial year end.

## Official Source Bindings

| Key proposition | Governing document | Issuer / version | URL |
|---|---|---|---|
| Consolidated SOCI Act, including the 2024 amendments | Security of Critical Infrastructure Act 2018 (Cth) | Federal Register of Legislation, current compilation | https://www.legislation.gov.au/C2018A00029/latest |
| 2024 amendments covering data storage systems, consequence management and telecommunications; Schedules 1–4 and 6 commenced 2024-12-20 and Schedule 5 commenced 2025-04-04 | SOCI and Other Legislation Amendment (Enhanced Response and Prevention) Act 2024 (No. 100, 2024) | Federal Register of Legislation | https://www.legislation.gov.au/C2024A00100/asmade |
| Electricity thresholds: 100,000 customers for transmission/distribution assets; SRAS or installed capacity of at least 30 MW plus wholesale-market connection for a generation station | SOCI Act s 10; Security of Critical Infrastructure (Definitions) Rules (LIN 21/039) 2021 s 5 | Federal Register of Legislation, F2021L01769 / F2023C00097 | https://www.legislation.gov.au/F2021L01769/latest |
| CIRMP obligations, four hazard classes, recognised frameworks including AESCSF SP-1 and transition ending 2024-08-17 | Security of Critical Infrastructure (CIRMP) Rules (LIN 23/006) 2023 | Home Affairs, commenced 2023-02-17 | https://www.legislation.gov.au/F2023L00112/latest |
| Enhanced benchmarks, controls and 12/24-month grace periods | Security of Critical Infrastructure Legislation Amendment (Enhanced Critical Infrastructure Risk Management Program) Rules 2026 | Federal Register of Legislation, F2026L00701, in force from 2026-06-10 | https://www.legislation.gov.au/F2026L00701/asmade |
| Current consolidated CIRMP Rules after the 2026 amendments | Security of Critical Infrastructure (Critical infrastructure risk management program) Rules (LIN 23/006) 2023 | Federal Register of Legislation, F2026C00562 C02, compilation date 2026-06-10 | https://www.legislation.gov.au/F2023L00112/latest |
| 12-hour and 72-hour reports, 84-hour and 48-hour oral-report follow-ups, and 50-unit civil penalties | SOCI Act ss 30BC–30BD | Federal Register of Legislation, current Act compilation | https://www.legislation.gov.au/C2018A00029/latest |
| Four Enhanced Cyber Security Obligations for a SoNS | CISC Factsheet — Systems of National Significance and ECSO | CISC | https://www.cisc.gov.au/resources-subsite/Documents/cisc-factsheet-systems-of-national-significance-enhanced-cyber-security-obligations.pdf |
| AESCSF Version 1 and 2 structure, MILs, practice counts for SP-1/2/3, E-CAT, AESCSF Lite and relationship to SOCI | AESCSF Overview 2025 | AEMO, June 2025 | https://www.aemo.com.au/-/media/files/initiatives/cyber-security/aescsf/guidance-materials/aescsf-2025-overview.pdf |
| Guidance for low-criticality organisations | AESCSF Guidance Material for Low Criticality Organisations | AEMO | https://www.aemo.com.au/-/media/files/initiatives/cyber-security/aescsf/2023/aescsf-guidance-material-for-low-criticality-organisations.pdf |
| Penalty unit of $364 from 2026-07-01 | Crimes (Amount of a Penalty Unit) Instrument 2026 | Federal Register of Legislation, F2026N00424 | https://www.legislation.gov.au/F2026N00424/asmade |
| Fivefold body-corporate maximum for civil penalty provisions | Regulatory Powers (Standard Provisions) Act 2014 s 82(5) | Federal Register of Legislation | https://www.legislation.gov.au/C2014A00093/latest |
