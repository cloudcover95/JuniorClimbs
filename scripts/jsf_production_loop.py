#!/usr/bin/env python3
"""JuniorStoneField production loop — engine tests + BitNet field probe + covenant gate."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def run_tests() -> int:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT)
    r = subprocess.run(
        [sys.executable, str(ROOT / "tests" / "test_stonefield_engines.py")],
        cwd=str(ROOT),
        env=env,
    )
    return r.returncode


def probe_bitnet() -> dict:
    from backend.bitnet_field_core import field_core

    return field_core.score("dry granite, USFS open, V4 crimp line").to_dict()


def probe_covenant() -> None:
    from backend.stonefield_covenant import outdoor_publish_allowed

    ok, _ = outdoor_publish_allowed("private", False, "public")
    if ok:
        raise SystemExit("covenant gate failed — private publish must be blocked")


def main() -> int:
    print("JuniorStoneField production loop")
    probe_covenant()
    probe = probe_bitnet()
    print("bitnet_field", probe["backend"], probe["condition"], probe["access"])
    rc = run_tests()
    print("tests", "PASS" if rc == 0 else "FAIL")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
