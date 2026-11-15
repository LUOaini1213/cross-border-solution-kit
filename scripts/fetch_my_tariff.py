"""Fetch Malaysian tariff lines used by the templates from the Royal Malaysian Customs
Department (JKDM) HS Explorer and write data/public/my_tariff_lines.csv.

Network script; the offline pipeline reads only the committed CSV.

Source: JKDM HS Explorer, https://ezhs.customs.gov.my/ (public search endpoint
`public-find-hs-data`, the same request the site's search form sends). Schedules queried:
    PDK   "PDK 2025 - PERINTAH DUTI KASTAM 2025" (MFN import duty, SST column, excise, cess, prohibitions)
    ACFTA "ACFTA - ASEAN CHINA FREE TRADE AGREEMENT" (current preferential rate)
    RCEP  "RCEP - REGIONAL COMPREHENSIVE ECONOMIC PARTNERSHIP" (current preferential rate)
    AHTN  "PDK (ATIGA) - ASEAN TRADE GOODS AGREEMENT (ATIGA) 2022"
On the access date the site's full ACFTA and RCEP tables showed "The content of this site is
being updated"; the search endpoint still returned rates. The site carries a disclaimer that
JKDM accepts no liability for its use. Rates must be re-checked before any real declaration.

    python scripts/fetch_my_tariff.py
"""
from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_CSV = ROOT / "data" / "public" / "my_tariff_lines.csv"
OUT_META = ROOT / "data" / "public" / "my_tariff_lines.meta.json"
ENDPOINT = "https://ezhs.customs.gov.my/public-find-hs-data"
LINES = [  # (tariff code as HEADER.SUB.ITEM, template use)
    ("8708.29.9500", "automotive: body panels and closures"),
    ("9401.20.1000", "automotive: seats"),
    ("8544.30.1200", "automotive: wiring harness sets"),
    ("8708.30.2900", "automotive: brake modules"),
    ("8708.40.2600", "automotive: gearboxes (assembled)"),
    ("8708.80.1600", "automotive: suspension systems"),
    ("8703.23.2100", "automotive: CKD sedan 1,500-1,800 cc (classification-risk reference only)"),
    ("6109.10.2000", "consumer: cotton T-shirts (women's)"),
    ("8518.30.2000", "consumer: earphones"),
    ("4202.92.9000", "consumer: bags with outer surface of plastics/textile, other"),
]
SCHEDULES = ("PDK", "ACFTA", "RCEP", "AHTN")


class _Table(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.rows: list[list[str]] = []
        self._row: list[str] | None = None
        self._cell: list[str] | None = None

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self._row = []
        elif tag in ("td", "th") and self._row is not None:
            if self._cell is not None:  # the site leaves some <td> unclosed: close it implicitly
                self._row.append(re.sub(r"\s+", " ", "".join(self._cell)).strip())
            self._cell = []

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self._row is not None and self._cell is not None:
            self._row.append(re.sub(r"\s+", " ", "".join(self._cell)).strip())
            self._cell = None
        elif tag == "tr" and self._row is not None:
            self.rows.append(self._row)
            self._row = None

    def handle_data(self, data):
        if self._cell is not None:
            self._cell.append(data)


def query(schedule: str, heading: str) -> tuple[list[list[str]], str]:
    body = urllib.parse.urlencode({"hsType": schedule, "hsCriteria": "1", "hsKeyword": heading,
                                   "find_item": "yes"}).encode()
    req = urllib.request.Request(ENDPOINT, data=body, headers={
        "User-Agent": "cbsk-portfolio/1.0 (research)", "Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=180) as r:
        raw = r.read()
    p = _Table()
    p.feed(raw.decode("utf-8", "replace"))
    return p.rows, hashlib.sha256(raw).hexdigest()


def main() -> int:
    headings = sorted({code[:4] for code, _ in LINES})
    tables: dict[tuple[str, str], list[list[str]]] = {}
    hashes: dict[str, str] = {}
    for sch in SCHEDULES:
        for h in headings:
            rows, digest = query(sch, h)
            tables[(sch, h)] = rows
            hashes[f"{sch}_{h}"] = digest
            time.sleep(1.0)

    def find(sch: str, code: str) -> list[str] | None:
        hd, sub, item = code.split(".")
        for row in tables[(sch, hd)]:
            if len(row) < 3:
                continue
            if sch == "AHTN":
                if row[0] == hd and row[1] == sub and (row[2] + row[3]) == item:
                    return row
            elif row[0] == hd and row[1] == sub and row[2] == item:
                return row
        return None

    out = []
    for code, use in LINES:
        pdk, acfta, rcep, ahtn = (find(s, code) for s in SCHEDULES)
        if pdk is None:
            raise SystemExit(f"{code} not found in PDK")
        out.append([
            code, pdk[4], pdk[3], pdk[5], pdk[8], pdk[9], pdk[10], pdk[11], pdk[12], pdk[13], pdk[14],
            acfta[5] if acfta else "", rcep[5] if rcep else "", ahtn[6] if ahtn else "", use,
        ])
    header = ["hs_code", "description", "unit", "mfn_import", "sst", "excise", "cess_1", "cess_2", "cess_3",
              "import_prohibition", "export_prohibition", "acfta_current", "rcep_current", "atiga", "template_use"]
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_CSV, "w", encoding="utf-8", newline="\n") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(header)
        w.writerows(out)
    meta = {
        "source": "https://ezhs.customs.gov.my/ (JKDM HS Explorer, search endpoint public-find-hs-data)",
        "publisher": "Royal Malaysian Customs Department (JKDM)",
        "schedules": {"PDK": "PDK 2025 - PERINTAH DUTI KASTAM 2025", "ACFTA": "ASEAN-China FTA (current rate)",
                      "RCEP": "RCEP (current rate)", "AHTN": "PDK (ATIGA) 2022"},
        "accessed": dt.date.today().isoformat(),
        "response_sha256": hashes,
        "note": ("ACFTA and RCEP full tables displayed 'being updated' on the access date; search results used. "
                 "The ezHS row text omits some parent headings; parent text was cross-checked against the "
                 "Customs Duties Order 2022 (P.U.(A) 114/2022) hierarchy for the same codes."),
    }
    OUT_META.write_text(json.dumps(meta, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {OUT_CSV.relative_to(ROOT)} ({len(out)} lines)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
