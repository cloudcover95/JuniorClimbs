"""Ape index helpers for JuniorClimbs.

Ape index compares arm span (wingspan) to height. Climbers often quote it
either as a difference (span - height) or as a ratio (span / height).
Pure functions, standard library only, no I/O.
"""

from __future__ import annotations

CM_PER_INCH = 2.54


def _check(value: float, name: str) -> float:
    v = float(value)
    if not v > 0:
        raise ValueError(f"{name} must be positive, got {value!r}")
    return v


def ape_difference(span: float, height: float) -> float:
    """Return span minus height, in the same unit as the inputs."""
    return _check(span, "span") - _check(height, "height")


def ape_ratio(span: float, height: float) -> float:
    """Return span divided by height (1.0 means span equals height)."""
    return _check(span, "span") / _check(height, "height")


def inches_to_cm(inches: float) -> float:
    return float(inches) * CM_PER_INCH


def classify(span: float, height: float, tolerance: float = 0.01) -> str:
    """Classify reach as 'positive', 'neutral', or 'negative'.

    tolerance is a fraction of height treated as neutral (default 1%).
    """
    if tolerance < 0:
        raise ValueError("tolerance must be non-negative")
    r = ape_ratio(span, height)
    if r > 1.0 + tolerance:
        return "positive"
    if r < 1.0 - tolerance:
        return "negative"
    return "neutral"


def _self_check() -> None:
    assert ape_difference(180, 175) == 5
    assert abs(ape_ratio(180, 180) - 1.0) < 1e-12
    assert classify(185, 175) == "positive"
    assert classify(170, 175) == "negative"
    assert classify(175.5, 175) == "neutral"
    assert abs(inches_to_cm(10) - 25.4) < 1e-9
    for bad in (0, -1):
        try:
            ape_ratio(bad, 170)
        except ValueError:
            pass
        else:
            raise AssertionError("expected ValueError")


if __name__ == "__main__":
    _self_check()
    print("ape_index self-check ok")
