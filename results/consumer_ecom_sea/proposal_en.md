# Cross-border e-commerce parcels from China and Singapore to Malaysia, Indonesia, Thailand and the Philippines

**RFQ** RFQ-ECOM-2026-003 · **Customer** Customer A (fictional) · **Issued** 2026-11-15 · **Valid** 30 days · **Currency** USD

> Portfolio example: the customer is fictional; freight and handling rates are **ILLUSTRATIVE** (not any carrier's or forwarder's tariff); duty and tax rates are official only where marked verified; regulatory statements were checked against official sources on 2026-11-15 (see the regulatory check log). Not tax or legal advice.

## 1. Executive summary

A direct-to-consumer lifestyle brand selling apparel, wireless earphones and bags through its own web shop. It ships from a Shenzhen warehouse and a Singapore regional stock point and wants delivered-duty-paid parcels.

| Lane | Recommended solution | Landed cost | P90 (days) | On time (target) | Risk | Status |
|---|---|---|---|---|---|---|
| C1 | Ocean bulk + local fulfilment | USD 4.13/parcel | 3.0 | 100.0% (7 days) | 29 | meets target |
| C2 | Ocean bulk + local fulfilment | USD 7.14/parcel | 4.5 | 100.0% (7 days) | 39 | meets target |
| C3 | Ocean bulk + local fulfilment | USD 7.08/parcel | 3.0 | 100.0% (7 days) | 29 | meets target |
| C4 | Ocean bulk + local fulfilment | USD 8.15/parcel | 4.5 | 100.0% (7 days) | 29 | meets target |
| C5 | Cross-border road | USD 6.14/parcel | 6.7 | 61.7% (5 days) | 28 | below target |
| C6 | Ocean bulk + local fulfilment | USD 7.53/parcel | 4.5 | 96.9% (5 days) | 39 | meets target |

Recommended options: annual quotation about USD 1,474,726 (logistics, VAS, insurance, permits); total landed cost including duties, taxes and inventory carrying about USD 3,300,003 a year.

**Key findings**

- Malaysia: low-value goods sold at up to RM500 carry 10% sales tax on the sale price, charged by the registered seller; bulk imports pay single-stage sales tax on CIF plus duty, a lower base.
- Indonesia: consignments above FOB USD 3 are taxed; apparel and bags pay 25% duty plus 5% income tax, plus VAT at an effective 11%, so parcels carry a much higher tax load than local stock.
- Thailand: since 1 January 2026 only items worth up to 1 baht are duty-free, so every parcel pays duty and 7% VAT (the duty rates used here are unverified placeholders).
- Philippines: parcels up to PHP 10,000 FOB pay no duties or taxes, the lightest tax load, but parcels miss the 7-day target.
- Singapore: low-value goods (sale value up to S$400, by air or post) bear GST collected by OVR-registered vendors since 1 January 2023; no lane here ends in Singapore, so it is shown for comparison only.

## 2. Requirements

- Flow: B2C parcels; Incoterm: DDP (Consumer's address); quoting to the seller.
- Service: at least 90% of shipments within each lane's target; weights cost 0.5, time 0.3, risk 0.2.

| Lane | Description | From → to | Target (days) |
|---|---|---|---|
| C1 | Shenzhen to Klang Valley, Malaysia | Shenzhen (CN) → Klang Valley (MY) | 7 |
| C2 | Shenzhen to Greater Jakarta, Indonesia | Shenzhen (CN) → Greater Jakarta (ID) | 7 |
| C3 | Shenzhen to Bangkok, Thailand | Shenzhen (CN) → Bangkok (TH) | 7 |
| C4 | Shenzhen to Metro Manila, Philippines | Shenzhen (CN) → Metro Manila (PH) | 7 |
| C5 | Singapore stock point to Klang Valley, Malaysia | Singapore (SG) → Klang Valley (MY) | 5 |
| C6 | Singapore stock point to Greater Jakarta, Indonesia | Singapore (SG) → Greater Jakarta (ID) | 5 |

## 3. Options per lane

Cost is landed cost per unit (quotation + duties and taxes + inventory carrying); P50/P90 are door-to-door days from 20,000 Monte Carlo draws; the risk score adds compliance flags, transit spread and hand-offs (0-100, lower is better).

### C1 · Shenzhen to Klang Valley, Malaysia

| Option | Landed cost per unit | P50 | P90 | On time | Risk | Result |
|---|---|---|---|---|---|---|
| Air parcel, DDP | USD 7.09 | 5.0 | 8.3 | 84.0% | 39 | dominated |
| Ocean bulk + local fulfilment | USD 4.13 | 2.2 | 3.0 | 100.0% | 29 | ★ recommended |

- Recommended: Ocean bulk + local fulfilment at USD 4.13 per parcel landed, P90 3.0 days, 100.0% on time against the 7-day target, risk score 29/100.
- It meets the 90.0% on-time requirement and has the best weighted score of cost, P90 time and risk among the options that do.
- Sensitivity: with a 6-day target the same option would be on time 100.0% of the time.
- Air parcel, DDP is dominated by Ocean bulk + local fulfilment (no better on cost, P90 or risk).
- Conditions to manage: [RADIO-TYPE-APPROVAL] Wireless audio devices may need radio type approval or registration in the destination; not verified. (HS 8518.30.2000) [BULK-IOR] Bulk import needs a local importer of record (own entity or appointed importer) with the destination tax registrations; local stock adds forecast and obsolescence risk.

### C2 · Shenzhen to Greater Jakarta, Indonesia

| Option | Landed cost per unit | P50 | P90 | On time | Risk | Result |
|---|---|---|---|---|---|---|
| Air parcel, DDP | USD 15.81 | 7.1 | 12.1 | 48.8% | 31 | Pareto |
| Sea-air via Singapore | USD 15.72 | 23.7 | 31.5 | 0.0% | 40 | dominated |
| Ocean bulk + local fulfilment | USD 7.14 | 3.2 | 4.5 | 100.0% | 39 | ★ recommended |

- Recommended: Ocean bulk + local fulfilment at USD 7.14 per parcel landed, P90 4.5 days, 100.0% on time against the 7-day target, risk score 39/100.
- It meets the 90.0% on-time requirement and has the best weighted score of cost, P90 time and risk among the options that do.
- Sensitivity: with a 6-day target the same option would be on time 100.0% of the time.
- Alternative on the Pareto front: Air parcel, DDP - 121% more per parcel, P90 12.1 days (+7.5), risk 31; on time 48.8% (below target).
- Sea-air via Singapore is dominated by Ocean bulk + local fulfilment (no better on cost, P90 or risk).
- Conditions to manage: [RADIO-TYPE-APPROVAL] Wireless audio devices may need radio type approval or registration in the destination; not verified. (HS 8518.30.2000) [ID-BULK-LICENSING] Bulk imports of apparel, footwear, bags or electronics into Indonesia may need trade-ministry import approvals; not verified. (HS 4202.92.9000, 6109.10.2000, 8518.30.2000) [BULK-IOR] Bulk import needs a local importer of record (own entity or appointed importer) with the destination tax registrations; local stock adds forecast and obsolescence risk.

### C3 · Shenzhen to Bangkok, Thailand

| Option | Landed cost per unit | P50 | P90 | On time | Risk | Result |
|---|---|---|---|---|---|---|
| Air parcel, DDP | USD 13.46 | 5.9 | 10.3 | 68.0% | 40 | dominated |
| Cross-border rail | USD 14.30 | 14.0 | 17.3 | 0.0% | 39 | dominated |
| Ocean bulk + local fulfilment | USD 7.08 | 2.2 | 3.0 | 100.0% | 29 | ★ recommended |

- Recommended: Ocean bulk + local fulfilment at USD 7.08 per parcel landed, P90 3.0 days, 100.0% on time against the 7-day target, risk score 29/100.
- It meets the 90.0% on-time requirement and has the best weighted score of cost, P90 time and risk among the options that do.
- Sensitivity: with a 6-day target the same option would be on time 100.0% of the time.
- Air parcel, DDP is dominated by Ocean bulk + local fulfilment (no better on cost, P90 or risk).
- Cross-border rail is dominated by Ocean bulk + local fulfilment (no better on cost, P90 or risk).
- Conditions to manage: [RADIO-TYPE-APPROVAL] Wireless audio devices may need radio type approval or registration in the destination; not verified. (HS 8518.30.2000) [BULK-IOR] Bulk import needs a local importer of record (own entity or appointed importer) with the destination tax registrations; local stock adds forecast and obsolescence risk.

### C4 · Shenzhen to Metro Manila, Philippines

| Option | Landed cost per unit | P50 | P90 | On time | Risk | Result |
|---|---|---|---|---|---|---|
| Air parcel, DDP | USD 4.45 | 6.8 | 12.3 | 54.1% | 36 | Pareto |
| Ocean bulk + local fulfilment | USD 8.15 | 3.2 | 4.5 | 100.0% | 29 | ★ recommended |

- Recommended: Ocean bulk + local fulfilment at USD 8.15 per parcel landed, P90 4.5 days, 100.0% on time against the 7-day target, risk score 29/100.
- It meets the 90.0% on-time requirement and has the best weighted score of cost, P90 time and risk among the options that do.
- Sensitivity: with a 6-day target the same option would be on time 100.0% of the time.
- Alternative on the Pareto front: Air parcel, DDP - 45% less per parcel, P90 12.3 days (+7.8), risk 36; on time 54.1% (below target).
- Not offered: sea_air - Singapore hub is off-route: via-hub distance is 4.2x the direct distance (limit 1.6x).
- Conditions to manage: [RADIO-TYPE-APPROVAL] Wireless audio devices may need radio type approval or registration in the destination; not verified. (HS 8518.30.2000) [BULK-IOR] Bulk import needs a local importer of record (own entity or appointed importer) with the destination tax registrations; local stock adds forecast and obsolescence risk.

### C5 · Singapore stock point to Klang Valley, Malaysia

| Option | Landed cost per unit | P50 | P90 | On time | Risk | Result |
|---|---|---|---|---|---|---|
| Cross-border road | USD 6.14 | 4.8 | 6.7 | 61.7% | 28 | ★ recommended |
| Air parcel, DDP | USD 6.53 | 4.9 | 8.2 | 54.8% | 39 | dominated |

- No option reaches 90.0% on time within 5 days. Recommended for now: Cross-border road (61.7% on time, P90 6.7 days, USD 6.14 per parcel); the target or the lead time needs to be renegotiated.
- Air parcel, DDP is dominated by Cross-border road (no better on cost, P90 or risk).
- Conditions to manage: [RADIO-TYPE-APPROVAL] Wireless audio devices may need radio type approval or registration in the destination; not verified. (HS 8518.30.2000) [MY-LVG-REGISTRATION] Malaysian LVG sales of about RM 17,841,600 a year exceed the RM 500,000 registration threshold: the seller must register, charge 10% sales tax at checkout and print the LVG registration number on parcels and waybills.

### C6 · Singapore stock point to Greater Jakarta, Indonesia

| Option | Landed cost per unit | P50 | P90 | On time | Risk | Result |
|---|---|---|---|---|---|---|
| Air parcel, DDP | USD 15.31 | 6.9 | 12.0 | 12.0% | 31 | Pareto |
| Ocean bulk + local fulfilment | USD 7.53 | 3.2 | 4.5 | 96.9% | 39 | ★ recommended |

- Recommended: Ocean bulk + local fulfilment at USD 7.53 per parcel landed, P90 4.5 days, 96.9% on time against the 5-day target, risk score 39/100.
- It meets the 90.0% on-time requirement and has the best weighted score of cost, P90 time and risk among the options that do.
- Sensitivity: with a 4-day target the same option would be on time 78.5% of the time.
- Alternative on the Pareto front: Air parcel, DDP - 103% more per parcel, P90 12.0 days (+7.5), risk 31; on time 12.0% (below target).
- Conditions to manage: [RADIO-TYPE-APPROVAL] Wireless audio devices may need radio type approval or registration in the destination; not verified. (HS 8518.30.2000) [ID-BULK-LICENSING] Bulk imports of apparel, footwear, bags or electronics into Indonesia may need trade-ministry import approvals; not verified. (HS 4202.92.9000, 6109.10.2000, 8518.30.2000) [BULK-IOR] Bulk import needs a local importer of record (own entity or appointed importer) with the destination tax registrations; local stock adds forecast and obsolescence risk.

## 4. Cost build-up of the recommended options (annual)

### C1 · Ocean bulk + local fulfilment

| Cost element | Annual (USD) | Per unit (USD) | Payer | In quote |
|---|---|---|---|---|
| Pickup at origin warehouse | 5,564 | 0.05 | seller | yes |
| Origin CFS | 7,668 | 0.07 | seller | yes |
| LCL ocean freight | 20,128 | 0.19 | seller | yes |
| Destination CFS | 9,585 | 0.09 | seller | yes |
| Delivery to local fulfilment centre | 5,564 | 0.05 | seller | yes |
| Export declaration | 2,340 | 0.02 | seller | yes |
| Import declaration (formal entry) | 3,640 | 0.03 | seller | yes |
| Consumption tax: apparel | 41,898 | 0.39 | seller | no |
| Consumption tax: earphones | 40,222 | 0.37 | seller | no |
| Consumption tax: bags | 17,876 | 0.17 | seller | no |
| Storage at local fulfilment centre | 6,948 | 0.06 | seller | yes |
| Pick and pack | 64,800 | 0.60 | seller | yes |
| Inventory carrying cost (pipeline and local stock) | 28,067 | 0.26 | seller | no |
| Last-mile delivery | 172,800 | 1.60 | seller | yes |
| Relabelling | 19,440 | 0.18 | seller | yes |
| **Quotation total** | 318,478 | 2.95 |  |  |
| **Total landed cost** | 446,541 | 4.13 |  |  |

### C2 · Ocean bulk + local fulfilment

| Cost element | Annual (USD) | Per unit (USD) | Payer | In quote |
|---|---|---|---|---|
| Pickup at origin warehouse | 5,564 | 0.04 | seller | yes |
| Origin CFS | 10,224 | 0.07 | seller | yes |
| LCL ocean freight | 26,838 | 0.19 | seller | yes |
| Destination CFS | 12,780 | 0.09 | seller | yes |
| Delivery to local fulfilment centre | 5,564 | 0.04 | seller | yes |
| Export declaration | 2,340 | 0.02 | seller | yes |
| Import declaration (formal entry) | 4,420 | 0.03 | seller | yes |
| Import duty: apparel | 55,786 | 0.39 | seller | no |
| Consumption tax: apparel | 190,080 | 1.32 | seller | no |
| Import duty: earphones | 53,555 | 0.37 | seller | no |
| Consumption tax: earphones | 185,328 | 1.29 | seller | no |
| Import duty: bags | 23,802 | 0.17 | seller | no |
| Consumption tax: bags | 91,872 | 0.64 | seller | no |
| Storage at local fulfilment centre | 9,265 | 0.06 | seller | yes |
| Pick and pack | 86,400 | 0.60 | seller | yes |
| Inventory carrying cost (pipeline and local stock) | 37,359 | 0.26 | seller | no |
| Last-mile delivery | 201,600 | 1.40 | seller | yes |
| Relabelling | 25,920 | 0.18 | seller | yes |
| **Quotation total** | 390,915 | 2.71 |  |  |
| **Total landed cost** | 1,028,696 | 7.14 |  |  |

### C3 · Ocean bulk + local fulfilment

| Cost element | Annual (USD) | Per unit (USD) | Payer | In quote |
|---|---|---|---|---|
| Pickup at origin warehouse | 5,564 | 0.07 | seller | yes |
| Origin CFS | 5,964 | 0.07 | seller | yes |
| LCL ocean freight | 15,656 | 0.19 | seller | yes |
| Destination CFS | 7,455 | 0.09 | seller | yes |
| Delivery to local fulfilment centre | 5,564 | 0.07 | seller | yes |
| Export declaration | 2,340 | 0.03 | seller | yes |
| Import declaration (formal entry) | 3,900 | 0.05 | seller | yes |
| Import duty: apparel | 97,917 | 1.17 | seller | no |
| Consumption tax: apparel | 70,560 | 0.84 | seller | no |
| Import duty: earphones | 31,333 | 0.37 | seller | no |
| Consumption tax: earphones | 68,796 | 0.82 | seller | no |
| Import duty: bags | 27,852 | 0.33 | seller | no |
| Consumption tax: bags | 34,104 | 0.41 | seller | no |
| Storage at local fulfilment centre | 5,404 | 0.06 | seller | yes |
| Pick and pack | 50,400 | 0.60 | seller | yes |
| Inventory carrying cost (pipeline and local stock) | 20,946 | 0.25 | seller | no |
| Last-mile delivery | 126,000 | 1.50 | seller | yes |
| Relabelling | 15,120 | 0.18 | seller | yes |
| **Quotation total** | 243,367 | 2.90 |  |  |
| **Total landed cost** | 594,875 | 7.08 |  |  |

### C4 · Ocean bulk + local fulfilment

| Cost element | Annual (USD) | Per unit (USD) | Payer | In quote |
|---|---|---|---|---|
| Pickup at origin warehouse | 5,564 | 0.06 | seller | yes |
| Origin CFS | 6,816 | 0.07 | seller | yes |
| LCL ocean freight | 17,892 | 0.19 | seller | yes |
| Destination CFS | 8,520 | 0.09 | seller | yes |
| Delivery to local fulfilment centre | 5,564 | 0.06 | seller | yes |
| Export declaration | 2,340 | 0.02 | seller | yes |
| Import declaration (formal entry) | 4,160 | 0.04 | seller | yes |
| Import duty: apparel | 55,903 | 0.58 | seller | no |
| Consumption tax: apparel | 138,240 | 1.44 | seller | no |
| Import duty: earphones | 25,044 | 0.26 | seller | no |
| Consumption tax: earphones | 134,784 | 1.40 | seller | no |
| Import duty: bags | 23,852 | 0.25 | seller | no |
| Consumption tax: bags | 66,816 | 0.70 | seller | no |
| Storage at local fulfilment centre | 6,176 | 0.06 | seller | yes |
| Pick and pack | 57,600 | 0.60 | seller | yes |
| Inventory carrying cost (pipeline and local stock) | 23,916 | 0.25 | seller | no |
| Last-mile delivery | 182,400 | 1.90 | seller | yes |
| Relabelling | 17,280 | 0.18 | seller | yes |
| **Quotation total** | 314,312 | 3.27 |  |  |
| **Total landed cost** | 782,867 | 8.15 |  |  |

### C5 · Cross-border road

| Cost element | Annual (USD) | Per unit (USD) | Payer | In quote |
|---|---|---|---|---|
| First-mile collection and sort | 2,700 | 0.07 | seller | yes |
| Export clearance (e-commerce) | 1,800 | 0.05 | seller | yes |
| Cross-border trucking Singapore-Malaysia | 1,890 | 0.05 | seller | yes |
| Import declaration per truck (K1) | 21,840 | 0.61 | seller | yes |
| Destination clearance (B2C) | 9,000 | 0.25 | seller | yes |
| Consumption tax: apparel | 43,200 | 1.20 | seller | no |
| Consumption tax: earphones | 42,120 | 1.17 | seller | no |
| Consumption tax: bags | 20,880 | 0.58 | seller | no |
| Last-mile delivery | 57,600 | 1.60 | seller | yes |
| Relabelling | 6,480 | 0.18 | seller | yes |
| Parcel packing | 12,600 | 0.35 | seller | yes |
| In-transit inventory carrying cost | 902 | 0.03 | seller | no |
| **Quotation total** | 113,910 | 3.16 |  |  |
| **Total landed cost** | 221,012 | 6.14 |  |  |

### C6 · Ocean bulk + local fulfilment

| Cost element | Annual (USD) | Per unit (USD) | Payer | In quote |
|---|---|---|---|---|
| Pickup at origin warehouse | 5,564 | 0.19 | seller | yes |
| Origin CFS | 2,130 | 0.07 | seller | yes |
| LCL ocean freight | 3,994 | 0.13 | seller | yes |
| Destination CFS | 2,662 | 0.09 | seller | yes |
| Delivery to local fulfilment centre | 5,564 | 0.19 | seller | yes |
| Export declaration | 2,080 | 0.07 | seller | yes |
| Import declaration (formal entry) | 4,420 | 0.15 | seller | yes |
| Import duty: apparel | 11,740 | 0.39 | seller | no |
| Consumption tax: apparel | 39,600 | 1.32 | seller | no |
| Import duty: earphones | 11,270 | 0.38 | seller | no |
| Consumption tax: earphones | 38,610 | 1.29 | seller | no |
| Import duty: bags | 5,009 | 0.17 | seller | no |
| Consumption tax: bags | 19,140 | 0.64 | seller | no |
| Storage at local fulfilment centre | 1,930 | 0.06 | seller | yes |
| Pick and pack | 18,000 | 0.60 | seller | yes |
| Inventory carrying cost (pipeline and local stock) | 6,898 | 0.23 | seller | no |
| Last-mile delivery | 42,000 | 1.40 | seller | yes |
| Relabelling | 5,400 | 0.18 | seller | yes |
| **Quotation total** | 93,744 | 3.12 |  |  |
| **Total landed cost** | 226,011 | 7.53 |  |  |

## 5. Compliance and risk

### Low-value regimes by destination (one-item parcel, air courier)

| Destination | Category | Price (USD) | Parcel duty | Parcel taxes | Rule applied | Bulk route taxes (per unit) |
|---|---|---|---|---|---|---|
| MY | apparel | 24.00 | 0.00 | 2.40 | MY LVG + air-courier de minimis | 0.75 |
| MY | earphones | 39.00 | 0.00 | 3.90 | MY LVG + air-courier de minimis | 1.20 |
| MY | bags | 29.00 | 0.00 | 2.90 | MY LVG + air-courier de minimis | 0.80 |
| ID | apparel | 24.00 | 6.88 | 5.50 | ID consignment USD 3-1,500 | 3.39 |
| ID | earphones | 39.00 | 3.19 | 5.03 | ID consignment USD 3-1,500 | 5.49 |
| ID | bags | 29.00 | 8.12 | 6.50 | ID consignment USD 3-1,500 | 3.99 |
| TH | apparel | 24.00 | 8.25 | 2.50 | TH dutiable from 1 Jan 2026 (placeholder MFN) | 3.93 |
| TH | earphones | 39.00 | 4.25 | 3.27 | TH dutiable from 1 Jan 2026 (placeholder MFN) | 3.93 |
| TH | bags | 29.00 | 6.50 | 2.73 | TH dutiable from 1 Jan 2026 (placeholder MFN) | 3.63 |
| PH | apparel | 24.00 | 0.00 | 0.00 | PH de minimis (FOB <= PHP 10,000) | 4.00 |
| PH | earphones | 39.00 | 0.00 | 0.00 | PH de minimis (FOB <= PHP 10,000) | 5.52 |
| PH | bags | 29.00 | 0.00 | 0.00 | PH de minimis (FOB <= PHP 10,000) | 4.68 |

Thai and Philippine MFN rates and Indonesian bulk MFN rates are unverified placeholders; bulk-route taxes are Malaysian import sales tax or, in VAT countries, output VAT on the retail price.

### Risk flags and mitigations

| Lane | Severity | Finding | Mitigation | Verified |
|---|---|---|---|---|
| — | medium | DDP makes the seller the importer of record; a non-resident seller needs an appointed importer or a registered tax position in each market. |  | yes |
| C1 | medium | Products containing lithium batteries fall under dangerous-goods rules for air transport; the specific requirements were not verified in this project. (HS 8518.30.2000) | Collect the battery test summary and packing instruction from the supplier; confirm the air line-haul accepts the battery type. | no |
| C1 | medium | Wireless audio devices may need radio type approval or registration in the destination; not verified. (HS 8518.30.2000) | Check the destination telecom regulator's requirements before listing the product. | no |
| C1 | medium | Malaysian LVG sales of about RM 17,841,600 a year exceed the RM 500,000 registration threshold: the seller must register, charge 10% sales tax at checkout and print the LVG registration number on parcels and waybills. | Register before go-live; pass the LVG number in the pre-alert data so import sales tax is not charged twice. | yes |
| C1 | medium | Bulk import needs a local importer of record (own entity or appointed importer) with the destination tax registrations; local stock adds forecast and obsolescence risk. | Decide the importer-of-record model before launch; start with the fastest-moving SKUs. | — |
| C2 | medium | Products containing lithium batteries fall under dangerous-goods rules for air transport; the specific requirements were not verified in this project. (HS 8518.30.2000) | Collect the battery test summary and packing instruction from the supplier; confirm the air line-haul accepts the battery type. | no |
| C2 | medium | Wireless audio devices may need radio type approval or registration in the destination; not verified. (HS 8518.30.2000) | Check the destination telecom regulator's requirements before listing the product. | no |
| C2 | medium | Bulk imports of apparel, footwear, bags or electronics into Indonesia may need trade-ministry import approvals; not verified. (HS 4202.92.9000, 6109.10.2000, 8518.30.2000) | Use an importer of record that holds the required import identity and approvals; confirm before the first shipment. | no |
| C2 | info | Indonesian consignments above FOB USD 3 pay 7.5% duty, or 25% for apparel and bags (plus 5% income tax), plus VAT at an effective 11%. | — | yes |
| C2 | medium | Bulk import needs a local importer of record (own entity or appointed importer) with the destination tax registrations; local stock adds forecast and obsolescence risk. | Decide the importer-of-record model before launch; start with the fastest-moving SKUs. | — |
| C3 | medium | Products containing lithium batteries fall under dangerous-goods rules for air transport; the specific requirements were not verified in this project. (HS 8518.30.2000) | Collect the battery test summary and packing instruction from the supplier; confirm the air line-haul accepts the battery type. | no |
| C3 | medium | Wireless audio devices may need radio type approval or registration in the destination; not verified. (HS 8518.30.2000) | Check the destination telecom regulator's requirements before listing the product. | no |
| C3 | medium | Since 1 January 2026 Thailand exempts from duty only items worth up to 1 baht, so every parcel is dutiable and VAT applies; the duty rates used here are placeholders (not verified). | Confirm the tariff lines and rates with a Thai broker before launch. | no |
| C3 | medium | Bulk import needs a local importer of record (own entity or appointed importer) with the destination tax registrations; local stock adds forecast and obsolescence risk. | Decide the importer-of-record model before launch; start with the fastest-moving SKUs. | — |
| C4 | medium | Products containing lithium batteries fall under dangerous-goods rules for air transport; the specific requirements were not verified in this project. (HS 8518.30.2000) | Collect the battery test summary and packing instruction from the supplier; confirm the air line-haul accepts the battery type. | no |
| C4 | medium | Wireless audio devices may need radio type approval or registration in the destination; not verified. (HS 8518.30.2000) | Check the destination telecom regulator's requirements before listing the product. | no |
| C4 | low | Parcels at or below PHP 10,000 FOB/FCA pay no duties and taxes in the Philippines (CMTA s.423); whether the threshold has been CPI-adjusted was not verified. | Re-check the current Bureau of Customs administrative order before relying on the threshold. | no |
| C4 | medium | Bulk import needs a local importer of record (own entity or appointed importer) with the destination tax registrations; local stock adds forecast and obsolescence risk. | Decide the importer-of-record model before launch; start with the fastest-moving SKUs. | — |
| C5 | medium | Products containing lithium batteries fall under dangerous-goods rules for air transport; the specific requirements were not verified in this project. (HS 8518.30.2000) | Collect the battery test summary and packing instruction from the supplier; confirm the air line-haul accepts the battery type. | no |
| C5 | medium | Wireless audio devices may need radio type approval or registration in the destination; not verified. (HS 8518.30.2000) | Check the destination telecom regulator's requirements before listing the product. | no |
| C5 | medium | Malaysian LVG sales of about RM 17,841,600 a year exceed the RM 500,000 registration threshold: the seller must register, charge 10% sales tax at checkout and print the LVG registration number on parcels and waybills. | Register before go-live; pass the LVG number in the pre-alert data so import sales tax is not charged twice. | yes |
| C6 | medium | Products containing lithium batteries fall under dangerous-goods rules for air transport; the specific requirements were not verified in this project. (HS 8518.30.2000) | Collect the battery test summary and packing instruction from the supplier; confirm the air line-haul accepts the battery type. | no |
| C6 | medium | Wireless audio devices may need radio type approval or registration in the destination; not verified. (HS 8518.30.2000) | Check the destination telecom regulator's requirements before listing the product. | no |
| C6 | medium | Bulk imports of apparel, footwear, bags or electronics into Indonesia may need trade-ministry import approvals; not verified. (HS 4202.92.9000, 6109.10.2000, 8518.30.2000) | Use an importer of record that holds the required import identity and approvals; confirm before the first shipment. | no |
| C6 | info | Indonesian consignments above FOB USD 3 pay 7.5% duty, or 25% for apparel and bags (plus 5% income tax), plus VAT at an effective 11%. | — | yes |
| C6 | medium | Bulk import needs a local importer of record (own entity or appointed importer) with the destination tax registrations; local stock adds forecast and obsolescence risk. | Decide the importer-of-record model before launch; start with the fastest-moving SKUs. | — |

## 6. Implementation plan

| When | Milestone |
|---|---|
| W0-2 | Register for Malaysian LVG sales tax; choose the importer-of-record model per market; check battery and radio rules |
| W2-4 | Integrate checkout tax calculation, HS codes and pre-alert data (incl. the LVG number) |
| W4-6 | Tender line-haul and last mile; set up local fulfilment where bulk stock is recommended |
| W6 | Pilot 500 parcels per lane; measure delivery time, holds and tax accuracy |
| W8 | Go-live with weekly dashboard |
| W12 | Review the split between parcels and local stock per market |

**RACI** (R responsible, A accountable, C consulted, I informed)

| Activity | Customer A logistics | Solution provider | Customs broker | Origin agent / supplier | Carrier |
|---|---|---|---|---|---|
| Tax registrations and checkout tax | A | C | C | I | I |
| Importer of record and licences | A | C | R | I | I |
| Line-haul and clearance | I | R | R | C | A |
| Local fulfilment and last mile | C | R | I | I | A |
| Product compliance (batteries, radio) | A | C | C | R | I |
| KPI reporting | I | R | C | I | C |

## 7. KPIs and post-go-live monitoring

The quotation workbook's Monitoring sheet takes monthly actuals and computes the year-to-date average and an OK / REVIEW status. Targets come from the recommended option's results.

**C1**

| KPI | Target | Better | Trigger and action |
|---|---|---|---|
| Parcels delivered within 7 days (share) | 0.9 | higher | Two weeks below target: rebalance stock or carriers |
| P90 delivery days | 3 | lower | Above target: check clearance holds and last mile |
| Cost to serve per parcel incl. duties and taxes (USD) | 4.13 | lower | Above target by 5%: review weights, rates and tax mix |
| Customs hold rate (share of parcels) | 0.03 | lower | Above target: audit HS codes and declared values |
| Duties and taxes per parcel (USD) | 0.93 | lower | Deviation above 5%: check rates and thresholds |
| Damage or loss rate (share) | 0.005 | lower | Above target: review packaging |

**C2**

| KPI | Target | Better | Trigger and action |
|---|---|---|---|
| Parcels delivered within 7 days (share) | 0.9 | higher | Two weeks below target: rebalance stock or carriers |
| P90 delivery days | 4.5 | lower | Above target: check clearance holds and last mile |
| Cost to serve per parcel incl. duties and taxes (USD) | 7.14 | lower | Above target by 5%: review weights, rates and tax mix |
| Customs hold rate (share of parcels) | 0.03 | lower | Above target: audit HS codes and declared values |
| Duties and taxes per parcel (USD) | 4.17 | lower | Deviation above 5%: check rates and thresholds |
| Damage or loss rate (share) | 0.005 | lower | Above target: review packaging |

**C3**

| KPI | Target | Better | Trigger and action |
|---|---|---|---|
| Parcels delivered within 7 days (share) | 0.9 | higher | Two weeks below target: rebalance stock or carriers |
| P90 delivery days | 3 | lower | Above target: check clearance holds and last mile |
| Cost to serve per parcel incl. duties and taxes (USD) | 7.08 | lower | Above target by 5%: review weights, rates and tax mix |
| Customs hold rate (share of parcels) | 0.03 | lower | Above target: audit HS codes and declared values |
| Duties and taxes per parcel (USD) | 3.94 | lower | Deviation above 5%: check rates and thresholds |
| Damage or loss rate (share) | 0.005 | lower | Above target: review packaging |

**C4**

| KPI | Target | Better | Trigger and action |
|---|---|---|---|
| Parcels delivered within 7 days (share) | 0.9 | higher | Two weeks below target: rebalance stock or carriers |
| P90 delivery days | 4.5 | lower | Above target: check clearance holds and last mile |
| Cost to serve per parcel incl. duties and taxes (USD) | 8.15 | lower | Above target by 5%: review weights, rates and tax mix |
| Customs hold rate (share of parcels) | 0.03 | lower | Above target: audit HS codes and declared values |
| Duties and taxes per parcel (USD) | 4.63 | lower | Deviation above 5%: check rates and thresholds |
| Damage or loss rate (share) | 0.005 | lower | Above target: review packaging |

**C5**

| KPI | Target | Better | Trigger and action |
|---|---|---|---|
| Parcels delivered within 5 days (share) | 0.9 | higher | Two weeks below target: rebalance stock or carriers |
| P90 delivery days | 6.7 | lower | Above target: check clearance holds and last mile |
| Cost to serve per parcel incl. duties and taxes (USD) | 6.14 | lower | Above target by 5%: review weights, rates and tax mix |
| Customs hold rate (share of parcels) | 0.03 | lower | Above target: audit HS codes and declared values |
| Duties and taxes per parcel (USD) | 2.95 | lower | Deviation above 5%: check rates and thresholds |
| Damage or loss rate (share) | 0.005 | lower | Above target: review packaging |

**C6**

| KPI | Target | Better | Trigger and action |
|---|---|---|---|
| Parcels delivered within 5 days (share) | 0.9 | higher | Two weeks below target: rebalance stock or carriers |
| P90 delivery days | 4.5 | lower | Above target: check clearance holds and last mile |
| Cost to serve per parcel incl. duties and taxes (USD) | 7.53 | lower | Above target by 5%: review weights, rates and tax mix |
| Customs hold rate (share of parcels) | 0.03 | lower | Above target: audit HS codes and declared values |
| Duties and taxes per parcel (USD) | 4.18 | lower | Deviation above 5%: check rates and thresholds |
| Damage or loss rate (share) | 0.005 | lower | Above target: review packaging |

## 8. Assumptions and data provenance

The workbook's Assumptions sheet lists every rate and parameter used by this template, labelled REAL (official or public data), ASSUMPTION (modelling choice or unverified placeholder), ILLUSTRATIVE (example rate) or SYNTHETIC (fictional RFQ data): ASSUMPTION 38, ILLUSTRATIVE 40, REAL 25.
Port and airport dwell times come from the World Bank LPI 2.0 (2024, CC BY 4.0); rate levels are anchored to the Drewry Intra-Asia Container Index (12 Nov 2026: USD 1,440 per 40ft) and the Drewry Airfreight Price Index (October 2026: USD 4.12/kg). The full source table is in docs/data_provenance.md.

## 9. Regulatory statements relied on

Each statement below was checked against the listed sources on 2026-11-15 (log: docs/regulatory_check.md); items marked not_verified are handled as labelled placeholders in the numbers.

| ID | Status | Statement | Sources |
|---|---|---|---|
| ID-ABOVE-1500 | not_verified | Consignments declared on a PIBK pay MFN duty and import taxes under the general rules (PMK 96/2023 Art. 29(5) as amended). That consignments above USD 1,500 must use a PIBK, and the MFN rates for the template products, were not verified. | [id_pmk4_2025](https://jdih.kemenkeu.go.id/api/download/b25e56eb-3cdc-4434-ad40-f77a864bb80f/2024pmkeuangan004.pdf) |
| ID-CN-BAND | verified | Between FOB USD 3 and USD 1,500 per recipient per shipment: import duty 7.5%, or 0% for books, 15% for cosmetics, iron/steel articles and watches, 25% for bags (42.02), textiles (chapters 61-63), footwear (chapter 64) and bicycles/e-bikes; anti-dumping and safeguard duties do not apply; VAT is collected; income tax is exempt except 5% for the 15%/25% commodities. | [id_pmk4_2025](https://jdih.kemenkeu.go.id/api/download/b25e56eb-3cdc-4434-ad40-f77a864bb80f/2024pmkeuangan004.pdf) |
| ID-CN-DEMINIMIS | verified | Consignments declared on a consignment note with a customs value up to FOB USD 3 per recipient per shipment are free of import duty and income tax but pay VAT (PMK 96/2023 Art. 29(2) as amended by PMK 4/2025). | [id_pmk96_2023](https://jdih.kemenkeu.go.id/api/download/4d5d2359-2490-4a4b-a4fe-a49d81a22a64/2023pmkeuangan096.pdf), [id_pmk4_2025](https://jdih.kemenkeu.go.id/api/download/b25e56eb-3cdc-4434-ad40-f77a864bb80f/2024pmkeuangan004.pdf) |
| ID-IMPORT-VALUE | not_verified | The kit takes Indonesia's VAT import value as customs value (CIF) plus import duty. The statutory definition was not retrieved, so this base is an assumption. | — |
| ID-LICENSING | not_verified | Bulk (non-consignment) imports of textiles, footwear, bags and electronics may need trade-ministry import approvals or technical requirements; these were not verified. | — |
| ID-VAT-EFFECTIVE | verified | From 1 January 2025, VAT on imports of non-luxury taxable goods is 12% of a base equal to 11/12 of the import value (an effective 11%). | [id_pmk131_2024](https://jdih.kemenkeu.go.id/api/download/ad276b82-94bd-4197-b409-af33e2842cd6/2024pmkeuangan131.pdf) |
| INCO-RULES | verified | Incoterms 2020 has 11 rules: seven for any mode of transport and four (FAS, FOB, CFR, CIF) for sea and inland waterway transport. | [trade_gov_incoterms](https://www.trade.gov/know-your-incoterms) |
| MY-DEMINIMIS | verified | Consignments by air courier or post through listed airports with a CIF value not exceeding RM500 are exempt from import duty and sales tax on imports (de minimis); the facility does not apply to goods imported by road or sea. | [my_lvg_guide](https://mylvg.customs.gov.my/uploads/Guide%20Sales%20Tax%20on%20LVG%20Guide%20as%20of%201%C2%A0August%C2%A02024.pdf) |
| MY-LVG | verified | Sales tax of 10% applies to low-value goods sold at a price not exceeding RM500 and brought into Malaysia by land, sea or air (tobacco, liquor and e-cigarette products excluded), imposed from 1 January 2024; sellers register once LVG sales exceed RM500,000 in 12 months. | [my_lvg_guide](https://mylvg.customs.gov.my/uploads/Guide%20Sales%20Tax%20on%20LVG%20Guide%20as%20of%201%C2%A0August%C2%A02024.pdf) |
| MY-LVG-NO-DOUBLE | verified | LVG already taxed at the point of sale are not charged sales tax on imports if the LVG registration number is in the import declaration. | [my_lvg_guide](https://mylvg.customs.gov.my/uploads/Guide%20Sales%20Tax%20on%20LVG%20Guide%20as%20of%201%C2%A0August%C2%A02024.pdf) |
| MY-ST-IMPORT-BASE | verified | Sales tax on imported taxable goods is charged on the customs value plus customs duty plus excise duty (Sales Tax Act 2018, s.9(2)). | [my_sales_tax_act](https://mysst.customs.gov.my/wp-content/uploads/2025/03/Sales-Tax-Act-2018.pdf) |
| MY-TARIFF-LINES | verified | Malaysian MFN, SST-column, ACFTA and RCEP rates are those shown by the customs HS Explorer (PDK 2025 schedule) on the access date; parent headings were cross-checked against the 2022 order's hierarchy for the same codes. | [my_jkdm_ezhs](https://ezhs.customs.gov.my/), [my_pdk_2022](https://www.miti.gov.my/miti/resources/Approve%20Permit/P.U_._(A)_114_-_Perintah_Duti_Kastam_2022_.pdf) |
| MY-VALUATION-CIF | verified | Malaysian customs value adds the cost of transport and insurance to the arrival of the goods in Malaysia (CIF basis), under the Customs (Rules of Valuation) Regulations 1999. | [my_jkdm_valuation](https://www.customs.gov.my/en/procedure/technical-services) |
| PH-CAO | not_verified | The Bureau of Customs' current administrative order on de minimis and low-value importations could not be read (the site refused scripted requests); thresholds other than s.423 were not verified. | — |
| PH-DEMINIMIS | verified | No duties and taxes are collected on goods with an FOB or FCA value of PHP 10,000 or below (CMTA s.423); the Secretary of Finance is to adjust the value every three years using the CPI, and de minimis tobacco and alcohol remain subject to excise. Whether an adjustment has been made was not verified. | [ph_cmta](https://lawphil.net/statutes/repacts/ra2016/ra_10863_2016.html), [ph_dof_deminimis](https://www.dof.gov.ph/boc-bares-new-rules-on-small-value-tobacco-alcohol-imports/) |
| PH-MFN | not_verified | Philippine MFN duty rates for the template products were not verified; the kit uses labelled placeholder rates. | — |
| PH-VAT | verified | Philippine VAT on importation is 12% of the customs value plus customs duties, excise taxes and other charges, paid before release. | [ph_bir_2550q](https://bir-cdn.bir.gov.ph/BIR/pdf/2550Q%20guidelines%20April%202024_final.pdf) |
| SVC-CLR-TH | verified | Cross-border rail freight runs between China, Laos and Thailand on the China-Laos Railway, with containers transferred at Vientiane South / Thanaleng to the metre-gauge line to Thailand. Departure frequency for a given origin was not verified. | [rail_kpl_2026](https://kpl.gov.la/detail.aspx?id=97814), [rail_star_2026](https://www.thestar.com.my/aseanplus/aseanplus-news/2026/11/07/thailand-steps-up-rail-links-with-laos-and-china-to-boost-regional-trade) |
| TH-DUTY-1BAHT | verified | From 1 January 2026, Customs Notification 219/2568 limits the duty exemption under category 12 of Part 4 of the Customs Tariff Decree to goods each priced (customs value) at no more than 1 baht, revoking Notification 191/2561. | [th_customs_219_2568](https://ccc.customs.go.th/data_files/bda1fd37fafedcc1055daafac2e3c48f.pdf) |
| TH-MFN | not_verified | Thai MFN duty rates for the template products were not verified; the kit uses labelled placeholder rates. | — |
| TH-VAT | verified | Thai import VAT is levied on CIF value plus import duty, excise tax and other taxes and fees; the general rate is currently 7%. | [th_rd_vat](https://www.rd.go.th/english/6043.html) |

