"""Compute the distances used for transit-time modelling and write them to data/public/.

Network + optional dependency script (see requirements-fetch.txt). The offline pipeline only
reads the committed CSVs.

* Airports: OurAirports airports.csv (public domain), https://ourairports.com/data/
  (mirror used: https://davidmegginson.github.io/ourairports-data/airports.csv).
  Great-circle distance (haversine, mean Earth radius 6,371.0088 km) between the airport pairs.
* Ports: shortest sea route length from the `searoute` package (Apache-2.0; network derived
  from Eurostat SeaRoute, EUPL-1.2, based on the ORNL Global Shipping Lane Network), between
  the UN/LOCODE port points bundled with the package. Northwest Passage excluded.

    PYTHONUTF8=1 python -m pip install -r requirements-fetch.txt
    python scripts/fetch_geo.py
"""
from __future__ import annotations

import csv
import datetime as dt
import hashlib
import io
import json
import math
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "public"
AIRPORTS_URL = "https://davidmegginson.github.io/ourairports-data/airports.csv"

AIR_PAIRS = [
    ("PVG", "KUL"), ("CKG", "KUL"), ("KIX", "SIN"), ("SIN", "KIX"), ("SFO", "SIN"), ("SIN", "SFO"),
    ("PEN", "SIN"), ("SIN", "PEN"), ("SZX", "KUL"), ("SZX", "CGK"), ("SZX", "BKK"), ("SZX", "MNL"),
    ("SIN", "CGK"), ("SIN", "MNL"), ("SIN", "KUL"), ("SZX", "SIN"),
]
SEA_PAIRS = [
    ("CNNGB", "MYPKG"), ("CNQZH", "MYPKG"), ("JPOSA", "SGSIN"), ("SGSIN", "JPOSA"),
    ("USOAK", "SGSIN"), ("SGSIN", "USOAK"), ("CNYTN", "MYPKG"), ("CNYTN", "IDTPP"),
    ("CNYTN", "THLCH"), ("CNYTN", "PHMNL"), ("CNYTN", "SGSIN"), ("SGSIN", "IDTPP"),
    ("SGSIN", "MYPKG"),
]
R_KM = 6371.0088


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi, dlmb = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * R_KM * math.asin(math.sqrt(a))


def main() -> int:
    req = urllib.request.Request(AIRPORTS_URL, headers={"User-Agent": "cbsk-portfolio/1.0 (research)"})
    with urllib.request.urlopen(req, timeout=300) as r:
        raw = r.read()
    codes = sorted({c for pair in AIR_PAIRS for c in pair})
    apt = {}
    for rec in csv.DictReader(io.StringIO(raw.decode("utf-8"))):
        if rec["iata_code"] in codes and rec["type"] in ("large_airport", "medium_airport"):
            apt[rec["iata_code"]] = (float(rec["latitude_deg"]), float(rec["longitude_deg"]), rec["name"], rec["iso_country"])
    missing = set(codes) - set(apt)
    if missing:
        raise SystemExit(f"airports not found: {sorted(missing)}")
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / "geo_air.csv", "w", encoding="utf-8", newline="\n") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["origin", "destination", "origin_name", "destination_name", "great_circle_km"])
        for o, d in AIR_PAIRS:
            lo, ld = apt[o], apt[d]
            w.writerow([o, d, lo[2], ld[2], f"{haversine_km(lo[0], lo[1], ld[0], ld[1]):.1f}"])

    import searoute as sr  # optional dependency
    from searoute.classes.passages import Passage

    pj = Path(sr.__file__).parent / "data" / "ports.geojson"
    ports = {f["properties"]["port"]: f for f in json.loads(pj.read_text(encoding="utf-8"))["features"]}
    with open(OUT / "geo_sea.csv", "w", encoding="utf-8", newline="\n") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["origin", "destination", "origin_name", "destination_name", "sea_nm"])
        for o, d in SEA_PAIRS:
            po, pd = ports[o], ports[d]
            route = sr.searoute(po["geometry"]["coordinates"], pd["geometry"]["coordinates"],
                                units="naut", restrictions=[Passage.northwest])
            nm = float(route["properties"]["length"])
            w.writerow([o, d, po["properties"]["name"], pd["properties"]["name"], f"{nm:.1f}"])
    import importlib.metadata as md
    meta = {
        "accessed": dt.date.today().isoformat(),
        "airports_source": AIRPORTS_URL,
        "airports_licence": "public domain (OurAirports)",
        "airports_raw_sha256": hashlib.sha256(raw).hexdigest(),
        "sea_tool": f"searoute {md.version('searoute')} (Apache-2.0); network: Eurostat SeaRoute (EUPL-1.2) / ORNL",
        "sea_restrictions": "Northwest Passage excluded",
        "earth_radius_km": R_KM,
    }
    (OUT / "geo.meta.json").write_text(json.dumps(meta, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print("wrote geo_air.csv, geo_sea.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
