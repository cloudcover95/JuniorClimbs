# JuniorSourceLedger

Open-source community pipeline for routes and boulders.
Crowd writes the project. The device stores it. License travels with the record.

## What we accept

A **JuniorSourceProject** is a JSON document you can put on a USB stick, a git repo, or ForumMesh gossip:

```json
{
  "format": "junior-source-v1",
  "license": "CC-BY-4.0",
  "attribution": "Name or handle",
  "project_name": "Flagstaff Crown community pack",
  "field_name": "Flagstaff Mountain",
  "nodes": [{"name": "Crown Rock", "lat": 40.0018, "lon": -105.2965, "rock_type": "sandstone"}],
  "problems": [{"node_name": "Crown Rock", "name": "example line", "grade": "V3", "style": "boulder", "description": "community beta you own"}],
  "notes": "optional"
}
```

Licenses allowed on ingest: `CC0-1.0`, `CC-BY-4.0`, `CC-BY-SA-4.0`, `public-domain`.
Anything else is stored as a *pointer* only (we do not copy closed beta).

## What we will not do

- Scrape Mountain Project, KAYA, 27crags, or commercial guides
- Import copyrighted topos without an explicit license field
- Link those products as the source of truth

Public *area names + GPS centroids* in seeds are facts. Line-by-line beta belongs to the people who license it here.

## Endpoints

- `POST /source/projects` — register a project metadata row
- `POST /source/import` — ingest a junior-source-v1 document
- `GET /source/projects`
- `GET /source/export?field_id=` — dump local nodes/problems as CC-BY bundle
- `GET /source/schema` — the document contract
