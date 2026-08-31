"""JuniorNavMesh models — offline maps, land, overland, GPS IoT. Additive."""
from __future__ import annotations

from datetime import datetime
from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base


class TilePack(Base):
    __tablename__ = "junior_tile_packs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    kind: Mapped[str] = mapped_column(String(24), default="osm")  # osm | sat | topo | custom
    path: Mapped[str] = mapped_column(String(512), default="data/tiles")
    min_zoom: Mapped[int] = mapped_column(Integer, default=8)
    max_zoom: Mapped[int] = mapped_column(Integer, default=15)
    south: Mapped[float] = mapped_column(Float, default=40.6)
    west: Mapped[float] = mapped_column(Float, default=-105.8)
    north: Mapped[float] = mapped_column(Float, default=40.95)
    east: Mapped[float] = mapped_column(Float, default=-105.35)
    bytes_est: Mapped[int] = mapped_column(Integer, default=0)
    offline_ready: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class LandLayer(Base):
    __tablename__ = "junior_land_layers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    tenure: Mapped[str] = mapped_column(String(32), default="usfs")  # usfs | blm | nps | state | private | unknown
    south: Mapped[float] = mapped_column(Float)
    west: Mapped[float] = mapped_column(Float)
    north: Mapped[float] = mapped_column(Float)
    east: Mapped[float] = mapped_column(Float)
    access: Mapped[str] = mapped_column(String(32), default="open")  # open | permit | closed | private
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class OverlandNode(Base):
    __tablename__ = "junior_overland_nodes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    kind: Mapped[str] = mapped_column(String(32), default="trailhead")
    # trailhead | camp | wild_camp | water | dump | parking | wifi | mechanic | gate
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lon: Mapped[float] = mapped_column(Float, nullable=False)
    field_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    conditions: Mapped[str | None] = mapped_column(Text, nullable=True)
    submitted_by: Mapped[str] = mapped_column(String(64), default="anon")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Waypoint(Base):
    __tablename__ = "junior_waypoints"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lon: Mapped[float] = mapped_column(Float, nullable=False)
    elev_ft: Mapped[float | None] = mapped_column(Float, nullable=True)
    kind: Mapped[str] = mapped_column(String(32), default="user")
    node_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class TrackRibbon(Base):
    __tablename__ = "junior_track_ribbons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    klass: Mapped[str] = mapped_column(String(32), default="approach")  # approach | offroad | hike | breadcrumb
    points_json: Mapped[str] = mapped_column(Text, default="[]")  # [[lat,lon,ele?], ...]
    field_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    node_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ApproachPath(Base):
    __tablename__ = "junior_approach_paths"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    from_overland_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    to_node_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    distance_mi: Mapped[float | None] = mapped_column(Float, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class GpsFix(Base):
    __tablename__ = "junior_gps_fixes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    device_id: Mapped[str] = mapped_column(String(64), default="handheld-1")
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lon: Mapped[float] = mapped_column(Float, nullable=False)
    elev_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    hdop: Mapped[float | None] = mapped_column(Float, nullable=True)
    sats: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source: Mapped[str] = mapped_column(String(24), default="nmea")  # nmea | gpx | manual
    raw: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
