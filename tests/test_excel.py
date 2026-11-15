"""The quotation workbook's live formulas must reproduce the Python totals (independent evaluator)."""
from __future__ import annotations

import json

import pytest

from cbsk import excel, pipeline, xlsx_eval
from cbsk.io import RESULTS

KEYS = ("TOTAL_QUOTE", "TOTAL_DUTY", "TOTAL_TAX", "TOTAL_ECONOMIC", "TOTAL_LANDED", "PER_UNIT")


@pytest.mark.parametrize("name", pipeline.TEMPLATES_ORDER)
def test_formula_totals_equal_python_totals(runs, tmp_path, name):
    res, side = runs[name]
    path = tmp_path / f"{name}.xlsx"
    cells = excel.write_workbook(res, side["calcs"], side["ratebook"], path)
    wb = xlsx_eval.Workbook(path)
    for sheet, addr, _ in wb.formulas():            # every formula parses and evaluates
        wb.value(sheet, addr)
    for oid, calc in side["calcs"].items():
        for key in KEYS:
            code = f"{calc.prefix}.{key}"
            assert wb.value(*cells[code]) == pytest.approx(calc.value(code), rel=1e-12, abs=1e-9), code
        for code, n in calc.nodes.items():         # every line, not only totals
            assert wb.value(*cells[code]) == pytest.approx(calc.value(code), rel=1e-12, abs=1e-9), code
    for lane, s in zip(res["lanes"], res["summary"]):
        assert wb.value(*cells[f"summary.{lane['id']}.landed"]) == pytest.approx(s["annual_landed"], rel=1e-12)
        assert wb.value(*cells[f"summary.{lane['id']}.per_unit"]) == pytest.approx(s["cost_per_unit"], rel=1e-12)
    assert wb.value(*cells["summary.total.landed"]) == pytest.approx(sum(s["annual_landed"] for s in res["summary"]))
    for rid, r in side["ratebook"].rates.items():
        assert wb.value(*cells[rid]) == pytest.approx(r["value"])


@pytest.mark.parametrize("name", pipeline.TEMPLATES_ORDER)
def test_committed_workbook_matches_committed_results(name):
    wb = xlsx_eval.Workbook(RESULTS / name / "quotation.xlsx")
    committed = json.loads((RESULTS / name / "results.json").read_text(encoding="utf-8"))
    ws = wb.wb["Summary"]
    header_row = next(r for r in range(1, 12) if ws.cell(row=r, column=1).value == "Lane")
    for i, s in enumerate(committed["summary"]):
        row = header_row + 1 + i
        assert ws.cell(row=row, column=1).value == s["lane"]
        assert wb.value("Summary", f"G{row}") == pytest.approx(s["annual_landed"], rel=1e-9, abs=1e-4)
        assert wb.value("Summary", f"I{row}") == pytest.approx(s["cost_per_unit"], rel=1e-9, abs=1e-6)


def test_evaluator_rejects_unsupported_functions(tmp_path):
    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "S"
    ws["A1"] = 2
    ws["A2"] = "=VLOOKUP(A1,A1:A1,1)"
    ws["A3"] = '=IF(COUNT(B1:B3)=0,"",AVERAGE(B1:B3))'
    ws["A4"] = "=-A1^2+MAX(A1,3)*(A1-1)/2"
    path = tmp_path / "t.xlsx"
    wb.save(path)
    book = xlsx_eval.Workbook(path)
    with pytest.raises(xlsx_eval.FormulaError):
        book.value("S", "A2")
    assert book.value("S", "A3") == ""                  # lazy IF: AVERAGE of an empty range is not evaluated
    assert book.value("S", "A4") == pytest.approx(4 + 3 * 1 / 2)   # Excel: negation binds tighter than ^
