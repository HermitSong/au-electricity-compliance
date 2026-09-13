---
country: Australia
tier: large-scale
category: market
last_updated: 2026-08-20
status: verified
sources:
  - https://www.aemo.com.au/energy-systems/electricity/national-electricity-market-nem/data-nem/data-dashboard-nem
  - https://leadingedgeenergy.com.au/blog/electricity-market-review-latest/
  - https://www.aer.gov.au/system/files/2025-08/State%20of%20the%20energy%20market%202025%20-%20Chapter%202%20-%20National%20Electricity%20Market.pdf
  - https://coremarkets.co/resources/market-prices
  - https://www.ecovantage.com.au/energy-certificate-market-update/
  - https://www.energy-storage.news/australias-ancillary-services-costs-coming-down-as-more-batteries-enter-market/
tags:
  - australia
  - large-scale
  - market
  - NEM
  - spot-price
  - LGC
  - FCAS
  - CIS
---

> **Nav**: [[00-Home/Dashboard|Dashboard]] > [[../_AU-Overview|Australia]] > **Large-Scale Generation** > **Market Data**

# Market Data -- Large-Scale Generation

## NEM Spot Prices by Region

### Recent Average Spot Prices (A$/MWh)

| Region | Feb 2026 | Jan 2026 | Nov 2025 | Trend |
|--------|----------|----------|----------|-------|
| NSW | $83.76 | $67.22 | ~$55 | Volatile; summer peaks |
| QLD | $69.87 | ~$60 | ~$50 | Moderate; solar suppression in daytime |
| VIC | $45.06 | $38.55 | ~$40 | Lowest mainland region; high wind + solar |
| SA | $56.00 | ~$50 | ~$45 | Declining; battery impact on peaks |
| TAS | ~$50 | ~$45 | $40.51 | Hydro-dependent; seasonal |

### Market Price Settings

| Parameter | Value (FY2025-26) |
|-----------|------------------|
| Market Price Cap (MPC) | $20,300/MWh |
| Market Floor Price | -$1,000/MWh |
| Cumulative Price Threshold (CPT) | ~$1,612,200 |
| Administered Price Cap | $600/MWh (triggered when CPT breached) |

### 2026 Futures Contracts (Indicative)

| Region | CAL 2026 Futures |
|--------|-----------------|
| NSW | ~$120/MWh |
| VIC | ~$77/MWh |
| QLD | ~$95/MWh |
| SA | ~$85/MWh |

Note: Futures prices subject to significant volatility and reflect forward expectations, not guaranteed outcomes.

## Certificate Prices

### LGCs (Large-scale Generation Certificates)

| Vintage | Price (A$) | Date |
|---------|-----------|------|
| Spot (Current) | ~$2.95 | Apr 2026 |
| CAL 2026 | ~$3.45-3.60 | Apr 2026 |
| CAL 2027 | ~$3.45-3.60 | Apr 2026 |
| CAL 2028-2030 | ~$3.00 | Apr 2026 |

LGC prices have declined significantly from historic highs (>$80 in 2018) as the LRET has been effectively met with surplus certificates in the market.

### STCs (Small-scale Technology Certificates)

| Parameter | Value |
|-----------|-------|
| STC Price (spot) | ~$38-39 |
| STC Clearing House Price | $40 (effective ceiling) |
| Small-scale Technology Percentage (STP) | Set annually by CER |

One STC is created per MWh of deemed renewable electricity over the system's lifetime (using zone-based deeming periods).

See also: [[../Residential/Market-Data]] for detailed STC economics.

## Capacity Investment Scheme (CIS)

The Australian Government's Capacity Investment Scheme is the primary mechanism for underwriting new generation and storage investment.

| Parameter | Detail |
|-----------|--------|
| Mechanism | Revenue underwriting (CfD-style collar: revenue floor / ceiling clawback) |
| Target | **40 GW by 2030** (uplifted from 32 GW on **29 July 2025**): ~26 GW renewable generation + ~14 GW dispatchable/clean storage |
| Eligible Technologies | Wind, solar, battery storage, pumped hydro |
| Contract Tenor | Up to 15 years |
| Delivery | DCCEEW underwriting tenders (revenue floor/ceiling contracts) |
| WA Extension | CIS design paper released for WEM adaptation |

The CIS replaces the former Underwriting New Generation Investments (UNGI) program and provides revenue certainty through a contract-for-difference structure.

## FCAS Prices

### Average FCAS Prices (Indicative, A$/MW/hr)

| Service | Q4 2025 Average | Trend |
|---------|----------------|-------|
| Regulation Raise | ~$15-25 | Declining as battery capacity grows |
| Regulation Lower | ~$8-15 | Declining |
| Contingency Raise 6s | ~$5-12 | Volatile; declining trend |
| Contingency Raise 60s | ~$3-8 | Declining |
| Contingency Raise 5min | ~$2-5 | Stable |
| Contingency Lower 6s | ~$2-6 | Declining |
| Contingency Lower 60s | ~$1-4 | Stable |
| Contingency Lower 5min | ~$1-3 | Stable |

Key trend: FCAS prices declining as more battery storage enters the market. Batteries held ~31% FCAS market share in FY2024, ahead of coal (21%) and hydro (21%).

## Revenue Stacking for Large-Scale Projects

Typical revenue streams for a utility-scale battery or hybrid project:

| Revenue Stream | Mechanism |
|---------------|-----------|
| Energy Arbitrage | Buy low (daytime solar surplus), sell high (evening peak) |
| FCAS | Fast frequency response services ([[../Market-Structure/FCAS-Ancillary|10 FCAS markets]], incl. 1-sec R1/L1) |
| CIS Revenue | Floor price guarantee from government |
| LGCs | Certificate revenue for renewable generation |
| Network Services | TNSP contracts for system strength, voltage support |
| Corporate PPA | Long-term offtake with C&I buyer |

See also: [[Grid-Requirements]], [[Industry-Insights]], [[../Market-Structure/NEM-Overview]], [[../Market-Structure/FCAS-Ancillary]]

## Related in This Tier
- [[Engineering-Standards]]
- [[Grid-Requirements]]
- [[Industry-Insights]]
- [[Safety-Compliance]]
