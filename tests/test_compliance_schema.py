"""Compliance rules (temporary admission, HS controls, risk score) and RFQ validation."""
from __future__ import annotations

import pytest

from cbsk import compliance, schema


@pytest.mark.parametrize("purpose,origin,dest,ata,tis", [
    ("exhibition", "JP", "SG", True, True),
    ("professional_equipment", "US", "SG", True, True),
    ("repair_in_sg", "MY", "SG", False, True),
    ("commercial_samples", "JP", "SG", False, False),
])
def test_ata_and_tis_into_singapore(ref, purpose, origin, dest, ata, tis):
    r = compliance.temporary_regimes(ref, purpose, origin, dest)
    assert r["ata_carnet"]["available"] is ata
    assert r["tis"]["available"] is tis


def test_repair_abroad_uses_temporary_export_not_carnet(ref):
    r = compliance.temporary_regimes(ref, "repair_abroad", "SG", "JP")
    assert r["ata_carnet"]["available"] is False
    assert r["temp_export_repair"]["available"] is True
    assert "SG-TEMPEXP-REPAIR" in r["temp_export_repair"]["statements"]


def test_hs_control_flags(ref):
    ids = lambda fl: {f["id"] for f in fl}
    assert "MY-AP-VEHICLE" in ids(compliance.hs_flags(ref, "MY", [{"hs": "8703.23.2100", "flags": set()}], set(), set()))
    assert "MY-AP-STEEL" in ids(compliance.hs_flags(ref, "MY", [{"hs": "7210.49.1100", "flags": set()}], set(), set()))
    parts = [{"hs": "8708.29.9500", "flags": set()}]
    assert "MY-KIT-CLASSIFICATION" in ids(compliance.hs_flags(ref, "MY", parts, {"kit"}, set()))
    assert "MY-KIT-CLASSIFICATION" not in ids(compliance.hs_flags(ref, "MY", parts, set(), set()))
    tool = [{"hs": "9031.41", "flags": {"strategic_screening"}}]
    assert "SG-STRATEGIC-SCREEN" in ids(compliance.hs_flags(ref, "SG", tool, set(), {"sg_export"}))
    assert "SG-STRATEGIC-SCREEN" not in ids(compliance.hs_flags(ref, "SG", tool, set(), set()))
    plain = [{"hs": "9031.41", "flags": set()}]
    assert "SG-STRATEGIC-SCREEN" not in ids(compliance.hs_flags(ref, "SG", plain, set(), {"sg_export"}))


def test_unverified_rules_are_reported_as_not_verified(ref):
    fl = compliance.hs_flags(ref, "MY", [{"hs": "8708.29.9500", "flags": set()}], {"kit"}, set())
    kit = next(f for f in fl if f["id"] == "MY-KIT-CLASSIFICATION")
    assert kit["verified"] is False
    assert compliance.statement_status(ref, ["SG-ATA-SCOPE", "SG-ATA-ISSUER"]) is True
    assert compliance.statement_status(ref, ["SG-ATA-SCOPE", "TH-MFN"]) is False
    assert compliance.statement_status(ref, []) is False


def test_risk_score_by_hand(ref):
    flags = [{"severity": "medium"}, {"severity": "low"}]
    r = compliance.risk_score(ref, flags, p50=10.0, p90=15.0, handoffs=3, unverified_service=False)
    assert r["score"] == pytest.approx(10 + 4 + 1.0 * 5 + 2 * 3)
    capped = compliance.risk_score(ref, [{"severity": "block"}], 1.0, 2.0, 0, False)
    assert capped["score"] == 100.0


def test_singapore_carnet_scope_in_template(runs):
    res, _ = runs["semiconductor_temp_sg"]
    b4 = next(ln for ln in res["lanes"] if ln["id"] == "B4")
    assert all(o["regime"] == "tis" for o in b4["options"])
    assert b4["extra"]["regimes"]["ata_carnet"]["available"] is False


def test_rail_without_verified_schedule_is_excluded(runs):
    res, _ = runs["automotive_ckd_cn_my"]
    a2 = next(ln for ln in res["lanes"] if ln["id"] == "A2")
    assert [x["mode"] for x in a2["excluded"]] == ["rail"]
    assert "SVC-ASEAN-EXPRESS" in a2["excluded"][0]["statements"]
    c3 = next(ln for ln in runs["consumer_ecom_sea"][0]["lanes"] if ln["id"] == "C3")
    assert any(o["mode"] == "rail" for o in c3["options"])      # China-Laos-Thailand corridor is verified


def test_sea_air_only_when_hub_is_on_the_way(runs):
    res, _ = runs["consumer_ecom_sea"]
    lanes = {ln["id"]: ln for ln in res["lanes"]}
    assert any(o["mode"] == "sea_air" for o in lanes["C2"]["options"])          # Shenzhen-Singapore-Jakarta
    assert [x["mode"] for x in lanes["C4"]["excluded"]] == ["sea_air"]           # Manila: 4.2x detour


# ------------------------------------------------------------------------------------------- schema
def test_templates_validate(rfqs):
    for rfq in rfqs.values():
        assert schema.validate(rfq) == []


@pytest.mark.parametrize("mutate,needle", [
    (lambda r: r.update(customer="Customer A"), "fictional"),
    (lambda r: r["lanes"][0]["monthly_profile"].__setitem__(0, 1.7), "sum to 12"),
    (lambda r: r.update(incoterm=None), "owner"),
    (lambda r: r["lanes"][0]["modes"].append("hyperloop"), "not allowed"),
    (lambda r: r.update(priorities={"cost": 0.5, "time": 0.5, "risk": 0.5}), "sum to 1"),
    (lambda r: r["lanes"][0]["lines"][0].update(hs="8708.29"), "hs must look like"),
    (lambda r: r["lanes"][0].update(shipments_per_month=0), "positive integer"),
    (lambda r: r["lanes"][0]["origin"].update(country="XX"), "not supported"),
    (lambda r: r.update(incoterm="FOBX"), "not an Incoterms"),
])
def test_invalid_b2b_rfq_rejected(rfqs, clone, mutate, needle):
    rfq = clone(rfqs["automotive_ckd_cn_my"])
    mutate(rfq)
    errors = schema.validate(rfq)
    assert any(needle in e for e in errors), errors


def test_invalid_parcel_and_temporary_rfqs_rejected(rfqs, clone):
    p = clone(rfqs["consumer_ecom_sea"])
    p["basket"][0]["share"] = 0.6
    assert any("shares must sum to 1" in e for e in schema.validate(p))
    t = clone(rfqs["semiconductor_temp_sg"])
    t["lanes"][2]["purpose"] = "sightseeing"
    t["lanes"][3]["regimes"] = ["bonded_magic"]
    errs = schema.validate(t)
    assert any("purpose must be" in e for e in errs) and any("regimes must be" in e for e in errs)
    with pytest.raises(schema.RFQError):
        from cbsk.io import TEMPLATES, load_yaml  # noqa: F401
        bad = clone(rfqs["consumer_ecom_sea"])
        bad["seed"] = "x"
        errs = schema.validate(bad)
        if errs:
            raise schema.RFQError("; ".join(errs))
