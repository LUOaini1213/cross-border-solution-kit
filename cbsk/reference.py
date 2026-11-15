"""Reference data loader with provenance tracking.

Every number the models take from data/ goes through `Reference.get` (or one of the dataset
accessors), which records the parameter id, value, unit, provenance label and sources. The
provenance table in docs/ is built from these records, so an input cannot be used without being
listed there.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .io import PUBLIC, REFERENCE, load_yaml, read_csv

LABELS = ("REAL", "ASSUMPTION", "ILLUSTRATIVE", "SYNTHETIC")
_FILE_DEFAULT_LABEL = {
    "rates": "ILLUSTRATIVE",
    "transit": "ASSUMPTION",
    "regimes": "ASSUMPTION",
    "compliance": "ASSUMPTION",
}


@dataclass
class Param:
    id: str
    value: Any
    unit: str
    label: str
    sources: list[str] = field(default_factory=list)
    statement: str | None = None
    note: str = ""

    def as_dict(self) -> dict:
        return {"id": self.id, "value": self.value, "unit": self.unit, "label": self.label,
                "sources": list(self.sources), "statement": self.statement, "note": self.note}


class Reference:
    def __init__(self) -> None:
        self.sources: dict = load_yaml(REFERENCE / "sources.yaml")["sources"]
        self.statements: dict = load_yaml(REFERENCE / "regulatory_statements.yaml")["statements"]
        self.files = {
            "regimes": load_yaml(REFERENCE / "regimes.yaml"),
            "rates": load_yaml(REFERENCE / "rates.yaml"),
            "transit": load_yaml(REFERENCE / "transit.yaml"),
            "compliance": load_yaml(REFERENCE / "compliance.yaml"),
        }
        self.incoterms: dict = load_yaml(REFERENCE / "incoterms_2020.yaml")
        self._lpi = {(r["iso3"], r["year"]): r for r in read_csv(PUBLIC / "lpi_dwell.csv")}
        self._air = {(r["origin"], r["destination"]): float(r["great_circle_km"]) for r in read_csv(PUBLIC / "geo_air.csv")}
        self._sea = {(r["origin"], r["destination"]): float(r["sea_nm"]) for r in read_csv(PUBLIC / "geo_sea.csv")}
        self._tariff = {r["hs_code"]: r for r in read_csv(PUBLIC / "my_tariff_lines.csv")}
        self.used: dict[str, Param] = {}

    # ------------------------------------------------------------------ generic parameters
    def _record(self, p: Param) -> Any:
        if p.label not in LABELS:
            raise ValueError(f"bad provenance label {p.label!r} for {p.id}")
        self.used[p.id] = p
        return p.value

    def _statement_sources(self, statement: str | None) -> list[str]:
        if not statement:
            return []
        return list(self.statements[statement].get("sources", []))

    def get(self, path: str) -> Any:
        """Return the value at `file.key.subkey` and record its provenance."""
        parts = path.split(".")
        node: Any = self.files[parts[0]]
        for key in parts[1:]:
            if not isinstance(node, dict) or key not in node:
                raise KeyError(f"reference parameter not found: {path}")
            node = node[key]
        default = _FILE_DEFAULT_LABEL[parts[0]]
        if isinstance(node, dict) and "value" in node:
            statement = node.get("statement")
            srcs = [node["source"]] if node.get("source") else self._statement_sources(statement)
            return self._record(Param(path, node["value"], str(node.get("unit", "")), node.get("label", default),
                                      srcs, statement, str(node.get("note", ""))))
        if isinstance(node, (int, float)):
            return self._record(Param(path, node, "", default))
        if isinstance(node, dict) and "rates" in node:   # labelled table (placeholders, band rates)
            statement = node.get("statement")
            return self._record(Param(path, node["rates"], "table", node.get("label", default),
                                      self._statement_sources(statement), statement, str(node.get("note", ""))))
        return node  # structural node (dict/list of rules), not a numeric input

    def triangular(self, path: str) -> tuple[float, float, float]:
        v = self.get(path)
        if not (isinstance(v, list) and len(v) == 3 and v[0] <= v[1] <= v[2]):
            raise ValueError(f"{path} is not a triangular (low, mode, high) triple")
        return float(v[0]), float(v[1]), float(v[2])

    def statement(self, sid: str) -> dict:
        return self.statements[sid]

    # ------------------------------------------------------------------ datasets
    def lpi(self, iso3: str, metric: str, year: str | None = None) -> float | None:
        year = year or str(self.get("transit.lpi_year"))
        row = self._lpi.get((iso3, year))
        if row is None or row.get(metric, "") == "":
            return None
        val = float(row[metric])
        self._record(Param(f"lpi.{iso3}.{year}.{metric}", val, "days", "REAL", ["wb_lpi20"],
                           note="World Bank LPI 2.0"))
        return val

    def air_km(self, o: str, d: str) -> float:
        km = self._air[(o, d)]
        self._record(Param(f"geo.air.{o}-{d}", km, "km (great circle)", "REAL", ["ourairports"],
                           note="computed from OurAirports coordinates"))
        return km

    def sea_nm(self, o: str, d: str) -> float:
        nm = self._sea[(o, d)]
        self._record(Param(f"geo.sea.{o}-{d}", nm, "nautical miles", "REAL", ["searoute"],
                           note="shortest sea route computed with searoute"))
        return nm

    def my_tariff(self, hs: str, column: str) -> float:
        """Malaysian tariff rate (fraction) for column in {mfn_import, sst, acfta_current, rcep_current, atiga}."""
        row = self._tariff[hs]
        raw = row[column].strip().rstrip("%")
        if raw in ("", "NIL"):
            raise ValueError(f"no {column} rate for {hs}")
        val = float(raw) / 100.0
        self._record(Param(f"tariff.MY.{hs}.{column}", val, "fraction", "REAL", ["my_jkdm_ezhs"],
                           statement="MY-TARIFF-LINES", note=row["description"]))
        return val

    def my_tariff_row(self, hs: str) -> dict:
        return dict(self._tariff[hs])

    def provenance_records(self) -> list[dict]:
        return [self.used[k].as_dict() for k in sorted(self.used)]
