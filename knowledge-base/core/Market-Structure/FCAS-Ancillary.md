---
country: Australia
tier: all
category: market-structure
last_updated: 2026-08-20
status: verified
sources:
  - https://www.aemo.com.au/-/media/files/electricity/nem/security_and_reliability/ancillary_services/market-ancillary-service-specification---v80.pdf
  - https://flowpower.com.au/resources/frequency-control-ancillary-services-explained/
  - https://theenergy.co/article/how-frequency-control-ancillary-services-work-in-the-nem
  - https://satec-global.com.au/frequency-control-ancillary-services-fcas-precision-metering-for-battery-storage/
  - https://www.energy-storage.news/australias-ancillary-services-costs-coming-down-as-more-batteries-enter-market/
  - https://energyinnovationtoolkit.gov.au/article/regulatory-changes/very-fast-frequency-control-ancillary-services
tags:
  - australia
  - FCAS
  - ancillary-services
  - frequency-control
  - MASS
  - battery
  - NEM
---

> **Nav**: [[../_AU-Overview|Australia]] > **Market Structure** > **FCAS Ancillary**

# Frequency Control Ancillary Services (FCAS) -- NEM

## Overview

FCAS markets are a critical component of the NEM, maintaining system frequency at 50 Hz. [[../Regulatory-Bodies#AEMO|AEMO]] co-optimises energy and FCAS dispatch every 5 minutes to minimise total cost.

> **Jurisdiction boundary:** This page describes NEM FCAS under the NER and AEMO MASS. Western Australia's WEM procures Essential System Services under separate WEM instruments. The NT is also outside this NEM FCAS framework.

## The 10 FCAS Markets

The NEM operates **10 FCAS markets** (since **9 October 2023**, when the two Very Fast 1-second contingency services went live under **MASS v8.0**), divided into two categories.

### Contingency FCAS (8 markets)

Contingency services respond to sudden, unexpected events (e.g., generator trip, load loss). Since MASS v8.0 there are **four** raise/lower timeframes — the newest being the 1-second Very Fast service.

| Market | Direction | Response Time | Purpose |
|--------|-----------|--------------|---------|
| **Very Fast Raise (R1)** 🆕 | Raise | Within **1 second** | Fast arrest of frequency decline in a low-inertia grid; battery-dominated |
| **Very Fast Lower (L1)** 🆕 | Lower | Within **1 second** | Fast arrest of frequency rise |
| **Fast Raise (R6)** | Raise | Within 6 seconds | Arrest frequency decline after generation loss |
| **Fast Lower (L6)** | Lower | Within 6 seconds | Arrest frequency rise after load loss |
| **Slow Raise (R60)** | Raise | Within 60 seconds | Stabilise frequency after fast response |
| **Slow Lower (L60)** | Lower | Within 60 seconds | Stabilise frequency after fast response |
| **Delayed Raise (R5)** | Raise | Within 5 minutes | Restore frequency to normal band |
| **Delayed Lower (L5)** | Lower | Within 5 minutes | Restore frequency to normal band |

### Regulation FCAS (2 markets)

Regulation services manage continuous, small frequency deviations caused by normal supply-demand imbalance.

| Market | Direction | Control | Purpose |
|--------|-----------|---------|---------|
| **Regulation Raise** | Raise | AGC (Automatic Generation Control) | Continuously increase output to raise frequency |
| **Regulation Lower** | Lower | AGC | Continuously decrease output to lower frequency |

### Frequency Response Sequence

```
Event: Generator trips (loss of 500 MW)

Time 0s:   Frequency begins dropping
            ↓
0-1s:   Fast Raise (R6) activates
        ├── Batteries respond in <100 ms
        ├── Synchronous generator governors respond
        └── Frequency decline arrested

1-6s:   Fast Raise continues; Slow Raise (R60) begins activating
        ├── Additional generation ramping up
        └── Frequency stabilising

6-60s:  Slow Raise (R60) sustaining
        ├── Frequency returning toward 50 Hz
        └── Delayed Raise (R5) begins activating

60s-5min: Delayed Raise (R5) sustaining
          ├── Frequency restored to normal operating band
          └── Replacement generation dispatched by AEMO

Throughout: Regulation Raise continuously trims frequency
```

## Very Fast FCAS (Live since 9 Oct 2023)

The two 1-second Very Fast contingency services (**Very Fast Raise R1 / Very Fast Lower L1**) commenced on **9 October 2023** under **MASS v8.0**, taking the NEM to **10 FCAS markets**. Introduced to address declining system inertia as synchronous generators retire.

| Parameter | Detail |
|-----------|--------|
| Service | Very Fast Raise (R1) / Very Fast Lower (L1) |
| Response time | Within **1 second** |
| Status | ✅ **Live since 9 October 2023** (MASS v8.0) — no longer "emerging" |
| Technology | Grid-scale **batteries / fast inverters** are the dominant providers |
| Purpose | Arrest fast RoCoF events as synchronous inertia declines |

## Market Ancillary Service Specification (MASS)

The MASS is the technical specification that defines the requirements for FCAS participation.

> **Official source binding:** The 10 FCAS markets, the Very Fast R1/L1 services that commenced on 9 October 2023, and the MASS parameters below are bound to the **AEMO Market Ancillary Service Specification (MASS) v8.0** ([AEMO MASS v8.0 PDF](https://www.aemo.com.au/-/media/files/electricity/nem/security_and_reliability/ancillary_services/market-ancillary-service-specification---v80.pdf)).

### Key MASS Requirements

| Requirement | Detail |
|-------------|--------|
| Registration | Must be registered with AEMO as an ancillary service provider |
| Metering | High-speed metering required (50 ms resolution for contingency services) |
| Verification | AEMO testing to verify response capability |
| Availability | Must declare availability and maintain readiness to respond |
| Performance monitoring | AEMO monitors actual response vs declared capability |

### MASS Technical Parameters

| Service | Frequency Trigger | Minimum Response | Minimum Enablement |
|---------|-------------------|-----------------|-------------------|
| Very Fast Raise (R1) | <49.85 Hz | Full response within **1s** | 1 MW |
| Very Fast Lower (L1) | >50.15 Hz | Full response within **1s** | 1 MW |
| Fast Raise (R6) | <49.85 Hz | Full response within 6s | 1 MW |
| Fast Lower (L6) | >50.15 Hz | Full response within 6s | 1 MW |
| Slow Raise (R60) | <49.85 Hz | Full response within 60s | 1 MW |
| Slow Lower (L60) | >50.15 Hz | Full response within 60s | 1 MW |
| Delayed Raise (R5) | <49.85 Hz | Full response within 5 min | 1 MW |
| Delayed Lower (L5) | >50.15 Hz | Full response within 5 min | 1 MW |
| Regulation Raise | Continuous | AGC-following (4s setpoint) | 1 MW |
| Regulation Lower | Continuous | AGC-following (4s setpoint) | 1 MW |

### FCAS Trapezium

Each FCAS provider declares a "trapezium" defining the relationship between energy output and FCAS capability:

```
FCAS Capability (MW)
    |
Max |  ________
    | /        \
    |/          \
    +----+----+----> Energy Output (MW)
     Low  Enablement  High
     Breakpoint Limit  Breakpoint
```

The trapezium ensures FCAS capability varies correctly with energy dispatch level.

## Battery FCAS Participation

### Why Batteries Excel at FCAS

| Advantage | Detail |
|-----------|--------|
| Response speed | Sub-100 ms response (far exceeds MASS requirements) |
| Bidirectional | Can provide both raise and lower services simultaneously |
| No fuel cost | Marginal cost of FCAS provision is near-zero |
| Precision | Accurate, repeatable response |
| Scalable | Can register and provide from 1 MW upward |

### Battery FCAS Market Share

| Metric | Value |
|--------|-------|
| Battery FCAS market share | ~31% (FY2024) |
| Next largest (black coal) | ~21% |
| Next largest (hydro) | ~21% |
| Trend | Battery share growing as new BESS commissioned |

### Battery FCAS Considerations

| Challenge | Mitigation |
|-----------|-----------|
| State of charge (SOC) management | Must maintain sufficient SOC to sustain FCAS response; MASS requires demonstration of sustained capability |
| Degradation | FCAS cycling adds to battery throughput; optimise across energy and FCAS |
| Revenue volatility | FCAS prices declining as more batteries enter; diversify revenue streams |
| Metering requirements | 50 ms precision metering per MASS (e.g., SATEC metering solutions) |
| Co-optimisation | AEMO co-optimises energy and FCAS; battery dispatch balances both |

### Battery Revenue from FCAS (Indicative)

| Revenue Stream | Typical Annual Revenue (per MW) |
|---------------|-------------------------------|
| Regulation Raise | $30,000-60,000 |
| Regulation Lower | $15,000-30,000 |
| Contingency Raise (all 3) | $20,000-50,000 |
| Contingency Lower (all 3) | $10,000-25,000 |
| **Total FCAS revenue** | **$75,000-165,000/MW/year** |

Note: FCAS revenue is highly variable and declining as battery capacity grows. Early BESS entrants captured significantly higher revenues.

## FCAS Pricing

### How FCAS Prices Are Set

| Step | Detail |
|------|--------|
| 1. FCAS requirements | AEMO determines MW requirement for each service based on system conditions |
| 2. Bidding | FCAS providers submit price-quantity bids (10 bands, similar to energy) |
| 3. Co-optimisation | NEMDE co-optimises energy and FCAS to minimise total cost |
| 4. Clearing price | Marginal price of last FCAS MW enabled in each service |
| 5. Payment | All enabled FCAS providers paid the clearing price for their service |

### FCAS Price Trends

| Trend | Detail |
|-------|--------|
| Overall decline | FCAS prices declining as battery capacity grows and competition increases |
| Volatility | Occasional price spikes during system events (generator trips, islanding) |
| Fast services premium | Fast Raise/Lower typically higher than Slow and Delayed |
| Regulation premium | Regulation services generally higher due to continuous commitment |
| Regional variation | SA and QLD FCAS prices often higher due to interconnector constraints |

### FCAS Cost Allocation

| Cost Component | Allocation |
|---------------|-----------|
| Regulation costs | Allocated to generators based on "causer pays" principle (frequency deviation contribution) |
| Contingency costs | Allocated 50% to generators, 50% to customers (market customers) |
| Regional allocation | FCAS costs allocated to the region where the service is provided |

## FCAS and System Security

| Concept | Description |
|---------|-------------|
| Inertia | Stored kinetic energy in synchronous generators; declining as coal retires |
| System strength | Fault level at network nodes; declining with IBR growth |
| Rate of Change of Frequency (RoCoF) | How quickly frequency changes after a disturbance; managed by inertia and fast FCAS |
| Frequency Operating Standard (FOS) | AEMC-set standard defining normal frequency band (49.85-50.15 Hz) and contingency limits |

As the NEM transitions to higher renewable penetration, FCAS markets become increasingly critical for maintaining system security. Battery storage is the key technology enabling this transition.

See also: [[NEM-Overview]], [[WEM-Overview]], [[../Large-Scale-Generation/Grid-Requirements]], [[../Large-Scale-Generation/Market-Data]]
