"""B2B import lanes (automotive template): FCL / LCL / air / rail-sea options with a multi-leg cost
build-up, FTA tariff choice per HS line and Malaysian duty + sales tax."""
from __future__ import annotations

from .. import compliance, duties, legs as L
from ..calc import C, Calc, R, add, div, mul, mx, sub
from ..duties import ISO3
from .common import Ctx, add_totals, ceil_div, option_label, run_transit

HANDOFFS = {"ocean_fcl": 2, "ocean_lcl": 4, "air": 2, "rail_sea_fcl": 3}


def _fta_rows(ctx: Ctx, lane: dict, pref: str) -> list[dict]:
    """Tariff treatment per line: MFN vs ACFTA vs RCEP, the chosen scheme and whether the preference pays
    for its paperwork (annual duty saving on goods value vs. certificate handling per shipment)."""
    rows = []
    shipments = 12 * int(lane["shipments_per_month"])
    doc_fee = float(ctx.ref.get("rates.fta.form_e_per_shipment"))
    margin = float(ctx.ref.get("compliance.fta.worth_it_margin_usd_per_year"))
    for ln in lane["lines"]:
        opts = duties.fta_options_my(ctx.ref, ln["hs"], ln["origin"], ln.get("supplier_rvc_pct"), ln.get("cth_met"))
        chosen = duties.choose_tariff(opts, pref)
        mfn = opts[0]["rate"]
        best = min(o["rate"] for o in opts if o["rate"] is not None)
        annual_value = lane["annual_units"] * ln["value_per_unit"]
        saving = (mfn - chosen["rate"]) * annual_value
        doc_cost = shipments * doc_fee / len(lane["lines"]) if chosen["scheme"] != "MFN" else 0.0
        rows.append({"sku": ln["sku"], "hs": ln["hs"], "rvc": ln.get("supplier_rvc_pct"), "options": opts,
                     "chosen": chosen, "mfn_rate": mfn,
                     "saving_if_qualified": (mfn - best) * annual_value,
                     "annual_goods_value": annual_value, "annual_saving": saving, "doc_cost": doc_cost,
                     "net_saving": saving - doc_cost, "worth_it": (saving - doc_cost) > margin})
    return rows


def lane_flags(ctx: Ctx, lane: dict, rfq: dict, fta_rows: list[dict]) -> list[dict]:
    ref = ctx.ref
    d2 = lane["destination"]["country"]
    lines = [{"hs": ln["hs"], "flags": set()} for ln in lane["lines"]]
    out = compliance.hs_flags(ref, d2, lines, {"kit"} if lane.get("kit") else set(), set())
    inv = lane.get("invoicing", {})
    out += compliance.fta_flags(ref, fta_rows, bool(inv.get("third_party")), inv.get("invoicing_country", ""))
    if rfq["service"].get("registered_manufacturer_schedule_c"):
        out.append(compliance.flag(
            "MY-SCHEDULE-C", "medium",
            "Sales tax on imported components is set to nil on the assumption that Customer A holds Schedule C (registered manufacturer) exemption; eligibility conditions were not verified. Without it, 10% sales tax applies on customs value plus duty.",
            "进口零部件销售税按 Customer A 已取得附表 C（注册制造商）豁免计为零；资格条件未经核实。若无此豁免，须按完税价格加关税的 10% 缴纳销售税。",
            "Confirm the Schedule C approval and its validity for each HS line before go-live.",
            "上线前确认附表 C 批文及其对各税号的有效性。", ["MY-ST-SCHEDULE-C", "MY-ST-IMPORT-BASE"], verified=False))
    out.append(compliance.flag(
        "MY-EV-INCENTIVE", "info",
        "The programme is an internal-combustion SUV, so the EV component duty exemption (until 31 Dec 2027) does not apply; an EV variant would need its own eligibility check.",
        "本项目为燃油 SUV，不适用电动车零部件进口关税豁免（至 2027 年 12 月 31 日）；如推出电动车型需另行确认资格。",
        statements=["MY-EV-CKD"]))
    return out


def _rail_service(ctx: Ctx, o2: str, d2: str) -> dict | None:
    for svc in ctx.ref.get("compliance.services"):
        if svc["mode"] == "rail" and f"{o2}-{d2}" in svc["lanes"]:
            return svc
    return None


def build_lane(ctx: Ctx, lane: dict, rfq: dict, lane_flag_list: list[dict], fta_rows: list[dict]) -> dict:
    ref = ctx.ref
    o, d = lane["origin"], lane["destination"]
    o2, d2 = o["country"], d["country"]
    if d2 != "MY":
        raise ValueError("the B2B duty model is implemented for Malaysia only")
    o3, d3 = ISO3[o2], ISO3[d2]
    U, S = float(lane["annual_units"]), int(lane["shipments_per_month"])
    prof = lane["monthly_profile"]
    g, v = float(lane["unit_gross_kg"]), float(lane["unit_cbm"])
    per_ship = [U * m / 12.0 / S for m in prof]
    shipments = 12 * S
    unit = lane.get("unit", "unit")
    n_risk = compliance.hold_flag_count(ref, lane_flag_list)
    options, excluded = [], []
    any_pref = any(r["chosen"]["scheme"] != "MFN" for r in fta_rows)

    for mode in lane["modes"]:
        if mode == "rail":
            svc = _rail_service(ctx, o2, d2)
            if svc is None or svc["status"] != "verified":
                excluded.append({"mode": mode, "reason_en": ("No verified scheduled cross-border rail service for this lane: "
                                                              + (svc["note"] if svc else "none in the services registry")),
                                 "reason_zh": "该线路无经核实的定期跨境铁路班列，暂不纳入方案。",
                                 "statements": svc["statements"] if svc else []})
                continue
        calc = Calc(f"{lane['id']}.{mode}", ctx.ratebook)
        UNITS = calc.input("UNITS", U, f"{unit}s per year", f"年{unit}量", unit)
        SHP = calc.input("SHIPMENTS", shipments, "Shipments per year", "年发运票数", "shipment")
        quantities = {"units_per_year": U, "shipments_per_year": shipments}
        to_border = []

        def truck_feu(short, n_expr, km_expr, en, zh, element):
            base = ctx.rate("rates.truck.feu_base", "Truck per 40ft move: fixed part", "40 尺拖车：固定部分")
            per_km = ctx.rate("rates.truck.feu_per_km", "Truck per 40ft move: per km", "40 尺拖车：每公里")
            return ctx.line(calc, short, mul(n_expr, add(base, mul(per_km, km_expr))), en, zh, element)

        def truck_light(short, n_expr, km_expr, en, zh, element):
            base = ctx.rate("rates.truck.light_base", "Light truck per shipment: fixed part", "轻型货车每票：固定部分")
            per_km = ctx.rate("rates.truck.light_per_km", "Light truck per shipment: per km", "轻型货车每票：每公里")
            return ctx.line(calc, short, mul(n_expr, add(base, mul(per_km, km_expr))), en, zh, element)

        exp_rate = ctx.rate(f"rates.handling.export_declaration.{o2}", f"Export declaration ({o2})", f"出口报关（{o2}）")
        imp_rate = ctx.rate(f"rates.handling.import_declaration.{d2}", f"Import declaration ({d2})", f"进口报关（{d2}）")

        if mode in ("ocean_fcl", "rail_sea_fcl"):
            cap = float(ref.get("rates.container.feu_usable_cbm")) * float(ref.get("rates.container.fill_factor"))
            payload = float(ref.get("rates.container.feu_payload_kg"))
            feu_by_month = [max(ceil_div(q * v, cap), ceil_div(q * g, payload)) for q in per_ship]
            feu = sum(S * n for n in feu_by_month)
            quantities.update({"feu_per_year": feu, "feu_per_shipment_by_month": feu_by_month,
                               "avg_fill": U * v / (feu * cap)})
            FEU = calc.input("FEU", feu, "40ft HC containers per year", "年 40 尺高柜数", "FEU")
            KM_P = calc.input("KM_PICKUP", o["pickup_km_port"], "Pickup distance to port/rail terminal", "提货至港口/铁路站距离", "km")
            KM_D = calc.input("KM_DELIVERY", d["delivery_km_port"], "Delivery distance from port", "港口至工厂距离", "km")
            to_border.append(truck_feu("PICKUP", FEU, KM_P, "Pickup at supplier (truck)", "供应商处提货（拖车）", "pre_carriage"))
            if mode == "rail_sea_fcl":
                to_border.append(ctx.line(calc, "RAIL", mul(FEU, ctx.rate("rates.rail.chongqing_qinzhou_feu", "Rail Chongqing-Qinzhou per 40ft", "重庆—钦州铁路每 40 尺")),
                                          "Rail to Qinzhou port", "铁路至钦州港", "pre_carriage"))
                port_o = "CNQZH"
            else:
                port_o = o["port"]
            to_border.append(ctx.line(calc, "THC_O", mul(FEU, ctx.rate(f"rates.handling.thc_origin_feu.{o2}", f"Origin THC per 40ft ({o2})", f"起运港码头操作费每 40 尺（{o2}）")),
                                      "Origin terminal handling", "起运港码头操作", "origin_terminal_handling"))
            ctx.line(calc, "EXPORT_DECL", mul(SHP, exp_rate), "Export declaration", "出口报关", "export_clearance")
            to_border.append(ctx.line(calc, "MAIN", mul(FEU, ctx.rate(f"rates.ocean_fcl_feu.{port_o}-{d['port']}", f"Ocean freight {port_o}-{d['port']} per 40ft", f"海运费 {port_o}-{d['port']} 每 40 尺")),
                                      "Ocean freight", "海运费", "main_carriage"))
            ctx.line(calc, "THC_D", mul(FEU, ctx.rate(f"rates.handling.thc_destination_feu.{d2}", f"Destination THC per 40ft ({d2})", f"目的港码头操作费每 40 尺（{d2}）")),
                     "Destination terminal handling", "目的港码头操作", "destination_terminal_handling")
            ctx.line(calc, "IMPORT_DECL", mul(SHP, imp_rate), "Import declaration", "进口报关", "import_clearance")
            truck_feu("DELIVERY", FEU, KM_D, "Delivery to plant (truck)", "送货至工厂（拖车）", "on_carriage")
            if "returnable_racks" in rfq["service"]["vas"]:
                ctx.line(calc, "VAS_RACKS", mul(FEU, ctx.rate("rates.vas.returnable_rack_per_feu", "Returnable rack management per 40ft", "循环料架管理每 40 尺")),
                         "Returnable rack management", "循环料架管理", None, group="vas")
            legs = L.truck("pickup", ref, o["pickup_km_port"])
            if mode == "rail_sea_fcl":
                lo, mo, hi = ref.triangular("transit.rail.qinzhou_rail_days")
                legs += [L.leg("rail Chongqing-Qinzhou", "triangular", low=lo, mode=mo, high=hi, source="transit.rail.qinzhou_rail_days"),
                         L.wait("wait for rail-sea train", float(ref.get("transit.rail.qinzhou_headway_days")), "transit.rail.qinzhou_headway_days")]
            legs += L.ocean_main(ref, o3, port_o, d3, d["port"])
        elif mode == "ocean_lcl":
            wm_by_month = [max(q * v, q * g / 1000.0, float(ref.get("rates.ocean_lcl.min_wm"))) for q in per_ship]
            wm = sum(S * w for w in wm_by_month)
            quantities.update({"wm_per_year": wm})
            WM = calc.input("WM", wm, "Freight tonnes (W/M) per year", "年计费吨（W/M）", "W/M")
            KM_P = calc.input("KM_PICKUP", o["pickup_km_port"], "Pickup distance to CFS", "提货至集拼站距离", "km")
            KM_D = calc.input("KM_DELIVERY", d["delivery_km_port"], "Delivery distance from CFS", "集拼站至工厂距离", "km")
            to_border.append(truck_light("PICKUP", SHP, KM_P, "Pickup at supplier (truck)", "供应商处提货（货车）", "pre_carriage"))
            to_border.append(ctx.line(calc, "CFS_O", mul(WM, ctx.rate("rates.ocean_lcl.cfs_origin_per_wm", "Origin CFS per W/M", "起运港集拼站费每计费吨")),
                                      "Origin CFS handling", "起运港集拼站操作", "origin_terminal_handling"))
            ctx.line(calc, "EXPORT_DECL", mul(SHP, exp_rate), "Export declaration", "出口报关", "export_clearance")
            to_border.append(ctx.line(calc, "MAIN", mul(WM, ctx.rate("rates.ocean_lcl.freight_per_wm.CN-SEA", "LCL ocean freight per W/M (China-SE Asia)", "拼箱海运费每计费吨（中国—东南亚）")),
                                      "LCL ocean freight", "拼箱海运费", "main_carriage"))
            ctx.line(calc, "CFS_D", mul(WM, ctx.rate("rates.ocean_lcl.cfs_destination_per_wm", "Destination CFS per W/M", "目的港集拼站费每计费吨")),
                     "Destination CFS handling", "目的港集拼站操作", "destination_terminal_handling")
            ctx.line(calc, "IMPORT_DECL", mul(SHP, imp_rate), "Import declaration", "进口报关", "import_clearance")
            truck_light("DELIVERY", SHP, KM_D, "Delivery to plant (truck)", "送货至工厂（货车）", "on_carriage")
            legs = (L.truck("pickup", ref, o["pickup_km_port"]) + [L.tri("LCL consolidation at origin CFS", ref, "transit.sea.lcl_consolidation_days")]
                    + L.ocean_main(ref, o3, o["port"], d3, d["port"])
                    + [L.tri("LCL deconsolidation at destination CFS", ref, "transit.sea.lcl_deconsolidation_days")])
        elif mode == "air":
            vol = float(ref.get("rates.air.volumetric_kg_per_cbm"))
            mink = float(ref.get("rates.air.min_chargeable_kg"))
            chg_by_month = [max(q * g, q * v * vol, mink) for q in per_ship]
            chg = sum(S * c for c in chg_by_month)
            quantities.update({"chargeable_kg_per_year": chg})
            KG = calc.input("CHG_KG", chg, "Chargeable kg per year", "年计费重量（公斤）", "kg")
            KM_P = calc.input("KM_PICKUP", o["pickup_km_airport"], "Pickup distance to airport", "提货至机场距离", "km")
            KM_D = calc.input("KM_DELIVERY", d["delivery_km_airport"], "Delivery distance from airport", "机场至工厂距离", "km")
            to_border.append(truck_light("PICKUP", SHP, KM_P, "Pickup at supplier (truck to airport)", "供应商处提货（送机场）", "pre_carriage"))
            to_border.append(ctx.line(calc, "HANDLING_O", mul(KG, ctx.rate("rates.air.handling_origin_per_kg", "Origin airport handling per kg", "起运机场操作费每公斤")),
                                      "Origin airport handling", "起运机场操作", "origin_terminal_handling"))
            ctx.line(calc, "EXPORT_DECL", mul(SHP, exp_rate), "Export declaration", "出口报关", "export_clearance")
            key = f"{o['airport']}-{d['airport']}"
            to_border.append(ctx.line(calc, "MAIN", mul(KG, ctx.rate(f"rates.air.per_kg.{key}", f"Air freight {key} per kg", f"空运费 {key} 每公斤")),
                                      "Air freight", "空运费", "main_carriage"))
            ctx.line(calc, "HANDLING_D", mul(KG, ctx.rate("rates.air.handling_destination_per_kg", "Destination airport handling per kg", "目的机场操作费每公斤")),
                     "Destination airport handling", "目的机场操作", "destination_terminal_handling")
            ctx.line(calc, "IMPORT_DECL", mul(SHP, imp_rate), "Import declaration", "进口报关", "import_clearance")
            truck_light("DELIVERY", SHP, KM_D, "Delivery to plant (truck)", "送货至工厂（货车）", "on_carriage")
            legs = L.truck("pickup", ref, o["pickup_km_airport"]) + L.air_main(ref, o["airport"], d["airport"], d3)
        else:
            raise ValueError(f"unsupported B2B mode {mode}")

        # goods value, insurance, VAS, origin documents
        goods_nodes = {}
        for ln in lane["lines"]:
            goods_nodes[ln["sku"]] = calc.input(f"GOODS_{ln['sku']}", U * ln["value_per_unit"],
                                                f"Goods value {ln['sku']} (FCA price)", f"货值 {ln['sku']}（FCA 价）", "USD", "goods")
        GOODS = calc.calc("GOODS_TOTAL", add(*goods_nodes.values()), "Goods value total", "货值合计", group="goods")
        ins = None
        if rfq["service"].get("insurance"):
            rate = ctx.rate("rates.insurance.rate", "Cargo insurance rate", "货运保险费率")
            factor = ctx.rate("rates.insurance.insured_value_factor", "Insured value factor (CIF x 110%)", "投保加成（CIF × 110%）")
            minimum = ctx.rate("rates.insurance.min_per_shipment", "Insurance minimum per shipment", "每票最低保险费")
            ins = ctx.line(calc, "INSURANCE", mx(mul(SHP, minimum), mul(rate, factor, add(GOODS, *to_border))),
                           "Cargo insurance (110% of CIF)", "货运保险（CIF 的 110%）", "insurance", group="insurance")
        if "kitting" in rfq["service"]["vas"]:
            ctx.line(calc, "VAS_KITTING", mul(UNITS, ctx.rate("rates.vas.kitting_per_kit", "Kitting / sequencing per kit", "配套/排序每套")),
                     "Kitting and line-side sequencing", "配套及工位排序", None, group="vas")
        if any_pref:
            ctx.line(calc, "FTA_DOCS", mul(SHP, ctx.rate("rates.fta.form_e_per_shipment", "Form E certificate per shipment", "Form E 原产地证每票")),
                     "Certificate of origin (Form E) handling", "原产地证（Form E）办理", "import_clearance", group="fta_docs")

        # duties and sales tax per HS line (CIF valuation)
        schc = ctx.fixed("rfq.registered_manufacturer_schedule_c",
                         1.0 if rfq["service"].get("registered_manufacturer_schedule_c") else 0.0,
                         "Schedule C sales-tax exemption applied (1 = yes)", "适用附表 C 销售税豁免（1 = 是）", "SYNTHETIC")
        freight_ins = add(*to_border, ins) if ins is not None else add(*to_border)
        for ln, fr in zip(lane["lines"], fta_rows):
            gi = goods_nodes[ln["sku"]]
            cv = calc.calc(f"CV_{ln['sku']}", add(gi, mul(div(gi, GOODS), freight_ins)),
                           f"Customs value {ln['sku']} (CIF)", f"完税价格 {ln['sku']}（CIF）", group="info")
            col = {"MFN": "mfn_import", "ACFTA": "acfta_current", "RCEP": "rcep_current"}[fr["chosen"]["scheme"]]
            r_duty = ctx.tariff(ln["hs"], col, f"Import duty {ln['hs']} ({fr['chosen']['scheme']})",
                                f"进口关税 {ln['hs']}（{fr['chosen']['scheme']}）")
            duty = ctx.line(calc, f"DUTY_{ln['sku']}", mul(r_duty, cv), f"Import duty {ln['sku']} ({fr['chosen']['scheme']})",
                            f"进口关税 {ln['sku']}（{fr['chosen']['scheme']}）", "duties_taxes", group="duty")
            r_st = ctx.tariff(ln["hs"], "sst", f"Sales tax {ln['hs']} (SST column)", f"销售税 {ln['hs']}（SST 栏）")
            ctx.line(calc, f"SALES_TAX_{ln['sku']}", mul(r_st, add(cv, duty), sub(C(1.0), schc)),
                     f"Sales tax on import {ln['sku']}", f"进口销售税 {ln['sku']}", "duties_taxes", group="tax")

        # transit
        hold = L.customs_hold(ref, n_risk)
        legs = legs + [hold]
        km_del = d["delivery_km_airport"] if mode == "air" else d["delivery_km_port"]
        legs = legs + L.truck("delivery", ref, km_del)
        tm, _ = run_transit(legs, ctx, float(lane["target_transit_days"]), rfq["rfq_id"], lane["id"], mode)
        MEAN = calc.input("MEAN_TRANSIT_DAYS", tm["mean"], "Mean door-to-door days (simulated)", "平均门到门天数（模拟）", "days")
        ctx.line(calc, "CARRYING", mul(GOODS, ctx.rate("rates.economics.carrying_cost_pa", "Inventory carrying cost per year", "库存资金占用年费率"),
                                       div(MEAN, C(365.0))),
                 "Pipeline inventory carrying cost", "在途库存资金占用成本", None, group="economic")
        totals_nodes = add_totals(calc, UNITS, unit)
        totals = {k: calc.value(e[1]) for k, e in totals_nodes.items()}

        opt_flags = compliance.flags_for_option(lane_flag_list, mode, mode)
        if mode == "ocean_lcl":
            opt_flags = opt_flags + [compliance.flag("LCL-HANDLING", "low",
                                                     "LCL adds two CFS handlings per shipment, raising damage and shortage risk for kit parts.",
                                                     "拼箱每票增加两次集拼站作业，散件破损及短少风险上升。",
                                                     "Use crates sized for mixed loading; count at destination CFS.", "采用适合混装的木箱；目的港集拼站点数。")]
        if mode == "rail_sea_fcl":
            opt_flags = opt_flags + [compliance.flag("RAIL-SEA-FREQUENCY", "low",
                                                     "Rail-sea chain: domestic rail leg to Qinzhou is evidenced only by state-affiliated media; train frequency is an assumption.",
                                                     "铁海联运：重庆至钦州铁路段仅有官方背景媒体报道，班列频率为假设。",
                                                     "Confirm the rail-sea schedule and cut-off before committing volume.", "承诺货量前确认铁海联运班期与截关时间。",
                                                     ["SVC-ILSTC"], verified=False)]
        risk = compliance.risk_score(ref, opt_flags, tm["p50"], tm["p90"], HANDOFFS[mode], False)
        label_en, label_zh = option_label(mode)
        options.append({"id": f"{lane['id']}-{mode}", "mode": mode, "regime": None, "label_en": label_en, "label_zh": label_zh,
                        "quantities": quantities, "legs": legs, "transit": tm, "totals": totals,
                        "costs": calc.table(), "flags": opt_flags, "risk": risk, "handoffs": HANDOFFS[mode],
                        "_calc": calc})
    return {"options": options, "excluded": excluded}
