---
country: Australia
tier: commercial-industrial
category: grid
last_updated: 2026-08-20
status: verified
sources:
  - https://www.aemo.com.au
  - https://www.energynetworks.com.au
  - https://www.ausgrid.com.au
  - https://www.sapowernetworks.com.au
tags:
  - australia
  - commercial-industrial
  - grid
  - DNSP
  - connection
  - export-limits
  - demand-management
---

> **Nav**: [[00-Home/Dashboard|Dashboard]] > [[../_AU-Overview|Australia]] > **Commercial-Industrial** > **Grid Requirements**

# Grid Connection -- Commercial-Industrial (100 kW - 5 MW)

## DNSP Connection Standards

C&I systems connect to the distribution network under DNSP-specific connection standards.

### Connection Process (Typical)

```
1. Pre-Application Enquiry
   ├── Check available hosting capacity (DNSP online tools)
   ├── Determine connection voltage and metering requirements
   └── Identify export limit constraints

2. Connection Application
   ├── Complete DNSP application form
   ├── Single line diagram
   ├── Inverter specification (CEC-approved, AS/NZS 4777.2 compliant)
   ├── Protection coordination study (if >200 kW)
   └── Payment of application fee

3. DNSP Assessment
   ├── Network impact assessment
   ├── Voltage rise calculation
   ├── Fault level contribution assessment
   └── Connection offer with conditions

4. Installation and Commissioning
   ├── Installation by CEC-accredited installer
   ├── DNSP metering installation
   ├── Inverter commissioning and settings verification
   └── Export testing and energisation
```

### Timeframes by DNSP

| DNSP | Typical Assessment Time | Connection Fee (Indicative) |
|------|------------------------|---------------------------|
| Ausgrid (NSW) | 20-45 business days | $1,500-$15,000+ |
| Endeavour Energy (NSW) | 20-40 business days | $1,000-$10,000+ |
| Essential Energy (NSW) | 20-40 business days | $1,000-$8,000+ |
| AusNet Services (VIC) | 20-50 business days | $1,500-$20,000+ |
| SA Power Networks (SA) | 15-30 business days | $1,000-$10,000+ |
| Energex (QLD) | 15-35 business days | $1,000-$12,000+ |

Fees vary significantly based on system size, network augmentation requirements, and metering.

## Export Limits

### Standard Export Limits by DNSP (Indicative)

| DNSP | Default Export Limit | Notes |
|------|---------------------|-------|
| Ausgrid | 200 kW per phase (LV); negotiated for HV | Higher limits available via network study |
| Endeavour Energy | 200 kW (LV); up to connection capacity (HV) | Dynamic export possible |
| AusNet Services | 150-300 kW (LV); negotiated for HV | Voltage constraint areas may have zero export |
| SA Power Networks | 200 kW (LV); negotiated for HV | SA has high solar penetration; constraints common |
| Energex | 200 kW (LV); 1.5 MW (HV typical) | Smart inverter settings required |

### Managing Export Limits

| Strategy | Description |
|----------|-------------|
| Battery storage | Absorb excess generation; export during peak times |
| Load shifting | Shift discretionary loads to solar generation hours |
| Dynamic export | Real-time export adjustment based on network conditions (DNSP-enabled) |
| Zero export | All generation consumed on-site; simplest DNSP approval |
| Demand response | Reduce export during network-constrained periods |

## Demand Management

### Network Tariff Structures

C&I customers are typically on demand-based network tariffs:

| Tariff Component | Description | Typical Rate |
|-----------------|-------------|-------------|
| Demand charge (kW) | Based on maximum demand in billing period | $8-25/kW/month |
| Energy charge (kWh) | Volumetric charge per kWh consumed | $0.02-0.08/kWh |
| Fixed charge | Daily supply charge | $1-5/day |
| Time-of-use energy | Peak/off-peak/shoulder rates | Varies by DNSP |
| Critical peak demand | Additional charge during network peak events | Up to $50/kW |

### Battery for Demand Charge Reduction

| Scenario | Demand Reduction | Annual Savings |
|----------|-----------------|---------------|
| 100 kW battery on 500 kW site | 15-25% peak demand reduction | $15,000-$40,000 |
| 500 kW battery on 2 MW site | 20-30% peak demand reduction | $50,000-$150,000 |

Demand charge savings are often the primary economic driver for C&I battery installation.

### Demand Response Programs

| Program | Operator | C&I Participation |
|---------|----------|-------------------|
| RERT (Reliability and Emergency Reserve Trader) | [[../Regulatory-Bodies#AEMO|AEMO]] | Large C&I with dispatchable load/generation |
| Wholesale Demand Response Mechanism (WDRM) | AEMO/Aggregator | Via aggregator; minimum 1 MW portfolio |
| DNSP demand management programs | Individual DNSPs | Site-specific contracts |
| VPP programs | Retailers/Aggregators | Aggregated C&I batteries and flexible loads |

## Metering Requirements

| System Size | Metering Type |
|-------------|--------------|
| <200 kW | Type 4 smart meter (interval metering) |
| 200 kW - 750 kW | Type 4 meter; may require CT metering |
| 750 kW - 5 MW | Type 1-3 metering (CT/VT); DNSP or metering coordinator installation |
| Export metering | Bidirectional meter required for all systems with export capability |

See also: [[Engineering-Standards]], [[Market-Data]], [[../Medium-Scale/Grid-Requirements]]

## Related in This Tier
- [[Engineering-Standards]]
- [[Industry-Insights]]
- [[Market-Data]]
- [[Safety-Compliance]]
