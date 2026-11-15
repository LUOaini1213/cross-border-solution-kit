"""Incoterms 2020 responsibility checks for a quotation."""
from __future__ import annotations

from .reference import Reference

RULES = ("EXW", "FCA", "FAS", "FOB", "CFR", "CIF", "CPT", "CIP", "DAP", "DPU", "DDP")
SEA_MODES = {"ocean_fcl", "ocean_lcl", "ocean_fcl20", "rail_sea_fcl", "ocean_bulk_local"}


def payer(ref: Reference, rule: str | None, element: str, quoting_role: str) -> str:
    """'buyer' / 'seller' / 'owner' for one cost element.

    With no sale (temporary moves of the owner's goods) every element is the owner's.
    """
    if rule is None:
        return "owner"
    code = ref.incoterms["payer"][rule][element]
    return {"S": "seller", "B": "buyer"}[code]


def in_quote(ref: Reference, rule: str | None, element: str, quoting_role: str) -> bool:
    """A cost belongs in our quotation to Customer A when Customer A pays it under the sale terms."""
    p = payer(ref, rule, element, quoting_role)
    return p == quoting_role or p == "owner"


def check(ref: Reference, rule: str | None, quoting_role: str, modes: list[str]) -> list[dict]:
    """Consistency findings for the RFQ's Incoterm, the quoting party and the candidate modes."""
    out = []
    if rule is None:
        if quoting_role != "owner":
            out.append({"id": "INCO-NO-RULE", "severity": "medium",
                        "en": "No Incoterm given although goods are sold; cost responsibility is undefined.",
                        "zh": "货物涉及销售却未约定贸易术语，费用责任划分不明确。"})
        return out
    if rule not in RULES:
        raise ValueError(f"unknown Incoterm {rule}")
    sea_only = set(ref.incoterms["sea_only"])
    bad = [m for m in modes if rule in sea_only and m not in SEA_MODES]
    if bad:
        out.append({"id": "INCO-SEA-ONLY", "severity": "high",
                    "en": f"{rule} is a sea/inland-waterway rule but the RFQ allows {', '.join(bad)}; use FCA/CPT/CIP instead.",
                    "zh": f"{rule} 仅适用于海运/内河运输，但询价允许 {', '.join(bad)}，应改用 FCA/CPT/CIP。",
                    "statements": ["INCO-RULES"]})
    if quoting_role == "buyer" and ref.incoterms["payer"][rule]["main_carriage"] == "S":
        out.append({"id": "INCO-SELLER-CARRIAGE", "severity": "high",
                    "en": f"Under {rule} the seller buys the main carriage; quoting it to the buyer would double-charge.",
                    "zh": f"{rule} 下主运费由卖方承担，向买方报价将造成重复计费。", "statements": ["INCO-RULES"]})
    if rule == "DDP" and quoting_role == "seller":
        out.append({"id": "INCO-DDP-IOR", "severity": "medium",
                    "en": "DDP makes the seller the importer of record; a non-resident seller needs an appointed importer or a registered tax position in each market.",
                    "zh": "DDP 下卖方为进口登记人；非居民卖方须在各市场指定进口商或取得相应税务登记。",
                    "statements": ["INCO-RULES"]})
    if rule == "FCA" and quoting_role == "buyer":
        out.append({"id": "INCO-FCA-EXPORT", "severity": "info",
                    "en": "Under FCA the seller clears goods for export and loads them at its premises; export clearance is excluded from the buyer's quotation.",
                    "zh": "FCA 下由卖方办理出口清关并在其场所装货，出口报关费不计入买方报价。",
                    "statements": ["INCO-RULES"]})
    return out
