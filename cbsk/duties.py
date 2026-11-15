"""Duty and tax calculations. Pure functions on numbers so they can be checked by hand in tests.

Only rules recorded in data/reference/regulatory_statements.yaml are implemented; where a rate is
not verified the caller passes a labelled placeholder and the result carries the statement id so
reports can say "not verified".
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .reference import Reference

ISO3 = {"CN": "CHN", "MY": "MYS", "SG": "SGP", "ID": "IDN", "TH": "THA", "PH": "PHL", "JP": "JPN", "US": "USA",
        "DE": "DEU", "VN": "VNM", "LA": "LAO", "KH": "KHM", "MM": "MMR"}


@dataclass
class TaxResult:
    regime: str
    duty: float = 0.0
    consumption_tax: float = 0.0      # VAT / GST / sales tax borne by the consumer or the importer
    income_tax: float = 0.0           # Indonesian PPh on consignments
    duty_rate: float = 0.0
    tax_rate: float = 0.0
    statements: list[str] = field(default_factory=list)
    note: str = ""

    @property
    def total(self) -> float:
        return self.duty + self.consumption_tax + self.income_tax

    def as_dict(self) -> dict:
        return {"regime": self.regime, "duty": self.duty, "consumption_tax": self.consumption_tax,
                "income_tax": self.income_tax, "total": self.total, "duty_rate": self.duty_rate,
                "tax_rate": self.tax_rate, "statements": list(self.statements), "note": self.note}


# ---------------------------------------------------------------- Malaysia, B2B import
def my_import_line(goods_value: float, freight_insurance_alloc: float, duty_rate: float, sales_tax_rate: float,
                   schedule_c_exempt: bool) -> dict:
    """Customs value on a CIF basis; sales tax on customs value + duty (Sales Tax Act 2018 s.9(2)).
    Excise is nil for these lines."""
    cv = goods_value + freight_insurance_alloc
    duty = duty_rate * cv
    st = 0.0 if schedule_c_exempt else sales_tax_rate * (cv + duty)
    return {"customs_value": cv, "duty": duty, "sales_tax": st}


def fta_options_my(ref: Reference, hs: str, origin: str, rvc_pct: float | None, cth_met: bool | None) -> list[dict]:
    """Candidate tariff treatments for one Malaysian import line from a given origin."""
    comp = ref.get("compliance.fta")
    heading = hs.replace(".", "")[:4]
    out = [{"scheme": "MFN", "rate": ref.my_tariff(hs, "mfn_import"), "available": True,
            "reason": "general rate", "statements": ["MY-TARIFF-LINES"]}]
    acfta_ok = origin in comp["ACFTA"]["parties"] and rvc_pct is not None and rvc_pct >= 40.0
    out.append({"scheme": "ACFTA", "rate": ref.my_tariff(hs, "acfta_current"), "available": acfta_ok,
                "reason": ("supplier RVC >= 40% (general rule)" if acfta_ok
                           else "supplier RVC below 40%: general rule not met (product-specific rule not checked)"),
                "statements": ["FTA-ACFTA-ORIGIN", "MY-TARIFF-LINES"]})
    psr = comp["RCEP"]["origin_rule_by_heading"].get(heading)
    rvc_ok = rvc_pct is not None and rvc_pct >= 40.0
    if psr == "CTH or RVC40":
        rcep_ok = origin in comp["RCEP"]["parties"] and (rvc_ok or cth_met is True)
        why = "PSR CTH or RVC40: " + ("met" if rcep_ok else "neither RVC40 nor CTH confirmed")
    else:
        rcep_ok = origin in comp["RCEP"]["parties"] and rvc_ok
        why = "PSR not checked for this heading; RVC40 assumed sufficient" if rcep_ok else "RVC below 40%; PSR not checked"
    try:
        rcep_rate = ref.my_tariff(hs, "rcep_current")
    except ValueError:
        rcep_rate, rcep_ok, why = None, False, "no RCEP rate published for this line"
    out.append({"scheme": "RCEP", "rate": rcep_rate, "available": rcep_ok, "reason": why,
                "statements": ["FTA-RCEP-PSR", "FTA-RCEP-POO", "MY-TARIFF-LINES"]})
    return out


def choose_tariff(options: list[dict], preference: str = "auto") -> dict:
    """Lowest available rate; MFN wins ties (no origin paperwork). `preference` forces a scheme if available."""
    avail = [o for o in options if o["available"] and o["rate"] is not None]
    if preference not in ("auto", "none"):
        forced = [o for o in avail if o["scheme"] == preference]
        if forced:
            return forced[0]
    if preference == "none":
        return next(o for o in options if o["scheme"] == "MFN")
    order = {"MFN": 0, "ACFTA": 1, "RCEP": 2}
    return min(avail, key=lambda o: (round(o["rate"], 9), order[o["scheme"]]))


# ---------------------------------------------------------------- B2C parcels
def _prefix_rate(hs: str, table: list[dict]) -> dict | None:
    digits = hs.replace(".", "")
    for row in table:
        for p in row["prefixes"]:
            if digits.startswith(p):
                return row
    return None


def parcel_taxes(ref: Reference, dest: str, channel: str, hs: str, retail: float, shipping: float,
                 seller_registered_lvg: bool = True) -> TaxResult:
    """Duties and taxes on one B2C parcel holding one item.

    channel: air_courier (air courier / postal, incl. the air leg of sea-air), road, sea, rail.
    Customs value of a B2C sale = price paid + shipping charged (CIF basis where the destination values
    on CIF); value tests that the rules define on FOB/FCA use the item price.
    """
    cif = retail + shipping
    heading = hs.replace(".", "")[:4]
    if dest == "MY":
        fx = float(ref.get("regimes.fx.MYR"))
        lvg_limit = float(ref.get("regimes.MY.lvg_price_threshold_myr"))
        is_lvg = retail * fx <= lvg_limit
        lvg_tax = float(ref.get("regimes.MY.lvg_rate")) * retail if (is_lvg and seller_registered_lvg) else 0.0
        mfn = ref.my_tariff(hs, "mfn_import")
        if channel == "air_courier":
            dm_limit = float(ref.get("regimes.MY.deminimis_cif_myr"))
            if cif * fx <= dm_limit:
                return TaxResult("MY LVG + air-courier de minimis", 0.0, lvg_tax, 0.0, 0.0,
                                 float(ref.get("regimes.MY.lvg_rate")) if lvg_tax else 0.0,
                                 ["MY-LVG", "MY-DEMINIMIS", "MY-LVG-NO-DOUBLE"])
        duty = mfn * cif
        if lvg_tax:
            return TaxResult("MY LVG, duty at import (no de minimis by road/sea)", duty, lvg_tax, 0.0, mfn,
                             float(ref.get("regimes.MY.lvg_rate")), ["MY-LVG", "MY-DEMINIMIS", "MY-LVG-NO-DOUBLE", "MY-TARIFF-LINES"])
        st = ref.my_tariff(hs, "sst")
        return TaxResult("MY general import", duty, st * (cif + duty), 0.0, mfn, st,
                         ["MY-TARIFF-LINES", "MY-ST-IMPORT-BASE", "MY-VALUATION-CIF"])
    if dest == "ID":
        if channel not in ("air_courier",):
            raise ValueError("Indonesian consignment regime modelled for air courier only")
        dm = float(ref.get("regimes.ID.deminimis_fob_usd"))
        upper = float(ref.get("regimes.ID.band_upper_fob_usd"))
        vat_eff = float(ref.get("regimes.ID.vat_nominal")) * float(ref.get("regimes.ID.vat_base_fraction"))
        if retail <= dm:
            return TaxResult("ID consignment <= USD 3", 0.0, vat_eff * cif, 0.0, 0.0, vat_eff,
                             ["ID-CN-DEMINIMIS", "ID-VAT-EFFECTIVE", "ID-IMPORT-VALUE"])
        if retail <= upper:
            row = _prefix_rate(hs, ref.get("regimes.ID.band_specific_rates"))
            rate = row["rate"] if row else float(ref.get("regimes.ID.band_duty_rate"))
            duty = rate * cif
            base = cif + duty
            pph = float(ref.get("regimes.ID.pph_specific_rate")) * base if (row and row["pph"]) else 0.0
            return TaxResult("ID consignment USD 3-1,500", duty, vat_eff * base, pph, rate, vat_eff,
                             ["ID-CN-BAND", "ID-VAT-EFFECTIVE", "ID-IMPORT-VALUE"],
                             note=(row["group"] if row else "general 7.5%"))
        rate = float(ref.get("regimes.ID.mfn_placeholder_rate"))
        duty = rate * cif
        return TaxResult("ID above USD 1,500 (placeholder MFN)", duty, vat_eff * (cif + duty), 0.0, rate, vat_eff,
                         ["ID-ABOVE-1500", "ID-VAT-EFFECTIVE"])
    if dest == "TH":
        fx = float(ref.get("regimes.fx.THB"))
        vat = float(ref.get("regimes.TH.vat_rate"))
        if cif * fx <= float(ref.get("regimes.TH.duty_exemption_customs_value_thb")):
            return TaxResult("TH exempt (<= 1 baht)", 0.0, vat * cif, 0.0, 0.0, vat, ["TH-DUTY-1BAHT", "TH-VAT"])
        rate = float(ref.get("regimes.TH.mfn_placeholder_rates")[heading])
        duty = rate * cif
        return TaxResult("TH dutiable from 1 Jan 2026 (placeholder MFN)", duty, vat * (cif + duty), 0.0, rate, vat,
                         ["TH-DUTY-1BAHT", "TH-VAT", "TH-MFN"])
    if dest == "PH":
        fx = float(ref.get("regimes.fx.PHP"))
        if retail * fx <= float(ref.get("regimes.PH.deminimis_fob_php")):
            return TaxResult("PH de minimis (FOB <= PHP 10,000)", 0.0, 0.0, 0.0, 0.0, 0.0, ["PH-DEMINIMIS"])
        rate = float(ref.get("regimes.PH.mfn_placeholder_rates")[heading])
        vat = float(ref.get("regimes.PH.vat_rate"))
        duty = rate * cif
        return TaxResult("PH above de minimis (placeholder MFN)", duty, vat * (cif + duty), 0.0, rate, vat,
                         ["PH-DEMINIMIS", "PH-VAT", "PH-MFN"])
    raise ValueError(f"no parcel regime for {dest}")


def bulk_import_taxes(ref: Reference, dest: str, hs: str, cif_unit: float, retail: float) -> TaxResult:
    """Per-unit duties and consumption tax when stock is imported in bulk and sold locally.

    Malaysia: sales tax is single-stage, charged on import on CIF + duty and not again on the local sale.
    VAT countries (ID, TH, PH): import VAT is creditable for a registered importer; the consumer bears
    output VAT on the retail price, which is what is counted here.
    """
    heading = hs.replace(".", "")[:4]
    if dest == "MY":
        mfn = ref.my_tariff(hs, "mfn_import")
        st = ref.my_tariff(hs, "sst")
        duty = mfn * cif_unit
        return TaxResult("MY bulk import: duty + single-stage sales tax", duty, st * (cif_unit + duty), 0.0, mfn, st,
                         ["MY-TARIFF-LINES", "MY-ST-IMPORT-BASE", "MY-VALUATION-CIF"])
    if dest == "ID":
        rate = float(ref.get("regimes.ID.mfn_placeholder_rate"))
        vat_eff = float(ref.get("regimes.ID.vat_nominal")) * float(ref.get("regimes.ID.vat_base_fraction"))
        return TaxResult("ID bulk import (placeholder MFN) + output VAT on retail", rate * cif_unit, vat_eff * retail,
                         0.0, rate, vat_eff, ["ID-ABOVE-1500", "ID-VAT-EFFECTIVE", "ID-LICENSING"])
    if dest == "TH":
        rate = float(ref.get("regimes.TH.mfn_placeholder_rates")[heading])
        vat = float(ref.get("regimes.TH.vat_rate"))
        return TaxResult("TH bulk import (placeholder MFN) + output VAT on retail", rate * cif_unit, vat * retail,
                         0.0, rate, vat, ["TH-MFN", "TH-VAT"])
    if dest == "PH":
        rate = float(ref.get("regimes.PH.mfn_placeholder_rates")[heading])
        vat = float(ref.get("regimes.PH.vat_rate"))
        return TaxResult("PH bulk import (placeholder MFN) + output VAT on retail", rate * cif_unit, vat * retail,
                         0.0, rate, vat, ["PH-MFN", "PH-VAT"])
    raise ValueError(f"no bulk regime for {dest}")


# ---------------------------------------------------------------- Singapore temporary moves
def sg_tis_security(ref: Reference, cif_value: float, gst_registered: bool) -> float:
    gst = float(ref.get("regimes.SG.gst_rate"))
    share = float(ref.get("regimes.SG.tis_security_share_registered" if gst_registered
                          else "regimes.SG.tis_security_share_unregistered"))
    return share * gst * cif_value


def sg_repair_reimport_gst(ref: Reference, item_value: float, new_parts_share: float, warranty_share: float) -> float:
    """Expected GST per repair loop: GST on new parts unless repaired free under warranty."""
    gst = float(ref.get("regimes.SG.gst_rate"))
    return gst * item_value * new_parts_share * (1.0 - warranty_share)
