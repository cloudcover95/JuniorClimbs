# JuniorRegionSphere

Viewing layer for JuniorStoneField / JuniorNavMesh.
Capability pattern (not a clone, no Niantic/Pokémon assets):
central **arenas** in a region, tap one, stand inside a **360° sphere** of that field,
hotspots on walls/boulders, select one → bearing + problems + beta + AR lock.

## Names

| Name | Role |
|------|------|
| **JuniorArenaNode** | Central “gym” of a sub-region (trailhead / parking / obvious gathering rock) |
| **JuniorRegionSphere** | One 360° (or cubemap) wrap of photos around an arena |
| **JuniorSphereHotspot** | A boulder/wall painted onto the sphere at yaw/pitch |
| **JuniorLookFrame** | Current device heading + GPS → which hotspot you are facing |
| **JuniorLookAR** | 2D canvas or WebXR / device-orientation overlay |

## Experience

1. Map (2D NavMesh) shows ArenaNodes like gyms — only at *central* spots, not every rock.
2. Open an arena → RegionSphere viewer (`/sphere/view/{id}`).
3. Drag or use compass. Hotspots sit at true bearings from the arena GPS.
4. Select a hotspot → name, distance, compass, problems, last ForumMesh trust, NavMesh goto.
5. Flip **AR**: phone heading + GNSS drives the same hotspots over the camera (or a 2D stand-in if no sensor).

## BitNet

JuniorBitNetFieldCore ternary embed + a heading-lock head:
`look_lock(heading, hotspots)` returns the hotspot whose yaw is closest, with a ternary confidence so noisy compass does not flip walls.

## Offline

Sphere images live under `data/spheres/{id}/` (equirect or 6-face). No street-view vendor. You own the photos.

## Endpoints

- `/arena/` `/arena/{id}`
- `/sphere/{id}` `/sphere/{id}/look?heading=`
- `/sphere/{id}/ar` — AR payload
- `/sphere/view/{id}` — 2D+AR HTML viewer
