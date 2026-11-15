"""Small I/O helpers. All text is written as UTF-8 with LF line endings so files hash the same on
Windows and Linux."""
from __future__ import annotations

import csv
import datetime as dt
import json
import math
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
REFERENCE = DATA / "reference"
PUBLIC = DATA / "public"
TEMPLATES = ROOT / "templates"
RESULTS = ROOT / "results"
DOCS = ROOT / "docs"


def load_yaml(path: Path) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def read_csv(path: Path) -> list[dict[str, str]]:
    with open(path, "r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not text.endswith("\n"):
        text += "\n"
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def clean_floats(obj: Any, ndigits: int = 6) -> Any:
    """Round floats for stable JSON (results are compared with a tolerance anyway); dates become ISO strings."""
    if isinstance(obj, (dt.date, dt.datetime)):
        return obj.isoformat()
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            raise ValueError("non-finite float in results")
        r = round(obj, ndigits)
        return 0.0 if r == 0 else r
    if isinstance(obj, dict):
        return {str(k): clean_floats(v, ndigits) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [clean_floats(v, ndigits) for v in obj]
    return obj


def write_json(path: Path, obj: Any) -> None:
    write_text(path, json.dumps(clean_floats(obj), indent=2, sort_keys=True, ensure_ascii=False))


def read_json(path: Path) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
