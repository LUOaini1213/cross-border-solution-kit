"""Seeded Monte Carlo of door-to-door transit time.

An option's transit time is the sum of independent leg durations (an assumption: a congested port
would in reality slow several legs at once). Leg specs are plain dicts so they can be written to the
results file and checked by tests.
"""
from __future__ import annotations

import math

import numpy as np

from .seeds import stable_seed  # noqa: F401  (re-exported)

Z75 = 0.6744897501960817  # standard normal 75th percentile




def lognormal_from_quartiles(median: float, q1: float, q3: float) -> tuple[float, float]:
    if not (0 < q1 <= median <= q3):
        raise ValueError("quartiles must satisfy 0 < q1 <= median <= q3")
    mu = math.log(median)
    sigma = (math.log(q3) - math.log(q1)) / (2.0 * Z75)
    return mu, sigma


def lognormal_from_median_mean(median: float, mean: float) -> tuple[float, float]:
    if median <= 0:
        raise ValueError("median must be positive")
    ratio = max(mean / median, 1.0 + 1e-9)   # a mean below the median is impossible for a lognormal
    return math.log(median), math.sqrt(2.0 * math.log(ratio))


def lognormal_from_mean_cv(mean: float, cv: float) -> tuple[float, float]:
    s2 = math.log(1.0 + cv * cv)
    return math.log(mean) - s2 / 2.0, math.sqrt(s2)


def leg(name: str, kind: str, **params) -> dict:
    return {"name": name, "kind": kind, **params}


def sample_leg(spec: dict, rng: np.random.Generator, n: int) -> np.ndarray:
    k = spec["kind"]
    if k == "fixed":
        return np.full(n, float(spec["days"]))
    if k == "uniform":
        return rng.uniform(spec["low"], spec["high"], n)
    if k == "triangular":
        lo, mo, hi = spec["low"], spec["mode"], spec["high"]
        if hi == lo:
            return np.full(n, float(lo))
        return rng.triangular(lo, mo, hi, n)
    if k == "lognormal_q":
        mu, sigma = lognormal_from_quartiles(spec["median"], spec["q1"], spec["q3"])
        return rng.lognormal(mu, sigma, n)
    if k == "lognormal_mm":
        mu, sigma = lognormal_from_median_mean(spec["median"], spec["mean"])
        return rng.lognormal(mu, sigma, n)
    if k == "lognormal_cv":
        mu, sigma = lognormal_from_mean_cv(spec["mean"], spec["cv"])
        return rng.lognormal(mu, sigma, n)
    if k == "gamma":
        return rng.gamma(spec["shape"], spec["mean"] / spec["shape"], n)
    if k == "bernoulli":
        hit = rng.random(n) < spec["p"]
        inner = sample_leg(spec["delay"], rng, n)
        return np.where(hit, inner, 0.0)
    raise ValueError(f"unknown leg kind {k}")


def leg_mean(spec: dict) -> float:
    """Analytic mean of a leg (used by tests to check the simulation)."""
    k = spec["kind"]
    if k == "fixed":
        return float(spec["days"])
    if k == "uniform":
        return (spec["low"] + spec["high"]) / 2.0
    if k == "triangular":
        return (spec["low"] + spec["mode"] + spec["high"]) / 3.0
    if k == "lognormal_q":
        mu, s = lognormal_from_quartiles(spec["median"], spec["q1"], spec["q3"])
        return math.exp(mu + s * s / 2.0)
    if k == "lognormal_mm":
        mu, s = lognormal_from_median_mean(spec["median"], spec["mean"])
        return math.exp(mu + s * s / 2.0)
    if k == "lognormal_cv":
        return float(spec["mean"])
    if k == "gamma":
        return float(spec["mean"])
    if k == "bernoulli":
        return spec["p"] * leg_mean(spec["delay"])
    raise ValueError(k)


def simulate(legs: list[dict], seed: int, n: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    total = np.zeros(n)
    for spec in legs:
        total += sample_leg(spec, rng, n)
    return total


def metrics(samples: np.ndarray, target_days: float) -> dict:
    step = max(1.0, round(0.2 * target_days))
    return {
        "mean": float(np.mean(samples)),
        "p50": float(np.percentile(samples, 50)),
        "p90": float(np.percentile(samples, 90)),
        "p95": float(np.percentile(samples, 95)),
        "on_time_probability": float(np.mean(samples <= target_days)),
        "target_days": float(target_days),
        "on_time_at": {f"{t:g}": float(np.mean(samples <= t)) for t in (target_days - step, target_days, target_days + step)},
    }
