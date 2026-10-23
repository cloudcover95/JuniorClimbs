"""Send-rate statistics for climbing sessions.

Pure-stdlib helpers that summarise a list of route/problem attempts:
flash rate, send rate, and average attempts-to-send per grade label.
Additive module; no network, no I/O.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional


@dataclass(frozen=True)
class Attempt:
    """One logged effort on a climb."""

    climb_id: str
    grade: str
    sent: bool


@dataclass(frozen=True)
class GradeStats:
    grade: str
    climbs: int
    sends: int
    flashes: int
    attempts: int
    send_rate: float
    flash_rate: float
    avg_attempts_to_send: Optional[float]


def _group(attempts: Iterable[Attempt]) -> Dict[str, List[Attempt]]:
    grouped: Dict[str, List[Attempt]] = {}
    for a in attempts:
        grouped.setdefault(a.climb_id, []).append(a)
    return grouped


def grade_stats(attempts: Iterable[Attempt]) -> Dict[str, GradeStats]:
    """Return per-grade stats. Attempt order within a climb is preserved.

    A climb is a flash if its first attempt is a send. Attempts after the
    first send on a climb are ignored when counting attempts-to-send.
    """
    per_grade: Dict[str, dict] = {}
    for climb_id, tries in _group(attempts).items():
        grade = tries[0].grade
        g = per_grade.setdefault(
            grade, {"climbs": 0, "sends": 0, "flashes": 0, "attempts": 0, "to_send": []}
        )
        g["climbs"] += 1
        g["attempts"] += len(tries)
        for idx, t in enumerate(tries, start=1):
            if t.sent:
                g["sends"] += 1
                g["to_send"].append(idx)
                if idx == 1:
                    g["flashes"] += 1
                break
    out: Dict[str, GradeStats] = {}
    for grade, g in per_grade.items():
        climbs = g["climbs"]
        to_send = g["to_send"]
        out[grade] = GradeStats(
            grade=grade,
            climbs=climbs,
            sends=g["sends"],
            flashes=g["flashes"],
            attempts=g["attempts"],
            send_rate=g["sends"] / climbs if climbs else 0.0,
            flash_rate=g["flashes"] / climbs if climbs else 0.0,
            avg_attempts_to_send=(sum(to_send) / len(to_send)) if to_send else None,
        )
    return out


def _self_check() -> None:
    log = [
        Attempt("a", "V3", True),
        Attempt("b", "V3", False),
        Attempt("b", "V3", True),
        Attempt("c", "V5", False),
        Attempt("c", "V5", False),
    ]
    s = grade_stats(log)
    v3, v5 = s["V3"], s["V5"]
    assert (v3.climbs, v3.sends, v3.flashes, v3.attempts) == (2, 2, 1, 3)
    assert v3.send_rate == 1.0 and v3.flash_rate == 0.5
    assert v3.avg_attempts_to_send == 1.5
    assert (v5.sends, v5.send_rate, v5.avg_attempts_to_send) == (0, 0.0, None)
    assert grade_stats([]) == {}


if __name__ == "__main__":
    _self_check()
    print("send_rate self-check ok")
