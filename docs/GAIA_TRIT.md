# Gaia threads × trit unpack (live beta)

Domain-agnostic cores living in `core/`. Climbs is one **area label**, not the owner of the math.

Pollinated from JuniorPoker trit_felt, JuniorHome GAIA_SYS/GAIA_WIRE, JuniorLLM ports.gaia_proto.
Does not replace BitNet-mlx v88+ or StoneField.

Probe:

```
python scripts/gaia_trit_prod.py
python -m unittest tests.test_trit_unpack tests.test_gaia_threads
```

HTTP: GET /api/v1/gaia/status  POST /api/v1/gaia/handshake|pulse|compare|flip
