"""JuniorForumMesh — append-only crowd events + gossip metadata."""
from __future__ import annotations

from datetime import datetime
from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base


class CrowdEvent(Base):
    __tablename__ = "junior_crowd_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    kind: Mapped[str] = mapped_column(String(32), default="beta")
    # beta | conditions | access | overland | waypoint | photo | grade | general
    author: Mapped[str] = mapped_column(String(64), default="anon")
    origin_node: Mapped[str] = mapped_column(String(64), default="local")
    field_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    node_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    problem_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    overland_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    title: Mapped[str] = mapped_column(String(160), default="")
    body: Mapped[str] = mapped_column(Text, nullable=False)
    lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    lon: Mapped[float | None] = mapped_column(Float, nullable=True)
    trust: Mapped[float] = mapped_column(Float, default=0.5)
    disagreement: Mapped[float] = mapped_column(Float, default=0.0)
    recommendation: Mapped[str] = mapped_column(String(32), default="low_confidence")
    condition: Mapped[str] = mapped_column(String(24), default="unknown")
    access: Mapped[str] = mapped_column(String(24), default="unknown")
    embed_csv: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
