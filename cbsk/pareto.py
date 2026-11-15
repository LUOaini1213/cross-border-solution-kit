"""Pareto frontier over (cost per unit, P90 transit days, risk score) and the recommendation rule."""
from __future__ import annotations


def dominates(a: tuple, b: tuple) -> bool:
    """a dominates b if it is no worse on every objective and strictly better on at least one (minimise)."""
    return all(x <= y for x, y in zip(a, b)) and any(x < y for x, y in zip(a, b))


def pareto_front(points: list[tuple]) -> list[int]:
    """Indices of non-dominated points (exact duplicates are all kept)."""
    return [i for i, p in enumerate(points) if not any(dominates(q, p) for j, q in enumerate(points) if j != i)]


def dominated_by(points: list[tuple], i: int) -> list[int]:
    return [j for j, q in enumerate(points) if j != i and dominates(q, points[i])]


def recommend(options: list[dict], weights: dict, target_probability: float) -> dict:
    """Choose an option.

    1. Feasible = on-time probability >= target and no blocking flag.
    2. Among feasible options on the Pareto front, minimise a weighted sum of objectives, each scaled by the
       best feasible value (cost and P90) or offset-scaled (risk + 10) so a zero risk score does not divide by zero.
    3. If nothing is feasible, take the highest on-time probability (ties: lower cost) and say so.
    """
    pts = [(o["metrics"]["cost_per_unit"], o["metrics"]["p90"], o["metrics"]["risk"]) for o in options]
    front = set(pareto_front(pts))
    feasible = [i for i, o in enumerate(options)
                if o["metrics"]["on_time_probability"] >= target_probability
                and not any(f["severity"] == "block" for f in o["flags"])]
    wc, wt, wr = (float(weights.get(k, 0.0)) for k in ("cost", "time", "risk"))
    if feasible:
        cand = [i for i in feasible if i in front] or feasible
        cmin = min(pts[i][0] for i in feasible)
        tmin = min(pts[i][1] for i in feasible)
        rmin = min(pts[i][2] for i in feasible)

        def score(i):
            c, t, r = pts[i]
            return wc * c / cmin + wt * t / tmin + wr * (r + 10.0) / (rmin + 10.0)
        best = min(cand, key=lambda i: (round(score(i), 12), pts[i][0], options[i]["id"]))
        status = "meets_target"
        scores = {options[i]["id"]: score(i) for i in feasible}
    else:
        best = max(range(len(options)), key=lambda i: (options[i]["metrics"]["on_time_probability"], -pts[i][0]))
        status = "target_not_met"
        scores = {}
    return {"chosen": options[best]["id"], "status": status, "front": sorted(options[i]["id"] for i in front),
            "feasible": [options[i]["id"] for i in feasible], "scores": scores}
