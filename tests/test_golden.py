"""Golden test: a fresh pipeline run must reproduce the committed results and generated documents."""
from __future__ import annotations

import json
import math

import pytest

from cbsk import docs, pipeline, proposal
from cbsk.io import DOCS, RESULTS, ROOT, clean_floats

pytestmark = pytest.mark.golden


def _compare(a, b, path="$"):
    if isinstance(a, dict):
        assert isinstance(b, dict) and set(a) == set(b), f"{path}: keys differ: {set(a) ^ set(b)}"
        for k in a:
            _compare(a[k], b[k], f"{path}.{k}")
    elif isinstance(a, list):
        assert isinstance(b, list) and len(a) == len(b), f"{path}: length {len(a)} vs {len(b)}"
        for i, (x, y) in enumerate(zip(a, b)):
            _compare(x, y, f"{path}[{i}]")
    elif isinstance(a, float) or isinstance(b, float):
        assert math.isclose(float(a), float(b), rel_tol=1e-9, abs_tol=2e-6), f"{path}: {a} vs {b}"
    else:
        assert a == b, f"{path}: {a!r} vs {b!r}"


@pytest.mark.parametrize("name", pipeline.TEMPLATES_ORDER)
def test_results_reproduce(runs, name):
    res, _ = runs[name]
    fresh = json.loads(json.dumps(clean_floats(res), sort_keys=True, ensure_ascii=False))
    committed = json.loads((RESULTS / name / "results.json").read_text(encoding="utf-8"))
    _compare(fresh, committed)


@pytest.mark.parametrize("name", pipeline.TEMPLATES_ORDER)
def test_proposals_reproduce(runs, ref, name):
    res, _ = runs[name]
    res = json.loads(json.dumps(clean_floats(res), sort_keys=True, ensure_ascii=False))
    for lang in ("en", "zh"):
        text = proposal.render(res, lang, ref.statements, ref.sources)
        assert text == (RESULTS / name / f"proposal_{lang}.md").read_text(encoding="utf-8"), (name, lang)


def test_generated_docs_reproduce(runs, ref):
    results = {n: json.loads((RESULTS / n / "results.json").read_text(encoding="utf-8")) for n in pipeline.TEMPLATES_ORDER}
    assert docs.provenance_md(results, ref.sources) == (DOCS / "data_provenance.md").read_text(encoding="utf-8")
    log_path = DOCS / "regulatory_check_log.json"
    log = json.loads(log_path.read_text(encoding="utf-8")) if log_path.exists() else None
    assert docs.regulatory_md(ref.statements, ref.sources, log) == (DOCS / "regulatory_check.md").read_text(encoding="utf-8")
