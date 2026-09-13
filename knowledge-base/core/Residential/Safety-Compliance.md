---
country: Australia
tier: residential
category: safety
last_updated: 2026-08-20
status: verified
sources:
  - https://www.safeworkaustralia.gov.au
  - https://www.esv.vic.gov.au
  - https://www.safework.nsw.gov.au
  - https://cleanenergycouncil.org.au/
tags:
  - australia
  - residential
  - safety
  - electrical-safety
  - DC-isolator
  - installer-accreditation
---

> **Nav**: [[00-Home/Dashboard|Dashboard]] > [[../_AU-Overview|Australia]] > **Residential** > **Safety Compliance**

# Safety and Compliance -- Residential (<100 kW)

## State Electrical Safety Acts

### Regulatory Framework by State

| State | Act | Regulator | Key Requirements |
|-------|-----|-----------|-----------------|
| NSW | Electricity Supply Act 1995; Home Building Act 1989 | SafeWork NSW; Fair Trading NSW | CCEW (Certificate of Compliance) required; consumer protection via Home Building Act |
| VIC | Electricity Safety Act 1998 | Energy Safe Victoria (ESV) | Certificate of Electrical Safety (CES) within 24 hours; prescribed electrical work |
| QLD | Electrical Safety Act 2002 | Electrical Safety Office (ESO) | Form 18 notice of electrical work; Electrical Safety Certificate |
| SA | Electricity Act 1996 | Office of the Technical Regulator (OTR) | Certificate of Compliance; inspection regime |
| TAS | Electricity Industry Safety and Administration Act 1997 | WorkSafe Tasmania / CBOS | Certificate of Compliance |
| WA | Electricity Act 1945 | Building and Energy (DEMIRS) | Preliminary Notice; Electrician's Work Report |
| ACT | Electricity Safety Act 1971 | Access Canberra | Electrical work licence; certificate of compliance |
| NT | Electrical Workers and Contractors Act 1978 | NT WorkSafe | Registered electrical contractor required |

## Installer Accreditation

### CEC Accreditation (National)

CEC accreditation is the primary quality assurance mechanism for residential solar installations.

| Level | Scope | Requirements |
|-------|-------|-------------|
| CEC Accredited Installer -- Grid-Connected Solar | Design and install grid-connected solar PV up to 100 kW | Electrical licence + CEC training + assessment |
| CEC Accredited Installer -- Battery Storage | Install battery storage systems | Additional CEC battery training module |
| CEC Accredited Designer | Design solar PV systems (separate from installation) | Engineering or electrical background + CEC training |

### Accreditation Compliance

| Requirement | Detail |
|-------------|--------|
| Installation Standards | Must comply with AS/NZS 5033, AS/NZS 4777.2, AS/NZS 3000 |
| Documentation | Installation must be documented with photos, SLD, compliance certificate |
| STC creation | Only CEC-accredited installers can create STCs for the installation |
| Complaints mechanism | CEC investigates consumer complaints against accredited installers |
| De-accreditation | Serious non-compliance can result in loss of CEC accreditation |

### State Electrical Licence Requirements

| State | Licence Type | Solar-Specific |
|-------|-------------|---------------|
| NSW | Qualified Supervisor Certificate + Contractor Licence | No additional solar licence; CEC accreditation covers solar |
| VIC | Registered Electrical Inspector (REI) for inspection; Licensed Electrician for work | ESV registration for electrical workers |
| QLD | Electrical Contractor Licence | Solar-specific endorsement not required (CEC accreditation covers) |
| SA | PGE (Plumbing, Gas, Electrical) Licence | OTR registration |
| WA | Electrical Contractor Licence (EC) or Restricted Electrical Licence (REL) | DEMIRS registration |

## DC Isolator Requirements

DC isolators have been a major safety issue following rooftop fires attributed to DC isolator failures.

### Current Requirements (AS/NZS 5033:2021)

| Location | Requirement |
|----------|-------------|
| Rooftop DC isolator (next to inverter) | **No longer mandatory** for new installations (removed in 2021 revision) |
| Array-level DC isolator | Required for maintenance isolation |
| Inverter integrated DC isolator | Acceptable if inverter includes compliant integrated DC switch |
| String-level fusing | Required for systems with 3+ parallel strings |
| Labelling | All DC isolation points must be clearly labelled |

### Historical Context

- Pre-2021: rooftop DC isolators were mandatory under AS/NZS 5033:2014
- Multiple rooftop fire incidents attributed to water ingress and arcing in external DC isolators
- 2021 revision removed mandatory rooftop DC isolator requirement
- Existing installations with DC isolators should be inspected for degradation

### Safety Recommendations

| Item | Recommendation |
|------|---------------|
| Existing DC isolators | Inspect annually; replace if showing signs of degradation |
| New installations | Use inverter-integrated DC switching where possible |
| Module-level shutdown | Consider module-level power electronics (optimisers or microinverters) for enhanced DC safety |
| Arc fault detection | AFCI (Arc Fault Circuit Interrupter) recommended but not yet mandatory in Australia |

## Consumer Protection

### Solar Installation Warranties

| Warranty Type | Typical Coverage |
|--------------|-----------------|
| Installer workmanship warranty | 5-10 years (varies by state consumer law) |
| Module product warranty | 12-15 years |
| Module performance warranty | 25-30 years (degradation guarantee) |
| Inverter warranty | 5-12 years (varies; 10 years becoming standard) |
| Battery warranty | 10 years |

### Consumer Recourse

| Issue | Recourse |
|-------|----------|
| Faulty installation | CEC complaints process; state fair trading; ACCC |
| Product defect | Manufacturer warranty; Australian Consumer Law (ACL) |
| Unsafe installation | State electrical safety regulator; emergency: call DNSP |
| STC fraud | Clean Energy Regulator enforcement |

See also: [[Engineering-Standards]], [[Grid-Requirements]], [[../Commercial-Industrial/Safety-Compliance]]

## Related in This Tier
- [[Engineering-Standards]]
- [[Grid-Requirements]]
- [[Industry-Insights]]
- [[Market-Data]]
