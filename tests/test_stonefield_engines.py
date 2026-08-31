"""Industry-style unit tests for JuniorStoneField lean engines (stdlib unittest)."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.navmesh_engine import (  # noqa: E402
    haversine_mi,
    bearing_deg,
    compass,
    goto,
    parse_nmea,
    tracks_to_gpx,
    waypoints_to_gpx,
    parse_gpx,
)
from backend.bitnet_field_core import (  # noqa: E402
    ternary_embed,
    cosine_ternary,
    field_core,
    JuniorBitNetFieldCore,
)
from backend.stonefield_covenant import outdoor_publish_allowed, TERMS_VERSION  # noqa: E402
from backend.sphere_engine import look_lock, yaw_from_gps, wrap360  # noqa: E402
from backend.models_source import ALLOWED_LICENSES  # noqa: E402


class NavMathTests(unittest.TestCase):
    def test_haversine_zero(self):
        self.assertAlmostEqual(haversine_mi(40.0, -105.0, 40.0, -105.0), 0.0, places=6)

    def test_rfl_to_flagstaff_ballpark(self):
        d = haversine_mi(40.80154, -105.59009, 40.0014, -105.296)
        self.assertTrue(50 < d < 70, d)

    def test_bearing_east(self):
        b = bearing_deg(40.0, -105.0, 40.0, -104.0)
        self.assertTrue(80 < b < 100, b)
        self.assertEqual(compass(90), "E")

    def test_goto_keys(self):
        g = goto(40.74608, -105.54033, 40.86577, -105.52388)
        self.assertIn("distance_mi", g)
        self.assertIn("compass", g)
        self.assertTrue(g["distance_mi"] > 5)


class NmeaGpxTests(unittest.TestCase):
    def test_gga(self):
        s = "$GPGGA,123519,4048.0924,N,10535.4054,W,1,08,0.9,2500.0,M,0,M,,"
        p = parse_nmea(s)
        self.assertIsNotNone(p)
        self.assertAlmostEqual(p["lat"], 40.80154, places=3)
        self.assertTrue(p["lon"] < 0)

    def test_rmc_void(self):
        self.assertIsNone(parse_nmea("$GPRMC,123519,V,4048.0924,N,10535.4054,W,0,0,230506,,,,"))

    def test_gpx_roundtrip_track(self):
        pts = [[40.74608, -105.54033], [40.80154, -105.59009]]
        xml = tracks_to_gpx("elkhorn-rfl", pts)
        parsed = parse_gpx(xml)
        self.assertEqual(len(parsed["tracks"]), 1)
        self.assertEqual(len(parsed["tracks"][0]["points"]), 2)
        self.assertAlmostEqual(parsed["tracks"][0]["points"][0][0], 40.74608, places=5)

    def test_gpx_waypoints(self):
        xml = waypoints_to_gpx("wps", [{"name": "Xanadu", "lat": 40.86577, "lon": -105.52388}])
        parsed = parse_gpx(xml)
        self.assertEqual(parsed["waypoints"][0]["name"], "Xanadu")


class BitNetFieldTests(unittest.TestCase):
    def test_embed_ternary(self):
        v = ternary_embed("dry granite USFS open V4")
        self.assertEqual(len(v), 32)
        self.assertTrue(all(x in (-1, 0, 1) for x in v))

    def test_embed_deterministic(self):
        self.assertEqual(ternary_embed("crown rock"), ternary_embed("crown rock"))

    def test_cosine_range(self):
        a, b = ternary_embed("dry"), ternary_embed("seeping wet ice")
        self.assertTrue(-1.0 <= cosine_ternary(a, b) <= 1.0)

    def test_conditions_and_access(self):
        dry = field_core.score("crisp dry granite, good friction, USFS open")
        wet = field_core.score("seeping wet drainage, do not climb, private ranch")
        self.assertEqual(dry.condition, "dry")
        self.assertEqual(dry.access, "open")
        self.assertEqual(wet.condition, "seeping")
        self.assertEqual(wet.access, "private")

    def test_grade_bins(self):
        self.assertEqual(field_core.score("classic V6 crimp").grade_bin, "V5-V7")
        self.assertEqual(field_core.score("5.12c sport").grade_bin, "5.12+")

    def test_disagreement_rises(self):
        first = field_core.score("dry good friction")
        second = JuniorBitNetFieldCore().score("ice verglas frozen", prior_embed=first.embed)
        self.assertGreater(second.disagreement, 0.0)


class CovenantTests(unittest.TestCase):
    def test_public_ok(self):
        ok, _ = outdoor_publish_allowed("osmp", False, "public")
        self.assertTrue(ok)

    def test_private_blocked(self):
        ok, reason = outdoor_publish_allowed("private", False, "public")
        self.assertFalse(ok)
        self.assertIn("consent", reason)

    def test_unknown_blocked(self):
        ok, _ = outdoor_publish_allowed("unknown", False, "public")
        self.assertFalse(ok)

    def test_consent_allows(self):
        ok, _ = outdoor_publish_allowed("private", True, "public")
        self.assertTrue(ok)

    def test_gym_internal_always_ok(self):
        ok, why = outdoor_publish_allowed("unknown", False, "gym_internal")
        self.assertTrue(ok)
        self.assertEqual(why, "stored_non_public")

    def test_terms_version(self):
        self.assertTrue(TERMS_VERSION.startswith("jsf-covenant-"))


class SphereLockTests(unittest.TestCase):
    def test_wrap(self):
        self.assertEqual(wrap360(370), 10)

    def test_lock_nearest(self):
        spots = [
            {"id": 1, "name": "Crown Rock", "yaw_deg": 10},
            {"id": 2, "name": "First Overhang", "yaw_deg": 200},
        ]
        lock = look_lock(12, spots, fov_deg=28)
        self.assertEqual(lock["locked"]["id"], 1)
        self.assertEqual(lock["mode"], "ar-lock")

    def test_scan_when_far(self):
        spots = [{"id": 1, "name": "Nub", "yaw_deg": 0}]
        lock = look_lock(180, spots, fov_deg=20)
        self.assertIsNone(lock["locked"])
        self.assertEqual(lock["mode"], "scan")

    def test_yaw_from_gps_finite(self):
        y = yaw_from_gps(40.00179, -105.29708, 40.00323, -105.29856)
        self.assertTrue(0 <= y < 360)


class SourceLicenseTests(unittest.TestCase):
    def test_open_licenses_only(self):
        self.assertIn("CC-BY-4.0", ALLOWED_LICENSES)
        self.assertNotIn("proprietary", ALLOWED_LICENSES)


if __name__ == "__main__":
    unittest.main(verbosity=2)
