"""Static Alembic revision-graph check (no DB, no alembic import).

Parses alembic/versions/*.py for revision/down_revision, then reports
heads, roots and dangling parents. Exit 1 if >1 head or a dangling ref.
Usage: python3 scripts/alembic_heads.py
"""
from __future__ import annotations

import ast
import pathlib
import sys

VERS = pathlib.Path(__file__).resolve().parent.parent / "alembic" / "versions"


def _graph() -> dict[str, tuple]:
    g = {}
    for p in sorted(VERS.glob("*.py")):
        rev = down = None
        for n in ast.parse(p.read_text()).body:
            if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name):
                k = n.targets[0].id
                if k in ("revision", "down_revision"):
                    v = ast.literal_eval(n.value)
                    if k == "revision":
                        rev = v
                    else:
                        down = v
        if rev:
            downs = () if down is None else ((down,) if isinstance(down, str) else tuple(down))
            g[rev] = (downs, p.name)
    return g


def main() -> int:
    g = _graph()
    parents = {d for downs, _ in g.values() for d in downs}
    heads = sorted(r for r in g if r not in parents)
    roots = sorted(r for r, (d, _) in g.items() if not d)
    dangling = sorted({d for downs, _ in g.values() for d in downs if d not in g})
    print(f"revisions={len(g)} roots={roots} heads={heads} dangling={dangling}")
    if len(heads) > 1:
        print("multiple heads -> consider: alembic merge -m 'merge' " + " ".join(heads))
    return 1 if len(heads) > 1 or dangling else 0


if __name__ == "__main__":
    sys.exit(main())
