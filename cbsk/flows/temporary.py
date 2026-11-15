"""Temporary moves (semiconductor template): exhibition and professional-equipment moves into Singapore
under an ATA Carnet or the Temporary Import Scheme, and repair loops out of / into Singapore."""
from __future__ import annotations

from .. import compliance, duties, legs as L
from ..calc import C, Calc, add, div, mul, mx
from ..duties import ISO3
from .common import Ctx, add_totals, option_label, run_transit

HANDOFFS = {"air": 4, "ocean_fcl20": 4, "ocean_lcl": 8, "road": 2}


def lane_flags(ctx: Ctx, lane: dict, regimes: dict) -> list[dict]:
    ref = ctx.ref
    item = lane["item"]
    lines = [{"hs": item["hs"], "flags": {"strategic_screening"} if item.get("strategic_screening") else set()}]
    o2, d2 = lane["origin"]["country"], lane["destination"]["country"]
    context = {"sg_export"}   # every loop leaves Singapore once (return leg or outbound repair leg)
    if o2 != "SG":
        context.add("origin_export_semiconductor")
    out = compliance.hs_flags(ref, d2, lines, set(), context)
    out += compliance.temporary_flags(ref, lane, regimes)
    return out


def _leg_costs(ctx: Ctx, calc: Calc, tag: str, mode: str, frm: dict, to: dict, item: dict, MOVES, en_dir: str, zh_dir: str,
               regime: str | None):
    """Costs of one direction (per year = per move x moves)."""
    ref = ctx.ref
    f2, t2 = frm["country"], to["country"]
    mult = ctx.rate("rates.truck.air_ride_multiplier", "Air-ride / tail-lift truck premium (x)", "气垫车/尾板车加价倍数")
    if mode == "air":
        vol = float(ref.get("rates.air.volumetric_kg_per_cbm"))
        chg = max(item["gross_kg"], item["cbm"] * vol, float(ref.get("rates.air.min_chargeable_kg")))
        KG = calc.input(f"{tag}_CHG_KG", chg, f"Chargeable kg per move ({en_dir})", f"每次计费重量（{zh_dir}）", "kg")
        km_p = frm["pickup_km_airport"]
        km_d = to["delivery_km_airport"]
    elif mode == "ocean_lcl":
        wm = max(item["cbm"], item["gross_kg"] / 1000.0, float(ref.get("rates.ocean_lcl.min_wm")))
        WM = calc.input(f"{tag}_WM", wm, f"W/M per move ({en_dir})", f"每次计费吨（{zh_dir}）", "W/M")
        km_p, km_d = frm["pickup_km_port"], to["delivery_km_port"]
    elif mode == "ocean_fcl20":
        km_p, km_d = frm["pickup_km_port"], to["delivery_km_port"]
    elif mode == "road":
        km_p = km_d = 0.0
    else:
        raise ValueError(mode)
    lines = []
    if mode == "road":
        lines.append(ctx.line(calc, f"{tag}_ROAD", mul(MOVES, ctx.rate("rates.truck.cross_border_sg_my_ftl", "Cross-border truck Penang-Singapore (full truck)", "槟城—新加坡跨境整车")),
                              f"Cross-border truck, air-ride ({en_dir})", f"跨境气垫车运输（{zh_dir}）", "main_carriage"))
    else:
        KMP = calc.input(f"{tag}_KM_P", km_p, f"Pickup km ({en_dir})", f"提货公里数（{zh_dir}）", "km")
        KMD = calc.input(f"{tag}_KM_D", km_d, f"Delivery km ({en_dir})", f"送货公里数（{zh_dir}）", "km")
        if mode == "ocean_fcl20":
            base = ctx.rate("rates.truck.feu_base", "Truck per container move: fixed part", "集装箱拖车：固定部分")
            per_km = ctx.rate("rates.truck.feu_per_km", "Truck per container move: per km", "集装箱拖车：每公里")
        else:
            base = ctx.rate("rates.truck.light_base", "Light truck per shipment: fixed part", "轻型货车每票：固定部分")
            per_km = ctx.rate("rates.truck.light_per_km", "Light truck per shipment: per km", "轻型货车每票：每公里")
        lines.append(ctx.line(calc, f"{tag}_PICKUP", mul(MOVES, mult, add(base, mul(per_km, KMP))),
                              f"Air-ride pickup ({en_dir})", f"气垫车提货（{zh_dir}）", "pre_carriage"))
        if mode == "air":
            key = f"{frm['airport']}-{to['airport']}"
            lines.append(ctx.line(calc, f"{tag}_HANDLING_O", mul(MOVES, KG, ctx.rate("rates.air.handling_origin_per_kg", "Origin airport handling per kg", "起运机场操作费每公斤")),
                                  f"Origin airport handling ({en_dir})", f"起运机场操作（{zh_dir}）", "origin_terminal_handling"))
            lines.append(ctx.line(calc, f"{tag}_MAIN", mul(MOVES, KG, ctx.rate(f"rates.air.per_kg.{key}", f"Air freight {key} per kg", f"空运费 {key} 每公斤")),
                                  f"Air freight {key}", f"空运费 {key}", "main_carriage"))
            lines.append(ctx.line(calc, f"{tag}_HANDLING_D", mul(MOVES, KG, ctx.rate("rates.air.handling_destination_per_kg", "Destination airport handling per kg", "目的机场操作费每公斤")),
                                  f"Destination airport handling ({en_dir})", f"目的机场操作（{zh_dir}）", "destination_terminal_handling"))
        elif mode == "ocean_lcl":
            key = f"{f2}-{t2}" if f"{f2}-{t2}" in ("JP-SG", "US-SG", "SG-JP", "SG-US") else None
            if key is None:
                raise ValueError(f"no LCL rate for {f2}-{t2}")
            lines.append(ctx.line(calc, f"{tag}_CFS_O", mul(MOVES, WM, ctx.rate("rates.ocean_lcl.cfs_origin_per_wm", "Origin CFS per W/M", "起运港集拼站费每计费吨")),
                                  f"Origin CFS ({en_dir})", f"起运港集拼站（{zh_dir}）", "origin_terminal_handling"))
            lines.append(ctx.line(calc, f"{tag}_MAIN", mul(MOVES, WM, ctx.rate(f"rates.ocean_lcl.freight_per_wm.{key}", f"LCL ocean freight {key} per W/M", f"拼箱海运费 {key} 每计费吨")),
                                  f"LCL ocean freight {key}", f"拼箱海运费 {key}", "main_carriage"))
            lines.append(ctx.line(calc, f"{tag}_CFS_D", mul(MOVES, WM, ctx.rate("rates.ocean_lcl.cfs_destination_per_wm", "Destination CFS per W/M", "目的港集拼站费每计费吨")),
                                  f"Destination CFS ({en_dir})", f"目的港集拼站（{zh_dir}）", "destination_terminal_handling"))
        else:  # 20ft FCL
            key = f"{frm['port']}-{to['port']}"
            teu = ctx.rate("rates.teu_factor", "20ft price as share of 40ft", "20 尺价格占 40 尺比例")
            lines.append(ctx.line(calc, f"{tag}_THC_O", mul(MOVES, teu, ctx.rate(f"rates.handling.thc_origin_feu.{f2}", f"Origin THC per 40ft ({f2})", f"起运港码头操作费每 40 尺（{f2}）")),
                                  f"Origin THC, 20ft ({en_dir})", f"起运港码头操作 20 尺（{zh_dir}）", "origin_terminal_handling"))
            lines.append(ctx.line(calc, f"{tag}_MAIN", mul(MOVES, teu, ctx.rate(f"rates.ocean_fcl_feu.{key}", f"Ocean freight {key} per 40ft", f"海运费 {key} 每 40 尺")),
                                  f"Ocean freight 20ft {key}", f"20 尺海运费 {key}", "main_carriage"))
            lines.append(ctx.line(calc, f"{tag}_THC_D", mul(MOVES, teu, ctx.rate(f"rates.handling.thc_destination_feu.{t2}", f"Destination THC per 40ft ({t2})", f"目的港码头操作费每 40 尺（{t2}）")),
                                  f"Destination THC, 20ft ({en_dir})", f"目的港码头操作 20 尺（{zh_dir}）", "destination_terminal_handling"))
            if regime in ("ata_carnet", "tis") and "SG" in (f2, t2):
                lines.append(ctx.line(calc, f"{tag}_SUPERVISION", mul(MOVES, ctx.rate("rates.handling.supervision_fee", "Customs supervision of (un)stuffing", "海关监管拆装箱费")),
                                      f"Customs supervision of container (un)stuffing ({en_dir})", f"海关监管拆/装箱（{zh_dir}）", "import_clearance",
                                      group="temporary_admission"))
        lines.append(ctx.line(calc, f"{tag}_DELIVERY", mul(MOVES, mult, add(base, mul(per_km, KMD))),
                              f"Air-ride delivery ({en_dir})", f"气垫车送货（{zh_dir}）", "on_carriage"))
    lines.append(ctx.line(calc, f"{tag}_EXPORT_DECL", mul(MOVES, ctx.rate(f"rates.handling.export_declaration.{f2}", f"Export declaration ({f2})", f"出口报关（{f2}）")),
                          f"Export declaration ({en_dir})", f"出口报关（{zh_dir}）", "export_clearance"))
    lines.append(ctx.line(calc, f"{tag}_IMPORT_DECL", mul(MOVES, ctx.rate(f"rates.handling.import_declaration.{t2}", f"Import declaration ({t2})", f"进口报关（{t2}）")),
                          f"Import declaration ({en_dir})", f"进口报关（{zh_dir}）", "import_clearance"))
    return lines


def _transit_dir(ctx: Ctx, mode: str, frm: dict, to: dict, n_risk: int, road_km: float | None) -> list[dict]:
    ref = ctx.ref
    f3, t3 = ISO3[frm["country"]], ISO3[to["country"]]
    if mode == "air":
        legs = L.truck("pickup", ref, frm["pickup_km_airport"]) + L.air_main(ref, frm["airport"], to["airport"], t3)
        legs += [L.customs_hold(ref, n_risk)] + L.truck("delivery", ref, to["delivery_km_airport"])
    elif mode in ("ocean_lcl", "ocean_fcl20"):
        legs = L.truck("pickup", ref, frm["pickup_km_port"])
        if mode == "ocean_lcl":
            legs.append(L.tri("LCL consolidation", ref, "transit.sea.lcl_consolidation_days"))
        legs += L.ocean_main(ref, f3, frm["port"], t3, to["port"])
        if mode == "ocean_lcl":
            legs.append(L.tri("LCL deconsolidation", ref, "transit.sea.lcl_deconsolidation_days"))
        legs += [L.customs_hold(ref, n_risk)] + L.truck("delivery", ref, to["delivery_km_port"])
    elif mode == "road":
        legs = L.truck("cross-border truck", ref, road_km or 0.0)
        legs += [L.tri("Woodlands/Tuas border clearance", ref, "transit.truck.cross_border_sg_my_days"),
                 L.customs_hold(ref, n_risk)]
    else:
        raise ValueError(mode)
    return legs


def build_lane(ctx: Ctx, lane: dict, rfq: dict, lane_flag_list: list[dict], regimes: dict) -> dict:
    ref = ctx.ref
    item = lane["item"]
    o, d = lane["origin"], lane["destination"]
    moves = float(lane["moves_per_year"])
    n_risk = sum(1 for f in lane_flag_list if f["severity"] in ("medium", "high"))
    options, excluded = [], []
    for rg in lane["regimes"]:
        info = regimes.get(rg)
        if info is None or not info["available"]:
            excluded.append({"regime": rg, "reason_en": info["reason_en"] if info else "not applicable to this direction",
                             "reason_zh": info["reason_zh"] if info else "不适用于该方向",
                             "statements": info["statements"] if info else []})
    usable = [rg for rg in lane["regimes"] if regimes.get(rg, {}).get("available")]
    for mode in lane["modes"]:
        for rg in usable:
            calc = Calc(f"{lane['id']}.{mode}.{rg}", ctx.ratebook)
            MOVES = calc.input("MOVES", moves, "Moves (round trips) per year", "年往返次数", "move")
            VALUE = calc.input("ITEM_VALUE", item["value"], "Equipment value", "设备价值", "USD", "goods")
            out_lines = _leg_costs(ctx, calc, "OUT", mode, o, d, item, MOVES, "outbound", "去程", rg)
            ret_lines = _leg_costs(ctx, calc, "RET", mode, d, o, item, MOVES, "return", "回程", rg)
            vas = rfq["service"]["vas"]
            for key, pid, en, zh in (("semicon_crate", "rates.vas.semicon_crate_per_move", "Export crate with shock mounting", "防震出口木箱"),
                                     ("shock_tilt_indicators", "rates.vas.shock_tilt_indicators_per_move", "Shock and tilt indicators", "冲击/倾斜指示器"),
                                     ("cleanroom_bagging", "rates.vas.cleanroom_bagging_per_move", "Cleanroom bagging", "洁净室包装")):
                if key in vas:
                    ctx.line(calc, f"VAS_{key.upper()}", mul(MOVES, ctx.rate(pid, en + " per move", zh + "每次")), en, zh, None, group="vas")
            if rfq["service"].get("insurance"):
                rate = ctx.rate("rates.insurance.rate", "Cargo insurance rate", "货运保险费率")
                factor = ctx.rate("rates.insurance.insured_value_factor", "Insured value factor (110%)", "投保加成（110%）")
                ctx.line(calc, "INSURANCE", mul(MOVES, C(2.0), rate, factor, VALUE), "Transit insurance, both directions",
                         "往返运输保险", "insurance", group="insurance")
            # temporary-admission instrument
            if rg == "ata_carnet":
                fee = ctx.rate("rates.temporary_admission.foreign_carnet_fee", "ATA Carnet fee (carnet issued abroad)", "ATA 单证册签发费（境外签发）")
                share = ctx.rate("rates.temporary_admission.carnet_security_share", "Carnet security as share of value", "单证册担保占货值比例")
                gfee = ctx.rate("rates.temporary_admission.guarantee_fee_pa", "Guarantee / bond cost per year", "保函/保证保险年费率")
                ctx.line(calc, "CARNET_FEE", fee, "ATA Carnet issuance (one carnet a year covers the year's trips)",
                         "ATA 单证册签发（一本单证册覆盖全年行程）", None, group="temporary_admission")
                ctx.line(calc, "CARNET_SECURITY", mul(share, VALUE, gfee), "Carnet security cost (guarantee for one year)",
                         "单证册担保成本（一年期保函）", None, group="temporary_admission")
            elif rg == "tis":
                gst_reg = bool(rfq["service"].get("sg_entity_gst_registered", True))
                gst = ctx.rate("regimes.SG.gst_rate", "Singapore GST rate", "新加坡 GST 税率")
                shp = ctx.rate("regimes.SG.tis_security_share_registered" if gst_reg else "regimes.SG.tis_security_share_unregistered",
                               "TIS security as share of potential GST", "TIS 担保占潜在 GST 比例")
                gfee = ctx.rate("rates.temporary_admission.guarantee_fee_pa", "Guarantee / bond cost per year", "保函/保证保险年费率")
                stay = lane["stay_days"] if lane["purpose"] != "repair_in_sg" else ref.triangular("transit.temporary.repair_turnaround_days")[1]
                minm = float(ref.get("rates.temporary_admission.guarantee_min_months"))
                months = max(stay / 30.4, minm)
                MONTHS = calc.input("GUARANTEE_MONTHS", months, "Guarantee period per move (months, minimum applies)", "每次保函期限（月，适用最低期限）", "months")
                inbound_main = [n for n in out_lines if n[1].endswith("_MAIN") or n[1].endswith("_ROAD")]
                cif = calc.calc("CIF_SG", add(VALUE, div(add(*inbound_main), MOVES)), "Value at import into Singapore (CIF, per move)",
                                "进口新加坡时的价值（CIF，每次）", group="info")
                ctx.line(calc, "TIS_SECURITY_COST", mul(MOVES, shp, gst, cif, gfee, div(MONTHS, C(12.0))),
                         "TIS security cost (guarantee on the suspended GST)", "TIS 担保成本（就暂缓 GST 提供保函）", None,
                         group="temporary_admission")
                permit = ctx.rate("rates.handling.permit_fee", "Customs permit fee", "海关许可证费")
                agent = ctx.rate("rates.temporary_admission.tis_agent_fee_per_permit", "Declaring-agent fee per TIS permit", "TIS 每份许可证报关代理费")
                ctx.line(calc, "TIS_PERMITS", mul(MOVES, C(2.0), add(permit, agent)), "TIS inward and outward permits",
                         "TIS 进出许可证", None, group="temporary_admission")
            elif rg == "temp_export_repair":
                permit = ctx.rate("rates.handling.permit_fee", "Customs permit fee", "海关许可证费")
                agent = ctx.rate("rates.temporary_admission.tis_agent_fee_per_permit", "Declaring-agent fee per TIS permit", "TIS 每份许可证报关代理费")
                ctx.line(calc, "TEMP_EXPORT_PERMITS", mul(MOVES, C(2.0), add(permit, agent)),
                         "OUT (TCI) and In-Non-Payment (TCI) permits", "OUT (TCI) 与 In-Non-Payment (TCI) 许可证", None,
                         group="temporary_admission")
                ctx.line(calc, "DEST_REPAIR_ENTRY", mul(MOVES, ctx.rate("rates.temporary_admission.temp_import_repair_abroad_fee",
                                                                       "Destination temporary-import handling for repair", "目的地维修临时进口操作费")),
                         "Repair-centre country: temporary import handling (regime not verified)", "维修所在国：临时进口操作（制度未核实）",
                         None, group="temporary_admission")
                gst = ctx.rate("regimes.SG.gst_rate", "Singapore GST rate", "新加坡 GST 税率")
                nps = ctx.fixed(f"rfq.{lane['id']}.new_parts_share", lane["new_parts_share"], "New parts as share of item value per repair",
                                "每次维修新换部件占设备价值比例", "SYNTHETIC")
                wsh = ctx.fixed(f"rfq.{lane['id']}.warranty_share", lane["warranty_share"], "Share of repairs free under warranty",
                                "保修期内免费维修占比", "SYNTHETIC")
                ctx.line(calc, "GST_NEW_PARTS", mul(MOVES, gst, VALUE, nps, add(C(1.0), mul(C(-1.0), wsh))),
                         "GST on new parts at re-import (expected)", "复进口时新换部件 GST（期望值）", None, group="tax")
            # transit
            legs_out = _transit_dir(ctx, mode, o, d, n_risk, lane.get("road_km"))
            legs_ret = _transit_dir(ctx, mode, d, o, n_risk, lane.get("road_km"))
            if lane["transit_metric"] == "round_trip":
                lo, mo, hi = ref.triangular("transit.temporary.repair_turnaround_days")
                legs = legs_out + [L.leg("repair turnaround at the repair shop", "triangular", low=lo, mode=mo, high=hi,
                                         source="transit.temporary.repair_turnaround_days")] + legs_ret
            else:
                legs = legs_out
            tm, _ = run_transit(legs, ctx, float(lane["target_transit_days"]), rfq["rfq_id"], lane["id"], mode, rg)
            leg_days = calc.input("TRANSIT_DAYS_PER_MOVE", tm["mean"] if lane["transit_metric"] == "round_trip" else 2 * tm["mean"],
                                  "Days in transit per move (mean, both directions)", "每次往返在途天数（均值）", "days")
            ctx.line(calc, "CARRYING", mul(MOVES, VALUE, ctx.rate("rates.economics.carrying_cost_pa", "Inventory carrying cost per year", "库存资金占用年费率"),
                                           div(leg_days, C(365.0))),
                     "Capital tied up in transit", "在途资金占用成本", None, group="economic")
            totals_nodes = add_totals(calc, MOVES, "move")
            totals = {k: calc.value(e[1]) for k, e in totals_nodes.items()}
            opt_flags = compliance.flags_for_option(lane_flag_list, mode, mode)
            if rg == "tis" and lane["purpose"] in ("exhibition", "professional_equipment"):
                opt_flags = opt_flags + [compliance.flag("TIS-LOCAL-DECLARANT", "low",
                                                         "TIS permits are filed through TradeNet by a Singapore declarant, and security must be lodged before import.",
                                                         "TIS 许可证须由新加坡申报人通过 TradeNet 申报，并在进口前提交担保。",
                                                         "Appoint the declaring agent and lodge the guarantee two weeks before the move.",
                                                         "提前两周指定报关代理并提交担保。", ["SG-TIS-SECURITY"])]
            if rg == "ata_carnet":
                opt_flags = opt_flags + [compliance.flag("ATA-GENERAL-LIST", "low",
                                                         "The carnet's general list must match the goods exactly; partial shipments and changes need care at each border.",
                                                         "单证册总清单须与实物完全一致；分批发运或变更时每个关口都须核对。",
                                                         "Check serial numbers against the general list before each crossing.",
                                                         "每次过境前按总清单核对序列号。", ["SG-ATA-SAME-CONDITION"])]
            risk = compliance.risk_score(ref, opt_flags, tm["p50"], tm["p90"], HANDOFFS[mode], False)
            label_en, label_zh = option_label(mode, rg)
            options.append({"id": f"{lane['id']}-{mode}-{rg}", "mode": mode, "regime": rg, "label_en": label_en,
                            "label_zh": label_zh, "quantities": {"moves_per_year": moves}, "legs": legs, "transit": tm,
                            "totals": totals, "costs": calc.table(), "flags": opt_flags, "risk": risk,
                            "handoffs": HANDOFFS[mode], "_calc": calc})
    return {"options": options, "excluded": excluded}
