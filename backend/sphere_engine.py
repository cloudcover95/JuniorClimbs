"""JuniorLookFrame — heading lock + BitNet confidence for sphere hotspots."""
from __future__ import annotations

import math
from typing import Any

from backend.navmesh_engine import bearing_deg, compass, haversine_mi, goto
from backend.bitnet_field_core import ternary_embed, cosine_ternary


def wrap360(deg: float) -> float:
    return deg % 360.0


def angular_delta(a: float, b: float) -> float:
    d = abs(wrap360(a) - wrap360(b)) % 360.0
    return min(d, 360.0 - d)


def yaw_from_gps(arena_lat: float, arena_lon: float, tgt_lat: float, tgt_lon: float, north_offset: float = 0.0) -> float:
    return wrap360(bearing_deg(arena_lat, arena_lon, tgt_lat, tgt_lon) - north_offset)


def look_lock(heading_deg: float, hotspots: list[dict[str, Any]], fov_deg: float = 28.0) -> dict[str, Any]:
    """Pick the hotspot the user is facing. BitNet embed of heading token vs hotspot name for tie-break."""
    heading = wrap360(heading_deg)
    ranked = []
    head_emb = ternary_embed(f"heading {int(heading)} {compass(heading)}")
    for hs in hotspots:
        yaw = float(hs.get("yaw_deg") or 0.0)
        delta = angular_delta(heading, yaw)
        name_emb = ternary_embed(str(hs.get("name") or ""))
        sim = cosine_ternary(head_emb, name_emb)
        # lock score: mostly angle, tiny ternary prior so names do not dominate
        score = max(0.0, 1.0 - delta / max(fov_deg, 1.0)) + 0.05 * max(0.0, sim)
        ranked.append({**hs, "delta_deg": round(delta, 1), "lock_score": round(score, 3)})
    ranked.sort(key=lambda r: r["delta_deg"])
    locked = ranked[0] if ranked and ranked[0]["delta_deg"] <= fov_deg else None
    return {
        "heading_deg": round(heading, 1),
        "compass": compass(heading),
        "locked": locked,
        "nearby": ranked[:6],
        "mode": "ar-lock" if locked else "scan",
        "bitnet": "ternary-heading-lock",
    }


def hotspot_payload(
    hs,
    arena_lat: float,
    arena_lon: float,
    fix_lat: float | None = None,
    fix_lon: float | None = None,
) -> dict[str, Any]:
    out = {
        "id": hs.id,
        "name": hs.name,
        "yaw_deg": hs.yaw_deg,
        "pitch_deg": hs.pitch_deg,
        "node_id": hs.node_id,
        "lat": hs.lat,
        "lon": hs.lon,
        "thumb_path": hs.thumb_path,
        "notes": hs.notes,
        "compass_from_arena": compass(hs.yaw_deg) if hs.yaw_deg is not None else None,
    }
    if hs.lat is not None and hs.lon is not None:
        out["from_arena"] = goto(arena_lat, arena_lon, hs.lat, hs.lon)
        if fix_lat is not None and fix_lon is not None:
            out["from_fix"] = goto(fix_lat, fix_lon, hs.lat, hs.lon)
    return out
