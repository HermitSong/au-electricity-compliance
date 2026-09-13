---
country: Australia
category: compliance/emissions-reporting-and-scheme-obligations
domain: D10-gap
title: NGER Reporting, Safeguard Mechanism, LRET/LGC, CIS Contracts and GO/REGO Compliance
last_updated: 2026-08-27
status: draft-researched
audience: BESS developer / EMS vendor / retail-license applicant (NEM, SA/NSW/VIC)
sources:
  - NGER Act 2007 (Cth) — Clean Energy Regulator (CER)
  - National Greenhouse and Energy Reporting (Safeguard Mechanism) Rule 2015, as amended 2023 — DCCEEW
  - Renewable Energy (Electricity) Act 2000 (Cth) — CER
  - Future Made in Australia (Guarantee of Origin) Act 2024 — CER/DCCEEW
  - Capacity Investment Scheme Agreement (CISA) — DCCEEW
tags: [NGER, Safeguard-Mechanism, LRET, LGC, STC, CIS, CISA, REGO, Guarantee-of-Origin, Clean-Energy-Regulator, BESS, compliance]
---

# D10-gap: NGER Reporting and CIS Contract Compliance, Including Safeguard, LRET and GO Obligations

> **Purpose:** This page covers five Commonwealth measurement, reporting and contract-compliance regimes relevant to combined solar and storage portfolios: **NGER**, mandatory greenhouse-gas and energy reporting; the **Safeguard Mechanism**, which constrains large-emitting facilities but applies a special sectoral baseline to grid-connected electricity generation; **LRET/LGC**, the creation and surrender of renewable-energy certificates; **CIS/CISA**, the contractual obligations of successful Capacity Investment Scheme proponents; and **GO/REGO**, the successor provenance-certificate scheme launched in November 2025. The **Clean Energy Regulator (CER)** administers the statutory schemes. For CIS, the Commonwealth is the contracting party, **DCCEEW** administers the scheme and bodies such as AEMO Services conduct transactions.

## 1. Overview as of 2026-08-27

| Regime | Legal basis | Administrator | Application to a solar/BESS portfolio | Key figures |
|---|---|---|---|---|
| NGER reporting | National Greenhouse and Energy Reporting Act 2007 (Cth), the **NGER Act** | CER | **May apply:** a facility producing or consuming ≥100 TJ, or a corporate group producing or consuming ≥200 TJ, must report as detailed below | Facility thresholds: 25 kt CO2-e / 100 TJ; group thresholds: 50 kt CO2-e / 200 TJ; annual report due **31 October** and initial registration due **31 August** |
| Safeguard Mechanism | NGER Act Part 3H and Safeguard Mechanism Rule 2015, as amended by the 2023 reforms | CER; policy by DCCEEW | **No individual baseline:** grid-connected generating facilities use the sectoral baseline, and solar/BESS scope 1 emissions are far below 100 kt | Coverage at scope 1 emissions ≥100 kt CO2-e per year; general facility baselines decline **4.9% per year** to 2030; electricity-sector baseline **198 Mt CO2-e** |
| LRET / LGC | Renewable Energy (Electricity) Act 2000 (Cth), the **REE Act** | CER | **Applies:** a power station >100 kW must be accredited to create LGCs; a licensed retailer is a liable entity and must surrender certificates | Power-station threshold >100 kW; LGC shortfall charge **$65 per certificate**, non-deductible; a shortfall ≤10% may be carried forward; current LRET target 33,000 GWh to 2030 |
| CIS / CISA | Contractual scheme rather than dedicated legislation; each CISA is a legal contract between the Commonwealth and a project owner | DCCEEW; CER is not involved | **Contract-specific:** obligations and revenue-underwriting terms are those in the executed CISA and applicable tender documents | Current target **40 GW** by 2030, comprising 26 GW renewable generation and 14 GW clean dispatchable capacity; underwriting lasts 1–15 years |
| GO / REGO | Future Made in Australia (Guarantee of Origin) Act 2024 (Cth) and GO Rules 2025 | CER | **Optional registration:** an eligible storage facility can create certificates for dispatched electricity demonstrated to be renewable | Scheme launched **2025-11-03**; REGO continues beyond the end of LGC creation on **2030-12-31**; each REGO records when electricity was generated or dispatched |

---

## 2. NGER: Who Must Report for a Solar/BESS Portfolio

### 2.1 Thresholds under NGER Act ss 12–13

| Level | Scope 1 + 2 emissions | Energy **production** | Energy **consumption** |
|---|---|---|---|
| **Facility** | ≥25 kt CO2-e | ≥100 TJ | ≥100 TJ |
| **Corporate group** | ≥50 kt CO2-e | ≥200 TJ | ≥200 TJ |

**Essential conversion:** 100 TJ is approximately **27.78 GWh**, and 200 TJ is approximately **55.56 GWh**.

- **Individual solar farm:** annual generation above 27.78 GWh, approximately the output of a 13–15 MW AC solar farm at a typical capacity factor, triggers the facility threshold through energy production **even where emissions are close to zero**. NGER reports emissions and energy; zero emissions do not create an exemption.
- **BESS:** charging electricity is energy consumption and discharged electricity is production. The annual throughput of a 100 MW / 200 MWh BESS can readily exceed 100 TJ in each direction. A smaller 5 MW / 10 MWh BESS with annual throughput of approximately 3–4 GWh, or 11–14 TJ, is well below the single-facility threshold.
- **Portfolio level, especially important for this knowledge base's audience:** facilities controlled by the same **controlling corporation**, being the highest Australian holding company in the control chain, are aggregated. A portfolio whose combined production or consumption reaches 200 TJ, or 55.56 GWh, must register and report annually. **Operational control** determines who reports for a facility. For solar and BESS assets, this is generally the owner with authority over operating decisions; an O&M contractor ordinarily does not have operational control. A declaration may alter the outcome under NGER Act ss 11B–11C.
- **Retail-authorisation applicants:** NGER reporting is independent of AER retail authorisation. Electricity acquired by a retailer is, however, relevant to its separate liable-entity calculation under the REE Act; see Section 4.

**Deadlines:** after first crossing a threshold during a 1 July–30 June reporting year, register through the CER Client Portal by **31 August** and submit the annual report through the **Emissions and Energy Reporting System (EERS)** by **31 October**. Measurement methods are prescribed by the **NGER (Measurement) Determination 2008**, as updated for each reporting year.

### 2.2 CER audit and enforcement powers

- **Audit:** NGER Act Part 6 permits the CER to appoint a **registered greenhouse and energy auditor** to conduct a compliance audit. Auditor registration and professional requirements are set by the **NGER (Audit) Determination 2009**. The CER also conducts annual desktop reviews and data matching, including cross-checking reported generation against AEMO settlement data.
- **Record retention:** records supporting a report must be retained for **5 years** under NGER Act s 22.
- **Civil penalties:** failure to register or report attracts a maximum of **2,000 penalty units**, with additional daily penalties for a continuing contravention. The Commonwealth penalty unit was **$330** from 2024-11-07 and increased to **$364** from **2026-07-01** under Crimes Act 1914 s 4AA, making the maximum for a single failure approximately **$728,000**. The CER may also issue infringement notices, accept enforceable undertakings and publicly name the entity.
- **Enforcement example:** **Beach Energy Ltd**, an ASX-listed oil and gas company, made inaccurate statements in historical NGER reports following internal-control failures. On **2025-07-09**, the CER accepted an **enforceable undertaking** requiring Beach Energy to engage an external adviser to establish documented controls, strengthen data-collection processes and obtain an external **reasonable assurance audit** before submitting each of its next **three reporting-period** NGER reports. No monetary penalty was imposed, but the public enforcement record demonstrates substantial reputation risk for listed or prospective listed entities.

---

## 3. Safeguard Mechanism after the 2023 Reforms: Why Electricity Is Covered but Not Individually Constrained

- **Coverage threshold:** a facility with scope 1 emissions of at least **100 kt CO2-e per year** is a safeguard facility. Approximately 219 facilities are covered, representing about 28% of Australian emissions.
- **2023 reforms:** the Safeguard Mechanism (Crediting) Amendment Act 2023 and amended Safeguard Rule commenced on **2023-07-01**. Facility baselines generally decline by **4.9% per year** to 2030. A facility below its baseline may receive **Safeguard Mechanism Credits (SMCs)**; a facility above its baseline must surrender SMCs or ACCUs or otherwise resolve an excess-emissions situation.
- **Electricity-sector treatment:** all **grid-connected generating facilities** use the aggregate **198 Mt CO2-e sectoral electricity baseline** rather than individual baselines. Individual baselines are activated only if aggregate emissions from grid-connected generation exceed 198 Mt. Actual emissions have remained well below that level as coal generation retires, so the sectoral baseline has never been exceeded and is not expected to be exceeded. The 2023 reforms **did not change** this treatment of the electricity sector.
- **Conclusion for solar and BESS:** direct scope 1 emissions from solar and BESS facilities, such as backup diesel use or SF6 leakage, are several orders of magnitude below 100 kt. Even gas-fired peaking plant benefits from the sectoral-baseline treatment where it is grid connected. Off-grid generation, such as a mine-site power station, can be subject to an individual baseline. **No Safeguard action is ordinarily required**, but the independent NGER reporting obligation in Section 2 can still apply because NGER data underpins the Safeguard Mechanism.

---

## 4. LRET / LGC: Certificate Compliance for an Accredited Power Station

### 4.1 Certificate creation by generators

- **Current eligibility:** unless and until amending regulations commence, an eligible renewable power station above **100 kW** must obtain CER **accreditation** before it may create **LGCs**, while eligible solar systems no larger than 100 kW use the SRES/STC pathway. On **2026-08-05**, the Commonwealth announced an intended expansion for solar PV systems between 100 kW and 1 MW installed from **2026-10-01**, expressly **subject to regulations being in place**. The CER stated that commencement dates and detailed eligibility, design, installation and compliance requirements would be published before the change takes effect. Do not price or contract a 100 kW–1 MW project on STC eligibility until the regulations and CER implementation guidance are in force.
- **A BESS does not itself create LGCs.** Storage is not generation for LGC purposes. At a hybrid site, eligible solar generation may create LGCs, but charging and discharging losses must be correctly separated under the approved metering arrangement. Storage certificates are addressed through REGO in Section 6.
- **Ongoing obligations:** maintain metering and records under the **Renewable Energy (Electricity) Regulations 2001**. Certificate creation relies on metering data and is subject to CER audit, using the registered greenhouse and energy auditor framework for RET audits. False certificate creation may lead to civil and criminal liability. In **E Connect Solar & Electrical**, a Federal Court matter decided on 2023-09-13, the company and its current and former directors were ordered to pay combined civil penalties of **$240,000** for fraudulent STC conduct. Although it concerned the SRES, the case shows that the CER may pursue directors personally.

### 4.2 Certificate surrender by retailers

- A **liable entity**, principally an electricity retailer, calculates its LGC liability by multiplying wholesale acquisitions by the annual **Renewable Power Percentage (RPP)** set by regulation. It must lodge an energy acquisition statement and surrender the required certificates by **14 February** each year.
- A shortfall of **10% or less** may be carried forward and rectified in the next year. A larger shortfall attracts the **$65 per LGC** large-scale generation shortfall charge, which is **not tax deductible**, creating an after-tax equivalent cost of approximately $92.86 at a 30% corporate tax rate. The entity may seek a refund of the charge if it surrenders the corresponding LGCs within three years under REE Act ss 95–98.
- The LRET target remains 33,000 GWh to **2030**. The liable-entity surrender obligation and LGC regime then end as described in Section 6.

---

## 5. CIS / CISA: Contractual Obligations for Successful BESS Proponents

The CIS is not established by dedicated legislation. **Participant obligations arise under the executed Capacity Investment Scheme Agreement (CISA)** signed with the Commonwealth, represented by DCCEEW, and the documents for the relevant tender. The target was increased in July 2025 from 32 GW to **40 GW by 2030**, comprising 26 GW of renewable generation and 14 GW of clean dispatchable capacity. DCCEEW expressly states that CISA conditions are unique to the relevant contract; an older draft or a CISA from another tender must not be treated as a universal scheme rule.

| Obligation category | Requirement |
|---|---|
| **Revenue underwriting** | The floor, ceiling, revenue-sharing percentages, payment cadence, reconciliation mechanics and eligible-revenue definition must be taken from the executed CISA. The former 90% floor-support and 50% above-ceiling figures appeared in earlier public material but are not stated by DCCEEW as universal terms for every current CISA |
| **Availability and performance** | Use the performance, availability, dispatch and system-stress provisions in the relevant executed CISA. A universal LOR3 penalty or derating formula cannot be stated from current DCCEEW holder guidance |
| **Commercial structures** | Clause 15 of the applicable CISA is the authoritative source for whether a wholesale or bilateral contract is an Eligible Contract. DCCEEW's guidance assists self-assessment but does not approve or guarantee continuing eligibility |
| **Milestones** | The project owner reports against milestones until operation. DCCEEW identifies land tenure, planning and environmental approvals, a grid connection offer, financial close, construction and operation as milestone categories; dates and termination consequences remain contract-specific |
| **Reporting and payment start** | CISA holders report regularly through the CISA Management Portal. The project must be operational and generating revenue before underwriting support can be received |
| **Term** | Revenue underwriting lasts from 1 to **15 years**, as specified in the relevant CISA |

**SA, NSW and VIC:** CIS tenders and awards proceed in rounds and remain subject to execution of a CISA. The current DCCEEW tender pages must be checked for each project. **Commercial consequence:** a CISA changes merchant revenue exposure, but the amount and direction of that effect depend on the executed revenue-underwriting terms; no universal 50% upside-sharing assumption should be used in a financial model.

---

## 6. GO / REGO: Implementation in 2025–26 and the LGC Transition

- **Legislation:** the **Future Made in Australia (Guarantee of Origin) Act 2024 (Cth)**, related Charges Acts and the Future Made in Australia (Guarantee of Origin) Rules 2025 establish two product streams: **Product GO (PGO)**, initially for hydrogen and later for products such as green metals, and the **Renewable Electricity Guarantee of Origin (REGO)**.
- **Launch:** the CER announced that the GO scheme commenced on **2025-11-03**, after the original 2025-01-01 date was postponed twice. The 2025–26 period is the initial registration and certificate-creation ramp-up.
- **Relationship between REGO and LGC:** the two schemes operate in parallel for **five years**, through 2030. LGC creation and RET surrender obligations end on **2030-12-31**, after which REGO becomes the sole Commonwealth renewable-electricity attribute certificate. The same MWh cannot support both an LGC and a REGO; double counting is prohibited.
- **Three important changes for BESS:** 
  1. **Storage is eligible:** an eligible storage facility may create one REGO for each MWh of eligible renewable electricity it dispatches. The operator must demonstrate the renewable input through a qualifying direct-supply relationship, by surrendering LGCs or retiring upstream REGOs, or by a permitted combination of those methods.
  2. **Hourly timestamping:** each REGO identifies the **hour** of generation or discharge, with longer intervals available as an option. This supports 24/7 matching products and requires EMS and metering data capable of hourly aggregation.
  3. **Below-baseline certificates:** pre-1997 hydro and other below-baseline generation may create certificates, but retirement is **restricted** under GO Rules 2025 ss 52–53. That restriction ends on **2031-01-01**.
- **Compliance cost:** the CER operates the GO scheme on a cost-recovery basis, charging registration and certificate-creation fees set out in its GO cost-recovery material.
- **Storage calculation:** GO Rules ss 49–50 calculate the maximum eligible amount, conversion efficiency and the renewable electricity required for the claimed dispatch. Mixed or grid charging is supported only to the extent demonstrated by direct supply and/or surrendered or retired upstream certificates. The facility's measurement and certificate calculation method must comply with the GO Measurement Standard and be accepted through CER registration and certificate-creation processes. Storage losses therefore reduce the amount that can be supported by a given quantity of renewable input.

---

## 7. Penalties and Enforcement

| Contravention | Regime | Consequence | Authority / example |
|---|---|---|---|
| Failure to register or submit an NGER report on time | NGER | Civil penalty up to 2,000 penalty units, approximately **$728,000** at $364 per unit from 2026-07-01, plus daily penalties for a continuing contravention; infringement notice | NGER Act Part 5; Crimes Act 1914 s 4AA |
| Inaccurate NGER data, including an inadvertent misstatement | NGER | Enforceable undertaking, three reporting periods of external assurance and public naming | **Beach Energy enforceable undertaking, 2025-07-09**, CER |
| LGC shortfall greater than 10% | LRET | **$65 per LGC** shortfall charge, non-deductible, with an after-tax equivalent of approximately $92.86; refundable if corrected within three years | REE Act ss 95–98 |
| False creation of certificates | RET | Civil or criminal liability, including potential personal liability for directors | **E Connect Solar & Electrical**, Federal Court, 2023-09-13; combined penalties **$240,000** for the company and current and former directors |
| CISA breach | CIS | Contractual consequences, payment adjustments and termination rights are determined by the executed CISA; no universal LOR3 penalty or CP-sunset consequence is stated in current DCCEEW holder guidance | Executed CISA and applicable tender documents |
| Safeguard baseline exceedance, not ordinarily applicable to grid-connected generation | Safeguard | Excess-emissions situation requiring SMC or ACCU surrender and potentially a civil penalty | NGER Act Part 3H |

---

## 8. Official Source Bindings

| # | Key proposition | Governing document | Issuer / version | URL |
|---|---|---|---|---|
| 1 | NGER thresholds of 25 kt / 100 TJ for a facility and 50 kt / 200 TJ for a group; registration due 31 August and report due 31 October | NGER Act 2007 and CER "Assess your obligations" guidance | CER, current guidance for the 2025–26 reporting year | https://cer.gov.au/schemes/national-greenhouse-and-energy-reporting-scheme/assess-your-obligations |
| 2 | Five-year NGER record retention, audit and enforcement powers, and penalties | CER "Record keeping and compliance for greenhouse and energy reporting"; NGER Act Parts 5–6 | CER | https://cer.gov.au/schemes/national-greenhouse-and-energy-reporting-scheme/record-keeping-and-compliance-greenhouse-and-energy-reporting |
| 3 | NGER Act provisions, including ss 11–13, 19 and 22 and Parts 3H, 5 and 6 | National Greenhouse and Energy Reporting Act 2007 (Cth), current compilation | Federal Register of Legislation | https://www.legislation.gov.au/C2007A00175/latest |
| 4 | Beach Energy enforceable undertaking for inaccurate NGER reporting, 2025-07-09 | CER news release | CER, 2025-07 | https://cer.gov.au/news-and-media/news/2025/july/clean-energy-regulator-accepts-enforceable-undertaking-beach-energy |
| 5 | Safeguard reforms: 4.9% annual baseline decline, SMCs and unchanged 198 Mt electricity-sector baseline | Safeguard Mechanism reforms factsheet 2023 and DCCEEW overview | DCCEEW, 2023 reforms effective 2023-07-01 | https://www.dcceew.gov.au/sites/default/files/documents/safeguard-mechanism-reforms-factsheet-2023.pdf ; https://www.dcceew.gov.au/climate-change/emissions-reporting/national-greenhouse-energy-reporting-scheme/safeguard-mechanism/overview |
| 6 | Current 100 kW boundary and intended SRES expansion for 100 kW–1 MW solar installed from 2026-10-01, subject to regulations being in place | Expansion of solar PV eligibility under the SRES | CER, 2026-08-05 | https://cer.gov.au/news-and-media/news/2026/august/expansion-solar-photovoltaic-pv-eligibility-under-small-scale-renewable-energy-scheme |
| 7 | $65 LGC shortfall charge, 10% carry-forward and three-year refund | CER "Certificate shortfall"; REE Act 2000 ss 95–98 | CER | https://cer.gov.au/schemes/renewable-energy-target/renewable-energy-target-liability-and-exemptions/certificate-shortfall |
| 8 | E Connect Solar civil penalties of $240,000 on 2023-09-13 | CER Compliance Update, July–September 2023 | CER, 2023 | https://cer.gov.au/about-us/our-compliance-approach/compliance-and-enforcement-priorities/compliance-and-enforcement-priorities-2023-2024/compliance-update-1-july-30-september-2023 |
| 9 | Current 40 GW target, comprising 26 GW generation and 14 GW dispatchable capacity | Capacity Investment Scheme | DCCEEW, updated 2026-06-24 | https://www.dcceew.gov.au/energy/renewable/capacity-investment-scheme |
| 10 | Contract-specific CISA terms; milestone reporting, Management Portal, operational prerequisite and 1–15 year underwriting term | Information for CISA holders | DCCEEW, updated 2026-05-20 | https://www.dcceew.gov.au/energy/renewable/capacity-investment-scheme/open-cis-tenders/information-for-cisa-holders |
| 11 | Eligible-contract assessment is governed by the applicable CISA, including clause 15, and DCCEEW guidance is not approval | Guide to assessing eligible contracts under a CISA | DCCEEW, 2026 | https://www.dcceew.gov.au/sites/default/files/documents/guide-assessing-eligible-contracts-cisa.pdf |
| 12 | GO scheme launched on 2025-11-03 | CER news, "Guarantee of Origin Scheme launches" | CER, 2025-11 | https://cer.gov.au/news-and-media/news/2025/november/guarantee-origin-scheme-launches |
| 13 | Storage eligibility, direct supply and upstream-certificate requirements | Register and manage your facility; REGO Participant Handbook | CER, current | https://cer.gov.au/schemes/guarantee-origin-scheme/renewable-electricity-guarantee-origin/how-to-participate-rego/register-and-manage-your-facility ; https://cer.gov.au/document/renewable-electricity-guarantee-origin-participant-handbook |
| 14 | Storage maximum eligible amount, mixed-source calculation and loss treatment | GO Rules 2025 ss 49–50 | Federal Register of Legislation, F2025L01281 | https://www.legislation.gov.au/F2025L01281/asmade |
| 15 | Penalty unit increased from $330 to $364 on 2026-07-01 | Crimes (Amount of a Penalty Unit) Instrument 2026 | Federal Register of Legislation, F2026N00424 | https://www.legislation.gov.au/F2026N00424/asmade |
