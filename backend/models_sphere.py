"""JuniorRegionSphere / JuniorArenaNode models."""
from __future__ import annotations

from datetime import datetime
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class ArenaNode(Base):
    __tablename__ = "junior_arena_nodes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    field_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lon: Mapped[float] = mapped_column(Float, nullable=False)
    kind: Mapped[str] = mapped_column(String(32), default="trailhead")  # trailhead | parking | summit | crag
    radius_m: Mapped[float] = mapped_column(Float, default=80.0)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    spheres = relationship("RegionSphere", back_populates="arena")


class RegionSphere(Base):
    __tablename__ = "junior_region_spheres"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    arena_id: Mapped[int] = mapped_column(ForeignKey("junior_arena_nodes.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    pano_path: Mapped[str] = mapped_column(String(512), default="")  # data/spheres/{id}/equirect.jpg
    north_offset_deg: Mapped[float] = mapped_column(Float, default=0.0)  # photo north vs true north
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    arena = relationship("ArenaNode", back_populates="spheres")
    hotspots = relationship("SphereHotspot", back_populates="sphere")


class SphereHotspot(Base):
    __tablename__ = "junior_sphere_hotspots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sphere_id: Mapped[int] = mapped_column(ForeignKey("junior_region_spheres.id"), nullable=False)
    node_id: Mapped[int | None] = mapped_column(Integer, nullable=True)  # JuniorBoulderNode
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    yaw_deg: Mapped[float] = mapped_column(Float, default=0.0)  # 0 = north of pano
    pitch_deg: Mapped[float] = mapped_column(Float, default=0.0)
    lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    lon: Mapped[float | None] = mapped_column(Float, nullable=True)
    thumb_path: Mapped[str] = mapped_column(String(512), default="")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    sphere = relationship("RegionSphere", back_populates="hotspots")
