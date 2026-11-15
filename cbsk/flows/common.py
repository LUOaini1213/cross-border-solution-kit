"""Shared helpers for the flow models."""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from .. import incoterms, transit
from ..calc import C, Calc, R, RateBook, add
from ..reference import Reference

QUOTE_GROUPS = ("logistics", "vas", "insurance", "temporary_admission", "fta_docs")

MODE_LABELS = {
    "ocean_fcl": ("Ocean FCL (40ft HC)", "海运整箱（40 尺高柜）"),
    "ocean_fcl20": ("Ocean FCL (20ft)", "海运整箱（20 尺）"),
    "ocean_lcl": ("Ocean LCL", "海运拼箱"),
    "air": ("Air freight", "空运"),
    "rail_sea_fcl": ("Rail-sea via Qinzhou (FCL)", "经钦州铁海联运（整箱）"),
    "rail": ("Cross-border rail", "跨境铁路"),
    "road": ("Cross-border road", "跨境公路"),
    "air_parcel": ("Air parcel, DDP", "空运小包（完税交付）"),
    "sea_air": ("Sea-air via Singapore", "经新加坡海空联运"),
    "ocean_bulk_local": ("Ocean bulk + local fulfilment", "海运备货 + 本地履约"),
}
REGIME_LABELS = {
    "ata_carnet": ("ATA Carnet", "ATA 单证册"),
    "tis": ("Temporary Import Scheme", "临时进口计划（TIS）"),
    "temp_export_repair": ("temporary export for repair", "出境维修临时出口"),
}


@dataclass
class Ctx:
    ref: Reference
    ratebook: RateBook
    rule: str | None          # Incoterm of the sale (None for owner's goods)
    role: str                 # buyer | seller | owner
    seed: int
    draws: int

    def rate(self, pid: str, en: str, zh: str) -> tuple:
        value = self.ref.get(pid)
        return self.ratebook.add(pid, float(value), en, zh, self.ref)

    def tariff(self, hs: str, column: str, en: str, zh: str) -> tuple:
        value = self.ref.my_tariff(hs, column)
        return self.ratebook.add(f"tariff.MY.{hs}.{column}", value, en, zh, self.ref)

    def fixed(self, pid: str, value: float, en: str, zh: str, label: str, unit: str = "") -> tuple:
        """A rate that is not in data/reference (RFQ scenario switches, derived regime values)."""
        return self.ratebook.add(pid, float(value), en, zh, None, label=label, unit=unit)

    def line(self, calc: Calc, short: str, expr, en: str, zh: str, element: str | None, group: str = "logistics",
             unit: str = "USD", note: str = ""):
        if element is None:
            payer = "owner" if self.rule is None else self.role
        else:
            payer = incoterms.payer(self.ref, self.rule, element, self.role)
        in_q = (payer == self.role or payer == "owner") and group in QUOTE_GROUPS
        return calc.calc(short, expr, en, zh, unit=unit, group=group, element=element, payer=payer,
                         in_quote=in_q, note=note)


def add_totals(calc: Calc, units_expr, unit_label: str) -> dict:
    nodes = list(calc.nodes.values())

    def total(short, pred, en, zh, group="total"):
        items = [R(n.code) for n in nodes if n.kind == "calc" and pred(n)]
        return calc.calc(short, add(*items) if items else C(0.0), en, zh, group=group)

    q = total("TOTAL_QUOTE", lambda n: n.in_quote, "Total quotation (logistics, VAS, insurance, permits)",
              "报价合计（物流、增值服务、保险、许可）")
    s = total("TOTAL_SELLER_SIDE", lambda n: n.group in QUOTE_GROUPS and not n.in_quote,
              "Costs on the seller's side under the Incoterm (excluded)", "按贸易术语由卖方承担的费用（不计入）")
    d = total("TOTAL_DUTY", lambda n: n.group == "duty", "Duties (estimated)", "关税（估算）")
    t = total("TOTAL_TAX", lambda n: n.group == "tax", "Import / consumption taxes (estimated)", "进口环节税及消费税（估算）")
    e = total("TOTAL_ECONOMIC", lambda n: n.group == "economic", "Inventory carrying cost (economic, not invoiced)",
              "在途/安全库存资金占用成本（经济成本，不开票）")
    landed = calc.calc("TOTAL_LANDED", add(q, d, t, e), "Total landed cost (decision basis)", "总落地成本（决策口径）",
                       group="total")
    per_unit = calc.calc("PER_UNIT", ("div", landed, units_expr), f"Landed cost per {unit_label}",
                         f"每{unit_label}落地成本", unit=f"USD/{unit_label}", group="total")
    return {"quote": q, "seller_side": s, "duty": d, "tax": t, "economic": e, "landed": landed, "per_unit": per_unit}


def ceil_div(x: float, cap: float) -> int:
    return int(math.ceil(x / cap - 1e-9)) if x > 0 else 0


def run_transit(legs: list[dict], ctx: Ctx, target: float, *parts: str) -> tuple[dict, np.ndarray]:
    seed = transit.stable_seed(ctx.seed, *parts)
    samples = transit.simulate(legs, seed, ctx.draws)
    m = transit.metrics(samples, target)
    m["seed"] = seed
    return m, samples


def option_label(mode: str, regime: str | None = None) -> tuple[str, str]:
    en, zh = MODE_LABELS[mode]
    if regime:
        ren, rzh = REGIME_LABELS[regime]
        return f"{en} + {ren}", f"{zh} + {rzh}"
    return en, zh
