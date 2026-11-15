"""Platform-independent seeds (kept free of heavy imports so it can be checked in a subprocess quickly)."""
from __future__ import annotations

import zlib


def stable_seed(base: int, *parts: str) -> int:
    """Seed from a base seed and labels; Python's hash() is salted per process, so CRC32 is used instead."""
    return (int(base) ^ zlib.crc32("|".join(parts).encode("utf-8"))) & 0xFFFFFFFF
