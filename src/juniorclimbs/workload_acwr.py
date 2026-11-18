"""Acute:chronic workload ratio for climbing sessions (EWMA form). Pure stdlib."""
from __future__ import annotations
from typing import Iterable, List


def ewma(loads: Iterable[float], span: int) -> List[float]:
    if span < 1:
        raise ValueError("span must be >= 1")
    a = 2.0 / (span + 1)
    out: List[float] = []
    prev = None
    for x in loads:
        if x < 0:
            raise ValueError("load must be >= 0")
        prev = float(x) if prev is None else a * x + (1 - a) * prev
        out.append(prev)
    return out


def acwr(daily_loads: Iterable[float], acute: int = 7, chronic: int = 28) -> List[float]:
    """Return per-day acute/chronic EWMA ratio (0.0 where chronic is 0)."""
    loads = list(daily_loads)
    if acute >= chronic:
        raise ValueError("acute span must be < chronic span")
    ac, ch = ewma(loads, acute), ewma(loads, chronic)
    return [a / c if c > 0 else 0.0 for a, c in zip(ac, ch)]


def zone(ratio: float) -> str:
    if ratio < 0.8:
        return "detraining"
    if ratio <= 1.3:
        return "sweet_spot"
    if ratio <= 1.5:
        return "caution"
    return "high_risk"


def _self_check() -> None:
    assert all(abs(r - 1.0) < 1e-9 for r in acwr([50] * 40))
    assert acwr([0] * 5) == [0.0] * 5
    assert acwr([30] * 28 + [120] * 7)[-1] > 1.5
    assert zone(1.0) == "sweet_spot" and zone(0.5) == "detraining" and zone(2) == "high_risk"
    try:
        ewma([-1], 3)
    except ValueError:
        pass
    else:
        raise AssertionError
    print("acwr self-check ok")


if __name__ == "__main__":
    _self_check()
