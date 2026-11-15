"""Builders for transit-time leg specifications from reference data (LPI dwell times, distances,
labelled assumptions)."""
from __future__ import annotations

from .reference import Reference
from .transit import leg


def tri(name: str, ref: Reference, path: str) -> dict:
    lo, mo, hi = ref.triangular(path)
    return leg(name, "triangular", low=lo, mode=mo, high=hi, source=path)


def truck(name: str, ref: Reference, km: float) -> list[dict]:
    per_day = float(ref.get("transit.truck.km_per_day"))
    return [tri(f"{name}: handling", ref, "transit.truck.handling_days"),
            leg(f"{name}: driving {km:.0f} km", "fixed", days=km / per_day, source="transit.truck.km_per_day")]


def wait(name: str, headway_days: float, source: str) -> dict:
    return leg(name, "uniform", low=0.0, high=float(headway_days), source=source)


def container_export_dwell(ref: Reference, iso3: str) -> dict:
    md, q1, q3 = (ref.lpi(iso3, f"ct_export_{m}") for m in ("median", "q1", "q3"))
    if None in (md, q1, q3):
        raise ValueError(f"no LPI export dwell for {iso3}")
    return leg(f"origin port dwell ({iso3}, LPI)", "lognormal_q", median=md, q1=q1, q3=q3, source=f"lpi.{iso3}.ct_export")


def container_import_dwell(ref: Reference, iso3: str) -> dict:
    md, q1, q3 = (ref.lpi(iso3, f"ct_import_{m}") for m in ("median", "q1", "q3"))
    if None in (md, q1, q3):
        raise ValueError(f"no LPI import dwell for {iso3}")
    return leg(f"destination port + customs dwell ({iso3}, LPI)", "lognormal_q", median=md, q1=q1, q3=q3,
               source=f"lpi.{iso3}.ct_import")


def air_import_dwell(ref: Reference, iso3: str) -> dict:
    md, mean = ref.lpi(iso3, "air_import_median"), ref.lpi(iso3, "air_import_mean")
    if None in (md, mean):
        raise ValueError(f"no LPI air dwell for {iso3}")
    return leg(f"destination airport + customs dwell ({iso3}, LPI)", "lognormal_mm", median=md, mean=mean,
               source=f"lpi.{iso3}.air_import")


def transshipment(ref: Reference, iso3_dest: str) -> dict:
    n = ref.lpi(iso3_dest, "transshipments_mean")
    days = ref.lpi(iso3_dest, "transshipment_days_mean")
    k = float(ref.get("transit.sea.transshipment_shape_k"))
    p = min(1.0, max(0.0, n))
    return leg(f"transshipment (LPI {iso3_dest}: {n} per shipment, {days} d)", "bernoulli", p=p,
               delay=leg("transshipment time", "gamma", shape=k, mean=days), source=f"lpi.{iso3_dest}.transshipment")


def sailing(ref: Reference, o: str, d: str) -> dict:
    nm = ref.sea_nm(o, d)
    kn = float(ref.get("transit.sea.speed_knots"))
    allowance = float(ref.get("transit.sea.port_call_days_per_1000nm"))
    cv = float(ref.get("transit.sea.sailing_cv"))
    mean = nm / (kn * 24.0) + allowance * nm / 1000.0
    return leg(f"sailing {o}-{d} ({nm:.0f} nm)", "lognormal_cv", mean=mean, cv=cv, source=f"geo.sea.{o}-{d}")


def flight(ref: Reference, o: str, d: str) -> dict:
    km = ref.air_km(o, d)
    factor = float(ref.get("transit.air.route_factor"))
    speed = float(ref.get("transit.air.block_kmh"))
    return leg(f"flight {o}-{d} ({km:.0f} km great circle)", "fixed", days=km * factor / speed / 24.0,
               source=f"geo.air.{o}-{d}")


def customs_hold(ref: Reference, n_flags: int) -> dict:
    p = float(ref.get("transit.customs_hold.base_probability")) + \
        n_flags * float(ref.get("transit.customs_hold.extra_probability_per_risk_flag"))
    p = min(p, 0.9)
    lo, mo, hi = ref.triangular("transit.customs_hold.delay_days")
    return leg(f"customs hold / inspection (p={p:.2f})", "bernoulli", p=p,
               delay=leg("hold delay", "triangular", low=lo, mode=mo, high=hi), source="transit.customs_hold")


def ocean_main(ref: Reference, o_iso: str, o_port: str, d_iso: str, d_port: str) -> list[dict]:
    return [container_export_dwell(ref, o_iso),
            wait("wait for weekly sailing", float(ref.get("transit.sea.headway_days")), "transit.sea.headway_days"),
            sailing(ref, o_port, d_port),
            transshipment(ref, d_iso),
            container_import_dwell(ref, d_iso)]


def air_main(ref: Reference, o_air: str, d_air: str, d_iso: str) -> list[dict]:
    return [tri("origin airport handling + export clearance", ref, "transit.air.origin_handling_days"),
            wait("wait for flight", float(ref.get("transit.air.headway_days")), "transit.air.headway_days"),
            flight(ref, o_air, d_air),
            air_import_dwell(ref, d_iso)]
