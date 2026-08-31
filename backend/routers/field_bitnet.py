"""JuniorFieldBitNet HTTP surface."""
from fastapi import APIRouter
from pydantic import BaseModel

from backend.services.field_bitnet import field_bitnet, LABELS

router = APIRouter(prefix="/fieldbitnet", tags=["JuniorFieldBitNet"])


class InferIn(BaseModel):
    text: str
    lat: float | None = None
    lon: float | None = None


@router.get("/status")
def status():
    return {
        "name": "JuniorFieldBitNet",
        "discipline": ["JuniorStoneField", "JuniorNavMesh", "JuniorCrowdMesh"],
        "backend": field_bitnet.backend,
        "labels": LABELS,
        "offline": True,
        "weights": "ternary {-1,0,+1}",
    }


@router.post("/infer")
def infer(payload: InferIn):
    inf = field_bitnet.infer(payload.text, payload.lat, payload.lon)
    return {
        "label": inf.label,
        "score": inf.score,
        "scores": inf.scores,
        "backend": inf.backend,
        "notes": inf.notes,
    }
