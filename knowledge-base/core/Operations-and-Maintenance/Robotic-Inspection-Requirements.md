---
country: Australia
type: deliverable
category: O&M-robotics
audience: robotics-vendor
last_updated: 2026-08-27
status: draft-procurement-requirements
language: en-AU
tags: [australia, OandM, robotics, inspection, PV, BESS, substation, wildlife, requirements]
---

> **Nav**: [[00-Home/Dashboard|Dashboard]] > [[../_AU-Overview|Australia]] > **Operations & Maintenance** > **Robotic Inspection Requirements**

# Technical Requirements Specification for Routine Inspection Robots at Australian Power Facilities

---

## Document Purpose

This document describes the operating environments, hazards and work activities involved in routine inspection and maintenance at Australian **commercial and industrial and utility-scale solar farms, battery energy storage systems and substations**. It defines the functions, sensing capabilities and response strategies required from a robot or algorithm supplier.

> **Evidence and legal-status boundary:** this is a draft procurement specification, not a statement that every listed feature or numerical target is required by Australian law or an Australian Standard. Unless a requirement is tied to a cited instrument, numerical values in Parts 4–7 are candidate owner acceptance criteria. The owner must validate them through the site hazard study, applicable network and electrical-safety requirements, and a representative vendor trial before putting them into a contract. No detection, avoidance, availability, cost-saving or early-warning outcome is guaranteed.

---

## Part 1: Site Overview

### 1.1 Typical Australian Facility Specifications, from C&I to Utility Scale

| Item | Typical specification | Notes |
|---|---|---|
| **Solar farm capacity** | 200 kW–500 MW | Covers commercial and industrial through large utility scale; some projects exceed 1 GW, including NSW Western Renewables |
| **Site area** | 0.5–1,500 ha, or 0.005–15 km² | Approximately 2–3 ha per MW; a C&I project may occupy as little as 0.5 ha |
| **Trackers** | Single-axis trackers | Common suppliers include Nextracker, Array and PV Hardware |
| **Inverters** | Central, in blocks >1 MW, or string, in blocks <500 kW | Sungrow, SMA, Power Electronics and Huawei are common |
| **BESS capacity, stand-alone or coupled** | 5–850 MW / 4–8 hours | Examples include Hornsdale at 150 MW and Waratah Super Battery at 850 MW |
| **Substation voltage levels** | 33/66/132/220/275/330/500 kV | Depends on the connection point |
| **Typical service life** | 25–30 years / 15–20 years / 40–50 years for a substation | |

## Part 2: Environmental and Operating Conditions

### 2.1 Climate Conditions in Australia's Extreme Environments

| Parameter | Range | Extreme condition |
|---|---|---|
| **Ambient temperature** | −5°C to +48°C | Inland ground-surface temperature may reach 60–70°C in summer |
| **Humidity** | 5–95% RH | Persistently high in the tropical north; arid in central Australia |
| **Solar irradiation** | 4–8 kWh/m²/day | UV index 11–14, among the world's highest |
| **Wind speed** | Normally 0–15 m/s | Thunderstorm gusts of 25–35 m/s |
| **Rainfall** | Seasonal in the north, >2,000 mm/year; <300 mm in central Australia | Flash flooding and rainfall above 100 mm/hour |
| **Hail** | High risk, especially in NSW, QLD and SA | Large hailstones 5–10 cm in diameter |
| **Dust storms** | Common in central and western regions | Visibility <100 m and PM10 >1,000 μg/m³ |
| **Bushfire risk** | Nationwide; Total Fire Ban conditions on extreme or catastrophic days | Smoke and radiant heat from nearby fires |
| **Salt spray** | Within 5 km of the coast | Accelerated equipment corrosion |

### 2.2 Terrain and Ground Surface

| Surface type | Prevalence | Required robotic response |
|---|---|---|
| **Gravel roads** | Most main site roads | Wheeled or tracked mobility |
| **Compacted soil within arrays** | Predominant array surface | High dust resistance |
| **Sand in central and western regions** | Central and western projects | Resistance to bogging and wide tracks |
| **Grassland and scrub** | Site perimeter | Fire resistance and safe interaction with animals |
| **Saline soil** | Some inland sites | Corrosion resistance |
| **Mud after rain** | Common in the wet season | IP67+ and slip resistance |
| **Slopes of 5–15°** | Some hilly projects | Centre-of-gravity control |
| **Underground and above-ground cable trenches** | Frequent within arrays | Ability to cross a trench ≥30 cm wide |
| **Asphalt roads** | Within substations | Standard mobility |

### 2.3 Site Location and Connectivity

| Site location | Distance to nearest town | Communications |
|---|---|---|
| **Central and western inland project** | 200–500 km | Intermittent 4G/5G; Starlink recommended |
| **Project near a NSW or Victorian population centre** | 50–150 km | Good 4G coverage |
| **Remote Queensland project** | 100–300 km | Intermittent 4G |
| **Remote Tasmanian or South Australian project** | 50–200 km | Moderate 4G coverage |

> **Critical requirement:** the robot must continue operating during a **network outage or weak connection** and **must not depend on real-time cloud decisions**.

---

## Part 3: Wildlife and Biological Hazards

### 3.1 Large Mammals

| Animal | Frequency | Risk | Required robotic response |
|---|---|---|---|
| **Kangaroo** | Site-dependent, especially around dawn and dusk | A large animal may strike the robot or enter its path | Visual recognition, conservative separation and a safe stop; validate the response on the actual site |
| **Feral pig** | Serious risk in QLD and NT | Digs under fences and damages cable trenches and equipment | Detect and report; do not actively repel because of aggression risk |
| **Dingo or feral dog** | Inland projects | May attack people and small robots | Detect and report |
| **Cattle or sheep where co-grazing is used** | Some projects permit sheep | May rub against module structures | Detect, avoid startling and route around |
| **Wallaby** | Hilly projects | Similar to a kangaroo | Treat as a kangaroo |

### 3.2 Small Animals, a Critical Risk

| Animal | Risk | Robot requirement |
|---|---|---|
| **Rabbit** | Burrow networks may undermine routes or drainage and create collapse hazards | Detect and map suspicious depressions or burrows, route around them and alert the owner; use owner-approved pest management rather than an unvalidated robot-mounted deterrent |
| **Rats and other rodents** | May chew cable insulation or enter cabinets | Detect and report visible gnawing, nests and burrows; refer control measures to the owner's pest-management program |
| **Wombat** | Common in VIC, TAS and southern NSW | Excavates deep burrows | Treat as for rabbits |
| **Echidna** | Occasional | Excavates shallow pits | Avoid |
| **Common brushtail possum and other possums** | Coastal and nocturnal | Enter control rooms and chew cables | Infrared detection |
| **Fox** | Inland | Burrowing and potential attack on small robots | Visual recognition and avoidance |

### 3.3 Reptiles

| Animal | Risk | Robot requirement |
|---|---|---|
| **Eastern brown snake** | Venomous snake whose occurrence is site-dependent | Detect a possible snake, stop at a separation validated by the site risk assessment and alert; do not rely on species classification alone |
| **Inland taipan** | Highly venomous snake with a limited inland range | Same as above |
| **Red-bellied black snake** | Coastal regions and river valleys | Same as above |
| **Death adder** | Nationwide and highly camouflaged | Thermal imaging and AI recognition to address visual misses |
| **Goanna** | 1–2 m long | Detect and avoid |
| **Australian water dragon** | Coastal regions | Generally harmless; route around |

### 3.4 Arthropods, Commonly Underestimated

| Animal | Risk | Robot requirement |
|---|---|---|
| **Redback spider** | Venomous; hides under cabinet handles and hinges | AI visual scan before operating a cabinet door |
| **Funnel-web spider** | Potentially fatal; NSW and QLD | Visual recognition and warning |
| **Huntsman spider** | Large but of low venom risk; commonly enters inverter cabinets | Visual recognition |
| **Bull ant / red imported fire ant** | Aggressive and forms dense nests | Detect nests through raised ground features |
| **European honeybee swarm** | Builds hives on PV structures and inside inverter cabinets | Detect hives and do not disturb them |
| **Scorpion** | Generally low risk | No special treatment normally required |
| **Termite** | Damages timber posts and cable sheaths | Detect mounds and gnawing or damage marks |

### 3.5 Birds

| Bird | Risk | Robot requirement |
|---|---|---|
| **Sulphur-crested cockatoo** | May damage exposed materials at some sites | Detect and report; any exclusion or deterrence measure must be selected and approved under the site's wildlife-management plan |
| **Emu** | Collides with fences and may trip over equipment | Treat as a large animal |
| **Crow / Australian magpie** | May attack moving objects in spring | Overhead protection against bird strikes |
| **Raptor, including eagles and falcons** | May attack small drones or robots | Top protection |
| **Bird-dropping accumulation** | Shades modules and contaminates insulators | Detect high-density deposits |

### 3.6 Vegetation and Weeds, a Substantially Underestimated O&M Burden

> **User priority:** weed growth is severe at many Australian power facilities. It is a major routine O&M workload and a principal use case for a robotic vegetation-management capability.

#### Characteristics of Weeds at Australian Power Facilities

| Factor | Site reality | Challenge for the robot |
|---|---|---|
| **Species diversity** | Species and protected-vegetation constraints vary by site and season | Build the recognition list from a site ecological and weed survey; do not assume a universal number of species |
| **Stem and growth-form variation** | Soft grasses, vines and woody plants require different controls | Measure the site's vegetation before selecting cutting torque, tool type or stem-capacity criteria |
| **Height** | Tall vegetation may shade lower module rows or block inspection routes | Set cutting range and intervention thresholds from actual module clearances and route geometry |
| **Growth rate** | Growth varies materially with rainfall, climate, soil and prior treatment | Set patrol and cutting frequency from measured seasonal growth rather than a generic weekly rate |
| **Seasonal outbreak** | Growth is concentrated in the northern wet season from November to April and becomes dormant in the dry season | Workload varies substantially by season |
| **Invasive-weed control** | State laws require control of declared invasive weeds such as blackberry, lantana and mile-a-minute; failure to control can be unlawful | Identify declared weeds and create reportable records |

#### Operational Harm Caused by Weeds

| Harm | Mechanism | Consequence |
|---|---|---|
| **Generation shading** | Tall grass may shade the lower edge of the lowest module row | Quantify any generation loss from site monitoring; no universal percentage is assumed |
| **Fire hazard** | Dry weeds provide fuel during the Australian bushfire season | Site fire, ignition of surrounding land, and insurance and compliance consequences |
| **Blocked inspection routes** | Vegetation closes routes within the array | Robots and personnel cannot pass |
| **Snake and insect habitat** | Tall grass shelters brown snakes and redback spiders | Increases the biological hazards in Sections 3.3 and 3.4 |
| **Accelerated corrosion** | Vegetation retains moisture around structure foundations | Accelerated corrosion at the base of galvanised structures |
| **Tracker interference** | Vines wrap around a tracker drive shaft | Tracker seizure and motor overload |
| **Blocked drainage** | Weed roots damage drainage channels | Wet-season ponding and softened foundations |

#### Current Manual Vegetation-Control Methods and the Problems a Robot Should Address

| Method | Current use | Limitation |
|---|---|---|
| **Manual brush cutter** | Workers clear each row while carrying a brush cutter | High physical load, heat-stress and snakebite risk, and low productivity |
| **Large mower or tractor** | Used on main access lanes | Cannot enter narrow spaces below modules and may strike module structures |
| **Herbicide application** | Used at some sites | Increasing environmental restrictions, potential corrosion of module earthing components and invasive-species compliance requirements |
| **Grazing by sheep** | Used at a minority of projects | Limited control and additional animal-management burden; see Section 3.1 |

> **Business-case boundary:** evaluate robotic vegetation management against the site's measured contractor cost, treatment frequency, access constraints, safety exposure and trial performance. No general Australian cost per MW or guaranteed saving is asserted here.

---

## Part 4: Routine Inspection Scenarios and Work Activities

### 4.1 Routine Solar-Farm Inspection

#### A. Module-Level Inspection

| Inspection item | Frequency | Current manual method | Required robot capability |
|---|---|---|---|
| **Hot spots** | Quarterly plus event-triggered | Handheld IR camera | **Onboard telephoto infrared thermal imager, resolution ≥640×512, NETD ≤30 mK, capable of identifying a temperature difference ≥10 K at 5–50 m** |
| **Microcracks** | Annual | EL testing requires de-energisation | **Daytime V-I curve scanning or PL imaging**; automatically record each string voltage along the travelled route |
| **Potential-induced degradation (PID)** | Sample testing | Specialist test | Detect abnormal distribution of module-output degradation |
| **Snail trails** | Annual plus event-triggered | Visual inspection | AI visual recognition |
| **Broken glass** | Event-triggered | Visual inspection | AI visual recognition, especially after a storm |
| **Junction-box heating** | Quarterly | Sampled IR inspection | **Targeted infrared scanning at the junction-box location along the lower rear edge of the module** |
| **Abnormal tracker angle** | Daily | SCADA plus visual inspection | Visual angle measurement and reporting where deviation ≥3° |
| **Structure corrosion or loosening** | Half-yearly | Sampled visual inspection | AI vision plus vibration analysis |
| **Obstruction by vegetation or bird droppings** | Monthly | Visual inspection | AI estimation of coverage |
| **Module contamination by dust** | Event-triggered | Visual and IR inspection | Visual and edge detection |
| **Ponding or ground collapse** | After rain | Visual inspection | **3D terrain scan and abnormal-depression detection** as an early sign of rabbit burrows |

#### B. Electrical Equipment Inspection

| Inspection item | Frequency | Required robot capability |
|---|---|---|
| **String combiner box** | Monthly | **Closed-cabinet temperature assessment**, Section 4.4, plus vision |
| **Inverter-container exterior** | Weekly | Whole-surface IR scan, vision and **acoustic anomaly detection** |
| **Inverter internal airflow** | Monthly | Visual filter-blockage and HVAC checks |
| **MV transformer** | Weekly | **Oil temperature, visually read oil level and abnormal acoustic signature** |
| **Cable-trench inspection** | Monthly | **Crossing capability**, cable-temperature measurement and collapse detection |
| **Earthing terminal** | Quarterly | Visual corrosion assessment and contact-resistance measurement using a contact probe |
| **Surge arrester** | Half-yearly | Visual damage assessment |

#### C. Fence and Security Inspection

| Inspection item | Frequency | Required robot capability |
|---|---|---|
| **Fence integrity** | Weekly, or daily in high-risk areas | Complete visual patrol and **opening detection for animals or intrusion** |
| **Gate locks and hinges** | Monthly | Visual and contact-based abnormal-sound assessment |
| **Intrusion detection** | 24/7 | **Night-time thermal imaging**, vision and human-form anomaly detection |
| **Evidence of copper or aluminium theft** | Weekly | Visual anomaly detection, especially at exposed cable sections |

### 4.2 Routine BESS Inspection

#### A. Battery-Container Exterior

| Inspection item | Frequency | Required robot capability |
|---|---|---|
| **Container-surface temperature** | Daily | **IR scan of the entire container**, especially the face exposed to direct sunlight; alert immediately at an abnormal difference ≥10 K |
| **HVAC outlet temperature and air speed** | Weekly | **Contact or non-contact flow meter** |
| **Abnormal HVAC noise** | Daily | **Acoustic spectral analysis** for characteristic bearing-fault and loose-belt frequencies |
| **Fire-barrier seals** | Monthly | Visual exterior inspection |
| **Container-foundation settlement** | Monthly | **3D ranging** against the established baseline |

#### B. Early Detection of Battery Thermal Runaway, the Most Critical Scenario

| Inspection item | Frequency | Required robot capability |
|---|---|---|
| **Gas outside the container** | 24/7 | **Multi-gas sensor combination:** H₂, CO, CO₂ and VOCs |
| **Abnormal sound outside the container** | 24/7 | **Acoustic anomaly detection** for battery vent hissing and casing expansion or rupture |
| **Localised abnormal surface heating** | 24/7 | IR scanning with **pattern recognition** that distinguishes a local hot spot from uniform warming |
| **Smoke at door seams** | Event-triggered | Visual smoke recognition |

> **Critical design principle:** on suspicion of thermal runaway, the robot must stop approaching, withdraw along its approved route, issue an alarm and follow the site's emergency response plan. The safe distance and isolation boundary must be set by the site's fire and emergency risk assessment; this document does not prescribe a universal 30 m distance.

#### C. Control Room

| Inspection item | Frequency | Required robot capability |
|---|---|---|
| **MV/LV switchgear, including BMS cabinets** | Monthly | **Closed-cabinet hot-spot assessment**, Section 4.4 |
| **Inside a PCS container** | Monthly | Vision, IR and acoustics |
| **Fire-system pressure gauge** | Monthly | Visual OCR |
| **DC battery bank for backup UPS** | Quarterly | Visual appearance and IR |

### 4.3 Routine Substation Inspection

#### A. Primary Plant

| Inspection item | Frequency | Required robot capability |
|---|---|---|
| **Main-transformer exterior** | Weekly | Visual oil-leak, oil-level and surface-condition assessment; IR hot spots |
| **Transformer bushing** | Monthly | Visual crack and discharge-mark assessment; **solar-blind ultraviolet corona detection** |
| **Transformer fan and cooler** | Weekly | Vision and acoustics |
| **GIS/AIS switchgear exterior** | Weekly | **IR joint-temperature assessment** and **SF6 leak detection** using laser methane and SF6 modules |
| **Disconnector joint** | Monthly | Long-range IR scan |
| **Surge-arrester leakage-current indicator** | Monthly | Visual OCR |
| **Overhead-line insulator** | Quarterly | **Solar-blind UV corona detection**, particularly in fog or dew, plus visual contamination assessment |
| **Earthing down-conductor** | Half-yearly | Visual corrosion assessment and contact-resistance measurement |
| **CT/PT secondary circuits** | Quarterly | Visual condition inside a cabinet, combined with Section 4.4 |
| **Support structures and gantries** | Quarterly | Visual corrosion and tilt assessment |

#### B. Secondary Systems in the Control Room

| Inspection item | Frequency | Required robot capability |
|---|---|---|
| **Protection panel and relays** | Monthly | Visual indicator status and display OCR |
| **SCADA RTU** | Monthly | Visual status-light assessment |
| **DC system and battery bank** | Monthly | IR, vision and gas sensing |
| **Charger cabinet** | Monthly | Vision and display reading |
| **Communications cabinet and fibre distribution frame** | Half-yearly | Vision |
| **Control-room environment, including temperature, humidity and leaks** | Weekly | Temperature and humidity sensing plus vision |

### 4.4 Common Requirement: Closed-Cabinet Temperature Assessment

> **Critical user scenario:** low-voltage and high-voltage cabinets remain locked, but internal points may overheat. The condition must be assessed without opening the cabinet.

#### Physical Constraints

- A metal cabinet with a steel wall ≥1 mm thick blocks almost all infrared radiation.
- Rubber door seals block airflow.
- Only some cabinets have an **infrared inspection window** made from a suitable glass or polymer.

#### Feasible Detection Methods in Order of Practicality

| Method | Principle | Practicality | Notes |
|---|---|---|---|
| **1. IR-window scan** | Some cabinets already have an IR window | Highest | **The project should plan IR windows in advance**; the robot scans internal joints through the window |
| **2. Cabinet-surface temperature plus thermal model** | Infer an internal source from changes in external surface temperature | Low and indirect | Ineffective for a large cabinet or high thermal resistance |
| **3. Exhaust-air temperature** | Measure temperature at a top or side vent | Moderate | Only for ventilated cabinets and requires close approach |
| **4. Acoustic signature of overheating** | A hot joint may emit a faint high-frequency hiss | Low accuracy | Requires an ultrasonic microphone and AI classification |
| **5. Partial-discharge detection** | UHF 0.3–3 GHz or transient earth voltage sensing | High for HV switchgear | Detects discharge rather than heat; TEV requires a contact probe |
| **6. Vibration sensing** | Detect micro-vibration from thermal expansion at a hot joint | Very low | Generally not recommended |
| **7. AI vision and colour change** | Detect paint discolouration or seal deformation from heat | Slow response | Signal develops only after long-term accumulation |

#### Required Multisensor Closed-Cabinet Workflow

```text
Standard sequence when the robot approaches a cabinet:

1. Visually identify the cabinet model and whether an IR window is present.
   |
   +-- IR window present --> align with the window and scan internal joints by IR.
   |
   +-- No IR window
       |
       +-- 1. Six-point IR scan of the enclosure: top, upper side, lower side and base,
       |      integrating each point for at least 5 seconds.
       |      Compare with baseline temperature for the same cabinet type under
       |      a comparable load condition.
       |
       +-- 2. Close-range IR at the top vent plus contact air-temperature sensing.
       |
       +-- 3. Use a 30–100 kHz ultrasonic microphone to detect high-frequency
       |      partial-discharge or arcing noise, using technology comparable to
       |      the UE Systems Ultraprobe class.
       |
       +-- 4. Apply a TEV probe to the external surface of an HV cabinet to detect PD.
       |
       +-- 5. Report combined multisensor data and compare the time-series trend.
              Anomaly score ≥ threshold --> create work order:
              "Recommend opening cabinet for confirmatory inspection."
```

> **Project decision:** assess IR inspection windows during equipment design, taking account of the cabinet rating, arc-flash and enclosure requirements, the inspection method and a supplier quote. No general per-cabinet cost or inspection-effort saving is assumed.

---

## Part 5: Core Capability Requirements

The values in this Part are **candidate acceptance-test parameters**. They are not statutory minima, published Australian market benchmarks or representations of available product performance. Confirm or replace each value after a site survey and competitive vendor trial.

### 5.1 Sensing System

| Sensor | Purpose | Requirement | Suggested specification |
|---|---|---|---|
| **High-resolution optical camera** | General vision and AI | Mandatory | 4K with 20–50× optical zoom for distant modules |
| **Long-wave infrared thermal imager** | Hot spots and equipment temperature | **Mandatory** | ≥640×512, NETD ≤30 mK, variable focal length |
| **Short-wave infrared** | Temperature through glass in limited scenarios | Optional | — |
| **Solar-blind ultraviolet camera** | Corona and arcing | Recommended; mandatory for substation use | 240–280 nm filter |
| **3D LiDAR** | SLAM navigation, obstacles and terrain | **Mandatory** | ≥16 channels and range ≥100 m |
| **3D camera / structured light** | Close-range measurement of burrows and collapse | **Mandatory** | Range 0.5–5 m and accuracy ≤1 cm |
| **Ultrasonic microphone array** | Partial discharge, arcing and HVAC noise | **Mandatory** | 30–200 kHz with at least four microphones |
| **Gas sensors** | H₂, CO, CO₂, VOC and SF6 | **Mandatory** | Multi-gas combination with independent power |
| **RTK GPS** | Centimetre-level positioning | Mandatory | Dual-frequency GNSS with RTK correction |
| **Nine-axis IMU** | Attitude | Mandatory | Industrial grade |
| **Environmental sensors** | Temperature, humidity, wind speed and irradiation | Recommended | Integrated |
| **TEV probe** | Partial discharge in HV cabinets | Recommended for substations | Contact probe |
| **Laser methane plus SF6 sensor** | Remote gas-leak detection | Recommended for substations | TDLAS principle |
| **Collision tactile sensors and bumpers** | Contact safety | Mandatory | Full-body coverage |

### 5.2 Mobile Platform

| Item | Requirement |
|---|---|
| **Wheels versus tracks** | **Tracked or hybrid track-wheel platform** for sand and collapse edges |
| **Ground clearance** | ≥150 mm |
| **Trench-crossing capability** | Width ≥300 mm and depth ≥200 mm |
| **Gradeability** | ≥20°, preferably 30° |
| **Side-slope stability** | ≥15° |
| **Maximum speed** | ≥1.5 m/s for inspection and ≥3 m/s in an emergency |
| **Endurance** | ≥8 hours continuous operation; 12 hours recommended |
| **Charging** | Autonomous return to dock plus solar assistance while parked outdoors |
| **Payload** | ≥30 kg for equipment and battery |
| **Total mass** | ≤80 kg so personnel can tow it during recovery |
| **Ingress protection** | ≥IP65; IP67 recommended |
| **Operating temperature** | −10°C to +55°C |
| **Acoustic emission** | ≤60 dB to avoid startling animals and workers |

### 5.3 Autonomy

| Capability | Specific requirement |
|---|---|
| **SLAM and positioning** | Sensor fusion of RTK, LiDAR-SLAM and vision at centimetre-level accuracy |
| **Path planning** | Offline map plus online obstacle avoidance; at least 200 predefined inspection points |
| **Offline operation** | Fully autonomous inspection for ≥4 hours without instructions, with local decisions and storage |
| **Return to charging station** | Return autonomously when battery state falls below 20% |
| **Autonomous docking** | At least 95% successful docking indoors and outdoors |
| **Fault self-test** | Pre-start and continuous self-test; alert immediately on fault |
| **Emergency stop** | Physical E-stop, remote E-stop and self-test E-stop |

### 5.4 Wildlife Management, a User Priority

| Function | Requirement | Implementation |
|---|---|---|
| **Rodent and rabbit response** | **Mandatory** | Detect and report evidence, map exclusion zones and route around hazards; pest control remains an owner-approved activity. No efficacy claim is made for ultrasonic deterrence |
| **Collapse and rabbit-burrow detection** | **Mandatory** | 3D terrain scan and AI depression detection; **slow down at least 2 m before a burrow and stop at least 1 m away, then report** |
| **Self-recovery after collapse** | **Mandatory** | See Section 5.5 |
| **Snake detection** | **Mandatory** | AI vision plus thermal imaging for the typical coiled shape; stop at least 3 m away, wait and submit video evidence |
| **Large-mammal avoidance** | **Mandatory** | LiDAR plus AI vision; detect at ≥10 m, slow at ≥3 m and stop completely at ≥1 m |
| **Bird response** | Recommended | Detect, avoid contact and report recurring damage or nesting; use only owner-approved wildlife-management measures |
| **Spider and hive recognition** | Recommended | AI visual scan before approaching a cabinet-door handle |
| **Ant-nest recognition** | Recommended | Detect raised ground on the path and route around it |
| **Animal condition assessment after contact** | Recommended | If accidental contact occurs, record video, alert immediately and avoid a second contact |
| **Predictive bird-dropping and nest detection** | Recommended | Locate high-density bird-dropping areas for owner cleaning |

### 5.5 Autonomous Self-Recovery, a User Priority

#### Scenario: Robot Accidentally Enters a Rabbit Burrow or Collapse Pit

| Stage | Required robot action |
|---|---|
| **Before approach** | Scan the terrain in 3D; on a suspicious depression, slow down and probe the edge; route around if depth ≥30 cm |
| **Accidental entry, depth <50 cm** | **1. Check attitude.** If tilt <20°, attempt reverse exit. If unsuccessful, oscillate the tracks forwards and backwards to climb out |
| **Accidental entry, depth 50–100 cm** | **2. Activate recovery mode:** repeatedly drive the tracks forwards and backwards at high torque; use a manipulator arm to brace and climb if fitted |
| **Depth ≥100 cm or rollover** | **3. Enter self-protection:** stop high-speed motors to prevent further sinking; issue a high-priority alert; continuously upload GPS location and video; activate a locating light and buzzer |
| **Complete rollover** | **4. Self-right** using a circular or symmetric design, or remain stationary for rescue while keeping electronics operating |
| **Permanent immobilisation** | **5. Provide a remotely releasable lifting point** for personnel recovery |

#### Suggested Design Parameters

| Design target | Recommendation |
|---|---|
| Maximum track output torque | ≥3× rated-load requirement |
| Reverse climbing capability | 50° reverse slope |
| Rollover recovery | Four-sided symmetry and self-righting, comparable to Boston Dynamics Spot, or an external roll cage |
| Emergency location | LoRaWAN or satellite backup beacon |
| Emergency light | Flashing LED ≥30 lumens for ≥24 hours |
| Endurance while awaiting recovery | ≥72 hours using only GPS and communications |
| Protection | Reinforced upper structure against kangaroo kicks and falling rocks |

### 5.6 Vegetation Recognition and Cutting, a User Priority

> This section addresses the weed hazards in Section 3.6. Australian sites have diverse, hard and fast-growing weeds, making vegetation management a high-value, high-frequency task.

#### A. Whether the Product Includes Vegetation Cutting

The robotics supplier must state clearly **whether it provides integrated vegetation cutting or only identifies vegetation for manual work or a separate machine**.

| Option | Description | Suitable use |
|---|---|---|
| **Option 1: Integrated inspection and cutting robot** | One platform performs inspection and mechanical cutting | Small and medium facilities with integrated O&M |
| **Option 2: Inspection robot coordinated with a dedicated cutting robot** | The inspection robot maps weed distribution and dispatches a specialist cutting robot | Large facilities where specialised roles improve productivity |
| **Option 3: Identify and report for manual treatment only** | The robot produces a vegetation heat map and work orders | Entry-level option that remains dependent on manual cutting |

#### B. Vegetation-Recognition Requirements

| Function | Requirement | Implementation |
|---|---|---|
| **Species or vegetation-class recognition** | Site-specific | Train and validate against the species, vegetation classes and declared weeds identified by the site's ecological and weed survey |
| **Height measurement** | Mandatory | 3D ranging or LiDAR to measure weed height and identify grass shading modules |
| **Density heat map** | Mandatory | Site-wide distribution map locating priority areas |
| **Declared invasive-weed tagging** | Recommended | Identify blackberry, lantana and mile-a-minute and create reportable records |
| **Distinguish weeds from crops or native vegetation** | Recommended | Avoid removing protected native vegetation where environmental approval conditions apply |

#### C. Mechanical Cutting Requirements for Options 1 or 2

| Function | Requirement | Explanation |
|---|---|---|
| **Stem-cutting capacity** | Set after the site vegetation survey and cutting trial | State the validated plant type, moisture condition, diameter and duty cycle; refer growth outside the validated envelope for another treatment method |
| **Cutting-height range** | **Adjustable from 20 mm to 600 mm** | Supports different growth stages; a low residual height is needed near modules |
| **Cutting width** | ≥400 mm on main routes, with a narrow configuration for clearances below modules | Must enter narrow spaces below modules |
| **Tool type** | Choice of high-torque carbide blade, nylon line or chain flail head | Line for soft grass and blade for hard growth; automatic changeover is preferred |
| **Obstacle protection** | **Never contact a module, cable, structure or earthing conductor** | Use vision and LiDAR for exact boundaries; missed vegetation is preferable to equipment damage |
| **Operating speed** | ≥0.3 m/s while cutting | Balance productivity and cutting quality |
| **Cut-material handling** | Mulch in place without creating ignition piles | Avoid dry-grass accumulation during the dry season |
| **Fire-safe design** | Cutting must not produce sparks | Critical during the Australian bushfire season |
| **Slope operation** | Stable cutting on slopes ≤15° | Required for some hilly projects |
| **Dust and debris control** | Prevent fragments from contaminating modules or entering cooling inlets | Avoid secondary cleaning work |

#### D. Vegetation-Management Strategy

| Function | Requirement |
|---|---|
| **Seasonal adaptation** | Increase frequency during the wet season and reduce it during the dry season; schedule work from measured growth rate |
| **Zone priority** | First clear vegetation shading modules, blocking routes, increasing fire risk or providing snake habitat |
| **Combined cutting and inspection** | Perform vision and IR inspection during cutting so one pass completes multiple tasks |
| **Invasive-species compliance records** | Automatically create removal records for declared weeds for owner reporting |
| **Wildlife avoidance** | Scan before cutting; pause and report if a snake or small-animal nest is found, linked to Sections 3.3 and 3.6 |

> ⚠️ **Safety boundary:** when the cutting tool approaches a module, cable trench or earthing conductor, it **must maintain adequate clearance and reduce speed**. In an uncertain area, leave the vegetation and refer it for manual work. **Damage to electrical equipment is not permitted.**

### 5.7 Self-Protection

| Threat | Response |
|---|---|
| **Dust storm** | Detect particulate concentration, find shelter such as a container shadow or area beside a lightning mast, and shut down safely |
| **Strong wind ≥20 m/s** | Stop automatically, lower the centre of gravity and seek shelter |
| **Heavy rain or thunderstorm** | Detect a rapid pressure fall, leave exposed areas, protect sensors and shut down temporarily |
| **Approaching bushfire** | Detect smoke or rapid temperature rise, issue a highest-priority alert and withdraw toward an exit |
| **Hail** | Use visual and radar warning, then shelter in a container shadow |
| **Theft or vandalism** | Tamper sensor, GPS tracking and real-time alert |

### 5.8 Communications and Data

| Item | Requirement |
|---|---|
| **Primary communications** | Automatic switching between 4G/5G and Starlink |
| **On-site communications** | Private LTE or Wi-Fi 6, avoiding ISM interference |
| **Local storage** | ≥1 TB SSD for video and images |
| **Upload priority** | Alerts first, then video, then weekly reports |
| **Edge computing** | Perform principal AI inference locally to avoid latency and bandwidth dependence |
| **Protocols** | MQTT and OPC UA as general protocols; REST API for owner integration |
| **Cybersecurity** | TLS 1.3 or later, zero-trust architecture and regular firmware updates; no remote door opening or cabinet control because inspection is **read-only** |

---

## Part 6: Collaboration with Personnel

### 6.1 Division of Work

| Task | Robot | Person |
|---|---|---|
| Routine IR thermal scan | Primary | Confirm anomaly |
| General visual inspection | Primary | Monthly sample inspection |
| Fence patrol | Primary | Quarterly full-site inspection |
| Wildlife monitoring | Primary | Response, including carcass removal |
| Open-cabinet maintenance | Not permitted | Personnel only |
| Wiring or tightening | Not permitted | Personnel only |
| Recover trapped equipment | Not permitted | Personnel only |
| Emergency response | Trigger alert | Respond |

### 6.2 Safe Interaction

| Situation | Requirement |
|---|---|
| **Person detected within 3 m** | Reduce speed; stop within 1.5 m; emergency stop within 0.5 m |
| **Worker detected without complete PPE** | Report an alert as AI assistance only; do not physically prevent the worker |
| **Entry to a permitted work area** | Visually read the LOTO tag and identify its status |
| **Avoid blocking access** | Know every emergency route and never stop on one |
| **Emergency-vehicle recognition** | On detecting a rotating warning light, immediately yield and move at least 5 m away |

### 6.3 WHS Compliance

| Instrument | Effect |
|---|---|
| **Applicable state or territory WHS/OHS law** | The relevant PCBU or employer duties continue to apply; identify the operating jurisdiction rather than assuming one national Act applies directly |
| **AS 4024 Safety of machinery series** | Select applicable parts through the machinery risk assessment |
| **AS/NZS 60204.1, electrical equipment of machines** | Apply where the equipment falls within the standard's scope, as determined by the conformity and risk assessment |
| **AEMO, SAPN or owner-specific requirements** | A particular owner may require permits or a toolbox talk |

---

## Part 7: Operational Scenarios for Australian Facilities

The following are hypothetical acceptance-test scenarios. Distances, sensor readings and outcomes are examples for test design, not observed incidents, guaranteed performance or emergency-response instructions. The approved site procedure controls in an actual event.

### Scenario 1: Kangaroos Crossing at Dawn

```text
05:30, central-western 100 MW solar farm.
The robot leaves its dock to begin the daily inspection.
At the northern end of row 47, LiDAR detects moving objects 12 m away.
AI vision identifies eight kangaroos, including adult red kangaroos and joeys,
crossing the inspection route.

Robot decision:
  1. Immediately reduce speed to 0.3 m/s.
  2. Enter quiet mode and switch off non-essential fans.
  3. Do not use lights, to avoid startling the animals.
  4. Wait at the end of row 47.
  5. Rescan every 30 seconds and continue after the animals leave.

Expected delay: 5–15 minutes, with no human intervention.
Complete the day's inspection normally.
```

### Scenario 2: Rabbit-Warren Collapse

```text
10:15, inland 200 MW solar farm.
While travelling along row 23, the 3D scan identifies a depression approximately
35 cm in diameter, 1.5 m ahead.

Decision:
  1. Reduce speed to 0.1 m/s.
  2. Probe the edge with a laser. The depression is 80 cm deep, well beyond
     the route-around threshold.
  3. Scan the perimeter and identify three rabbit-burrow entrances connected
     as a warren.
  4. Upload alert: "Suspected rabbit-warren system at GPS 31.234°S, 142.567°E.
     Systemic ground-collapse risk. Recommend pest-control attendance."
  5. Replan the route through the opposite end of row 23.

Continue the inspection.

Variant: robot enters a depression after a misclassification.
  1. IMU detects pitch +18° and track slip of 35%.
  2. Start recovery mode using high-torque reverse drive.
  3. If unsuccessful after 5 seconds, begin oscillation mode.
  4. If still immobilised after 30 seconds, send a high-priority alert with
     GPS location and video.
  5. Enter low-power rescue mode while maintaining communications.
  6. The owner receives the alert and sends personnel within two hours.
  7. After manual recovery, the robot completes a self-test and restarts.
```

### Scenario 3: Early Sign of Thermal Runaway in a BESS Container

```text
14:23, 50 MW BESS in Victoria.
The robot approaches BESS Container 7 during its weekly inspection.
The gas sensor shows CO rising suddenly from ≤1 ppm to 22 ppm, more than 20 times
the baseline increase.
At the same time, the acoustic microphone detects a low-frequency hiss inside
the container that does not match the baseline.
IR shows a local +12°C anomaly on the eastern surface.

Decision:
  1. Stop approaching immediately.
  2. Withdraw to the exclusion distance specified in the approved site emergency response plan.
  3. Issue the highest-priority alert: "Suspected thermal runaway in Container 7.
     CO = 22 ppm, IR temperature difference = +12 K, abnormal acoustic signature."
  4. Continue monitoring remotely and stream video to the control centre.
  5. Trigger the owner's fire response plan.
  6. Support remote isolation by SAPN or the network management centre.

The test passes only if the robot alarms and withdraws as required. This scenario does not claim that external sensing will identify a cell-level fault or provide a minimum advance-warning period.
```

### Scenario 4: Fence Damage and Intrusion after a Storm

```text
06:00, morning after a thunderstorm at a 350 MW solar farm in Queensland.
The robot starts the expanded post-storm inspection mode.
Along the eastern fence it identifies a 30 m section of collapsed wire mesh and
two shoe prints nearby.
It also identifies suspicious tool marks consistent with cable-theft equipment.

Decision:
  1. Do not enter the suspicious area, preserving evidence.
  2. Capture and upload high-resolution images.
  3. Follow the suspected footprints in reverse to the fence opening.
  4. Capture a panoramic image from at least 10 m outside the opening.
  5. Notify security and police.
  6. Continue inspecting the remaining fence.

The owner attends that afternoon, repairs the fence and files a police report.
```

### Scenario 5: Closed-Cabinet Assessment at a 110 kV GIS Joint

```text
09:30, 132 kV substation in NSW.
The robot approaches Bay 4 in the 110 kV GIS.
The cabinet door is closed and has no IR inspection window.

Closed-cabinet hot-spot assessment:
  1. Identify the cabinet type and number visually.
  2. Perform a six-point surface IR scan:
     - top +3.2°C / side +1.1°C / base +0.4°C;
     - the gradient is abnormal, although every absolute temperature remains
       in the normal range.
  3. Scan with a 30–100 kHz ultrasonic microphone array:
     - detect an 87 kHz discrete signal at 42 dB SPL, compared with a 28 dB baseline;
     - match the signature to partial discharge.
  4. Apply a TEV probe to the cabinet surface and record at least 200 PD events
     per minute.
  5. Combined determination: early evidence of internal partial discharge.
  6. Create work order: "Suspected partial discharge in Bay 4. Recommend outage
     inspection and PD localisation testing within seven days."

The owner schedules specialist PD localisation.
Final inspection identifies a loose joint and small air-gap discharge on one side
of a 220 kV disconnector. PD ceases after tightening, preventing a potential failure.
```

### Scenario 6: Combined Rabbit and Snake Hazard

```text
07:30, 80 MW solar farm in northern NT.
The robot is inspecting row 12.
AI vision identifies a possible snake-shaped obstruction. Species identification is
not treated as reliable enough to reduce the conservative response.

Response:
  1. Stop immediately.
  2. Reverse to at least 3 m away.
  3. Capture high-resolution and thermal images of the snake.
  4. Issue a wildlife alert and reject the route.
  5. Replan through the opposite side of row 12.

Additional observation: three new rabbit holes are identified 4 m away.
  6. Record the rabbit-warren location.
  7. Submit combined report: "Snake and rabbit-warren concentration area.
     Recommend pest control and wildlife-management attendance."

The inspection takes an additional 25 minutes but avoids human snakebite exposure.
```

---

## Part 8: Additional Material Required from a Robotics Supplier

Before proposing a product to an Australian asset owner, provide the following.

### 8.1 Performance Validation Report

| Item | Evidence required |
|---|---|
| **Representative trial** | Duration, site conditions, operating hours, route coverage, interventions and exclusions; the owner sets the minimum duration after assessing risk |
| **Availability** | Measured uptime with the numerator, denominator, excluded downtime and confidence interval stated |
| **Detection performance** | Per-hazard probability of detection, miss rate and false-alarm rate against a labelled test set representative of the site |
| **Wildlife interaction** | Logs of detections, stops, near misses and contacts; demonstrate conservative stopping without claiming that zero future collisions can be guaranteed |
| **Recovery performance** | Number and severity of recovery trials, autonomous successes, human interventions and failure modes; no universal percentage is assumed |

### 8.2 Integration

| Owner system | Integration method |
|---|---|
| **SCADA**, such as GE Predix or Schneider EcoStruxure | OPC UA standard |
| **CMMS**, such as Maximo, SAP PM or Pronto | Automatic work-order creation through REST API |
| **AEMO reporting system** | Monitoring data only; not real time |
| **Owner cloud platform** | Private cloud or customer-selected cloud |

### 8.3 Compliance

| Item | Requirement |
|---|---|
| **ACMA regulatory compliance mark (RCM)** | Where the product is within an applicable ACMA labelling notice, the Australian responsible supplier must follow the ACMA compliance process: determine the applicable rules, demonstrate compliance, keep records, register where required and apply the RCM. The obsolete C-Tick is not an alternative current mark |
| **Electrical-equipment safety** | Identify the equipment-specific standard required by the applicable electrical-safety regime and EESS classification. Do not apply AS/NZS 60950 or AS/NZS 60601 as blanket robot standards. AS/NZS 62368.1 may be relevant only where the product falls within its audio/video or ICT equipment scope |
| **Hazardous areas** | Explosion-protection certification is required only if the site hazardous-area classification and the robot's intended operating zone require it; determine the equipment protection level from that assessment rather than assuming Ex ic or Zone 2 |
| **TGA status** | Ordinary power-facility inspection equipment is not regulated by the TGA merely because it is a robot. Assess TGA requirements only if the product has a therapeutic intended purpose and meets the statutory medical-device definition |
| **WHS/OHS assessment** | Provide a machinery and task risk assessment under the law of the operating jurisdiction. Provide a safe work method statement where the work is legally classified as high-risk construction work, not as a universal paperwork requirement |

---

## Part 9: Suggested Roadmap

### Phase 1, Months 0–6: Basic Inspection

- Fence patrol, visual anomalies and basic IR scanning.
- Wildlife collision avoidance as a priority.
- Partial self-recovery after ground collapse.

### Phase 2, Months 6–12: Advanced Sensing

- Closed-cabinet hot-spot assessment, including ultrasound and TEV.
- Early BESS gas warning.
- AI recognition of snakes and spiders.

### Phase 3, Months 12–24: Autonomous Improvement

- Autonomous expanded inspection after a storm.
- Predictive maintenance based on trends.
- Multi-robot coordination for large facilities.
- Vegetation heat mapping and declared invasive-species records.

### Phase 4, Month 24 Onward: Enhanced Capability

- Mechanical vegetation cutting through an integrated or coordinated robot.
- Simple maintenance such as dust blowing and trimming.
- Coordination with drones, combining aerial and ground coverage.
- Integration with SAPN and AEMO for rapid emergency response.

---

## Part 10: User Decision Matrix

Questions for a robotics supplier:

| Question | Expected response |
|---|---|
| 1. What representative environmental and endurance testing has the product completed? | Raw test data, conditions, duration, exclusions and failures mapped to this site's operating envelope |
| 2. **How does the system minimise wildlife collision risk and enter a safe state after uncertain detection?** | Testable sensing, stopping and escalation design, without a guarantee of zero future collisions |
| 3. **What is the demonstrated self-recovery performance across defined collapse and immobilisation tests?** | Trial counts, success rate, failure modes and video evidence |
| 4. **How does the multisensor closed-cabinet hot-spot algorithm work?** | Detailed explanation |
| 5. **What external BESS warning conditions can the system detect, and with what validated limitations?** | Hazard-specific test evidence; no fixed early-warning period is assumed |
| 6. **Can it operate autonomously for four hours without a network connection?** | Yes, with demonstration |
| 7. **How is possible-snake detection validated without relying on species classification?** | Site-representative test set, miss and false-alarm rates, and a conservative stop response |
| 8. **How does it respond to dust storms, heavy rain and bushfires?** | Three specific response plans |
| 9. **How does it integrate with owner systems such as SAPN or AEMO?** | Standard API |
| 10. **What Australian support coverage and response commitments are offered?** | Named service locations, hours, escalation path, spares and contractually committed response times based on the owner's criticality assessment |
| 11. **Does it provide mechanical vegetation cutting through an integrated or coordinated solution?** | Clear selection of Option 1, 2 or 3 |
| 12. **What plant types, moisture conditions, stem diameters and duty cycles have been validated for cutting?** | Site-representative trial evidence and stated operating envelope |
| 13. **Which site-specific vegetation classes and declared weeds can it recognise?** | Results against a labelled data set derived from the site survey |
| 14. **How does it ensure cutting never damages a module, cable or earthing conductor?** | Specific safety-boundary algorithm |
| 15. **Can cutting produce sparks during the bushfire season?** | Spark-free design |

---

## Appendix A: Glossary

| Term | Definition |
|---|---|
| Utility-scale solar farm | Large grid-connected solar generating facility, generally tens to hundreds of megawatts |
| Battery energy storage system | Battery storage facility, commonly abbreviated BESS |
| Substation | Facility for voltage transformation, switching and control |
| Tracker | Single-axis or dual-axis structure that moves PV modules to follow the sun |
| Module | Solar photovoltaic panel |
| String combiner box | Junction box that combines current from multiple PV strings |
| Central inverter | High-capacity central unit that converts DC to AC |
| String inverter | Distributed lower-capacity inverter |
| Medium-voltage transformer | Transformer at medium-voltage level, commonly containerised or kiosk-mounted |
| High-voltage transformer | Main transformer at a high-voltage level |
| Switchgear | High- or medium-voltage switching equipment, either gas-insulated or air-insulated |
| Primary plant | Main equipment that directly carries electrical energy, including transformers and circuit breakers |
| Secondary system | Protection and control equipment, including relays and control panels |
| Closed-cabinet assessment | Assessment of internal cabinet condition without opening the door |
| Partial discharge | Small electrical discharge within insulation and an early indicator of failure |
| Corona | Ionisation discharge in air around a high-voltage conductor |
| Thermal runaway | Uncontrolled cascading increase in battery temperature that may cause fire |
| Infrared inspection window | Window installed in a cabinet that transmits infrared radiation |
| Rabbit-warren system | Underground network excavated by rabbits that can cause ground collapse |
| Brown snake | Venomous Australian snake; occurrence and response controls are site-specific |
| Taipan | Highly venomous Australian snake with a limited range; occurrence and response controls are site-specific |
| Redback spider | Common venomous Australian spider that often hides in cabinet gaps |
| Funnel-web spider | Potentially fatal venomous spider associated with the Sydney region |
| Cockatoo | Sulphur-crested cockatoo, known to chew cables |
| Wombat | Burrowing Australian marsupial that excavates deep burrows |
| Work health and safety law | Australian Work Health and Safety Act 2011 framework |
| Network management centre | Utility dispatch and monitoring centre, commonly abbreviated NMC |

---

## Appendix B: Referenced Standards and Documents

| Document | Application |
|---|---|
| **AEMO MASS v8.2** | Current Market Ancillary Services Specification, effective 3 June 2024. It is not a robotics product standard; it is relevant only where measurement or verification is within an FCAS service scope |
| **SAPN TS129 / TS132 / TS134** | South Australian network technical standards |
| **NER Chapter 5 / S5.2.5** | National connection technical standards |
| **AS/NZS 5033** | Site-interface reference where work affects a PV array; not a general mobile-robot product standard |
| **AS/NZS 5139** | Site-interface reference where work affects a battery installation; not a general mobile-robot product standard |
| **AS 4024 Safety of machinery series** | Select applicable parts through the machinery risk assessment; do not cite an unspecified `4024.1xxx` requirement |
| **AS/NZS 60204.1** | Apply only where the robot and its electrical equipment fall within the standard's scope |
| **AS/NZS 4836** | Relevant where work is performed on or near low-voltage electrical installations and equipment |
| **Applicable state or territory WHS/OHS law** | Duties and terminology vary by jurisdiction; the model WHS Act is not itself a universal operating law |
| **ACMA RCM compliance process** | https://www.acma.gov.au/5-steps-suppliers |
| **EESS equipment-specific relevant standards** | https://www.eess.gov.au/relevant-standard/ |
| **TGA medical-device decision tree** | https://www.tga.gov.au/resources/decision-trees/my-product-medical-device/md-medical-device-7 |
| **AEMO MASS current publication page** | https://aemo.com.au/energy-systems/electricity/national-electricity-market-nem/system-operations/ancillary-services/market-ancillary-services-specification-and-fcas-verification-tool |

---

## Appendix C: Version History

| Version | Date | Change |
|---|---|---|
| v1.0 | 2026-06-04 | Initial version, including emphasis on wildlife and closed-cabinet assessment |
| v1.2 | 2026-06-05 | Removed animal emoji; changed capacity range to 200 kW–500 MW; removed site-layout diagram and commercial terms |
| v1.3 | 2026-06-05 | Converted the complete document to Chinese; added Section 3.6 on vegetation and weeds and Section 5.6 on recognition and cutting; added vegetation questions to the decision matrix |
| v1.4 | 2026-08-27 | Refactored the complete document into professional English while preserving technical thresholds and internal links |
| v1.5 | 2026-08-27 | Reclassified numerical targets as draft acceptance criteria; removed unsupported cost, wildlife-deterrence and guaranteed-performance claims; corrected Australian product-compliance and MASS references |

> **Note:** this document is designed to be iterative. After a technical assessment by the robotics supplier, the owner and supplier should jointly refine the specific capability requirements in Part 5 into a contract schedule.

---

## Related

- [[../_AU-Overview]]
- [[../Large-Scale-Generation/Grid-Requirements]]
- [[../Large-Scale-Generation/Safety-Compliance]]
- [[../Market-Structure/Battery-5MW-Registration-Pathway]]
