"""JuniorArenaNode + JuniorRegionSphere + LookAR routes."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database import SessionLocal
from backend.models_sphere import ArenaNode, RegionSphere, SphereHotspot
from backend.models_navmesh import GpsFix
from backend.models_stonefield import ClimbProblem
from backend.seed_sphere import ensure_sphere_seed
from backend.sphere_engine import look_lock, hotspot_payload
from backend.sphere_viewer import render_viewer

router = APIRouter(tags=["JuniorRegionSphere"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ArenaIn(BaseModel):
    name: str
    lat: float
    lon: float
    field_id: int | None = None
    kind: str = "trailhead"
    radius_m: float = 80.0
    notes: str | None = None


class HotspotIn(BaseModel):
    sphere_id: int
    name: str
    yaw_deg: float
    pitch_deg: float = 0.0
    node_id: int | None = None
    lat: float | None = None
    lon: float | None = None
    thumb_path: str = ""
    notes: str | None = None


def _last_fix(db: Session) -> GpsFix | None:
    return db.query(GpsFix).order_by(GpsFix.id.desc()).first()


@router.get("/arena")
def list_arenas(db: Session = Depends(get_db)):
    ensure_sphere_seed(db)
    rows = db.query(ArenaNode).all()
    return [
        {
            "id": r.id,
            "name": r.name,
            "lat": r.lat,
            "lon": r.lon,
            "kind": r.kind,
            "radius_m": r.radius_m,
            "field_id": r.field_id,
            "notes": r.notes,
            "spheres": [s.id for s in r.spheres],
        }
        for r in rows
    ]


@router.post("/arena")
def create_arena(payload: ArenaIn, db: Session = Depends(get_db)):
    row = ArenaNode(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.get("/sphere/{sphere_id}")
def get_sphere(sphere_id: int, db: Session = Depends(get_db)):
    ensure_sphere_seed(db)
    sph = db.get(RegionSphere, sphere_id)
    if not sph:
        raise HTTPException(404, "Sphere not found")
    arena = sph.arena
    fix = _last_fix(db)
    spots = [
        hotspot_payload(
            h,
            arena.lat,
            arena.lon,
            fix.lat if fix else None,
            fix.lon if fix else None,
        )
        for h in sph.hotspots
    ]
    return {
        "id": sph.id,
        "name": sph.name,
        "pano_path": sph.pano_path,
        "north_offset_deg": sph.north_offset_deg,
        "arena": {"id": arena.id, "name": arena.name, "lat": arena.lat, "lon": arena.lon},
        "hotspots": spots,
    }


@router.get("/sphere/{sphere_id}/look")
def look(sphere_id: int, heading: float = 0.0, db: Session = Depends(get_db)):
    data = get_sphere(sphere_id, db)
    lock = look_lock(heading, data["hotspots"])
    locked = lock["locked"]
    if locked and locked.get("node_id"):
        probs = db.query(ClimbProblem).filter(ClimbProblem.node_id == locked["node_id"]).all()
        lock["problems"] = [{"id": p.id, "name": p.name, "grade": p.grade} for p in probs]
    return lock


@router.get("/sphere/{sphere_id}/ar")
def ar_payload(sphere_id: int, heading: float = 0.0, db: Session = Depends(get_db)):
    data = get_sphere(sphere_id, db)
    lock = look_lock(heading, data["hotspots"], fov_deg=24.0)
    return {
        "mode": "ar",
        "sphere_id": sphere_id,
        "pano_path": data["pano_path"],
        "arena": data["arena"],
        "heading": heading,
        "lock": lock,
        "hotspots": data["hotspots"],
        "bitnet": "ternary-heading-lock",
        "note": "Project hotspots by yaw-heading onto camera or 2D stand-in.",
    }


@router.post("/sphere/hotspot")
def add_hotspot(payload: HotspotIn, db: Session = Depends(get_db)):
    if not db.get(RegionSphere, payload.sphere_id):
        raise HTTPException(404, "Sphere not found")
    row = SphereHotspot(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.get("/sphere/view/{sphere_id}", response_class=HTMLResponse)
def view(sphere_id: int, db: Session = Depends(get_db)):
    data = get_sphere(sphere_id, db)
    return render_viewer(data)
