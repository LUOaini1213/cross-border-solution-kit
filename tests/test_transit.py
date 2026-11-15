"""Monte Carlo determinism, distribution fits and reliability metrics."""
from __future__ import annotations

import math
import os
import subprocess
import sys

import numpy as np
import pytest

from cbsk import transit
from cbsk.io import ROOT


def test_seed_is_independent_of_python_hash_randomisation():
    code = "from cbsk.transit import stable_seed; print(stable_seed(20261115, 'RFQ-AUTO-2026-001', 'A1', 'ocean_fcl'))"
    outs = set()
    for hs in ("1", "2", "random"):
        env = {**os.environ, "PYTHONHASHSEED": hs, "PYTHONPATH": str(ROOT)}
        outs.add(subprocess.run([sys.executable, "-c", code], env=env, capture_output=True, text=True, check=True).stdout)
    assert len(outs) == 1


def test_simulation_is_deterministic_per_seed():
    legs = [transit.leg("a", "triangular", low=1, mode=2, high=5), transit.leg("b", "lognormal_q", median=3.5, q1=1.8, q3=6.7)]
    a = transit.simulate(legs, 42, 5000)
    b = transit.simulate(legs, 42, 5000)
    c = transit.simulate(legs, 43, 5000)
    assert np.array_equal(a, b)
    assert not np.array_equal(a, c)


def test_pipeline_metrics_are_reproducible(runs):
    res, _ = runs["automotive_ckd_cn_my"]
    o = next(o for ln in res["lanes"] for o in ln["options"] if o["id"] == "A1-ocean_fcl")
    samples = transit.simulate(o["legs"], o["transit"]["seed"], res["monte_carlo_draws"])
    m = transit.metrics(samples, o["transit"]["target_days"])
    for k in ("mean", "p50", "p90", "on_time_probability"):
        assert m[k] == pytest.approx(o["transit"][k], abs=1e-6)


def test_lognormal_quartile_fit_reproduces_quartiles():
    rng = np.random.default_rng(7)
    mu, sigma = transit.lognormal_from_quartiles(3.5, 1.8, 6.7)
    x = rng.lognormal(mu, sigma, 400_000)
    q1, md, q3 = np.percentile(x, [25, 50, 75])
    assert md == pytest.approx(3.5, rel=0.02)
    assert q1 == pytest.approx(math.exp(mu - transit.Z75 * sigma), rel=0.02)
    assert q3 == pytest.approx(math.exp(mu + transit.Z75 * sigma), rel=0.02)
    # symmetric in log space around the median: the fit passes through sqrt(q1*q3) and the log-IQR
    assert math.exp(mu - transit.Z75 * sigma) * math.exp(mu + transit.Z75 * sigma) == pytest.approx(3.5 ** 2)
    assert math.exp(mu + transit.Z75 * sigma) / math.exp(mu - transit.Z75 * sigma) == pytest.approx(6.7 / 1.8)


@pytest.mark.parametrize("spec", [
    transit.leg("u", "uniform", low=0, high=7),
    transit.leg("t", "triangular", low=1, mode=3, high=8),
    transit.leg("q", "lognormal_q", median=3.7, q1=2.3, q3=5.8),
    transit.leg("m", "lognormal_mm", median=0.4, mean=0.9),
    transit.leg("c", "lognormal_cv", mean=7.4, cv=0.1),
    transit.leg("g", "gamma", shape=2.0, mean=4.8),
    transit.leg("b", "bernoulli", p=0.5, delay=transit.leg("g", "gamma", shape=2.0, mean=4.8)),
    transit.leg("f", "fixed", days=1.25),
])
def test_sample_means_match_analytic_means(spec):
    x = transit.simulate([spec], 11, 200_000)
    se = max(np.std(x) / math.sqrt(len(x)), 1e-12)
    assert abs(np.mean(x) - transit.leg_mean(spec)) <= 4 * se + 1e-12


def test_on_time_counts_arrival_on_the_target_day():
    samples = transit.simulate([transit.leg("f", "fixed", days=5.0)], 1, 10)
    assert transit.metrics(samples, 5.0)["on_time_probability"] == 1.0
    assert transit.metrics(samples, 4.999)["on_time_probability"] == 0.0


def test_transshipment_probability_from_lpi(runs):
    res, _ = runs["automotive_ckd_cn_my"]
    o = next(o for ln in res["lanes"] for o in ln["options"] if o["id"] == "A1-ocean_fcl")
    t = next(lg for lg in o["legs"] if lg["name"].startswith("transshipment"))
    assert t["p"] == pytest.approx(0.5)              # LPI 2.0, Malaysia 2024: 0.5 transshipments per shipment
    assert t["delay"]["mean"] == pytest.approx(4.8)
    dwell = next(lg for lg in o["legs"] if lg["name"].startswith("destination port"))
    assert (dwell["median"], dwell["q1"], dwell["q3"]) == (3.5, 1.8, 6.7)
