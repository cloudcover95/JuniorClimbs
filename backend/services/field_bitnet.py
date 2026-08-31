"""JuniorFieldBitNet — ternary core for StoneField + NavMesh + CrowdMesh.

Original JuniorCloud discipline head. Not a hosted LLM.
Torch TinyQuantized path when available; deterministic ternary fallback otherwise.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = None
    nn = None

LABELS = ["beta_trust", "access_caution", "tenure_usfs", "tenure_private", "nav_priority"]

ACCESS_TOKENS = ("private", "gate", "no trespass", "closed", "posted", "ranch", "permit")
USFS_TOKENS = ("usfs", "national forest", "dispersed", "forest service", "blm")
BETA_TOKENS = ("crimp", "mantle", "sit start", "v0", "v1", "v2", "v3", "v4", "v5",
               "v6", "v7", "v8", "pad", "topout", "arete", "slab")
NAV_TOKENS = ("trailhead", "parking", "approach", "gps", "waypoint", "water", "camp")


def _fnv_bytes(text: str, n: int = 16) -> list[float]:
    digest = hashlib.sha256(text.encode("utf-8", errors="replace")).digest()
    out = []
    for i in range(n):
        # map byte to ternary-ish {-1, 0, 1} then keep as float feature
        b = digest[i % len(digest)]
        if b < 85:
            out.append(-1.0)
        elif b < 170:
            out.append(0.0)
        else:
            out.append(1.0)
    return out


def _token_hits(text: str, tokens: tuple[str, ...]) -> float:
    low = text.lower()
    hits = sum(1 for t in tokens if t in low)
    return min(1.0, hits / 3.0)


@dataclass
class FieldInference:
    label: str
    score: float
    scores: dict[str, float]
    backend: str
    notes: str


if TORCH_AVAILABLE:
    class FieldTernaryNet(nn.Module):
        def __init__(self, dim: int = 16, hidden: int = 24, heads: int = 5):
            super().__init__()
            self.fc1 = nn.Linear(dim, hidden)
            self.fc2 = nn.Linear(hidden, heads)
            with torch.no_grad():
                for p in self.parameters():
                    p.data = torch.round(p.data).clamp(-1, 1)

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            x = torch.tanh(self.fc1(x))
            return self.fc2(x)
else:
    FieldTernaryNet = None  # type: ignore


class JuniorFieldBitNet:
    def __init__(self):
        self.backend = "torch-ternary" if TORCH_AVAILABLE else "ternary-hash"
        self.model = None
        if TORCH_AVAILABLE:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model = FieldTernaryNet().to(self.device).eval()
        else:
            self.device = None

    def features(self, text: str, lat: float | None = None, lon: float | None = None) -> list[float]:
        feats = _fnv_bytes(text, 12)
        feats.append(_token_hits(text, BETA_TOKENS))
        feats.append(_token_hits(text, ACCESS_TOKENS))
        feats.append(_token_hits(text, USFS_TOKENS))
        geo = 0.0
        if lat is not None and lon is not None:
            geo = 1.0 if (40.65 < lat < 41.0 and -105.85 < lon < -105.30) else 0.35
        feats.append(geo)
        return feats[:16] if len(feats) >= 16 else feats + [0.0] * (16 - len(feats))

    def infer(self, text: str, lat: float | None = None, lon: float | None = None) -> FieldInference:
        feats = self.features(text, lat, lon)
        notes = []

        if self.model is not None:
            x = torch.tensor([feats], dtype=torch.float32, device=self.device)
            with torch.no_grad():
                logits = self.model(x)[0]
                probs = torch.softmax(logits, dim=0)
            scores = {LABELS[i]: float(probs[i].item()) for i in range(len(LABELS))}
            idx = int(probs.argmax().item())
            backend = f"torch-ternary:{self.device}"
        else:
            raw = {
                "beta_trust": 0.25 + 0.7 * feats[12],
                "access_caution": 0.15 + 0.8 * feats[13],
                "tenure_usfs": 0.2 + 0.7 * feats[14],
                "tenure_private": 0.15 + 0.8 * feats[13],
                "nav_priority": 0.2 + 0.6 * _token_hits(text, NAV_TOKENS) + 0.2 * feats[15],
            }
            total = sum(raw.values()) or 1.0
            scores = {k: v / total for k, v in raw.items()}
            idx = max(range(len(LABELS)), key=lambda i: scores[LABELS[i]])
            backend = "ternary-hash"

        if feats[13] > 0:
            notes.append("access language present")
        if feats[12] > 0:
            notes.append("beta lexicon present")
        if feats[15] >= 1.0:
            notes.append("inside RFL geo envelope")

        return FieldInference(
            label=LABELS[idx],
            score=round(scores[LABELS[idx]], 4),
            scores={k: round(v, 4) for k, v in scores.items()},
            backend=backend,
            notes="; ".join(notes) or "neutral",
        )


field_bitnet = JuniorFieldBitNet()
