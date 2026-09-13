---
country: Australia
category: wholesale-market-compliance
page_id: D02
title: AER Wholesale Electricity Enforcement, Bidding, Dispatch, FCAS and Availability
last_updated: 2026-08-27
status: draft-researched
sources:
  - AER wholesale enforcement releases, compliance pages, court-case pages and annual reports
  - Federal Court of Australia decisions
  - AEMC National Electricity Rules and bidding rule-change materials
  - AER civil and criminal penalty indexation page
tags: [AER, NER, bidding, rebidding, good-faith, false-or-misleading, civil-penalty, FCAS, dispatch, PASA, availability, BESS, GPS]
---

# D02 - AER Wholesale Electricity Enforcement, Bidding, Dispatch, FCAS and Availability

This page summarises selected official wholesale electricity enforcement records relevant to NEM scheduled and semi-scheduled generators, scheduled bidirectional units, BESS operators, traders and EMS/SCADA vendors. It does not claim complete coverage of every AER notice or market event.

## Core obligations

| topic | primary rule / source | regulator | compliance point |
|---|---|---|---|
| Wholesale market monitoring | NEL ss 18C-18D | AER | AER monitors wholesale market performance, pricing, bidding, rebidding and contract-market information within its statutory remit. |
| Bids and rebids not false or misleading | NER cl 3.8.22A | AER | Bids and rebids must not be false, misleading or likely to mislead. |
| Rebidding | NER cl 3.8.22 | AER | Rebid as soon as practicable after relevant changed conditions become known; give brief, specific and accurate reasons; keep contemporaneous records for late rebids. |
| Dispatch instructions | NER cl 4.9.8 and related dispatch rules | AER / AEMO | Participants must follow AEMO dispatch instructions unless a valid rule-based exception applies. |
| FCAS capability and delivery | NER dispatch, offer and ancillary service provisions | AER / AEMO | Enabled FCAS must be deliverable according to offers, plant capability and dispatch instructions. |
| PASA and availability information | NER cl 3.7.3(e), cl 3.13.2(h), related PASA rules | AER / AEMO | Availability information and changes to submitted information must be accurate and notified when required. |
| Generator performance standards | NER cl 4.15(a)(1), Schedule 5.2 and registered performance standards | AER / AEMO / NSP | Plant must be operated consistently with approved performance standards and approved settings. |

## Bidding law: old good-faith test and current objective test

The old NER clause 3.8.22A required bids to be made in good faith. AER v Stanwell Corporation Ltd [2011] FCA 991 showed the difficulty of enforcing that subjective test. AEMC's National Electricity Amendment (Bidding in Good Faith) Rule 2015 No. 13, made on 10 December 2015 and commencing on 1 July 2016, replaced the old approach with the current objective false-or-misleading prohibition and strengthened rebid timing and record obligations.

| period | rule position | status |
|---|---|---|
| 2002-2016 | Old "bidding in good faith" obligation based on genuine intention to honour bids if material conditions did not change. | `old-rule`; useful for history only. |
| From 2016-07-01 | Bids and rebids must not be false or misleading; rebids must be made as soon as practicable after relevant conditions change; late rebid records must be kept. | Current rule architecture. |

Automated bidding systems should record the triggering condition, timestamp, bid/rebid reason, plant state, SOC or fuel position, constraint context, relevant forecast or price input and approval/audit trail.

## PASA and availability

Pelican Point is the key official availability case in this KB. The final records should be stated carefully:

- AER alleged failures in relation to capacity available during the February 2017 South Australian heatwave.
- The final penalty record identifies contraventions of NER cl 3.7.3(e)(2) and cl 3.13.2(h).
- AER's MT PASA allegation under cl 3.7.2(d) was not finally found in the liability judgment.

For BESS and automated dispatch operations, the practical control is broader than the final Pelican Point rule labels: any material change in available capacity, energy, SOC, thermal derating, auxiliary failure or protection limitation should trigger an assessed update to bids, PASA submissions and AEMO notifications where the rules require it.

## Selected official enforcement records

| date | entity | domain | issue | rules / obligations | outcome | status note | source |
|---|---|---|---|---|---|---|---|
| 2006-08-31 | AGL Hydro | Rebidding / inflexibility | MCKAY1 rebid and inflexibility declaration reasons | Old NER rebid and inflexibility requirements | $20,000 infringement notice | `old-rule`; pre-2015 rebidding reform | https://www.aer.gov.au/news/articles/news-releases/20000-penalty-imposed-agl-hydro |
| 2008-11-05 | Braemar Power Project | Dispatch / offer capability | Capability offer and dispatch instruction issues | NER dispatch and offer obligations | $60,000 infringement penalties | `old-rule`; early capability-offer case | https://www.aer.gov.au/news/articles/news-releases/aer-imposes-60000-penalty-braemar-power-project |
| 2009-09 | Babcock & Brown Power / Playford and Braemar | Dispatch / availability | Failure to follow dispatch instructions; availability change controls | NER dispatch instruction obligations | Two notices totalling $40,000; availability compliance improvements | `old-rule` | https://www.aer.gov.au/publications/reports/compliance/babcock-and-brown-power-failure-follow-dispatch-instructions-11-february-2009 |
| 2011-08-30 | Stanwell Corporation | Bidding | Old good-faith rebidding case | Old NER cl 3.8.22A | AER claim dismissed | `old-rule`; superseded by 2015 rule change | https://www.aer.gov.au/news/articles/news-releases/aer-queensland-generator-stanwell-decision-disappointing |
| 2015-02-12 | Snowy Hydro | Dispatch | Failure to comply with AEMO dispatch instructions | NER dispatch obligations | Federal Court penalty $400,000; enforceable undertaking | `current`; first Federal Court NER penalty | https://www.aer.gov.au/news/articles/news-releases/snowy-hydro-ordered-pay-400-000-penalties-failure-comply-aemo-dispatch-instructions |
| 2016-07-04 | CS Energy | Dispatch / offer capability | Wivenhoe and Gladstone dispatch/capability issues | NER dispatch and offer obligations | Four notices totalling $80,000; enforceable undertaking | `old-rule`; separate from 2021 CS Energy FCAS matter | https://www.aer.gov.au/news/articles/news-releases/cs-energy-pays-penalties-and-provides-court-enforceable-undertakings-aer |
| 2017-01-13 | AGL / EnergyAustralia | Dispatch / offer capability | Failure to follow dispatch and offer rules | NER cl 4.9.8(a), cl 4.9.8(b) | AGL $20,000; EnergyAustralia $40,000 | `old-rule`; date and amounts verified | https://www.aer.gov.au/news/articles/news-releases/agl-and-energyaustralia-pay-penalties-alleged-failure-follow-electricity-market-dispatch-and-offer-rules |
| 2018-07-19 | Synergen / ENGIE Dry Creek | Dispatch | Failure to follow AEMO dispatch instructions | NER cl 4.9.8(a) | Three notices totalling $60,000 | `current`; dispatch responsiveness reference | https://www.aer.gov.au/publications/reports/compliance/engie-failure-follow-dispatch-instructions-and-related-obligations |
| 2020-12-22 | Snowtown 2 Wind Farm | GPS / protection settings | Unapproved LVRT settings | NER performance standard obligations | Federal Court penalty $1,000,000 | `current` | https://www.aer.gov.au/news/articles/news-releases/snowtown-2-pay-penalty-1-million-rule-breach |
| 2021-02 | CS Energy | FCAS | FCAS offer not matching actual capability | FCAS capability / offer obligations | Infringement penalties $200,000; approximately $1.13 million FCAS payment returned | `current`; separate from 2016 dispatch case | https://www.aer.gov.au/system/files/AER%20Annual%20compliance%20and%20enforcement%20report%202020-21%20%20-%20July%202021.pdf |
| 2021-07-01 | Pacific Hydro Clements Gap / HWF1 Hornsdale | GPS / protection settings | Unapproved LVRT settings | NER performance standard obligations | Penalties totalling over $1.6 million | `current` | https://www.aer.gov.au/news/articles/news-releases/pacific-hydro-and-hornsdale-pay-over-16-million-penalties-breaching-energy-rules |
| 2022-06-28 | Hornsdale Power Reserve | BESS / FCAS | Contingency FCAS not provided according to offers and dispatch instructions | NER cl 3.8.7A(l), cl 4.9.8(a), cl 4.9.8(d) | Federal Court penalty $900,000 | `current`; most direct BESS/FCAS case | https://www.aer.gov.au/publications/reports/compliance/aer-v-hornsdale-power-reserve-pty-ltd-2022-fca-738 |
| 2022-06-28 | AGL HP wind farm entities | GPS / information | Protection settings and information failures after SA Black System | NER performance standard and information obligations | Federal Court penalty $3.5 million; enforceable undertaking | `current` | https://www.aer.gov.au/publications/reports/compliance/aer-v-agl-hp-1-pty-ltd-2022-fca-737 |
| 2023-06-01 | Stanwell | GPS / protection settings | Unapproved protection settings and voltage-disturbance ride-through failures | NER cl 4.15(a)(1) and registered GPS | Six notices totalling $263,400 | `current`; Callide-related GPS controls | https://www.aer.gov.au/publications/reports/compliance/stanwell-corporation-limited-breaches-national-electricity-rules |
| 2023-10-31 | AGL Macquarie / AGL Loy Yang | FCAS | Enabled contingency FCAS not provided | NER FCAS and dispatch obligations | Federal Court penalty $6 million | `current`; key FCAS enforcement case | https://www.aer.gov.au/publications/reports/compliance/agl-alleged-breaches-national-electricity-rules-0 |
| 2024-03-27 | Pelican Point Power | PASA / availability | Failure to inform AEMO of available capacity during 2017 SA heatwave | NER cl 3.7.3(e)(2), cl 3.13.2(h) | Federal Court penalty $900,000; costs $950,000 | `current`; MT PASA cl 3.7.2(d) not finally found | https://www.aer.gov.au/news/articles/news-releases/pelican-point-power-limited-penalised-900000-national-electricity-rules-breaches-during-2017-heat-wave |
| 2025-02-04 | Callide Power Trading | GPS / performance standards | Callide C4 performance standard failures | NER cl 4.15(a)(1) and registered GPS | Federal Court penalty $9 million; costs $150,000 | `current`; high-value GPS reference | https://www.aer.gov.au/publications/reports/compliance/callide-power-trading-breaches-national-electricity-rules |
| 2025-12-17 | Transgrid | Network / outages | Broken Hill outage-related allegations | NER network maintenance, restoration and compliance allegations | Proceedings instituted; penalties and declarations sought | `proceedings`; allegations only | https://www.aer.gov.au/news/articles/news-releases/aer-institutes-proceedings-against-transgrid-following-2024-broken-hill-outages |

## Civil penalties

Use AER's penalty indexation page for current values. From 1 July 2026, body corporate maximum court penalties are:

| tier | maximum court penalty |
|---|---|
| Tier 1 | Greater of $12,390,000, three times attributable benefit, or 10% annual turnover where benefit cannot be determined. |
| Tier 2 | $1,778,000 plus $89,000 per continuing day. |
| Tier 3 | $210,600 plus $21,100 per continuing day. |

Infringement notice amounts from 1 July 2026 are $84,000 for Tier 1 and Tier 2 body corporate provisions and $42,000 for Tier 3 body corporate provisions, subject to prescribed lesser amounts and AER determinations.

Do not state that NER cl 3.8.22 or cl 3.8.22A is a specific tier unless the current National Electricity Regulations schedule has been checked.

## BESS / EMS / SCADA controls

| control | reason |
|---|---|
| Keep bid and rebid trigger evidence, reason text, timestamps and plant-state snapshots. | Supports NER cl 3.8.22 and cl 3.8.22A compliance. |
| Validate SOC, available energy, MW limits, ramping, telemetry and FCAS response before offers and during enablement. | Hornsdale Power Reserve, AGL FCAS and CS Energy FCAS show actual capability matters. |
| Automate exception alerts for capacity, energy, fuel or derating changes that may affect PASA, bids or AEMO notifications. | Pelican Point shows availability information must be actively maintained. |
| Treat protection settings and GPS parameters as controlled configuration, not ordinary tuning variables. | Snowtown 2, Pacific Hydro/Hornsdale, AGL HP, Stanwell and Callide show approval and GPS compliance risk. |
| Preserve dispatch instruction evidence and response logs. | Dispatch cases turn on whether the instruction was followed and whether valid exceptions existed. |

## Source anchors

| topic | official source |
|---|---|
| NER cl 3.8.22 rebidding | https://energy-rules.aemc.gov.au/ner/622/528972 |
| NER cl 3.8.22A false or misleading bids/rebids | https://energy-rules.aemc.gov.au/ner/622/528973 |
| AEMC Bidding in Good Faith Rule 2015 | https://www.aemc.gov.au/rule-changes/bidding-in-good-faith |
| AER wholesale performance reports | https://www.aer.gov.au/industry/wholesale/performance |
| AER Enhanced Wholesale Market Monitoring Guideline | https://www.aer.gov.au/industry/registers/resources/guidelines/enhanced-wholesale-market-monitoring-guideline-2024 |
| AER PASA Compliance Bulletin and Checklist | https://www.aer.gov.au/system/files/2025-08/AER%20-%20PASA%20Compliance%20Bulletin%20-%20August%202025.pdf ; https://www.aer.gov.au/system/files/2025-08/AER%20-%20PASA%20Compliance%20Checklist%20-%20August%202025.pdf |
| AER civil and criminal penalty indexation | https://www.aer.gov.au/civil-and-criminal-penalty-indexation |
| Full timeline of selected enforcement events | D00-Enforcement-Event-Timeline-2006-2026.md |

## Coverage caveats

- This page is a selected case library, not a complete AER wholesale enforcement register.
- Technical market events such as the June 2022 NEM suspension are covered in D00/D15 as system events, not as contravention findings.
- Rule numbers and penalty tiers must be checked against the current NER and regulations before legal use.
