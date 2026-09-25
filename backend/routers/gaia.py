"""Gaia + trit beta endpoints. Domain label is a field, not a hard-coded gym."""
from __future__ import annotations

import sys
from pathlib import Path

from fastapi import APIRouter
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.services.gaia_trit import beta_status, compare_series, envelope, flip_note, pulse

router = APIRouter(prefix="/api/v1/gaia", tags=["Gaia / Trit"])


@router.get("/status")
def status() -> dict[str, Any]:
    return beta_status()


@router.post("/handshake")
def do_handshake(payload: dict) -> dict[str, Any]:
    note = str(payload.get("note") or "home dash")
    area = str(payload.get("area") or "home")
    mode = str(payload.get("mode") or "centered")
    return envelope(note, area=area, mode=mode)


@router.post("/pulse")
def do_pulse(payload: dict) -> dict[str, Any]:
    note = str(payload.get("note") or "home dash")
    area = str(payload.get("area") or "home")
    return pulse(note, area=area)


@router.post("/compare")
def do_compare(payload: dict) -> dict[str, Any]:
    a = payload.get("a") or []
    b = payload.get("b") or []
    return compare_series(list(a), list(b))


@router.post("/flip")
def do_flip(payload: dict) -> dict[str, Any]:
    note = str(payload.get("note") or "home dash")
    index = int(payload.get("index") or 0)
    return flip_note(note, index=index)


@router.get("/areas")
def areas() -> dict[str, Any]:
    from core.gaia_threads import AREAS, JOBS, LAYERS, PROTO

    return {"protocol": PROTO, "layers": list(LAYERS), "areas": list(AREAS), "jobs": list(JOBS)}
