"""Hand-worked duty and tax calculations, including the threshold boundaries."""
from __future__ import annotations

import pytest

from cbsk import duties


def test_my_import_line_cif_and_sales_tax_base():
    r = duties.my_import_line(1000.0, 100.0, 0.25, 0.10, schedule_c_exempt=False)
    assert r == pytest.approx({"customs_value": 1100.0, "duty": 275.0, "sales_tax": 137.5})
    r = duties.my_import_line(1000.0, 100.0, 0.25, 0.10, schedule_c_exempt=True)
    assert r["sales_tax"] == 0.0 and r["duty"] == pytest.approx(275.0)


def test_fta_options_and_choice_for_body_panels(ref):
    opts = duties.fta_options_my(ref, "8708.29.9500", "CN", 58, None)
    by = {o["scheme"]: o for o in opts}
    assert by["MFN"]["rate"] == pytest.approx(0.25)
    assert by["ACFTA"]["available"] and by["ACFTA"]["rate"] == pytest.approx(0.0)
    assert by["RCEP"]["available"] and by["RCEP"]["rate"] == pytest.approx(0.227)
    assert duties.choose_tariff(opts)["scheme"] == "ACFTA"
    assert duties.choose_tariff(opts, "RCEP")["scheme"] == "RCEP"
    assert duties.choose_tariff(opts, "none")["scheme"] == "MFN"


def test_origin_not_met_leaves_mfn_only(ref):
    opts = duties.fta_options_my(ref, "8544.30.1200", "CN", 38, False)
    by = {o["scheme"]: o for o in opts}
    assert not by["ACFTA"]["available"]
    assert not by["RCEP"]["available"]            # PSR CTH or RVC40: neither met
    assert duties.choose_tariff(opts)["scheme"] == "MFN"
    # change of heading alone qualifies under RCEP for 85.44
    assert {o["scheme"]: o for o in duties.fta_options_my(ref, "8544.30.1200", "CN", 38, True)}["RCEP"]["available"]


def test_tariff_tie_prefers_mfn(ref):
    opts = duties.fta_options_my(ref, "6109.10.2000", "CN", 80, None)   # 0% MFN, 0% ACFTA
    assert duties.choose_tariff(opts)["scheme"] == "MFN"


def test_malaysia_lvg_air_courier_parcel(ref):
    t = duties.parcel_taxes(ref, "MY", "air_courier", "6109.10.2000", 24.0, 3.5, True)
    assert t.duty == 0.0
    assert t.consumption_tax == pytest.approx(2.40)       # 10% of the sale price, transport excluded
    assert "MY-DEMINIMIS" in t.statements


def test_malaysia_lvg_price_boundary(ref):
    at_limit = 500.0 / 4.20
    assert duties.parcel_taxes(ref, "MY", "air_courier", "6109.10.2000", at_limit, 0.0, True).consumption_tax == \
        pytest.approx(0.10 * at_limit)
    above = duties.parcel_taxes(ref, "MY", "air_courier", "6109.10.2000", 125.0, 0.0, True)
    assert above.regime == "MY general import"            # not LVG, and CIF RM525 is above the de minimis
    assert above.consumption_tax == pytest.approx(0.10 * 125.0)


def test_malaysia_road_parcel_pays_duty_but_not_import_sales_tax(ref):
    t = duties.parcel_taxes(ref, "MY", "road", "8708.29.9500", 50.0, 5.0, True)
    assert t.duty == pytest.approx(0.25 * 55.0)            # no de minimis by road
    assert t.consumption_tax == pytest.approx(5.0)         # LVG tax at sale, none at import


def test_indonesia_consignment_band_by_hand(ref):
    shirt = duties.parcel_taxes(ref, "ID", "air_courier", "6109.10.2000", 24.0, 3.5)
    cif = 27.5
    duty = 0.25 * cif
    assert shirt.duty == pytest.approx(duty)
    assert shirt.consumption_tax == pytest.approx(0.12 * 11 / 12 * (cif + duty))
    assert shirt.income_tax == pytest.approx(0.05 * (cif + duty))
    assert shirt.total == pytest.approx(6.875 + 3.78125 + 1.71875)
    buds = duties.parcel_taxes(ref, "ID", "air_courier", "8518.30.2000", 39.0, 3.5)
    assert buds.duty == pytest.approx(0.075 * 42.5)
    assert buds.income_tax == 0.0


def test_indonesia_usd3_boundary(ref):
    t = duties.parcel_taxes(ref, "ID", "air_courier", "6109.10.2000", 3.0, 0.5)
    assert t.duty == 0.0 and t.income_tax == 0.0
    assert t.consumption_tax == pytest.approx(0.11 * 3.5)
    t2 = duties.parcel_taxes(ref, "ID", "air_courier", "6109.10.2000", 3.01, 0.5)
    assert t2.duty == pytest.approx(0.25 * 3.51)


def test_thailand_every_parcel_dutiable_since_2026(ref):
    t = duties.parcel_taxes(ref, "TH", "air_courier", "6109.10.2000", 24.0, 3.5)
    assert t.duty == pytest.approx(0.30 * 27.5)            # placeholder rate, flagged as not verified
    assert t.consumption_tax == pytest.approx(0.07 * (27.5 + 8.25))
    small = duties.parcel_taxes(ref, "TH", "air_courier", "6109.10.2000", 1.0, 0.23)   # ~40 baht
    assert small.duty > 0
    tiny = duties.parcel_taxes(ref, "TH", "air_courier", "6109.10.2000", 0.02, 0.0)    # 0.65 baht
    assert tiny.duty == 0.0


def test_philippines_deminimis_on_fob(ref):
    at_limit = 10000.0 / 58.0
    t = duties.parcel_taxes(ref, "PH", "air_courier", "8518.30.2000", at_limit, 3.5)
    assert t.total == 0.0                                   # FOB at the limit, shipping not counted
    over = duties.parcel_taxes(ref, "PH", "air_courier", "8518.30.2000", 173.0, 3.5)
    assert over.duty == pytest.approx(0.07 * 176.5)
    assert over.consumption_tax == pytest.approx(0.12 * (176.5 + 0.07 * 176.5))


def test_bulk_import_taxes(ref):
    my = duties.bulk_import_taxes(ref, "MY", "6109.10.2000", 10.0, 24.0)
    assert my.duty == 0.0 and my.consumption_tax == pytest.approx(1.0)
    idn = duties.bulk_import_taxes(ref, "ID", "6109.10.2000", 10.0, 24.0)
    assert idn.duty == pytest.approx(1.0) and idn.consumption_tax == pytest.approx(0.11 * 24.0)


def test_singapore_tis_security_and_repair_gst(ref):
    assert duties.sg_tis_security(ref, 850000.0, True) == pytest.approx(0.30 * 0.09 * 850000)
    assert duties.sg_tis_security(ref, 850000.0, False) == pytest.approx(0.50 * 0.09 * 850000)
    assert duties.sg_repair_reimport_gst(ref, 65000.0, 0.12, 0.5) == pytest.approx(351.0)
    assert duties.sg_repair_reimport_gst(ref, 65000.0, 0.12, 1.0) == 0.0
