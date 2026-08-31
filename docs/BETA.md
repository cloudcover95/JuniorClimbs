# JuniorStoneField live beta

Product space on JuniorClimbs. Offline-first. BitNet field core included.

## Run

```bash
python -m pip install -r requirements-beta.txt
export DATABASE_URL=sqlite:///./juniorclimbs.db
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Open:
- http://127.0.0.1:8000/stonefield/app
- http://127.0.0.1:8000/stonefield/health
- http://127.0.0.1:8000/stonefield/terms
- http://127.0.0.1:8000/sphere/view/1

## Verify without the web stack

```bash
PYTHONPATH=. python tests/test_stonefield_engines.py
PYTHONPATH=. python scripts/jsf_production_loop.py
PYTHONPATH=. python scripts/beta_health_probe.py
```

Expected seed after first boot: Red Feather Lakes, Flagstaff Mountain, Golden Front Range, Mt. Xanadu, JuniorHall + Summer camp week 1.
