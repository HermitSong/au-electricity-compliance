---
country: Australia
tier: residential
category: engineering
last_updated: 2026-08-20
status: verified
sources:
  - https://www.standards.org.au
  - https://cleanenergycouncil.org.au/
  - https://www.aemo.com.au
tags:
  - australia
  - residential
  - engineering
  - AS-NZS-5033
  - AS-NZS-4777
  - CEC-approved
---

> **Nav**: [[00-Home/Dashboard|Dashboard]] > [[../_AU-Overview|Australia]] > **Residential** > **Engineering Standards**

# Engineering Standards -- Residential (<100 kW)

## Core Standards

### AS/NZS 5033:2021 -- Installation and Safety Requirements for PV Arrays

| Requirement | Detail |
|-------------|--------|
| Array Design | Maximum system voltage calculation; string sizing; orientation and tilt |
| DC Wiring | Cable selection per AS/NZS 3008; UV-rated cable for outdoor; conduit requirements |
| DC Isolation | Array isolator required; rooftop isolator no longer mandatory (2021 revision) |
| Earthing | Array frame earthing; equipment earthing per AS/NZS 3000 |
| Labelling | DC warning labels at switchboard, meter box, and inverter; fire brigade information sign |
| Exclusion Zones | Minimum clearances from edges of roof for fire brigade access |

### AS/NZS 4777.2:2020 -- Grid Connection of Energy Systems via Inverters

This is the primary standard governing how residential inverters interact with the grid.

#### Smart Inverter Requirements (Mandatory)

| Function | Description | Default Setting |
|----------|-------------|----------------|
| Volt-Watt (V-W) | Curtails active power output when grid voltage rises | Activates at 253V; zero export at 265V |
| Volt-Var (V-Var) | Injects or absorbs reactive power to manage voltage | 4-quadrant capability; DNSP-configurable |
| Frequency-Watt (f-W) | Reduces active power during over-frequency events | Droop response above 50.25 Hz |
| Power Rate Limiting | Limits rate of change of power output | 16.7% of rated power per minute (default) |
| Reconnection Ramp | Gradual reconnection after grid disturbance | Ramp over 10 minutes default |

#### Grid Protection Settings (AS/NZS 4777.2:2020)

| Protection | Trip Setting | Trip Time |
|-----------|-------------|-----------|
| Over-voltage Stage 1 | 255V | 10 minutes |
| Over-voltage Stage 2 | 265V | 1 second |
| Under-voltage Stage 1 | 180V | 10 minutes |
| Under-voltage Stage 2 | 100V | 2 seconds |
| Over-frequency | 52 Hz | 2 seconds |
| Under-frequency | 47 Hz | 2 seconds |
| Anti-islanding | Passive + active detection | <2 seconds |

#### DNSP-Specific Settings

Each DNSP assigns a "Country Code" that configures region-specific inverter settings. Installers must select the correct country code during commissioning.

### AS/NZS 3000:2018 -- Wiring Rules

Applies to all residential electrical work including:
- AC wiring from inverter to switchboard
- Metering connections
- Earthing and bonding
- Circuit protection (MCBs, RCDs)

## CEC Approved Equipment Lists

### Module Approval

| Requirement | Detail |
|-------------|--------|
| CEC Approved Modules List | All PV modules must be listed for STC eligibility |
| IEC 61215 certification | Performance qualification required |
| IEC 61730 certification | Safety qualification required |
| Module degradation warranty | Minimum 25 years performance warranty standard |
| Module product warranty | Typically 12-15 years |

### Inverter Approval

| Requirement | Detail |
|-------------|--------|
| CEC Approved Inverters List | All inverters must be listed for STC eligibility |
| AS/NZS 4777.2:2020 compliance | Mandatory for grid connection |
| IEC 62109-1/2 safety certification | Inverter safety qualification |
| DER Register listing | Inverter must support AEMO DER Register data reporting |

### Battery Approval

| Requirement | Detail |
|-------------|--------|
| CEC Approved Battery List | Batteries must be listed for eligibility under state rebate programs |
| AS/NZS 5139:2019 compliance | Installation safety requirements |
| IEC 62619 or IEC 62133 | Cell-level safety certification |
| Cycle warranty | Typically 6,000-10,000 cycles or 10 years |

## Typical Residential System Specifications

### Solar PV System

| Parameter | Typical Value |
|-----------|--------------|
| System size | 6.6 kW (most common); range 3-15 kW |
| Module type | Monocrystalline PERC/TOPCon; 400-450 W per panel |
| Number of panels | 15-17 (for 6.6 kW) |
| Inverter size | 5 kW (single-phase); 5-10 kW (three-phase) |
| Annual generation | 8,000-11,000 kWh (location-dependent) |
| Roof area required | 30-45 m2 (for 6.6 kW) |

### Battery Storage

| Parameter | Typical Value |
|-----------|--------------|
| Capacity | 5-15 kWh (most common: 10 kWh) |
| Power rating | 3-5 kW continuous |
| Chemistry | Lithium iron phosphate (LFP) dominant |
| Cycle life | 6,000-10,000 cycles |
| Warranty | 10 years |
| Leading products | Tesla Powerwall 3, BYD BatteryBox, Enphase IQ Battery, SolarEdge Home Battery |

## CEC Installer Requirements

| Requirement | Detail |
|-------------|--------|
| CEC Accredited Installer | Mandatory for all residential solar installations claiming STCs |
| Electrical licence | Must hold state electrical licence (unrestricted or restricted) |
| Clean Energy Council membership | Required for accreditation |
| CPD requirements | Minimum hours of continuing professional development annually |
| Insurance | Professional indemnity and public liability insurance required |

See also: [[Safety-Compliance]], [[Grid-Requirements]], [[../Commercial-Industrial/Engineering-Standards]]

## Related in This Tier
- [[Grid-Requirements]]
- [[Industry-Insights]]
- [[Market-Data]]
- [[Safety-Compliance]]
