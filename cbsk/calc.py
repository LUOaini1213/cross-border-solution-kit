"""A tiny calculation graph shared by the Python totals and the Excel workbook.

Cost build-ups are written once as expression trees over named nodes. Python evaluates the trees;
the Excel writer turns the same trees into live formulas. A separate formula evaluator in the tests
recomputes the workbook from its formulas, so a wrong cell reference or operator is caught.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

Expr = tuple


def R(code: str) -> Expr:
    return ("ref", code)


def C(x: float) -> Expr:
    return ("const", float(x))


def add(*args: Expr) -> Expr:
    return ("add",) + tuple(args)


def mul(*args: Expr) -> Expr:
    return ("mul",) + tuple(args)


def sub(a: Expr, b: Expr) -> Expr:
    return ("sub", a, b)


def div(a: Expr, b: Expr) -> Expr:
    return ("div", a, b)


def mx(*args: Expr) -> Expr:
    return ("max",) + tuple(args)


def evaluate(expr: Expr, lookup) -> float:
    op = expr[0]
    if op == "const":
        return expr[1]
    if op == "ref":
        return lookup(expr[1])
    vals = [evaluate(e, lookup) for e in expr[1:]]
    if op == "add":
        return float(sum(vals))
    if op == "mul":
        out = 1.0
        for v in vals:
            out *= v
        return out
    if op == "sub":
        return vals[0] - vals[1]
    if op == "div":
        return vals[0] / vals[1]
    if op == "max":
        return max(vals)
    raise ValueError(f"unknown op {op}")


def refs(expr: Expr) -> list[str]:
    if expr[0] == "ref":
        return [expr[1]]
    if expr[0] == "const":
        return []
    out: list[str] = []
    for e in expr[1:]:
        out.extend(refs(e))
    return out


@dataclass
class Node:
    code: str
    label_en: str
    label_zh: str
    kind: str                      # input | calc
    unit: str = ""
    value: float | None = None     # inputs
    expr: Expr | None = None       # calcs
    group: str = "info"            # quantity, goods, logistics, vas, insurance, temporary_admission, duty, tax, economic, total
    element: str | None = None     # Incoterms cost element, when applicable
    payer: str | None = None       # buyer | seller | owner
    in_quote: bool = False
    note: str = ""

    def as_dict(self, value: float) -> dict:
        return {"code": self.code, "label_en": self.label_en, "label_zh": self.label_zh, "kind": self.kind,
                "unit": self.unit, "value": value, "group": self.group, "element": self.element,
                "payer": self.payer, "in_quote": self.in_quote, "note": self.note}


@dataclass
class RateBook:
    """Assumptions register for one template: every rate used by any option, with provenance."""
    rates: dict[str, dict] = field(default_factory=dict)

    def add(self, pid: str, value: float, desc_en: str, desc_zh: str, ref, label: str | None = None,
            unit: str | None = None) -> Expr:
        p = ref.used.get(pid) if ref is not None else None
        entry = {"id": pid, "value": float(value), "desc_en": desc_en, "desc_zh": desc_zh,
                 "unit": unit if unit is not None else (p.unit if p else ""),
                 "label": label or (p.label if p else "ASSUMPTION"),
                 "sources": list(p.sources) if p else [], "statement": p.statement if p else None}
        old = self.rates.get(pid)
        if old is not None and abs(old["value"] - entry["value"]) > 1e-12:
            raise ValueError(f"rate {pid} registered with two values")
        self.rates[pid] = entry
        return R(pid)

    def value(self, pid: str) -> float:
        return self.rates[pid]["value"]


class Calc:
    """Ordered nodes of one option's cost build-up."""

    def __init__(self, prefix: str, ratebook: RateBook) -> None:
        self.prefix = prefix
        self.nodes: dict[str, Node] = {}
        self.ratebook = ratebook
        self._cache: dict[str, float] = {}

    def code(self, short: str) -> str:
        return f"{self.prefix}.{short}"

    def input(self, short: str, value: float, label_en: str, label_zh: str, unit: str = "",
              group: str = "quantity", note: str = "") -> Expr:
        c = self.code(short)
        if c in self.nodes:
            raise ValueError(f"duplicate node {c}")
        self.nodes[c] = Node(c, label_en, label_zh, "input", unit, float(value), None, group, note=note)
        return R(c)

    def calc(self, short: str, expr: Expr, label_en: str, label_zh: str, unit: str = "USD", group: str = "logistics",
             element: str | None = None, payer: str | None = None, in_quote: bool = False, note: str = "") -> Expr:
        c = self.code(short)
        if c in self.nodes:
            raise ValueError(f"duplicate node {c}")
        self.nodes[c] = Node(c, label_en, label_zh, "calc", unit, None, expr, group, element, payer, in_quote, note)
        return R(c)

    def value(self, code: str) -> float:
        if code in self._cache:
            return self._cache[code]
        if code in self.ratebook.rates:
            return self.ratebook.value(code)
        node = self.nodes[code]
        v = node.value if node.kind == "input" else evaluate(node.expr, self.value)
        self._cache[code] = float(v)
        return float(v)

    def table(self) -> list[dict]:
        return [n.as_dict(self.value(c)) for c, n in self.nodes.items()]

    def sum_where(self, pred) -> float:
        return float(sum(self.value(c) for c, n in self.nodes.items() if n.kind == "calc" and pred(n)))
