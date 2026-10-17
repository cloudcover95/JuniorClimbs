"""Bouldering grade conversion helpers (V-scale <-> Fontainebleau).

Standalone, stdlib-only, additive utility for JuniorClimbs.
Run `python grade_convert.py` to execute the built-in self-check.
"""

V_TO_FONT = {
    0: "4", 1: "5", 2: "5+", 3: "6A", 4: "6B", 5: "6C", 6: "7A",
    7: "7A+", 8: "7B", 9: "7C", 10: "7C+", 11: "8A", 12: "8A+",
    13: "8B", 14: "8B+", 15: "8C", 16: "8C+", 17: "9A",
}
FONT_TO_V = {font: v for v, font in V_TO_FONT.items()}


def parse_v(grade):
    """Parse 'V5', 'v5' or 5 into an int V grade."""
    if isinstance(grade, int):
        value = grade
    else:
        text = str(grade).strip().upper()
        if text.startswith("V"):
            text = text[1:]
        if not text.isdigit():
            raise ValueError("not a V grade: %r" % (grade,))
        value = int(text)
    if value not in V_TO_FONT:
        raise ValueError("V grade out of range: %r" % (grade,))
    return value


def v_to_font(grade):
    return V_TO_FONT[parse_v(grade)]


def font_to_v(grade):
    key = str(grade).strip().upper()
    if key not in FONT_TO_V:
        raise ValueError("unknown Font grade: %r" % (grade,))
    return "V%d" % FONT_TO_V[key]


def _self_check():
    assert v_to_font("V0") == "4"
    assert v_to_font("v6") == "7A"
    assert v_to_font(10) == "7C+"
    assert font_to_v("7a+") == "V7"
    assert font_to_v("8A") == "V11"
    for v in V_TO_FONT:
        assert font_to_v(v_to_font(v)) == "V%d" % v
    for bad in ("V99", "X3", ""):
        try:
            v_to_font(bad)
        except ValueError:
            pass
        else:
            raise AssertionError("expected ValueError for %r" % bad)
    return True


if __name__ == "__main__":
    _self_check()
    print("grade_convert self-check OK")
