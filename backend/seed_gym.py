"""Default indoor JuniorHall field + camp program for local gym beta."""
from __future__ import annotations

from sqlalchemy.orm import Session

from backend.models_stonefield import StoneField, BoulderNode, RouteSetLedger
from backend.models_programs import GymProgram, ClassBlock, StudyPlan


def ensure_gym_seed(db: Session) -> StoneField:
    hall = db.query(StoneField).filter(StoneField.name == "JuniorHall").first()
    if hall is None:
        hall = StoneField(
            name="JuniorHall",
            region="Indoor — local gym",
            lat=0.0,
            lon=0.0,
            elevation_ft=0,
            notes="Default indoor field for camps, classes, and current sets. Not a public crag.",
            access_notes="visibility=gym_internal. Staff present sets; members do not publish outdoor private land here.",
        )
        db.add(hall)
        db.commit()
        db.refresh(hall)

    existing = {n.name for n in db.query(BoulderNode).filter(BoulderNode.field_id == hall.id).all()}
    for name, wall in [("Cave", "cave"), ("Main slab", "slab"), ("Comp wall", "comp")]:
        if name in existing:
            continue
        db.add(
            BoulderNode(
                field_id=hall.id,
                name=name,
                lat=0.0,
                lon=0.0,
                subarea=wall,
                rock_type="plastic",
                notes="Indoor volume. Gym-internal.",
                submitted_by="juniorhall-seed",
            )
        )
    if db.query(RouteSetLedger).filter(RouteSetLedger.venue == "gym").count() == 0:
        db.add(
            RouteSetLedger(
                name="Week-of set — moderate circuit",
                venue="gym",
                setter="staff",
                grade_range="V1-V4",
                color="teal",
                wall="Cave",
                notes="Swap this each reset. Used by default camp study plan.",
                field_id=hall.id,
            )
        )
    if db.query(GymProgram).filter(GymProgram.name == "Summer camp week 1").first() is None:
        prog = GymProgram(
            name="Summer camp week 1",
            kind="camp",
            season="2026-summer",
            visibility="gym_internal",
            notes="Template camp. Attach class blocks and a study plan.",
        )
        db.add(prog)
        db.commit()
        db.refresh(prog)
        db.add(
            ClassBlock(
                program_id=prog.id,
                title="Slab movement",
                day="Mon",
                start_time="10:00",
                wall="Main slab",
                coach="staff",
            )
        )
        db.add(
            ClassBlock(
                program_id=prog.id,
                title="Cave power",
                day="Wed",
                start_time="10:00",
                wall="Cave",
                coach="staff",
            )
        )
        db.add(
            StudyPlan(
                program_id=prog.id,
                name="Camp circuit A",
                field_id=hall.id,
                notes="Point kids at the teal circuit + one outdoor public field trip later.",
            )
        )
    db.commit()
    return hall
