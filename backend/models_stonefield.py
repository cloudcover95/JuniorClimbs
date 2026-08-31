"""JuniorStoneField SQLAlchemy models — additive tables only."""
from __future__ import annotations

from datetime import datetime
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class StoneField(Base):
    __tablename__ = "junior_stone_fields"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    region: Mapped[str] = mapped_column(String(64), default="Colorado")
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lon: Mapped[float] = mapped_column(Float, nullable=False)
    elevation_ft: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    access_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    nodes = relationship("BoulderNode", back_populates="field")


class BoulderNode(Base):
    __tablename__ = "junior_boulder_nodes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    field_id: Mapped[int] = mapped_column(ForeignKey("junior_stone_fields.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lon: Mapped[float] = mapped_column(Float, nullable=False)
    subarea: Mapped[str | None] = mapped_column(String(128), nullable=True)
    rock_type: Mapped[str] = mapped_column(String(32), default="granite")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    submitted_by: Mapped[str] = mapped_column(String(64), default="anon")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    field = relationship("StoneField", back_populates="nodes")
    problems = relationship("ClimbProblem", back_populates="node")


class ClimbProblem(Base):
    __tablename__ = "junior_problems"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    node_id: Mapped[int] = mapped_column(ForeignKey("junior_boulder_nodes.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    grade: Mapped[str] = mapped_column(String(24), nullable=False)
    style: Mapped[str] = mapped_column(String(24), default="boulder")
    sit_start: Mapped[bool] = mapped_column(Boolean, default=False)
    first_ascent: Mapped[str | None] = mapped_column(String(128), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    submitted_by: Mapped[str] = mapped_column(String(64), default="anon")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    node = relationship("BoulderNode", back_populates="problems")


class TopoMesh(Base):
    __tablename__ = "junior_topo_mesh"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    node_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    problem_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    caption: Mapped[str] = mapped_column(String(256), default="")
    media_path: Mapped[str] = mapped_column(String(512), default="")
    kind: Mapped[str] = mapped_column(String(24), default="photo")
    submitted_by: Mapped[str] = mapped_column(String(64), default="anon")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class RouteSetLedger(Base):
    __tablename__ = "junior_routeset_ledger"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    venue: Mapped[str] = mapped_column(String(24), default="gym")
    setter: Mapped[str] = mapped_column(String(64), default="")
    grade_range: Mapped[str] = mapped_column(String(32), default="")
    color: Mapped[str | None] = mapped_column(String(32), nullable=True)
    wall: Mapped[str | None] = mapped_column(String(64), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    field_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    node_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    stripped: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class BetaPost(Base):
    __tablename__ = "junior_beta_board"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    field_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    node_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    problem_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    author: Mapped[str] = mapped_column(String(64), default="anon")
    title: Mapped[str] = mapped_column(String(160), default="")
    body: Mapped[str] = mapped_column(Text, nullable=False)
    kind: Mapped[str] = mapped_column(String(24), default="beta")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    replies = relationship("BetaReply", back_populates="post")


class BetaReply(Base):
    __tablename__ = "junior_beta_replies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("junior_beta_board.id"), nullable=False)
    author: Mapped[str] = mapped_column(String(64), default="anon")
    body: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    post = relationship("BetaPost", back_populates="replies")
