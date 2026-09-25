#!/usr/bin/env python3
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.gaia_threads import AREAS, LAYERS, GaiaPool, handshake, witness


class GaiaThreadTests(unittest.TestCase):
    def test_handshake_schema(self) -> None:
        env = handshake("home dash beta", area="home")
        self.assertEqual(env["system"], "JuniorGaia")
        self.assertTrue(env["schema_ok"])
        self.assertFalse(env["ue5_launch"])
        self.assertFalse(env["download"])
        self.assertIn(env["note"]["area"], AREAS)

    def test_area_ports_are_labels(self) -> None:
        climbs = handshake("ignore", area="climbs")
        poker = handshake("ignore", area="poker")
        self.assertEqual(climbs["note"]["port"], "JuniorClimbs")
        self.assertEqual(poker["note"]["port"], "JuniorPoker")

    def test_pool_pulse_all_layers(self) -> None:
        pulse = GaiaPool().pulse("quant trit series", area="quant")
        self.assertTrue(pulse["ok"])
        self.assertEqual(set(pulse["layers"].keys()), set(LAYERS))
        self.assertEqual(len(pulse["witness"]), 64)

    def test_witness_stable(self) -> None:
        env = handshake("home dash", area="home", mode="raw")
        self.assertEqual(witness(env), witness(env))


if __name__ == "__main__":
    unittest.main()
