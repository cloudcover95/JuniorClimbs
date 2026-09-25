#!/usr/bin/env python3
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.trit_unpack import (
    flip_packed,
    flip_packed_all_signs,
    pack,
    pack_centered,
    pack_delta,
    pack_i2s,
    trit_ham,
    unpack,
    unpack_i2s,
)


class TritUnpackTests(unittest.TestCase):
    def test_pack_unpack_roundtrip(self) -> None:
        blob = pack([3, -8, 0, 5, -1, 2])
        self.assertEqual(unpack(blob), blob["trits"])
        bits, n = pack_i2s(blob["trits"])
        self.assertEqual(unpack_i2s(bits, n), blob["trits"])

    def test_centered_and_delta_modes(self) -> None:
        ids = list(range(12))
        c = pack_centered(ids)
        d = pack_delta(ids)
        self.assertEqual(c["mode"], "centered")
        self.assertEqual(d["mode"], "delta")
        self.assertEqual(unpack(c), c["trits"])
        self.assertEqual(unpack(d), d["trits"])

    def test_flip_packed_zero_stays(self) -> None:
        trits = [1, 0, -1, 1]
        bits, n = pack_i2s(trits)
        flipped = flip_packed(bits, n, 1)
        self.assertEqual(unpack_i2s(flipped, n)[1], 0)
        flipped0 = flip_packed(bits, n, 0)
        self.assertEqual(unpack_i2s(flipped0, n)[0], -1)

    def test_flip_all_signs(self) -> None:
        trits = [1, 0, -1, 1, 0]
        bits, n = pack_i2s(trits)
        out = unpack_i2s(flip_packed_all_signs(bits, n), n)
        self.assertEqual(out, [-1, 0, 1, -1, 0])

    def test_hamming_identity(self) -> None:
        a = pack([1, 2, 3])["trits"]
        self.assertEqual(trit_ham(a, a), 0)

    def test_not_a_hash(self) -> None:
        self.assertFalse(pack([1, 2, 3]).get("collision_resistant"))


if __name__ == "__main__":
    unittest.main()
