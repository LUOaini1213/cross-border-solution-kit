"""Rebuild every output offline: results JSON, quotation workbooks, bilingual proposals (Markdown, and PDF
when pandoc + Playwright are available), the monitoring templates, data provenance, the regulatory check
document and the README numbers.

    python scripts/build_all.py            # everything (PDF if the tools exist)
    python scripts/build_all.py --no-pdf   # skip PDFs
"""
from __future__ import annotations

import csv
import io as _io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from cbsk import docs, excel, pdf, pipeline, proposal  # noqa: E402
from cbsk.io import DOCS, RESULTS, write_json, write_text  # noqa: E402
from cbsk.plan import kpis  # noqa: E402
from cbsk.reference import Reference  # noqa: E402


def monitoring_csv(res: dict) -> str:
    buf = _io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    w.writerow(["lane", "kpi", "kpi_zh", "target", "better"] + months + ["trigger"])
    tgt = float(res["rfq"]["service"]["on_time_target_probability"])
    for lane, s in zip(res["lanes"], res["summary"]):
        for k in kpis(res["rfq"]["flow_type"], lane, s, tgt):
            w.writerow([lane["id"], k["en"], k["zh"], k["target"], k["better"]] + [""] * 12 + [k["trigger_en"]])
    return buf.getvalue()


def build(make_pdf: bool = True, out_root: Path = RESULTS, docs_root: Path = DOCS, readme_path: Path = ROOT / "README.md") -> dict:
    ref = Reference()
    all_results = {}
    for name in pipeline.TEMPLATES_ORDER:
        res, side = pipeline.run_template(name)
        out = out_root / name
        write_json(out / "results.json", res)
        excel.write_workbook(res, side["calcs"], side["ratebook"], out / "quotation.xlsx")
        md_en = proposal.render(res, "en", ref.statements, ref.sources)
        md_zh = proposal.render(res, "zh", ref.statements, ref.sources)
        write_text(out / "proposal_en.md", md_en)
        write_text(out / "proposal_zh.md", md_zh)
        write_text(out / "monitoring_template.csv", monitoring_csv(res))
        if make_pdf:
            print(name, pdf.build_pdf(md_en, md_zh, res["rfq"]["title_en"], out / "proposal.pdf"), flush=True)
        all_results[name] = json.loads((out / "results.json").read_text(encoding="utf-8"))
        print(f"{name}: " + "; ".join(f"{s['lane']} -> {s['option']} ({s['status']})" for s in res["summary"]), flush=True)
    summary = {name: res["summary"] for name, res in all_results.items()}
    write_json(out_root / "summary.json", summary)
    write_text(docs_root / "data_provenance.md", docs.provenance_md(all_results, ref.sources))
    log_path = docs_root / "regulatory_check_log.json"
    log = json.loads(log_path.read_text(encoding="utf-8")) if log_path.exists() else None
    write_text(docs_root / "regulatory_check.md", docs.regulatory_md(ref.statements, ref.sources, log))
    mut_path = docs_root / "mutation_report.json"
    mutation = json.loads(mut_path.read_text(encoding="utf-8")) if mut_path.exists() else None
    template = (docs_root / "README.template.md")
    if template.exists():
        values = docs.readme_values(all_results, ref.statements, mutation)
        write_text(readme_path, docs.render_template(template.read_text(encoding="utf-8"), values))
    return all_results


if __name__ == "__main__":
    build(make_pdf="--no-pdf" not in sys.argv)
