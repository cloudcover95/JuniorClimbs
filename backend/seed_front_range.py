"""Seed Boulder + Golden + Mt. Xanadu StoneFields from public centroids.

Names + GPS only. No guidebook text, topos, or problem beta copied.
Mt. Xanadu boulders sit north of the Swoosh / RFL batholith (Larimer),
not inside the City of Golden — seeded as their own field so they are findable.
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from backend.models_stonefield import StoneField, BoulderNode
from backend.models_sphere import ArenaNode, RegionSphere, SphereHotspot
from backend.sphere_engine import yaw_from_gps

# Public published area pins (MP area pages, 27crags, Wikipedia, municipal parks).
FLAGSTAFF_NODES = [
    # name, subarea, lat, lon
    ("Hobo Cave / Lower Mountain", "Lower Flagstaff", 39.99933, -105.29088),
    ("Cloud Shadow / Capstan / Dark Side", "Capstan",
     40.00270, -105.29564),
    ("Amphitheater / Red Wall", "Crown / Monkey", 40.00179, -105.29708),
    ("Monkey Traverse Area", "Crown / Monkey", 40.00179, -105.29708),
    ("Crown Rock", "Crown / Monkey", 40.0018, -105.2965),
    ("Pratt's Rock", "Crown / Monkey", 40.0016, -105.2968),
    ("Beer Barrel", "Crown / Monkey", 40.0015, -105.2969),
    ("Great Ridge", "First Overhang cluster", 40.00323, -105.29856),
    ("First Overhang", "First Overhang cluster", 40.00323, -105.29856),
    ("Upper Y", "First Overhang cluster", 40.0034, -105.2988),
    ("Pumpkin Rock", "Lower Flagstaff", 39.9998, -105.2915),
    ("Cookie Jar Rock", "Lower Flagstaff", 39.9996, -105.2912),
]

GOLDEN_NODES = [
    ("North Table Mountain / Golden Cliffs", "North Table", 39.7828, -105.2050),
    ("Golden Cliffs south benches", "North Table", 39.7795, -105.2075),
    ("Clear Creek Canyon — Tunnel 6 vicinity", "Clear Creek", 39.7430, -105.2900),
    ("Clear Creek Canyon — High Wire vicinity", "Clear Creek", 39.7425, -105.2980),
    ("Lookout Mountain Road crags", "Lookout", 39.7325, -105.2380),
    ("Mount Galbraith vicinity", "Galbraith", 39.7700, -105.2480),
    ("Golden Gate Canyon SP — field pin", "GGC", 39.8310, -105.4100),
]

XANADU_NODES = [
    ("Mt. Xanadu — main cluster", "Xanadu", 40.86577, -105.52388),
    ("Battleship Boulder", "Xanadu", 40.8659, -105.5241),
    ("The Nub Boulder", "Xanadu", 40.8656, -105.5236),
    ("Northern Swoosh approach (Wanton Whim bearing)", "Swoosh approach", 40.8620, -105.5280),
]


def _ensure_field(db: Session, name: str, region: str, lat: float, lon: float,
                  elev: int, notes: str, access: str) -> StoneField:
    field = db.query(StoneField).filter(StoneField.name == name).first()
    if field is None:
        field = StoneField(
            name=name,
            region=region,
            lat=lat,
            lon=lon,
            elevation_ft=elev,
            notes=notes,
            access_notes=access,
        )
        db.add(field)
        db.commit()
        db.refresh(field)
    return field


def _ensure_nodes(db: Session, field: StoneField, rows: list, rock: str) -> None:
    existing = {n.name for n in db.query(BoulderNode).filter(BoulderNode.field_id == field.id).all()}
    for name, sub, lat, lon in rows:
        if name in existing:
            continue
        db.add(
            BoulderNode(
                field_id=field.id,
                name=name,
                lat=lat,
                lon=lon,
                subarea=sub,
                rock_type=rock,
                notes="Public subarea pin. Problems + topos come from JuniorSourceLedger / ForumMesh.",
                submitted_by="junior-front-range-seed",
            )
        )
    db.commit()


def _ensure_arena(db: Session, field: StoneField, name: str, lat: float, lon: float,
                  kind: str, nodes_for_sphere: list[BoulderNode] | None = None) -> None:
    if db.query(ArenaNode).filter(ArenaNode.name == name).first():
        return
    arena = ArenaNode(
        name=name,
        field_id=field.id,
        lat=lat,
        lon=lon,
        kind=kind,
        radius_m=120,
        notes="Central viewing arena for this field.",
    )
    db.add(arena)
    db.commit()
    db.refresh(arena)
    slug = name.lower().replace(" ", "-")[:24]
    sph = RegionSphere(
        arena_id=arena.id,
        name=f"{name} 360",
        pano_path=f"data/spheres/{slug}/equirect.jpg",
        north_offset_deg=0.0,
    )
    db.add(sph)
    db.commit()
    db.refresh(sph)
    if not nodes_for_sphere:
        nodes_for_sphere = db.query(BoulderNode).filter(BoulderNode.field_id == field.id).all()
    for n in nodes_for_sphere:
        db.add(
            SphereHotspot(
                sphere_id=sph.id,
                node_id=n.id,
                name=n.name,
                yaw_deg=yaw_from_gps(arena.lat, arena.lon, n.lat, n.lon),
                pitch_deg=3.0,
                lat=n.lat,
                lon=n.lon,
                notes=n.notes,
            )
        )
    db.commit()


def ensure_front_range_seed(db: Session) -> dict[str, StoneField]:
    flag = _ensure_field(
        db,
        "Flagstaff Mountain",
        "Colorado — Boulder",
        40.0014,
        -105.2960,
        6983,
        "City of Boulder OSMP sandstone boulders along Flagstaff Road. Public area centroid.",
        "Paid / resident parking. OSMP rules. Sensitive access — read current signage. No glue.",
    )
    _ensure_nodes(db, flag, FLAGSTAFF_NODES, "sandstone")

    golden = _ensure_field(
        db,
        "Golden Front Range",
        "Colorado — Golden / Jefferson County",
        39.7525,
        -105.2260,
        5713,
        "North Table / Golden Cliffs, Clear Creek, Lookout, Galbraith, Golden Gate field pins.",
        "Mix of Jeffco Open Space, CDOT canyon pullouts, and state park. Confirm seasonal raptor closures.",
    )
    _ensure_nodes(db, golden, GOLDEN_NODES, "basalt")

    xan = _ensure_field(
        db,
        "Mt. Xanadu",
        "Colorado — Larimer / Red Feather batholith",
        40.86577,
        -105.52388,
        8039,
        "Granite boulders north of Northern Swoosh (Battleship, Nub). Public area centroid.",
        "Same RFL land mosaic. Approach from Swoosh / Wanton Whim bearing. Respect gates.",
    )
    _ensure_nodes(db, xan, XANADU_NODES, "granite")

    _ensure_arena(db, flag, "Flagstaff Crown Arena", 40.00179, -105.29708, "crag")
    _ensure_arena(db, golden, "North Table Arena", 39.7828, -105.2050, "crag")
    _ensure_arena(db, xan, "Xanadu Arena", 40.86577, -105.52388, "crag")
    return {"flagstaff": flag, "golden": golden, "xanadu": xan}
