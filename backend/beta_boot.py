"""Assemble a live-beta health snapshot. Import all models then seed."""
from __future__ import annotations

from sqlalchemy.orm import Session

from backend.models_stonefield import StoneField, BoulderNode, RouteSetLedger
from backend.models_navmesh import TilePack, GpsFix
from backend.models_forum import CrowdEvent
from backend.models_sphere import ArenaNode, RegionSphere
from backend.models_source import SourceProject
from backend.models_programs import GymProgram, AccessPledge
from backend.seed_red_feather import ensure_red_feather_seed
from backend.seed_navmesh import ensure_navmesh_seed
from backend.seed_sphere import ensure_sphere_seed
from backend.seed_front_range import ensure_front_range_seed
from backend.seed_gym import ensure_gym_seed
from backend.stonefield_covenant import TERMS_VERSION
from backend.bitnet_field_core import field_core


def seed_all(db: Session) -> None:
    ensure_red_feather_seed(db)
    ensure_navmesh_seed(db)
    ensure_sphere_seed(db)
    ensure_front_range_seed(db)
    ensure_gym_seed(db)


def health(db: Session) -> dict:
    seed_all(db)
    probe = field_core.score("dry granite, USFS open, V3")
    return {
        "product": "JuniorStoneField",
        "status": "beta",
        "offline": True,
        "covenant": TERMS_VERSION,
        "fields": db.query(StoneField).count(),
        "nodes": db.query(BoulderNode).count(),
        "arenas": db.query(ArenaNode).count(),
        "spheres": db.query(RegionSphere).count(),
        "tile_packs": db.query(TilePack).count(),
        "programs": db.query(GymProgram).count(),
        "routesets": db.query(RouteSetLedger).count(),
        "forum_events": db.query(CrowdEvent).count(),
        "source_projects": db.query(SourceProject).count(),
        "pledges": db.query(AccessPledge).count(),
        "gps_fixes": db.query(GpsFix).count(),
        "field_names": [r.name for r in db.query(StoneField).all()],
        "bitnet_field": {"backend": probe.backend, "condition": probe.condition},
        "hub": "/stonefield/app",
        "terms": "/stonefield/terms",
    }
