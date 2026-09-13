---
country: Australia
tier: all
category: market-structure
last_updated: 2026-08-20
status: verified
sources:
  - https://www.aemo.com.au/-/media/files/electricity/nem/national-electricity-market-fact-sheet.pdf
  - https://www.aemc.gov.au/regulation/energy-rules/national-electricity-rules
  - https://www.aer.gov.au/system/files/2025-08/State%20of%20the%20energy%20market%202025%20-%20Chapter%202%20-%20National%20Electricity%20Market.pdf
  - https://en.wikipedia.org/wiki/National_Electricity_Market
tags:
  - australia
  - NEM
  - market-structure
  - dispatch
  - settlement
  - price-cap
---

> **Nav**: [[../_AU-Overview|Australia]] > **Market Structure** > **NEM Overview**

# National Electricity Market (NEM) Overview

> **Jurisdiction boundary:** The NEM is a wholesale electricity and power-system framework covering Queensland, New South Wales, Victoria, South Australia and Tasmania, with the ACT participating through the NSW region. It does not include Western Australia or the Northern Territory. Victoria is in the NEM but is outside the National Energy Customer Framework (NECF) for retail regulation.

## Market Design

The NEM is one of the world's longest interconnected power systems, spanning ~5,000 km from Queensland to Tasmania. It is a gross pool, energy-only market with mandatory participation for most generators.

### Key Design Features

| Feature | Detail |
|---------|--------|
| Market type | Gross pool; energy-only (no separate capacity market in NEM) |
| Dispatch interval | 5 minutes |
| Settlement interval | 5 minutes (changed from 30 minutes in October 2021) |
| Pricing | Locational marginal pricing at regional reference nodes |
| Participation | Mandatory for generators >5 MW (exemptions available) |
| Operator | [[../Regulatory-Bodies#AEMO\|AEMO]] |
| Rule maker | [[../Regulatory-Bodies#AEMC\|AEMC]] |
| Economic regulator | [[../Regulatory-Bodies#AER\|AER]] |

## Five NEM Regions

| Region | Regional Reference Node (RRN) | Key Generation |
|--------|------------------------------|---------------|
| NSW (New South Wales) | Sydney West 330 kV | Coal (declining), solar, wind, hydro, gas |
| QLD (Queensland) | South Pine 275 kV | Coal, gas, solar (high resource), wind |
| VIC (Victoria) | Thomastown 220 kV | Brown coal (declining), wind, solar, gas |
| SA (South Australia) | Torrens Island 66 kV | Wind, solar, gas, battery storage |
| TAS (Tasmania) | George Town 220 kV | Hydro (dominant), wind |

### Interconnectors

| Interconnector | Regions | Capacity (Nominal) |
|---------------|---------|-------------------|
| QNI (Queensland-NSW Interconnector) | QLD-NSW | ~600 MW |
| Terranora | QLD-NSW | ~210 MW |
| VIC-NSW | VIC-NSW | ~1,600 MW |
| Heywood | VIC-SA | ~650 MW |
| Murraylink | VIC-SA | ~220 MW |
| Basslink | VIC-TAS | ~500 MW (DC cable) |
| EnergyConnect (under construction) | NSW-SA | ~800 MW (expected ~2027) |
| Marinus Link (proposed) | VIC-TAS | ~1,500 MW |
| HumeLink (under construction) | Snowy-Sydney-Melbourne | ~2,200 MW equivalent |

## 5-Minute Settlement

### How It Works

```
Dispatch Process (every 5 minutes):

1. Generators submit price-quantity bids (10 price bands per unit)
   ├── Bid range: -$1,000/MWh to $20,300/MWh (bid cap = MPC, FY2025-26)
   └── Bids can be rebid in real-time with reason

2. AEMO's NEMDE (NEM Dispatch Engine) runs optimisation
   ├── Minimises cost of meeting demand
   ├── Respects network constraints
   ├── Co-optimises energy and FCAS
   └── Determines dispatch targets and prices

3. Dispatch targets sent to generators
   ├── Generators must follow targets within tolerance band
   └── Non-conformance triggers investigation

4. Spot price set at each RRN
   ├── Price = marginal cost of next MW of demand
   └── All generators in region paid the same spot price
```

### Settlement

| Parameter | Value |
|-----------|-------|
| Settlement interval | 5 minutes (aligned with dispatch since October 2021) |
| Payment basis | All energy settled at the 5-minute dispatch interval price |
| Billing cycle | Weekly. Normally final statement within 7 business days; payment is the later of the ninth business day and two business days after final-statement receipt. Apply the billing-week transitional calendar during the August-October 2026 SSC transition. See [[Settlement-Prudential]]. |
| Prudential requirements | MCL = Outstandings Limit + Prudential Margin (NER Ch.3 r.3.3); SSC lowers required credit support — see [[Settlement-Prudential]] |

## Price Caps and Floors

### Current Settings (FY2025-26)

| Parameter | Value | Set By |
|-----------|-------|--------|
| Market Price Cap (MPC) | $20,300/MWh | [[../Regulatory-Bodies#AEMC\|AEMC]] (CPI-adjusted annually) |
| Market Floor Price | -$1,000/MWh | AEMC |
| Cumulative Price Threshold (CPT) | $1,823,600 (7-day rolling, FY2025-26) | AEMC |
| Administered Price Cap (APC) | $600/MWh (admin floor -$600/MWh) | Triggered when CPT exceeded |
| Bid cap (max generator bid) | $20,300/MWh (= MPC) | Maximum generator bid price |

### How Price Caps Work

```
Normal Operation:
  Spot price range: -$1,000 to +$20,300/MWh (per dispatch interval)

If rolling 7-day sum of spot prices exceeds CPT:
  → Administered Price Period declared
  → Prices capped at $600/MWh
  → Compensation claims available for generators dispatched below cost

Market Price Cap:
  → Settlement price cannot exceed $20,300/MWh in any interval
```

## Dispatch Process

### Generator Bidding

| Element | Detail |
|---------|--------|
| Bid structure | 10 price-quantity bands per generating unit |
| Price range | -$1,000/MWh to bid cap |
| Rebidding | Allowed at any time with stated reason |
| Bidding and rebidding | Since 1 July 2016, NER clauses 3.8.22 and 3.8.22A use objective rebidding and false-or-misleading controls; the earlier good-faith test is historical only |
| AEMO monitoring | AER monitors bidding behaviour for compliance |

### Demand Forecasting

| Forecast | Timeframe | Use |
|----------|-----------|-----|
| Pre-dispatch (PD) | 5 min to 40 hours ahead | Generator scheduling; price discovery |
| Short-term PASA | 6 days ahead | Reliability assessment |
| Medium-term PASA | 2 years ahead | Outage coordination; investment signals |

### Constraint Management

| Type | Description |
|------|-------------|
| Thermal constraints | Transmission line and transformer ratings |
| Voltage constraints | Voltage stability limits |
| Transient stability | System stability during faults |
| Oscillatory stability | Damping of power system oscillations |
| System strength | Minimum fault level requirements |
| Inertia | Minimum system inertia for frequency management |

## Reliability Framework

| Mechanism | Description |
|-----------|-------------|
| Reliability Standard | Maximum 0.002% unserved energy (USE) per region per year |
| Reliability Forecast | AEMO publishes annual ESOO (Electricity Statement of Opportunities) |
| RERT | Reliability and Emergency Reserve Trader -- AEMO contracts emergency reserves |
| Interim Reliability Measure | Ministerial power to direct AEMO procurement if reliability at risk |
| Capacity Investment Scheme (CIS) | Government investment underwriting for new capacity |

## Market Participants

| Type | Count (Approx.) | Role |
|------|-----------------|------|
| Scheduled Generators | ~100 | Dispatchable generation; follow dispatch targets |
| Semi-Scheduled Generators | ~200 | Wind/solar >30 MW; dispatched when constrained |
| Non-Scheduled Generators | ~500 | <30 MW or exempted; no dispatch obligation |
| Market Customers | ~50 | Retailers and large users buying from the pool |
| TNSPs | 5 (one per region) | Transmission network service providers |
| DNSPs | ~13 | Distribution network service providers |

## Official Source Binding

> The **$20,300 MPC**, CPT and bid cap are bound to the **AEMC** annual CPI-indexation settings. The nine-business-day SSC settlement reform is bound to **AEMC ERC0384**, [[official-documents/market-core-documents/AEMC-SSC-ERC0384-Final-Determination.pdf]], and [[Settlement-Prudential]]. The governing rules are **NER v251** at the [AEMC Energy Rules portal](https://energy-rules.aemc.gov.au/ner). The 10 FCAS markets are documented in [[FCAS-Ancillary]].

See also: [[FCAS-Ancillary]], [[WEM-Overview]], [[../Regulatory-Bodies]], [[../Large-Scale-Generation/Market-Data]]
