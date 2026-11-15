"""Written rationale for each lane's recommendation, in English and Simplified Chinese, generated from the
numbers so that the text can never disagree with the results."""
from __future__ import annotations

UNIT_ZH = {"kit": "套", "move": "次往返", "parcel": "个包裹", "unit": "件"}


def _pct(x: float) -> str:
    return f"{x * 100:.0f}%"


def _usd(x: float) -> str:
    return f"USD {x:,.2f}" if x < 100 else f"USD {x:,.0f}"


def _usd_zh(x: float) -> str:
    return f"{x:,.2f} 美元" if x < 100 else f"{x:,.0f} 美元"


def rationale(lane: dict, options: list[dict], rec: dict, target_p: float, unit: str) -> dict:
    by_id = {o["id"]: o for o in options}
    ch = by_id[rec["chosen"]]
    m = ch["metrics"]
    T = lane["target_transit_days"]
    uzh = UNIT_ZH.get(unit, "件")
    en, zh = [], []
    if rec["status"] == "meets_target":
        en.append(f"Recommended: {ch['label_en']} at {_usd(m['cost_per_unit'])} per {unit} landed, P90 {m['p90']:.1f} days, "
                  f"{_pct(m['on_time_probability'])} on time against the {T}-day target, risk score {m['risk']:.0f}/100.")
        zh.append(f"推荐方案：{ch['label_zh']}。每{uzh}落地成本 {_usd_zh(m['cost_per_unit'])}，P90 时效 {m['p90']:.1f} 天，"
                  f"{T} 天内送达概率 {_pct(m['on_time_probability'])}，风险评分 {m['risk']:.0f}/100。")
        en.append(f"It meets the {_pct(target_p)} on-time requirement and has the best weighted score of cost, P90 time and risk among the options that do.")
        zh.append(f"该方案满足 {_pct(target_p)} 准时率要求，并在满足要求的方案中成本、P90 时效与风险的加权得分最优。")
    else:
        en.append(f"No option reaches {_pct(target_p)} on time within {T} days. Recommended for now: {ch['label_en']} "
                  f"({_pct(m['on_time_probability'])} on time, P90 {m['p90']:.1f} days, {_usd(m['cost_per_unit'])} per {unit}); "
                  "the target or the lead time needs to be renegotiated.")
        zh.append(f"没有方案能在 {T} 天内达到 {_pct(target_p)} 的准时率。暂推荐 {ch['label_zh']}（准时率 {_pct(m['on_time_probability'])}，"
                  f"P90 {m['p90']:.1f} 天，每{uzh} {_usd_zh(m['cost_per_unit'])}），需与客户重新商定时效目标或备货提前期。")
    curve = {float(k): v for k, v in ch["transit"].get("on_time_at", {}).items()}
    later = sorted(t for t, p in curve.items() if t > T and p >= target_p)
    earlier = sorted((t for t in curve if t < T), reverse=True)
    if rec["status"] != "meets_target" and later:
        en.append(f"Planning {later[0]:g} days instead of {T} lifts this option to {_pct(curve[later[0]])} on time.")
        zh.append(f"若将计划时效由 {T} 天放宽至 {later[0]:g} 天，该方案准时率可提升至 {_pct(curve[later[0]])}。")
    elif rec["status"] == "meets_target" and earlier:
        e0 = earlier[0]
        en.append(f"Sensitivity: with a {e0:g}-day target the same option would be on time {_pct(curve[e0])} of the time.")
        zh.append(f"敏感性：若时效目标收紧至 {e0:g} 天，该方案准时率为 {_pct(curve[e0])}。")
    for o in options:
        if o["id"] == ch["id"]:
            continue
        om = o["metrics"]
        dc = om["cost_per_unit"] / m["cost_per_unit"] - 1.0
        dt = om["p90"] - m["p90"]
        if o["id"] in rec["front"]:
            cost_en = f"{abs(dc) * 100:.0f}% {'more' if dc > 0 else 'less'} per {unit}"
            cost_zh = f"每{uzh}成本{'高' if dc > 0 else '低'} {abs(dc) * 100:.0f}%"
            time_en = f"P90 {om['p90']:.1f} days ({'+' if dt >= 0 else '-'}{abs(dt):.1f})"
            time_zh = f"P90 {om['p90']:.1f} 天（{'多' if dt >= 0 else '少'} {abs(dt):.1f} 天）"
            miss = om["on_time_probability"] < target_p
            tail_en = f"; on time {_pct(om['on_time_probability'])}" + (" (below target)" if miss else "")
            tail_zh = f"；准时率 {_pct(om['on_time_probability'])}" + ("（未达目标）" if miss else "")
            en.append(f"Alternative on the Pareto front: {o['label_en']} - {cost_en}, {time_en}, risk {om['risk']:.0f}{tail_en}.")
            zh.append(f"帕累托前沿上的备选：{o['label_zh']}——{cost_zh}，{time_zh}，风险 {om['risk']:.0f}{tail_zh}。")
        else:
            doms = [by_id[i]["label_en"] for i in o.get("dominated_by", [])]
            doms_zh = [by_id[i]["label_zh"] for i in o.get("dominated_by", [])]
            en.append(f"{o['label_en']} is dominated by {', '.join(doms)} (no better on cost, P90 or risk).")
            zh.append(f"{o['label_zh']}在成本、P90 时效和风险上均不优于{'、'.join(doms_zh)}，属被占优方案。")
    for x in lane.get("excluded", []):
        what = x.get("mode") or x.get("regime")
        en.append(f"Not offered: {what} - {x['reason_en']}.")
        zh.append(f"未纳入：{what}——{x['reason_zh']}。")
    key = [f for f in ch["flags"] if f["severity"] in ("medium", "high", "block")]
    if key:
        en.append("Conditions to manage: " + " ".join(f"[{f['id']}] {f['en']}" for f in key))
        zh.append("需重点管控：" + " ".join(f"【{f['id']}】{f['zh']}" for f in key))
    return {"en": en, "zh": zh}
