"""Ingest / export JuniorSourceProject documents into StoneField."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from backend.models_source import ALLOWED_LICENSES, SourceProject
from backend.models_stonefield import StoneField, BoulderNode, ClimbProblem
from backend.forum_mesh import publish

SCHEMA = {
    "format": "junior-source-v1",
    "license": "CC-BY-4.0 | CC0-1.0 | CC-BY-SA-4.0 | public-domain",
    "attribution": "string",
    "project_name": "string",
    "field_name": "string",
    "nodes": [{"name": "str", "lat": "float", "lon": "float", "rock_type": "str?", "subarea": "str?", "notes": "str?"}],
    "problems": [{"node_name": "str", "name": "str", "grade": "str", "style": "boulder", "description": "str?"}],
}


def _now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def import_document(db: Session, doc: dict[str, Any]) -> dict[str, Any]:
    license_id = (doc.get("license") or "").strip()
    if license_id not in ALLOWED_LICENSES:
        return {
            "ok": False,
            "error": "license_not_open",
            "allowed": list(ALLOWED_LICENSES),
            "note": "Closed or missing license is not copied into the local store.",
        }
    field_name = doc.get("field_name") or "Community Field"
    field = db.query(StoneField).filter(StoneField.name == field_name).first()
    if field is None:
        first_node = (doc.get("nodes") or [{}])[0]
        field = StoneField(
            name=field_name,
            region="community",
            lat=float(first_node.get("lat") or 0.0),
            lon=float(first_node.get("lon") or 0.0),
            notes=f"Created from source project {doc.get('project_name')}",
        )
        db.add(field)
        db.commit()
        db.refresh(field)

    added_nodes = 0
    added_problems = 0
    by_name: dict[str, BoulderNode] = {
        n.name: n for n in db.query(BoulderNode).filter(BoulderNode.field_id == field.id).all()
    }
    attr = doc.get("attribution") or "community"
    for raw in doc.get("nodes") or []:
        name = (raw.get("name") or "").strip()
        if not name:
            continue
        if name not in by_name:
            node = BoulderNode(
                field_id=field.id,
                name=name,
                lat=float(raw.get("lat") or field.lat),
                lon=float(raw.get("lon") or field.lon),
                subarea=raw.get("subarea"),
                rock_type=raw.get("rock_type") or "unknown",
                notes=raw.get("notes"),
                submitted_by=attr,
            )
            db.add(node)
            db.commit()
            db.refresh(node)
            by_name[name] = node
            added_nodes += 1
        node = by_name[name]
    for raw in doc.get("problems") or []:
        nname = (raw.get("node_name") or "").strip()
        pname = (raw.get("name") or "").strip()
        if not nname or not pname or nname not in by_name:
            continue
        node = by_name[nname]
        exists = (
            db.query(ClimbProblem)
            .filter(ClimbProblem.node_id == node.id, ClimbProblem.name == pname)
            .first()
        )
        if exists:
            continue
        db.add(
            ClimbProblem(
                node_id=node.id,
                name=pname,
                grade=raw.get("grade") or "?",
                style=raw.get("style") or "boulder",
                description=raw.get("description"),
                submitted_by=attr,
            )
        )
        added_problems += 1
    db.commit()

    proj = SourceProject(
        project_name=doc.get("project_name") or "untitled",
        license=license_id,
        attribution=attr,
        field_name=field.name,
        field_id=field.id,
        homepage=doc.get("homepage") or "",
        notes=doc.get("notes"),
        node_count=added_nodes,
        problem_count=added_problems,
        created_at=_now(),
    )
    db.add(proj)
    db.commit()
    db.refresh(proj)

    publish(
        db,
        kind="general",
        title=f"source import: {proj.project_name}",
        body=f"{attr} licensed {license_id} — {added_nodes} nodes, {added_problems} problems into {field.name}",
        author=attr,
        field_id=field.id,
    )
    return {
        "ok": True,
        "project_id": proj.id,
        "field_id": field.id,
        "added_nodes": added_nodes,
        "added_problems": added_problems,
        "license": license_id,
    }


def export_field(db: Session, field_id: int, license_id: str = "CC-BY-4.0") -> dict[str, Any]:
    field = db.get(StoneField, field_id)
    if field is None:
        return {"ok": False, "error": "field_not_found"}
    nodes = db.query(BoulderNode).filter(BoulderNode.field_id == field_id).all()
    payload_nodes = []
    payload_problems = []
    for n in nodes:
        payload_nodes.append(
            {
                "name": n.name,
                "lat": n.lat,
                "lon": n.lon,
                "rock_type": n.rock_type,
                "subarea": n.subarea,
                "notes": n.notes,
            }
        )
        for p in n.problems:
            payload_problems.append(
                {
                    "node_name": n.name,
                    "name": p.name,
                    "grade": p.grade,
                    "style": p.style,
                    "description": p.description,
                }
            )
    return {
        "format": "junior-source-v1",
        "license": license_id,
        "attribution": "JuniorClimbs local node",
        "project_name": f"{field.name} local export",
        "field_name": field.name,
        "nodes": payload_nodes,
        "problems": payload_problems,
    }
