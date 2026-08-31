"""JuniorSourceLedger — licensed community route/boulder projects."""
from __future__ import annotations

from datetime import datetime
from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base

ALLOWED_LICENSES = ("CC0-1.0", "CC-BY-4.0", "CC-BY-SA-4.0", "public-domain")


class SourceProject(Base):
    __tablename__ = "junior_source_projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_name: Mapped[str] = mapped_column(String(160), nullable=False)
    license: Mapped[str] = mapped_column(String(32), default="CC-BY-4.0")
    attribution: Mapped[str] = mapped_column(String(160), default="anon")
    field_name: Mapped[str] = mapped_column(String(128), default="")
    field_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    homepage: Mapped[str] = mapped_column(String(256), default="")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    node_count: Mapped[int] = mapped_column(Integer, default=0)
    problem_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
