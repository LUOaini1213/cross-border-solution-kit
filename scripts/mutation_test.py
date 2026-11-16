"""Mutation testing: break the core logic on purpose and check that the tests notice.

Each mutant replaces one exact snippet (which must occur exactly once) in a copy of the repository
(.mutation_work/, git-ignored), runs the unit tests (pytest -m "not golden", stop at first failure) and,
only if they all pass, the golden regression tests. A mutant is killed when a run fails. Results go to
docs/mutation_report.json and docs/mutation_report.md.

    python scripts/mutation_test.py
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / ".mutation_work"
COPY = ["cbsk", "tests", "data", "templates", "results", "docs", "scripts", "README.md", "LICENSE", "pyproject.toml",
        ".gitattributes", ".gitignore", "requirements.txt"]

MUTANTS = [
    ("cbsk/flows/common.py", "return int(math.ceil(x / cap - 1e-9)) if x > 0 else 0", "return int(x / cap) if x > 0 else 0",
     "container count rounds down instead of up"),
    ("cbsk/flows/b2b.py", "wm_by_month = [max(q * v, q * g / 1000.0,", "wm_by_month = [min(q * v, q * g / 1000.0,",
     "LCL freight tonnes use min instead of max(W, M)"),
    ("cbsk/flows/b2b.py", "chg_by_month = [max(q * g, q * v * vol, mink) for q in per_ship]",
     "chg_by_month = [max(q * g, mink) for q in per_ship]", "air chargeable weight ignores volumetric weight"),
    ("cbsk/flows/b2b.py", "mul(rate, factor, add(GOODS, *to_border))", "mul(rate, factor, add(GOODS))",
     "insured value excludes freight to the border (not CIF)"),
    ("cbsk/flows/b2b.py", "add(gi, mul(div(gi, GOODS), freight_ins))", "add(gi, mul(div(gi, GOODS), C(0.0)))",
     "customs value on FOB instead of CIF"),
    ("cbsk/flows/b2b.py", "mul(r_st, add(cv, duty), sub(C(1.0), schc))", "mul(r_st, cv, sub(C(1.0), schc))",
     "sales tax base omits import duty"),
    ("cbsk/flows/b2b.py", "sub(C(1.0), schc)", "C(1.0)", "Schedule C exemption ignored"),
    ("cbsk/flows/b2b.py", 'col = {"MFN": "mfn_import", "ACFTA": "acfta_current", "RCEP": "rcep_current"}[fr["chosen"]["scheme"]]',
     'col = "mfn_import"', "chosen FTA rate not applied (always MFN)"),
    ("cbsk/duties.py", "st = 0.0 if schedule_c_exempt else sales_tax_rate * (cv + duty)",
     "st = 0.0 if schedule_c_exempt else sales_tax_rate * cv", "my_import_line: sales tax base omits duty"),
    ("cbsk/duties.py", "is_lvg = retail * fx <= lvg_limit", "is_lvg = retail * fx < lvg_limit",
     "Malaysian LVG limit made exclusive (RM500 itself no longer LVG)"),
    ("cbsk/duties.py", 'if channel == "air_courier":\n            dm_limit', 'if channel in ("air_courier", "road"):\n            dm_limit',
     "Malaysian de minimis wrongly applied to road imports"),
    ("cbsk/duties.py", "if retail <= dm:", "if retail < dm:", "Indonesian USD 3 de minimis made exclusive"),
    ("cbsk/duties.py", 'pph = float(ref.get("regimes.ID.pph_specific_rate")) * base if (row and row["pph"]) else 0.0',
     "pph = 0.0", "Indonesian 5% income tax on listed consignments dropped"),
    ("cbsk/duties.py", 'return TaxResult("ID consignment USD 3-1,500", duty, vat_eff * base, pph,',
     'return TaxResult("ID consignment USD 3-1,500", duty, vat_eff * cif, pph,', "Indonesian VAT base omits duty"),
    ("cbsk/duties.py", 'if cif * fx <= float(ref.get("regimes.TH.duty_exemption_customs_value_thb")):',
     "if cif * fx <= 1500.0:", "Thailand keeps the pre-2026 THB 1,500 exemption"),
    ("cbsk/duties.py", 'if retail * fx <= float(ref.get("regimes.PH.deminimis_fob_php")):',
     'if cif * fx <= float(ref.get("regimes.PH.deminimis_fob_php")):', "Philippine de minimis tested on CIF instead of FOB"),
    ("cbsk/duties.py", '"regimes.SG.tis_security_share_registered" if gst_registered',
     '"regimes.SG.tis_security_share_registered" if not gst_registered', "TIS security shares swapped"),
    ("cbsk/duties.py", 'return min(avail, key=lambda o: (round(o["rate"], 9), order[o["scheme"]]))',
     'return max(avail, key=lambda o: (round(o["rate"], 9), order[o["scheme"]]))', "tariff choice picks the highest rate"),
    ("cbsk/duties.py", 'rcep_ok = origin in comp["RCEP"]["parties"] and (rvc_ok or cth_met is True)',
     'rcep_ok = origin in comp["RCEP"]["parties"]', "RCEP origin granted without RVC40 or CTH evidence"),
    ("data/reference/incoterms_2020.yaml", "FCA: {export_packing: S, loading_at_origin: S, pre_carriage: B, export_clearance: S,",
     "FCA: {export_packing: S, loading_at_origin: S, pre_carriage: B, export_clearance: B,", "FCA export clearance put on the buyer"),
    ("cbsk/pareto.py", "and any(x < y for x, y in zip(a, b))", "and any(x <= y for x, y in zip(a, b))",
     "Pareto dominance without the strict-improvement condition"),
    ("cbsk/pareto.py", 'if o["metrics"]["on_time_probability"] >= target_probability', "if True",
     "recommendation ignores the on-time target"),
    ("cbsk/seeds.py", 'return (int(base) ^ zlib.crc32("|".join(parts).encode("utf-8"))) & 0xFFFFFFFF',
     'return (int(base) ^ hash("|".join(parts))) & 0xFFFFFFFF', "seed from Python's salted hash() (not reproducible)"),
    ("cbsk/transit.py", "sigma = (math.log(q3) - math.log(q1)) / (2.0 * Z75)", "sigma = (math.log(q3) - math.log(q1)) / 2.0",
     "lognormal fit to quartiles without the normal-quantile scaling"),
    ("cbsk/transit.py", '"on_time_probability": float(np.mean(samples <= target_days)),',
     '"on_time_probability": float(np.mean(samples < target_days)),', "arrival on the target day counted as late"),
    ("cbsk/legs.py", "p = min(1.0, max(0.0, n))", "p = 1.0", "every shipment transshipped regardless of LPI data"),
    ("cbsk/compliance.py", 'ok = purpose in ta["ata_sg_import_purposes"]',
     'ok = purpose in ta["ata_sg_import_purposes"] or purpose == "repair_in_sg"', "ATA Carnet accepted for repair"),
    ("cbsk/compliance.py", 'return sum(1 for f in flags if f["id"] in relevant and f["severity"] in ("medium", "high"))',
     'return sum(1 for f in flags if f["severity"] in ("medium", "high"))', "every medium flag raises the hold probability"),
    ("cbsk/compliance.py", "max(0.0, p90 - p50)", "max(0.0, p50 - p90)", "risk score ignores transit spread"),
    ("cbsk/excel.py", 'return "(" + "*".join(parts) + ")"', 'return "(" + "+".join(parts) + ")"',
     "workbook writes products as sums"),
    ("cbsk/flows/temporary.py", "mul(MOVES, gst, VALUE, nps, add(C(1.0), mul(C(-1.0), wsh)))", "mul(MOVES, gst, VALUE, nps)",
     "GST charged on warranty repairs"),
    ("cbsk/flows/parcel.py", "base = mul(N, RET)                       # LVG sales tax on the sale price, excluding transport",
     "base = mul(N, CV)", "LVG sales tax on price plus shipping instead of the sale price"),
]


def rmtree(path: Path) -> None:
    """Remove a tree including read-only files (git object files are read-only on Windows)."""
    def onerror(func, p, _exc):
        os.chmod(p, stat.S_IWRITE)
        func(p)
    if path.exists():
        shutil.rmtree(path, onerror=onerror)


def run(args: list[str], timeout: int = 600) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=WORK, capture_output=True, text=True, timeout=timeout)


def first_failure(output: str) -> str:
    m = re.search(r"^(FAILED|ERROR) (\S+)", output, re.MULTILINE)
    return m.group(2) if m else output.strip().splitlines()[-1] if output.strip() else "?"


def write_markdown(report: dict) -> None:
    rows, killed, n_tests = report["mutants"], report["killed"], report["tests_collected"]
    lines = ["# Mutation report", "",
             f"Run {report['run_date']}: **{killed}/{len(rows)} mutants killed** ({report['killed_by_unit_tests']} by the unit tests, "
             f"{report['killed_by_golden_only']} only by the golden regression test, {report['survived']} survived). "
             f"{n_tests} tests collected.", "",
             "Each mutant changes one snippet of core logic in a copy of the repository; the unit tests run first "
             "(`pytest -m \"not golden\" -x`), and the golden comparison with the committed results only if they all pass.", "",
             "The last column is the first test that failed, in file order. Where it names a test that looks unrelated "
             "(`test_singapore_carnet_scope_in_template` for the Indonesian VAT base and the Malaysian LVG base), the failure is the "
             "pipeline's own cross-check: `flows/parcel.py` compares the workbook formulas' tax total with `duties.parcel_taxes` and "
             "refuses to build when they disagree, which fails the shared pipeline fixture before the hand-worked tests "
             "(`test_indonesia_consignment_band_by_hand`, `test_air_parcel_chargeable_weight_and_freight_by_hand`) are reached. "
             "Both hand-worked tests were run separately against these two mutants (with the cross-check disabled for the second) "
             "and fail as well.", "",
             "| # | File | Mutation | Killed by | First failing test |", "|---|---|---|---|---|"]
    for i, r in enumerate(rows, 1):
        lines.append(f"| {i} | `{r['file']}` | {r['mutation']} | {r['killed_by']} | `{r['first_failure']}` |")
    survivors = [r for r in rows if not r["killed"]]
    lines += ["", "## Survivors", ""]
    lines += [f"- {r['mutation']} (`{r['file']}`)" for r in survivors] or ["None."]
    (ROOT / "docs" / "mutation_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    if "--render-only" in sys.argv:      # rebuild the Markdown from docs/mutation_report.json
        write_markdown(json.loads((ROOT / "docs" / "mutation_report.json").read_text(encoding="utf-8")))
        return 0
    rmtree(WORK)
    WORK.mkdir()
    for item in COPY:
        src = ROOT / item
        if src.is_dir():
            shutil.copytree(src, WORK / item, ignore=shutil.ignore_patterns("__pycache__"))
        else:
            shutil.copy2(src, WORK / item)
    for args in (["git", "init", "-q"], ["git", "add", "-A"]):
        run(args)
    py = sys.executable
    base = run([py, "-m", "pytest", "-q", "-p", "no:cacheprovider"])
    if base.returncode != 0:
        print(base.stdout[-3000:])
        raise SystemExit("baseline test run fails; fix before mutation testing")
    collected = run([py, "-m", "pytest", "--collect-only", "-q", "-p", "no:cacheprovider"]).stdout
    m = re.search(r"(\d+) tests? collected", collected)
    n_tests = int(m.group(1)) if m else (sum(int(x) for x in re.findall(r"^\S+\.py: (\d+)$", collected, re.M)) or None)
    rows = []
    for path, old, new, why in MUTANTS:
        target = WORK / path
        original = target.read_text(encoding="utf-8")
        if original.count(old) != 1:
            raise SystemExit(f"mutant snippet must occur exactly once in {path}: {old!r} ({original.count(old)})")
        target.write_text(original.replace(old, new), encoding="utf-8", newline="\n")
        t0 = time.time()
        try:
            unit = run([py, "-m", "pytest", "-x", "-q", "-m", "not golden", "-p", "no:cacheprovider"])
            by = "unit" if unit.returncode != 0 else None
            detail = first_failure(unit.stdout + unit.stderr) if by else ""
            if by is None:
                gold = run([py, "-m", "pytest", "-x", "-q", "-m", "golden", "-p", "no:cacheprovider"])
                if gold.returncode != 0:
                    by, detail = "golden", first_failure(gold.stdout + gold.stderr)
        finally:
            target.write_text(original, encoding="utf-8", newline="\n")
        rows.append({"file": path, "mutation": why, "killed": by is not None, "killed_by": by or "survived",
                     "first_failure": detail, "seconds": round(time.time() - t0, 1)})
        print(f"[{'KILLED' if by else 'SURVIVED'}] {why} ({by or '-'}: {detail})", flush=True)
    rmtree(WORK)
    killed = sum(r["killed"] for r in rows)
    report = {"run_date": dt.date.today().isoformat(), "total": len(rows), "killed": killed,
              "killed_by_unit_tests": sum(r["killed_by"] == "unit" for r in rows),
              "killed_by_golden_only": sum(r["killed_by"] == "golden" for r in rows),
              "survived": len(rows) - killed, "tests_collected": n_tests, "mutants": rows}
    docs = ROOT / "docs"
    (docs / "mutation_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    write_markdown(report)
    # README numbers include the mutation score: re-render it so the repository stays consistent
    subprocess.run([py, str(ROOT / "scripts" / "build_all.py"), "--readme-only"], cwd=ROOT, check=True)
    print(f"{killed}/{len(rows)} killed")
    return 0 if killed == len(rows) else 1


if __name__ == "__main__":
    sys.exit(main())
