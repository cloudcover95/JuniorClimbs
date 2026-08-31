#!/usr/bin/env python3
"""Seed + print JuniorStoneField health (no HTTP). Uses sqlite memory."""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import backend.database as database
from backend.database import Base

engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, future=True)
Session = sessionmaker(bind=engine, future=True, autoflush=False, autocommit=False)
database.engine = engine
database.SessionLocal = Session

import backend.models_stonefield  # noqa: F401
import backend.models_navmesh  # noqa: F401
import backend.models_forum  # noqa: F401
import backend.models_sphere  # noqa: F401
import backend.models_source  # noqa: F401
import backend.models_programs  # noqa: F401

Base.metadata.create_all(bind=engine)
from backend.beta_boot import health

db = Session()
print(health(db))
