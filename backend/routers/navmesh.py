"""JuniorNavMesh FastAPI router — offline maps, land, overland, GPX, IoT GPS."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database import SessionLocal
from backend.models_navmesh import (
    TilePack,
    LandLayer,
    OverlandNode,
    Waypoint,
    TrackRibbon,
    ApproachPath,
    GpsFix,
)
from backend.models_stonefield import BoulderNode
from backend.navmesh_engine import (
    OFFLINE,
    goto,
    parse_nmea,
    parse_gpx,
    tracks_to_gpx,
    waypoints_to_gpx,
    dump_points,
    load_points,
    point_in_bbox,
)
from backend.seed_navmesh import ensure_navmesh_seed

router = APIRouter(prefix="/nav", tags=["JuniorNavMesh"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class FixIn(BaseModel):
    device_id: str = "handheld-1"
    lat: float
    lon: float
    elev_m: float | None = None
    hdop: float | None = None
    sats: int | None = None
    source: str = "manual"


class NmeaIn(BaseModel):
    device_id: str = "handheld-1"
    sentence: str


class WaypointIn(BaseModel):
    name: str
    lat: float
    lon: float
    elev_ft: float | None = None
    kind: str = "user"
    node_id: int | None = None
    notes: str | None = None


class OverlandIn(BaseModel):
    name: str
    kind: str = "trailhead"
    lat: float
    lon: float
    field_id: int | None = None
    notes: str | None = None
    conditions: str | None = None
    submitted_by: str = "anon"


class TrackIn(BaseModel):
    name: str
    klass: str = "approach"
    points: list[list[float]]
    field_id: int | None = None
    node_id: int | None = None
    notes: str | None = None


class GpxImportIn(BaseModel):
    xml: str
    as_waypoints: bool = True
    as_tracks: bool = True


class ApproachIn(BaseModel):
    name: str
    from_overland_id: int | None = None
    to_node_id: int | None = None
    minutes: int | None = None
    distance_mi: float | None = None
    notes: str | None = None


def _last_fix(db: Session) -> GpsFix | None:
    return db.query(GpsFix).order_by(GpsFix.id.desc()).first()


@router.get("/status")
def nav_status(db: Session = Depends(get_db)):
    ensure_navmesh_seed(db)
    fix = _last_fix(db)
    return {
        "offline": OFFLINE,
        "vendor_links": False,
        "packs": db.query(TilePack).count(),
        "land_layers": db.query(LandLayer).count(),
        "overland": db.query(OverlandNode).count(),
        "waypoints": db.query(Waypoint).count(),
        "tracks": db.query(TrackRibbon).count(),
        "last_fix": None
        if fix is None
        else {
            "device_id": fix.device_id,
            "lat": fix.lat,
            "lon": fix.lon,
            "elev_m": fix.elev_m,
            "sats": fix.sats,
            "source": fix.source,
            "at": fix.created_at.isoformat() if fix.created_at else None,
        },
        "note": "All navigation is local. Load your own tile packs under data/tiles/.",
    }


@router.get("/packs")
def list_packs(db: Session = Depends(get_db)):
    ensure_navmesh_seed(db)
    rows = db.query(TilePack).all()
    return [
        {
            "id": r.id,
            "name": r.name,
            "kind": r.kind,
            "path": r.path,
            "zoom": [r.min_zoom, r.max_zoom],
            "bbox": [r.south, r.west, r.north, r.east],
            "offline_ready": r.offline_ready,
            "notes": r.notes,
        }
        for r in rows
    ]


@router.get("/land")
def list_land(lat: float | None = None, lon: float | None = None, db: Session = Depends(get_db)):
    ensure_navmesh_seed(db)
    rows = db.query(LandLayer).all()
    out = []
    for r in rows:
        hit = None
        if lat is not None and lon is not None:
            hit = point_in_bbox(lat, lon, r.south, r.west, r.north, r.east)
        out.append(
            {
                "id": r.id,
                "name": r.name,
                "tenure": r.tenure,
                "access": r.access,
                "bbox": [r.south, r.west, r.north, r.east],
                "contains_point": hit,
                "notes": r.notes,
            }
        )
    return out


@router.get("/overland")
def list_overland(kind: str | None = None, db: Session = Depends(get_db)):
    ensure_navmesh_seed(db)
    q = db.query(OverlandNode)
    if kind:
        q = q.filter(OverlandNode.kind == kind)
    return q.all()


@router.post("/overland")
def add_overland(payload: OverlandIn, db: Session = Depends(get_db)):
    row = OverlandNode(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.get("/waypoints")
def list_waypoints(db: Session = Depends(get_db)):
    ensure_navmesh_seed(db)
    return db.query(Waypoint).all()


@router.post("/waypoints")
def add_waypoint(payload: WaypointIn, db: Session = Depends(get_db)):
    row = Waypoint(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.get("/tracks")
def list_tracks(db: Session = Depends(get_db)):
    rows = db.query(TrackRibbon).all()
    return [
        {
            "id": r.id,
            "name": r.name,
            "klass": r.klass,
            "points": load_points(r.points_json),
            "field_id": r.field_id,
            "node_id": r.node_id,
            "notes": r.notes,
        }
        for r in rows
    ]


@router.post("/tracks")
def add_track(payload: TrackIn, db: Session = Depends(get_db)):
    row = TrackRibbon(
        name=payload.name,
        klass=payload.klass,
        points_json=dump_points(payload.points),
        field_id=payload.field_id,
        node_id=payload.node_id,
        notes=payload.notes,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return {"id": row.id, "name": row.name, "points": payload.points}


@router.get("/tracks/{track_id}/gpx", response_class=PlainTextResponse)
def export_track_gpx(track_id: int, db: Session = Depends(get_db)):
    row = db.get(TrackRibbon, track_id)
    if not row:
        raise HTTPException(404, "Track not found")
    return tracks_to_gpx(row.name, load_points(row.points_json))


@router.get("/waypoints/gpx", response_class=PlainTextResponse)
def export_waypoints_gpx(db: Session = Depends(get_db)):
    rows = db.query(Waypoint).all()
    payload = [{"name": r.name, "lat": r.lat, "lon": r.lon, "elev_ft": r.elev_ft} for r in rows]
    return waypoints_to_gpx("JuniorNavMesh waypoints", payload)


@router.post("/gpx/import")
def import_gpx(payload: GpxImportIn, db: Session = Depends(get_db)):
    parsed = parse_gpx(payload.xml)
    created = {"waypoints": 0, "tracks": 0}
    if payload.as_waypoints:
        for w in parsed["waypoints"]:
            db.add(Waypoint(name=w["name"], lat=w["lat"], lon=w["lon"], kind="gpx"))
            created["waypoints"] += 1
    if payload.as_tracks:
        for t in parsed["tracks"]:
            db.add(
                TrackRibbon(
                    name=t["name"],
                    klass="gpx",
                    points_json=dump_points(t["points"]),
                )
            )
            created["tracks"] += 1
    db.commit()
    return {"imported": created, "offline": OFFLINE}


@router.post("/iot/fix")
def push_fix(payload: FixIn, db: Session = Depends(get_db)):
    row = GpsFix(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.post("/iot/nmea")
def push_nmea(payload: NmeaIn, db: Session = Depends(get_db)):
    parsed = parse_nmea(payload.sentence)
    if not parsed:
        raise HTTPException(400, "Unrecognized or void NMEA sentence")
    row = GpsFix(
        device_id=payload.device_id,
        lat=parsed["lat"],
        lon=parsed["lon"],
        elev_m=parsed.get("elev_m"),
        hdop=parsed.get("hdop"),
        sats=parsed.get("sats"),
        source=parsed.get("source", "nmea"),
        raw=payload.sentence,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.get("/iot/last")
def last_fix(db: Session = Depends(get_db)):
    row = _last_fix(db)
    if not row:
        return {"fix": None, "note": "No GNSS fix yet. POST /nav/iot/nmea or /nav/iot/fix."}
    return row


@router.get("/goto/node/{node_id}")
def goto_node(node_id: int, db: Session = Depends(get_db)):
    node = db.get(BoulderNode, node_id)
    if not node:
        raise HTTPException(404, "BoulderNode not found")
    fix = _last_fix(db)
    if not fix:
        return {
            "target": {"id": node.id, "name": node.name, "lat": node.lat, "lon": node.lon},
            "fix": None,
            "note": "Need a local GNSS fix before bearing/distance can be computed.",
        }
    nav = goto(fix.lat, fix.lon, node.lat, node.lon)
    nav["target"] = {"id": node.id, "name": node.name}
    nav["device_id"] = fix.device_id
    return nav


@router.get("/goto/overland/{oid}")
def goto_overland(oid: int, db: Session = Depends(get_db)):
    node = db.get(OverlandNode, oid)
    if not node:
        raise HTTPException(404, "OverlandNode not found")
    fix = _last_fix(db)
    if not fix:
        raise HTTPException(400, "No GNSS fix")
    nav = goto(fix.lat, fix.lon, node.lat, node.lon)
    nav["target"] = {"id": node.id, "name": node.name, "kind": node.kind}
    return nav


@router.post("/approach")
def add_approach(payload: ApproachIn, db: Session = Depends(get_db)):
    row = ApproachPath(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.get("/approach")
def list_approach(db: Session = Depends(get_db)):
    return db.query(ApproachPath).all()
