from sqlalchemy.orm import Mapped, mapped_column
from backend.database import Base
from typing import Optional

class Athlete(Base):
    __tablename__ = "athletes"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(nullable=False)
    team: Mapped[Optional[str]] = mapped_column(default=None)
    age: Mapped[Optional[int]] = mapped_column(default=None)
    position: Mapped[Optional[str]] = mapped_column(default=None)
    notes: Mapped[Optional[str]] = mapped_column(default=None)
