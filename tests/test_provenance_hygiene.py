"""Provenance completeness, regulatory-statement integrity, README rendering and repository hygiene."""
from __future__ import annotations

import json
import re
import subprocess

import pytest

from cbsk import docs, pipeline
from cbsk.io import DOCS, RESULTS, ROOT, load_yaml
from cbsk.reference import LABELS

METHODS = {"html", "pdf", "ezhs", "image", "manual"}


def _committed():
    return {n: json.loads((RESULTS / n / "results.json").read_text(encoding="utf-8")) for n in pipeline.TEMPLATES_ORDER}


def test_sources_have_url_and_access_date(ref):
    for sid, s in ref.sources.items():
        assert s["url"].startswith("https://"), sid
        assert str(s["accessed"]) == "2026-11-15", sid
        assert s["kind"] in {"official", "intergovernmental", "index", "data", "secondary"}, sid


def test_statements_are_well_formed(ref):
    for sid, st in ref.statements.items():
        assert st["status"] in {"verified", "corrected", "not_verified"}, sid
        assert st["en"].strip() and st["zh"].strip(), sid
        assert st["check"]["method"] in METHODS, sid
        for s in st["sources"]:
            assert s in ref.sources, (sid, s)
        if st["status"] in ("verified", "corrected"):
            assert st["sources"], f"{sid}: a verified statement needs a source"
            assert all(ref.sources[s]["kind"] != "secondary" for s in st["sources"][:1]), \
                f"{sid}: the first source of a verified statement must not be secondary"
        if st["check"]["method"] in ("html", "pdf"):
            assert st["check"]["phrase"], sid
            assert st["check"]["source"] in st["sources"], sid


def test_every_parameter_is_labelled_and_real_ones_are_sourced(ref):
    for name, res in _committed().items():
        for p in res["provenance"] + [dict(a, note=a.get("desc_en", "")) for a in res["assumptions"]]:
            assert p["label"] in LABELS, (name, p["id"])
            if p["label"] == "REAL":
                assert p["sources"], (name, p["id"])
                for s in p["sources"]:
                    assert s in ref.sources, (name, p["id"], s)


def test_unverified_statements_never_back_a_real_rate(ref):
    for name, res in _committed().items():
        for a in res["assumptions"]:
            for sid in [x for x in str(a.get("statement") or "").split(",") if x]:
                if ref.statements[sid]["status"] == "not_verified":
                    assert a["label"] != "REAL", (name, a["id"], sid)


def test_flags_cite_existing_statements(ref):
    for name, res in _committed().items():
        for sid in res["statements_used"]:
            assert sid in ref.statements, (name, sid)
        for ln in res["lanes"]:
            for f in ln["lane_flags"] + [f for o in ln["options"] for f in o["flags"]]:
                for sid in f["statements"]:
                    assert sid in ref.statements, (name, f["id"], sid)
                if f["verified"] is True:     # a "verified" finding must rest on verified statements only
                    assert f["statements"], (name, f["id"])
                    assert all(ref.statements[s]["status"] in ("verified", "corrected") for s in f["statements"]), (name, f["id"])
                if f["verified"] is None:     # operational finding, no regulatory claim
                    assert f["statements"] == [], (name, f["id"])


def test_provenance_doc_lists_every_parameter():
    text = (DOCS / "data_provenance.md").read_text(encoding="utf-8")
    for name, res in _committed().items():
        for p in res["provenance"] + res["assumptions"]:
            assert f"`{p['id']}`" in text, (name, p["id"])


def test_regulatory_check_doc_lists_every_statement(ref):
    text = (DOCS / "regulatory_check.md").read_text(encoding="utf-8")
    for sid in ref.statements:
        assert f"`{sid}`" in text


def test_readme_is_rendered_from_results(ref):
    mut_path = DOCS / "mutation_report.json"
    mutation = json.loads(mut_path.read_text(encoding="utf-8")) if mut_path.exists() else None
    values = docs.readme_values(_committed(), ref.statements, mutation)
    expected = docs.render_template((DOCS / "README.template.md").read_text(encoding="utf-8"), values)
    assert (ROOT / "README.md").read_text(encoding="utf-8") == expected + ("" if expected.endswith("\n") else "\n")


def _tracked_text_files():
    out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.split()
    return [ROOT / p for p in out if not p.endswith((".xlsx", ".pdf", ".png"))]


def test_text_files_use_lf_line_endings():
    files = _tracked_text_files()
    assert files, "git ls-files returned nothing"
    bad = [str(p.relative_to(ROOT)) for p in files if p.exists() and b"\r\n" in p.read_bytes()]
    assert bad == []


FORBIDDEN = [r"\brecruit", r"\bjob application", r"\bhiring\b", r"\binterview", r"\bDHL\b", r"\bMaersk\b", r"\bMSC\b",
             r"\bOOCL\b", r"\bFedEx\b", r"\bKuehne", r"\bSchenker\b", r"\bExpeditors\b", r"\bCEVA\b", r"\bShopee\b",
             r"\bLazada\b", r"\bNinja ?Van\b", r"\bKTMB\b", r"\bCOSCO\b", r"\bEvergreen\b"]


def test_no_employer_customer_or_carrier_names():
    hits = []
    for p in _tracked_text_files():
        if not p.exists() or p.name == "test_provenance_hygiene.py":
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        for pat in FORBIDDEN:
            if re.search(pat, text):
                hits.append((str(p.relative_to(ROOT)), pat))
    assert hits == []


def test_licence_and_customers():
    lic = (ROOT / "LICENSE").read_text(encoding="utf-8")
    assert "MIT License" in lic and "Copyright (c) 2026 Wenjie Luo (LUOaini1213)" in lic
    for name in pipeline.TEMPLATES_ORDER:
        rfq = load_yaml(ROOT / "templates" / name / "rfq.yaml")
        assert rfq["customer"] == "Customer A (fictional)"
