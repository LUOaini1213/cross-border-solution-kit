# Mutation report

Run 2026-11-15: **32/32 mutants killed** (32 by the unit tests, 0 only by the golden regression test, 0 survived). 102 tests collected.

Each mutant changes one snippet of core logic in a copy of the repository; the unit tests run first (`pytest -m "not golden" -x`), and the golden comparison with the committed results only if they all pass.

The last column is the first test that failed, in file order. Where it names a test that looks unrelated (`test_singapore_carnet_scope_in_template` for the Indonesian VAT base and the Malaysian LVG base), the failure is the pipeline's own cross-check: `flows/parcel.py` compares the workbook formulas' tax total with `duties.parcel_taxes` and refuses to build when they disagree, which fails the shared pipeline fixture before the hand-worked tests (`test_indonesia_consignment_band_by_hand`, `test_air_parcel_chargeable_weight_and_freight_by_hand`) are reached. Both hand-worked tests were run separately against these two mutants (with the cross-check disabled for the second) and fail as well.

| # | File | Mutation | Killed by | First failing test |
|---|---|---|---|---|
| 1 | `cbsk/flows/common.py` | container count rounds down instead of up | unit | `tests/test_costing.py::test_a1_fcl_container_count_by_hand` |
| 2 | `cbsk/flows/b2b.py` | LCL freight tonnes use min instead of max(W, M) | unit | `tests/test_costing.py::test_a1_lcl_and_air_quantities_by_hand` |
| 3 | `cbsk/flows/b2b.py` | air chargeable weight ignores volumetric weight | unit | `tests/test_costing.py::test_air_volumetric_weight_governs_light_bulky_kits` |
| 4 | `cbsk/flows/b2b.py` | insured value excludes freight to the border (not CIF) | unit | `tests/test_costing.py::test_a1_fcl_lines_by_hand` |
| 5 | `cbsk/flows/b2b.py` | customs value on FOB instead of CIF | unit | `tests/test_costing.py::test_a1_fcl_lines_by_hand` |
| 6 | `cbsk/flows/b2b.py` | sales tax base omits import duty | unit | `tests/test_costing.py::test_sales_tax_without_schedule_c_by_hand` |
| 7 | `cbsk/flows/b2b.py` | Schedule C exemption ignored | unit | `tests/test_costing.py::test_a1_fcl_lines_by_hand` |
| 8 | `cbsk/flows/b2b.py` | chosen FTA rate not applied (always MFN) | unit | `tests/test_costing.py::test_a1_fcl_lines_by_hand` |
| 9 | `cbsk/duties.py` | my_import_line: sales tax base omits duty | unit | `tests/test_duties.py::test_my_import_line_cif_and_sales_tax_base` |
| 10 | `cbsk/duties.py` | Malaysian LVG limit made exclusive (RM500 itself no longer LVG) | unit | `tests/test_duties.py::test_malaysia_lvg_price_boundary` |
| 11 | `cbsk/duties.py` | Malaysian de minimis wrongly applied to road imports | unit | `tests/test_duties.py::test_malaysia_road_parcel_pays_duty_but_not_import_sales_tax` |
| 12 | `cbsk/duties.py` | Indonesian USD 3 de minimis made exclusive | unit | `tests/test_duties.py::test_indonesia_usd3_boundary` |
| 13 | `cbsk/duties.py` | Indonesian 5% income tax on listed consignments dropped | unit | `tests/test_duties.py::test_indonesia_consignment_band_by_hand` |
| 14 | `cbsk/duties.py` | Indonesian VAT base omits duty | unit | `tests/test_compliance_schema.py::test_singapore_carnet_scope_in_template` |
| 15 | `cbsk/duties.py` | Thailand keeps the pre-2026 THB 1,500 exemption | unit | `tests/test_duties.py::test_thailand_every_parcel_dutiable_since_2026` |
| 16 | `cbsk/duties.py` | Philippine de minimis tested on CIF instead of FOB | unit | `tests/test_duties.py::test_philippines_deminimis_on_fob` |
| 17 | `cbsk/duties.py` | TIS security shares swapped | unit | `tests/test_duties.py::test_singapore_tis_security_and_repair_gst` |
| 18 | `cbsk/duties.py` | tariff choice picks the highest rate | unit | `tests/test_costing.py::test_a1_fcl_lines_by_hand` |
| 19 | `cbsk/duties.py` | RCEP origin granted without RVC40 or CTH evidence | unit | `tests/test_duties.py::test_origin_not_met_leaves_mfn_only` |
| 20 | `data/reference/incoterms_2020.yaml` | FCA export clearance put on the buyer | unit | `tests/test_costing.py::test_a1_fcl_lines_by_hand` |
| 21 | `cbsk/pareto.py` | Pareto dominance without the strict-improvement condition | unit | `tests/test_incoterms_pareto.py::test_dominance_and_front` |
| 22 | `cbsk/pareto.py` | recommendation ignores the on-time target | unit | `tests/test_incoterms_pareto.py::test_recommend_respects_target_and_blocks` |
| 23 | `cbsk/seeds.py` | seed from Python's salted hash() (not reproducible) | unit | `tests/test_transit.py::test_seed_is_independent_of_python_hash_randomisation` |
| 24 | `cbsk/transit.py` | lognormal fit to quartiles without the normal-quantile scaling | unit | `tests/test_transit.py::test_lognormal_quartile_fit_reproduces_quartiles` |
| 25 | `cbsk/transit.py` | arrival on the target day counted as late | unit | `tests/test_transit.py::test_on_time_counts_arrival_on_the_target_day` |
| 26 | `cbsk/legs.py` | every shipment transshipped regardless of LPI data | unit | `tests/test_transit.py::test_transshipment_probability_from_lpi` |
| 27 | `cbsk/compliance.py` | ATA Carnet accepted for repair | unit | `tests/test_compliance_schema.py::test_ata_and_tis_into_singapore[repair_in_sg-MY-SG-False-True]` |
| 28 | `cbsk/compliance.py` | every medium flag raises the hold probability | unit | `tests/test_costing.py::test_hold_flag_count_uses_only_hold_relevant_flags` |
| 29 | `cbsk/compliance.py` | risk score ignores transit spread | unit | `tests/test_compliance_schema.py::test_risk_score_by_hand` |
| 30 | `cbsk/excel.py` | workbook writes products as sums | unit | `tests/test_excel.py::test_formula_totals_equal_python_totals[automotive_ckd_cn_my]` |
| 31 | `cbsk/flows/temporary.py` | GST charged on warranty repairs | unit | `tests/test_costing.py::test_repair_loop_gst_on_new_parts_by_hand` |
| 32 | `cbsk/flows/parcel.py` | LVG sales tax on price plus shipping instead of the sale price | unit | `tests/test_compliance_schema.py::test_singapore_carnet_scope_in_template` |

## Survivors

None.
