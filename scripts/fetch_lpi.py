"""Download World Bank LPI 2.0 dwell-time indicators and write a small extract.

Network script. The offline pipeline (scripts/build_all.py) only reads the committed
extract in data/public/, so CI never needs the network. Re-running this script refreshes
the snapshot; results will then change and the golden test will ask for a rebuild.

Source: The World Bank, Logistics Performance Indicators (LPI 2.0), Data360 bulk file
    https://data360files.worldbank.org/data360-data/data/WB_LPI_20/WB_LPI_20.csv
Licence: CC BY 4.0 (https://www.worldbank.org/en/about/legal/terms-of-use-for-datasets).

Indicator codes kept (container data from carrier/AIS tracking, aviation data from Cargo iQ,
as described by the LPI 2.0 methodology):
    CT_DT_M  container import dwell time (days): MD median, M mean, Q1, Q3
    CT_DT_X  container export dwell time (days): MD, M, Q1, Q3
    AV_DT    aviation import dwell time (days): MD, M
    TRS_NUM  mean number of transshipments, TRS_T mean transshipment time (days)
The Data360 file labels metric "M" as "Median"; it is the mean (M >= MD for almost every
economy, and the LPI 2.0 methodology reports mean, median and IQR). Values are unchanged.

    python scripts/fetch_lpi.py
"""
from __future__ import annotations

import csv
import datetime as dt
import hashlib
import io
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_CSV = ROOT / "data" / "public" / "lpi_dwell.csv"
OUT_META = ROOT / "data" / "public" / "lpi_dwell.meta.json"
URL = "https://data360files.worldbank.org/data360-data/data/WB_LPI_20/WB_LPI_20.csv"
ECONOMIES = ["CHN", "DEU", "IDN", "JPN", "KHM", "LAO", "MMR", "MYS", "PHL", "SGP", "THA", "USA", "VNM"]
YEARS = ("2023", "2024")
COLS = {
    ("CT_DT_M", "MD"): "ct_import_median", ("CT_DT_M", "M"): "ct_import_mean",
    ("CT_DT_M", "Q1"): "ct_import_q1", ("CT_DT_M", "Q3"): "ct_import_q3",
    ("CT_DT_X", "MD"): "ct_export_median", ("CT_DT_X", "M"): "ct_export_mean",
    ("CT_DT_X", "Q1"): "ct_export_q1", ("CT_DT_X", "Q3"): "ct_export_q3",
    ("AV_DT", "MD"): "air_import_median", ("AV_DT", "M"): "air_import_mean",
    ("TRS_NUM", "_Z"): "transshipments_mean", ("TRS_T", "_Z"): "transshipment_days_mean",
}


def main() -> int:
    req = urllib.request.Request(URL, headers={"User-Agent": "cbsk-portfolio/1.0 (research)"})
    with urllib.request.urlopen(req, timeout=600) as r:
        raw = r.read()
    rows: dict[tuple[str, str], dict[str, str]] = {}
    names: dict[str, str] = {}
    for rec in csv.DictReader(io.StringIO(raw.decode("utf-8"))):
        col = COLS.get((rec["INDICATOR"], rec["METRIC"]))
        if col is None or rec["REF_AREA"] not in ECONOMIES or rec["TIME_PERIOD"] not in YEARS:
            continue
        if rec["OBS_VALUE"] == "":
            continue
        key = (rec["REF_AREA"], rec["TIME_PERIOD"])
        rows.setdefault(key, {})[col] = rec["OBS_VALUE"]
        names[rec["REF_AREA"]] = rec["REF_AREA_LABEL"]
    header = ["iso3", "name", "year"] + list(COLS.values())
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_CSV, "w", encoding="utf-8", newline="\n") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(header)
        for (iso, year) in sorted(rows):
            w.writerow([iso, names.get(iso, iso), year] + [rows[(iso, year)].get(c, "") for c in COLS.values()])
    meta = {
        "source": URL,
        "publisher": "The World Bank, Logistics Performance Indicators (LPI 2.0)",
        "licence": "CC BY 4.0",
        "accessed": dt.date.today().isoformat(),
        "raw_sha256": hashlib.sha256(raw).hexdigest(),
        "economies_requested": ECONOMIES,
        "economies_with_data": sorted({k[0] for k in rows}),
        "note": "metric M is the mean although the file labels it Median; values unchanged",
    }
    OUT_META.write_text(json.dumps(meta, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {OUT_CSV.relative_to(ROOT)} ({len(rows)} rows)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
