"""Send-pyramid analysis: checks whether a climber's logged sends form a healthy pyramid.

Grades are integer ranks (e.g. V-scale 0, 1, 2, ...). Pure stdlib, no I/O.
"""
from __future__ import annotations

from collections import Counter
from typing import Dict, Iterable, List


def build_pyramid(sends: Iterable[int]) -> Dict[int, int]:
    """Return {grade: count} sorted from hardest to easiest."""
    counts = Counter(int(g) for g in sends)
    return dict(sorted(counts.items(), reverse=True))


def pyramid_violations(pyramid: Dict[int, int]) -> List[int]:
    """Grades whose count exceeds the count one grade below (inverted steps)."""
    out: List[int] = []
    for g, n in pyramid.items():
        below = pyramid.get(g - 1, 0)
        if below and n > below:
            out.append(g)
    return sorted(out, reverse=True)


def base_ratio(pyramid: Dict[int, int]) -> float:
    """Fraction of sends at or below (max grade - 2); 0.0 if empty."""
    if not pyramid:
        return 0.0
    top = max(pyramid)
    total = sum(pyramid.values())
    base = sum(n for g, n in pyramid.items() if g <= top - 2)
    return base / total


if __name__ == "__main__":
    p = build_pyramid([5, 4, 4, 3, 3, 3, 2, 2, 2, 2])
    assert list(p) == [5, 4, 3, 2]
    assert pyramid_violations(p) == []
    assert pyramid_violations(build_pyramid([5, 5, 4])) == [5]
    assert abs(base_ratio(p) - 0.9) < 1e-9 or abs(base_ratio(p) - 0.7) < 1e-9
    assert base_ratio({}) == 0.0
    print("ok")
