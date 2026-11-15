from __future__ import annotations

import copy

import pytest

from cbsk import pipeline, schema
from cbsk.calc import RateBook
from cbsk.flows.common import Ctx
from cbsk.io import TEMPLATES
from cbsk.reference import Reference


@pytest.fixture(scope="session")
def runs():
    """One pipeline run per template, shared by the tests (about 3 s)."""
    return {name: pipeline.run_template(name) for name in pipeline.TEMPLATES_ORDER}


@pytest.fixture()
def ref():
    return Reference()


@pytest.fixture()
def rfqs():
    return {name: schema.load_rfq(TEMPLATES / name / "rfq.yaml") for name in pipeline.TEMPLATES_ORDER}


def make_ctx(ref: Reference, rfq: dict, draws: int = 2000) -> Ctx:
    return Ctx(ref, RateBook(), rfq["incoterm"], rfq["quoting_party_role"], int(rfq["seed"]), draws)


def option(results: dict, option_id: str) -> dict:
    for lane in results["lanes"]:
        for o in lane["options"]:
            if o["id"] == option_id:
                return o
    raise KeyError(option_id)


def node(opt: dict, short: str) -> float:
    for c in opt["costs"]:
        if c["code"].endswith("." + short):
            return c["value"]
    raise KeyError(short)


@pytest.fixture()
def clone():
    return copy.deepcopy
