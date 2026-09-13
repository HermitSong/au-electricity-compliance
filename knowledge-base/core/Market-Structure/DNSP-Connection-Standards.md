---
country: Australia
type: market-structure
category: dnsp-connection
last_updated: 2026-08-20
status: verified
audience: engineering, product, business-development
tags: [australia, DNSP, embedded-generation, connection-standard, SCADA, DNP3, IEC-61850, Modbus, TS133, TS134, NS194, PDI5000, STNW, CPPAL, VEBM, DOE]
sources:
  - https://www.ausgrid.com.au/-/media/Documents/Technical-Documentation/NS/NS194.pdf
  - https://www.energex.com.au/__data/assets/pdf_file/0020/1072550/STNW1175-Standard-for-HV-EG-Connections.pdf
  - https://media.powercor.com.au/wp-content/uploads/2025/03/05100744/CPPAL-ST-2008.2-LV-EG-Network-Access-Standard-Capacity-Greater-Than-200kVA.pdf
  - https://www.ausnetservices.com.au/-/media/project/ausnet/corporate-website/files/renewable-solutions/industry/5000kw-or-greater/download-block-update/embedded-generation-guidelines-sop-33-05_issue-5---jul-2023.pdf
  - https://www.tasnetworks.com.au/embedded-generation
---

> **Nav**: [[../_AU-Overview|Australia]] > **Market Structure** > **DNSP Connection Standards**

# DNSP Embedded-Generation Connection and SCADA Interface Comparison

> Verified to August 2026. Each distribution network service provider (DNSP) publishes its own embedded-generation (EG) connection standards and SCADA or telemetry requirements. Document identifiers, protocols, RTU ownership, control terminology, and failure responses are not uniform. SA Power Networks (SAPN) has the deepest source coverage in this knowledge base and is therefore used as the comparison baseline.

> **Jurisdiction boundary:** NSW, ACT, QLD, SA, VIC and TAS connections sit within the NEM framework, although each DNSP applies its own connection instruments and Victoria may add state-specific emergency controls. Western Power's SWIS requirements belong to the WA/WEM framework. Power and Water's NT requirements belong to the separate NT framework. NEM or NER conclusions must not be carried into WA or NT without a jurisdiction-specific source.

## Principal Product Implication for EMS and SCADA

> **DNP3 appears to be the most common protocol across the NEM DNSPs reviewed, while SAPN's Modbus architecture is comparatively unusual.** A Modbus-only EMS may align with the documented SAPN design but will generally require a DNP3 adaptation layer for broader NEM deployment. IEC 61850 may also be required in some connection designs. The WA material reviewed points toward API or cloud-based DER controls, including CSIP-AUS-style approaches, but applicability to large storage remains unverified. These are implementation patterns, not universal protocol mandates; the executed connection agreement and current DNSP specification control.

## Comparison Table

| DNSP | Jurisdiction | EG connection standard or SAPN analogue | SCADA protocol | RTU ownership or control arrangement | Principal difference from SAPN |
|------|--------------|------------------------------------------|----------------|--------------------------------------|--------------------------------|
| **SA Power Networks (baseline)** | SA; NEM | **TS133** (technical), **TS134** (communications/SCADA), and TS129 (protection) | **Modbus** RTU/TCP | Customer PLC operates as slave; **SAPN installs its own RTV** as master; GDL/NEL/NIL, permission signal, and 60-second fail-to-trip response | Baseline |
| Ausgrid | NSW; NEM | **NS194 Embedded Generation** and NS194B (rotating machines) | **DNP3** is indicated for distribution SCADA, but the reviewed standard does not state a universal single-protocol mandate | SCADA signals and export limits are negotiated for each registered or large connection | Protection consolidated in NS194; SCADA is project-specific; no confirmed SAPN-style Modbus-slave design |
| Endeavour Energy | NSW; NEM | **PDI 5000** (protection and control) and SDI 538 (SCADA equipment) | Reviewed material requires a customer-supplied ABB RTU; **IEC 61850** may also be required | Customer supplies the ABB RTU; signal schedule is negotiated | Customer-owned, brand-restricted RTU rather than SAPN-owned RTU; stronger IEC 61850 orientation |
| Essential Energy | NSW; NEM | **STNW1165** (EG), CEOS7902 (SCADA design), and CEOP8026 (supply) | **DNP3 or IEC 61850** | SCADA trigger identified as **>1.5 MVA, at least 22 kV, or requiring ANM**; frequency window 48-52 Hz | Threshold stated up front; DNP3/IEC 61850; requirements split across three documents |
| **Evoenergy** | ACT; NEM through the NSW region | PO0842, PO0843, PO0845 and PO07391 | **DNP3 required** in the reviewed material, including class polling and DNP3 time synchronisation; **Evoenergy RTU polls the customer PLC every two seconds** | Control room issues a Generator CB Close Enable permission; plant must support controlled automatic shutdown | Architecturally close to SAPN, but uses DNP3 rather than Modbus |
| **Energex** | QLD; NEM | Energy Queensland **STNW** suite: STNW1174 (LV), **STNW1175 (HV)** and STNW3522 (large customers) | **DNP3 Level 3**; customer control system must accept DNP3 setpoints and runback | **DNSP owns and programs the RTU**; single substation SCADA interface; reviewed material requires Edge Defence firewalling and deep packet inspection | DNP3 Level 3; DNSP-managed RTU; dynamic operating envelope (DOE) rather than GDL/NEL; explicit cyber controls |
| **Ergon Energy** | QLD; NEM for the interconnected area, with separate isolated-network considerations | Shared Energy Queensland STNW suite plus STNW3514/3515 for isolated networks | **DNP3 Level 3** | DNSP manages the RTU; reviewed material identifies a five-minute watchdog and 30-minute stale-data response, compared with SAPN's 60-second fail-to-trip response | Broadly aligned with Energex; longer communications-failure intervals in the reviewed material |
| Powercor / **CitiPower** | VIC; NEM wholesale, Victorian state overlays | **CPPAL-ST-2008.x** network access standards and Customer Guidelines | **DNP3 over Ethernet** for indications and controls | Customer provides SCADA data and protection-failure alarms through a secondary interface to the CPPAL SCADA master | DNP3; **VEBM and DOE** terminology under Victorian instruments rather than GDL/NEL/NIL |
| United Energy | VIC; NEM wholesale, Victorian state overlays | **UE-ST-2008.x**, structured similarly to CPPAL standards under the same operating group | **DNP3.0 over Ethernet** | Connection agreement specifies export limits and DNP3 runback; primary and backup protection | CPPAL-style framework with VEBM/DOE controls |
| **AusNet Services** | VIC; NEM wholesale, Victorian state overlays | **SOP 33-05** (at least 5 MW), SOP 33-06 (export-limited systems up to 200 kVA), and SOP 11-16 (protection) | The reviewed material indicates an **IEC 61850 orientation**; SCADA is relayed through an **AusNet-installed automatic circuit recloser (ACR)** | ACR provides the intermediary between the plant and the control centre | Most distinct Victorian design in this comparison: IEC 61850, ACR intermediary, and SOP-numbered documents |
| Jemena | VIC; NEM wholesale, Victorian state overlays | Large EG Technical Access Standards, connection principles, and JEN-ELE-999-GL-EL-007 backstop material | **DNP3**; reviewed material indicates that systems above 200 kVA connect to Jemena's SCADA master through a **DNP3 gateway and 4G modem** | Customer control system accepts an analogue DNP3 setpoint for DOE and runback | DNP3 gateway and 4G; analogue DOE setpoint rather than discrete GDL/NEL controls |
| TasNetworks | TAS; NEM | Basic, LV and **MV EG** technical requirements organised by voltage | **DNP3.0** is stated in MV EG section 5.5.1; fibre is preferred | LV and Basic connections require generation control; export limits use the AS/NZS 4777.2 "soft" approach | DNP3.0 and fibre; voltage-tiered standards rather than SAPN's functional TS133/TS134 split |
| Western Power | **WA; SWIS/WEM, not NEM** | WA Electricity Networks Access Code, **Technical Rules** for the SWIS, and DER documents including Basic EG | No confirmed large-project PLC-to-RTU pattern in the reviewed sources; DER controls include **API/cloud approaches** and Emergency Solar Management metering arrangements | Reviewed material identifies 3 kW per inverter at shared connection points and 1.5 kW without a retail arrangement, subject to AS/NZS 4777.2 site limiting | Separate WA regime; NER Chapters 5 and 5A do not govern the SWIS connection pathway |
| Power and Water | **NT; separate from NEM, NECF and WEM** | Basic Micro (up to 30 kVA), **Negotiated 30-2,000 kVA** (December 2023), and BESS connection specifications | Where PWC SCADA is required, details are set in the negotiated specification; protocol remains unconfirmed | Negotiated export limits apply; AS/NZS 4777.2 **Region Australia A**, as in SA | Separate NT legislative and grid-code framework; confirm current NT modifications or derogations for each project |

## Cross-Jurisdiction Findings

1. **Protocols:** DNP3 is prevalent in the reviewed NSW, QLD, VIC, TAS and ACT material. IEC 61850 may be required by AusNet, Endeavour Energy or Essential Energy. SAPN uses the documented Modbus arrangement. The reviewed WA DER material uses API or cloud control patterns.
2. **RTU ownership:** The reviewed SA, QLD and ACT designs place installation or management of the RTU on the DNSP side. Endeavour Energy requires a customer-supplied ABB RTU. Victorian designs more commonly use a customer gateway or secondary interface to the DNSP SCADA master.
3. **Control terminology:** SA uses GDL/NEL/NIL. QLD and VIC use DOE and runback concepts. Victorian projects may also be subject to the Victorian Emergency Backstop Mechanism (VEBM) under state instruments.
4. **Communications failure:** The reviewed SAPN material uses a 60-second fail-to-trip response. The reviewed QLD material uses a five-minute watchdog and a 30-minute stale-data interval. Every value must be confirmed against the current project specification.
5. **Cybersecurity:** The reviewed QLD material expressly requires Edge Defence firewalling and deep packet inspection, providing a more explicit network-security layer than most sources reviewed here.

## Items Requiring Primary-Source Confirmation

- Whether Ausgrid formally mandates DNP3 in all relevant cases, and the controlling SCADA protocol document number.
- Exact communications-loss timeouts for each DNSP.
- Protocol fields and RTU ownership under Power and Water's negotiated NT specification.
- Whether CSIP-AUS applies to large WA storage rather than only residential or small DER.
- Many DNSP standards are restricted to accredited service providers or require payment. Some comparison fields were derived from search extracts or third-party pages. A live project must obtain the current official standard and executed connection terms from the relevant DNSP.

## Official Source Binding

> **Source level means official issuer, not necessarily a government domain.** DNSP connection standards are issued by regulated network businesses rather than government agencies. The comparison table identifies the issuing instrument where available. Local source copies include:
> - **Powercor/CitiPower CPPAL-ST-2008.2**: [[official-documents/market-core-documents/Powercor-CPPAL-ST-2008.2-LV-EG.pdf]]
> - **AusNet SOP 33-05**: [[official-documents/market-core-documents/AusNet-SOP-33-05-Embedded-Generation.pdf]]
> - Ausgrid NS194 and Energex STNW1175 could not be archived because the official sites returned HTTP 403 responses; their official live links are retained. Some other DNSP standards are restricted or paid sources. Any field based on search extracts remains medium confidence and requires confirmation from the issuing DNSP before project use.

## Related in This Tier
- [[Battery-5MW-Registration-Pathway|SAPN 5 MW Battery Connection Pathway baseline]]
- [[Network-Pricing-and-Metering|Network Pricing and Metering, including DNSP directory]]
- [[NEM-Overview]]
