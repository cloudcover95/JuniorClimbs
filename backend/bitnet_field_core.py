"""JuniorBitNetFieldCore — original 1.58-bit ternary engine for StoneField + NavMesh crowd reports.

Stdlib always works. Torch optional, matching BitNetIoT style.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

try:
    import torch
    import torch.nn as nn
    TORCH = True
except ImportError:
    TORCH = False
    torch = None
    nn = None

EMBED_DIM = 32
CONDITION_LABELS = ["unknown", "dry", "seeping", "icy", "wind", "hot", "restriction"]
ACCESS_LABELS = ["unknown", "open", "caution", "private", "closed"]
GRADE_BINS = ["VB-V1", "V2-V4", "V5-V7", "V8-V10", "V11+", "5.easy", "5.10-5.11", "5.12+"]


def _fnv(text: str) -> int:
    h = 2166136261
    for ch in text.encode("utf-8"):
        h ^= ch
        h = (h * 16777619) & 0xFFFFFFFF
    return h


def ternary_embed(text: str, dim: int = EMBED_DIM) -> list[int]:
    """Deterministic {-1,0,1} embedding from text. No network."""
    t = (text or "").lower()
    vec = [0] * dim
    if not t:
        return vec
    tokens = t.replace("/", " ").replace(",", " ").split()
    for i, tok in enumerate(tokens):
        h = _fnv(tok)
        idx = h % dim
        sign = -1 if (h >> 8) & 1 else 1
        if (h >> 3) & 7 == 0:
            vec[idx] = 0
        else:
            v = vec[idx] + sign
            vec[idx] = 1 if v > 0 else (-1 if v < 0 else 0)
        # second hash for spread
        idx2 = (h // dim) % dim
        vec[idx2] = 1 if ((h >> 1) + i) & 1 else -1
    return vec


def cosine_ternary(a: list[int], b: list[int]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(y * y for y in b) ** 0.5
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


_CONDITION_CUES = {
    "dry": ["dry", "crisp", "sendable", "good friction"],
    "seeping": ["seep", "wet", "damp", "drainage"],
    "icy": ["ice", "verglas", "frozen"],
    "wind": ["wind", "gust", "blown"],
    "hot": ["bake", "sunbaked", "too hot"],
    "restriction": ["closure", "fire ban", "restriction", "seasonal"],
}
_ACCESS_CUES = {
    "open": ["open", "public", "usfs", "blm", "good to go"],
    "caution": ["soft", "mud", "full lot", "5-car", "respect"],
    "private": ["private", "ranch", "no trespass", "gate locked"],
    "closed": ["closed", "rangers", "ticket", "do not"],
}


def _cue_label(text: str, table: dict[str, list[str]], labels: list[str]) -> tuple[str, float]:
    t = (text or "").lower()
    scores = {k: 0 for k in table}
    for label, cues in table.items():
        for c in cues:
            if c in t:
                scores[label] += 1
    best = max(scores, key=scores.get)
    total = sum(scores.values())
    if total == 0:
        return labels[0], 0.35
    return best, min(0.95, 0.45 + 0.15 * scores[best])


def _grade_bin(text: str) -> tuple[str, float]:
    t = (text or "").upper().replace(" ", "")
    import re
    m = re.search(r"V(\d{1,2})", t)
    if m:
        v = int(m.group(1))
        if v <= 1:
            return "VB-V1", 0.8
        if v <= 4:
            return "V2-V4", 0.8
        if v <= 7:
            return "V5-V7", 0.8
        if v <= 10:
            return "V8-V10", 0.8
        return "V11+", 0.8
    m = re.search(r"5\.(\d{1,2})", t)
    if m:
        n = int(m.group(1))
        if n <= 9:
            return "5.easy", 0.75
        if n <= 11:
            return "5.10-5.11", 0.75
        return "5.12+", 0.75
    return GRADE_BINS[0], 0.2


class _TinyFieldNet(nn.Module if TORCH else object):
    def __init__(self):
        if not TORCH:
            return
        super().__init__()
        self.fc1 = nn.Linear(EMBED_DIM, 16)
        self.fc2 = nn.Linear(16, 4)  # trust-ish logits
        with torch.no_grad():
            for p in self.parameters():
                p.data = torch.round(p.data).clamp(-1, 1)

    def forward(self, x):
        return self.fc2(torch.relu(self.fc1(x)))


@dataclass
class FieldScore:
    embed: list[int]
    trust: float
    disagreement: float
    recommendation: str
    condition: str
    condition_conf: float
    access: str
    access_conf: float
    grade_bin: str
    grade_conf: float
    backend: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class JuniorBitNetFieldCore:
    """Edge ternary core for crowd field reports."""

    def __init__(self):
        self.backend = "python-ternary"
        self.model = None
        if TORCH:
            dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model = _TinyFieldNet().to(dev).eval()
            self.device = dev
            self.backend = f"torch-ternary:{dev}"

    def score(self, text: str, prior_embed: list[int] | None = None) -> FieldScore:
        emb = ternary_embed(text)
        cond, cconf = _cue_label(text, _CONDITION_CUES, CONDITION_LABELS)
        acc, aconf = _cue_label(text, _ACCESS_CUES, ACCESS_LABELS)
        grade, gconf = _grade_bin(text)

        trust = 0.55 + 0.1 * min(len((text or "").split()) / 20.0, 1.0)
        if self.model is not None:
            x = torch.tensor([emb], dtype=torch.float32, device=self.device)
            with torch.no_grad():
                logits = self.model(x)
                trust = float(torch.sigmoid(logits[0, 0]).item())

        disagree = 0.0
        if prior_embed:
            sim = cosine_ternary(emb, prior_embed)
            disagree = max(0.0, 1.0 - (sim + 1.0) / 2.0)
            trust = max(0.05, trust * (1.0 - 0.4 * disagree))

        if disagree > 0.55:
            rec = "review_needed"
        elif trust >= 0.6:
            rec = "high_confidence"
        else:
            rec = "low_confidence"

        return FieldScore(
            embed=emb,
            trust=round(trust, 3),
            disagreement=round(disagree, 3),
            recommendation=rec,
            condition=cond,
            condition_conf=round(cconf, 3),
            access=acc,
            access_conf=round(aconf, 3),
            grade_bin=grade,
            grade_conf=round(gconf, 3),
            backend=self.backend,
        )


field_core = JuniorBitNetFieldCore()
