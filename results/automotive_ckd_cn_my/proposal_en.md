# KD kits China to Malaysia for local vehicle assembly

**RFQ** RFQ-AUTO-2026-001 · **Customer** Customer A (fictional) · **Issued** 2026-11-15 · **Valid** 30 days · **Currency** USD

> Portfolio example: the customer is fictional; freight and handling rates are **ILLUSTRATIVE** (not any carrier's or forwarder's tariff); duty and tax rates are official only where marked verified; regulatory statements were checked against official sources on 2026-11-15 (see the regulatory check log). Not tax or legal advice.

## 1. Executive summary

A vehicle assembler in the Klang Valley, Malaysia, building a compact SUV (internal-combustion) from knock-down kits sourced from two Chinese supplier clusters.

| Lane | Recommended solution | Landed cost | P90 (days) | On time (target) | Risk | Status |
|---|---|---|---|---|---|---|
| A1 | Ocean FCL (40ft HC) | USD 286/kit | 35.2 | 93.1% (38 days) | 56 | meets target |
| A2 | Rail-sea via Qinzhou (FCL) | USD 80.84/kit | 36.0 | 92.4% (38 days) | 62 | meets target |

Recommended options: annual quotation about USD 1,083,184 (logistics, VAS, insurance, permits); total landed cost including duties, taxes and inventory carrying about USD 2,202,889 a year.

**Key findings**

- On goods value, ACFTA cuts annual duty from about USD 8,007,000 (MFN) to about USD 684,000; RCEP's current rates for these lines are higher than ACFTA's, so Form E is the instrument of choice.
- HARN (8544.30.1200) does not qualify for origin (RVC below 40% and no change of heading), so MFN applies; about USD 684,000 a year of duty depends on documenting more regional content.
- Parts declared under 87.08 and similar headings need no MITI Approved Permit, but a set that amounts to an essentially complete vehicle could be classified as a CKD vehicle needing an AP; a classification ruling comes first.
- The Malaysia-China block train via Thailand and Laos made a first run in 2024, but no current official timetable was found, so it is not offered.

## 2. Requirements

- Flow: B2B import; Incoterm: FCA (Supplier's warehouse (seller's premises), China); quoting to the buyer.
- Service: at least 90% of shipments within each lane's target; weights cost 0.5, time 0.3, risk 0.2.

| Lane | Description | From → to | Target (days) |
|---|---|---|---|
| A1 | Ningbo body and interior kits to Shah Alam plant | Ningbo (CN) → Shah Alam (MY) | 38 |
| A2 | Chongqing powertrain and chassis parts to Shah Alam plant (invoiced by a Singapore trading entity) | Chongqing (CN) → Shah Alam (MY) | 38 |

## 3. Options per lane

Cost is landed cost per unit (quotation + duties and taxes + inventory carrying); P50/P90 are door-to-door days from 20,000 Monte Carlo draws; the risk score adds compliance flags, transit spread and hand-offs (0-100, lower is better).

### A1 · Ningbo body and interior kits to Shah Alam plant

| Option | Landed cost per unit | P50 | P90 | On time | Risk | Result |
|---|---|---|---|---|---|---|
| Ocean FCL (40ft HC) | USD 286 | 23.6 | 35.2 | 93.1% | 56 | ★ recommended |
| Ocean LCL | USD 395 | 28.7 | 40.7 | 85.3% | 64 | dominated |
| Air freight | USD 1,683 | 4.3 | 7.0 | 100.0% | 47 | Pareto |

- Recommended: Ocean FCL (40ft HC) at USD 286 per kit landed, P90 35.2 days, 93.1% on time against the 38-day target, risk score 56/100.
- It meets the 90.0% on-time requirement and has the best weighted score of cost, P90 time and risk among the options that do.
- Sensitivity: with a 30-day target the same option would be on time 78.5% of the time.
- Ocean LCL is dominated by Ocean FCL (40ft HC) (no better on cost, P90 or risk).
- Alternative on the Pareto front: Air freight - 488% more per kit, P90 7.0 days (-28.2), risk 47; on time 100.0%.
- Conditions to manage: [MY-KIT-CLASSIFICATION] Kit components are declared as parts. If the shipped set amounts to an essentially complete vehicle, customs may classify it as a CKD vehicle (8703 CKD lines, MITI AP needed). Not verified for this kit. (HS 8544.30.1200, 8708.29.9500, 8708.30.2900, 9401.20.1000) [FTA-ACFTA-FORM-E] ACFTA preference claimed: each shipment needs a Form E issued before or at shipment, valid one year; origin evidence (RVC >= 40%) must be kept for verification. [FTA-ORIGIN-NOT-MET] HARN (8544.30.1200): supplier RVC 38% does not meet the 40% general rule and CTH is not met, so MFN 30% applies. Annual duty at stake: USD 684,000. [MY-SCHEDULE-C] Sales tax on imported components is set to nil on the assumption that Customer A holds Schedule C (registered manufacturer) exemption; eligibility conditions were not verified. Without it, 10% sales tax applies on customs value plus duty.

### A2 · Chongqing powertrain and chassis parts to Shah Alam plant (invoiced by a Singapore trading entity)

| Option | Landed cost per unit | P50 | P90 | On time | Risk | Result |
|---|---|---|---|---|---|---|
| Rail-sea via Qinzhou (FCL) | USD 80.84 | 24.1 | 36.0 | 92.4% | 62 | ★ recommended |
| Air freight | USD 794 | 3.9 | 7.3 | 100.0% | 47 | Pareto |

- Recommended: Rail-sea via Qinzhou (FCL) at USD 80.84 per kit landed, P90 36.0 days, 92.4% on time against the 38-day target, risk score 62/100.
- It meets the 90.0% on-time requirement and has the best weighted score of cost, P90 time and risk among the options that do.
- Sensitivity: with a 30-day target the same option would be on time 76.8% of the time.
- Alternative on the Pareto front: Air freight - 882% more per kit, P90 7.3 days (-28.8), risk 47; on time 100.0%.
- Not offered: rail - No verified scheduled cross-border rail service for this lane: First run 2024; no current official timetable found. Re-enable by setting status: verified once a scheduled departure is confirmed..
- Conditions to manage: [MY-KIT-CLASSIFICATION] Kit components are declared as parts. If the shipped set amounts to an essentially complete vehicle, customs may classify it as a CKD vehicle (8703 CKD lines, MITI AP needed). Not verified for this kit. (HS 8708.40.2600, 8708.80.1600) [FTA-ACFTA-FORM-E] ACFTA preference claimed: each shipment needs a Form E issued before or at shipment, valid one year; origin evidence (RVC >= 40%) must be kept for verification. [THIRD-COUNTRY-INVOICE] Goods ship China to Malaysia but are invoiced by an entity in SG: ACFTA Form E must show the third-party invoice number in Box 10 with that invoice attached (exporter and consignee in Parties); under RCEP tick Box 17 and name the invoicing company in Box 14. Customs value follows the sale for export to Malaysia (which sale applies in a chain was not verified). [MY-SCHEDULE-C] Sales tax on imported components is set to nil on the assumption that Customer A holds Schedule C (registered manufacturer) exemption; eligibility conditions were not verified. Without it, 10% sales tax applies on customs value plus duty.

## 4. Cost build-up of the recommended options (annual)

### A1 · Ocean FCL (40ft HC)

| Cost element | Annual (USD) | Per unit (USD) | Payer | In quote |
|---|---|---|---|---|
| Pickup at supplier (truck) | 65,688 | 10.95 | buyer | yes |
| Origin terminal handling | 38,640 | 6.44 | buyer | yes |
| Export declaration | 2,160 | 0.36 | seller | no |
| Ocean freight | 414,000 | 69.00 | buyer | yes |
| Destination terminal handling | 46,920 | 7.82 | buyer | yes |
| Import declaration | 3,360 | 0.56 | buyer | yes |
| Delivery to plant (truck) | 62,652 | 10.44 | buyer | yes |
| Returnable rack management | 16,560 | 2.76 | buyer | yes |
| Cargo insurance (110% of CIF) | 27,771 | 4.63 | buyer | yes |
| Kitting and line-side sequencing | 54,000 | 9.00 | buyer | yes |
| Certificate of origin (Form E) handling | 1,920 | 0.32 | buyer | yes |
| Import duty HARN (MFN) | 702,203 | 117.03 | buyer | no |
| Pipeline inventory carrying cost | 284,163 | 47.36 | buyer | no |
| **Quotation total** | 731,511 | 121.92 |  |  |
| **Total landed cost** | 1,717,877 | 286.31 |  |  |

Seller-side costs under the Incoterm, excluded from this quotation: about USD 2,160 (e.g. export clearance).

### A2 · Rail-sea via Qinzhou (FCL)

| Cost element | Annual (USD) | Per unit (USD) | Payer | In quote |
|---|---|---|---|---|
| Pickup at supplier (truck) | 20,736 | 3.46 | buyer | yes |
| Rail to Qinzhou port | 62,400 | 10.40 | buyer | yes |
| Origin terminal handling | 13,440 | 2.24 | buyer | yes |
| Export declaration | 2,160 | 0.36 | seller | no |
| Ocean freight | 139,200 | 23.20 | buyer | yes |
| Destination terminal handling | 16,320 | 2.72 | buyer | yes |
| Import declaration | 3,360 | 0.56 | buyer | yes |
| Delivery to plant (truck) | 21,792 | 3.63 | buyer | yes |
| Returnable rack management | 5,760 | 0.96 | buyer | yes |
| Cargo insurance (110% of CIF) | 12,746 | 2.12 | buyer | yes |
| Kitting and line-side sequencing | 54,000 | 9.00 | buyer | yes |
| Certificate of origin (Form E) handling | 1,920 | 0.32 | buyer | yes |
| Pipeline inventory carrying cost | 133,338 | 22.22 | buyer | no |
| **Quotation total** | 351,674 | 58.61 |  |  |
| **Total landed cost** | 485,012 | 80.84 |  |  |

Seller-side costs under the Incoterm, excluded from this quotation: about USD 2,160 (e.g. export clearance).

## 5. Compliance and risk

### FTA origin options (imports into Malaysia)

| Lane | SKU | HS | RVC | MFN | ACFTA | RCEP | Chosen | Annual duty saved (USD) | Paperwork (USD) | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| A1 | BODY | 8708.29.9500 | 58% | 25.0% | 0.0% | 22.7% | ACFTA | 3,150,000 | 480 | worth it |
| A1 | SEAT | 9401.20.1000 | 62% | 30.0% | 0.0% | 23.7% | ACFTA | 1,170,000 | 480 | worth it |
| A1 | HARN | 8544.30.1200 | 38% | 30.0% | 0.0% (not met) | 30.0% (not met) | MFN | 0 | 0 | n/a |
| A1 | BRKE | 8708.30.2900 | 52% | 30.0% | 0.0% | 27.3% | ACFTA | 522,000 | 480 | worth it |
| A2 | GBOX | 8708.40.2600 | 64% | 25.0% | 0.0% | 22.7% | ACFTA | 1,725,000 | 960 | worth it |
| A2 | SUSP | 8708.80.1600 | 49% | 30.0% | 0.0% | 27.3% | ACFTA | 756,000 | 960 | worth it |

Documents: ACFTA needs a Form E (issued before or at shipment, presented within one year; with third-party invoicing the invoice number goes in Box 10 and the invoice is attached). RCEP accepts a certificate of origin or an approved exporter's declaration (valid one year; with third-party invoicing tick Box 17 and name the invoicing company in Box 14).

### Risk flags and mitigations

| Lane | Severity | Finding | Mitigation | Verified |
|---|---|---|---|---|
| — | info | Under FCA the seller clears goods for export and loads them at its premises; export clearance is excluded from the buyer's quotation. |  | yes |
| A1 | medium | Kit components are declared as parts. If the shipped set amounts to an essentially complete vehicle, customs may classify it as a CKD vehicle (8703 CKD lines, MITI AP needed). Not verified for this kit. (HS 8544.30.1200, 8708.29.9500, 8708.30.2900, 9401.20.1000) | Obtain a written tariff classification ruling from Malaysian customs for the kit structure; keep kit content lists per container. | no |
| A1 | medium | ACFTA preference claimed: each shipment needs a Form E issued before or at shipment, valid one year; origin evidence (RVC >= 40%) must be kept for verification. | Collect cost breakdowns from suppliers; check Form E data against the invoice before departure. | yes |
| A1 | medium | HARN (8544.30.1200): supplier RVC 38% does not meet the 40% general rule and CTH is not met, so MFN 30% applies. Annual duty at stake: USD 684,000. | Work with the supplier to document regional content (e.g. ASEAN or Chinese terminals and copper) before claiming; re-run the origin check. | yes |
| A1 | medium | Sales tax on imported components is set to nil on the assumption that Customer A holds Schedule C (registered manufacturer) exemption; eligibility conditions were not verified. Without it, 10% sales tax applies on customs value plus duty. | Confirm the Schedule C approval and its validity for each HS line before go-live. | yes |
| A1 | info | The programme is an internal-combustion SUV, so the EV component duty exemption (until 31 Dec 2027) does not apply; an EV variant would need its own eligibility check. | — | yes |
| A2 | medium | Kit components are declared as parts. If the shipped set amounts to an essentially complete vehicle, customs may classify it as a CKD vehicle (8703 CKD lines, MITI AP needed). Not verified for this kit. (HS 8708.40.2600, 8708.80.1600) | Obtain a written tariff classification ruling from Malaysian customs for the kit structure; keep kit content lists per container. | no |
| A2 | medium | ACFTA preference claimed: each shipment needs a Form E issued before or at shipment, valid one year; origin evidence (RVC >= 40%) must be kept for verification. | Collect cost breakdowns from suppliers; check Form E data against the invoice before departure. | yes |
| A2 | medium | Goods ship China to Malaysia but are invoiced by an entity in SG: ACFTA Form E must show the third-party invoice number in Box 10 with that invoice attached (exporter and consignee in Parties); under RCEP tick Box 17 and name the invoicing company in Box 14. Customs value follows the sale for export to Malaysia (which sale applies in a chain was not verified). | Align the three documents (supplier invoice, third-party invoice, Form E) before departure; keep the contract chain on file. | yes |
| A2 | medium | Sales tax on imported components is set to nil on the assumption that Customer A holds Schedule C (registered manufacturer) exemption; eligibility conditions were not verified. Without it, 10% sales tax applies on customs value plus duty. | Confirm the Schedule C approval and its validity for each HS line before go-live. | yes |
| A2 | info | The programme is an internal-combustion SUV, so the EV component duty exemption (until 31 Dec 2027) does not apply; an EV variant would need its own eligibility check. | — | yes |
| A2 | low | Rail-sea chain: domestic rail leg to Qinzhou is evidenced only by state-affiliated media; train frequency is an assumption. | Confirm the rail-sea schedule and cut-off before committing volume. | no |

## 6. Implementation plan

| When | Milestone |
|---|---|
| W0-2 | Kick-off; request a written tariff classification for the kit structure; confirm Schedule C sales-tax exemption |
| W2-4 | Collect supplier cost statements (RVC) and set up the Form E routine; agree third-party invoice wording |
| W3-5 | Tender the recommended routes; secure weekly container allocation and rail-sea slots |
| W5-6 | Pilot: one shipment per lane, measure door-to-door time and document quality |
| W7-8 | Go-live with weekly control-tower report |
| W12 | First quarterly review: lead-time buffer, routing mix, FTA claims |

**RACI** (R responsible, A accountable, C consulted, I informed)

| Activity | Customer A logistics | Solution provider | Customs broker | Origin agent / supplier | Carrier |
|---|---|---|---|---|---|
| Tariff classification and Schedule C | A | R | C | C | I |
| Origin evidence and Form E | A | C | C | R | I |
| Booking and allocation | I | R | I | C | A |
| Import declaration and duty payment | A | C | R | I | I |
| Kitting and line feed | A | R | I | I | I |
| KPI reporting | I | R | C | C | C |

## 7. KPIs and post-go-live monitoring

The quotation workbook's Monitoring sheet takes monthly actuals and computes the year-to-date average and an OK / REVIEW status. Targets come from the recommended option's results.

**A1**

| KPI | Target | Better | Trigger and action |
|---|---|---|---|
| Shipments delivered within 38 days (share) | 0.9 | higher | Two months below target: add buffer stock or move part of the volume to the next Pareto option |
| Door-to-door P90 (days) | 35.2 | lower | P90 above target by 3 days: review port dwell and transshipment |
| Logistics cost per kit (USD, quote basis) | 121.92 | lower | Above target by 5%: check container fill and surcharges |
| Import clearance, median days | 3.5 | lower | Above target: review document quality with the broker |
| Form E accepted first time (share) | 0.98 | higher | Below target: audit supplier origin data |
| Damage or shortage incidents per 100 shipments | 1 | lower | Above target: review packing and seals |

**A2**

| KPI | Target | Better | Trigger and action |
|---|---|---|---|
| Shipments delivered within 38 days (share) | 0.9 | higher | Two months below target: add buffer stock or move part of the volume to the next Pareto option |
| Door-to-door P90 (days) | 36 | lower | P90 above target by 3 days: review port dwell and transshipment |
| Logistics cost per kit (USD, quote basis) | 58.61 | lower | Above target by 5%: check container fill and surcharges |
| Import clearance, median days | 3.5 | lower | Above target: review document quality with the broker |
| Form E accepted first time (share) | 0.98 | higher | Below target: audit supplier origin data |
| Damage or shortage incidents per 100 shipments | 1 | lower | Above target: review packing and seals |

## 8. Assumptions and data provenance

The workbook's Assumptions sheet lists every rate and parameter used by this template, labelled REAL (official or public data), ASSUMPTION (modelling choice or unverified placeholder), ILLUSTRATIVE (example rate) or SYNTHETIC (fictional RFQ data): ASSUMPTION 1, ILLUSTRATIVE 24, REAL 12, SYNTHETIC 1.
Port and airport dwell times come from the World Bank LPI 2.0 (2024, CC BY 4.0); rate levels are anchored to the Drewry Intra-Asia Container Index (12 Nov 2026: USD 1,440 per 40ft) and the Drewry Airfreight Price Index (October 2026: USD 4.12/kg). The full source table is in docs/data_provenance.md.

## 9. Regulatory statements relied on

Each statement below was checked against the listed sources on 2026-11-15 (log: docs/regulatory_check.md); items marked not_verified are handled as labelled placeholders in the numbers.

| ID | Status | Statement | Sources |
|---|---|---|---|
| FTA-ACFTA-3PI | verified | ACFTA accepts a Form E when the invoice is issued by a company in a third country (Party or non-Party), provided the goods meet the rules of origin: the invoice number goes in Box 10, the exporter and consignee must be located in the Parties and the invoice is attached. | [acfta_ocp](https://asean.org/wp-content/uploads/2021/08/02a-ANNEX-1-Attachment-A-Revised-OCP_Final.pdf), [my_miti_acfta_qa](https://fta.miti.gov.my/index.php/pages/view/22) |
| FTA-ACFTA-DIRECT | verified | ACFTA preference requires direct consignment; transit through another country is allowed only if justified geographically or by transport needs, the goods are not traded or consumed there and undergo only unloading, reloading or preservation. | [acfta_roo](https://asean.org/wp-content/uploads/2021/09/02-ANNEX-1-ACFTA-Ugrading-Protocol-ACFTAROO-text-22Nov2015_13.15-f....pdf) |
| FTA-ACFTA-FORM-E | verified | A Form E is issued before or at shipment (retroactively within 12 months, marked ISSUED RETROACTIVELY) and must be submitted to the importing customs within one year of issue. | [acfta_ocp](https://asean.org/wp-content/uploads/2021/08/02a-ANNEX-1-Attachment-A-Revised-OCP_Final.pdf) |
| FTA-ACFTA-ORIGIN | verified | Under the upgraded ACFTA rules, a good not wholly obtained is originating if its regional value content is at least 40% of FOB and the final process is in a Party, or (for listed chapters) all non-originating materials change tariff heading, unless product-specific rules provide otherwise. | [acfta_roo](https://asean.org/wp-content/uploads/2021/09/02-ANNEX-1-ACFTA-Ugrading-Protocol-ACFTAROO-text-22Nov2015_13.15-f....pdf) |
| FTA-RCEP-3PI | verified | RCEP Article 3.20: an importing Party shall not deny preference only because the invoice was not issued by the exporter or producer; on the certificate, Box 17 'Third-party invoicing' is ticked and the invoicing company's name and country go in Box 14. | [rcep_text](https://asean.org/wp-content/uploads/2024/10/Regional-Comprehensive-Economic-Partnership-RCEP-Agreement-Full-Text.pdf), [rcep_co_notes](https://rcepsec.org/wp-content/uploads/2026/06/R03-RCEP-CO-Format-and-ON-1-Jan-2023.pdf) |
| FTA-RCEP-PSR | verified | RCEP product-specific rules for headings 87.08 (vehicle parts) and 85.44 (insulated wire, harnesses) are CTH or RVC40. | [rcep_text](https://asean.org/wp-content/uploads/2024/10/Regional-Comprehensive-Economic-Partnership-RCEP-Agreement-Full-Text.pdf) |
| INCO-RULES | verified | Incoterms 2020 has 11 rules: seven for any mode of transport and four (FAS, FOB, CFR, CIF) for sea and inland waterway transport. | [trade_gov_incoterms](https://www.trade.gov/know-your-incoterms) |
| MY-AP-VEHICLES | verified | An Approved Permit from MITI is required for all motor vehicles and motorcycles (including commercial vehicles) imported as CBU or CKD. | [my_miti_ap_faq](https://www.miti.gov.my/index.php/pages/view/10621) |
| MY-CKD-CLASSIFICATION | not_verified | The Malaysian tariff has CKD vehicle lines (e.g. 8703.23.21 00, CKD sedans of 1,500-1,800 cc, MFN 10% in PDK 2025). Whether a set of kit components is a vehicle in CKD form (General Interpretative Rule 2(a)) or separate parts is a classification decision that was not verified for the fictional kit. | [my_jkdm_ezhs](https://ezhs.customs.gov.my/), [my_pdk_2022](https://www.miti.gov.my/miti/resources/Approve%20Permit/P.U_._(A)_114_-_Perintah_Duti_Kastam_2022_.pdf) |
| MY-EV-CKD | verified | Budget 2023 gave locally assembled EVs a full import duty exemption on components and locally assembled CKD EVs a full excise duty and sales tax exemption, both until 31 December 2027 (reaffirmed by MITI in July 2024). Later budget changes and the eligibility conditions were not checked. | [my_budget2023_touchpoints](https://belanjawan.mof.gov.my/pdf/belanjawan2023/ucapan/touchpoint-budget-en.pdf), [my_mida_ev_2024](https://www.mida.gov.my/mida-news/govt-backs-move-for-more-locally-assembled-ev-models-miti/) |
| MY-ST-IMPORT-BASE | verified | Sales tax on imported taxable goods is charged on the customs value plus customs duty plus excise duty (Sales Tax Act 2018, s.9(2)). | [my_sales_tax_act](https://mysst.customs.gov.my/wp-content/uploads/2025/03/Sales-Tax-Act-2018.pdf) |
| MY-ST-SCHEDULE-C | verified | Under Schedule C of the Sales Tax (Persons Exempted from Payment of Tax) Order, a registered manufacturer can acquire raw materials, components and packaging used to manufacture taxable goods exempt from sales tax. Eligibility conditions and the approval process were not verified. | [my_mysst_faq](https://mysst.customs.gov.my/faq-sales-tax/) |
| MY-TARIFF-LINES | verified | Malaysian MFN, SST-column, ACFTA and RCEP rates are those shown by the customs HS Explorer (PDK 2025 schedule) on the access date; parent headings were cross-checked against the 2022 order's hierarchy for the same codes. | [my_jkdm_ezhs](https://ezhs.customs.gov.my/), [my_pdk_2022](https://www.miti.gov.my/miti/resources/Approve%20Permit/P.U_._(A)_114_-_Perintah_Duti_Kastam_2022_.pdf) |
| MY-VALUATION-CIF | verified | Malaysian customs value adds the cost of transport and insurance to the arrival of the goods in Malaysia (CIF basis), under the Customs (Rules of Valuation) Regulations 1999. | [my_jkdm_valuation](https://www.customs.gov.my/en/procedure/technical-services) |
| SVC-ILSTC | not_verified | Rail-sea services link Chongqing with Qinzhou port (New International Land-Sea Trade Corridor); state-affiliated media describe them as operating steadily. Frequency is an assumption in the kit. | [rail_ilstc_2026](https://app.ichongqing.info/mixmedia/a/202601/10/WS6961a39be4b05476c268ee7e.html) |

