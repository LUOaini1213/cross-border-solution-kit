# Temporary moves of semiconductor equipment and spares into and out of Singapore

**RFQ** RFQ-SEMI-2026-002 · **Customer** Customer A (fictional) · **Issued** 2026-11-15 · **Valid** 30 days · **Currency** USD

> Portfolio example: the customer is fictional; freight and handling rates are **ILLUSTRATIVE** (not any carrier's or forwarder's tariff); duty and tax rates are official only where marked verified; regulatory statements were checked against official sources on 2026-11-15 (see the regulatory check log). Not tax or legal advice.

## 1. Executive summary

A semiconductor equipment service organisation with a regional service hub in Singapore. It moves demonstration tools to exhibitions, sends field engineers' metrology kits to fabs, and runs repair loops for failed modules.

| Lane | Recommended solution | Landed cost | P90 (days) | On time (target) | Risk | Status |
|---|---|---|---|---|---|---|
| B1 | Air freight + Temporary Import Scheme | USD 20,801/move | 4.8 | 100.0% (12 days) | 57 | meets target |
| B2 | Air freight + ATA Carnet | USD 7,132/move | 5.3 | 94.9% (7 days) | 47 | below target |
| B3 | Air freight + temporary export for repair | USD 4,967/move | 31.4 | 96.9% (35 days) | 44 | meets target |
| B4 | Cross-border road + Temporary Import Scheme | USD 3,695/move | 28.1 | 96.5% (30 days) | 59 | meets target |

Recommended options: annual quotation about USD 159,673 (logistics, VAS, insurance, permits); total landed cost including duties, taxes and inventory carrying about USD 187,677 a year.

**Key findings**

- Singapore Customs accepts foreign ATA Carnets only for exhibitions, professional equipment and scientific equipment; commercial samples and repair are not covered, so repair loops use the TIS or temporary export for repair.
- Local ATA Carnets in Singapore are issued by the Singapore International Chamber of Commerce (SICC), Singapore's National Guaranteeing and Issuing Association.
- Semiconductor manufacturing equipment and specially designed parts may be strategic goods (control list 3B001); export or re-export from Singapore then needs an XO/XP permit applied for at least 5 working days ahead, carnet or not.
- TIS security is 30% of the potential GST for a GST-registered entity and covers only the Singapore side; the origin country's temporary export and re-import are separate.

## 2. Requirements

- Flow: temporary moves; Incoterm: not applicable: no sale, the owner's goods move and return; quoting to the owner of the goods.
- Service: at least 95% of shipments within each lane's target; weights cost 0.35, time 0.35, risk 0.3.

| Lane | Description | From → to | Target (days) |
|---|---|---|---|
| B1 | Exhibition demonstration tool, Osaka to a Singapore exhibition and back | Osaka (JP) → Singapore (SG) | 12 |
| B2 | Field-service metrology kit, San Jose to a Singapore fab for an installation and back | San Jose (US) → Singapore (SG) | 7 |
| B3 | Failed RF generator, Singapore fab to the OEM repair centre in Osaka and back | Singapore (SG) → Osaka (JP) | 35 |
| B4 | Customer spares, Penang to the Singapore repair hub and back | Penang (MY) → Singapore (SG) | 30 |

## 3. Options per lane

Cost is landed cost per unit (quotation + duties and taxes + inventory carrying); P50/P90 are door-to-door days from 20,000 Monte Carlo draws; the risk score adds compliance flags, transit spread and hand-offs (0-100, lower is better).

### B1 · Exhibition demonstration tool, Osaka to a Singapore exhibition and back

| Option | Landed cost per unit | P50 | P90 | On time | Risk | Result |
|---|---|---|---|---|---|---|
| Air freight + ATA Carnet | USD 25,918 | 3.6 | 4.7 | 100.0% | 47 | Pareto |
| Air freight + Temporary Import Scheme | USD 20,801 | 3.6 | 4.8 | 100.0% | 57 | ★ recommended |
| Ocean FCL (20ft) + ATA Carnet | USD 35,266 | 22.6 | 31.5 | 0.1% | 55 | dominated |
| Ocean FCL (20ft) + Temporary Import Scheme | USD 30,139 | 22.6 | 31.4 | 0.1% | 65 | dominated |

- Recommended: Air freight + Temporary Import Scheme at USD 20,801 per move landed, P90 4.8 days, 100.0% on time against the 12-day target, risk score 57/100.
- It meets the 95.0% on-time requirement and has the best weighted score of cost, P90 time and risk among the options that do.
- Sensitivity: with a 10-day target the same option would be on time 99.3% of the time.
- Alternative on the Pareto front: Air freight + ATA Carnet - 25% more per move, same P90 (4.7 days), risk 47; on time 100.0%.
- Ocean FCL (20ft) + ATA Carnet is dominated by Air freight + ATA Carnet (no better on cost, P90 or risk).
- Ocean FCL (20ft) + Temporary Import Scheme is dominated by Air freight + ATA Carnet, Air freight + Temporary Import Scheme (no better on cost, P90 or risk).
- Conditions to manage: [SG-STRATEGIC-SCREEN] Semiconductor manufacturing or test equipment and specially designed parts may be strategic goods in Singapore (control list category 3B). Each export or re-export of a listed item needs an XO/XP permit applied for at least five working days ahead, even under an ATA Carnet. (HS 9031.41) [ORIGIN-EXPORT-CONTROL] Export controls of the origin country (for example on temporary exports of tools of trade or on returns after repair) were not assessed. (HS 9031.41) [TIS-ORIGIN-SIDE] TIS covers only the Singapore side; the return into JP needs that country's own temporary-export or goods-returned procedure, which was not verified. An ATA Carnet covers both ends where both countries accept it.

### B2 · Field-service metrology kit, San Jose to a Singapore fab for an installation and back

| Option | Landed cost per unit | P50 | P90 | On time | Risk | Result |
|---|---|---|---|---|---|---|
| Air freight + ATA Carnet | USD 7,132 | 4.3 | 5.3 | 94.9% | 47 | ★ recommended |
| Air freight + Temporary Import Scheme | USD 7,183 | 4.2 | 5.3 | 94.5% | 57 | dominated |
| Ocean LCL + ATA Carnet | USD 9,458 | 43.5 | 51.9 | 0.0% | 62 | dominated |
| Ocean LCL + Temporary Import Scheme | USD 9,511 | 43.6 | 51.9 | 0.0% | 72 | dominated |

- No option reaches 95.0% on time within 7 days. Recommended for now: Air freight + ATA Carnet (94.9% on time, P90 5.3 days, USD 7,132 per move); the target or the lead time needs to be renegotiated.
- Planning 8 days instead of 7 lifts this option to 96.4% on time.
- Air freight + Temporary Import Scheme is dominated by Air freight + ATA Carnet (no better on cost, P90 or risk).
- Ocean LCL + ATA Carnet is dominated by Air freight + ATA Carnet, Air freight + Temporary Import Scheme (no better on cost, P90 or risk).
- Ocean LCL + Temporary Import Scheme is dominated by Air freight + ATA Carnet, Air freight + Temporary Import Scheme (no better on cost, P90 or risk).
- Conditions to manage: [SG-STRATEGIC-SCREEN] Semiconductor manufacturing or test equipment and specially designed parts may be strategic goods in Singapore (control list category 3B). Each export or re-export of a listed item needs an XO/XP permit applied for at least five working days ahead, even under an ATA Carnet. (HS 9031.80) [ORIGIN-EXPORT-CONTROL] Export controls of the origin country (for example on temporary exports of tools of trade or on returns after repair) were not assessed. (HS 9031.80)

### B3 · Failed RF generator, Singapore fab to the OEM repair centre in Osaka and back

| Option | Landed cost per unit | P50 | P90 | On time | Risk | Result |
|---|---|---|---|---|---|---|
| Air freight + temporary export for repair | USD 4,967 | 25.5 | 31.4 | 96.9% | 44 | ★ recommended |
| Ocean LCL + temporary export for repair | USD 6,101 | 75.4 | 91.1 | 0.0% | 62 | dominated |

- Recommended: Air freight + temporary export for repair at USD 4,967 per move landed, P90 31.4 days, 96.9% on time against the 35-day target, risk score 44/100.
- It meets the 95.0% on-time requirement and has the best weighted score of cost, P90 time and risk among the options that do.
- Sensitivity: with a 28-day target the same option would be on time 70.9% of the time.
- Ocean LCL + temporary export for repair is dominated by Air freight + temporary export for repair (no better on cost, P90 or risk).
- Not offered: ata_carnet - Repair is not an ATA purpose and goods must return in the same condition.
- Conditions to manage: [SG-STRATEGIC-SCREEN] Semiconductor manufacturing or test equipment and specially designed parts may be strategic goods in Singapore (control list category 3B). Each export or re-export of a listed item needs an XO/XP permit applied for at least five working days ahead, even under an ATA Carnet. (HS 8486.90) [DEST-REPAIR-REGIME] Temporary admission for repair at the destination (JP) was not assessed; duty or tax on arrival may apply unless a relief is used.

### B4 · Customer spares, Penang to the Singapore repair hub and back

| Option | Landed cost per unit | P50 | P90 | On time | Risk | Result |
|---|---|---|---|---|---|---|
| Cross-border road + Temporary Import Scheme | USD 3,695 | 22.9 | 28.1 | 96.5% | 59 | ★ recommended |
| Air freight + Temporary Import Scheme | USD 3,654 | 24.0 | 29.5 | 91.8% | 64 | Pareto |

- Recommended: Cross-border road + Temporary Import Scheme at USD 3,695 per move landed, P90 28.1 days, 96.5% on time against the 30-day target, risk score 59/100.
- It meets the 95.0% on-time requirement and has the best weighted score of cost, P90 time and risk among the options that do.
- Sensitivity: with a 24-day target the same option would be on time 60.5% of the time.
- Alternative on the Pareto front: Air freight + Temporary Import Scheme - 1% less per move, P90 29.5 days (+1.4), risk 64; on time 91.8% (below target).
- Not offered: ata_carnet - Singapore accepts foreign carnets only for exhibitions, professional equipment and scientific equipment; 'repair_in_sg' is not one of them.
- Conditions to manage: [SG-STRATEGIC-SCREEN] Semiconductor manufacturing or test equipment and specially designed parts may be strategic goods in Singapore (control list category 3B). Each export or re-export of a listed item needs an XO/XP permit applied for at least five working days ahead, even under an ATA Carnet. (HS 8414.10) [ORIGIN-EXPORT-CONTROL] Export controls of the origin country (for example on temporary exports of tools of trade or on returns after repair) were not assessed. (HS 8414.10) [ORIGIN-REIMPORT-REGIME] Re-import into MY after repair (duty/tax relief on return) was not assessed. [TIS-ORIGIN-SIDE] TIS covers only the Singapore side; the return into MY needs that country's own temporary-export or goods-returned procedure, which was not verified. An ATA Carnet covers both ends where both countries accept it.

## 4. Cost build-up of the recommended options (annual)

### B1 · Air freight + Temporary Import Scheme

| Cost element | Annual (USD) | Per unit (USD) | Payer | In quote |
|---|---|---|---|---|
| Air-ride pickup (outbound) | 193 | 192.80 | owner | yes |
| Origin airport handling (outbound) | 216 | 216.00 | owner | yes |
| Air freight KIX-SIN | 5,760 | 5,760.00 | owner | yes |
| Destination airport handling (outbound) | 270 | 270.00 | owner | yes |
| Air-ride delivery (outbound) | 164 | 164.00 | owner | yes |
| Export declaration (outbound) | 60 | 60.00 | owner | yes |
| Import declaration (outbound) | 55 | 55.00 | owner | yes |
| Air-ride pickup (return) | 164 | 164.00 | owner | yes |
| Origin airport handling (return) | 216 | 216.00 | owner | yes |
| Air freight SIN-KIX | 5,400 | 5,400.00 | owner | yes |
| Destination airport handling (return) | 270 | 270.00 | owner | yes |
| Air-ride delivery (return) | 193 | 192.80 | owner | yes |
| Export declaration (return) | 40 | 40.00 | owner | yes |
| Import declaration (return) | 90 | 90.00 | owner | yes |
| Export crate with shock mounting | 1,200 | 1,200.00 | owner | yes |
| Shock and tilt indicators | 40 | 40.00 | owner | yes |
| Cleanroom bagging | 150 | 150.00 | owner | yes |
| Transit insurance, both directions | 2,244 | 2,244.00 | owner | yes |
| TIS security cost (guarantee on the suspended GST) | 87 | 86.65 | owner | yes |
| TIS inward and outward permits | 180 | 180.00 | owner | yes |
| Temporary export and re-import formalities in JP (regime not verified) | 150 | 150.00 | owner | yes |
| Capital tied up in transit | 3,660 | 3,659.73 | owner | no |
| **Quotation total** | 17,141 | 17,141.25 |  |  |
| **Total landed cost** | 20,801 | 20,800.98 |  |  |

### B2 · Air freight + ATA Carnet

| Cost element | Annual (USD) | Per unit (USD) | Payer | In quote |
|---|---|---|---|---|
| Air-ride pickup (outbound) | 858 | 214.40 | owner | yes |
| Origin airport handling (outbound) | 168 | 42.00 | owner | yes |
| Air freight SFO-SIN | 6,440 | 1,610.00 | owner | yes |
| Destination airport handling (outbound) | 210 | 52.50 | owner | yes |
| Air-ride delivery (outbound) | 685 | 171.20 | owner | yes |
| Export declaration (outbound) | 300 | 75.00 | owner | yes |
| Import declaration (outbound) | 220 | 55.00 | owner | yes |
| Air-ride pickup (return) | 685 | 171.20 | owner | yes |
| Origin airport handling (return) | 168 | 42.00 | owner | yes |
| Air freight SIN-SFO | 6,720 | 1,680.00 | owner | yes |
| Destination airport handling (return) | 210 | 52.50 | owner | yes |
| Air-ride delivery (return) | 858 | 214.40 | owner | yes |
| Export declaration (return) | 160 | 40.00 | owner | yes |
| Import declaration (return) | 480 | 120.00 | owner | yes |
| Export crate with shock mounting | 4,800 | 1,200.00 | owner | yes |
| Shock and tilt indicators | 160 | 40.00 | owner | yes |
| Cleanroom bagging | 600 | 150.00 | owner | yes |
| Transit insurance, both directions | 1,267 | 316.80 | owner | yes |
| ATA Carnet issuance (one carnet a year covers the year's trips) | 450 | 112.50 | owner | yes |
| Carnet security cost (guarantee for one year) | 720 | 180.00 | owner | yes |
| Capital tied up in transit | 2,371 | 592.68 | owner | no |
| **Quotation total** | 26,158 | 6,539.50 |  |  |
| **Total landed cost** | 28,529 | 7,132.18 |  |  |

### B3 · Air freight + temporary export for repair

| Cost element | Annual (USD) | Per unit (USD) | Payer | In quote |
|---|---|---|---|---|
| Air-ride pickup (outbound) | 1,712 | 171.20 | owner | yes |
| Origin airport handling (outbound) | 144 | 14.40 | owner | yes |
| Air freight SIN-KIX | 3,600 | 360.00 | owner | yes |
| Destination airport handling (outbound) | 180 | 18.00 | owner | yes |
| Air-ride delivery (outbound) | 2,000 | 200.00 | owner | yes |
| Export declaration (outbound) | 400 | 40.00 | owner | yes |
| Import declaration (outbound) | 900 | 90.00 | owner | yes |
| Air-ride pickup (return) | 2,000 | 200.00 | owner | yes |
| Origin airport handling (return) | 144 | 14.40 | owner | yes |
| Air freight KIX-SIN | 3,840 | 384.00 | owner | yes |
| Destination airport handling (return) | 180 | 18.00 | owner | yes |
| Air-ride delivery (return) | 1,712 | 171.20 | owner | yes |
| Export declaration (return) | 600 | 60.00 | owner | yes |
| Import declaration (return) | 550 | 55.00 | owner | yes |
| Export crate with shock mounting | 12,000 | 1,200.00 | owner | yes |
| Shock and tilt indicators | 400 | 40.00 | owner | yes |
| Cleanroom bagging | 1,500 | 150.00 | owner | yes |
| Transit insurance, both directions | 1,716 | 171.60 | owner | yes |
| OUT (TCI) and In-Non-Payment (TCI) permits | 1,800 | 180.00 | owner | yes |
| Repair-centre country: temporary import handling (regime not verified) | 1,500 | 150.00 | owner | yes |
| GST on new parts at re-import (expected) | 3,510 | 351.00 | owner | no |
| Capital tied up in transit | 9,278 | 927.77 | owner | no |
| **Quotation total** | 36,878 | 3,687.80 |  |  |
| **Total landed cost** | 49,666 | 4,966.57 |  |  |

### B4 · Cross-border road + Temporary Import Scheme

| Cost element | Annual (USD) | Per unit (USD) | Payer | In quote |
|---|---|---|---|---|
| Cross-border truck, air-ride (outbound) | 15,600 | 650.00 | owner | yes |
| Export declaration (outbound) | 1,080 | 45.00 | owner | yes |
| Import declaration (outbound) | 1,320 | 55.00 | owner | yes |
| Cross-border truck, air-ride (return) | 15,600 | 650.00 | owner | yes |
| Export declaration (return) | 960 | 40.00 | owner | yes |
| Import declaration (return) | 1,680 | 70.00 | owner | yes |
| Export crate with shock mounting | 28,800 | 1,200.00 | owner | yes |
| Shock and tilt indicators | 960 | 40.00 | owner | yes |
| Cleanroom bagging | 3,600 | 150.00 | owner | yes |
| Transit insurance, both directions | 1,901 | 79.20 | owner | yes |
| TIS security cost (guarantee on the suspended GST) | 74 | 3.10 | owner | yes |
| TIS inward and outward permits | 4,320 | 180.00 | owner | yes |
| Temporary export and re-import formalities in MY (regime not verified) | 3,600 | 150.00 | owner | yes |
| Capital tied up in transit | 9,186 | 382.76 | owner | no |
| **Quotation total** | 79,495 | 3,312.30 |  |  |
| **Total landed cost** | 88,681 | 3,695.06 |  |  |

## 5. Compliance and risk

### Temporary-admission instrument per lane

| Lane | Move | ATA Carnet | TIS | Temporary export for repair | Recommended |
|---|---|---|---|---|---|
| B1 | Exhibition demonstration tool, Osaka to a Singapore exhibition and back | available | available | — | Air freight + Temporary Import Scheme |
| B2 | Field-service metrology kit, San Jose to a Singapore fab for an installation and back | available | available | — | Air freight + ATA Carnet |
| B3 | Failed RF generator, Singapore fab to the OEM repair centre in Osaka and back | not available | — | available | Air freight + temporary export for repair |
| B4 | Customer spares, Penang to the Singapore repair hub and back | not available | available | — | Cross-border road + Temporary Import Scheme |

### Risk flags and mitigations

| Lane | Severity | Finding | Mitigation | Verified |
|---|---|---|---|---|
| B1 | high | Semiconductor manufacturing or test equipment and specially designed parts may be strategic goods in Singapore (control list category 3B). Each export or re-export of a listed item needs an XO/XP permit applied for at least five working days ahead, even under an ATA Carnet. (HS 9031.41) | Classify each item against the Strategic Goods Control List (the 2026 Order applies from 1 Dec 2026); obtain the OEM's export classification and the origin country's licence; build 5 working days into the return plan. | yes |
| B1 | medium | Export controls of the origin country (for example on temporary exports of tools of trade or on returns after repair) were not assessed. (HS 9031.41) | Ask the equipment owner's trade-compliance team for the export classification and any licence exception before booking. | no |
| B1 | low | Goods must leave Singapore in the same condition within the permitted period (6 months for TIS and ATA); selling or leaving them behind triggers GST. | Track re-export dates; file extensions before expiry. | yes |
| B1 | low | TIS permits are filed through TradeNet by a Singapore declarant, and security must be lodged before import. | Appoint the declaring agent and lodge the guarantee two weeks before the move. | yes |
| B1 | medium | TIS covers only the Singapore side; the return into JP needs that country's own temporary-export or goods-returned procedure, which was not verified. An ATA Carnet covers both ends where both countries accept it. | Confirm the JP export and re-import treatment with the owner's broker before the first move. | no |
| B2 | high | Semiconductor manufacturing or test equipment and specially designed parts may be strategic goods in Singapore (control list category 3B). Each export or re-export of a listed item needs an XO/XP permit applied for at least five working days ahead, even under an ATA Carnet. (HS 9031.80) | Classify each item against the Strategic Goods Control List (the 2026 Order applies from 1 Dec 2026); obtain the OEM's export classification and the origin country's licence; build 5 working days into the return plan. | yes |
| B2 | medium | Export controls of the origin country (for example on temporary exports of tools of trade or on returns after repair) were not assessed. (HS 9031.80) | Ask the equipment owner's trade-compliance team for the export classification and any licence exception before booking. | no |
| B2 | low | Goods must leave Singapore in the same condition within the permitted period (6 months for TIS and ATA); selling or leaving them behind triggers GST. | Track re-export dates; file extensions before expiry. | yes |
| B2 | low | The carnet's general list must match the goods exactly; partial shipments and changes need care at each border. | Check serial numbers against the general list before each crossing. | yes |
| B3 | high | Semiconductor manufacturing or test equipment and specially designed parts may be strategic goods in Singapore (control list category 3B). Each export or re-export of a listed item needs an XO/XP permit applied for at least five working days ahead, even under an ATA Carnet. (HS 8486.90) | Classify each item against the Strategic Goods Control List (the 2026 Order applies from 1 Dec 2026); obtain the OEM's export classification and the origin country's licence; build 5 working days into the return plan. | yes |
| B3 | info | ATA Carnet excluded: Repair is not an ATA purpose and goods must return in the same condition. | — | yes |
| B3 | medium | Temporary admission for repair at the destination (JP) was not assessed; duty or tax on arrival may apply unless a relief is used. | Ask the repair centre's customs broker for the inward-processing / re-export relief before the first loop. | no |
| B4 | high | Semiconductor manufacturing or test equipment and specially designed parts may be strategic goods in Singapore (control list category 3B). Each export or re-export of a listed item needs an XO/XP permit applied for at least five working days ahead, even under an ATA Carnet. (HS 8414.10) | Classify each item against the Strategic Goods Control List (the 2026 Order applies from 1 Dec 2026); obtain the OEM's export classification and the origin country's licence; build 5 working days into the return plan. | yes |
| B4 | medium | Export controls of the origin country (for example on temporary exports of tools of trade or on returns after repair) were not assessed. (HS 8414.10) | Ask the equipment owner's trade-compliance team for the export classification and any licence exception before booking. | no |
| B4 | info | ATA Carnet excluded: Singapore accepts foreign carnets only for exhibitions, professional equipment and scientific equipment; 'repair_in_sg' is not one of them. | — | yes |
| B4 | medium | Re-import into MY after repair (duty/tax relief on return) was not assessed. | Confirm MY's temporary-export-for-repair procedure with the customer's broker. | no |
| B4 | medium | TIS covers only the Singapore side; the return into MY needs that country's own temporary-export or goods-returned procedure, which was not verified. An ATA Carnet covers both ends where both countries accept it. | Confirm the MY export and re-import treatment with the owner's broker before the first move. | no |

## 6. Implementation plan

| When | Milestone |
|---|---|
| W0-1 | Classify each item against the Strategic Goods Control List; obtain the owner's export classification |
| W1-2 | Choose the instrument per move (ATA Carnet, TIS or temporary export); apply for the carnet or lodge TIS security |
| W2-3 | Book air capacity, air-ride trucks and crates; file strategic-goods permits at least 5 working days before export |
| Move | Execute, track and endorse documents at each border |
| Monthly | Close out carnet vouchers and TIS permits; report open items |

**RACI** (R responsible, A accountable, C consulted, I informed)

| Activity | Customer A logistics | Solution provider | Customs broker | Origin agent / supplier | Carrier |
|---|---|---|---|---|---|
| Strategic-goods classification and permits | A | C | R | C | I |
| Carnet / TIS security | A | R | C | I | I |
| Packing, crating and indicators | C | R | I | C | I |
| Transport and handling | I | R | I | C | A |
| Re-export / discharge within period | A | R | C | I | I |
| KPI reporting | I | R | C | I | C |

## 7. KPIs and post-go-live monitoring

The quotation workbook's Monitoring sheet takes monthly actuals and computes the year-to-date average and an OK / REVIEW status. Targets come from the recommended option's results.

**B1**

| KPI | Target | Better | Trigger and action |
|---|---|---|---|
| Moves arriving within 12 days (share) | 0.95 | higher | Any miss on an event move: root-cause review before the next event |
| P90 days (metric of the RFQ) | 4.8 | lower | Above target: check permits and hold reasons |
| Temporary admissions discharged within the period (share) | 1 | higher | Any open item 30 days before expiry: file extension or re-export |
| GST or duty claims from non-discharge (count) | 0 | lower | Any claim: review the tracking process |
| Cost per move (USD, quote basis) | 17141.2 | lower | Above target by 10%: re-tender |
| Strategic-goods permits in place before export (share of moves needing one) | 1 | higher | Any miss: stop shipment, escalate |

**B2**

| KPI | Target | Better | Trigger and action |
|---|---|---|---|
| Moves arriving within 7 days (share) | 0.95 | higher | Any miss on an event move: root-cause review before the next event |
| P90 days (metric of the RFQ) | 5.3 | lower | Above target: check permits and hold reasons |
| Temporary admissions discharged within the period (share) | 1 | higher | Any open item 30 days before expiry: file extension or re-export |
| GST or duty claims from non-discharge (count) | 0 | lower | Any claim: review the tracking process |
| Cost per move (USD, quote basis) | 6539.5 | lower | Above target by 10%: re-tender |
| Strategic-goods permits in place before export (share of moves needing one) | 1 | higher | Any miss: stop shipment, escalate |

**B3**

| KPI | Target | Better | Trigger and action |
|---|---|---|---|
| Moves arriving within 35 days (share) | 0.95 | higher | Any miss on an event move: root-cause review before the next event |
| P90 days (metric of the RFQ) | 31.4 | lower | Above target: check permits and hold reasons |
| Temporary admissions discharged within the period (share) | 1 | higher | Any open item 30 days before expiry: file extension or re-export |
| GST or duty claims from non-discharge (count) | 0 | lower | Any claim: review the tracking process |
| Cost per move (USD, quote basis) | 3687.8 | lower | Above target by 10%: re-tender |
| Strategic-goods permits in place before export (share of moves needing one) | 1 | higher | Any miss: stop shipment, escalate |

**B4**

| KPI | Target | Better | Trigger and action |
|---|---|---|---|
| Moves arriving within 30 days (share) | 0.95 | higher | Any miss on an event move: root-cause review before the next event |
| P90 days (metric of the RFQ) | 28.1 | lower | Above target: check permits and hold reasons |
| Temporary admissions discharged within the period (share) | 1 | higher | Any open item 30 days before expiry: file extension or re-export |
| GST or duty claims from non-discharge (count) | 0 | lower | Any claim: review the tracking process |
| Cost per move (USD, quote basis) | 3312.3 | lower | Above target by 10%: re-tender |
| Strategic-goods permits in place before export (share of moves needing one) | 1 | higher | Any miss: stop shipment, escalate |

## 8. Assumptions and data provenance

The workbook's Assumptions sheet lists every rate and parameter used by this template, labelled REAL (official or public data), ASSUMPTION (modelling choice or unverified placeholder), ILLUSTRATIVE (example rate) or SYNTHETIC (fictional RFQ data): ASSUMPTION 1, ILLUSTRATIVE 48, REAL 2, SYNTHETIC 2.
Port and airport dwell times come from the World Bank LPI 2.0 (2024, CC BY 4.0); rate levels are anchored to the Drewry Intra-Asia Container Index (12 Nov 2026: USD 1,440 per 40ft) and the Drewry Airfreight Price Index (October 2026: USD 4.12/kg). The full source table is in docs/data_provenance.md.

## 9. Regulatory statements relied on

Each statement below was checked against the listed sources on 2026-11-15 (log: docs/regulatory_check.md); items marked not_verified are handled as labelled placeholders in the numbers.

| ID | Status | Statement | Sources |
|---|---|---|---|
| SG-ATA-ISSUER | corrected | In Singapore, local ATA Carnets are obtained from the Singapore International Chamber of Commerce (SICC), Singapore's National Guaranteeing and Issuing Association. | [sg_customs_ata_local](https://www.customs.gov.sg/permits-and-licences/import-export-facilitation-schemes/temporary-import-export/ata-carnet/local-ata-carnet/), [icc_ata](https://iccwbo.org/business-solutions/ata-carnet/), [sicc_nga_2024](https://sicc.com.sg/memberCONNECT/2024/508.html) |
| SG-ATA-NO-SAMPLES | corrected | Commercial samples are not among the purposes for which Singapore Customs accepts a foreign ATA Carnet. The SICC lists commercial samples as covered for carnets it issues for use abroad, subject to the destination's acceptance. | [sg_customs_ata_foreign](https://www.customs.gov.sg/permits-and-licences/import-export-facilitation-schemes/temporary-import-export/ata-carnet/foreign-ata-carnet/), [sicc_ata](https://sicc.com.sg/trade-documentation/ata-carnet-tdb-boft-carnets/) |
| SG-ATA-PERIOD | verified | Goods imported under a foreign ATA Carnet must be re-exported by the earlier of six months from import or one day before the carnet's validity date. | [sg_customs_ata_foreign](https://www.customs.gov.sg/permits-and-licences/import-export-facilitation-schemes/temporary-import-export/ata-carnet/foreign-ata-carnet/) |
| SG-ATA-SAME-CONDITION | verified | Goods under an ATA Carnet must be re-exported in the same condition; GST and/or duty become payable if they are sold, transferred, changed in condition or not re-exported in time. Repair or processing is not an accepted ATA purpose, so repair moves use the TIS or a temporary export permit instead. | [sg_customs_ata_foreign](https://www.customs.gov.sg/permits-and-licences/import-export-facilitation-schemes/temporary-import-export/ata-carnet/foreign-ata-carnet/), [icc_ata](https://iccwbo.org/business-solutions/ata-carnet/) |
| SG-ATA-SCOPE | verified | Singapore accepts a foreign ATA Carnet only for goods displayed or used at exhibitions, fairs or similar events, professional equipment, or scientific equipment used for testing, experiments or demonstrations. | [sg_customs_ata_foreign](https://www.customs.gov.sg/permits-and-licences/import-export-facilitation-schemes/temporary-import-export/ata-carnet/foreign-ata-carnet/) |
| SG-ATA-XO | verified | Strategic goods exported from Singapore under a local ATA Carnet still need a Strategic Goods (Control) permit (XO permit) before export. | [sg_customs_ata_local](https://www.customs.gov.sg/permits-and-licences/import-export-facilitation-schemes/temporary-import-export/ata-carnet/local-ata-carnet/) |
| SG-GST-RATE | verified | Singapore GST is 9% (from 1 January 2024). | [iras_gst_rates](https://www.iras.gov.sg/taxes/goods-services-tax-(gst)/basics-of-gst/current-gst-rates), [iras_lvg_etax](https://www.iras.gov.sg/media/docs/default-source/e-tax/gst-e-tax-guide_taxing-imported-low-value-goods-by-way-of-the-overseas-vendor-registration-regime_(1st-ed).pdf?sfvrsn=b1a36692_6) |
| SG-SGCA-3B001 | verified | The Schedule to the Strategic Goods (Control) Order 2026 (S 741/2026, in operation from 1 December 2026) lists category 3B001, equipment for manufacturing semiconductor devices or materials and specially designed components and accessories. The 2025 Order in force until then was not checked line by line. | [sg_sgco_2026](https://assets.egazette.gov.sg/2026/Legislative%20Supplements/Subsidiary%20Legislation%20Supplement/26sls741.pdf), [sg_customs_sgcl](https://www.customs.gov.sg/permits-and-licences/trade-controls-and-prohibitions/strategic-goods-control/strategic-goods-control-list/strategic-goods-control-list-overview/) |
| SG-SGCA-PERMIT | verified | An individual permit (prefixed XO or XP) is needed for each export, re-export, transhipment or transit of strategic goods, applied for at least five working days before shipment, with supporting documents such as the origin country's export licence and an end-user statement. | [sg_customs_sgc_permits](https://www.customs.gov.sg/permits-and-licences/trade-controls-and-prohibitions/strategic-goods-control/permit-and-registration-requirements/permit-and-registration-requirements-overview/), [sg_customs_sgc_individual](https://www.customs.gov.sg/permits-and-licences/trade-controls-and-prohibitions/strategic-goods-control/permit-and-registration-requirements/individual-permit-export-transhipment-and-transit/) |
| SG-SGCA-SCOPE | verified | The Strategic Goods (Control) Act, in force since 1 January 2003, regulates the export, transhipment, transit, intangible transfer and brokering of strategic goods and technology, with a catch-all for weapons-of-mass-destruction end use. | [sg_customs_sgc_overview](https://www.customs.gov.sg/permits-and-licences/trade-controls-and-prohibitions/strategic-goods-control/strategic-goods-control-overview/) |
| SG-TIS-6M | verified | Under the TIS, goods can be temporarily imported for approved purposes for up to 6 months with GST and duty suspended. | [sg_customs_tis_overview](https://www.customs.gov.sg/permits-and-licences/import-export-facilitation-schemes/temporary-import-export/temporary-import-export-scheme-overview/) |
| SG-TIS-PAYMENT | verified | If TIS goods are sold, disposed of, transferred or not re-exported in time, a Customs In-Payment permit must be taken within 3 working days. | [sg_customs_tis_additional_import](https://www.customs.gov.sg/permits-and-licences/import-export-facilitation-schemes/temporary-import-export/additional-requirements-for-import/) |
| SG-TIS-SECURITY | verified | TIS users lodge security (banker's guarantee, finance company guarantee or insurance bond). For non-dutiable, non-selected goods it is 30% of the potential GST for a GST-registered entity and 50% otherwise (50%/100% for selected goods); TradeFIRST banding can reduce or waive it. | [sg_customs_tis_overview](https://www.customs.gov.sg/permits-and-licences/import-export-facilitation-schemes/temporary-import-export/temporary-import-export-scheme-overview/), [sg_customs_tis_additional_import](https://www.customs.gov.sg/permits-and-licences/import-export-facilitation-schemes/temporary-import-export/additional-requirements-for-import/), [sg_customs_security_amount](https://www.customs.gov.sg/doing-business/getting-started/security-lodgement/what-is-the-amount-of-security-required/) |

