---
country: Australia
tier: all
category: market-structure
last_updated: 2026-04-03
status: draft
sources:
  - https://www.aemo.com.au/energy-systems/electricity/wholesale-electricity-market-wem/about-the-wholesale-electricity-market-wa-wem
  - https://www.erawa.com.au/markets/wholesale-electricity-market
  - https://www.wa.gov.au/government/document-collections/wholesale-electricity-market-rules
  - https://modoenergy.com/research/en/australia-introduction-wem-wholesale-electricity-market
  - https://www.baringa.com/en/insights/low-carbon-capital/australia-wholesale-electricity-market-developments/
tags:
  - australia
  - WEM
  - market-structure
  - capacity-mechanism
  - Western-Australia
---

> **Nav**: [[../_AU-Overview|Australia]] > **Market Structure** > **WEM Overview**

# Western Australia Wholesale Electricity Market (WEM)

## Market Overview

The WEM serves the South West Interconnected System (SWIS) in Western Australia, which is electrically isolated from the NEM. It operates as a hybrid capacity + energy market, distinct from the NEM's energy-only design.

> **Jurisdiction boundary:** This page concerns the SWIS/WEM only. It does not govern other isolated WA systems, any NEM region, or the Northern Territory. NER, NECF and NEM FCAS terminology must not be substituted for the controlling WA instruments.

### Key Statistics

| Parameter | Value |
|-----------|-------|
| Coverage | South West Interconnected System (SWIS), WA |
| Geographic span | Perth to Kalgoorlie; Albany to Geraldton |
| Peak demand | ~4.5 GW |
| Installed capacity | ~10 GW (including rooftop solar) |
| Market operator | [[../Regulatory-Bodies#AEMO\|AEMO]] (since 2016) |
| Economic regulator | Economic Regulation Authority (ERA) |
| Rule setter | WA Government (Coordinator of Energy) |
| Network operator | Western Power (SWIS) |

## Market Structure

The WEM has three interacting market components:

### 1. Reserve Capacity Mechanism (RCM)

The RCM is WA's capacity market, ensuring sufficient generation capacity to meet peak demand plus a reserve margin.

| Element | Detail |
|---------|--------|
| Purpose | Ensure generation adequacy; capacity payments to generators |
| Planning horizon | 2 years ahead (Reserve Capacity Cycle) |
| Capacity requirement | Set by AEMO based on 10% Probability of Exceedance (POE) demand forecast + reserve margin |
| Capacity price | Set administratively based on the cost of a new reference technology |
| Reference technology | 200 MW / 1,200 MWh lithium-ion battery (updated September 2025, from 200 MW / 800 MWh) |
| Capacity credits | Assigned to generators based on certified capacity |
| Payment | Annual capacity credits x capacity price |

### Capacity Credit Allocation

| Technology | Capacity Credit Method |
|-----------|----------------------|
| Conventional (gas, coal) | Nameplate capacity adjusted for forced outage rate |
| Wind | Relevant Level Method (based on historical contribution during peak periods) |
| Solar | Relevant Level Method; declining credits as solar penetration increases |
| Battery | Certified based on sustained power output and duration |
| Demand-side management | Certified based on demonstrated reduction capability |

### New Flexibility Product

The 2025 RCM review introduced a new flexibility product:
- Designed to meet steepest operational ramp periods
- Targets fast-ramping resources (batteries, gas peakers)
- Provides additional capacity payments for ramp capability
- Benefits eligible BESS projects with greater-than-anticipated revenue

### 2. Short-Term Energy Market (STEM)

| Element | Detail |
|---------|--------|
| Purpose | Day-ahead bilateral energy trading |
| Operation | Day-ahead market with voluntary participation |
| Pricing | Bilateral; STEM clearing price set by supply-demand intersection |
| Settlement | Net settlement against bilateral contract positions |

### 3. Balancing Market

| Element | Detail |
|---------|--------|
| Purpose | Real-time energy balancing (dispatch) |
| Dispatch interval | 5 minutes |
| Pricing | Marginal pricing at Muja 330 kV reference node |
| Price cap | $600/MWh (significantly lower than NEM's $20,300) |
| Price floor | -$1,000/MWh |
| Participation | Mandatory for registered facilities |

## Reform Timeline

The WEM has undergone significant reform since 2020:

### Completed Reforms

| Date | Reform |
|------|--------|
| October 2023 | New Market Rules commenced |
| October 2023 | 5-minute dispatch intervals (from 30 minutes) |
| October 2023 | Constrained access network model introduced |
| October 2023 | Security-constrained economic dispatch (SCED) |
| October 2023 | Co-optimisation of energy and Essential System Services (ESS) |
| 2024 | Essential System Services market launched (replaces ancillary services) |
| September 2025 | RCM reference technology updated to 200 MW / 1,200 MWh battery |

### Upcoming / In Progress

| Date | Reform |
|------|--------|
| 2025-2026 | Flexibility product implementation under RCM |
| 2025-2026 | Capacity Investment Scheme (CIS) adapted for WEM |
| 2026+ | Real-time market enhancements |
| 2026+ | DER integration rules (managing rooftop solar growth) |

## Essential System Services (ESS)

The WEM's ancillary services (called Essential System Services) were reformed in 2023-2024:

| Service | Description |
|---------|-------------|
| Regulation Raise | Continuous frequency regulation (increase generation) |
| Regulation Lower | Continuous frequency regulation (decrease generation) |
| Contingency Reserve Raise | Response to sudden generation loss |
| Contingency Reserve Lower | Response to sudden load loss |
| Rate of Change of Frequency (RoCoF) | Inertia and fast frequency response |
| System Restart | Black start capability |

## Key Differences: WEM vs NEM

| Aspect | WEM | NEM |
|--------|-----|-----|
| Capacity market | Yes (RCM) | No (energy-only; CIS is government scheme, not market mechanism) |
| Price cap (energy) | $600/MWh | $20,300/MWh |
| Network model | Constrained access (since 2023) | Constrained access |
| Regions | Single region (SWIS) | 5 regions |
| Interconnection | Isolated (no interconnectors) | Interconnected (5 regions) |
| Scale | ~10 GW capacity | ~70+ GW capacity |
| DER management | Emergency Solar Management scheme | AEMO backstop mechanism |

## Market Participants (WEM)

| Type | Examples |
|------|---------|
| State-owned generators | Synergy (dominant generator/retailer) |
| Private generators | Alinta Energy, NewGen Power, Collgar Wind Farm |
| Network operator | Western Power |
| Retailer (incumbent) | Synergy |
| Contestable retailers | Alinta Energy, Kleenheat, Perth Energy, others |

Note: Synergy holds a dominant position as both the largest generator and the default retailer, which is unique compared to the NEM's more competitive structure.

## Capacity Investment Scheme (CIS) -- WEM Adaptation

The Australian Government's CIS is being adapted for the WEM:

| Element | Detail |
|---------|--------|
| Design paper | Released 2025 |
| Mechanism | Revenue underwriting (consistent with NEM CIS) |
| Eligible technologies | Renewables and battery storage |
| Interaction with RCM | CIS revenue additional to capacity credits |
| Exclusion | Projects receiving WA Government revenue support ineligible |

See also: [[NEM-Overview]], [[FCAS-Ancillary]], [[../Regulatory-Bodies]], [[../_AU-Overview]]
