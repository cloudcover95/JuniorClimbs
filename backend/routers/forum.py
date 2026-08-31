"""JuniorForumMesh + BitNetFieldCore routes."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database import SessionLocal
from backend.models_forum import CrowdEvent
from backend.forum_mesh import publish, export_bundle, import_bundle
from backend.bitnet_field_core import field_core

router = APIRouter(tags=["JuniorForumMesh"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class EventIn(BaseModel):
    kind: str = "beta"
    body: str
    author: str = "anon"
    origin_node: str = "local"
    title: str = ""
    field_id: int | None = None
    node_id: int | None = None
    problem_id: int | None = None
    overland_id: int | None = None
    lat: float | None = None
    lon: float | None = None


class ScoreIn(BaseModel):
    text: str


class BundleIn(BaseModel):
    format: str | None = None
    events: list[dict]


@router.get("/forum/events")
def list_events(
    kind: str | None = None,
    node_id: int | None = None,
    field_id: int | None = None,
    db: Session = Depends(get_db),
):
    q = db.query(CrowdEvent)
    if kind:
        q = q.filter(CrowdEvent.kind == kind)
    if node_id is not None:
        q = q.filter(CrowdEvent.node_id == node_id)
    if field_id is not None:
        q = q.filter(CrowdEvent.field_id == field_id)
    rows = q.order_by(CrowdEvent.id.desc()).limit(200).all()
    return rows


@router.post("/forum/events")
def post_event(payload: EventIn, db: Session = Depends(get_db)):
    row = publish(db, **payload.model_dump())
    return {
        "event_id": row.event_id,
        "trust": row.trust,
        "disagreement": row.disagreement,
        "recommendation": row.recommendation,
        "condition": row.condition,
        "access": row.access,
        "kind": row.kind,
    }


@router.get("/forum/thread")
def thread(node_id: int | None = None, kind: str | None = None, db: Session = Depends(get_db)):
    q = db.query(CrowdEvent)
    if node_id is not None:
        q = q.filter(CrowdEvent.node_id == node_id)
    if kind:
        q = q.filter(CrowdEvent.kind == kind)
    rows = q.order_by(CrowdEvent.created_at.asc()).all()
    return {
        "count": len(rows),
        "mean_trust": round(sum(r.trust for r in rows) / len(rows), 3) if rows else None,
        "events": rows,
    }


@router.get("/forum/bundle/export")
def bundle_export(db: Session = Depends(get_db)):
    return export_bundle(db)


@router.post("/forum/bundle/import")
def bundle_import(payload: BundleIn, db: Session = Depends(get_db)):
    return import_bundle(db, payload.model_dump())


@router.post("/forum/score")
def score_text(payload: ScoreIn):
    return field_core.score(payload.text).to_dict()


@router.get("/bitnet-field/status")
def bitnet_field_status():
    probe = field_core.score("dry granite, USFS open, V4 crimp line")
    return {
        "core": "JuniorBitNetFieldCore",
        "backend": field_core.backend,
        "offline": True,
        "probe": probe.to_dict(),
        "discipline": ["JuniorStoneField", "JuniorNavMesh", "JuniorForumMesh"],
    }
