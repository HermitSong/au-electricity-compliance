---
country: Australia
tier: medium-scale
category: engineering
last_updated: 2026-08-20
status: verified
sources:
  - https://www.standards.org.au
  - https://cleanenergycouncil.org.au/
  - https://www.aemo.com.au
tags:
  - australia
  - medium-scale
  - engineering
  - standards
  - AS-NZS
  - CEC
---

> **Nav**: [[00-Home/Dashboard|Dashboard]] > [[../_AU-Overview|Australia]] > **Medium-Scale** > **Engineering Standards**

# Engineering Standards -- Medium-Scale Generation (5-30 MW)

## Applicable AS/NZS Standards

Medium-scale systems are subject to the same core standards as [[../Large-Scale-Generation/Engineering-Standards|large-scale generation]], with some practical differences in application.

### Core Standards

| Standard | Title | Application to Medium-Scale |
|----------|-------|-----------------------------|
| AS/NZS 3000:2018 | Wiring Rules | All electrical installations |
| AS/NZS 5033:2021 | Installation and Safety Requirements for PV Arrays | Solar PV array design (same as large-scale) |
| AS/NZS 3008 | Selection of Cables | Cable sizing for MV and LV systems |
| AS 2067 | Substations and HV Installations | Substation design (often 33 kV or 66 kV connection) |
| AS/NZS 5139:2019 | Safety of BESS | Battery storage installations |
| AS/NZS 1768 | Lightning Protection | Exposed generation sites |

### Inverter Standards

| Standard | Title | Application |
|----------|-------|-------------|
| AS/NZS 4777.2:2020 | Grid Connection of Energy Systems via Inverters -- Part 2 | Inverter requirements for grid connection (applies to systems using inverters <200 kVA per unit; larger central inverters may reference IEC standards directly) |
| IEC 62109 | Safety of Power Converters for PV | Inverter safety qualification |
| IEC 61683 | PV Systems -- Power Conditioners -- Procedure for Measuring Efficiency | Inverter efficiency measurement |

### Metering Standards

| Standard | Title | Application |
|----------|-------|-------------|
| AS 1284 | Electricity Metering | Revenue metering requirements |
| AS 62053 | Electricity Metering Equipment | Accuracy classes for metering |
| NER Chapter 7 | Metering | NEM metering obligations for registered generators |

## CEC Guidelines for Medium-Scale Systems

The Clean Energy Council provides guidance specific to medium-scale installations:

| Guideline | Scope |
|-----------|-------|
| CEC Best Practice Guide for Solar PV | Design, construction, commissioning for systems >100 kW |
| CEC Approved Equipment Lists | Modules and inverters must be CEC-approved for LRET eligibility |
| CEC Accredited Installer | CEC-accredited installer required for LGC creation |
| CEC Accredited Designer | Design sign-off by CEC-accredited designer recommended for >100 kW |

## Design Considerations for Medium-Scale

### Connection Voltage

| System Size | Typical Connection Voltage | Connection Point |
|-------------|---------------------------|-----------------|
| 5-10 MW | 11 kV or 22 kV | Distribution (DNSP) |
| 10-20 MW | 33 kV or 66 kV | Sub-transmission (DNSP or TNSP) |
| 20-30 MW | 33 kV or 66 kV | Sub-transmission or transmission |

### Key Design Differences from Large-Scale

| Aspect | Medium-Scale | Large-Scale |
|--------|-------------|-------------|
| Substation | Often single transformer; simpler protection | Multiple transformers; full protection scheme |
| SCADA | Basic monitoring; DNSP interface | Full AEMO SCADA integration |
| Dispatch | May be non-scheduled or semi-scheduled | Scheduled or semi-scheduled |
| Protection | DNSP protection coordination | TNSP protection coordination |
| Earthing | AS/NZS 3000 + AS 2067 | Full earthing grid design to AS 2067 |

## Quality Assurance

| Phase | Requirements |
|-------|-------------|
| Design Review | Independent review by CEC-accredited designer |
| Component Procurement | CEC-listed modules and inverters; IEC-certified transformers |
| Construction QA | ITP (Inspection and Test Plan); hold points for critical stages |
| Pre-Commissioning | Megger testing, relay testing, protection settings verification |
| Commissioning | DNSP witnessed testing; AEMO R2 testing if NEM-registered |
| O&M | Scheduled maintenance per manufacturer requirements |

See also: [[Safety-Compliance]], [[Grid-Requirements]], [[../Large-Scale-Generation/Engineering-Standards]]

## Related in This Tier
- [[Grid-Requirements]]
- [[Industry-Insights]]
- [[Market-Data]]
- [[Safety-Compliance]]
