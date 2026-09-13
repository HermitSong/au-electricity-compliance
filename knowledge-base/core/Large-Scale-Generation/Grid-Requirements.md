---
country: Australia
tier: large-scale
category: grid
last_updated: 2026-08-20
status: verified
sources:
  - https://www.aemc.gov.au/regulation/energy-rules/national-electricity-rules
  - https://www.aemo.com.au/energy-systems/electricity/national-electricity-market-nem/participate-in-the-market/network-connections
  - https://www.aemo.com.au/-/media/files/electricity/nem/security_and_reliability/ancillary_services/market-ancillary-service-specification---v80.pdf
  - https://www.aemo.com.au/energy-systems/electricity/national-electricity-market-nem/participate-in-the-market/network-connections/modelling-requirements
  - https://www.aemo.com.au/-/media/files/electricity/nem/network_connections/stage-3/connection-application-checklist.pdf
  - https://aemo.com.au/-/media/files/electricity/nem/network_connections/stage-6/generator-connection-r1-submission-checklist.pdf
  - https://www.aemo.com.au/-/media/files/electricity/nem/network_connections/model-acceptance-test-guideline-nov-2021.pdf
  - https://www.aemo.com.au/-/media/Files/Electricity/NEM/Network_Connections/Access-Standard-Assessment-Guide-20190131.pdf
  - https://www.aemc.gov.au/sites/default/files/content/ce6543aa-7b77-4105-8bc8-29670c078442/AECOM-report-EMT-and-RMS-Model-Requirements.pdf
  - https://aemo.com.au/-/media/files/stakeholder_consultation/consultations/nem-consultations/2025/psmg-and-data-sheets-consultation/final-documents/psmg-2025-final-report.pdf
  - https://www.aemo.com.au/-/media/files/stakeholder_consultation/consultations/nem-consultations/2023/gps-template/generator-performance-standards-template-change-marked-document.pdf
  - https://energy-rules.aemc.gov.au/ner
tags:
  - australia
  - large-scale
  - grid
  - NER
  - GPS
  - FCAS
  - MASS
---

> **Nav**: [[00-Home/Dashboard|Dashboard]] > [[../_AU-Overview|Australia]] > **Large-Scale Generation** > **Grid Requirements**

# Grid Connection Requirements -- Large-Scale Generation (>30 MW)

## NER Chapter 5 -- Network Connection

National Electricity Rules Chapter 5 governs the connection of generators and loads to the NEM transmission and distribution networks.

### Connection Types

| Type | Application | Process |
|------|-------------|---------|
| Registered Connection | Scheduled Generators >30 MW | Full Chapter 5 connection process |
| Semi-Scheduled Connection | Intermittent generation >30 MW (wind, solar) | Chapter 5 with semi-scheduled classification |
| Non-Scheduled Connection | Generation <30 MW or exempted | Simplified process; may use Chapter 5A |

### Connection Process (Chapter 5)

```
1. Connection Enquiry
   ├── Preliminary response from TNSP (within 20 business days)
   └── System strength and hosting capacity assessment

2. Connection Application
   ├── Detailed technical information
   ├── Proposed Generator Performance Standards
   ├── Power system studies (load flow, fault level, stability)
   └── TNSP response with connection offer

3. Connection Agreement
   ├── Negotiation of access standards (GPS)
   ├── Network augmentation requirements
   ├── Connection charges and cost allocation
   └── Execution of connection agreement

4. Detailed Design and Construction
   ├── Protection settings coordination
   ├── SCADA and communications integration
   └── Metering installation (NER Chapter 7)

5. Commissioning and Registration
   ├── R2 commissioning tests (AEMO witnessed)
   ├── GPS compliance testing
   ├── AEMO registration as Scheduled/Semi-Scheduled Generator
   └── Market participant registration
```

**Typical timeline:** 12-36 months from connection enquiry to registration.

---

## Connection Application (CA) — Detailed Requirements

The Connection Application (NER Clause 5.3.4) is the most critical and technically demanding stage of the Chapter 5 process. AEMO will not consider the application complete until **all** technical information requirements are satisfied.

### CA Submission Checklist

The following documents must be submitted to the connecting NSP and AEMO (per [AEMO Connection Application Checklist](https://www.aemo.com.au/-/media/files/electricity/nem/network_connections/stage-3/connection-application-checklist.pdf)):

| # | Document | NER Reference | Description |
|---|----------|---------------|-------------|
| 1 | **Project Description** | 5.3.4(b) | Site layout, single-line diagram, equipment specifications (inverters, transformers, switchgear) |
| 2 | **Proposed GPS Template** | 5.3.4(c), S5.2.5 | Completed GPS template indicating Automatic (A) or Negotiated (N) access for each standard |
| 3 | **GPS Compliance Studies** | 5.3.4A | Power system simulation results demonstrating compliance with each proposed access standard |
| 4 | **R1 Model Package** | S5.2.4 | PSS®E + PSCAD models with source code and validation reports (see Modelling section below) |
| 5 | **Schedule 5.5 Data** | S5.5.6 | Design and setting data sheets (per Power System Design and Setting Data Sheets 2025) |
| 6 | **Schedule 5.4 Data** | S5.4 | Plant technical data (ratings, impedances, time constants, protection settings) |
| 7 | **System Strength Impact Assessment** | 5.3.4B | Assessment of impact on system strength at the connection point |
| 8 | **Protection Coordination Study** | 5.3.4(d) | Proposed protection settings and coordination with existing network protection |
| 9 | **Power Quality Study** | S5.2.5.2 | Harmonic analysis, flicker assessment, voltage fluctuation study |
| 10 | **Commissioning Program** | 5.3.4(e) | Proposed commissioning timeline, hold-point schedule, R2 testing plan |
| 11 | **Project & Construction Program** | 5.3.4(f) | Project timeline with key milestones |

### GPS Template Requirements

The GPS template ([AEMO GPS Template](https://www.aemo.com.au/-/media/files/stakeholder_consultation/consultations/nem-consultations/2023/gps-template/generator-performance-standards-template-change-marked-document.pdf)) requires the Connection Applicant to:

1. Complete **Column 4** — propose either **Automatic Access (A)** or **Negotiated Access (N)** for each standard
2. Complete **Column 5** — provide the specific proposed performance level
3. Provide supporting evidence (simulation results) for each proposed standard
4. If proposing Negotiated Access, justify why Automatic Access cannot be met

> ⚠️ **2025 Package 1 Rule Change**: NER amendments effective 21 August 2025 have tightened access standards. Projects that had NOT received a connection enquiry response by this date must comply with the new, more stringent standards. Key changes include enhanced frequency response, stronger fault ride-through, and mandatory reactive power capability.

---

## R1 Power System Modelling Requirements

### Overview

All IBR projects (solar, wind, battery) must submit **two types of simulation models** to AEMO. This is governed by NER S5.2.4 and the **AEMO Power System Model Guidelines (PSMG) v3.0 (2025)**.

### Required Model Types

| Model Type | Software | Purpose | When Required |
|------------|----------|---------|---------------|
| **RMS Model** (Root Mean Square / Phasor) | **PSS®E** (Siemens PTI) | Electromechanical transient analysis — load flow, fault level, frequency stability, voltage stability, inter-area oscillations | **All generators** |
| **EMT Model** (Electromagnetic Transient) | **PSCAD™/EMTDC™** (Manitoba Hydro International) | Detailed switching-level simulation — inverter control behaviour, fault ride-through, harmonics, sub-synchronous oscillations, weak grid performance | **All IBR generators** (mandatory) |

> 📌 Both models must produce **consistent results for balanced events** (e.g., three-phase faults). Discrepancies will trigger AEMO rejection.

### R1 Model Package Contents

Per the [R1 Submission Checklist](https://aemo.com.au/-/media/files/electricity/nem/network_connections/stage-6/generator-connection-r1-submission-checklist.pdf):

| # | Deliverable | Detail |
|---|------------|--------|
| 1 | **PSS®E compiled model + libraries** | Dynamic simulation model files |
| 2 | **PSS®E source code (FORTRAN)** | Must be provided — AEMO does not accept black-box models |
| 3 | **PSS®E v34 AND v36 source code** | Both versions required from 4 Aug 2025; full transition by July 2026 |
| 4 | **PSCAD/EMTDC compiled model + libraries** | EMT model files and all associated component libraries |
| 5 | **Transfer function block diagrams** | Complete control system logic: PLL, current control loop, power control loop, voltage/reactive control, protection logic, MPPT (solar), pitch control (wind) |
| 6 | **Complete parameter/settings list** | Every tunable parameter for both PSS®E and PSCAD models |
| 7 | **PSS®E model validation report** | Comparison against measured data (factory test or field commissioning) for fault ride-through events |
| 8 | **PSCAD model validation report** | Same as above for EMT model |
| 9 | **Model user guide** | Operating instructions, initialization procedure, limitations |
| 10 | **Design data sheets** | Per Power System Design and Setting Data Sheets 2025 (NER S5.5.6) |

### Modelling Workflow (How to Do It)

```
Phase 1: Obtain OEM Base Models
├── Request PSS®E + PSCAD models from inverter/turbine OEM
│   (e.g., Huawei SUN2000, Sungrow, GoldWind, Vestas, CATL BESS)
├── Confirm model version compatibility:
│   ├── PSS®E v34 + v36 (both required from Aug 2025)
│   └── PSCAD v5.x (confirm with AEMO)
└── Obtain OEM model validation certificate (factory test data)

Phase 2: Plant-Level Model Integration
├── Aggregate single-unit model → full plant representation
│   ├── Number of inverters/turbines × unit model
│   ├── Collector network (MV cables, string transformers)
│   ├── Main transformer (HV/MV)
│   ├── Reactive power compensation (SVG, SVC, capacitor banks)
│   ├── BESS (if hybrid plant)
│   └── Plant-level controller (PPC / SCADA)
├── Obtain network model from TNSP
│   ├── Thevenin equivalent or detailed network at connection point
│   └── Fault level data, X/R ratio, SCR (Short Circuit Ratio)
└── Integrate plant model with network model

Phase 3: GPS Compliance Simulation
├── PSS®E Studies (RMS):
│   ├── Load flow analysis (normal and contingency)
│   ├── Short-circuit analysis (3-phase, SLG, LL faults)
│   ├── Frequency response (governor droop, inertial response)
│   ├── Voltage stability (P-V, Q-V curves)
│   ├── Small-signal stability (eigenvalue analysis)
│   └── Transient stability (fault scenarios per GPS)
├── PSCAD Studies (EMT):
│   ├── Fault ride-through (3-phase, SLG — 0V to 130%)
│   ├── Phase angle jump ride-through
│   ├── Harmonic analysis (THD, individual harmonics)
│   ├── Sub-synchronous oscillation screening
│   ├── Weak grid performance (low SCR scenarios)
│   ├── Active/reactive power step response
│   └── Islanding detection and anti-islanding
├── Cross-validation:
│   └── Verify PSS®E and PSCAD produce consistent results
│       for balanced three-phase events
└── Compile GPS compliance report (one section per S5.2.5.x clause)

Phase 4: Model Validation (with measured data)
├── Use factory acceptance test (FAT) data if available
├── Use commissioning test recordings (voltage/current waveforms)
├── Overlay model output vs. measured data
├── Acceptable accuracy: typically <5% deviation on key metrics
└── Produce Model Validation Report per AEMO Dynamic Model
    Acceptance Test Guideline v2

Phase 5: R1 Submission to AEMO + TNSP
├── Compile all deliverables per R1 Submission Checklist
├── Submit to connecting NSP and AEMO simultaneously
├── AEMO review period: typically 2-6 months
├── Expect 1-3 rounds of queries / revision requests
└── Once approved → proceed to Connection Agreement
```

### Common AEMO Rejection Reasons

| Issue | Description |
|-------|-------------|
| Black-box models | Source code not provided; AEMO cannot verify behaviour |
| PSS®E / PSCAD mismatch | Significant discrepancy between RMS and EMT results for balanced events |
| Missing fault ride-through validation | No measured data to validate model accuracy during voltage disturbances |
| Incomplete control diagrams | Missing PLL, current limiter, or protection logic block diagrams |
| Outdated PSS®E version | Not compatible with v34/v36 (post Aug 2025 requirement) |
| Inadequate weak-grid performance | Model fails at the projected SCR at the connection point |

---

## Key Regulatory & Compliance Documents

### AEMO Documents (Mandatory Reference)

| Document | Version | Local File | Online URL | Scope |
|----------|---------|-----------|------------|-------|
| **Power System Model Guidelines (PSMG)** | v3.0 (2025) | [[Attachments/AU/AEMO-PSMG-2025-Final-Report.pdf]] | [AEMO PSMG](https://aemo.com.au/-/media/files/stakeholder_consultation/consultations/nem-consultations/2025/psmg-and-data-sheets-consultation/final-documents/psmg-2025-final-report.pdf) | Defines all RMS/EMT model structure, behaviour, and documentation requirements |
| **Power System Design and Setting Data Sheets** | 2025 | — | [AEMO Modelling Requirements](https://www.aemo.com.au/energy-systems/electricity/national-electricity-market-nem/participate-in-the-market/network-connections/modelling-requirements) | Data submission templates per NER S5.5.6 |
| **Connection Application Checklist** | Current | [[Attachments/AU/AEMO-Connection-Application-Checklist.pdf]] | [CA Checklist](https://www.aemo.com.au/-/media/files/electricity/nem/network_connections/stage-3/connection-application-checklist.pdf) | Complete checklist of CA submission documents |
| **R1 Submission Checklist** | Current | — (blocked by CDN) | [R1 Checklist](https://aemo.com.au/-/media/files/electricity/nem/network_connections/stage-6/generator-connection-r1-submission-checklist.pdf) | Detailed checklist for R1 model package |
| **Dynamic Model Acceptance Test Guideline** | v2 (2021) | [[Attachments/AU/AEMO-DMAT-Guideline-v2.pdf]] | [DMAT Guideline](https://www.aemo.com.au/-/media/files/electricity/nem/network_connections/model-acceptance-test-guideline-nov-2021.pdf) | How to validate models against measured data |
| **Access Standard Assessment Guide** | 2019 | [[Attachments/AU/AEMO-Access-Standard-Assessment-Guide.pdf]] | [Assessment Guide](https://www.aemo.com.au/-/media/Files/Electricity/NEM/Network_Connections/Access-Standard-Assessment-Guide-20190131.pdf) | How AEMO evaluates proposed GPS levels |
| **GPS Template** | Latest | [[Attachments/AU/AEMO-GPS-Template.pdf]] | [GPS Template](https://www.aemo.com.au/-/media/files/stakeholder_consultation/consultations/nem-consultations/2023/gps-template/generator-performance-standards-template-change-marked-document.pdf) | Official template for proposing access standards |
| **Market Ancillary Service Specification (MASS)** | v8.0 | — (blocked by CDN) | [MASS](https://www.aemo.com.au/-/media/files/electricity/nem/security_and_reliability/ancillary_services/market-ancillary-service-specification---v80.pdf) | Technical requirements for FCAS participation |
| **2025 Power System Stability Guidelines** | Draft/Final 2025 | — | [Stability Guidelines Consultation](https://www.aemo.com.au/consultations/current-and-closed-consultations/2025-power-system-stability-guidelines) | System stability requirements and obligations |

### AEMC / NER Documents (Legislative Authority)

| Document | Reference | Local File | Online URL | Scope |
|----------|-----------|-----------|------------|-------|
| **National Electricity Rules (Chapter 5 within)** | **Consolidated v251 (23 Jul 2026)** — current | [[Attachments/AU/NER-v251-Full.pdf]] (full NER; Ch.5 within) | [NER live portal (always current)](https://energy-rules.aemc.gov.au/ner) · [AEMC NER](https://www.aemc.gov.au/regulation/energy-rules/national-electricity-rules) | Connection process (5.3), access standards (S5.2), data requirements (S5.4, S5.5) |
| **NER Schedule 5.2** | S5.2.5 | Contained in NER Ch.5 above | — | Generator Performance Standards (all technical requirements) |
| **NER Schedule 5.4** | S5.4 | Contained in NER Ch.5 above | — | Plant technical data requirements |
| **NER Schedule 5.5** | S5.5.6 | Contained in NER Ch.5 above | — | Design and setting data requirements |
| **Package 1 Rule 2025** | ERC0393 | — | [AEMC Rule Change](https://www.aemc.gov.au/rule-changes/generating-system-model-guidelines) | Improved access standards effective 21 Aug 2025 |
| **EMT and RMS Model Requirements Report** | AECOM Report | [[Attachments/AU/AECOM-EMT-RMS-Model-Requirements-Report.pdf]] | [EMT/RMS Report](https://www.aemc.gov.au/sites/default/files/content/ce6543aa-7b77-4105-8bc8-29670c078442/AECOM-report-EMT-and-RMS-Model-Requirements.pdf) | Independent review of modelling requirements |

### TNSP-Specific Documents (varies by state)

| TNSP | Coverage | Key Document |
|------|----------|-------------|
| **Transgrid** | NSW, ACT | [System Security Specification for Synchronous Machines](https://www.transgrid.com.au/media/aygl21z2/2406-transgrid_system-security-specification-for-synchronous-machines.pdf) |
| **AusNet Services** | VIC | AusNet Connection Process Guide |
| **Powerlink** | QLD | Powerlink Connection Standards |
| **ElectraNet** | SA | ElectraNet Connection Guideline |
| **TasNetworks** | TAS | TasNetworks Generator Connection Guide |
| **Western Power** | WA (WEM) | Western Power Technical Rules (separate from NEM) |

### Industry Reference (Non-Mandatory but Recommended)

| Resource | Publisher | URL |
|----------|----------|-----|
| Navigating AEMO Requirements for Grid Connection Studies | Partum Engineering | [Guide](https://www.partumengineering.com.au/news/navigating-aemo-requirements-for-grid-connection-studies/) |
| Grid Connection: Meeting AEMO Simulation Model Requirements | PV Magazine AU | [Article](https://www.pv-magazine-australia.com/2021/03/03/grid-connection-meeting-the-new-aemo-requirements-for-simulation-model/) |
| Connections Reform Initiative Update (Dec 2025) | Clean Energy Council | [CEC Update](https://cleanenergycouncil.org.au/news-resources/connections-reform-initiative-december-2025-update) |
| R1 Capability Assessment Guideline Submission | Transgrid | [Submission (PDF)](https://www.transgrid.com.au/media/5tojoqpc/transgrid-submission-to-r1-capability-assessment-guideline_20-05-2025_1.pdf) |
| Grid Integration and GPS Studies of Renewables with PSCAD | Monash University | [Course PDE1001](https://www.monash.edu/study/courses/find-a-course/grid-integration-and-gps-studies-of-renewables-using-pscad-pde1001) |

---

## Generator Performance Standards (GPS) -- NER S5.2.5

Schedule 5.2.5 of the NER defines the technical performance requirements that generators must meet. Each standard has three levels:

| Level | Description |
|-------|-------------|
| Automatic Access | Meets the standard without negotiation |
| Negotiated Access | Agreed performance between generator and NSP/AEMO |
| Minimum Access | Lowest acceptable performance; must be exceeded |

### Key GPS Categories

#### S5.2.5.1 -- Reactive Power Capability

- Must provide reactive power support within a defined power factor range
- Automatic access: 0.395 lagging to 0.395 leading (at rated MW)
- Minimum access: voltage control capability within +/-5% of normal voltage

#### S5.2.5.2 -- Quality of Electricity Generated

- Harmonic distortion limits per AS/NZS 61000.3.6
- Voltage fluctuation and flicker limits
- Negative sequence current limits

#### S5.2.5.3 -- Response to Frequency Disturbances

- Must remain connected and generating during frequency events
- Operating range: 47 Hz to 52 Hz (continuous)
- Extended range: 47 Hz to 52 Hz for defined durations
- Frequency response capability (governor response or equivalent)

#### S5.2.5.4 -- Response to Voltage Disturbances

- Fault ride-through capability (symmetric and asymmetric faults)
- Must remain connected for voltage down to 0% at the connection point for defined durations
- Automatic access: 15 cycles at zero voltage (transmission-connected)

#### S5.2.5.5 -- Active Power Control

- Active power ramping capability
- Frequency response (droop) settings
- Power system stabilizer (PSS) function for synchronous generators
- Automatic generation control (AGC) interface for dispatch

#### S5.2.5.11 -- Power System Stability

- Generators must not adversely affect power system stability
- Sub-synchronous resonance analysis required
- EMT (electromagnetic transient) modelling for IBR (inverter-based resources)

### IBR-Specific Requirements

Since 2023, AEMO has increased focus on inverter-based resource (IBR) performance:

- Grid-forming inverter capability encouraged (not yet mandated for all)
- Phase jump ride-through requirements
- System strength remediation obligations
- Detailed EMT models required for connection studies

## Automatic Generation Control (AGC)

Generators with AGC capability participate in AEMO's central dispatch:

| Element | Requirement |
|---------|-------------|
| SCADA Interface | 4-second data refresh to AEMO |
| Dispatch Target | Must follow AEMO dispatch targets within tolerance band |
| Ramp Rate | Must declare ramp rates; dispatch within declared range |
| Regulation FCAS | AGC-enabled generators can provide [[../Market-Structure/FCAS-Ancillary|regulation FCAS]] |
| Conformance | AEMO monitors dispatch conformance; non-conformance triggers investigation |

## Market Ancillary Service Specification (MASS)

The MASS defines technical requirements for participation in [[../Market-Structure/FCAS-Ancillary|FCAS markets]].

### FCAS Enablement Requirements

| Service | Response Time | Sustain Duration | Key MASS Requirement |
|---------|--------------|-----------------|---------------------|
| Fast Raise (R6) | 1 second | 6 seconds | Must arrest frequency decline within 1s |
| Fast Lower (L6) | 1 second | 6 seconds | Must arrest frequency rise within 1s |
| Slow Raise (R60) | 6 seconds | 60 seconds | Stabilise frequency within 6s |
| Slow Lower (L60) | 6 seconds | 60 seconds | Stabilise frequency within 6s |
| Delayed Raise (R5) | 60 seconds | 5 minutes | Restore frequency within 60s |
| Delayed Lower (L5) | 60 seconds | 5 minutes | Restore frequency within 60s |
| Regulation Raise | Continuous | Continuous | AGC-following raise service |
| Regulation Lower | Continuous | Continuous | AGC-following lower service |

### Battery FCAS Participation

Batteries are particularly well-suited for FCAS due to sub-second response times. Requirements:
- Must demonstrate response capability through AEMO testing
- State of charge management to sustain service delivery
- Precision metering at 50 ms resolution (per SATEC metering requirements)
- Batteries held a 31% FCAS market share in FY2024

## System Strength

AEMO's system strength framework requires:

- **Fault Level Shortfall Declaration** -- AEMO may declare a fault level shortfall at a node
- **System Strength Remediation** -- Connecting generators may be required to provide system strength (synchronous condensers, grid-forming inverters)
- **System Strength Service Provider (SSSP)** -- TNSPs appointed as SSSP to maintain minimum fault levels

See also: [[Engineering-Standards]], [[Market-Data]], [[../Market-Structure/NEM-Overview]], [[../Market-Structure/FCAS-Ancillary]]

## Related in This Tier
- [[Engineering-Standards]]
- [[Industry-Insights]]
- [[Market-Data]]
- [[Safety-Compliance]]
