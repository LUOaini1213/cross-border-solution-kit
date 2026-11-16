"""Incoterms responsibility consistency and Pareto / recommendation correctness."""
from __future__ import annotations

import pytest

from cbsk import incoterms, pareto

# hand-typed from the ICC / ITA summaries (S = seller pays, B = buyer pays)
EXPECTED = {
    "EXW": {"loading_at_origin": "B", "export_clearance": "B", "main_carriage": "B", "import_clearance": "B"},
    "FCA": {"loading_at_origin": "S", "pre_carriage": "B", "export_clearance": "S", "main_carriage": "B", "insurance": "B"},
    "FOB": {"pre_carriage": "S", "origin_terminal_handling": "S", "main_carriage": "B"},
    "CFR": {"main_carriage": "S", "insurance": "B", "destination_terminal_handling": "B"},
    "CIF": {"main_carriage": "S", "insurance": "S", "on_carriage": "B"},
    "CPT": {"main_carriage": "S", "insurance": "B"},
    "CIP": {"main_carriage": "S", "insurance": "S"},
    "DAP": {"on_carriage": "S", "unloading_at_destination": "B", "import_clearance": "B", "duties_taxes": "B"},
    "DPU": {"unloading_at_destination": "S", "import_clearance": "B"},
    "DDP": {"import_clearance": "S", "duties_taxes": "S", "unloading_at_destination": "B"},
}


def test_matrix_complete(ref):
    elements = ref.incoterms["elements"]
    assert set(ref.incoterms["payer"]) == set(incoterms.RULES)
    for rule in incoterms.RULES:
        assert set(ref.incoterms["payer"][rule]) == set(elements)
    assert ref.incoterms["sea_only"] == ["FAS", "FOB", "CFR", "CIF"]


@pytest.mark.parametrize("rule", sorted(EXPECTED))
def test_payer_cells(ref, rule):
    for element, code in EXPECTED[rule].items():
        assert incoterms.payer(ref, rule, element, "buyer") == {"S": "seller", "B": "buyer"}[code], (rule, element)


def test_in_quote_follows_quoting_party(ref):
    assert not incoterms.in_quote(ref, "FCA", "export_clearance", "buyer")
    assert incoterms.in_quote(ref, "FCA", "main_carriage", "buyer")
    assert incoterms.in_quote(ref, "DDP", "duties_taxes", "seller")
    assert incoterms.in_quote(ref, None, "main_carriage", "owner")


def test_consistency_checks(ref):
    ids = lambda fl: {f["id"] for f in fl}
    assert "INCO-SEA-ONLY" in ids(incoterms.check(ref, "FOB", "buyer", ["air"]))
    assert "INCO-SEA-ONLY" not in ids(incoterms.check(ref, "FOB", "buyer", ["ocean_fcl"]))
    assert "INCO-SELLER-CARRIAGE" in ids(incoterms.check(ref, "CIF", "buyer", ["ocean_fcl"]))
    assert "INCO-DDP-IOR" in ids(incoterms.check(ref, "DDP", "seller", ["air_parcel"]))
    assert "INCO-FCA-EXPORT" in ids(incoterms.check(ref, "FCA", "buyer", ["ocean_fcl"]))
    assert incoterms.check(ref, None, "owner", ["air"]) == []
    assert "INCO-NO-RULE" in ids(incoterms.check(ref, None, "buyer", ["air"]))


def test_template_quotes_respect_incoterm(runs):
    res, _ = runs["automotive_ckd_cn_my"]
    for lane in res["lanes"]:
        for o in lane["options"]:
            for c in o["costs"]:
                if c["element"] == "export_clearance":
                    assert c["payer"] == "seller" and not c["in_quote"]
                if c["element"] in ("main_carriage", "pre_carriage", "import_clearance") and c["kind"] == "calc":
                    assert c["payer"] == "buyer"


def test_dominance_and_front():
    pts = [(1, 5, 5), (2, 2, 2), (3, 3, 3), (1, 5, 5), (2, 2, 3)]
    assert pareto.dominates((2, 2, 2), (3, 3, 3))
    assert not pareto.dominates((1, 5, 5), (1, 5, 5))      # equal points do not dominate each other
    assert pareto.pareto_front(pts) == [0, 1, 3]
    assert pareto.dominated_by(pts, 2) == [1, 4]


def _opt(oid, cost, p90, risk, ontime, block=False):
    return {"id": oid, "metrics": {"cost_per_unit": cost, "p90": p90, "risk": risk, "on_time_probability": ontime},
            "flags": [{"severity": "block"}] if block else []}


def test_recommend_respects_target_and_blocks():
    opts = [_opt("cheap-late", 1.0, 30, 10, 0.5), _opt("ok", 2.0, 10, 20, 0.95), _opt("fast", 5.0, 3, 20, 1.0),
            _opt("blocked", 0.5, 2, 0, 1.0, block=True)]
    rec = pareto.recommend(opts, {"cost": 0.5, "time": 0.3, "risk": 0.2}, 0.9)
    assert rec["status"] == "meets_target"
    assert rec["chosen"] == "ok"
    assert set(rec["feasible"]) == {"ok", "fast"}
    rec2 = pareto.recommend(opts, {"cost": 0.0, "time": 1.0, "risk": 0.0}, 0.9)
    assert rec2["chosen"] == "fast"


def test_recommend_when_no_option_meets_target():
    opts = [_opt("a", 1.0, 30, 10, 0.5), _opt("b", 2.0, 20, 10, 0.8)]
    rec = pareto.recommend(opts, {"cost": 1.0, "time": 0.0, "risk": 0.0}, 0.9)
    assert rec["status"] == "target_not_met" and rec["chosen"] == "b"


def test_template_recommendations_are_on_the_front_or_justified(runs):
    for name, (res, _) in runs.items():
        for lane in res["lanes"]:
            rec = lane["recommendation"]
            if rec["status"] == "meets_target":
                assert rec["chosen"] in rec["front"], (name, lane["id"])
            for o in lane["options"]:
                assert o["pareto"] == (o["id"] in rec["front"])
                assert o["pareto"] == (not o["dominated_by"])


def test_recommend_counts_on_time_equal_to_target_as_feasible():
    opts = [_opt("exact", 1.0, 10, 10, 0.9), _opt("safe", 3.0, 8, 10, 0.99)]
    rec = pareto.recommend(opts, {"cost": 1.0, "time": 0.0, "risk": 0.0}, 0.9)
    assert rec["status"] == "meets_target"
    assert set(rec["feasible"]) == {"exact", "safe"} and rec["chosen"] == "exact"
