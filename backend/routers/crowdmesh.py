"""JuniorCrowdMesh — offline decentralized forum + FieldBitNet scoring."""
from __future__ import annotations

import hashlib
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database import SessionLocal
from backend.models_crowdmesh import CrowdEnvelope
from backend.services.field_bitnet import field_bitnet

router = APIRouter(prefix="/crowd", tags=["JuniorCrowdMesh"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def envelope_hash(author: str, title: str, body: str, created: str) -> str:
    raw = f"{author}|{title}|{body}|{created}".encode("utf-8", errors="replace")
    return hashlib.sha256(raw).hexdigest()[:32]


class EnvelopeIn(BaseModel):
    author: str = "anon"
    topic: str = "general"
    title: str = ""
    body: str
    lat: float | None = None
    lon: float | None = None
    field_id: int | None = None
    node_id: int | None = None
    origin_device: str = "local"
    score_now: bool = True


class InferIn(BaseModel):
    text: str
    lat: float | None = None
    lon: float | None = None


class BundleIn(BaseModel):
    envelopes: list[dict[str, Any]]


def _to_dict(row: CrowdEnvelope) -> dict[str, Any]:
    return {
        "envelope_id": row.envelope_id,
        "author": row.author,
        "topic": row.topic,
        "title": row.title,
        "body": row.body,
        "lat": row.lat,
        "lon": row.lon,
        "field_id": row.field_id,
        "node_id": row.node_id,
        "origin_device": row.origin_device,
        "bitnet_label": row.bitnet_label,
        "bitnet_score": row.bitnet_score,
        "created_at": row.created_at.isoformat() if row.created_at else None,
    }


@router.get("/envelopes")
def list_envelopes(topic: str | None = None, db: Session = Depends(get_db)):
    q = db.query(CrowdEnvelope).order_by(CrowdEnvelope.id.desc())
    if topic:
        q = q.filter(CrowdEnvelope.topic == topic)
    return [_to_dict(r) for r in q.all()]


@router.post("/envelopes")
def post_envelope(payload: EnvelopeIn, db: Session = Depends(get_db)):
    now = datetime.utcnow()
    eid = envelope_hash(payload.author, payload.title, payload.body, now.isoformat())
    existing = db.query(CrowdEnvelope).filter(CrowdEnvelope.envelope_id == eid).first()
    if existing:
        return {"status": "duplicate", "envelope": _to_dict(existing)}

    row = CrowdEnvelope(
        envelope_id=eid,
        author=payload.author,
        topic=payload.topic,
        title=payload.title,
        body=payload.body,
        lat=payload.lat,
        lon=payload.lon,
        field_id=payload.field_id,
        node_id=payload.node_id,
        origin_device=payload.origin_device,
        created_at=now,
    )
    if payload.score_now:
        inf = field_bitnet.infer(f"{payload.title}\n{payload.body}", payload.lat, payload.lon)
        row.bitnet_label = inf.label
        row.bitnet_score = inf.score
    db.add(row)
    db.commit()
    db.refresh(row)
    return {"status": "stored", "offline": True, "envelope": _to_dict(row)}


@router.get("/envelopes/{envelope_id}")
def get_envelope(envelope_id: str, db: Session = Depends(get_db)):
    row = db.query(CrowdEnvelope).filter(CrowdEnvelope.envelope_id == envelope_id).first()
    if not row:
        raise HTTPException(404, "Envelope not found")
    return _to_dict(row)


@router.get("/bundle")
def export_bundle(topic: str | None = None, db: Session = Depends(get_db)):
    q = db.query(CrowdEnvelope)
    if topic:
        q = q.filter(CrowdEnvelope.topic == topic)
    items = [_to_dict(r) for r in q.all()]
    return {
        "format": "junior-crowdmesh-bundle-v1",
        "count": len(items),
        "offline": True,
        "envelopes": items,
    }


@router.post("/bundle")
def import_bundle(payload: BundleIn, db: Session = Depends(get_db)):
    added = 0
    skipped = 0
    for item in payload.envelopes:
        eid = item.get("envelope_id")
        body = item.get("body") or ""
        author = item.get("author") or "anon"
        title = item.get("title") or ""
        created = item.get("created_at") or datetime.utcnow().isoformat()
        if not eid:
            eid = envelope_hash(author, title, body, created)
        if db.query(CrowdEnvelope).filter(CrowdEnvelope.envelope_id == eid).first():
            skipped += 1
            continue
        row = CrowdEnvelope(
            envelope_id=eid,
            author=author,
            topic=item.get("topic") or "general",
            title=title,
            body=body,
            lat=item.get("lat"),
            lon=item.get("lon"),
            field_id=item.get("field_id"),
            node_id=item.get("node_id"),
            origin_device=item.get("origin_device") or "peer",
            bitnet_label=item.get("bitnet_label"),
            bitnet_score=item.get("bitnet_score"),
        )
        db.add(row)
        added += 1
    db.commit()
    return {"merged": added, "duplicates": skipped, "offline": True}


@router.post("/score/{envelope_id}")
def score_envelope(envelope_id: str, db: Session = Depends(get_db)):
    row = db.query(CrowdEnvelope).filter(CrowdEnvelope.envelope_id == envelope_id).first()
    if not row:
        raise HTTPException(404, "Envelope not found")
    inf = field_bitnet.infer(f"{row.title}\n{row.body}", row.lat, row.lon)
    row.bitnet_label = inf.label
    row.bitnet_score = inf.score
    db.commit()
    return {
        "envelope_id": envelope_id,
        "inference": {
            "label": inf.label,
            "score": inf.score,
            "scores": inf.scores,
            "backend": inf.backend,
            "notes": inf.notes,
        },
    }
