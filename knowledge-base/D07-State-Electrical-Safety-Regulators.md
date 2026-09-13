---
country: Australia
category: electrical-safety-regulators-and-licensing
domain: D07
title: State and Territory Electrical Safety Regulators
last_updated: 2026-08-27
status: draft-researched
audience: BESS developers, generation owners, EMS vendors, EPC contractors, and retail licence applicants
primary_sources:
  - SA Electricity Act 1996 and Electricity (General) Regulations 2012
  - VIC Electricity Safety Act 1998 and Electricity Safety (General) Regulations 2019
  - NSW Gas and Electricity (Consumer Safety) Act 2017 and Home Building Act 1989
  - QLD Electrical Safety Act 2002
  - WA Electricity Act 1945, Electricity (Licensing) Regulations 1991, and Electricity (Network Safety) Regulations 2015
  - TAS Electricity Industry Safety and Administration Act 1997, Occupational Licensing Act 2005, and Electricity Safety Act 2022 commencement framework
  - ACT Electricity Safety Act 1971 and Construction Occupations (Licensing) Act 2004
  - NT Electrical Workers and Contractors Act 1978
tags: [electrical-safety, licensing, ESV, OTR, NSW-Fair-Trading, ESO, Building-and-Energy, CBOS, Access-Canberra, NT-WorkSafe, COES, CCEW, eCoC, BESS, ESMS]
---

# D07 - State and Territory Electrical Safety Regulators

Electrical safety and electrical occupational licensing are state and territory regimes. They are not created by the National Electricity Law, the National Energy Retail Law, or AEMO registration. A BESS developer, EMS vendor, solar EPC, or retailer with field staff must map the electrical safety law of the state where the work is performed.

## 1. Eight-jurisdiction regulator map

| Jurisdiction | Electrical safety regulator | Electrical worker / contractor licensing | Core legislation | Electrical completion certificate or equivalent | Practical distinction |
|---|---|---|---|---|---|
| ACT | Access Canberra | Access Canberra | Electricity Safety Act 1971 (ACT); Construction Occupations (Licensing) Act 2004 (ACT) | Certificate and inspection requirements under ACT construction/electrical licensing framework | Small jurisdiction integrated with construction occupations licensing. Confirm current certificate forms before site work. |
| NSW | Building Commission NSW / NSW Fair Trading for consumer electrical installation safety; SafeWork NSW for workplace electrical risks | NSW Fair Trading / Building Commission NSW | Gas and Electricity (Consumer Safety) Act 2017 (NSW); Gas and Electricity (Consumer Safety) Regulation 2018; Home Building Act 1989 (NSW) | Certificate of Compliance for Electrical Work (CCEW), generally submitted within 7 days after safety and compliance testing | NSW separates consumer installation safety from WHS notification. CCEW control is central for embedded networks, solar, and BESS installation work. |
| NT | NT WorkSafe and the Electrical Workers and Contractors Licensing Board | Electrical Workers and Contractors Licensing Board / NT WorkSafe | Electrical Workers and Contractors Act 1978 (NT); Electricity Reform Act 2000 (NT) for broader supply framework | NT electrical safety certificate requirements must be confirmed for the work class | NT combines a small-market licensing board model with separate electricity supply legislation. Verify forms and exemptions project by project. |
| QLD | Electrical Safety Office (ESO), Office of Industrial Relations; prosecutions by the Office of the Work Health and Safety Prosecutor | ESO | Electrical Safety Act 2002 (Qld); Electrical Safety Regulation 2013 | Certificate of testing and safety/compliance documentation under QLD electrical safety regulation | Queensland has Australia's clearest standalone electrical safety statute, parallel to WHS law. It is also outside automatic mutual recognition for many occupational licences. |
| SA | Office of the Technical Regulator (OTR), Department for Energy and Mining | Consumer and Business Services (CBS) for electrical worker registration and contractor licensing | Electricity Act 1996 (SA); Electricity (General) Regulations 2012; Plumbers, Gas Fitters and Electricians Act 1995 (SA) | Electronic Certificate of Compliance (eCoC), issued before energisation and submitted within the required period | OTR is deeply involved in generation infrastructure technical regulation and commissioning. BESS schedules must allow for OTR/SAPN witnessing where required. |
| TAS | Consumer, Building and Occupational Services (CBOS), Department of Justice | CBOS | Electricity Industry Safety and Administration Act 1997 (Tas), currently in force; Occupational Licensing Act 2005 (Tas); Occupational Licensing (Electrical Work) Regulations 2018; Electricity Safety Act 2022 (Tas), subject to proclamation commencement | Certificate of electrical compliance under the occupational licensing framework | Do not treat the 2022 Act as operative until the relevant commencement proclamation is confirmed. The 1997 Act remains the current electricity-industry safety statute at this baseline. |
| VIC | Energy Safe Victoria (ESV) | ESV: licensed electricians, registered electrical contractors, licensed electrical inspectors | Electricity Safety Act 1998 (Vic); Electricity Safety (General) Regulations 2019; Electricity Safety (Management) Regulations 2019 | Certificate of Electrical Safety (COES), submitted through ESVConnect; prescribed electrical installation work requires licensed electrical inspector involvement | Victoria has strong ESV enforcement, complex electrical installation duties, bushfire mitigation controls, and ESMS pathways. |
| WA | Building and Energy, Department of Local Government, Industry Regulation and Safety; statutory role of Director of Energy Safety | Building and Energy | Electricity Act 1945 (WA); Electricity (Licensing) Regulations 1991; Electricity (Network Safety) Regulations 2015 | Notice of Completion and Electrical Safety Certificate under licensing regulations | WA uses a Director of Energy Safety model and has separate network safety incident reporting obligations. |

## 2. Actor-based obligations

Most jurisdictions distinguish between an individual worker, practitioner, or electrician licence and an electrical contractor licence or registered electrical contractor status. For BESS and solar projects, contract review should verify both levels. A licensed electrician employed by an unlicensed contractor does not automatically cure the contractor licensing issue.

Key state distinctions:

- NSW: electrical wiring work must be carried out by appropriately licensed persons. The NSW Government identifies unlicensed electrical wiring work penalties under the Home Building Act framework, historically including maximum penalties of $22,000 for individuals and $110,000 for corporations.
- VIC: electrical installation work is performed by licensed electricians; contracting requires Registered Electrical Contractor status; prescribed electrical installation work requires inspection by a licensed electrical inspector before connection.
- QLD: unlicensed electrical work is prosecuted under the Electrical Safety Act 2002 and can result in criminal penalties. QLD electrical safety prosecutions are published by the Office of the Work Health and Safety Prosecutor.
- SA: electrical workers and contractors are licensed or registered by CBS, while OTR regulates electrical installation and infrastructure technical safety.
- WA, TAS, ACT, and NT: each has separate occupational licensing rules and should not be assumed to accept another state's electrical licence without a mutual recognition check.

Automatic Mutual Recognition (AMR) under the Mutual Recognition Act 1992 (Cth) does not remove the need to check local exclusions, notification rules, and vulnerable work categories. Queensland is not part of AMR. NSW also operates the East Coast Electricians Scheme for certain QLD, VIC, and ACT electricians working in NSW.

## 3. Asset-owner duties

Owners and operators have direct electrical safety duties even when an EPC contractor performs the work.

- VIC: an electrical installation with generation capacity equal to or greater than 1000 kVA is a complex electrical installation. ESV guidance expressly includes BESS, solar farms, wind farms, co-generation, rotating grid stabilisers, and other generating technologies. Owners/operators must design, construct, operate, maintain, and decommission the installation to minimise, as far as practicable, safety risks, property damage risks, and bushfire danger.
- SA: electricity infrastructure design, construction, testing, commissioning, and operation are subject to OTR technical regulation. Development applications for generation infrastructure can require OTR certificates and technical evidence. In practice, generator/BESS commissioning often depends on OTR and network-service-provider witness requirements.
- WA: network operators must comply with the Electricity (Network Safety) Regulations 2015, including network incident reporting pathways.
- NSW: installation safety, CCEW, and consumer electrical installation controls are separate from workplace safety notification to SafeWork NSW.

## 4. Serious electrical incident notification

| Jurisdiction | Primary recipient | Trigger and timing | Practical control |
|---|---|---|---|
| ACT | Access Canberra and, where workplace-related, WorkSafe ACT | Confirm current ACT electrical and WHS incident rules | Use a dual-notification matrix for electrical and WHS triggers. |
| NSW | SafeWork NSW for workplace notifiable incidents; Building Commission NSW / Fair Trading for consumer electrical safety matters where required | WHS notifiable incident rules apply to workplace electric shock, serious injury, fire, or dangerous incident | Do not assume a CCEW issue is the same as WHS notification. |
| NT | NT WorkSafe and the electrical licensing regulator where required | Confirm current NT electrical accident reporting requirements | Confirm reporting contacts at mobilisation. |
| QLD | ESO / WorkSafe Queensland | Electrical Safety Act 2002 distinguishes serious electrical incidents and dangerous electrical events | Electrical incident response should use QLD-specific forms and call pathways. |
| SA | OTR, and SafeWork SA where workplace notifiable incident rules also apply | Electric shock, electrical burn, and prescribed electrical fire events may trigger OTR reporting; workplace events may also trigger WHS reporting | SA BESS incident SOPs often need dual reporting: OTR plus SafeWork SA. |
| TAS | CBOS and WorkSafe Tasmania where applicable | Apply the current Electricity Industry Safety and Administration Act 1997 and occupational licensing rules; separately confirm whether any Electricity Safety Act 2022 provisions have commenced by proclamation | Record the legislation version and proclamation check in the incident file. |
| VIC | ESV, and WorkSafe Victoria where workplace-related | ESV guidance for complex installations: serious electrical incidents must be reported as soon as practicable; other electrical incidents can have separate reporting timeframes under the 2019 Regulations | For BESS fire, electric shock, or HV incident, notify ESV through the complex installation pathway and preserve WHS notifications separately. |
| WA | Director of Energy Safety / Building and Energy | Electricity (Licensing) Regulations 1991 reg 63 requires electrical accident reporting; network operators also have Electricity (Network Safety) Regulations 2015 reg 23 pathways | Network incidents and installation incidents can use different WA pathways. |

## 5. Enforcement and penalties

### Victoria enforcement status

The following are confirmed ESV or court outcomes and should be described as electrical safety enforcement, not retail enforcement.

| Date | Entity | Court / regulator | Issue | Outcome | Source |
|---|---|---|---|---|---|
| 2023-08-10 | Hydroxygas Pty Ltd / Renaud Kobrynski | Melbourne Magistrates' Court / ESV | Unsafe BESS was disconnected by ESV and then reconnected contrary to direction | Convictions; company fined $50,000 and director fined $10,000 | ESV prosecutions register |
| 2023-10-11 | United Energy Distribution Pty Ltd | Frankston Magistrates' Court / ESV | Electric line clearance failures in hazardous bushfire risk areas | Conviction; aggregate fine $80,000 plus $13,200 costs | ESV prosecutions register |
| 2024-03-08 | Powercor Australia Ltd | Shepparton Magistrates' Court / ESV | Failed to inspect 4866 spans before fire danger period; 140 clearance failures; Glenmore fire burned about 185 ha | Guilty plea; fine $2.1 million plus $25,000 costs | ESV prosecutions register and ESV media release |
| 2024-07 | AusNet Services | Supreme Court of Victoria / ESV | Installed and energised a bare 22 kV high-voltage powerline in a highest-bushfire-risk area | Ordered to pay $200,000; AusNet admitted breach of Electricity Safety Act 1998 s 120N | ESV media release |
| 2026-01-08 | Greenova Pty Ltd | Seymour Magistrates' Court / ESV | Unsafe home battery installations at five Victorian properties, including one minor house fire; BESS not assessed by a licensed electrical inspector before connection | Guilty plea; fine $9,000 without conviction | ESV media release |

Victoria penalty caution: ESV announced increased penalties effective May 2025 for specified Electricity Safety Act offences, including knowingly installing unsafe electrical equipment and carrying out non-compliant, untested electrical installation work. ESV states the new maximum is 240 penalty units for an individual and 1200 penalty units for a body corporate. ESV's page uses the FY2024-25 penalty unit value of $197.59; convert using the current Victorian penalty unit for later periods.

### Technical incidents are not automatically penalties

Use the following as incident and engineering-control material unless a separate prosecution, penalty notice, or court order is identified:

- 2009 Black Saturday and the 2010 Victorian Bushfires Royal Commission findings on electricity-caused fires.
- 2014 Supreme Court approval of the Kilmore East-Kinglake class action settlement. Settlement approval is not a regulatory penalty and is not an admission of statutory breach unless the source states so.
- ESV technical investigation reports for the Australia Day 2018 outages, the St Patrick's Day 2018 fires, and the Victorian Big Battery fire statement of technical findings.

## 6. BESS and generation safety checklist

1. Confirm the state electrical contractor and worker licensing position before tender award.
2. Identify the state certificate pathway: VIC COES, NSW CCEW, SA eCoC, WA Notice of Completion / Electrical Safety Certificate, or local equivalent.
3. For VIC projects equal to or above 1000 kVA, treat the asset as a complex electrical installation and assess ESMS, operator competence, written operating procedures, incident reporting, and bushfire-risk controls.
4. For SA projects, allow time for OTR technical review and network commissioning witnessing.
5. For NSW projects, separate CCEW compliance from SafeWork NSW incident notification and from planning consent conditions.
6. For QLD projects, treat ESO electrical safety obligations as their own statutory track, not a subset of WHS.
7. For WA network assets, check both licensing regulations and network safety regulations.
8. For TAS, apply the in-force 1997 safety statute unless commencement of the 2022 Act is confirmed; for ACT and NT, verify the current certificate form before issuing construction-for-connection documents.

## 7. Source of truth

| Claim | Primary source | Publisher | URL |
|---|---|---|---|
| SA Technical Regulator, eCoC, electrical trades and infrastructure technical regulation | Electricity Act 1996; Electricity (General) Regulations 2012; OTR guidance | SA Legislation / Department for Energy and Mining | https://www.legislation.sa.gov.au/lz?path=%2FC%2FA%2FELECTRICITY+ACT+1996 ; https://www.legislation.sa.gov.au/lz?path=%2FC%2FR%2FElectricity+%28General%29+Regulations+2012 ; https://energymining.sa.gov.au/industry/regulatory-services/office-of-the-technical-regulator/electronic-certificates-of-compliance-ecoc |
| VIC complex electrical installation, BESS inclusion, general duties, incident reporting and ESMS | Electricity Safety Act 1998; Electricity Safety (General) Regulations 2019; ESV guidance | Energy Safe Victoria / Victorian legislation | https://www.energysafe.vic.gov.au/industry-guidance/electrical/electrical-technical-information/safety-standards-high-voltage-and ; https://www.energysafe.vic.gov.au/industry-guidance/electrical/electrical-installations/electrical-safety-management-schemes |
| VIC increased electrical safety penalties | Increased penalties | Energy Safe Victoria | https://www.energysafe.vic.gov.au/about-us/regulatory-framework/enforcement/increased-penalties |
| VIC prosecutions and technical investigation reports | Prosecutions; Electrical incident and technical investigations reports | Energy Safe Victoria | https://www.energysafe.vic.gov.au/about-us/regulatory-framework/enforcement/prosecutions ; https://www.energysafe.vic.gov.au/about-us/our-organisation/reports/electrical-incident-and-technical-investigations-reports |
| NSW CCEW and electrical licensing | Electrical compliance requirements; NSW electrical work licensing | NSW Government / Building Commission NSW | https://www.fairtrading.nsw.gov.au/trades-and-businesses/construction-and-trade-essentials/electricians/electrical-compliance-requirements ; https://www.nsw.gov.au/business-and-economy/licences-and-credentials/building-and-trade-licences-and-registrations/electrical |
| QLD electrical safety statute and prosecutions | Electrical Safety Act 2002; OWHSP court reports | Queensland legislation / OWHSP | https://www.legislation.qld.gov.au/view/html/inforce/current/act-2002-042 ; https://www.owhsp.qld.gov.au/court-report |
| WA licensing and network safety | Electricity (Licensing) Regulations 1991; Electricity (Network Safety) Regulations 2015 | WA legislation / Building and Energy | https://classic.austlii.edu.au/au/legis/wa/consol_reg/er1991331/ ; https://www.wa.gov.au/organisation/building-and-energy |
| TAS electrical safety and occupational licensing | Electricity Industry Safety and Administration Act 1997, current in-force text; Occupational Licensing Act 2005; Electricity Safety Act 2022 as made and subject to proclamation; CBOS guidance | Tasmanian legislation / CBOS | https://www.legislation.tas.gov.au/view/whole/html/inforce/current/act-1997-072/lh ; https://www.legislation.tas.gov.au/view/whole/html/inforce/current/act-2005-047 ; https://www.legislation.tas.gov.au/view/pdf/asmade/act-2022-032/lh ; https://www.cbos.tas.gov.au/topics/licensing-and-registration/licensed-occupations/electricians |
| ACT electrical licensing and safety | Electricity Safety Act 1971; Construction Occupations (Licensing) Act 2004 | ACT legislation / Access Canberra | https://www.legislation.act.gov.au/a/1971-42/ ; https://www.accesscanberra.act.gov.au/ |
| NT electrical worker and contractor licensing | Electrical Workers and Contractors Act 1978 | NT legislation / NT WorkSafe | https://legislation.nt.gov.au/en/Legislation/ELECTRICAL-WORKERS-AND-CONTRACTORS-ACT-1978 ; https://worksafe.nt.gov.au/ |
| Interstate electrical work and mutual recognition | Interstate workers; East Coast Electricians Scheme; AMR pages | ESV / NSW Government / WA Government | https://www.energysafe.vic.gov.au/licensing/electrical-licences/interstate-and-international-workers/interstate-electrical-workers ; https://www.nsw.gov.au/business-and-economy/licences-and-credentials/building-and-trade-licences-and-registrations/working-interstate-and-mutual-recognition/east-coast-electricians-scheme ; https://www.dmirs.wa.gov.au/corporate/automatic-mutual-recognition-amr |

## 8. Current-law caveats

- TAS: the Electricity Industry Safety and Administration Act 1997 remains in force at the baseline. The Electricity Safety Act 2022 commences by proclamation; verify the current proclamation position before treating any 2022 Act provision as operative.
- ACT and NT: certificate nomenclature and form requirements are less standardised in public national summaries; confirm regulator forms directly.
- AMR: do not rely on generic mutual recognition summaries for electrical work. Check the destination state's exclusions and notification rules.
- Victoria penalty conversion: ESV's 2025 increased-penalties page quotes FY2024-25 penalty unit values. Convert penalty units using the current Victorian value when advising after 1 July 2025.
