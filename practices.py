from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from backend.database import Base
from typing import Optional

class Practice(Base):
    __tablename__ = "practices"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(nullable=False)
    date: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    team: Mapped[Optional[str]] = mapped_column(default=None)
    duration: Mapped[int] = mapped_column(default=60)
    location: Mapped[Optional[str]] = mapped_column(default=None)
    notes: Mapped[Optional[str]] = mapped_column(default=None)
