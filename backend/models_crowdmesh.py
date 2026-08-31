"""JuniorCrowdMesh — offline crowdsourced envelopes. Additive."""
from __future__ import annotations

from datetime import datetime
from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base


class CrowdEnvelope(Base):
    __tablename__ = "junior_crowd_envelopes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    envelope_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    author: Mapped[str] = mapped_column(String(64), default="anon")
    topic: Mapped[str] = mapped_column(String(24), default="general")
    title: Mapped[str] = mapped_column(String(160), default="")
    body: Mapped[str] = mapped_column(Text, nullable=False)
    lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    lon: Mapped[float | None] = mapped_column(Float, nullable=True)
    field_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    node_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    origin_device: Mapped[str] = mapped_column(String(64), default="local")
    bitnet_label: Mapped[str | None] = mapped_column(String(32), nullable=True)
    bitnet_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
