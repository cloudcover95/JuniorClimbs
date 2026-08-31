"""JuniorStoneField gym programs + access pledges."""
from __future__ import annotations

from datetime import datetime
from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base


class AccessPledge(Base):
    __tablename__ = "junior_access_pledges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    subject_kind: Mapped[str] = mapped_column(String(24), default="node")  # node | field | problem | source
    subject_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tenure: Mapped[str] = mapped_column(String(24), default="unknown")
    owner_consent: Mapped[bool] = mapped_column(Boolean, default=False)
    consent_by: Mapped[str] = mapped_column(String(128), default="")
    visibility: Mapped[str] = mapped_column(String(24), default="public")  # public | gym_internal | private
    attester: Mapped[str] = mapped_column(String(64), default="anon")
    accepted_terms: Mapped[str] = mapped_column(String(64), default="")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class GymProgram(Base):
    __tablename__ = "junior_gym_programs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    kind: Mapped[str] = mapped_column(String(32), default="camp")  # camp | team | after_school | clinic | staff
    season: Mapped[str] = mapped_column(String(64), default="")
    visibility: Mapped[str] = mapped_column(String(24), default="gym_internal")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ClassBlock(Base):
    __tablename__ = "junior_class_blocks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    program_id: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    day: Mapped[str] = mapped_column(String(32), default="")
    start_time: Mapped[str] = mapped_column(String(16), default="")
    wall: Mapped[str] = mapped_column(String(64), default="")
    coach: Mapped[str] = mapped_column(String(64), default="")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class StudyPlan(Base):
    __tablename__ = "junior_study_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    program_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    problem_ids: Mapped[str] = mapped_column(Text, default="")  # csv
    routeset_ids: Mapped[str] = mapped_column(Text, default="")
    field_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
