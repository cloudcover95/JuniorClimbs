# JuniorNavMesh

Sovereign, offline-first navigation + land + overland + climbing GPS layer for JuniorClimbs / JuniorStoneField.

**No links to Google Maps, Apple Maps, onX, iOverlander, Mountain Project, or KAYA.**
Those products define the *capability set*. This module implements that set on-device.

## Capability map (what we own locally)

| Capability | Source pattern | Junior name |
|------------|----------------|-------------|
| Basemap + satellite + topo packs | GMaps / Apple / onX | **JuniorTilePack** |
| Place search + favorites | GMaps / Apple | **JuniorWaypointLedger** |
| Offline routing (waypoint chain) | GMaps / Apple | **JuniorTrackRibbon** + navigate |
| Public-land / private tenure | onX Backcountry | **JuniorLandLayer** |
| Off-road / forest roads / tracks | onX Offroad | **JuniorTrackRibbon** (class=offroad) |
| User camps / water / dump / trailheads | iOverlander | **JuniorOverlandNode** |
| Conditions + reviews on POIs | iOverlander | Overland notes + JuniorBetaBoard |
| Area → boulder → problem GPS | Mountain Project / KAYA | JuniorStoneField (existing) |
| Navigate-to-climb + approach | KAYA | **JuniorApproachPath** |
| Offline GPS unit / NMEA / GPX | Garmin-class IoT | **JuniorFixIoT** |

## Offline contract

1. All reads work with `JUNIOR_OFFLINE=1` (no network).
2. Tile packs live under `data/tiles/` as MBTiles or XYZ folders you load yourself (OSM / USGS / your own).
3. Land layers are local GeoJSON / bbox records — you ingest public cadastral / FS data; we do not fetch vendors.
4. GPS units speak NMEA or GPX files over USB/serial later; v1 stores last fix + GPX import/export.
5. No API keys. No outbound map SDKs.

## Device profile (van / M4 / handheld)

- Phone or laptop holds the SQLite atlas + tile packs.
- Handheld GPS or ESP32/GNSS module writes NMEA into JuniorFixIoT.
- BitNet IoT can later tag a send with the last fix.

## Endpoints

- `/nav/status` — offline mode, packs, last fix
- `/nav/packs` — tile packs
- `/nav/land` — tenure layers
- `/nav/overland` — camps / water / trailheads
- `/nav/waypoints`
- `/nav/tracks` + `/nav/tracks/{id}/gpx`
- `/nav/gpx/import`
- `/nav/iot/fix` — push a GNSS fix from a local device
- `/nav/iot/nmea` — parse one NMEA sentence
- `/nav/goto/node/{id}` — bearing + distance from last fix to a boulder
- `/nav/approach` — parking → node paths
