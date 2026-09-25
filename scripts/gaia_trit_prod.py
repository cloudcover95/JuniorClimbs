#!/usr/bin/env python3
"""Live-beta probe: trit unpack + Gaia threads. Domain-agnostic."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.gaia_threads import GaiaPool
from core.trit_unpack import pack, pack_centered, pack_delta, trit_ham, unpack, flip_packed_all_signs, unpack_i2s


def main() -> int:
    a = list(range(32))
    b = list(range(31, -1, -1))
    pa, pb = pack(a), pack(b)
    ca, cb = pack_centered(a), pack_centered(b)
    da, db = pack_delta(a), pack_delta(b)
    rt = unpack(ca)
    flipped = flip_packed_all_signs(int(ca["i2s_hex"], 16), ca["n"])
    pool = GaiaPool()
    pulses = {
        "home": pool.pulse("home dash beta"),
        "climbs": pool.pulse("climbs wall view", area="climbs"),
        "poker": pool.pulse("poker shoe felt", area="poker"),
        "quant": pool.pulse("quant trit series", area="quant"),
    }
    report = {
        "grade": "live-beta",
        "domain_agnostic": True,
        "raw_ham": trit_ham(pa["trits"], pb["trits"]),
        "centered_ham": trit_ham(ca["trits"], cb["trits"]),
        "delta_ham": trit_ham(da["trits"], db["trits"]),
        "unpack_roundtrip": rt == ca["trits"],
        "flip_changes": unpack_i2s(flipped, ca["n"]) != ca["trits"],
        "pulses_ok": {k: bool(v.get("ok")) for k, v in pulses.items()},
        "witnesses": {k: v.get("witness") for k, v in pulses.items()},
        "schema_ok": {k: (v.get("envelope") or {}).get("schema_ok") for k, v in pulses.items()},
    }
    print(json.dumps(report, indent=2))
    return 0 if report["unpack_roundtrip"] and all(report["pulses_ok"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
