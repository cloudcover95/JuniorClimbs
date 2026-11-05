"""Hangboard load helpers: bodyweight percent for weighted or assisted hangs.

Stdlib-only. Additive slice for JuniorClimbs training math.
"""

from __future__ import annotations


def effective_load_kg(bodyweight_kg: float, added_kg: float = 0.0) -> float:
    """Return total hanging mass in kg (bodyweight + added; negative added = assistance)."""
    if bodyweight_kg <= 0:
        raise ValueError("bodyweight_kg must be positive")
    total = bodyweight_kg + added_kg
    if total <= 0:
        raise ValueError("effective load must be positive (too much assistance)")
    return total


def load_percent_bw(bodyweight_kg: float, added_kg: float = 0.0) -> float:
    """Effective load as a percent of bodyweight (100 = bodyweight hang)."""
    bw = bodyweight_kg
    if bw <= 0:
        raise ValueError("bodyweight_kg must be positive")
    return 100.0 * effective_load_kg(bw, added_kg) / bw


def added_kg_for_target_percent(bodyweight_kg: float, target_percent_bw: float) -> float:
    """Added mass (kg) needed so effective load equals target_percent_bw of bodyweight.

    Positive = weight plate; negative = pulley assistance.
    """
    if bodyweight_kg <= 0:
        raise ValueError("bodyweight_kg must be positive")
    if target_percent_bw <= 0:
        raise ValueError("target_percent_bw must be positive")
    return bodyweight_kg * (target_percent_bw / 100.0 - 1.0)


def _self_check() -> None:
    assert abs(effective_load_kg(70.0, 10.0) - 80.0) < 1e-9
    assert abs(effective_load_kg(70.0, -14.0) - 56.0) < 1e-9
    assert abs(load_percent_bw(70.0, 0.0) - 100.0) < 1e-9
    assert abs(load_percent_bw(70.0, 14.0) - 120.0) < 1e-9
    assert abs(load_percent_bw(70.0, -14.0) - 80.0) < 1e-9
    assert abs(added_kg_for_target_percent(70.0, 120.0) - 14.0) < 1e-9
    assert abs(added_kg_for_target_percent(70.0, 80.0) - (-14.0)) < 1e-9
    assert abs(added_kg_for_target_percent(70.0, 100.0)) < 1e-9
    try:
        effective_load_kg(0.0, 0.0)
        raise AssertionError("expected ValueError for non-positive bodyweight")
    except ValueError:
        pass
    try:
        effective_load_kg(70.0, -80.0)
        raise AssertionError("expected ValueError for non-positive effective load")
    except ValueError:
        pass
    try:
        added_kg_for_target_percent(70.0, 0.0)
        raise AssertionError("expected ValueError for non-positive target")
    except ValueError:
        pass
    # Round-trip: percent -> added -> percent
    for pct in (70.0, 100.0, 130.0):
        add = added_kg_for_target_percent(72.5, pct)
        assert abs(load_percent_bw(72.5, add) - pct) < 1e-9


if __name__ == "__main__":
    _self_check()
    print("hangboard_load self-check: ok")
