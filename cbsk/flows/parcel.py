"""B2C parcel lanes (consumer-goods template): air parcels DDP, sea-air via Singapore, China-Laos-Thailand
rail, Singapore-Malaysia road, and bulk ocean replenishment with local fulfilment."""
from __future__ import annotations

from .. import compliance, duties, legs as L
from ..calc import C, Calc, add, div, mul
from ..duties import ISO3
from .common import Ctx, add_totals, ceil_div, option_label, run_transit

HANDOFFS = {"air_parcel": 3, "sea_air": 6, "rail": 6, "road": 3, "ocean_bulk_local": 4}
DETOUR_LIMIT = 1.6          # sea-air only when the hub is broadly on the way (ASSUMPTION, documented)
LOCAL_DC_KM = 30.0          # port to local fulfilment centre (ASSUMPTION)


def _service(ctx: Ctx, mode: str, o2: str, d2: str) -> dict | None:
    for svc in ctx.ref.get("compliance.services"):
        if svc["mode"] == mode and f"{o2}-{d2}" in svc["lanes"]:
            return svc
    return None


def _regime_rate(ctx: Ctx, pid: str, value: float, statements: list[str], en: str, zh: str):
    ref = ctx.ref
    verified = statements and all(ref.statement(s)["status"] in ("verified", "corrected") for s in statements)
    entry = ctx.ratebook.add(pid, value, en, zh, None, label="REAL" if verified else "ASSUMPTION", unit="fraction")
    srcs = []
    for s in statements:
        srcs += ref.statement(s).get("sources", [])
    ctx.ratebook.rates[pid]["sources"] = sorted(set(srcs))
    ctx.ratebook.rates[pid]["statement"] = ",".join(statements)
    return entry


def lane_flags(ctx: Ctx, lane: dict, rfq: dict, annual_lvg_sales_myr: float | None) -> list[dict]:
    ref = ctx.ref
    d2 = lane["destination"]["country"]
    lines = []
    for b in rfq["basket"]:
        fl = set()
        if b.get("contains_lithium_battery"):
            fl.add("contains_lithium_battery")
        if b.get("wireless"):
            fl.add("wireless")
        lines.append({"hs": b["hs"], "flags": fl})
    out = compliance.hs_flags(ref, d2, lines, set(), set())
    out += compliance.parcel_regime_flags(ref, d2, annual_lvg_sales_myr if d2 == "MY" else None)
    return out


def _parcel_taxes(ctx: Ctx, calc: Calc, rfq: dict, dest: str, channel: str, counts: dict, prefix: str) -> list[float]:
    """Adds duty / consumption tax / income tax lines per basket category and returns the Python totals
    from duties.parcel_taxes for a build-time consistency check."""
    ship = float(rfq["service"].get("shipping_charged_per_parcel", 0.0))
    reg = bool(rfq["service"].get("seller_registered_my_lvg", False))
    expected = []
    for b in rfq["basket"]:
        cat = b["category"]
        tr = duties.parcel_taxes(ctx.ref, dest, channel, b["hs"], b["retail_usd"], ship, reg)
        expected.append(tr.total * counts[cat])
        N = calc.input(f"N_{cat}", counts[cat], f"Parcels per year: {cat}", f"年包裹数：{cat}", "parcel")
        CV = calc.input(f"CVP_{cat}", b["retail_usd"] + ship, f"Customs value per parcel: {cat} (price + shipping)",
                        f"每包裹完税价格：{cat}（售价 + 运费）", "USD")
        RET = calc.input(f"RETAIL_{cat}", b["retail_usd"], f"Retail price per parcel: {cat}", f"每包裹零售价：{cat}", "USD")
        r_d = _regime_rate(ctx, f"regime.{dest}.{channel}.{b['hs']}.duty", tr.duty_rate, tr.statements,
                           f"Duty rate {dest} {b['hs']} ({tr.regime})", f"关税率 {dest} {b['hs']}（{tr.regime}）")
        duty = ctx.line(calc, f"{prefix}DUTY_{cat}", mul(N, CV, r_d), f"Import duty: {cat}", f"进口关税：{cat}",
                        "duties_taxes", group="duty", note=tr.regime)
        r_t = _regime_rate(ctx, f"regime.{dest}.{channel}.{b['hs']}.tax", tr.tax_rate, tr.statements,
                           f"Consumption tax rate {dest} ({tr.regime})", f"消费税率 {dest}（{tr.regime}）")
        if tr.regime.startswith("MY LVG"):
            base = mul(N, RET)                       # LVG sales tax on the sale price, excluding transport
        else:
            base = add(mul(N, CV), duty)              # VAT / sales tax on customs value + duty
        ctx.line(calc, f"{prefix}CTAX_{cat}", mul(r_t, base), f"Consumption tax: {cat}", f"消费税：{cat}",
                 "duties_taxes", group="tax", note=tr.regime)
        if tr.income_tax:
            r_p = _regime_rate(ctx, f"regime.{dest}.pph", float(ctx.ref.get("regimes.ID.pph_specific_rate")), ["ID-CN-BAND"],
                               "Indonesian income tax (PPh) on listed consignments", "印尼特定快件所得税（PPh）")
            ctx.line(calc, f"{prefix}PPH_{cat}", mul(r_p, add(mul(N, CV), duty)), f"Income tax (PPh): {cat}",
                     f"所得税（PPh）：{cat}", "duties_taxes", group="tax", note=tr.regime)
    return expected


def build_lane(ctx: Ctx, lane: dict, rfq: dict, lane_flag_list: list[dict]) -> dict:
    ref = ctx.ref
    o, d = lane["origin"], lane["destination"]
    o2, d2 = o["country"], d["country"]
    o3, d3 = ISO3[o2], ISO3[d2]
    basket = rfq["basket"]
    prof = rfq["monthly_profile"]
    P = float(lane["parcels_per_month"]) * 12.0
    counts = {b["category"]: P * b["share"] for b in basket}
    vol = float(ref.get("rates.air.volumetric_kg_per_cbm"))
    actual_kg = sum(counts[b["category"]] * b["kg"] for b in basket)
    chg_kg = sum(counts[b["category"]] * max(b["kg"], b["cbm"] * vol) for b in basket)
    cube = float(ref.get("rates.local_fulfilment.carton_cube_factor"))
    cbm_year = sum(counts[b["category"]] * b["cbm"] for b in basket) * cube
    n_risk = compliance.hold_flag_count(ref, lane_flag_list)
    options, excluded = [], []
    target = float(lane["target_transit_days"])

    for mode in lane["modes"]:
        if mode in ("rail", "road"):
            svc = _service(ctx, mode, o2, d2)
            if svc is None or svc["status"] != "verified":
                excluded.append({"mode": mode, "reason_en": "no verified scheduled service for this lane",
                                 "reason_zh": "该线路无经核实的定期班次", "statements": svc["statements"] if svc else []})
                continue
        if mode == "sea_air":
            hub = "SIN"
            direct = ref.air_km(o["airport"], d["airport"])
            via = ref.air_km(o["airport"], hub) + ref.air_km(hub, d["airport"])
            ratio = via / direct
            if ratio > DETOUR_LIMIT:
                excluded.append({"mode": mode, "reason_en": f"Singapore hub is off-route: via-hub distance is {ratio:.1f}x the direct distance (limit {DETOUR_LIMIT}x)",
                                 "reason_zh": f"新加坡中转绕行过远：经中转距离为直达的 {ratio:.1f} 倍（上限 {DETOUR_LIMIT} 倍）",
                                 "statements": []})
                continue
        calc = Calc(f"{lane['id']}.{mode}", ctx.ratebook)
        PARCELS = calc.input("PARCELS", P, "Parcels per year", "年包裹数", "parcel")
        quantities = {"parcels_per_year": P, "actual_kg_per_year": actual_kg, "chargeable_kg_per_year": chg_kg}
        to_border = []
        goods_nodes = {}
        channel = "air_courier"
        if mode in ("air_parcel", "sea_air", "rail", "road"):
            AKG = calc.input("ACTUAL_KG", actual_kg, "Actual kg per year", "年实际重量（公斤）", "kg")
            ctx.line(calc, "FIRST_MILE", mul(AKG, ctx.rate(f"rates.parcel.first_mile_per_kg.{o2}", f"First mile per kg ({o2})", f"头程揽收每公斤（{o2}）")),
                     "First-mile collection and sort", "头程揽收与分拣", "pre_carriage")
            ctx.line(calc, "EXPORT_CLR", mul(PARCELS, ctx.rate(f"rates.parcel.export_clearance_per_parcel.{o2}", f"Export clearance per parcel ({o2})", f"出口清关每包裹（{o2}）")),
                     "Export clearance (e-commerce)", "出口清关（跨境电商）", "export_clearance")
        if mode == "air_parcel":
            KG = calc.input("CHG_KG", chg_kg, "Chargeable kg per year", "年计费重量（公斤）", "kg")
            key = f"{o['airport']}-{d['airport']}"
            ctx.line(calc, "HANDLING_O", mul(KG, ctx.rate("rates.air.handling_origin_per_kg", "Origin airport handling per kg", "起运机场操作费每公斤")),
                     "Origin airport handling", "起运机场操作", "origin_terminal_handling")
            ctx.line(calc, "MAIN", mul(KG, ctx.rate(f"rates.air.per_kg.{key}", f"Air freight {key} per kg", f"空运费 {key} 每公斤")),
                     f"Air line-haul {key}", f"空运干线 {key}", "main_carriage")
            ctx.line(calc, "HANDLING_D", mul(KG, ctx.rate("rates.air.handling_destination_per_kg", "Destination airport handling per kg", "目的机场操作费每公斤")),
                     "Destination airport handling", "目的机场操作", "destination_terminal_handling")
            legs = [L.tri("first mile", ref, "transit.parcel.first_mile_days")] + L.air_main(ref, o["airport"], d["airport"], d3)
        elif mode == "sea_air":
            WM = calc.input("WM", cbm_year, "Freight tonnes (W/M) on the sea leg per year", "海运段年计费吨", "W/M")
            KG = calc.input("CHG_KG", chg_kg, "Chargeable kg on the air leg per year", "空运段年计费重量", "kg")
            ctx.line(calc, "CFS_O", mul(WM, ctx.rate("rates.ocean_lcl.cfs_origin_per_wm", "Origin CFS per W/M", "起运港集拼站费每计费吨")),
                     "Origin CFS", "起运港集拼站", "origin_terminal_handling")
            ctx.line(calc, "MAIN_SEA", mul(WM, ctx.rate("rates.ocean_lcl.freight_per_wm.CN-SEA", "LCL ocean freight per W/M (China-SE Asia)", "拼箱海运费每计费吨（中国—东南亚）")),
                     "Sea leg to Singapore (LCL)", "海运至新加坡（拼箱）", "main_carriage")
            ctx.line(calc, "HUB", mul(AKG, ctx.rate("rates.parcel.sg_hub_transfer_per_kg", "Singapore hub transfer per kg", "新加坡中转操作每公斤")),
                     "Singapore hub transfer (sea to air)", "新加坡中转（海转空）", "main_carriage")
            key = f"SIN-{d['airport']}"
            ctx.line(calc, "MAIN_AIR", mul(KG, ctx.rate(f"rates.air.per_kg.{key}", f"Air freight {key} per kg", f"空运费 {key} 每公斤")),
                     f"Air leg {key}", f"空运段 {key}", "main_carriage")
            ctx.line(calc, "HANDLING_D", mul(KG, ctx.rate("rates.air.handling_destination_per_kg", "Destination airport handling per kg", "目的机场操作费每公斤")),
                     "Destination airport handling", "目的机场操作", "destination_terminal_handling")
            legs = [L.tri("first mile", ref, "transit.parcel.first_mile_days"),
                    L.tri("LCL consolidation", ref, "transit.sea.lcl_consolidation_days"),
                    L.container_export_dwell(ref, o3),
                    L.wait("wait for weekly sailing", float(ref.get("transit.sea.headway_days")), "transit.sea.headway_days"),
                    L.sailing(ref, o["port"], "SGSIN"),
                    L.tri("Singapore hub transfer", ref, "transit.sea_air.hub_transfer_days"),
                    L.wait("wait for flight", float(ref.get("transit.air.headway_days")), "transit.air.headway_days"),
                    L.flight(ref, "SIN", d["airport"]),
                    L.air_import_dwell(ref, d3)]
        elif mode == "rail":
            channel = "rail"
            cap = float(ref.get("rates.container.feu_usable_cbm")) * float(ref.get("rates.container.fill_factor"))
            S = 4
            feu_by_month = [ceil_div(cbm_year * m / 12.0 / S, cap) for m in prof]
            feu = sum(S * n for n in feu_by_month)
            quantities["feu_per_year"] = feu
            FEU = calc.input("FEU", feu, "40ft containers per year (weekly consolidation)", "年 40 尺箱量（每周集拼）", "FEU")
            ctx.line(calc, "TRUCK_KMG", mul(FEU, ctx.rate("rates.rail.shenzhen_kunming_truck_feu", "Truck Shenzhen-Kunming per 40ft", "深圳—昆明公路每 40 尺")),
                     "Truck Shenzhen to Kunming rail terminal", "深圳至昆明铁路场站公路运输", "pre_carriage")
            ctx.line(calc, "RAIL", mul(FEU, ctx.rate("rates.rail.kunming_bangkok_feu", "Rail Kunming-Bangkok per 40ft incl. transload", "昆明—曼谷铁路每 40 尺（含换装）")),
                     "China-Laos-Thailand rail incl. gauge transfer", "中老泰铁路（含换装）", "main_carriage")
            ctx.line(calc, "IMPORT_DECL", mul(FEU, ctx.rate(f"rates.handling.import_declaration.{d2}", f"Import declaration ({d2})", f"进口报关（{d2}）")),
                     "Import declaration per container", "每柜进口报关", "import_clearance")
            lo, mo, hi = ref.triangular("transit.rail.clr_block_days")
            legs = [L.tri("first mile", ref, "transit.parcel.first_mile_days")] + L.truck("truck to Kunming", ref, 1450.0) + [
                L.wait("wait for train", float(ref.get("transit.rail.clr_headway_days")), "transit.rail.clr_headway_days"),
                L.leg("rail Kunming-Vientiane South-Nong Khai incl. gauge transfer", "triangular", low=lo, mode=mo, high=hi,
                      source="transit.rail.clr_block_days"),
                L.tri("Thai border clearance + rail to Bangkok", ref, "transit.rail.th_rail_border_days")]
        elif mode == "road":
            channel = "road"
            dep = ctx.fixed("assumption.road_departures_per_year", 312.0, "Consolidated truck departures per year (6 a week)",
                            "年集拼发车次数（每周 6 班）", "ASSUMPTION", "departures")
            ctx.line(calc, "ROAD", mul(AKG, ctx.rate("rates.truck.cross_border_sg_my_per_kg", "Cross-border consolidated trucking per kg", "跨境集拼陆运每公斤")),
                     "Cross-border trucking Singapore-Malaysia", "新马跨境陆运", "main_carriage")
            ctx.line(calc, "IMPORT_DECL", mul(dep, ctx.rate(f"rates.handling.import_declaration.{d2}", f"Import declaration ({d2})", f"进口报关（{d2}）")),
                     "Import declaration per truck (K1)", "每车进口报关（K1）", "import_clearance")
            legs = [L.tri("first mile", ref, "transit.parcel.first_mile_days")] + L.truck("cross-border truck", ref, float(lane["road_km"])) + [
                L.tri("Woodlands/Tuas border clearance", ref, "transit.truck.cross_border_sg_my_days")]
        elif mode == "ocean_bulk_local":
            channel = None
            cap = float(ref.get("rates.container.feu_usable_cbm")) * float(ref.get("rates.container.fill_factor"))
            weeks = 52.0
            use_fcl = cbm_year / weeks >= 0.5 * cap
            SHP = calc.input("SHIPMENTS", weeks, "Replenishment shipments per year (weekly)", "年补货票数（每周）", "shipment")
            KM = calc.input("KM_DC", LOCAL_DC_KM, "Port to local fulfilment centre", "港口至本地履约中心距离", "km")
            if use_fcl:
                feu = sum(4 * ceil_div(cbm_year * m / 12.0 / 4, cap) for m in prof)
                quantities["feu_per_year"] = feu
                FEU = calc.input("FEU", feu, "40ft containers per year", "年 40 尺箱量", "FEU")
                base = ctx.rate("rates.truck.feu_base", "Truck per 40ft move: fixed part", "40 尺拖车：固定部分")
                per_km = ctx.rate("rates.truck.feu_per_km", "Truck per 40ft move: per km", "40 尺拖车：每公里")
                to_border.append(ctx.line(calc, "PICKUP", mul(FEU, add(base, mul(per_km, KM))), "Pickup at origin warehouse", "起运仓提货", "pre_carriage"))
                to_border.append(ctx.line(calc, "THC_O", mul(FEU, ctx.rate(f"rates.handling.thc_origin_feu.{o2}", f"Origin THC per 40ft ({o2})", f"起运港码头操作费每 40 尺（{o2}）")),
                                          "Origin terminal handling", "起运港码头操作", "origin_terminal_handling"))
                to_border.append(ctx.line(calc, "MAIN", mul(FEU, ctx.rate(f"rates.ocean_fcl_feu.{o['port']}-{d['port']}", f"Ocean freight {o['port']}-{d['port']} per 40ft", f"海运费 {o['port']}-{d['port']} 每 40 尺")),
                                          "Ocean freight", "海运费", "main_carriage"))
                ctx.line(calc, "THC_D", mul(FEU, ctx.rate(f"rates.handling.thc_destination_feu.{d2}", f"Destination THC per 40ft ({d2})", f"目的港码头操作费每 40 尺（{d2}）")),
                         "Destination terminal handling", "目的港码头操作", "destination_terminal_handling")
                ctx.line(calc, "DELIVERY_DC", mul(FEU, add(base, mul(per_km, KM))), "Delivery to local fulfilment centre", "送至本地履约中心", "on_carriage")
                repl_legs = L.truck("pickup", ref, LOCAL_DC_KM) + L.ocean_main(ref, o3, o["port"], d3, d["port"])
            else:
                WMv = calc.input("WM", cbm_year, "Freight tonnes (W/M) per year", "年计费吨", "W/M")
                lbase = ctx.rate("rates.truck.light_base", "Light truck per shipment: fixed part", "轻型货车每票：固定部分")
                lper = ctx.rate("rates.truck.light_per_km", "Light truck per shipment: per km", "轻型货车每票：每公里")
                lane_key = "SG-SEA" if o2 == "SG" else "CN-SEA"
                to_border.append(ctx.line(calc, "PICKUP", mul(SHP, add(lbase, mul(lper, KM))), "Pickup at origin warehouse", "起运仓提货", "pre_carriage"))
                to_border.append(ctx.line(calc, "CFS_O", mul(WMv, ctx.rate("rates.ocean_lcl.cfs_origin_per_wm", "Origin CFS per W/M", "起运港集拼站费每计费吨")),
                                          "Origin CFS", "起运港集拼站", "origin_terminal_handling"))
                to_border.append(ctx.line(calc, "MAIN", mul(WMv, ctx.rate(f"rates.ocean_lcl.freight_per_wm.{lane_key}", f"LCL ocean freight per W/M ({lane_key})", f"拼箱海运费每计费吨（{lane_key}）")),
                                          "LCL ocean freight", "拼箱海运费", "main_carriage"))
                ctx.line(calc, "CFS_D", mul(WMv, ctx.rate("rates.ocean_lcl.cfs_destination_per_wm", "Destination CFS per W/M", "目的港集拼站费每计费吨")),
                         "Destination CFS", "目的港集拼站", "destination_terminal_handling")
                ctx.line(calc, "DELIVERY_DC", mul(SHP, add(lbase, mul(lper, KM))), "Delivery to local fulfilment centre", "送至本地履约中心", "on_carriage")
                repl_legs = (L.truck("pickup", ref, LOCAL_DC_KM) + [L.tri("LCL consolidation", ref, "transit.sea.lcl_consolidation_days")]
                             + L.ocean_main(ref, o3, o["port"], d3, d["port"])
                             + [L.tri("LCL deconsolidation", ref, "transit.sea.lcl_deconsolidation_days")])
            ctx.line(calc, "EXPORT_DECL", mul(SHP, ctx.rate(f"rates.handling.export_declaration.{o2}", f"Export declaration ({o2})", f"出口报关（{o2}）")),
                     "Export declaration", "出口报关", "export_clearance")
            ctx.line(calc, "IMPORT_DECL", mul(SHP, ctx.rate(f"rates.handling.import_declaration.{d2}", f"Import declaration ({d2})", f"进口报关（{d2}）")),
                     "Import declaration (formal entry)", "进口报关（一般贸易）", "import_clearance")
            repl_legs = repl_legs + [L.customs_hold(ref, n_risk)] + L.truck("delivery to fulfilment centre", ref, LOCAL_DC_KM)
            rm, _ = run_transit(repl_legs, ctx, 999.0, rfq["rfq_id"], lane["id"], mode, "replenishment")
            quantities["replenishment_mean_days"] = rm["mean"]
            quantities["replenishment_p90_days"] = rm["p90"]
            # goods value at transfer price and duties/taxes on bulk import
            for b in basket:
                goods_nodes[b["category"]] = calc.input(f"GOODS_{b['category']}", counts[b["category"]] * b["cost_usd"],
                                                        f"Stock value at transfer price: {b['category']}", f"按转移价计的货值：{b['category']}", "USD", "goods")
            GOODS = calc.calc("GOODS_TOTAL", add(*goods_nodes.values()), "Stock value total", "货值合计", group="goods")
            freight = add(*to_border)
            for b in basket:
                cat = b["category"]
                gi = goods_nodes[cat]
                tr = duties.bulk_import_taxes(ref, d2, b["hs"], b["cost_usd"], b["retail_usd"])
                cv = calc.calc(f"CV_{cat}", add(gi, mul(div(gi, GOODS), freight)), f"Customs value {cat} (CIF)", f"完税价格 {cat}（CIF）", group="info")
                r_d = _regime_rate(ctx, f"regime.{d2}.bulk.{b['hs']}.duty", tr.duty_rate, tr.statements,
                                   f"Duty rate {d2} {b['hs']} (bulk import)", f"关税率 {d2} {b['hs']}（批量进口）")
                duty = ctx.line(calc, f"DUTY_{cat}", mul(r_d, cv), f"Import duty: {cat}", f"进口关税：{cat}", "duties_taxes", group="duty", note=tr.regime)
                r_t = _regime_rate(ctx, f"regime.{d2}.bulk.{b['hs']}.tax", tr.tax_rate, tr.statements,
                                   f"Consumption tax rate {d2} (bulk route)", f"消费税率 {d2}（备货模式）")
                if d2 == "MY":
                    base = add(cv, duty)
                else:
                    N = calc.input(f"N_{cat}", counts[cat], f"Units sold per year: {cat}", f"年销量：{cat}", "unit")
                    RET = calc.input(f"RETAIL_{cat}", b["retail_usd"], f"Retail price: {cat}", f"零售价：{cat}", "USD")
                    base = mul(N, RET)
                ctx.line(calc, f"CTAX_{cat}", mul(r_t, base), f"Consumption tax: {cat}", f"消费税：{cat}", "duties_taxes", group="tax", note=tr.regime)
            # local fulfilment
            safety = float(ref.get("rates.economics.safety_stock_days_local"))
            avg_cbm = cbm_year / 365.0 * (safety + 3.5)
            STOCK = calc.input("AVG_STOCK_CBM", avg_cbm, "Average stock volume at the fulfilment centre", "履约中心平均库存体积", "m3")
            ctx.line(calc, "STORAGE", mul(STOCK, ctx.rate("rates.local_fulfilment.storage_per_cbm_month", "Storage per m3 per month", "仓储费每立方米每月"), C(12.0)),
                     "Storage at local fulfilment centre", "本地履约中心仓储", None, group="logistics")
            ctx.line(calc, "PICK_PACK", mul(PARCELS, ctx.rate("rates.local_fulfilment.pick_pack_per_parcel", "Pick and pack per parcel", "拣货包装每包裹")),
                     "Pick and pack", "拣货与包装", None, group="logistics")
            DAYS = calc.input("STOCK_DAYS", rm["mean"] + safety + 3.5, "Days of stock held (pipeline + safety + half cycle)", "库存天数（在途 + 安全库存 + 半个周期）", "days")
            ctx.line(calc, "CARRYING", mul(GOODS, ctx.rate("rates.economics.carrying_cost_pa", "Inventory carrying cost per year", "库存资金占用年费率"), div(DAYS, C(365.0))),
                     "Inventory carrying cost (pipeline and local stock)", "库存资金占用（在途及本地库存）", None, group="economic")
            legs = [L.tri("pick and pack at local fulfilment centre", ref, "transit.parcel.local_dispatch_days")]
        else:
            raise ValueError(f"unsupported parcel mode {mode}")

        if mode != "ocean_bulk_local":
            ctx.line(calc, "IMPORT_CLR", mul(PARCELS, ctx.rate(f"rates.parcel.destination_clearance_per_parcel.{d2}", f"Destination clearance per parcel ({d2})", f"目的地清关每包裹（{d2}）")),
                     "Destination clearance (B2C)", "目的地清关（B2C）", "import_clearance")
            expected = _parcel_taxes(ctx, calc, rfq, d2, channel, counts, "")
            legs = legs + [L.customs_hold(ref, n_risk)]
        ctx.line(calc, "LAST_MILE", mul(PARCELS, ctx.rate(f"rates.parcel.last_mile_per_parcel.{d2}", f"Last mile per parcel ({d2})", f"尾程派送每包裹（{d2}）")),
                 "Last-mile delivery", "尾程派送", "on_carriage")
        for key, pid, en, zh in (("relabel", "rates.vas.relabel_per_parcel", "Relabelling", "换标"),
                                 ("parcel_pack", "rates.vas.parcel_pack_per_parcel", "Parcel packing", "包裹打包")):
            if key in rfq["service"]["vas"] and not (mode == "ocean_bulk_local" and key == "parcel_pack"):
                ctx.line(calc, f"VAS_{key.upper()}", mul(PARCELS, ctx.rate(pid, en + " per parcel", zh + "每包裹")), en, zh, None, group="vas")
        lm = ref.triangular(f"transit.parcel.last_mile_days.{d2}")
        legs = legs + [L.leg(f"last mile ({d2})", "triangular", low=lm[0], mode=lm[1], high=lm[2],
                             source=f"transit.parcel.last_mile_days.{d2}")]
        tm, _ = run_transit(legs, ctx, target, rfq["rfq_id"], lane["id"], mode)
        if mode != "ocean_bulk_local":
            for b in basket:
                goods_nodes[b["category"]] = calc.input(f"GOODS_{b['category']}", counts[b["category"]] * b["cost_usd"],
                                                        f"Goods value at cost: {b['category']}", f"按成本计的货值：{b['category']}", "USD", "goods")
            GOODS = calc.calc("GOODS_TOTAL", add(*goods_nodes.values()), "Goods value total (cost)", "货值合计（成本）", group="goods")
            MEAN = calc.input("MEAN_TRANSIT_DAYS", tm["mean"], "Mean door-to-door days (simulated)", "平均门到门天数（模拟）", "days")
            ctx.line(calc, "CARRYING", mul(GOODS, ctx.rate("rates.economics.carrying_cost_pa", "Inventory carrying cost per year", "库存资金占用年费率"), div(MEAN, C(365.0))),
                     "In-transit inventory carrying cost", "在途库存资金占用", None, group="economic")
        totals_nodes = add_totals(calc, PARCELS, "parcel")
        totals = {k: calc.value(e[1]) for k, e in totals_nodes.items()}
        if mode != "ocean_bulk_local":
            got = totals["duty"] + totals["tax"]
            want = sum(expected)
            if abs(got - want) > 1e-6 * max(1.0, abs(want)):
                raise AssertionError(f"parcel tax formulas diverge from duties.parcel_taxes: {got} vs {want}")
        opt_flags = compliance.flags_for_option(lane_flag_list, mode, mode)
        if mode == "ocean_bulk_local":
            opt_flags = opt_flags + [
                compliance.flag("BULK-IOR", "medium",
                                "Bulk import needs a local importer of record (own entity or appointed importer) with the destination tax registrations; local stock adds forecast and obsolescence risk.",
                                "批量进口须有当地进口登记人（自设主体或指定进口商）及相应税务登记；本地备货另增预测与滞销风险。",
                                "Decide the importer-of-record model before launch; start with the fastest-moving SKUs.",
                                "上线前确定进口登记人模式；先从周转最快的 SKU 开始备货。", [])]
        if mode == "rail":
            opt_flags = opt_flags + [compliance.flag("RAIL-FREQUENCY", "low",
                                                     "China-Laos-Thailand rail corridor verified on an official Lao source, but departure frequency from Kunming is an assumption.",
                                                     "中老泰铁路通道已经老挝官方来源核实，但昆明始发频率为假设。",
                                                     "Confirm weekly departures and cut-offs with the rail operator before committing volume.",
                                                     "承诺货量前向铁路运营方确认每周班次与截止时间。", ["SVC-CLR-TH"])]
        risk = compliance.risk_score(ref, opt_flags, tm["p50"], tm["p90"], HANDOFFS[mode], False)
        label_en, label_zh = option_label(mode)
        options.append({"id": f"{lane['id']}-{mode}", "mode": mode, "regime": None, "label_en": label_en, "label_zh": label_zh,
                        "quantities": quantities, "legs": legs, "transit": tm, "totals": totals, "costs": calc.table(),
                        "flags": opt_flags, "risk": risk, "handoffs": HANDOFFS[mode], "_calc": calc})
    return {"options": options, "excluded": excluded}
