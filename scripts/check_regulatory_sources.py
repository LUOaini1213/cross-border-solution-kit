"""Second, separate pass over the regulatory statements: fetch every cited source again and look for the
evidence phrase recorded with each statement. Network script (not used by the tests).

Writes docs/regulatory_check_log.json; scripts/build_all.py renders it into docs/regulatory_check.md.
Statements whose source cannot be read by a script (image-only gazette page, blocked sites, secondary-only
evidence) are logged as `manual` and were re-read by hand; the note field says what was checked.

    python -m pip install -r requirements-fetch.txt     # pymupdf for PDF text
    python scripts/check_regulatory_sources.py
"""
from __future__ import annotations

import csv
import datetime as dt
import html
import io
import json
import re
import ssl
import subprocess
import sys
import tempfile
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cbsk.io import load_yaml  # noqa: E402

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
INSECURE = {"my_lvg_guide"}          # the portal's TLS certificate had expired on the access date
MANUAL_NOTES = {
    "TH-DUTY-1BAHT": "Re-rendered the Royal Gazette page image and re-read items 1-4 (revokes 191/2561; exemption for goods each priced <= 1 baht; price = customs value; in force 1 Jan 2026).",
    "MY-ACFTA-UPDATE": "ezHS ACFTA/RCEP tables still show 'being updated'; amendment product list not found on an official page.",
    "MY-CKD-CLASSIFICATION": "Classification of the fictional kit is not something a source can confirm; CKD tariff lines re-read in ezHS and the 2022 order.",
    "ID-IMPORT-VALUE": "Statutory definition of import value not retrieved; kept as an assumption.",
    "ID-ABOVE-1500": "PMK 4/2025 Art. 29(5) (PIBK -> MFN) re-read; routing above USD 1,500 not confirmed.",
    "ID-LICENSING": "Not researched on an official source; kept as a caveat.",
    "TH-VAT-EXTENSION": "Only secondary sources found; the Revenue Department page still states 'Currently, the rate is 7 percent'.",
    "TH-MFN": "Thai tariff lines not retrieved; placeholders stay labelled.",
    "PH-CAO": "customs.gov.ph refused scripted requests (HTTP 403).",
    "PH-MFN": "Philippine tariff lines not retrieved; placeholders stay labelled.",
    "SVC-CLR-TH": "KPL page re-read: Vientiane South transshipment links the China-Laos Railway with Thailand's network; frequency not stated.",
    "SVC-ASEAN-EXPRESS": "No official timetable found; first run reported June-July 2024 by news media only.",
    "SVC-ILSTC": "Only state-affiliated media; no operator timetable.",
}


class _Text(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript"):
            self.skip += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript") and self.skip:
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def norm(text: str) -> str:
    text = html.unescape(text).replace(" ", " ").replace("­", "")
    text = re.sub(r"[‐-―−]", "-", text)
    text = text.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", text).strip().lower()


def fetch(url: str, insecure: bool) -> bytes:
    ctx = ssl.create_default_context()
    if insecure:
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
    with urllib.request.urlopen(req, timeout=300, context=ctx) as r:
        return r.read()


def to_text(raw: bytes) -> str:
    if raw[:5] == b"%PDF-":
        import pymupdf  # requirements-fetch.txt
        doc = pymupdf.open(stream=raw, filetype="pdf")
        return "\n".join(p.get_text() for p in doc)
    p = _Text()
    p.feed(raw.decode("utf-8", "replace"))
    return "\n".join(p.parts)


def check_ezhs() -> str:
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / "scripts").mkdir()
        (tmp / "data" / "public").mkdir(parents=True)
        src = (ROOT / "scripts" / "fetch_my_tariff.py").read_text(encoding="utf-8")
        (tmp / "scripts" / "fetch_my_tariff.py").write_text(src, encoding="utf-8", newline="\n")
        subprocess.run([sys.executable, str(tmp / "scripts" / "fetch_my_tariff.py")], check=True, capture_output=True, timeout=900)
        fresh = (tmp / "data" / "public" / "my_tariff_lines.csv").read_text(encoding="utf-8")
    committed = (ROOT / "data" / "public" / "my_tariff_lines.csv").read_text(encoding="utf-8")
    if fresh == committed:
        return "found"
    diffs = [f"{a} -> {b}" for a, b in zip(committed.splitlines(), fresh.splitlines()) if a != b]
    return "differs: " + "; ".join(diffs[:5])


def main() -> int:
    statements = load_yaml(ROOT / "data" / "reference" / "regulatory_statements.yaml")["statements"]
    sources = load_yaml(ROOT / "data" / "reference" / "sources.yaml")["sources"]
    cache: dict[str, str] = {}
    log = {"run_date": dt.date.today().isoformat(), "statements": {}}
    for sid, st in sorted(statements.items()):
        chk = st["check"]
        method, src, phrase = chk["method"], chk.get("source", ""), chk.get("phrase", "")
        entry = {"method": method, "source": src, "phrase": phrase}
        try:
            if method in ("html", "pdf"):
                if src not in cache:
                    cache[src] = norm(to_text(fetch(sources[src]["url"], src in INSECURE)))
                entry["result"] = "found" if norm(phrase) in cache[src] else "NOT FOUND"
            elif method == "ezhs":
                entry["result"] = check_ezhs()
            else:
                entry["result"] = "manual"
                entry["note"] = MANUAL_NOTES.get(sid, "")
        except Exception as exc:  # network errors are logged, not hidden
            entry["result"] = f"fetch error: {type(exc).__name__}: {exc}"[:200]
        log["statements"][sid] = entry
        print(f"{sid:24s} {entry['result']}", flush=True)
    res = [e["result"] for e in log["statements"].values()]
    log["found"] = sum(r == "found" for r in res)
    log["manual"] = sum(r == "manual" for r in res)
    log["not_found"] = sum(r.startswith(("NOT FOUND", "differs")) for r in res)
    log["errors"] = sum(r.startswith("fetch error") for r in res)
    (ROOT / "docs" / "regulatory_check_log.json").write_text(json.dumps(log, indent=2, ensure_ascii=False) + "\n",
                                                              encoding="utf-8", newline="\n")
    print(f"found {log['found']}, manual {log['manual']}, not found {log['not_found']}, errors {log['errors']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
