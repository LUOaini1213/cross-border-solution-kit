"""RFQ input schema and validation (hand-written so every rule is visible and testable)."""
from __future__ import annotations

import re
from pathlib import Path

from .incoterms import RULES
from .io import load_yaml

FLOW_TYPES = ("b2b_import", "temporary", "b2c_parcel")
MODES = {
    "b2b_import": {"ocean_fcl", "ocean_lcl", "air", "rail_sea_fcl", "rail"},
    "temporary": {"air", "ocean_fcl20", "ocean_lcl", "road"},
    "b2c_parcel": {"air_parcel", "sea_air", "rail", "road", "ocean_bulk_local"},
}
COUNTRIES = {"CN", "MY", "SG", "ID", "TH", "PH", "JP", "US"}
PURPOSES = {"exhibition", "professional_equipment", "repair_abroad", "repair_in_sg"}
REGIMES = {"ata_carnet", "tis", "temp_export_repair"}
ROLES = {"buyer", "seller", "owner"}
HS_MY = re.compile(r"^\d{4}\.\d{2}\.\d{4}$")
HS_ANY = re.compile(r"^\d{4}(\.\d{2}(\.\d{2,4})?)?$")


class RFQError(ValueError):
    pass


def _num(errors: list[str], where: str, value, lo: float | None = None, hi: float | None = None,
         strict_lo: bool = False) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        errors.append(f"{where}: expected a number, got {value!r}")
        return
    if lo is not None and (value < lo or (strict_lo and value == lo)):
        errors.append(f"{where}: {value} is below the allowed minimum {lo}")
    if hi is not None and value > hi:
        errors.append(f"{where}: {value} is above the allowed maximum {hi}")


def _profile(errors: list[str], where: str, prof) -> None:
    if not isinstance(prof, list) or len(prof) != 12:
        errors.append(f"{where}: monthly_profile must list 12 factors")
        return
    for i, x in enumerate(prof):
        _num(errors, f"{where}[{i}]", x, 0.0)
    if all(isinstance(x, (int, float)) for x in prof) and abs(sum(prof) - 12.0) > 1e-6:
        errors.append(f"{where}: monthly_profile must sum to 12 (got {sum(prof):.6f})")


def validate(rfq: dict) -> list[str]:
    e: list[str] = []
    for key in ("rfq_id", "template", "customer", "issue_date", "currency", "seed", "flow_type", "incoterm",
                "quoting_party_role", "priorities", "service", "lanes"):
        if key not in rfq:
            e.append(f"missing top-level key: {key}")
    if e:
        return e
    if "fictional" not in str(rfq["customer"]).lower():
        e.append("customer must be labelled fictional (e.g. 'Customer A (fictional)')")
    if rfq["currency"] != "USD":
        e.append("only USD quotations are supported")
    if not isinstance(rfq["seed"], int) or isinstance(rfq["seed"], bool):
        e.append("seed must be an integer")
    flow = rfq["flow_type"]
    if flow not in FLOW_TYPES:
        e.append(f"flow_type must be one of {FLOW_TYPES}")
        return e
    role = rfq["quoting_party_role"]
    if role not in ROLES:
        e.append(f"quoting_party_role must be one of {sorted(ROLES)}")
    inco = rfq["incoterm"]
    if inco is not None and inco not in RULES:
        e.append(f"incoterm {inco!r} is not an Incoterms 2020 rule")
    if (inco is None) != (role == "owner"):
        e.append("incoterm must be null exactly when the quoting party is the goods' owner (no sale)")
    pr = rfq["priorities"]
    if not isinstance(pr, dict) or set(pr) != {"cost", "time", "risk"}:
        e.append("priorities must have cost, time and risk")
    else:
        for k, v in pr.items():
            _num(e, f"priorities.{k}", v, 0.0, 1.0)
        if all(isinstance(v, (int, float)) for v in pr.values()) and abs(sum(pr.values()) - 1.0) > 1e-9:
            e.append("priorities must sum to 1")
    svc = rfq["service"]
    _num(e, "service.on_time_target_probability", svc.get("on_time_target_probability"), 0.0, 1.0, strict_lo=True)
    if not isinstance(svc.get("vas", []), list):
        e.append("service.vas must be a list")
    lanes = rfq["lanes"]
    if not isinstance(lanes, list) or not lanes:
        e.append("lanes must be a non-empty list")
        return e
    ids = [ln.get("id") for ln in lanes]
    if len(set(ids)) != len(ids):
        e.append("lane ids must be unique")
    if flow == "b2c_parcel":
        _profile(e, "monthly_profile", rfq.get("monthly_profile"))
        basket = rfq.get("basket") or []
        if not basket:
            e.append("basket is required for parcel RFQs")
        shares = 0.0
        for i, b in enumerate(basket):
            w = f"basket[{i}]"
            for k in ("category", "hs", "share", "retail_usd", "cost_usd", "kg", "cbm"):
                if k not in b:
                    e.append(f"{w}: missing {k}")
            if "hs" in b and not HS_MY.match(str(b["hs"])):
                e.append(f"{w}: hs must look like 6109.10.2000")
            for k in ("retail_usd", "cost_usd", "kg", "cbm"):
                if k in b:
                    _num(e, f"{w}.{k}", b[k], 0.0, strict_lo=True)
            if "share" in b:
                _num(e, f"{w}.share", b["share"], 0.0, 1.0)
                shares += float(b["share"]) if isinstance(b["share"], (int, float)) else 0.0
        if basket and abs(shares - 1.0) > 1e-9:
            e.append("basket shares must sum to 1")
    for ln in lanes:
        w = f"lane {ln.get('id')}"
        for end in ("origin", "destination"):
            c = (ln.get(end) or {}).get("country")
            if c not in COUNTRIES:
                e.append(f"{w}: {end}.country {c!r} not supported ({sorted(COUNTRIES)})")
        modes = ln.get("modes") or []
        if not modes:
            e.append(f"{w}: at least one mode is required")
        bad = sorted(set(modes) - MODES[flow])
        if bad:
            e.append(f"{w}: modes {bad} not allowed for {flow}")
        _num(e, f"{w}.target_transit_days", ln.get("target_transit_days"), 0.0, strict_lo=True)
        if flow == "b2b_import":
            _num(e, f"{w}.annual_units", ln.get("annual_units"), 0.0, strict_lo=True)
            _profile(e, f"{w}.monthly_profile", ln.get("monthly_profile"))
            spm = ln.get("shipments_per_month")
            if not isinstance(spm, int) or isinstance(spm, bool) or spm < 1:
                e.append(f"{w}: shipments_per_month must be a positive integer")
            _num(e, f"{w}.unit_gross_kg", ln.get("unit_gross_kg"), 0.0, strict_lo=True)
            _num(e, f"{w}.unit_cbm", ln.get("unit_cbm"), 0.0, strict_lo=True)
            if not ln.get("lines"):
                e.append(f"{w}: lines are required")
            for j, li in enumerate(ln.get("lines") or []):
                if not HS_MY.match(str(li.get("hs", ""))):
                    e.append(f"{w}.lines[{j}]: hs must look like 8708.29.9500")
                _num(e, f"{w}.lines[{j}].value_per_unit", li.get("value_per_unit"), 0.0, strict_lo=True)
                if li.get("origin") not in COUNTRIES:
                    e.append(f"{w}.lines[{j}]: origin country not supported")
                rvc = li.get("supplier_rvc_pct")
                if rvc is not None:
                    _num(e, f"{w}.lines[{j}].supplier_rvc_pct", rvc, 0.0, 100.0)
        elif flow == "temporary":
            if ln.get("purpose") not in PURPOSES:
                e.append(f"{w}: purpose must be one of {sorted(PURPOSES)}")
            if not set(ln.get("regimes") or []) <= REGIMES or not ln.get("regimes"):
                e.append(f"{w}: regimes must be a non-empty subset of {sorted(REGIMES)}")
            if ln.get("transit_metric") not in ("outbound", "round_trip"):
                e.append(f"{w}: transit_metric must be outbound or round_trip")
            _num(e, f"{w}.moves_per_year", ln.get("moves_per_year"), 0.0, strict_lo=True)
            _num(e, f"{w}.stay_days", ln.get("stay_days"), 0.0)
            item = ln.get("item") or {}
            if not HS_ANY.match(str(item.get("hs", ""))):
                e.append(f"{w}: item.hs missing or malformed")
            for k in ("value", "gross_kg", "cbm"):
                _num(e, f"{w}.item.{k}", item.get(k), 0.0, strict_lo=True)
            if ln.get("purpose") == "repair_abroad":
                for k in ("new_parts_share", "warranty_share"):
                    _num(e, f"{w}.{k}", ln.get(k), 0.0, 1.0)
            if "road" in modes:
                _num(e, f"{w}.road_km", ln.get("road_km"), 0.0, strict_lo=True)
        else:
            _num(e, f"{w}.parcels_per_month", ln.get("parcels_per_month"), 0.0, strict_lo=True)
            if "road" in modes:
                _num(e, f"{w}.road_km", ln.get("road_km"), 0.0, strict_lo=True)
    return e


def load_rfq(path: Path) -> dict:
    rfq = load_yaml(path)
    errors = validate(rfq)
    if errors:
        raise RFQError(f"{path}: " + "; ".join(errors))
    return rfq
