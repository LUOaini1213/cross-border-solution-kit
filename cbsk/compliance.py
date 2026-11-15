"""Compliance and risk checks: HS-based controls, FTA origin options, temporary admission (ATA Carnet /
TIS / temporary export), third-country invoicing, destination low-value regimes, hold-risk flags."""
from __future__ import annotations

from .reference import Reference

SEVERITIES = ("info", "low", "medium", "high", "block")


def flag(fid: str, severity: str, en: str, zh: str, mitigation_en: str = "", mitigation_zh: str = "",
         statements: list[str] | None = None, verified: bool | None = None, modes: list[str] | None = None,
         options: list[str] | None = None) -> dict:
    """A finding. `verified` is decided later from the cited statements (see finalize_flags) unless the caller
    already knows the rule is unverified; flags without statements are operational (verified = None)."""
    if severity not in SEVERITIES:
        raise ValueError(severity)
    return {"id": fid, "severity": severity, "en": en, "zh": zh, "mitigation_en": mitigation_en,
            "mitigation_zh": mitigation_zh, "statements": list(statements or []), "verified": verified,
            "modes": modes, "options": options}


def statement_status(ref: Reference, statements: list[str]) -> bool:
    """True only if every cited statement is verified/corrected on an official source."""
    return all(ref.statement(s)["status"] in ("verified", "corrected") for s in statements) if statements else False


def hs_flags(ref: Reference, dest: str, lines: list[dict], lane_flags: set[str], context: set[str]) -> list[dict]:
    """HS-based permit / control flags.

    lines: [{hs, flags:set}] ; lane_flags e.g. {"kit"} ; context e.g. {"sg_export", "origin_export_semiconductor"}.
    """
    out = []
    for rule in ref.get("compliance.hs_controls"):
        if rule.get("destination") and rule["destination"] != dest:
            continue
        if rule.get("applies_when") and rule["applies_when"] not in context:
            continue
        if rule.get("requires_lane_flag") and rule["requires_lane_flag"] not in lane_flags:
            continue
        hits = []
        for ln in lines:
            digits = ln["hs"].replace(".", "")
            if not any(digits.startswith(p) for p in rule["hs_prefixes"]):
                continue
            if rule.get("requires_line_flag") and rule["requires_line_flag"] not in ln.get("flags", set()):
                continue
            hits.append(ln["hs"])
        if hits:
            verified = bool(rule["verified"]) and statement_status(ref, rule["statements"])
            out.append(flag(rule["id"], rule["severity"], rule["en"] + f" (HS {', '.join(sorted(set(hits)))})",
                            rule["zh"] + f"（HS {'、'.join(sorted(set(hits)))}）", rule["mitigation_en"],
                            rule["mitigation_zh"], rule["statements"], verified, rule.get("modes"), rule.get("options")))
    return out


def fta_flags(ref: Reference, fta_rows: list[dict], third_party: bool, invoicing_country: str) -> list[dict]:
    out = []
    chosen = {r["chosen"]["scheme"] for r in fta_rows}
    failed = [r for r in fta_rows if not any(o["available"] for o in r["options"] if o["scheme"] != "MFN")
              and min((o["rate"] for o in r["options"] if o["rate"] is not None)) < r["mfn_rate"]]
    if "ACFTA" in chosen:
        out.append(flag("FTA-ACFTA-FORM-E", "medium",
                        "ACFTA preference claimed: each shipment needs a Form E issued before or at shipment, valid one year; origin evidence (RVC >= 40%) must be kept for verification.",
                        "申请 ACFTA 优惠：每票须在装运前或装运时取得 Form E（有效期一年），并留存区域价值成分不低于 40% 的原产地证据以备核查。",
                        "Collect cost breakdowns from suppliers; check Form E data against the invoice before departure.",
                        "向供应商收集成本构成；离港前核对 Form E 与发票信息一致。",
                        ["FTA-ACFTA-ORIGIN", "FTA-ACFTA-FORM-E", "FTA-ACFTA-DIRECT"]))
    for r in failed:
        out.append(flag("FTA-ORIGIN-NOT-MET", "medium",
                        f"{r['sku']} ({r['hs']}): supplier RVC {r['rvc']}% does not meet the 40% general rule and CTH is not met, so MFN {r['mfn_rate']:.0%} applies. Annual duty at stake: USD {r['saving_if_qualified']:,.0f}.",
                        f"{r['sku']}（{r['hs']}）：供应商区域价值成分 {r['rvc']}%，未达 40% 一般规则且不满足品目改变，适用最惠国税率 {r['mfn_rate']:.0%}；每年涉及关税约 {r['saving_if_qualified']:,.0f} 美元。",
                        "Work with the supplier to document regional content (e.g. ASEAN or Chinese terminals and copper) before claiming; re-run the origin check.",
                        "与供应商合作提升并记录区域价值成分（如采购中国或东盟产端子、铜材）后再申请优惠，并重新核算原产地。",
                        ["FTA-ACFTA-ORIGIN", "FTA-RCEP-PSR"]))
    if third_party:
        out.append(flag("THIRD-COUNTRY-INVOICE", "medium",
                        f"Goods ship China to Malaysia but are invoiced by an entity in {invoicing_country}: ACFTA Form E must show the third-party invoice number in Box 10 with that invoice attached (exporter and consignee in Parties); under RCEP tick Box 17 and name the invoicing company in Box 14. Customs value follows the sale for export to Malaysia (which sale applies in a chain was not verified).",
                        f"货物由中国直运马来西亚、由 {invoicing_country} 主体开票：ACFTA Form E 第 10 栏须填第三方发票号并随附该发票（出口商与收货人须在成员方境内）；RCEP 证书须勾选第 17 栏并在第 14 栏填写开票公司。完税价格以向马来西亚出口的销售为准（多环节销售中适用哪一环节未经核实）。",
                        "Align the three documents (supplier invoice, third-party invoice, Form E) before departure; keep the contract chain on file.",
                        "离港前核对供应商发票、第三方发票与 Form E 三者一致；留存完整合同链。",
                        ["FTA-ACFTA-3PI", "FTA-RCEP-3PI", "MY-VALUATION-CIF"]))
    return out


def temporary_regimes(ref: Reference, purpose: str, origin: str, dest: str) -> dict:
    """Which temporary-admission instruments apply to a move; reasons for exclusions."""
    ta = ref.get("compliance.temporary_admission")
    out = {}
    into_sg = dest == "SG"
    if into_sg:
        ok = purpose in ta["ata_sg_import_purposes"]
        foreign = origin
        acc = ta["ata_destinations_from_sicc_list"].get(foreign)
        out["ata_carnet"] = {
            "available": ok,
            "reason_en": ("Singapore accepts foreign ATA Carnets for this purpose" if ok else
                          f"Singapore accepts foreign carnets only for exhibitions, professional equipment and scientific equipment; '{purpose}' is not one of them"),
            "reason_zh": ("新加坡接受外国 ATA 单证册用于该用途" if ok else
                          "新加坡仅接受外国单证册用于展览、专业设备和科学设备，该用途不在其列"),
            "statements": ["SG-ATA-SCOPE", "SG-ATA-SAME-CONDITION", "SG-ATA-PERIOD"],
            "origin_member": acc is not None,
        }
        ok_tis = purpose in ("exhibition", "professional_equipment", "repair_in_sg")
        out["tis"] = {"available": ok_tis,
                      "reason_en": "TIS covers this purpose (up to 6 months, GST suspended against security)" if ok_tis else "not a TIS purpose",
                      "reason_zh": "TIS 适用该用途（最长 6 个月，提供担保后暂缓征收 GST）" if ok_tis else "不属于 TIS 适用用途",
                      "statements": ["SG-TIS-PURPOSES", "SG-TIS-6M", "SG-TIS-SECURITY"]}
    if origin == "SG":
        repair = purpose == "repair_abroad"
        out["ata_carnet"] = {
            "available": False if repair else True,
            "reason_en": ("Repair is not an ATA purpose and goods must return in the same condition" if repair
                          else "local carnet from SICC; destination acceptance to be checked"),
            "reason_zh": ("维修不属于 ATA 单证册用途，且货物须以原状返回" if repair else "可向 SICC 申请本地单证册，须核实目的国是否接受"),
            "statements": ["SG-ATA-SAME-CONDITION", "SG-ATA-ISSUER"],
            "origin_member": True,
        }
        out["temp_export_repair"] = {
            "available": repair,
            "reason_en": "Temporary export for repair: OUT (TCI) before export, re-import within 3 months; GST on new parts unless warranty",
            "reason_zh": "出境维修按临时出口办理：出口前申报 OUT (TCI)，3 个月内复进口；新换部件须缴 GST，保修免费维修除外",
            "statements": ["SG-TEMPEXP-REPAIR"]}
    return out


def temporary_flags(ref: Reference, lane: dict, regimes: dict) -> list[dict]:
    out = []
    purpose, o, d = lane["purpose"], lane["origin"]["country"], lane["destination"]["country"]
    if "ata_carnet" in regimes and not regimes["ata_carnet"]["available"]:
        out.append(flag("ATA-NOT-APPLICABLE", "info",
                        f"ATA Carnet excluded: {regimes['ata_carnet']['reason_en']}.",
                        f"不采用 ATA 单证册：{regimes['ata_carnet']['reason_zh']}。",
                        statements=regimes["ata_carnet"]["statements"] + ["SG-ATA-NO-SAMPLES"]))
    if purpose == "repair_abroad":
        out.append(flag("DEST-REPAIR-REGIME", "medium",
                        f"Temporary admission for repair at the destination ({d}) was not assessed; duty or tax on arrival may apply unless a relief is used.",
                        f"目的地（{d}）对维修类临时进口的处理未作评估；如不适用减免，入境时可能产生关税或税费。",
                        "Ask the repair centre's customs broker for the inward-processing / re-export relief before the first loop.",
                        "首次周转前，请维修中心的报关行确认进境加工或复出口减免安排。", [], verified=False))
    if purpose == "repair_in_sg" and o != "SG":
        out.append(flag("ORIGIN-REIMPORT-REGIME", "medium",
                        f"Re-import into {o} after repair (duty/tax relief on return) was not assessed.",
                        f"维修后复进口 {o} 的关税/税费减免未作评估。",
                        f"Confirm {o}'s temporary-export-for-repair procedure with the customer's broker.",
                        f"与客户报关行确认 {o} 的出境维修临时出口手续。", [], verified=False))
    if purpose in ("exhibition", "professional_equipment"):
        out.append(flag("TA-CONDITION", "low",
                        "Goods must leave Singapore in the same condition within the permitted period (6 months for TIS and ATA); selling or leaving them behind triggers GST.",
                        "货物须在许可期限内（TIS 与 ATA 均为 6 个月）以原状离境；出售或滞留将产生 GST。",
                        "Track re-export dates; file extensions before expiry.", "跟踪复出口日期，到期前申请延期。",
                        ["SG-ATA-PERIOD", "SG-TIS-6M", "SG-TIS-PAYMENT"]))
    return out


PARCEL_MODES = ["air_parcel", "sea_air", "rail", "road"]


def parcel_regime_flags(ref: Reference, dest: str, annual_lvg_sales_myr: float | None = None) -> list[dict]:
    """Destination low-value regimes; they apply to parcel channels, not to bulk import."""
    out = []
    if dest == "MY":
        thr = float(ref.get("regimes.MY.lvg_registration_threshold_myr"))
        if annual_lvg_sales_myr is not None and annual_lvg_sales_myr > thr:
            out.append(flag("MY-LVG-REGISTRATION", "medium",
                            f"Malaysian LVG sales of about RM {annual_lvg_sales_myr:,.0f} a year exceed the RM {thr:,.0f} registration threshold: the seller must register, charge 10% sales tax at checkout and print the LVG registration number on parcels and waybills.",
                            f"马来西亚低价值货物年销售额约 {annual_lvg_sales_myr:,.0f} 林吉特，超过 {thr:,.0f} 林吉特注册门槛：卖家须注册、在结账时收取 10% 销售税，并在包裹和运单上标注 LVG 注册号。",
                            "Register before go-live; pass the LVG number in the pre-alert data so import sales tax is not charged twice.",
                            "上线前完成注册；在预报数据中传送 LVG 注册号，避免进口环节重复征收销售税。",
                            ["MY-LVG", "MY-LVG-NO-DOUBLE"], modes=PARCEL_MODES))
    if dest == "ID":
        out.append(flag("ID-CONSIGNMENT-RATES", "info",
                        "Indonesian consignments above FOB USD 3 pay 7.5% duty, or 25% for apparel and bags (plus 5% income tax), plus VAT at an effective 11%.",
                        "印尼 FOB 3 美元以上的快件征收 7.5% 关税，服装、箱包为 25%（另征 5% 所得税），并征收实际税负 11% 的增值税。",
                        statements=["ID-CN-BAND", "ID-VAT-EFFECTIVE"], modes=PARCEL_MODES))
    if dest == "TH":
        out.append(flag("TH-NO-DEMINIMIS", "medium",
                        "Since 1 January 2026 Thailand exempts from duty only items worth up to 1 baht, so every parcel is dutiable and VAT applies; the duty rates used here are placeholders (not verified).",
                        "自 2026 年 1 月 1 日起泰国仅对价值不超过 1 泰铢的物品免征关税，因此每个包裹均须缴纳关税和增值税；本文所用关税税率为占位值（未经核实）。",
                        "Confirm the tariff lines and rates with a Thai broker before launch.", "上线前与泰国报关行确认税号和税率。",
                        ["TH-DUTY-1BAHT", "TH-VAT", "TH-MFN"], verified=False, modes=PARCEL_MODES))
    if dest == "PH":
        out.append(flag("PH-DEMINIMIS", "low",
                        "Parcels at or below PHP 10,000 FOB/FCA pay no duties and taxes in the Philippines (CMTA s.423); whether the threshold has been CPI-adjusted was not verified.",
                        "菲律宾对 FOB/FCA 不超过 10,000 比索的包裹免征关税和税费（CMTA 第 423 条）；该门槛是否已按 CPI 调整未经核实。",
                        "Re-check the current Bureau of Customs administrative order before relying on the threshold.",
                        "依赖该门槛前请复核菲律宾海关现行行政令。", ["PH-DEMINIMIS", "PH-CAO"], modes=PARCEL_MODES))
    return out


def risk_score(ref: Reference, flags: list[dict], p50: float, p90: float, handoffs: int, unverified_service: bool) -> dict:
    pts = ref.get("compliance.risk_points")
    flag_pts = sum(pts[f["severity"]] for f in flags)
    var_pts = min(float(pts["variability_cap"]), float(pts["variability_per_day"]) * max(0.0, p90 - p50))
    hand_pts = pts["per_handoff"] * handoffs
    svc_pts = pts["unverified_service"] if unverified_service else 0
    total = min(100.0, flag_pts + var_pts + hand_pts + svc_pts)
    return {"score": total, "flags": flag_pts, "variability": var_pts, "handoffs": hand_pts, "service": svc_pts}


def hold_flag_count(ref: Reference, flags: list[dict]) -> int:
    """Number of medium/high flags that make a customs hold more likely (drives the transit model)."""
    relevant = set(ref.get("compliance.hold_relevant_flags"))
    return sum(1 for f in flags if f["id"] in relevant and f["severity"] in ("medium", "high"))


def finalize_flags(ref: Reference, flags: list[dict]) -> None:
    """Set `verified`: True only if every cited statement is verified/corrected; None for operational flags."""
    for f in flags:
        if not f["statements"]:
            f["verified"] = None if f["verified"] is None else False
        elif f["verified"] is not False:
            f["verified"] = statement_status(ref, f["statements"])


def flags_for_option(flags: list[dict], mode: str, option_kind: str) -> list[dict]:
    out = []
    for f in flags:
        if f.get("modes") and mode not in f["modes"]:
            continue
        if f.get("options") and option_kind not in f["options"]:
            continue
        out.append(f)
    return out
