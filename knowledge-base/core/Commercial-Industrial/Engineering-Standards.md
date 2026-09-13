---
country: Australia
tier: commercial-industrial
category: engineering
last_updated: 2026-08-20
status: verified
sources:
  - https://www.standards.org.au
  - https://cleanenergycouncil.org.au/
  - https://www.aemo.com.au
tags:
  - australia
  - commercial-industrial
  - engineering
  - AS-NZS-5033
  - AS-NZS-4777
  - CEC
---

> **Nav**: [[00-Home/Dashboard|Dashboard]] > [[../_AU-Overview|Australia]] > **Commercial-Industrial** > **Engineering Standards**

# Engineering Standards -- Commercial-Industrial (100 kW - 5 MW)

## Core AS/NZS Standards

### Solar PV Standards

| Standard | Title | Application |
|----------|-------|-------------|
| AS/NZS 5033:2021 | Installation and Safety Requirements for PV Arrays | DC side design: string sizing, cable selection, isolation, earthing, labelling |
| AS/NZS 4777.2:2020 | Grid Connection of Energy Systems via Inverters -- Part 2: Inverter Requirements | Inverter grid connection requirements: power quality, anti-islanding, voltage/frequency ride-through |
| AS/NZS 3000:2018 | Wiring Rules | All electrical wiring from PV array to switchboard and grid connection |
| AS/NZS 3008 | Selection of Cables | Cable sizing for AC and DC circuits |

### Battery Storage Standards

| Standard | Title | Application |
|----------|-------|-------------|
| AS/NZS 5139:2019 | Electrical Installations -- Safety of BESS | Installation requirements for C&I battery systems |
| IEC 62619 | Secondary Lithium Cells -- Safety | Cell-level safety requirements |
| AS 2067 | Substations and HV Installations | If HV connection required (>1 MW systems) |

### Electrical Installation

| Standard | Title | Application |
|----------|-------|-------------|
| AS/NZS 3000:2018 | Wiring Rules | All electrical work |
| AS/NZS 3010 | Electrical Installations -- Generating Sets | Backup generators (if applicable) |
| AS/NZS 61000.3.6 | Electromagnetic Compatibility -- Harmonic Emission Limits | Harmonic distortion limits for C&I connections |

## AS/NZS 4777.2:2020 -- Key Requirements for C&I Inverters

The 2020 revision of AS/NZS 4777.2 introduced significant new requirements:

### Smart Inverter Functions

| Function | Requirement |
|----------|-------------|
| Volt-Watt Response | Mandatory; reduce active power when voltage rises above threshold |
| Volt-Var Response | Mandatory; inject/absorb reactive power based on voltage |
| Frequency-Watt Response | Mandatory; reduce power for over-frequency events |
| Power Quality Response Mode | Configurable by DNSP for local network conditions |
| Fixed Power Factor | Settable; default varies by DNSP |

### Grid Protection Settings

| Parameter | Default Setting |
|-----------|----------------|
| Over-voltage Stage 1 | 260V (10 min) |
| Over-voltage Stage 2 | 265V (1 sec) |
| Under-voltage Stage 1 | 180V (10 min) |
| Under-voltage Stage 2 | 100V (2 sec) |
| Over-frequency | 52 Hz (2 sec) |
| Under-frequency | 47 Hz (2 sec) |
| Anti-islanding | Passive + active detection; disconnect within 2 seconds |

### DNSP Configuration

DNSPs may specify custom settings for different regions. Installers must configure inverters according to the relevant DNSP's Country Code and regional settings per AS/NZS 4777.2.

## CEC Accredited Installer Requirements

### For C&I Systems (100 kW - 5 MW)

| Requirement | Detail |
|-------------|--------|
| CEC Accreditation Level | CEC Accredited Installer (Solar PV) required |
| Design Sign-Off | CEC Accredited Designer recommended for >100 kW; required for systems where designer and installer are different |
| Supervision | CEC-accredited person must supervise installation |
| Equipment | All modules and inverters must be on CEC Approved Lists |
| STC/LGC Eligibility | CEC-accredited installation mandatory for certificate creation |
| Ongoing CPD | CEC-accredited installers must complete continuing professional development |

### Accreditation Pathway

| Step | Detail |
|------|--------|
| 1. Electrical licence | Must hold unrestricted electrical licence (or equivalent) in relevant state |
| 2. CEC training | Complete CEC-approved training course |
| 3. Practical assessment | Demonstrate competency in installation |
| 4. Apply to CEC | Submit application with supporting evidence |
| 5. Renewal | Annual renewal with CPD requirements |

## Design Considerations for C&I Systems

### System Sizing

| Factor | Consideration |
|--------|--------------|
| Load profile | Match system size to daytime load to maximise self-consumption |
| Roof area | Structural assessment for rooftop systems; AS/NZS 1170 loading |
| Export limits | DNSP export limit may constrain system size |
| Network tariff structure | Demand charges may favour battery + solar over solar alone |
| Future load growth | EV charging, electrification may increase future consumption |

### Typical System Configurations

| Size Range | Configuration |
|-----------|--------------|
| 100-300 kW | String inverters; single LV connection; rooftop or ground-mount |
| 300 kW - 1 MW | Central or string inverters; LV or 11 kV connection; dedicated metering |
| 1-5 MW | Central inverters or power stations; 11 kV or 22 kV connection; dedicated substation |

See also: [[Safety-Compliance]], [[Grid-Requirements]], [[../Medium-Scale/Engineering-Standards]]

## Related in This Tier
- [[Grid-Requirements]]
- [[Industry-Insights]]
- [[Market-Data]]
- [[Safety-Compliance]]
