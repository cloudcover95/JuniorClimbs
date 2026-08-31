"""Seed public Red Feather Lakes StoneField + named subarea nodes.

Coordinates are widely published public area centroids (Mountain Project / climbing guides).
No guidebook text, topos, or copyrighted beta is copied.
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from backend.models_stonefield import StoneField, BoulderNode

RFL_LAT = 40.80154
RFL_LON = -105.59009

SUBAREAS = [
    # name, subarea, lat, lon — public area pins
    ("Creedmore Lakes Road", "Creedmore Lakes Road", 40.84988, -105.54071),
    ("Sky Prairie / Top Notch", "Creedmore Lakes Road", 40.84988, -105.54071),
    ("Boy Scout Road Areas", "Boy Scout Road", 40.74608, -105.54033),
    ("Swallow Crags", "Boy Scout Road", 40.74608, -105.54033),
    ("Elkhorn Creek Trailhead", "Boy Scout Road", 40.74608, -105.54033),
]


def ensure_red_feather_seed(db: Session) -> StoneField:
    field = db.query(StoneField).filter(StoneField.name == "Red Feather Lakes").first()
    if field is None:
        field = StoneField(
            name="Red Feather Lakes",
            region="Colorado — Larimer County",
            lat=RFL_LAT,
            lon=RFL_LON,
            elevation_ft=8334,
            notes=(
                "Granite domes and boulders across ~90 sq mi north of Poudre Canyon. "
                "Public area centroid. Users submit their own nodes, photos, and beta."
            ),
            access_notes=(
                "Mix of public forest and private land. Respect gates, 5-car max pullouts, "
                "and posted closures. Confirm current access before approaching."
            ),
        )
        db.add(field)
        db.commit()
        db.refresh(field)

    existing = {n.name for n in db.query(BoulderNode).filter(BoulderNode.field_id == field.id).all()}
    for name, sub, lat, lon in SUBAREAS:
        if name in existing:
            continue
        db.add(
            BoulderNode(
                field_id=field.id,
                name=name,
                lat=lat,
                lon=lon,
                subarea=sub,
                rock_type="granite",
                notes="Public subarea pin. Add problems / topos via submit endpoints.",
                submitted_by="juniorstonefield-seed",
            )
        )
    db.commit()
    return field
