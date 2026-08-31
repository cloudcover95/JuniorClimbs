"""JuniorStoneField product hub, terms, gym programs."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database import SessionLocal
from backend.models_programs import AccessPledge, GymProgram, ClassBlock, StudyPlan
from backend.models_stonefield import StoneField, BoulderNode, RouteSetLedger
from backend.stonefield_covenant import TERMS_TEXT, TERMS_VERSION, outdoor_publish_allowed

router = APIRouter(prefix="/stonefield", tags=["JuniorStoneField"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class NodeSubmit(BaseModel):
    field_id: int
    name: str
    lat: float
    lon: float
    subarea: str | None = None
    rock_type: str = "granite"
    notes: str | None = None
    submitted_by: str = "anon"
    tenure: str = "unknown"
    owner_consent: bool = False
    consent_by: str = ""
    visibility: str = "public"
    accept_terms: bool = False


class ProgramIn(BaseModel):
    name: str
    kind: str = "camp"
    season: str = ""
    visibility: str = "gym_internal"
    notes: str | None = None


class ClassIn(BaseModel):
    program_id: int
    title: str
    day: str = ""
    start_time: str = ""
    wall: str = ""
    coach: str = ""
    notes: str | None = None


class StudyIn(BaseModel):
    name: str
    program_id: int | None = None
    problem_ids: list[int] = []
    routeset_ids: list[int] = []
    field_id: int | None = None
    notes: str | None = None


@router.get("/terms", response_class=PlainTextResponse)
def terms():
    return TERMS_TEXT


@router.get("/terms.json")
def terms_json():
    return {"version": TERMS_VERSION, "text": TERMS_TEXT}


@router.post("/nodes/submit")
def submit_node_gated(payload: NodeSubmit, db: Session = Depends(get_db)):
    if not payload.accept_terms:
        raise HTTPException(400, "Must accept JuniorStoneField Access Covenant (/stonefield/terms)")
    if not db.get(StoneField, payload.field_id):
        raise HTTPException(404, "StoneField not found")
    ok, reason = outdoor_publish_allowed(payload.tenure, payload.owner_consent, payload.visibility)
    if not ok:
        raise HTTPException(
            403,
            {
                "error": reason,
                "covenant": TERMS_VERSION,
                "need": "owner_consent=true and consent_by=landowner or authorized speaker, or set visibility=private",
            },
        )
    row = BoulderNode(
        field_id=payload.field_id,
        name=payload.name,
        lat=payload.lat,
        lon=payload.lon,
        subarea=payload.subarea,
        rock_type=payload.rock_type,
        notes=payload.notes,
        submitted_by=payload.submitted_by,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    pledge = AccessPledge(
        subject_kind="node",
        subject_id=row.id,
        tenure=payload.tenure,
        owner_consent=payload.owner_consent,
        consent_by=payload.consent_by,
        visibility=payload.visibility,
        attester=payload.submitted_by,
        accepted_terms=TERMS_VERSION,
    )
    db.add(pledge)
    db.commit()
    return {"node_id": row.id, "visibility": payload.visibility, "tenure": payload.tenure, "pledge_id": pledge.id}


@router.get("/programs")
def list_programs(db: Session = Depends(get_db)):
    return db.query(GymProgram).all()


@router.post("/programs")
def create_program(payload: ProgramIn, db: Session = Depends(get_db)):
    row = GymProgram(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.get("/classes")
def list_classes(program_id: int | None = None, db: Session = Depends(get_db)):
    q = db.query(ClassBlock)
    if program_id is not None:
        q = q.filter(ClassBlock.program_id == program_id)
    return q.all()


@router.post("/classes")
def create_class(payload: ClassIn, db: Session = Depends(get_db)):
    if not db.get(GymProgram, payload.program_id):
        raise HTTPException(404, "Program not found")
    row = ClassBlock(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.get("/study-plans")
def list_plans(db: Session = Depends(get_db)):
    return db.query(StudyPlan).all()


@router.post("/study-plans")
def create_plan(payload: StudyIn, db: Session = Depends(get_db)):
    row = StudyPlan(
        name=payload.name,
        program_id=payload.program_id,
        problem_ids=",".join(str(i) for i in payload.problem_ids),
        routeset_ids=",".join(str(i) for i in payload.routeset_ids),
        field_id=payload.field_id,
        notes=payload.notes,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.get("/app", response_class=HTMLResponse)
def app_hub(db: Session = Depends(get_db)):
    fields = db.query(StoneField).count()
    nodes = db.query(BoulderNode).count()
    sets = db.query(RouteSetLedger).count()
    programs = db.query(GymProgram).count()
    return f"""<!doctype html><html><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>JuniorStoneField</title>
<style>
body{{margin:0;font-family:ui-sans-serif,system-ui;background:#0b0f14;color:#e8eef6}}
main{{max-width:720px;margin:0 auto;padding:28px 18px}}
h1{{font-size:28px;margin:0 0 8px}}
a{{color:#7ee0b1}}
.card{{background:#121820;border-radius:12px;padding:16px;margin:12px 0}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:10px}}
</style></head><body><main>
<h1>JuniorStoneField</h1>
<p>Outdoor fields + gym programs inside JuniorClimbs. Offline-first. No vendor guidebook scrape.</p>
<div class="grid">
<div class="card">Fields {fields}</div>
<div class="card">Nodes {nodes}</div>
<div class="card">Gym sets {sets}</div>
<div class="card">Programs {programs}</div>
</div>
<div class="card">
<strong>Covenant.</strong> Private-land boulders are not published without the owner's word of consent.
<a href="/stonefield/terms">Read terms</a>
</div>
<div class="card">
<a href="/stonefield/fields">Fields</a> ·
<a href="/arena">Arenas</a> ·
<a href="/sphere/view/1">360</a> ·
<a href="/stonefield/programs">Programs</a> ·
<a href="/source/schema">Source packs</a> ·
<a href="/nav/status">Nav</a>
</div>
</main></body></html>"""
