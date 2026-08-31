"""Seed JuniorArenaNodes + RegionSphere hotspots for Red Feather Lakes."""
from __future__ import annotations

from sqlalchemy.orm import Session

from backend.models_sphere import ArenaNode, RegionSphere, SphereHotspot
from backend.models_stonefield import StoneField, BoulderNode
from backend.seed_red_feather import ensure_red_feather_seed
from backend.sphere_engine import yaw_from_gps


def ensure_sphere_seed(db: Session) -> None:
    field = ensure_red_feather_seed(db)
    if db.query(ArenaNode).count() > 0:
        return

    elkhorn = ArenaNode(
        name="Elkhorn Creek Arena",
        field_id=field.id,
        lat=40.74608,
        lon=-105.54033,
        kind="trailhead",
        radius_m=120,
        notes="Central Boy Scout Road gathering node. Sphere origin = trailhead GPS.",
    )
    creed = ArenaNode(
        name="Creedmore / Sky Prairie Arena",
        field_id=field.id,
        lat=40.84988,
        lon=-105.54071,
        kind="crag",
        radius_m=150,
        notes="Northern batholith arena for Sky Prairie / Top Notch cluster.",
    )
    village = ArenaNode(
        name="Red Feather Village Arena",
        field_id=field.id,
        lat=40.80154,
        lon=-105.59009,
        kind="parking",
        radius_m=90,
        notes="Town centroid arena — services + field overview, not a crag itself.",
    )
    db.add_all([elkhorn, creed, village])
    db.commit()
    db.refresh(elkhorn)
    db.refresh(creed)

    s1 = RegionSphere(
        arena_id=elkhorn.id,
        name="Elkhorn 360",
        pano_path="data/spheres/elkhorn/equirect.jpg",
        north_offset_deg=0.0,
    )
    s2 = RegionSphere(
        arena_id=creed.id,
        name="Creedmore 360",
        pano_path="data/spheres/creedmore/equirect.jpg",
        north_offset_deg=0.0,
    )
    db.add_all([s1, s2])
    db.commit()
    db.refresh(s1)
    db.refresh(s2)

    nodes = db.query(BoulderNode).filter(BoulderNode.field_id == field.id).all()
    for n in nodes:
        if n.subarea and "Boy Scout" in (n.subarea or ""):
            yaw = yaw_from_gps(elkhorn.lat, elkhorn.lon, n.lat, n.lon)
            db.add(
                SphereHotspot(
                    sphere_id=s1.id,
                    node_id=n.id,
                    name=n.name,
                    yaw_deg=yaw,
                    pitch_deg=4.0,
                    lat=n.lat,
                    lon=n.lon,
                    notes=n.notes,
                )
            )
        if n.subarea and "Creedmore" in (n.subarea or ""):
            yaw = yaw_from_gps(creed.lat, creed.lon, n.lat, n.lon)
            db.add(
                SphereHotspot(
                    sphere_id=s2.id,
                    node_id=n.id,
                    name=n.name,
                    yaw_deg=yaw,
                    pitch_deg=3.0,
                    lat=n.lat,
                    lon=n.lon,
                    notes=n.notes,
                )
            )
    db.commit()
