"""JuniorStoneField + JuniorBetaBoard FastAPI router."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import SessionLocal
from backend.models_stonefield import (
    StoneField,
    BoulderNode,
    ClimbProblem,
    TopoMesh,
    RouteSetLedger,
    BetaPost,
    BetaReply,
)
from backend.schemas.stonefield import (
    StoneFieldIn,
    StoneFieldOut,
    BoulderNodeIn,
    BoulderNodeOut,
    ProblemIn,
    ProblemOut,
    TopoIn,
    TopoOut,
    RouteSetIn,
    RouteSetOut,
    BetaPostIn,
    BetaPostOut,
    BetaReplyIn,
    BetaReplyOut,
)
from backend.seed_red_feather import ensure_red_feather_seed

router = APIRouter(prefix="/stonefield", tags=["JuniorStoneField"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/fields", response_model=list[StoneFieldOut])
def list_fields(db: Session = Depends(get_db)):
    ensure_red_feather_seed(db)
    return db.query(StoneField).all()


@router.post("/fields", response_model=StoneFieldOut)
def create_field(payload: StoneFieldIn, db: Session = Depends(get_db)):
    row = StoneField(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.get("/nodes", response_model=list[BoulderNodeOut])
def list_nodes(field_id: int | None = None, db: Session = Depends(get_db)):
    q = db.query(BoulderNode)
    if field_id is not None:
        q = q.filter(BoulderNode.field_id == field_id)
    return q.all()


@router.post("/nodes", response_model=BoulderNodeOut)
def submit_node(payload: BoulderNodeIn, db: Session = Depends(get_db)):
    if not db.get(StoneField, payload.field_id):
        raise HTTPException(404, "StoneField not found")
    row = BoulderNode(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.get("/problems", response_model=list[ProblemOut])
def list_problems(node_id: int | None = None, db: Session = Depends(get_db)):
    q = db.query(ClimbProblem)
    if node_id is not None:
        q = q.filter(ClimbProblem.node_id == node_id)
    return q.all()


@router.post("/problems", response_model=ProblemOut)
def submit_problem(payload: ProblemIn, db: Session = Depends(get_db)):
    if not db.get(BoulderNode, payload.node_id):
        raise HTTPException(404, "BoulderNode not found")
    row = ClimbProblem(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.get("/topos", response_model=list[TopoOut])
def list_topos(node_id: int | None = None, problem_id: int | None = None, db: Session = Depends(get_db)):
    q = db.query(TopoMesh)
    if node_id is not None:
        q = q.filter(TopoMesh.node_id == node_id)
    if problem_id is not None:
        q = q.filter(TopoMesh.problem_id == problem_id)
    return q.all()


@router.post("/topos", response_model=TopoOut)
def submit_topo(payload: TopoIn, db: Session = Depends(get_db)):
    row = TopoMesh(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.get("/routesets", response_model=list[RouteSetOut])
def list_routesets(venue: str | None = None, db: Session = Depends(get_db)):
    q = db.query(RouteSetLedger)
    if venue:
        q = q.filter(RouteSetLedger.venue == venue)
    return q.all()


@router.post("/routesets", response_model=RouteSetOut)
def submit_routeset(payload: RouteSetIn, db: Session = Depends(get_db)):
    row = RouteSetLedger(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.get("/board", response_model=list[BetaPostOut])
def list_board(
    field_id: int | None = None,
    node_id: int | None = None,
    problem_id: int | None = None,
    db: Session = Depends(get_db),
):
    q = db.query(BetaPost)
    if field_id is not None:
        q = q.filter(BetaPost.field_id == field_id)
    if node_id is not None:
        q = q.filter(BetaPost.node_id == node_id)
    if problem_id is not None:
        q = q.filter(BetaPost.problem_id == problem_id)
    return q.order_by(BetaPost.created_at.desc()).all()


@router.post("/board", response_model=BetaPostOut)
def post_beta(payload: BetaPostIn, db: Session = Depends(get_db)):
    row = BetaPost(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.post("/board/reply", response_model=BetaReplyOut)
def reply_beta(payload: BetaReplyIn, db: Session = Depends(get_db)):
    if not db.get(BetaPost, payload.post_id):
        raise HTTPException(404, "Beta post not found")
    row = BetaReply(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.get("/red-feather")
def red_feather_overview(db: Session = Depends(get_db)):
    field = ensure_red_feather_seed(db)
    nodes = db.query(BoulderNode).filter(BoulderNode.field_id == field.id).all()
    return {
        "field": {
            "id": field.id,
            "name": field.name,
            "gps": [field.lat, field.lon],
            "elevation_ft": field.elevation_ft,
            "notes": field.notes,
            "access_notes": field.access_notes,
        },
        "nodes": [
            {"id": n.id, "name": n.name, "subarea": n.subarea, "gps": [n.lat, n.lon]}
            for n in nodes
        ],
        "capabilities_mirrored": [
            "GPS area + subarea tree",
            "user-submitted boulder nodes",
            "named problems + grades",
            "local topo / photo mesh",
            "gym + outdoor route-set ledger",
            "JuniorBetaBoard discussion",
        ],
        "source_inspiration": "public Red Feather Lakes area facts; local-first JuniorCloud implementation",
    }
