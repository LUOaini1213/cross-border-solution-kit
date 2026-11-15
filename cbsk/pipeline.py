"""Run one template end to end: RFQ -> options -> costs, transit, compliance -> Pareto -> recommendation."""
from __future__ import annotations

from . import compliance, incoterms, narrative, pareto, schema
from .calc import RateBook
from .flows import b2b, parcel, temporary
from .flows.common import Ctx
from .io import TEMPLATES
from .reference import Reference

TEMPLATES_ORDER = ("automotive_ckd_cn_my", "semiconductor_temp_sg", "consumer_ecom_sea")


def _jsonable_regimes(regimes: dict) -> dict:
    return {k: dict(v) for k, v in regimes.items()}


def run_template(name: str) -> tuple[dict, dict]:
    rfq = schema.load_rfq(TEMPLATES / name / "rfq.yaml")
    ref = Reference()
    rb = RateBook()
    draws = int(ref.get("transit.monte_carlo.draws"))
    ctx = Ctx(ref, rb, rfq["incoterm"], rfq["quoting_party_role"], int(rfq["seed"]), draws)
    flow = rfq["flow_type"]
    all_modes = sorted({m for ln in rfq["lanes"] for m in ln["modes"]})
    template_flags = [compliance.flag(f["id"], f["severity"], f["en"], f["zh"], statements=f.get("statements", []))
                      for f in incoterms.check(ref, rfq["incoterm"], rfq["quoting_party_role"], all_modes)]
    compliance.finalize_flags(ref, template_flags)
    target_p = float(rfq["service"]["on_time_target_probability"])
    lvg_sales_myr = None
    if flow == "b2c_parcel":
        avg_retail = sum(b["share"] * b["retail_usd"] for b in rfq["basket"])
        fx = float(ref.get("regimes.fx.MYR"))
        lvg_sales_myr = sum(ln["parcels_per_month"] * 12 * avg_retail * fx for ln in rfq["lanes"]
                            if ln["destination"]["country"] == "MY")
    lanes_out, calcs = [], {}
    for lane in rfq["lanes"]:
        extra: dict = {}
        if flow == "b2b_import":
            fta_rows = b2b._fta_rows(ctx, lane, rfq["service"].get("fta_preference", "auto"))
            lf = b2b.lane_flags(ctx, lane, rfq, fta_rows)
            res = b2b.build_lane(ctx, lane, rfq, lf, fta_rows)
            extra["fta"] = fta_rows
            unit = lane.get("unit", "unit")
        elif flow == "temporary":
            regimes = compliance.temporary_regimes(ref, lane["purpose"], lane["origin"]["country"], lane["destination"]["country"])
            lf = temporary.lane_flags(ctx, lane, regimes)
            res = temporary.build_lane(ctx, lane, rfq, lf, regimes)
            extra["regimes"] = _jsonable_regimes(regimes)
            unit = "move"
        else:
            lf = parcel.lane_flags(ctx, lane, rfq, lvg_sales_myr)
            res = parcel.build_lane(ctx, lane, rfq, lf)
            unit = "parcel"
        options = res["options"]
        compliance.finalize_flags(ref, lf)
        for opt in options:
            compliance.finalize_flags(ref, opt["flags"])
        if not options:
            raise RuntimeError(f"lane {lane['id']}: no feasible option generated")
        for opt in options:
            calcs[opt["id"]] = opt.pop("_calc")
            opt["metrics"] = {"cost_per_unit": opt["totals"]["per_unit"], "p50": opt["transit"]["p50"],
                              "p90": opt["transit"]["p90"], "mean": opt["transit"]["mean"],
                              "on_time_probability": opt["transit"]["on_time_probability"], "risk": opt["risk"]["score"]}
        pts = [(o["metrics"]["cost_per_unit"], o["metrics"]["p90"], o["metrics"]["risk"]) for o in options]
        rec = pareto.recommend(options, rfq["priorities"], target_p)
        for i, opt in enumerate(options):
            opt["pareto"] = opt["id"] in rec["front"]
            opt["dominated_by"] = [options[j]["id"] for j in pareto.dominated_by(pts, i)]
        lane_out = {
            "id": lane["id"], "name_en": lane["name_en"], "name_zh": lane["name_zh"],
            "origin": lane["origin"], "destination": lane["destination"], "target_transit_days": lane["target_transit_days"],
            "unit": unit, "options": options, "excluded": res["excluded"], "lane_flags": lf, "extra": extra,
            "recommendation": rec,
        }
        lane_out["rationale"] = narrative.rationale(lane_out, options, rec, target_p, unit)
        lanes_out.append(lane_out)
    summary = []
    for ln in lanes_out:
        ch = next(o for o in ln["options"] if o["id"] == ln["recommendation"]["chosen"])
        summary.append({"lane": ln["id"], "option": ch["id"], "label_en": ch["label_en"], "label_zh": ch["label_zh"],
                        "status": ln["recommendation"]["status"], "unit": ln["unit"],
                        "cost_per_unit": ch["metrics"]["cost_per_unit"], "p50": ch["metrics"]["p50"],
                        "p90": ch["metrics"]["p90"], "on_time_probability": ch["metrics"]["on_time_probability"],
                        "risk": ch["metrics"]["risk"], "annual_quote": ch["totals"]["quote"],
                        "annual_duty": ch["totals"]["duty"], "annual_tax": ch["totals"]["tax"],
                        "annual_landed": ch["totals"]["landed"]})
    statements_used = sorted({s for ln in lanes_out for o in ln["options"] for f in o["flags"] for s in f["statements"]}
                             | {s for ln in lanes_out for f in ln["lane_flags"] for s in f["statements"]}
                             | {s for f in template_flags for s in f["statements"]}
                             | {p.statement for p in ref.used.values() if p.statement}
                             | {s for r in rb.rates.values() if r.get("statement") for s in str(r["statement"]).split(",")})
    extra_tables: dict = {}
    if flow == "b2c_parcel":
        from . import duties
        ship = float(rfq["service"].get("shipping_charged_per_parcel", 0.0))
        rows = []
        for dest in ("MY", "ID", "TH", "PH"):
            for b in rfq["basket"]:
                pt = duties.parcel_taxes(ref, dest, "air_courier", b["hs"], b["retail_usd"], ship,
                                         bool(rfq["service"].get("seller_registered_my_lvg", False)))
                bt = duties.bulk_import_taxes(ref, dest, b["hs"], b["cost_usd"], b["retail_usd"])
                rows.append({"destination": dest, "category": b["category"], "category_zh": b.get("description_zh", b["category"]),
                             "hs": b["hs"], "retail": b["retail_usd"],
                             "parcel": pt.as_dict(), "bulk": bt.as_dict()})
        extra_tables["regime_table"] = rows
    results = {
        "template": name,
        "extra_tables": extra_tables,
        "rfq": {k: rfq[k] for k in ("rfq_id", "title_en", "title_zh", "customer", "customer_profile_en", "customer_profile_zh",
                                     "issue_date", "quote_validity_days", "currency", "seed", "flow_type", "incoterm",
                                     "incoterm_named_place", "incoterm_named_place_zh", "quoting_party_role", "priorities",
                                     "service") if k in rfq},
        "template_flags": template_flags,
        "lanes": lanes_out,
        "summary": summary,
        "assumptions": [rb.rates[k] for k in sorted(rb.rates)],
        "provenance": ref.provenance_records(),
        "statements_used": statements_used,
        "monte_carlo_draws": draws,
    }
    return results, {"calcs": calcs, "ratebook": rb, "ref": ref, "rfq": rfq}
