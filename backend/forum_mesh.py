"""JuniorForumMesh — offline crowd ledger + gossip import/export."""
from __future__ import annotations

import hashlib
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from backend.models_forum import CrowdEvent
from backend.bitnet_field_core import field_core

DATA_DIR = Path(os.getenv("JUNIOR_FORUM_DIR", "data/forum"))


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def make_event_id(author: str, body: str, created_iso: str) -> str:
    raw = f"{author}|{body}|{created_iso}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:32]


def _append_jsonl(event: dict[str, Any]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with (DATA_DIR / "events.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event, default=str) + "\n")


def publish(
    db: Session,
    *,
    kind: str,
    body: str,
    author: str = "anon",
    origin_node: str = "local",
    title: str = "",
    field_id: int | None = None,
    node_id: int | None = None,
    problem_id: int | None = None,
    overland_id: int | None = None,
    lat: float | None = None,
    lon: float | None = None,
    event_id: str | None = None,
    created_at: datetime | None = None,
) -> CrowdEvent:
    created = created_at or _now()
    eid = event_id or make_event_id(author, body, created.isoformat())
    existing = db.query(CrowdEvent).filter(CrowdEvent.event_id == eid).first()
    if existing:
        return existing

    prior = None
    if node_id is not None:
        last = (
            db.query(CrowdEvent)
            .filter(CrowdEvent.node_id == node_id, CrowdEvent.kind == kind)
            .order_by(CrowdEvent.id.desc())
            .first()
        )
        if last and last.embed_csv:
            prior = [int(x) for x in last.embed_csv.split(",") if x.strip()]

    score = field_core.score(f"{title} {body}", prior_embed=prior)
    row = CrowdEvent(
        event_id=eid,
        kind=kind,
        author=author,
        origin_node=origin_node,
        field_id=field_id,
        node_id=node_id,
        problem_id=problem_id,
        overland_id=overland_id,
        title=title,
        body=body,
        lat=lat,
        lon=lon,
        trust=score.trust,
        disagreement=score.disagreement,
        recommendation=score.recommendation,
        condition=score.condition,
        access=score.access,
        embed_csv=",".join(str(x) for x in score.embed),
        created_at=created,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    _append_jsonl(
        {
            "event_id": row.event_id,
            "kind": row.kind,
            "author": row.author,
            "origin_node": row.origin_node,
            "title": row.title,
            "body": row.body,
            "field_id": row.field_id,
            "node_id": row.node_id,
            "problem_id": row.problem_id,
            "overland_id": row.overland_id,
            "lat": row.lat,
            "lon": row.lon,
            "trust": row.trust,
            "created_at": row.created_at.isoformat() if row.created_at else None,
        }
    )
    return row


def export_bundle(db: Session, limit: int = 500) -> dict[str, Any]:
    rows = db.query(CrowdEvent).order_by(CrowdEvent.id.desc()).limit(limit).all()
    events = []
    for r in reversed(rows):
        events.append(
            {
                "event_id": r.event_id,
                "kind": r.kind,
                "author": r.author,
                "origin_node": r.origin_node,
                "title": r.title,
                "body": r.body,
                "field_id": r.field_id,
                "node_id": r.node_id,
                "problem_id": r.problem_id,
                "overland_id": r.overland_id,
                "lat": r.lat,
                "lon": r.lon,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
        )
    bundle = {
        "format": "junior-gossip-v1",
        "bundle_id": uuid.uuid4().hex[:16],
        "exported_at": _now().isoformat(),
        "count": len(events),
        "events": events,
    }
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    dest = DATA_DIR / "bundles"
    dest.mkdir(parents=True, exist_ok=True)
    path = dest / f"bundle_{bundle['bundle_id']}.json"
    path.write_text(json.dumps(bundle, indent=2), encoding="utf-8")
    bundle["path"] = str(path)
    return bundle


def import_bundle(db: Session, bundle: dict[str, Any]) -> dict[str, int]:
    added = 0
    skipped = 0
    for ev in bundle.get("events") or []:
        eid = ev.get("event_id") or make_event_id(
            ev.get("author", "anon"), ev.get("body", ""), ev.get("created_at") or ""
        )
        if db.query(CrowdEvent).filter(CrowdEvent.event_id == eid).first():
            skipped += 1
            continue
        created = None
        if ev.get("created_at"):
            try:
                created = datetime.fromisoformat(ev["created_at"].replace("Z", ""))
            except ValueError:
                created = None
        publish(
            db,
            kind=ev.get("kind") or "general",
            body=ev.get("body") or "",
            author=ev.get("author") or "anon",
            origin_node=ev.get("origin_node") or "gossip",
            title=ev.get("title") or "",
            field_id=ev.get("field_id"),
            node_id=ev.get("node_id"),
            problem_id=ev.get("problem_id"),
            overland_id=ev.get("overland_id"),
            lat=ev.get("lat"),
            lon=ev.get("lon"),
            event_id=eid,
            created_at=created,
        )
        added += 1
    return {"added": added, "skipped": skipped}
