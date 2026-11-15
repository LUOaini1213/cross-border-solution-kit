# cross-border-solution-kit

A cross-border logistics **solution-design and quotation kit**: an RFQ goes in, candidate solutions per lane
come out with a multi-leg cost build-up, Monte Carlo transit-time reliability, compliance and customs-risk
checks, a Pareto comparison, a recommendation with written rationale, an Excel quotation with live formulas,
and a bilingual (English / Simplified Chinese) proposal with an implementation plan and a monitoring sheet.
Three fully worked industry templates form a small solution asset library.

> **What this is.** A personal portfolio project (November 2026), built with AI assistance: code, data
> collection and write-up were drafted with an AI coding assistant and checked by running them. Customers are
> fictional ("Customer A"). Freight and handling rates are **ILLUSTRATIVE** round numbers, anchored in scale
> to public indices; they are not any carrier's or forwarder's tariff. Duty and tax rules are taken from
> official sources where marked verified and re-checked in a separate pass; everything else is labelled.
> **Not tax, customs or legal advice.**

README numbers are written by `scripts/build_all.py` from `results/*/results.json` (template
`docs/README.template.md`); a test re-renders this file and compares.

## The three templates

| Template | Flow | Lanes | Options evaluated | Excluded (with reason) |
|---|---|---|---|---|
| `automotive_ckd_cn_my` | KD auto-parts kits China → Malaysia for local assembly (FCA, buyer's quotation) | 2 | {{automotive_ckd_cn_my.options}} | {{automotive_ckd_cn_my.excluded}} |
| `semiconductor_temp_sg` | Equipment and spares moving temporarily into and out of Singapore (owner's goods) | 4 | {{semiconductor_temp_sg.options}} | {{semiconductor_temp_sg.excluded}} |
| `consumer_ecom_sea` | B2C parcels China / Singapore → Malaysia, Indonesia, Thailand, Philippines (DDP) | 6 | {{consumer_ecom_sea.options}} | {{consumer_ecom_sea.excluded}} |

Each template lives in `templates/<name>/rfq.yaml`; its outputs are in `results/<name>/`:
`results.json`, `quotation.xlsx` (Summary, Costs with live formulas, Assumptions, Options, Compliance,
Monitoring), `proposal_en.md`, `proposal_zh.md`, `proposal.pdf` (both languages) and `monitoring_template.csv`.

### Recommended solutions

Landed cost = quotation (logistics, VAS, insurance, permits) + duties and taxes + inventory carrying cost.
P90 and on-time probability come from {{automotive_ckd_cn_my.draws}} seeded Monte Carlo draws per option.

| Lane | Recommended | Landed cost / unit (USD) | P90 days | On time vs target | Risk | Status |
|---|---|---|---|---|---|---|
| A1 Ningbo → Shah Alam, kits | {{automotive_ckd_cn_my.A1.option}} | {{automotive_ckd_cn_my.A1.cost}} / kit | {{automotive_ckd_cn_my.A1.p90}} | {{automotive_ckd_cn_my.A1.ontime}} (38 d) | {{automotive_ckd_cn_my.A1.risk}} | {{automotive_ckd_cn_my.A1.status}} |
| A2 Chongqing → Shah Alam, powertrain | {{automotive_ckd_cn_my.A2.option}} | {{automotive_ckd_cn_my.A2.cost}} / kit | {{automotive_ckd_cn_my.A2.p90}} | {{automotive_ckd_cn_my.A2.ontime}} (38 d) | {{automotive_ckd_cn_my.A2.risk}} | {{automotive_ckd_cn_my.A2.status}} |
| B1 Osaka ⇄ Singapore exhibition tool | {{semiconductor_temp_sg.B1.option}} | {{semiconductor_temp_sg.B1.cost}} / move | {{semiconductor_temp_sg.B1.p90}} | {{semiconductor_temp_sg.B1.ontime}} (12 d) | {{semiconductor_temp_sg.B1.risk}} | {{semiconductor_temp_sg.B1.status}} |
| B2 San Jose ⇄ Singapore metrology kit | {{semiconductor_temp_sg.B2.option}} | {{semiconductor_temp_sg.B2.cost}} / move | {{semiconductor_temp_sg.B2.p90}} | {{semiconductor_temp_sg.B2.ontime}} (7 d) | {{semiconductor_temp_sg.B2.risk}} | {{semiconductor_temp_sg.B2.status}} |
| B3 Singapore ⇄ Osaka repair loop | {{semiconductor_temp_sg.B3.option}} | {{semiconductor_temp_sg.B3.cost}} / move | {{semiconductor_temp_sg.B3.p90}} | {{semiconductor_temp_sg.B3.ontime}} (35 d) | {{semiconductor_temp_sg.B3.risk}} | {{semiconductor_temp_sg.B3.status}} |
| B4 Penang ⇄ Singapore repair loop | {{semiconductor_temp_sg.B4.option}} | {{semiconductor_temp_sg.B4.cost}} / move | {{semiconductor_temp_sg.B4.p90}} | {{semiconductor_temp_sg.B4.ontime}} (30 d) | {{semiconductor_temp_sg.B4.risk}} | {{semiconductor_temp_sg.B4.status}} |
| C1 Shenzhen → Malaysia | {{consumer_ecom_sea.C1.option}} | {{consumer_ecom_sea.C1.cost}} / parcel | {{consumer_ecom_sea.C1.p90}} | {{consumer_ecom_sea.C1.ontime}} (7 d) | {{consumer_ecom_sea.C1.risk}} | {{consumer_ecom_sea.C1.status}} |
| C2 Shenzhen → Indonesia | {{consumer_ecom_sea.C2.option}} | {{consumer_ecom_sea.C2.cost}} / parcel | {{consumer_ecom_sea.C2.p90}} | {{consumer_ecom_sea.C2.ontime}} (7 d) | {{consumer_ecom_sea.C2.risk}} | {{consumer_ecom_sea.C2.status}} |
| C3 Shenzhen → Thailand | {{consumer_ecom_sea.C3.option}} | {{consumer_ecom_sea.C3.cost}} / parcel | {{consumer_ecom_sea.C3.p90}} | {{consumer_ecom_sea.C3.ontime}} (7 d) | {{consumer_ecom_sea.C3.risk}} | {{consumer_ecom_sea.C3.status}} |
| C4 Shenzhen → Philippines | {{consumer_ecom_sea.C4.option}} | {{consumer_ecom_sea.C4.cost}} / parcel | {{consumer_ecom_sea.C4.p90}} | {{consumer_ecom_sea.C4.ontime}} (7 d) | {{consumer_ecom_sea.C4.risk}} | {{consumer_ecom_sea.C4.status}} |
| C5 Singapore → Malaysia | {{consumer_ecom_sea.C5.option}} | {{consumer_ecom_sea.C5.cost}} / parcel | {{consumer_ecom_sea.C5.p90}} | {{consumer_ecom_sea.C5.ontime}} (5 d) | {{consumer_ecom_sea.C5.risk}} | {{consumer_ecom_sea.C5.status}} |
| C6 Singapore → Indonesia | {{consumer_ecom_sea.C6.option}} | {{consumer_ecom_sea.C6.cost}} / parcel | {{consumer_ecom_sea.C6.p90}} | {{consumer_ecom_sea.C6.ontime}} (5 d) | {{consumer_ecom_sea.C6.risk}} | {{consumer_ecom_sea.C6.status}} |

"Below target" is reported, not hidden: B2 misses 95%-within-7-days because of the customs-hold tail
(strategic-goods screening); the proposal shows that an 8-day plan meets it. C5 misses 90%-within-5-days.

### What the compliance checks found

* **Automotive (Malaysia).** Duty rates come from the Malaysian customs HS Explorer (PDK 2025 schedule) with
  ACFTA and RCEP columns. On goods value, ACFTA cuts annual duty from USD {{auto.duty_mfn}} (MFN) to
  USD {{auto.duty_chosen}}; RCEP rates for these lines are higher than ACFTA. The wiring-harness line misses
  the 40% regional-value rule and the RFQ records no change of tariff heading, so USD {{auto.duty_at_stake}}
  a year depends on the supplier documenting more regional content. Sales tax on
  components is set to nil under Schedule C (registered manufacturer), flagged as unverified eligibility.
  Kits declared as parts need no MITI Approved Permit, but a set amounting to a complete vehicle could be
  classified as a CKD vehicle (AP required): a classification ruling is the first milestone. The A2 lane is
  invoiced by a Singapore entity: Form E Box 10 / RCEP Box 17 third-party invoicing rules are applied.
* **Semiconductor (Singapore).** Singapore Customs accepts foreign ATA Carnets only for exhibitions,
  professional equipment and scientific equipment, so repair loops use the Temporary Import Scheme (TIS) or a
  temporary export for repair (GST on new parts unless warranty). TIS security is 30% of the potential GST
  (GST-registered entity). Semiconductor equipment and specially designed parts may fall under control-list
  category 3B001 of the Strategic Goods (Control) Order 2026, so each export or re-export needs an XO/XP
  permit at least five working days ahead, carnet or not.
* **Consumer goods (SEA parcels).** Malaysia: 10% LVG sales tax on the sale price for goods up to RM500, with
  air-courier de minimis on duty and import sales tax. Indonesia: from FOB USD 3, 7.5% duty, or 25% plus 5%
  income tax for apparel and bags, plus VAT at an effective 11%. Thailand: since 1 January 2026 only items worth
  up to 1 baht are duty-free. Philippines: no duties or taxes up to PHP 10,000 FOB. Singapore's OVR regime for
  low-value goods (since 1 January 2023) is documented for comparison. The China-Laos-Thailand rail corridor is
  offered (verified on an official Lao source); the Malaysia-China block train is not, because no current
  timetable was found.

## Regulatory check

{{reg.total}} regulatory or tax statements are kept in `data/reference/regulatory_statements.yaml`:
{{reg.verified}} verified on official sources, {{reg.corrected}} corrected (the brief assumed otherwise), and
{{reg.not_verified}} not verified (handled as labelled placeholders or caveats). Every statement was re-checked
in a separate pass; see `docs/regulatory_check.md`. Corrections worth knowing:

* Singapore's ATA Carnet issuer is the **Singapore International Chamber of Commerce (SICC)**, per Singapore
  Customs, the ICC directory and SICC.
* Commercial samples are **not** an accepted purpose for foreign carnets entering Singapore.
* Thailand's THB 1,500 duty exemption ended on 1 January 2026 (Customs Notification 219/2568).

## Data provenance

Every input the models read is labelled (full table: `docs/data_provenance.md`):
REAL {{prov.REAL}}, ASSUMPTION {{prov.ASSUMPTION}}, ILLUSTRATIVE {{prov.ILLUSTRATIVE}}, SYNTHETIC {{prov.SYNTHETIC}}
(distinct parameter ids across the three templates).

* **REAL**: World Bank LPI 2.0 container and air-cargo dwell times (2024; CC BY 4.0), airport coordinates
  (OurAirports, public domain), sea distances computed with `searoute`, Malaysian tariff lines (customs HS
  Explorer), and official regulatory parameters; index anchors (Drewry World Container Index and Intra-Asia
  Container Index of 12 Nov 2026, Drewry Airfreight Price Index for October 2026, Freightos FBX page value).
* **ASSUMPTION**: distribution shapes, speeds, handling times, hold probabilities, FX reference rates, risk
  weights, and placeholders for unverified tax rates (Thai and Philippine MFN rates, Indonesian bulk MFN).
* **ILLUSTRATIVE**: freight, handling, brokerage, VAS and fee rates.
* **SYNTHETIC**: the RFQs (customers, volumes, values, weights).

## How it works

```
templates/*/rfq.yaml ──► schema.py (validation)
data/reference/*.yaml ─► reference.py (every parameter recorded with its provenance label)
                          │
flows/{b2b,temporary,parcel}.py: candidate options per lane, cost graph per option (calc.py),
                          │       transit legs (legs.py: LPI dwell, distances, assumptions)
duties.py (MY sales tax, LVG, ID/TH/PH parcel rules, FTA rates) · compliance.py (HS controls, FTA origin,
ATA/TIS, third-country invoicing, hold risk) · incoterms.py (payer matrix and consistency)
                          │
transit.py (seeded Monte Carlo) ─► pareto.py (front + recommendation rule) ─► narrative.py (rationale EN/ZH)
                          │
excel.py (live-formula workbook) · proposal.py (EN/ZH Markdown) · pdf.py (pandoc + Chromium) · docs.py
```

* **Options**: air, ocean FCL/LCL, rail-sea, sea-air via Singapore (only when the hub is broadly on the way),
  road or rail only where a service is registered as verified in `data/reference/compliance.yaml`.
* **Cost build-up**: pickup, origin handling, export clearance, linehaul, transshipment/hub, destination handling,
  import clearance, last mile, VAS, insurance, temporary-admission instruments, duties and taxes, inventory
  carrying. Each element is assigned to buyer or seller with the Incoterms 2020 matrix; seller-side items are
  excluded from the buyer's quotation and reported separately.
* **Transit**: sum of independent legs; container and airport dwell from LPI 2.0 (lognormal through the published
  quartiles or median and mean), transshipment from LPI, sailing time from searoute distance at 16 knots, flights
  from great-circle distance, labelled assumptions elsewhere.
* **Recommendation**: options that meet the on-time target and carry no blocking flag; among those on the Pareto
  front (cost per unit, P90 days, risk score), the lowest weighted score using the RFQ's priorities.
* **Workbook**: every cost line is a live formula over the Assumptions sheet; a test recomputes the workbook with
  an independent formula evaluator and compares every total with the Python totals.

## Reproduce

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt     # Windows; .venv/bin/python elsewhere
.venv/Scripts/python scripts/build_all.py                   # offline: all results, workbooks, proposals, docs
.venv/Scripts/python -m pytest                              # offline, fast
.venv/Scripts/python scripts/mutation_test.py               # optional, writes docs/mutation_report.*
```

PDFs need pandoc (tested 3.8) and Playwright Chromium (`requirements-pdf.txt`); without them the build skips
the PDF and says so. Network fetch scripts are separate and only refresh `data/public/`:
`scripts/fetch_lpi.py`, `scripts/fetch_geo.py` (needs `requirements-fetch.txt`), `scripts/fetch_my_tariff.py`;
`scripts/check_regulatory_sources.py` repeats the regulatory re-check.

## Tests and mutation testing

`pytest` ({{mut.tests}} tests at the last mutation run) covers hand-worked cost arithmetic, duty and tax
calculations (including threshold boundaries), the Incoterms payer matrix, Pareto correctness, Monte Carlo
determinism and moments, schema validation, compliance rules, workbook formulas vs Python totals, provenance
completeness, line endings, README rendering, and a golden test that re-runs the pipeline and compares with the
committed results. `scripts/mutation_test.py` applies deliberate bugs to the core logic: **{{mut.killed}}/{{mut.total}}
mutants killed** ({{mut.unit_killed}} by the unit tests alone, before the golden comparison); details in
`docs/mutation_report.md`.

## Limitations

* Rates are illustrative; a real quotation needs tendered rates, surcharges and validity dates.
* Transit legs are independent; congestion that slows several legs at once is not modelled. LPI air-cargo dwell is
  used as a proxy for parcel clearance, which may be faster for pre-alerted e-commerce consignments.
* Duty modelling covers the HS lines in the templates only. Thai and Philippine MFN rates, Indonesian bulk rates,
  destination-side repair regimes, origin-country export controls and several eligibility conditions are not
  verified and are marked as such. Classification of the kits is assumed, not ruled.
* The risk score is a transparent heuristic (weights in `data/reference/compliance.yaml`), not a calibrated model.
* B2C tax comparisons count consumption taxes borne by consumers in both routes; income-tax and transfer-pricing
  effects of a local importer are out of scope.

## Related project

`global-logistics-ops` (the author's earlier portfolio project) covers warehouse slotting, ocean-vs-air inventory
policy, an Incoterms landed-cost engine and an overseas-rollout simulation with LPI dwell times. This kit is
self-contained and reuses only ideas (LPI-based dwell modelling, an Incoterms payer matrix), not code or data files.

## Data licences

World Bank LPI 2.0 data: CC BY 4.0 (The World Bank, Logistics Performance Indicators, accessed 2026-11-15).
OurAirports: public domain. `searoute` (Apache-2.0; network from Eurostat SeaRoute, EUPL-1.2). Malaysian tariff
lines were read from the public JKDM HS Explorer, which disclaims liability for use of its information. Index
values are quoted from public pages for scale only. Code: MIT (see `LICENSE`).

## 中文摘要

跨境物流方案设计与报价工具（个人作品集项目，2026 年 11 月，借助 AI 辅助完成）。输入询价（RFQ），按线路生成空运、海运整箱/拼箱、
铁海联运、经新加坡海空联运及经核实的公路/铁路方案，逐段测算费用（提货、起运港操作、出口报关、干线、中转、目的港操作、进口清关、
尾程、增值服务、保险、临时进出境工具、关税税费、库存资金占用），用世界银行 LPI 2.0 港口与机场滞留数据做 2 万次带种子的蒙特卡洛
时效模拟（P50/P90、准时率），并完成合规与风险检查（按 HS 编码的许可管制、ACFTA/RCEP 原产地方案、ATA 单证册适用性、第三方开票、
查验风险）。在成本、P90 时效与风险三维帕累托前沿上给出推荐方案及中英文理由，输出含实时公式的 Excel 报价单与中英文方案书
（含实施计划、RACI、KPI 与上线后监控表）。三个行业模板：中国至马来西亚汽车散件、半导体设备进出新加坡的临时运输、
中国/新加坡至东南亚四国的跨境电商包裹。运价为示意值；法规表述均对照官方来源核查并单独复核，未能核实者明确标注“未核实”。
不构成税务或法律意见。
