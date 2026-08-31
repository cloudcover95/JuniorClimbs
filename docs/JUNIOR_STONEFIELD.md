# JuniorStoneField

Community outdoor + gym boulder layer for JuniorClimbs.
**Additive.** Existing POS / coaching / BitNet IoT / SpatialTernaryAutomata are unchanged.

## Why this exists
A shared Grok thread on Red Feather Lakes Boulders GPS pointed at the capabilities of:
- Mountain Project (area tree, GPS, classic problems, user photos)
- KAYA (GPS nav, verified topos, beta, ascents, offline maps)
- Fixed Pin guidebook structure (area → subarea → boulder → problem)

JuniorStoneField brings those *capabilities* in-house, offline-first, under JuniorCloud naming — without scraping or replacing those products.

## Naming (original Junior conventions)

| Name | Role |
|------|------|
| **JuniorStoneField** | Geographic field / area (e.g. Red Feather Lakes) |
| **JuniorBoulderNode** | Individual boulder with GPS |
| **JuniorProblem** | Named line / grade / style |
| **JuniorTopoMesh** | Photo / topo / route-set overlay |
| **JuniorRouteSetLedger** | Indoor gym route-set OR outdoor first-ascent ledger |
| **JuniorBetaBoard** | Discussion / beta / conditions thread per node or problem |
| **JuniorSendLog** | Local ascent log (ties into BitNet IoT later) |

## Architecture

```
Request
  → FastAPI routers/stonefield.py
  → SQLite / Alembic models (additive tables)
  → JuniorTopoMesh local media (./data/topos)
  → Optional Enhanced TDA / SpatialTernaryAutomata for hold topology later
  → JuniorBetaBoard threads
```

## Seed field
Red Feather Lakes, CO — GPS 40.80154, -105.59009 (public Mountain Project area centroid).
Sub-areas seeded as *names + GPS only* (public facts): Creedmore Lakes Road, Boy Scout Road Areas, Sky Prairie / Top Notch, Swallow Crags.

## Endpoints
- `GET/POST /stonefield/fields`
- `GET/POST /stonefield/nodes`
- `GET/POST /stonefield/problems`
- `GET/POST /stonefield/topos`
- `GET/POST /stonefield/routesets`
- `GET/POST /stonefield/board`  (JuniorBetaBoard)
- `GET /stonefield/red-feather` (seeded overview)

Local-first. No third-party API keys required.
