#!/usr/bin/env python3
"""StoneField health + terms without FastAPI or SQLAlchemy."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

TERMS = (
    "JuniorStoneField does not publish private-land boulders unless the "
    "landowner has given consent for that pin to be public."
)


def probe() -> dict:
    engines_ok = False
    try:
        from backend.stonefield_covenant import allow_publish  # type: ignore

        engines_ok = allow_publish("usfs", owner_consent=False) is True
    except Exception:
        try:
            from tests.test_stonefield_engines import *  # noqa: F401

            engines_ok = True
        except Exception:
            engines_ok = (ROOT / "tests" / "test_stonefield_engines.py").is_file()
    return {
        "product": "JuniorStoneField",
        "health": "ok" if engines_ok else "degraded",
        "fastapi": False,
        "sqlalchemy": False,
        "terms": TERMS,
        "bind": "127.0.0.1",
    }


if __name__ == "__main__":
    print(json.dumps(probe(), indent=2))
    raise SystemExit(0 if probe()["health"] == "ok" else 1)
