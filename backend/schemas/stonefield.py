"""JuniorStoneField Pydantic schemas — community boulder + beta board."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class StoneFieldIn(BaseModel):
    name: str
    region: str = "Colorado"
    lat: float
    lon: float
    elevation_ft: Optional[int] = None
    notes: Optional[str] = None
    access_notes: Optional[str] = None


class StoneFieldOut(StoneFieldIn):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class BoulderNodeIn(BaseModel):
    field_id: int
    name: str
    lat: float
    lon: float
    subarea: Optional[str] = None
    rock_type: str = "granite"
    notes: Optional[str] = None
    submitted_by: str = "anon"


class BoulderNodeOut(BoulderNodeIn):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ProblemIn(BaseModel):
    node_id: int
    name: str
    grade: str = Field(..., description="V-scale or Yosemite decimal, e.g. V4 or 5.10a")
    style: str = "boulder"  # boulder | sport | trad | mixed
    sit_start: bool = False
    first_ascent: Optional[str] = None
    description: Optional[str] = None
    submitted_by: str = "anon"


class ProblemOut(ProblemIn):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class TopoIn(BaseModel):
    node_id: Optional[int] = None
    problem_id: Optional[int] = None
    caption: str = ""
    media_path: str = ""  # local relative path under data/topos
    kind: str = "photo"  # photo | topo | video_ref
    submitted_by: str = "anon"


class TopoOut(TopoIn):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class RouteSetIn(BaseModel):
    name: str
    venue: str = "gym"  # gym | outdoor
    setter: str = ""
    grade_range: str = ""
    color: Optional[str] = None
    wall: Optional[str] = None
    notes: Optional[str] = None
    field_id: Optional[int] = None
    node_id: Optional[int] = None


class RouteSetOut(RouteSetIn):
    id: int
    created_at: datetime
    stripped: bool = False

    class Config:
        from_attributes = True


class BetaPostIn(BaseModel):
    field_id: Optional[int] = None
    node_id: Optional[int] = None
    problem_id: Optional[int] = None
    author: str = "anon"
    title: str = ""
    body: str
    kind: str = "beta"  # beta | conditions | access | general


class BetaPostOut(BetaPostIn):
    id: int
    created_at: datetime
    replies: List["BetaReplyOut"] = []

    class Config:
        from_attributes = True


class BetaReplyIn(BaseModel):
    post_id: int
    author: str = "anon"
    body: str


class BetaReplyOut(BetaReplyIn):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


BetaPostOut.model_rebuild()
