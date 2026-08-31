"""Seed offline tile pack + land + overland nodes for Red Feather Lakes region."""
from __future__ import annotations

from sqlalchemy.orm import Session

from backend.models_navmesh import TilePack, LandLayer, OverlandNode, Waypoint


def ensure_navmesh_seed(db: Session) -> None:
    if db.query(TilePack).count() == 0:
        db.add(
            TilePack(
                name="RFL Topo Pack (local)",
                kind="topo",
                path="data/tiles/rfl-topo",
                min_zoom=10,
                max_zoom=15,
                south=40.70,
                west=-105.75,
                north=40.92,
                east=-105.40,
                notes="Drop USGS/OSM MBTiles or XYZ here. App never fetches vendors.",
                offline_ready=True,
            )
        )
        db.add(
            TilePack(
                name="RFL OSM Pack (local)",
                kind="osm",
                path="data/tiles/rfl-osm",
                min_zoom=8,
                max_zoom=15,
                south=40.70,
                west=-105.75,
                north=40.92,
                east=-105.40,
                notes="Offline street/forest road basemap you load yourself.",
                offline_ready=True,
            )
        )

    if db.query(LandLayer).count() == 0:
        db.add_all(
            [
                LandLayer(
                    name="Roosevelt NF — Red Feather vicinity",
                    tenure="usfs",
                    south=40.70,
                    west=-105.75,
                    north=40.92,
                    east=-105.40,
                    access="open",
                    notes="Approximate NF envelope. Confirm district rules + fire restrictions locally.",
                ),
                LandLayer(
                    name="Private inholdings / ranch mosaic",
                    tenure="private",
                    south=40.73,
                    west=-105.58,
                    north=40.78,
                    east=-105.50,
                    access="private",
                    notes="Boy Scout ranch and other private parcels exist. Do not treat bbox as a survey.",
                ),
            ]
        )

    if db.query(OverlandNode).count() == 0:
        db.add_all(
            [
                OverlandNode(
                    name="Elkhorn Creek Trailhead",
                    kind="trailhead",
                    lat=40.74608,
                    lon=-105.54033,
                    notes="Primary Boy Scout Road access. Overflow if 5-car pullout is full.",
                    conditions="Respect gate. Do not block private drive.",
                    submitted_by="juniornavmesh-seed",
                ),
                OverlandNode(
                    name="Swallow / Temple pullout (5-car max)",
                    kind="parking",
                    lat=40.74608,
                    lon=-105.54033,
                    notes="Small pullout east of trailhead. 5-car max.",
                    submitted_by="juniornavmesh-seed",
                ),
                OverlandNode(
                    name="Red Feather Lakes village",
                    kind="wifi",
                    lat=40.80154,
                    lon=-105.59009,
                    notes="Resupply / last reliable services before dispersing.",
                    submitted_by="juniornavmesh-seed",
                ),
                OverlandNode(
                    name="West Lake area (USFS camping vicinity)",
                    kind="camp",
                    lat=40.79,
                    lon=-105.57,
                    notes="Seasonal USFS camping exists in the lakes basin. Dates and fees change — verify locally.",
                    submitted_by="juniornavmesh-seed",
                ),
            ]
        )

    if db.query(Waypoint).filter(Waypoint.name == "RFL centroid").first() is None:
        db.add(
            Waypoint(
                name="RFL centroid",
                lat=40.80154,
                lon=-105.59009,
                elev_ft=8334,
                kind="field",
                notes="Public area centroid for Red Feather Lakes field.",
            )
        )
    db.commit()
