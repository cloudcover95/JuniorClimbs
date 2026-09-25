"""Climbs-facing adapter over domain-agnostic Gaia + trit cores.

Does not replace BitNet-mlx. Optional spatial hook only.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from core.gaia_threads import GaiaPool, handshake
from core.trit_unpack import pack, pack_centered, pack_delta, pack_note, trit_ham, unpack, flip_packed, unpack_i2s


_POOL = GaiaPool()


def envelope(note: str, area: str = "climbs", mode: str = "centered") -> dict:
    return handshake(note, area=area, mode=mode, job="dash-viewport")


def pulse(note: str = "climbs wall view", area: str = "climbs") -> dict:
    return _POOL.pulse(note, area=area, mode="centered")


def compare_series(a: list[int] | list[float], b: list[int] | list[float]) -> dict:
    pa, pb = pack(a), pack(b)
    ca, cb = pack_centered(a), pack_centered(b)
    da, db = pack_delta(a), pack_delta(b)
    return {
        "raw_ham": trit_ham(pa["trits"], pb["trits"]),
        "centered_ham": trit_ham(ca["trits"], cb["trits"]),
        "delta_ham": trit_ham(da["trits"], db["trits"]),
        "same_raw_hex": pa["i2s_hex"] == pb["i2s_hex"],
        "centered_hex_eq": ca["i2s_hex"] == cb["i2s_hex"],
        "collision_resistant": False,
    }


def flip_note(note: str, index: int = 0) -> dict:
    packed = pack_note(note, mode="centered")
    bits = int(packed["i2s_hex"], 16)
    flipped = flip_packed(bits, packed["n"], index)
    return {
        "note": note,
        "index": index,
        "before": packed["trits"],
        "after": unpack_i2s(flipped, packed["n"]),
        "before_hex": packed["i2s_hex"],
        "after_hex": format(flipped, "x"),
        "unpacked_roundtrip": unpack(packed) == packed["trits"],
    }


def beta_status() -> dict[str, Any]:
    sample = pulse("climbs beta core")
    return {
        "grade": "live-beta",
        "domain_agnostic": True,
        "bitnet_replaced": False,
        "area": (sample.get("envelope") or {}).get("note", {}).get("area"),
        "schema_ok": (sample.get("envelope") or {}).get("schema_ok"),
        "layers": list((sample.get("layers") or {}).keys()),
        "witness": sample.get("witness"),
    }
