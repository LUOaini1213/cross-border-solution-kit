"""Implementation plan (milestones, RACI) and post-go-live KPIs per flow type, in English and Chinese.
KPI targets are taken from the recommended option's results so the monitoring sheet matches the quote."""
from __future__ import annotations

ROLES = [("Customer A logistics", "Customer A 物流"), ("Solution provider", "方案提供方"),
         ("Customs broker", "报关行"), ("Origin agent / supplier", "起运地代理/供应商"), ("Carrier", "承运人")]

PLANS = {
    "b2b_import": {
        "milestones": [
            ("W0-2", "Kick-off; request a written tariff classification for the kit structure; confirm Schedule C sales-tax exemption",
             "项目启动；就散件结构申请书面税则归类；确认附表 C 销售税豁免"),
            ("W2-4", "Collect supplier cost statements (RVC) and set up the Form E routine; agree third-party invoice wording",
             "收集供应商成本构成（RVC）并建立 Form E 办理流程；确定第三方发票格式"),
            ("W3-5", "Tender the recommended routes; secure weekly container allocation and rail-sea slots",
             "按推荐路线招标；锁定每周舱位及铁海联运班列舱位"),
            ("W5-6", "Pilot: one shipment per lane, measure door-to-door time and document quality",
             "试运行：每条线路一票，测量门到门时效与单证质量"),
            ("W7-8", "Go-live with weekly control-tower report", "正式上线，每周发布控制塔报告"),
            ("W12", "First quarterly review: lead-time buffer, routing mix, FTA claims", "首次季度复盘：时效缓冲、路线组合、自贸协定享惠情况"),
        ],
        "raci": [
            ("Tariff classification and Schedule C", "税则归类与附表 C", ["A", "R", "C", "C", "I"]),
            ("Origin evidence and Form E", "原产地证据与 Form E", ["A", "C", "C", "R", "I"]),
            ("Booking and allocation", "订舱与舱位", ["I", "R", "I", "C", "A"]),
            ("Import declaration and duty payment", "进口申报与缴税", ["A", "C", "R", "I", "I"]),
            ("Kitting and line feed", "配套与工位配送", ["A", "R", "I", "I", "I"]),
            ("KPI reporting", "绩效报告", ["I", "R", "C", "C", "C"]),
        ],
    },
    "temporary": {
        "milestones": [
            ("W0-1", "Classify each item against the Strategic Goods Control List; obtain the owner's export classification",
             "逐项对照战略物资管制清单归类；取得货主出口管制分类"),
            ("W1-2", "Choose the instrument per move (ATA Carnet, TIS or temporary export); apply for the carnet or lodge TIS security",
             "按每次运输选择通关工具（ATA 单证册、TIS 或临时出口）；申请单证册或提交 TIS 担保"),
            ("W2-3", "Book air capacity, air-ride trucks and crates; file strategic-goods permits at least 5 working days before export",
             "预订空运舱位、气垫车及木箱；出口前至少 5 个工作日申领战略物资许可证"),
            ("Move", "Execute, track and endorse documents at each border", "执行运输，全程跟踪并在各关口完成单证签注"),
            ("Monthly", "Close out carnet vouchers and TIS permits; report open items", "核销单证册凭单及 TIS 许可证；通报未结项"),
        ],
        "raci": [
            ("Strategic-goods classification and permits", "战略物资归类与许可", ["A", "C", "R", "C", "I"]),
            ("Carnet / TIS security", "单证册/TIS 担保", ["A", "R", "C", "I", "I"]),
            ("Packing, crating and indicators", "包装、木箱与指示器", ["C", "R", "I", "C", "I"]),
            ("Transport and handling", "运输与操作", ["I", "R", "I", "C", "A"]),
            ("Re-export / discharge within period", "期限内复出口/核销", ["A", "R", "C", "I", "I"]),
            ("KPI reporting", "绩效报告", ["I", "R", "C", "I", "C"]),
        ],
    },
    "b2c_parcel": {
        "milestones": [
            ("W0-2", "Register for Malaysian LVG sales tax; choose the importer-of-record model per market; check battery and radio rules",
             "完成马来西亚低价值货物销售税注册；确定各市场进口登记人模式；核查电池与无线电相关规定"),
            ("W2-4", "Integrate checkout tax calculation, HS codes and pre-alert data (incl. the LVG number)",
             "打通结账计税、HS 编码与预报数据（含 LVG 注册号）"),
            ("W4-6", "Tender line-haul and last mile; set up local fulfilment where bulk stock is recommended",
             "招标干线与尾程；在推荐备货的市场搭建本地履约"),
            ("W6", "Pilot 500 parcels per lane; measure delivery time, holds and tax accuracy", "每条线路试运 500 个包裹，测量时效、查验率与计税准确性"),
            ("W8", "Go-live with weekly dashboard", "正式上线，每周看板"),
            ("W12", "Review the split between parcels and local stock per market", "复盘各市场包裹直邮与本地备货的比例"),
        ],
        "raci": [
            ("Tax registrations and checkout tax", "税务登记与结账计税", ["A", "C", "C", "I", "I"]),
            ("Importer of record and licences", "进口登记人与许可", ["A", "C", "R", "I", "I"]),
            ("Line-haul and clearance", "干线与清关", ["I", "R", "R", "C", "A"]),
            ("Local fulfilment and last mile", "本地履约与尾程", ["C", "R", "I", "I", "A"]),
            ("Product compliance (batteries, radio)", "产品合规（电池、无线电）", ["A", "C", "C", "R", "I"]),
            ("KPI reporting", "绩效报告", ["I", "R", "C", "I", "C"]),
        ],
    },
}


def plan(flow: str) -> dict:
    return PLANS[flow]


def _first_leg_median(option_legs: list[dict], key: str) -> float | None:
    for lg in option_legs:
        if lg.get("source", "").endswith(key) and "median" in lg:
            return float(lg["median"])
    return None


def kpis(flow: str, lane: dict, summary: dict, target_p: float) -> list[dict]:
    T = lane["target_transit_days"]
    chosen = next(o for o in lane["options"] if o["id"] == summary["option"])
    units = {"kit": "kit", "move": "move", "parcel": "parcel"}.get(lane["unit"], lane["unit"])
    divisor = chosen["quantities"].get("units_per_year") or chosen["quantities"].get("moves_per_year") \
        or chosen["quantities"].get("parcels_per_year")
    p90 = round(summary["p90"], 1)
    out = []
    if flow == "b2b_import":
        clr = _first_leg_median(chosen["legs"], "ct_import") or _first_leg_median(chosen["legs"], "air_import")
        out += [
            {"en": f"Shipments delivered within {T} days (share)", "zh": f"{T} 天内送达的票数占比", "target": target_p, "better": "higher",
             "trigger_en": "Two months below target: add buffer stock or move part of the volume to the next Pareto option",
             "trigger_zh": "连续两个月低于目标：增加缓冲库存或将部分货量转至下一个帕累托方案"},
            {"en": "Door-to-door P90 (days)", "zh": "门到门 P90 时效（天）", "target": p90, "better": "lower",
             "trigger_en": "P90 above target by 3 days: review port dwell and transshipment", "trigger_zh": "P90 超出目标 3 天：复核港口滞留与中转"},
            {"en": f"Logistics cost per {units} (USD, quote basis)", "zh": f"每{units}物流成本（美元，报价口径）",
             "target": round(summary["annual_quote"] / divisor, 2), "better": "lower",
             "trigger_en": "Above target by 5%: check container fill and surcharges", "trigger_zh": "超出目标 5%：检查装箱率与附加费"},
            {"en": "Import clearance, median days", "zh": "进口清关中位天数", "target": round(clr, 1) if clr else 2.0, "better": "lower",
             "trigger_en": "Above target: review document quality with the broker", "trigger_zh": "高于目标：与报关行复核单证质量"},
            {"en": "Form E accepted first time (share)", "zh": "Form E 一次通过率", "target": 0.98, "better": "higher",
             "trigger_en": "Below target: audit supplier origin data", "trigger_zh": "低于目标：审核供应商原产地数据"},
            {"en": "Damage or shortage incidents per 100 shipments", "zh": "每百票破损或短少事件数", "target": 1.0, "better": "lower",
             "trigger_en": "Above target: review packing and seals", "trigger_zh": "高于目标：复核包装与封条"},
        ]
    elif flow == "temporary":
        out += [
            {"en": f"Moves arriving within {T} days (share)", "zh": f"{T} 天内到达的运输占比", "target": target_p, "better": "higher",
             "trigger_en": "Any miss on an event move: root-cause review before the next event", "trigger_zh": "展会类运输任何一次延误：下次前完成根因分析"},
            {"en": "P90 days (metric of the RFQ)", "zh": "P90 天数（按询价口径）", "target": p90, "better": "lower",
             "trigger_en": "Above target: check permits and hold reasons", "trigger_zh": "高于目标：检查许可证与查验原因"},
            {"en": "Temporary admissions discharged within the period (share)", "zh": "期限内完成核销的临时进出口占比", "target": 1.0, "better": "higher",
             "trigger_en": "Any open item 30 days before expiry: file extension or re-export", "trigger_zh": "到期前 30 天仍未结：申请延期或安排复出口"},
            {"en": "GST or duty claims from non-discharge (count)", "zh": "因未核销产生的 GST/关税追缴（次数）", "target": 0.0, "better": "lower",
             "trigger_en": "Any claim: review the tracking process", "trigger_zh": "出现追缴：复核跟踪流程"},
            {"en": "Cost per move (USD, quote basis)", "zh": "每次往返成本（美元，报价口径）", "target": round(summary["annual_quote"] / divisor, 2),
             "better": "lower", "trigger_en": "Above target by 10%: re-tender", "trigger_zh": "超出目标 10%：重新招标"},
            {"en": "Strategic-goods permits in place before export (share of moves needing one)", "zh": "出口前已取得战略物资许可证的比例",
             "target": 1.0, "better": "higher", "trigger_en": "Any miss: stop shipment, escalate", "trigger_zh": "任何遗漏：暂停发运并上报"},
        ]
    else:
        tax_per = (summary["annual_duty"] + summary["annual_tax"]) / divisor
        out += [
            {"en": f"Parcels delivered within {T} days (share)", "zh": f"{T} 天内妥投包裹占比", "target": target_p, "better": "higher",
             "trigger_en": "Two weeks below target: rebalance stock or carriers", "trigger_zh": "连续两周低于目标：调整备货或承运商"},
            {"en": "P90 delivery days", "zh": "P90 妥投天数", "target": p90, "better": "lower",
             "trigger_en": "Above target: check clearance holds and last mile", "trigger_zh": "高于目标：检查清关查验与尾程"},
            {"en": "Cost to serve per parcel incl. duties and taxes (USD)", "zh": "每包裹履约成本（含关税与税费，美元）",
             "target": round(summary["cost_per_unit"], 2), "better": "lower",
             "trigger_en": "Above target by 5%: review weights, rates and tax mix", "trigger_zh": "超出目标 5%：复核重量、费率与税费结构"},
            {"en": "Customs hold rate (share of parcels)", "zh": "海关查验扣留率", "target": 0.03, "better": "lower",
             "trigger_en": "Above target: audit HS codes and declared values", "trigger_zh": "高于目标：审核 HS 编码与申报价值"},
            {"en": "Duties and taxes per parcel (USD)", "zh": "每包裹关税与税费（美元）", "target": round(tax_per, 2), "better": "lower",
             "trigger_en": "Deviation above 5%: check rates and thresholds", "trigger_zh": "偏差超过 5%：核查税率与门槛"},
            {"en": "Damage or loss rate (share)", "zh": "破损或丢失率", "target": 0.005, "better": "lower",
             "trigger_en": "Above target: review packaging", "trigger_zh": "高于目标：复核包装"},
        ]
    return out
