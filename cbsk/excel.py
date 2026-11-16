"""Quotation workbook: cost build-up with live formulas, assumptions register, options, compliance flags and
a post-go-live monitoring sheet."""
from __future__ import annotations

import datetime as dt
import re
import zipfile
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from .calc import Calc, RateBook
from .flows.common import MODE_LABELS, REGIME_LABELS
from .plan import kpis

HEAD = Font(bold=True)
TITLE = Font(bold=True, size=14)
FILL = PatternFill("solid", fgColor="DDE7F0")
TOTAL_KEYS = ("TOTAL_QUOTE", "TOTAL_DUTY", "TOTAL_TAX", "TOTAL_ECONOMIC", "TOTAL_LANDED", "PER_UNIT")
UNIT_NODE = {"move": "MOVES", "parcel": "PARCELS"}


def _num(x: float) -> str:
    r = repr(float(x))
    return r if "e" not in r and "inf" not in r else f"{x:.17g}"


class FormulaWriter:
    def __init__(self) -> None:
        self.cell: dict[str, tuple[str, str]] = {}   # code -> (sheet, A1)

    def ref(self, code: str, here: str) -> str:
        sheet, addr = self.cell[code]
        return addr if sheet == here else f"{sheet}!{addr}"

    def formula(self, expr: tuple, here: str) -> str:
        op = expr[0]
        if op == "const":
            v = expr[1]
            return f"({_num(v)})" if v < 0 else _num(v)
        if op == "ref":
            return self.ref(expr[1], here)
        parts = [self.formula(e, here) for e in expr[1:]]
        if op == "add":
            return "(" + "+".join(parts) + ")"
        if op == "mul":
            return "(" + "*".join(parts) + ")"
        if op == "sub":
            return f"({parts[0]}-{parts[1]})"
        if op == "div":
            return f"({parts[0]}/{parts[1]})"
        if op == "max":
            return "MAX(" + ",".join(parts) + ")"
        raise ValueError(op)


def _widths(ws, widths: dict[str, int]) -> None:
    for col, w in widths.items():
        ws.column_dimensions[col].width = w


def write_workbook(results: dict, calcs: dict[str, Calc], ratebook: RateBook, path: Path) -> dict:
    """Write the workbook; returns {node code: (sheet, cell)} for tests."""
    wb = Workbook()
    fw = FormulaWriter()
    summ = wb.active
    summ.title = "Summary"
    assum = wb.create_sheet("Assumptions")
    costs = wb.create_sheet("Costs")
    opts = wb.create_sheet("Options")
    comp = wb.create_sheet("Compliance")
    mon = wb.create_sheet("Monitoring")

    # ---- Assumptions register (rates referenced by formulas)
    assum.append(["id", "description", "说明", "value", "unit", "label", "sources", "statement"])
    for c in assum[1]:
        c.font = HEAD
        c.fill = FILL
    for i, rid in enumerate(sorted(ratebook.rates), start=2):
        r = ratebook.rates[rid]
        assum.append([rid, r["desc_en"], r["desc_zh"], r["value"], r["unit"], r["label"], ", ".join(r["sources"]),
                      r.get("statement") or ""])
        fw.cell[rid] = ("Assumptions", f"D{i}")
    _widths(assum, {"A": 46, "B": 52, "C": 34, "D": 14, "E": 18, "F": 14, "G": 40, "H": 24})

    # ---- Costs: one block per option; inputs are values, calculations are formulas
    costs.append(["code", "description", "说明", "unit", "value (USD unless unit says otherwise)", "group", "payer", "in quote", "note"])
    for c in costs[1]:
        c.font = HEAD
        c.fill = FILL
    row = 2
    for lane in results["lanes"]:
        for opt in lane["options"]:
            calc = calcs[opt["id"]]
            row += 1
            costs.cell(row=row, column=1, value=f"{lane['id']} | {opt['id']}").font = HEAD
            costs.cell(row=row, column=2, value=opt["label_en"]).font = HEAD
            costs.cell(row=row, column=3, value=opt["label_zh"]).font = HEAD
            row += 1
            for code in calc.nodes:
                fw.cell[code] = ("Costs", f"E{row}")
                row += 1
            row = row - len(calc.nodes)
            for code, node in calc.nodes.items():
                costs.cell(row=row, column=1, value=code)
                costs.cell(row=row, column=2, value=node.label_en)
                costs.cell(row=row, column=3, value=node.label_zh)
                costs.cell(row=row, column=4, value=node.unit)
                if node.kind == "input":
                    costs.cell(row=row, column=5, value=float(node.value))
                else:
                    costs.cell(row=row, column=5, value="=" + fw.formula(node.expr, "Costs"))
                costs.cell(row=row, column=5).number_format = "#,##0.00"
                costs.cell(row=row, column=6, value=node.group)
                costs.cell(row=row, column=7, value=node.payer or "")
                costs.cell(row=row, column=8, value="Y" if node.in_quote else "")
                costs.cell(row=row, column=9, value=node.note)
                if node.group == "total":
                    for col in range(1, 6):
                        costs.cell(row=row, column=col).font = HEAD
                row += 1
    _widths(costs, {"A": 34, "B": 52, "C": 36, "D": 12, "E": 20, "F": 18, "G": 9, "H": 9, "I": 40})

    # ---- Summary
    rfq = results["rfq"]
    summ["A1"] = rfq["title_en"]
    summ["A1"].font = TITLE
    summ["A2"] = rfq["title_zh"]
    summ["A3"] = f"{rfq['rfq_id']} | {rfq['customer']} | issued {rfq['issue_date']} | valid {rfq['quote_validity_days']} days | {rfq['currency']}"
    summ["A4"] = ("Portfolio example: fictional customer, ILLUSTRATIVE freight and handling rates (not a tariff), duty/tax rates "
                  "labelled REAL only where checked on an official source. See the Assumptions sheet. Not tax or legal advice.")
    summ["A4"].alignment = Alignment(wrap_text=True)
    header = ["Lane", "Recommended option", "Quote (annual)", "Duties", "Taxes", "Carrying (economic)", "Landed (annual)",
              "Units / year", "Landed per unit", "P50 days", "P90 days", "On-time prob.", "Risk (0-100)", "Status"]
    summ.append([])
    summ.append(header)
    hdr = summ.max_row
    for c in summ[hdr]:
        c.font = HEAD
        c.fill = FILL
    first = hdr + 1
    for lane, s in zip(results["lanes"], results["summary"]):
        oid = s["option"]
        p = calcs[oid].prefix
        r = summ.max_row + 1
        unit_code = f"{p}.{UNIT_NODE.get(lane['unit'], 'UNITS')}"
        summ.append([lane["id"], s["label_en"],
                     "=" + fw.ref(f"{p}.TOTAL_QUOTE", "Summary"), "=" + fw.ref(f"{p}.TOTAL_DUTY", "Summary"),
                     "=" + fw.ref(f"{p}.TOTAL_TAX", "Summary"), "=" + fw.ref(f"{p}.TOTAL_ECONOMIC", "Summary"),
                     "=" + fw.ref(f"{p}.TOTAL_LANDED", "Summary"), "=" + fw.ref(unit_code, "Summary"),
                     f"=G{r}/H{r}", s["p50"], s["p90"], s["on_time_probability"], s["risk"], s["status"]])
        fw.cell[f"summary.{lane['id']}.landed"] = ("Summary", f"G{r}")
        fw.cell[f"summary.{lane['id']}.per_unit"] = ("Summary", f"I{r}")
        fw.cell[f"summary.{lane['id']}.quote"] = ("Summary", f"C{r}")
    last = summ.max_row
    summ.append(["Total (recommended options)", "", f"=SUM(C{first}:C{last})", f"=SUM(D{first}:D{last})",
                 f"=SUM(E{first}:E{last})", f"=SUM(F{first}:F{last})", f"=SUM(G{first}:G{last})"])
    fw.cell["summary.total.landed"] = ("Summary", f"G{summ.max_row}")
    fw.cell["summary.total.quote"] = ("Summary", f"C{summ.max_row}")
    for c in summ[summ.max_row]:
        c.font = HEAD
    for rr in summ.iter_rows(min_row=first, max_row=summ.max_row, min_col=3, max_col=9):
        for c in rr:
            c.number_format = "#,##0.00"
    _widths(summ, {"A": 30, "B": 44, "C": 16, "D": 14, "E": 14, "F": 16, "G": 16, "H": 12, "I": 14, "J": 10, "K": 10,
                   "L": 12, "M": 12, "N": 16})

    # ---- Options
    opts.append(["Lane", "Option", "Label", "方案", "Landed per unit", "P50", "P90", "On-time prob.", "Risk", "Pareto",
                 "Recommended", "Dominated by"])
    for c in opts[1]:
        c.font = HEAD
        c.fill = FILL
    for lane in results["lanes"]:
        for o in lane["options"]:
            opts.append([lane["id"], o["id"], o["label_en"], o["label_zh"], "=" + fw.ref(f"{calcs[o['id']].prefix}.PER_UNIT", "Options"),
                         o["metrics"]["p50"], o["metrics"]["p90"], o["metrics"]["on_time_probability"], o["metrics"]["risk"],
                         "Y" if o["pareto"] else "", "Y" if o["id"] == lane["recommendation"]["chosen"] else "",
                         ", ".join(o["dominated_by"])])
        for x in lane["excluded"]:
            en_l, zh_l = MODE_LABELS.get(x.get("mode"), None) or REGIME_LABELS.get(x.get("regime"), (x.get("regime"),) * 2)
            opts.append([lane["id"], f"not offered: {en_l}", x["reason_en"], f"未纳入：{zh_l}——{x['reason_zh']}"])
    _widths(opts, {"A": 8, "B": 34, "C": 50, "D": 40, "E": 16, "F": 8, "G": 8, "H": 12, "I": 8, "J": 8, "K": 12, "L": 40})

    # ---- Compliance
    comp.append(["Lane", "Scope", "Flag", "Severity", "Verified", "Finding", "发现", "Mitigation", "应对", "Statements"])
    for c in comp[1]:
        c.font = HEAD
        c.fill = FILL
    for f in results["template_flags"]:
        comp.append(["all", "template", f["id"], f["severity"], {True: "Y", False: "N", None: "-"}[f["verified"]], f["en"], f["zh"],
                     f["mitigation_en"], f["mitigation_zh"], ", ".join(f["statements"])])
    for lane in results["lanes"]:
        seen = set()
        for f in lane["lane_flags"]:
            seen.add(f["id"])
            scope = ", ".join(f["modes"]) if f.get("modes") else "lane"
            comp.append([lane["id"], scope, f["id"], f["severity"], {True: "Y", False: "N", None: "-"}[f["verified"]], f["en"], f["zh"],
                         f["mitigation_en"], f["mitigation_zh"], ", ".join(f["statements"])])
        for o in lane["options"]:
            for f in o["flags"]:
                if f["id"] in seen:
                    continue
                comp.append([lane["id"], o["id"], f["id"], f["severity"], {True: "Y", False: "N", None: "-"}[f["verified"]], f["en"], f["zh"],
                             f["mitigation_en"], f["mitigation_zh"], ", ".join(f["statements"])])
    for col in "FGHI":
        for c in comp[col]:
            c.alignment = Alignment(wrap_text=True, vertical="top")
    _widths(comp, {"A": 6, "B": 22, "C": 24, "D": 9, "E": 8, "F": 60, "G": 46, "H": 46, "I": 36, "J": 30})

    # ---- Monitoring (post go-live): monthly actuals are entered by the user
    mon["A1"] = "Post-go-live monitoring sheet - enter monthly actuals in columns E:P"
    mon["A1"].font = HEAD
    mon.append(["Lane", "KPI", "Target", "Better", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct",
                "Nov", "Dec", "YTD average", "Status", "Trigger / action"])
    for c in mon[2]:
        c.font = HEAD
        c.fill = FILL
    for lane, s in zip(results["lanes"], results["summary"]):
        for k in kpis(results["rfq"]["flow_type"], lane, s, float(results["rfq"]["service"]["on_time_target_probability"])):
            r = mon.max_row + 1
            op = "<=" if k["better"] == "lower" else ">="
            mon.append([lane["id"], k["en"], k["target"], k["better"]] + [None] * 12 +
                       [f'=IF(COUNT(E{r}:P{r})=0,"",AVERAGE(E{r}:P{r}))',
                        f'=IF(Q{r}="","",IF(Q{r}{op}C{r},"OK","REVIEW"))', k["trigger_en"]])
    _widths(mon, {"A": 6, "B": 46, "C": 10, "D": 8, "Q": 12, "R": 10, "S": 60})

    wb.properties.creator = "cross-border-solution-kit"
    wb.properties.created = dt.datetime(2026, 11, 15)
    wb.properties.modified = dt.datetime(2026, 11, 15)
    path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(path)
    _normalise_xlsx(path)
    return dict(fw.cell)


FIXED_TIME = (2026, 11, 15, 0, 0, 0)


def _normalise_xlsx(path: Path) -> None:
    """Make the saved workbook byte-reproducible: fixed zip entry times and a fixed 'modified' stamp
    (openpyxl writes the current time into both), so a rebuild does not dirty the repository."""
    with zipfile.ZipFile(path) as zin:
        items = [(info.filename, zin.read(info.filename)) for info in zin.infolist()]
    stamp = "%04d-%02d-%02dT%02d:%02d:%02dZ" % FIXED_TIME
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zout:
        for name, data in items:
            if name == "docProps/core.xml":
                data = re.sub(rb"(<dcterms:(?:modified|created)[^>]*>)[^<]*(</dcterms:)", lambda m: m.group(1) + stamp.encode() + m.group(2), data)
            info = zipfile.ZipInfo(name, date_time=FIXED_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o600 << 16
            zout.writestr(info, data)
