---
country: Australia
tier: residential
category: grid
last_updated: 2026-08-20
status: verified
sources:
  - https://www.aemo.com.au
  - https://www.ausgrid.com.au
  - https://www.sapowernetworks.com.au
  - https://www.energex.com.au
  - https://www.ausnetservices.com.au
tags:
  - australia
  - residential
  - grid
  - AS-NZS-4777
  - voltage-rise
  - export-limits
  - smart-inverter
---

> **Nav**: [[00-Home/Dashboard|Dashboard]] > [[../_AU-Overview|Australia]] > **Residential** > **Grid Requirements**

# Grid Connection -- Residential (<100 kW)

## AS/NZS 4777.2 Grid Connection

All residential grid-connected inverters must comply with AS/NZS 4777.2:2020. This standard defines the technical requirements for inverter-grid interaction. See [[Engineering-Standards#AS/NZS 4777.2:2020|Engineering Standards]] for detailed inverter requirements.

### Connection Process (Residential)

```
1. System Design
   ├── CEC-accredited installer designs system
   ├── Check DNSP export limits and hosting capacity
   └── Select CEC-approved equipment

2. DNSP Connection Application
   ├── Online application via DNSP portal
   ├── Single-phase: typically auto-approved up to 5 kW
   ├── Three-phase: typically auto-approved up to 10-15 kW
   └── Larger systems: manual assessment required

3. Installation
   ├── CEC-accredited installer completes installation
   ├── State electrical compliance certificate issued
   └── Inverter commissioned with correct DNSP country code

4. Grid Connection
   ├── DNSP meter exchange or reconfiguration (smart meter)
   ├── Bidirectional metering activated
   └── Export enabled
```

### Typical Approval Timeframes

| System Size | Auto-Approval | Manual Assessment |
|-------------|--------------|-------------------|
| <5 kW (single-phase) | Yes (most DNSPs) | N/A |
| 5-10 kW (single-phase) | Some DNSPs | 5-15 business days |
| <15 kW (three-phase) | Yes (most DNSPs) | N/A |
| 15-30 kW (three-phase) | Some DNSPs | 10-20 business days |
| >30 kW | No | 20-45 business days |

## Voltage Rise Limits

Voltage rise from solar export is a primary constraint on residential systems.

### Regulatory Limits

| Parameter | Limit |
|-----------|-------|
| Nominal voltage (single-phase) | 230V |
| Upper voltage limit (steady state) | 253V (+10%) |
| Lower voltage limit (steady state) | 207V (-10%) |
| Allowable voltage rise from inverter | Typically 2-3% at point of connection |
| Total feeder voltage range | Must remain within +10%/-10% of nominal |

### Voltage Rise Causes

| Factor | Impact |
|--------|--------|
| High solar penetration on feeder | Multiple rooftop systems exporting simultaneously raise feeder voltage |
| Long feeder distance from substation | Higher impedance = greater voltage rise per kW exported |
| Small conductor size | Higher resistance = greater voltage rise |
| Transformer tap position | Off-nominal tap position can exacerbate voltage rise |

### DNSP Mitigation Strategies

| Strategy | Description |
|----------|-------------|
| Smart inverter settings | Volt-Watt and Volt-Var response (mandatory under AS/NZS 4777.2:2020) |
| Export limits | Static or dynamic export limits applied to new connections |
| Transformer tap adjustment | DNSPs lower distribution transformer taps to create headroom |
| Network augmentation | Conductor upgrade, new transformer, or voltage regulator |
| Community batteries | DNSP-installed battery on constrained feeders |

## Export Limits by DNSP

### Current Export Limits (Residential, Single-Phase)

| DNSP | State | Default Export Limit | Notes |
|------|-------|---------------------|-------|
| Ausgrid | NSW | 5 kW per phase | 10 kW for three-phase; dynamic export available |
| Endeavour Energy | NSW | 5 kW per phase | Higher limits by application |
| Essential Energy | NSW | 5 kW per phase | Rural areas may have lower limits |
| AusNet Services | VIC | 5 kW per phase | Some constrained areas: 3.5 kW or zero export |
| CitiPower/Powercor | VIC | 5 kW per phase | Dynamic export pilot programs |
| Jemena | VIC | 5 kW per phase | |
| United Energy | VIC | 5 kW per phase | |
| Energex | QLD | 5 kW per phase | 10 kW three-phase; 30 kW with application |
| Ergon Energy | QLD | 5 kW per phase | Rural constraints vary |
| SA Power Networks | SA | 5 kW per phase | 10 kW three-phase; SA has highest solar penetration and most constraints |
| TasNetworks | TAS | 5 kW per phase | |
| Western Power | WA | 5 kW per phase | WA has separate emergency solar management scheme |

### Dynamic Export Limits

Several DNSPs are implementing dynamic export limits that adjust in real-time:

| Feature | Description |
|---------|-------------|
| Dynamic Operating Envelope (DOE) | AEMO-defined framework for real-time export limits |
| Communication | Via smart inverter DER gateway or smart meter |
| Benefit | Allows higher exports when network has capacity; reduces curtailment |
| Status | Pilots underway at Ausgrid, SA Power Networks, AusNet Services (2025-26) |

## Smart Inverter Settings

### AS/NZS 4777.2:2020 Response Modes

All new residential inverters must support these response modes:

| Mode | Purpose | When Active |
|------|---------|-------------|
| Volt-Watt | Reduce export when voltage is high | Voltage > 253V (default threshold) |
| Volt-Var | Absorb/inject reactive power for voltage support | Continuous; configured per DNSP |
| Frequency-Watt | Reduce output during over-frequency | Frequency > 50.25 Hz |
| Emergency disconnect | Remote disconnection by DNSP | Emergency conditions (via DER gateway) |
| Reconnection ramp | Gradual restart after grid restoration | Post-disturbance; 10-minute default ramp |

### AEMO DER Register

All new DER installations must be registered in the AEMO Distributed Energy Resources Register:

| Data | Required |
|------|----------|
| System capacity (kW) | Yes |
| Inverter make/model | Yes |
| Battery capacity (if applicable) | Yes |
| Connection point (NMI) | Yes |
| Installation date | Yes |
| Installer details | Yes |

## Metering

| Meter Type | Application |
|-----------|-------------|
| Type 4 (smart meter) | Standard for all new solar connections; interval data |
| Bidirectional | Required for systems with export capability |
| Solar/generation meter | May be required separately for STC verification |
| Net meter | Measures net import/export at connection point |

See also: [[Engineering-Standards]], [[Market-Data]], [[../Commercial-Industrial/Grid-Requirements]]

## Related in This Tier
- [[Engineering-Standards]]
- [[Industry-Insights]]
- [[Market-Data]]
- [[Safety-Compliance]]
