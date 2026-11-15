"""Bilingual solution proposal (Markdown) generated from a template's results."""
from __future__ import annotations

from .plan import ROLES, kpis, plan

SEV_ZH = {"info": "提示", "low": "低", "medium": "中", "high": "高", "block": "阻断"}
STATUS_ZH = {"verified": "已核实", "corrected": "已更正", "not_verified": "未核实"}
UNIT_ZH = {"kit": "套", "move": "次往返", "parcel": "个包裹"}
FLOW_EN = {"b2b_import": "B2B import", "temporary": "temporary moves", "b2c_parcel": "B2C parcels"}
FLOW_ZH = {"b2b_import": "B2B 进口", "temporary": "临时进出境运输", "b2c_parcel": "B2C 跨境包裹"}
ROLE_EN = {"buyer": "buyer", "seller": "seller", "owner": "owner of the goods"}
ROLE_ZH = {"buyer": "买方", "seller": "卖方", "owner": "货物所有人"}
REGIME_ZH = {
    "MY LVG + air-courier de minimis": "马来西亚低价值货物销售税 + 空运快件低值豁免",
    "MY LVG, duty at import (no de minimis by road/sea)": "马来西亚低价值货物销售税；陆运/海运入境照征关税",
    "MY general import": "马来西亚一般进口",
    "ID consignment <= USD 3": "印尼快件（≤3 美元）",
    "ID consignment USD 3-1,500": "印尼快件（3–1,500 美元）",
    "ID above USD 1,500 (placeholder MFN)": "印尼快件（>1,500 美元，占位最惠国税率）",
    "TH exempt (<= 1 baht)": "泰国（≤1 泰铢免税）",
    "TH dutiable from 1 Jan 2026 (placeholder MFN)": "泰国 2026 年起全额征税（占位最惠国税率）",
    "PH de minimis (FOB <= PHP 10,000)": "菲律宾低值豁免（FOB ≤10,000 比索）",
    "PH above de minimis (placeholder MFN)": "菲律宾超出低值豁免（占位最惠国税率）",
}


def _esc(text: str) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ")


def _usd(x: float, zh: bool = False) -> str:
    s = f"{x:,.2f}" if abs(x) < 100 else f"{x:,.0f}"
    return f"{s} 美元" if zh else f"USD {s}"


def _pct(x: float) -> str:
    return f"{x * 100:.0f}%"


def _pct1(x: float) -> str:
    return f"{x * 100:.1f}%"


def _table(header: list[str], rows: list[list]) -> str:
    out = ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    out += ["| " + " | ".join(_esc(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def _ver(v, zh: bool) -> str:
    if v is None:
        return "—"
    return ("是" if v else "否") if zh else ("yes" if v else "no")


def _chosen(lane: dict) -> dict:
    return next(o for o in lane["options"] if o["id"] == lane["recommendation"]["chosen"])


def _key_findings(res: dict, zh: bool) -> list[str]:
    flow = res["rfq"]["flow_type"]
    out = []
    if flow == "b2b_import":
        mfn = sum(r["mfn_rate"] * r["annual_goods_value"] for ln in res["lanes"] for r in ln["extra"]["fta"])
        chosen = sum(r["chosen"]["rate"] * r["annual_goods_value"] for ln in res["lanes"] for r in ln["extra"]["fta"])
        lost = [(r["sku"], r["hs"], r["saving_if_qualified"]) for ln in res["lanes"] for r in ln["extra"]["fta"]
                if r["chosen"]["scheme"] == "MFN" and r["saving_if_qualified"] > 0]
        if zh:
            out.append(f"按商品货值估算，适用 ACFTA 后年度关税由最惠国口径的约 {_usd(mfn, True)}降至约 {_usd(chosen, True)}；"
                       "RCEP 对这些税目的现行税率高于 ACFTA，因此优先使用 Form E。")
            for sku, hs, amt in lost:
                out.append(f"{sku}（{hs}）原产地未达标（区域价值成分低于 40% 且不满足品目改变），按最惠国税率计税；补齐原产地证据后每年可争取约 {_usd(amt, True)}的关税减免。")
        else:
            out.append(f"On goods value, ACFTA cuts annual duty from about {_usd(mfn)} (MFN) to about {_usd(chosen)}; "
                       "RCEP's current rates for these lines are higher than ACFTA's, so Form E is the instrument of choice.")
            for sku, hs, amt in lost:
                out.append(f"{sku} ({hs}) does not qualify for origin (RVC below 40% and no change of heading), so MFN applies; "
                           f"about {_usd(amt)} a year of duty depends on documenting more regional content.")
        if zh:
            out.append("零部件按 87.08 等税目申报无需 MITI 核准准证，但若整批散件构成基本完整的车辆，可能被归入 CKD 整车税目并需 AP，建议先取得归类裁定。")
            out.append("经泰国、老挝至中国的中马铁路班列 2024 年首发后未找到现行官方时刻表，本方案未将其纳入可选方案。")
        else:
            out.append("Parts declared under 87.08 and similar headings need no MITI Approved Permit, but a set that amounts to an essentially "
                       "complete vehicle could be classified as a CKD vehicle needing an AP; a classification ruling comes first.")
            out.append("The Malaysia-China block train via Thailand and Laos made a first run in 2024, but no current official timetable "
                       "was found, so it is not offered.")
    elif flow == "temporary":
        if zh:
            out += ["新加坡海关只在展会、专业设备和科学设备三类用途下接受外国 ATA 单证册，商业样品与维修均不在其列；维修类运输改用 TIS 或出境维修临时出口。",
                    "新加坡本地 ATA 单证册由新加坡国际商会（SICC）签发，SICC 是新加坡的 ATA 担保与签发机构。",
                    "半导体制造设备及其专门设计的部件可能列入战略物资管制清单 3B001 类，从新加坡出口或复出口前须取得 XO/XP 许可证（至少提前 5 个工作日），使用 ATA 单证册也不例外。",
                    "TIS 担保额按潜在 GST 的 30%（已注册 GST 企业）计，仅覆盖新加坡一侧；起运国的临时出口与复进口须另行办理。"]
        else:
            out += ["Singapore Customs accepts foreign ATA Carnets only for exhibitions, professional equipment and scientific equipment; "
                    "commercial samples and repair are not covered, so repair loops use the TIS or temporary export for repair.",
                    "Local ATA Carnets in Singapore are issued by the Singapore International Chamber of Commerce (SICC), Singapore's "
                    "National Guaranteeing and Issuing Association.",
                    "Semiconductor manufacturing equipment and specially designed parts may be strategic goods (control list 3B001); export or "
                    "re-export from Singapore then needs an XO/XP permit applied for at least 5 working days ahead, carnet or not.",
                    "TIS security is 30% of the potential GST for a GST-registered entity and covers only the Singapore side; the origin "
                    "country's temporary export and re-import are separate."]
    else:
        if zh:
            out += ["马来西亚：售价不超过 500 林吉特的低价值货物须由注册卖家按售价收取 10% 销售税；批量进口则按 CIF 加关税缴纳一次性销售税，税基更低。",
                    "印尼：快件超过 FOB 3 美元即征税，服装、箱包按 25% 关税加 5% 所得税，另征实际税负 11% 的增值税，跨境直邮税负明显高于本地备货。",
                    "泰国：自 2026 年 1 月 1 日起仅单件价值不超过 1 泰铢的货物免税，包裹一律征收关税和 7% 增值税（本文关税税率为未核实的占位值）。",
                    "菲律宾：FOB 不超过 10,000 比索的包裹免征关税和税费，跨境直邮税负最低，但 7 天时效达标率不足。",
                    "新加坡：经空运或邮寄进口、售价不超过 400 新元的低价值货物自 2023 年 1 月 1 日起由 OVR 注册卖家征收 GST；本方案无新加坡目的地线路，仅作对照。"]
        else:
            out += ["Malaysia: low-value goods sold at up to RM500 carry 10% sales tax on the sale price, charged by the registered seller; "
                    "bulk imports pay single-stage sales tax on CIF plus duty, a lower base.",
                    "Indonesia: consignments above FOB USD 3 are taxed; apparel and bags pay 25% duty plus 5% income tax, plus VAT at an "
                    "effective 11%, so parcels carry a much higher tax load than local stock.",
                    "Thailand: since 1 January 2026 only items worth up to 1 baht are duty-free, so every parcel pays duty and 7% VAT "
                    "(the duty rates used here are unverified placeholders).",
                    "Philippines: parcels up to PHP 10,000 FOB pay no duties or taxes, the lightest tax load, but parcels miss the 7-day target.",
                    "Singapore: low-value goods (sale value up to S$400, by air or post) bear GST collected by OVR-registered vendors since "
                    "1 January 2023; no lane here ends in Singapore, so it is shown for comparison only."]
    return out


def render(res: dict, lang: str, statements: dict, sources: dict) -> str:
    zh = lang == "zh"
    rfq = res["rfq"]
    flow = rfq["flow_type"]
    L: list[str] = []
    title = rfq["title_zh"] if zh else rfq["title_en"]
    L.append(f"# {title}")
    L.append("")
    if zh:
        L.append(f"**询价编号** {rfq['rfq_id']} · **客户** {rfq['customer'].replace(' (fictional)', '（虚构客户）')} · **出具日期** {rfq['issue_date']} · "
                 f"**报价有效期** {rfq['quote_validity_days']} 天 · **币种** {rfq['currency']}")
        L.append("")
        L.append("> 本文为个人作品集示例：客户为虚构；运费及操作费为**示意值**（非任何承运人或货代运价）；关税与税费仅在标注“已核实”处采用官方税率；"
                 "法规表述已于 2026-11-15 对照官方来源核查（见《法规核查记录》）。本文不构成税务或法律意见。")
    else:
        L.append(f"**RFQ** {rfq['rfq_id']} · **Customer** {rfq['customer']} · **Issued** {rfq['issue_date']} · "
                 f"**Valid** {rfq['quote_validity_days']} days · **Currency** {rfq['currency']}")
        L.append("")
        L.append("> Portfolio example: the customer is fictional; freight and handling rates are **ILLUSTRATIVE** (not any carrier's or "
                 "forwarder's tariff); duty and tax rates are official only where marked verified; regulatory statements were checked "
                 "against official sources on 2026-11-15 (see the regulatory check log). Not tax or legal advice.")
    L.append("")
    # 1 executive summary
    L.append("## 1. 执行摘要" if zh else "## 1. Executive summary")
    L.append("")
    L.append(rfq["customer_profile_zh"] if zh else rfq["customer_profile_en"])
    L.append("")
    rows = []
    for ln, s in zip(res["lanes"], res["summary"]):
        u = UNIT_ZH.get(ln["unit"], ln["unit"]) if zh else ln["unit"]
        status = ("达标" if s["status"] == "meets_target" else "未达标") if zh else ("meets target" if s["status"] == "meets_target" else "below target")
        rows.append([ln["id"], s["label_zh"] if zh else s["label_en"],
                     (f"{_usd(s['cost_per_unit'], True)}/{u}" if zh else f"{_usd(s['cost_per_unit'])}/{u}"),
                     f"{s['p90']:.1f}", (f"{_pct1(s['on_time_probability'])}（{ln['target_transit_days']} 天）" if zh else
                                          f"{_pct1(s['on_time_probability'])} ({ln['target_transit_days']} days)"), f"{s['risk']:.0f}", status])
    hdr = (["线路", "推荐方案", "落地成本", "P90（天）", "准时率（目标时效）", "风险", "状态"] if zh else
           ["Lane", "Recommended solution", "Landed cost", "P90 (days)", "On time (target)", "Risk", "Status"])
    L.append(_table(hdr, rows))
    L.append("")
    tq = sum(s["annual_quote"] for s in res["summary"])
    tl = sum(s["annual_landed"] for s in res["summary"])
    if zh:
        L.append(f"推荐方案年度报价合计约 {_usd(tq, True)}（物流、增值服务、保险及许可类费用），含关税、税费及库存资金占用的年度总落地成本约 {_usd(tl, True)}。")
    else:
        L.append(f"Recommended options: annual quotation about {_usd(tq)} (logistics, VAS, insurance, permits); total landed cost "
                 f"including duties, taxes and inventory carrying about {_usd(tl)} a year.")
    L.append("")
    L.append("**主要结论**" if zh else "**Key findings**")
    L.append("")
    for k in _key_findings(res, zh):
        L.append(f"- {k}")
    L.append("")
    # 2 requirements
    L.append("## 2. 需求概述" if zh else "## 2. Requirements")
    L.append("")
    if zh:
        place = rfq.get("incoterm_named_place_zh") or rfq["incoterm_named_place"]
        inco = f"{rfq['incoterm']}（{place}）" if rfq["incoterm"] else f"不适用（{place}）"
        L.append(f"- 业务类型：{FLOW_ZH[flow]}；贸易术语：{inco}；报价对象角色：{ROLE_ZH[rfq['quoting_party_role']]}。")
        L.append(f"- 时效要求：各线路在目标时效内送达的概率不低于 {_pct(rfq['service']['on_time_target_probability'])}；权重：成本 {rfq['priorities']['cost']}、时效 {rfq['priorities']['time']}、风险 {rfq['priorities']['risk']}。")
    else:
        inco = f"{rfq['incoterm']} ({rfq['incoterm_named_place']})" if rfq["incoterm"] else rfq["incoterm_named_place"]
        L.append(f"- Flow: {FLOW_EN[flow]}; Incoterm: {inco}; quoting to the {ROLE_EN[rfq['quoting_party_role']]}.")
        L.append(f"- Service: at least {_pct(rfq['service']['on_time_target_probability'])} of shipments within each lane's target; "
                 f"weights cost {rfq['priorities']['cost']}, time {rfq['priorities']['time']}, risk {rfq['priorities']['risk']}.")
    L.append("")
    rows = []
    for ln in res["lanes"]:
        o, d = ln["origin"], ln["destination"]
        oc = o.get("city_zh", o["city"]) if zh else o["city"]
        dc = d.get("city_zh", d["city"]) if zh else d["city"]
        rows.append([ln["id"], ln["name_zh"] if zh else ln["name_en"], f"{oc} ({o['country']}) → {dc} ({d['country']})",
                     f"{ln['target_transit_days']}"])
    L.append(_table(["线路", "说明", "起讫地", "目标时效（天）"] if zh else ["Lane", "Description", "From → to", "Target (days)"], rows))
    L.append("")
    # 3 options
    L.append("## 3. 各线路方案比选" if zh else "## 3. Options per lane")
    L.append("")
    if zh:
        L.append("成本为每单位落地成本（物流报价 + 关税及税费 + 库存资金占用）；P50/P90 为 2 万次蒙特卡洛模拟的门到门天数；风险评分为合规标记、时效离散度与交接次数的加权（0–100，越低越好）。")
    else:
        L.append("Cost is landed cost per unit (quotation + duties and taxes + inventory carrying); P50/P90 are door-to-door days from "
                 "20,000 Monte Carlo draws; the risk score adds compliance flags, transit spread and hand-offs (0-100, lower is better).")
    L.append("")
    for ln in res["lanes"]:
        L.append(f"### {ln['id']} · {ln['name_zh'] if zh else ln['name_en']}")
        L.append("")
        rows = []
        for o in ln["options"]:
            m = o["metrics"]
            mark = ("★ 推荐" if zh else "★ recommended") if o["id"] == ln["recommendation"]["chosen"] else (
                ("帕累托" if zh else "Pareto") if o["pareto"] else ("被占优" if zh else "dominated"))
            rows.append([o["label_zh"] if zh else o["label_en"], _usd(m["cost_per_unit"], zh), f"{m['p50']:.1f}", f"{m['p90']:.1f}",
                         _pct1(m["on_time_probability"]), f"{m['risk']:.0f}", mark])
        L.append(_table(["方案", "每单位落地成本", "P50", "P90", "准时率", "风险", "结论"] if zh else
                        ["Option", "Landed cost per unit", "P50", "P90", "On time", "Risk", "Result"], rows))
        L.append("")
        for line in (ln["rationale"]["zh"] if zh else ln["rationale"]["en"]):
            L.append(f"- {line}")
        L.append("")
    # 4 cost build-up
    L.append("## 4. 推荐方案费用构成（年度）" if zh else "## 4. Cost build-up of the recommended options (annual)")
    L.append("")
    for ln in res["lanes"]:
        ch = _chosen(ln)
        L.append(f"### {ln['id']} · {ch['label_zh'] if zh else ch['label_en']}")
        L.append("")
        rows = []
        units = ch["quantities"].get("units_per_year") or ch["quantities"].get("moves_per_year") or ch["quantities"].get("parcels_per_year")
        for c in ch["costs"]:
            if c["kind"] != "calc" or c["group"] in ("info", "goods", "total") or abs(c["value"]) < 1e-9:
                continue
            payer = {"buyer": "买方", "seller": "卖方", "owner": "货主"}.get(c["payer"], c["payer"]) if zh else c["payer"]
            inq = ("是" if c["in_quote"] else "否") if zh else ("yes" if c["in_quote"] else "no")
            rows.append([c["label_zh"] if zh else c["label_en"], f"{c['value']:,.0f}", f"{c['value'] / units:,.2f}", payer, inq])
        t = ch["totals"]
        rows.append(["**报价合计**" if zh else "**Quotation total**", f"{t['quote']:,.0f}", f"{t['quote'] / units:,.2f}", "", ""])
        rows.append(["**总落地成本**" if zh else "**Total landed cost**", f"{t['landed']:,.0f}", f"{t['landed'] / units:,.2f}", "", ""])
        L.append(_table(["费用项", "年度（美元）", "每单位（美元）", "承担方", "计入报价"] if zh else
                        ["Cost element", "Annual (USD)", "Per unit (USD)", "Payer", "In quote"], rows))
        L.append("")
        if t.get("seller_side", 0) > 0:
            L.append((f"按贸易术语由卖方承担、未计入本报价的费用约 {_usd(t['seller_side'], True)}（如出口报关）。" if zh else
                      f"Seller-side costs under the Incoterm, excluded from this quotation: about {_usd(t['seller_side'])} (e.g. export clearance)."))
            L.append("")
    # 5 compliance
    L.append("## 5. 合规与风险" if zh else "## 5. Compliance and risk")
    L.append("")
    if flow == "b2b_import":
        L.append("### 自贸协定原产地方案（马来西亚进口）" if zh else "### FTA origin options (imports into Malaysia)")
        L.append("")
        rows = []
        for ln in res["lanes"]:
            for r in ln["extra"]["fta"]:
                opts = {o["scheme"]: o for o in r["options"]}
                fmt = lambda o: ("—" if o["rate"] is None else f"{o['rate'] * 100:.1f}%") + ("" if o["available"] else (" (不满足)" if zh else " (not met)"))
                verdict = (("值得" if r["worth_it"] else "不适用") if zh else ("worth it" if r["worth_it"] else "n/a"))
                rows.append([ln["id"], r["sku"], r["hs"], f"{r['rvc']}%", fmt(opts["MFN"]), fmt(opts["ACFTA"]), fmt(opts["RCEP"]),
                             r["chosen"]["scheme"], f"{r['annual_saving']:,.0f}", f"{r['doc_cost']:,.0f}", verdict])
        L.append(_table(["线路", "物料", "税号", "RVC", "最惠国", "ACFTA", "RCEP", "选择", "年节省关税（美元）", "单证成本（美元）", "结论"] if zh else
                        ["Lane", "SKU", "HS", "RVC", "MFN", "ACFTA", "RCEP", "Chosen", "Annual duty saved (USD)", "Paperwork (USD)", "Verdict"], rows))
        L.append("")
        if zh:
            L.append("单证要求：ACFTA 须取得 Form E（装运前或装运时签发，一年内向进口海关提交；第三方开票时在第 10 栏填写发票号并随附发票）；RCEP 可用原产地证书或经核准出口商的原产地声明（有效期一年；第三方开票时勾选第 17 栏并在第 14 栏注明开票公司）。")
        else:
            L.append("Documents: ACFTA needs a Form E (issued before or at shipment, presented within one year; with third-party invoicing the invoice "
                     "number goes in Box 10 and the invoice is attached). RCEP accepts a certificate of origin or an approved exporter's declaration "
                     "(valid one year; with third-party invoicing tick Box 17 and name the invoicing company in Box 14).")
        L.append("")
    if flow == "temporary":
        L.append("### 临时进出境工具选择" if zh else "### Temporary-admission instrument per lane")
        L.append("")
        rows = []
        for ln in res["lanes"]:
            reg = ln["extra"]["regimes"]
            cell = lambda k: ("—" if k not in reg else (("可用" if reg[k]["available"] else "不可用") if zh else ("available" if reg[k]["available"] else "not available")))
            ch = _chosen(ln)
            rows.append([ln["id"], ln["name_zh"] if zh else ln["name_en"], cell("ata_carnet"), cell("tis"), cell("temp_export_repair"),
                         ch["label_zh"] if zh else ch["label_en"]])
        L.append(_table(["线路", "运输", "ATA 单证册", "TIS", "出境维修临时出口", "推荐"] if zh else
                        ["Lane", "Move", "ATA Carnet", "TIS", "Temporary export for repair", "Recommended"], rows))
        L.append("")
    if flow == "b2c_parcel":
        L.append("### 各目的国低价值货物税制（单件包裹，空运快件渠道）" if zh else "### Low-value regimes by destination (one-item parcel, air courier)")
        L.append("")
        rows = []
        for r in res["extra_tables"]["regime_table"]:
            p, b = r["parcel"], r["bulk"]
            rows.append([r["destination"], r["category_zh"] if zh else r["category"], f"{r['retail']:.2f}", f"{p['duty']:.2f}",
                         f"{p['consumption_tax'] + p['income_tax']:.2f}", REGIME_ZH.get(p["regime"], p["regime"]) if zh else p["regime"],
                         f"{b['duty'] + b['consumption_tax']:.2f}"])
        L.append(_table(["目的国", "品类", "售价（美元）", "包裹关税", "包裹税费", "适用规则", "本地备货税负（每件）"] if zh else
                        ["Destination", "Category", "Price (USD)", "Parcel duty", "Parcel taxes", "Rule applied", "Bulk route taxes (per unit)"], rows))
        L.append("")
        if zh:
            L.append("说明：泰国、菲律宾及印尼一般贸易项下的最惠国税率为未经核实的占位值；本地备货税负按马来西亚进口销售税或增值税国家的零售环节销项税计算。")
        else:
            L.append("Thai and Philippine MFN rates and Indonesian bulk MFN rates are unverified placeholders; bulk-route taxes are Malaysian import "
                     "sales tax or, in VAT countries, output VAT on the retail price.")
        L.append("")
    L.append("### 风险标记与应对" if zh else "### Risk flags and mitigations")
    L.append("")
    rows = []
    seen = set()
    for f in res["template_flags"]:
        rows.append(["—", SEV_ZH[f["severity"]] if zh else f["severity"], f["zh"] if zh else f["en"], f["mitigation_zh"] if zh else f["mitigation_en"],
                     _ver(f["verified"], zh)])
    for ln in res["lanes"]:
        flags = list(ln["lane_flags"]) + [f for o in ln["options"] if o["id"] == ln["recommendation"]["chosen"] for f in o["flags"]]
        for f in flags:
            key = (ln["id"], f["id"])
            if key in seen:
                continue
            seen.add(key)
            rows.append([ln["id"], SEV_ZH[f["severity"]] if zh else f["severity"], f["zh"] if zh else f["en"],
                         (f["mitigation_zh"] if zh else f["mitigation_en"]) or "—",
                         _ver(f["verified"], zh)])
    L.append(_table(["线路", "等级", "发现", "应对措施", "已核实"] if zh else ["Lane", "Severity", "Finding", "Mitigation", "Verified"], rows))
    L.append("")
    # 6 implementation plan
    pl = plan(flow)
    L.append("## 6. 实施计划" if zh else "## 6. Implementation plan")
    L.append("")
    L.append(_table(["时间", "里程碑"] if zh else ["When", "Milestone"], [[w, z if zh else e] for w, e, z in pl["milestones"]]))
    L.append("")
    L.append("**RACI**（R 执行，A 负责，C 咨询，I 知会）" if zh else "**RACI** (R responsible, A accountable, C consulted, I informed)")
    L.append("")
    L.append(_table(["工作项"] + [z for _, z in ROLES] if zh else ["Activity"] + [e for e, _ in ROLES],
                    [[z if zh else e] + codes for e, z, codes in pl["raci"]]))
    L.append("")
    # 7 KPIs and monitoring
    L.append("## 7. 关键绩效指标与上线后监控" if zh else "## 7. KPIs and post-go-live monitoring")
    L.append("")
    if zh:
        L.append("报价工作簿的“Monitoring”工作表按月录入实际值，自动计算年内均值并判定“OK / REVIEW”。目标值取自推荐方案的测算结果。")
    else:
        L.append("The quotation workbook's Monitoring sheet takes monthly actuals and computes the year-to-date average and an OK / REVIEW "
                 "status. Targets come from the recommended option's results.")
    L.append("")
    tgt = float(rfq["service"]["on_time_target_probability"])
    for ln, s in zip(res["lanes"], res["summary"]):
        rows = [[k["zh"] if zh else k["en"], f"{k['target']:g}", ("越低越好" if k["better"] == "lower" else "越高越好") if zh else k["better"],
                 k["trigger_zh"] if zh else k["trigger_en"]] for k in kpis(flow, ln, s, tgt)]
        L.append(f"**{ln['id']}**")
        L.append("")
        L.append(_table(["指标", "目标", "方向", "触发条件与行动"] if zh else ["KPI", "Target", "Better", "Trigger and action"], rows))
        L.append("")
    # 8 assumptions
    L.append("## 8. 假设与数据来源" if zh else "## 8. Assumptions and data provenance")
    L.append("")
    counts: dict[str, int] = {}
    for a in res["assumptions"]:
        counts[a["label"]] = counts.get(a["label"], 0) + 1
    if zh:
        L.append("报价工作簿“Assumptions”表列出本模板使用的全部费率与参数，按 REAL（官方或公开数据）、ASSUMPTION（建模假设或未核实占位值）、"
                 "ILLUSTRATIVE（示意费率）、SYNTHETIC（虚构询价数据）分类：" + "，".join(f"{k} {v} 项" for k, v in sorted(counts.items())) + "。")
        L.append("港口与机场滞留时间来自世界银行 LPI 2.0（2024 年数据，CC BY 4.0）；运价量级参照 Drewry 亚洲区域内集装箱指数（2026-11-12：每 40 尺 1,440 美元）及 Drewry 空运价格指数（2026 年 10 月：每公斤 4.12 美元）。完整来源表见 docs/data_provenance.md。")
    else:
        L.append("The workbook's Assumptions sheet lists every rate and parameter used by this template, labelled REAL (official or public data), "
                 "ASSUMPTION (modelling choice or unverified placeholder), ILLUSTRATIVE (example rate) or SYNTHETIC (fictional RFQ data): "
                 + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())) + ".")
        L.append("Port and airport dwell times come from the World Bank LPI 2.0 (2024, CC BY 4.0); rate levels are anchored to the Drewry "
                 "Intra-Asia Container Index (12 Nov 2026: USD 1,440 per 40ft) and the Drewry Airfreight Price Index (October 2026: "
                 "USD 4.12/kg). The full source table is in docs/data_provenance.md.")
    L.append("")
    # 9 statements
    L.append("## 9. 引用的法规表述" if zh else "## 9. Regulatory statements relied on")
    L.append("")
    L.append("以下表述均已于 2026-11-15 对照所列来源核查，核查记录见 docs/regulatory_check.md；“未核实”项在测算中以标注的占位值处理。" if zh else
             "Each statement below was checked against the listed sources on 2026-11-15 (log: docs/regulatory_check.md); items marked "
             "not_verified are handled as labelled placeholders in the numbers.")
    L.append("")
    L.append(render_statements(res, statements, sources, lang))
    return "\n".join(L) + "\n"


def render_statements(res: dict, statements: dict, sources: dict, lang: str) -> str:
    zh = lang == "zh"
    rows = []
    for sid in res["statements_used"]:
        st = statements[sid]
        links = ", ".join(f"[{s}]({sources[s]['url']})" for s in st.get("sources", []) if s in sources) or "—"
        rows.append([sid, STATUS_ZH[st["status"]] if zh else st["status"], st["zh"] if zh else st["en"], links])
    return _table(["编号", "状态", "表述", "来源"] if zh else ["ID", "Status", "Statement", "Sources"], rows) + "\n"
