"""Hand-worked checks of the multi-leg cost build-up (numbers typed from the RFQ and rates.yaml)."""
from __future__ import annotations

import math

import pytest

from cbsk import compliance
from cbsk.flows import b2b, temporary
from tests.conftest import make_ctx, node, option

PROFILE = [0.70, 0.80, 1.00, 1.05, 1.10, 1.10, 1.10, 1.05, 1.05, 1.05, 1.00, 1.00]


def test_a1_fcl_container_count_by_hand(runs):
    res, _ = runs["automotive_ckd_cn_my"]
    o = option(res, "A1-ocean_fcl")
    cap = 76.0 * 0.85
    by_month = []
    for m in PROFILE:
        kits = 6000 * m / 12 / 4
        by_month.append(max(math.ceil(kits * 2.6 / cap), math.ceil(kits * 520 / 26000)))
    assert by_month == [4, 5, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6]
    assert o["quantities"]["feu_per_year"] == 4 * sum(by_month) == 276


def test_a1_fcl_lines_by_hand(runs):
    res, _ = runs["automotive_ckd_cn_my"]
    o = option(res, "A1-ocean_fcl")
    feu, ship = 276, 48
    assert node(o, "PICKUP") == pytest.approx(feu * (150 + 2.2 * 40))
    assert node(o, "THC_O") == pytest.approx(feu * 140)
    assert node(o, "MAIN") == pytest.approx(feu * 1500)
    assert node(o, "THC_D") == pytest.approx(feu * 170)
    assert node(o, "DELIVERY") == pytest.approx(feu * (150 + 2.2 * 35))
    assert node(o, "IMPORT_DECL") == pytest.approx(ship * 70)
    assert node(o, "EXPORT_DECL") == pytest.approx(ship * 45)
    goods = 6000 * (2100 + 650 + 380 + 290)
    to_border = feu * (150 + 2.2 * 40) + feu * 140 + feu * 1500
    insurance = max(ship * 25, 0.0012 * 1.10 * (goods + to_border))
    assert node(o, "INSURANCE") == pytest.approx(insurance)
    quote = (to_border + feu * 170 + ship * 70 + feu * (150 + 2.2 * 35) + feu * 60 + insurance + 6000 * 9.0 + ship * 40)
    assert o["totals"]["quote"] == pytest.approx(quote)
    # FCA: the seller clears for export, so export declarations sit outside the buyer's quotation
    assert o["totals"]["seller_side"] == pytest.approx(ship * 45)
    # harness line misses origin (RVC 38%): MFN 30% on a CIF customs value, freight allocated by value
    harn = 6000 * 380
    cv = harn + harn / goods * (to_border + insurance)
    assert node(o, "CV_HARN") == pytest.approx(cv)
    assert node(o, "DUTY_HARN") == pytest.approx(0.30 * cv)
    assert node(o, "DUTY_BODY") == pytest.approx(0.0)          # ACFTA 0%
    assert node(o, "SALES_TAX_HARN") == pytest.approx(0.0)     # Schedule C exemption applied


def test_a1_lcl_and_air_quantities_by_hand(runs):
    res, _ = runs["automotive_ckd_cn_my"]
    # W/M per shipment = max(cbm, tonnes, 1) = 2.6 per kit; all shipments together carry 6,000 kits
    assert option(res, "A1-ocean_lcl")["quantities"]["wm_per_year"] == pytest.approx(2.6 * 6000)
    # chargeable kg = max(gross 520, volumetric 2.6 x 167 = 434.2) per kit
    assert option(res, "A1-air")["quantities"]["chargeable_kg_per_year"] == pytest.approx(520 * 6000)


def test_air_volumetric_weight_governs_light_bulky_kits(ref, rfqs, clone):
    rfq = clone(rfqs["automotive_ckd_cn_my"])
    lane = rfq["lanes"][0]
    lane["unit_cbm"] = 5.0          # volumetric 5 x 167 = 835 kg > gross 520 kg
    lane["modes"] = ["air"]
    ctx = make_ctx(ref, rfq)
    rows = b2b._fta_rows(ctx, lane, "auto")
    out = b2b.build_lane(ctx, lane, rfq, b2b.lane_flags(ctx, lane, rfq, rows), rows)
    assert out["options"][0]["quantities"]["chargeable_kg_per_year"] == pytest.approx(5.0 * 167 * 6000)


def test_sales_tax_without_schedule_c_by_hand(ref, rfqs, clone):
    rfq = clone(rfqs["automotive_ckd_cn_my"])
    rfq["service"]["registered_manufacturer_schedule_c"] = False
    lane = rfq["lanes"][0]
    lane["modes"] = ["ocean_fcl"]
    ctx = make_ctx(ref, rfq)
    rows = b2b._fta_rows(ctx, lane, "auto")
    o = b2b.build_lane(ctx, lane, rfq, b2b.lane_flags(ctx, lane, rfq, rows), rows)["options"][0]
    cv = node(o, "CV_HARN")
    assert node(o, "SALES_TAX_HARN") == pytest.approx(0.10 * (cv + 0.30 * cv))
    assert node(o, "SALES_TAX_BODY") == pytest.approx(0.10 * node(o, "CV_BODY"))   # ACFTA: no duty in the base


def test_tis_security_cost_by_hand(runs):
    res, _ = runs["semiconductor_temp_sg"]
    o = option(res, "B1-air-tis")
    freight_in = max(1800, 9.0 * 167, 45) * 3.20             # KIX-SIN per move
    cif = 850000 + freight_in
    security = 0.30 * 0.09 * cif                              # GST-registered entity, non-dutiable goods
    months = max(21 / 30.4, 3)
    assert node(o, "TIS_SECURITY_COST") == pytest.approx(security * 0.015 * months / 12)
    assert node(o, "TIS_PERMITS") == pytest.approx(2 * (10 + 80))


def test_repair_loop_gst_on_new_parts_by_hand(runs):
    res, _ = runs["semiconductor_temp_sg"]
    o = option(res, "B3-air-temp_export_repair")
    assert node(o, "GST_NEW_PARTS") == pytest.approx(10 * 0.09 * 65000 * 0.12 * (1 - 0.5))
    # repair abroad cannot use an ATA Carnet: only the temporary-export option exists
    lane = next(ln for ln in res["lanes"] if ln["id"] == "B3")
    assert [x["regime"] for x in lane["excluded"]] == ["ata_carnet"]


def test_air_parcel_chargeable_weight_and_freight_by_hand(runs):
    res, _ = runs["consumer_ecom_sea"]
    o = option(res, "C1-air_parcel")
    parcels = 9000 * 12
    chg = parcels * (0.5 * max(0.35, 0.0035 * 167) + 0.3 * max(0.30, 0.0020 * 167) + 0.2 * max(0.55, 0.0060 * 167))
    assert o["quantities"]["chargeable_kg_per_year"] == pytest.approx(chg)
    assert node(o, "MAIN") == pytest.approx(chg * 2.40)
    # Malaysian LVG: 10% sales tax on the sale price, no duty under the air-courier de minimis
    lvg = parcels * (0.5 * 24.0 + 0.3 * 39.0 + 0.2 * 29.0) * 0.10
    assert o["totals"]["tax"] == pytest.approx(lvg)
    assert o["totals"]["duty"] == pytest.approx(0.0)


def test_hold_flag_count_uses_only_hold_relevant_flags(ref):
    flags = [compliance.flag("MY-KIT-CLASSIFICATION", "medium", "", ""),
             compliance.flag("MY-SCHEDULE-C", "medium", "", ""),
             compliance.flag("SG-STRATEGIC-SCREEN", "info", "", "")]
    assert compliance.hold_flag_count(ref, flags) == 1


def test_temporary_round_trip_includes_both_directions(ref, rfqs):
    rfq = rfqs["semiconductor_temp_sg"]
    lane = next(ln for ln in rfq["lanes"] if ln["id"] == "B4")
    regimes = compliance.temporary_regimes(ref, lane["purpose"], lane["origin"]["country"], lane["destination"]["country"])
    ctx = make_ctx(ref, rfq)
    out = temporary.build_lane(ctx, lane, rfq, temporary.lane_flags(ctx, lane, regimes), regimes)
    road = next(o for o in out["options"] if o["mode"] == "road")
    assert node(road, "OUT_ROAD") == pytest.approx(24 * 650)
    assert node(road, "RET_ROAD") == pytest.approx(24 * 650)
    names = [lg["name"] for lg in road["legs"]]
    assert sum("cross-border truck" in n for n in names) == 4     # handling + driving, each direction
    assert any("repair turnaround" in n for n in names)
