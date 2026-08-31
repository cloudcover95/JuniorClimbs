# JuniorForumMesh + JuniorBitNetFieldCore

Crowdsourced climbing / overland knowledge that stays on the device.
Looks like an open forum. Stores like a local ledger. Syncs like a mesh — not a cloud.

## Is it a decentralized open forum?

Yes, with an offline-first contract:

- Anyone can post beta, conditions, access, camps, GPS pins, photos (paths), grades.
- Every post is an append-only **JuniorCrowdEvent** with a content hash.
- The node is the store. No account vendor. No live feed requirement.
- When two devices meet (USB, local Wi-Fi, sneakernet file), they exchange a **JuniorGossipBundle**.
- Merge is idempotent: same `event_id` is skipped. Newer edits are new events, not silent overwrites.
- BitNet scores incoming crowd text *on device* before you treat it as trusted.

Not a link to Mountain Project / KAYA / Reddit / iOverlander. Same social pattern, local ownership.

## Offline store

```
data/forum/
  events.jsonl          # append-only log (also mirrored in SQLite)
  bundles/              # exported gossip files for other nodes
```

`JUNIOR_OFFLINE=1` remains default. Gossip import is the only sync path.

## JuniorBitNetFieldCore (original ecosystem BitNet)

Discipline-specific 1.58-bit ternary engine for StoneField + NavMesh:

| Head | Job |
|------|-----|
| **TrustDrift** | Disagreement / confidence on a crowd claim |
| **ConditionHead** | dry / seeping / icy / wind / fire-restriction-ish language |
| **AccessHead** | open / caution / private / closed language |
| **GradeVote** | map free text + V/YDS tokens toward a compact grade bin |
| **TernaryEmbed** | 32-dim {-1,0,1} fingerprint of a report for similarity / dedupe |

Torch when present (same spirit as BitNetIoT TinyQuantizedBitNet). Pure-Python ternary fallback otherwise — van / M4 / no lab.

## Endpoints

- `GET/POST /forum/events`
- `GET /forum/thread?node_id=&kind=`
- `GET /forum/bundle/export`
- `POST /forum/bundle/import`
- `POST /forum/score` — run BitNetFieldCore on text
- `GET /bitnet-field/status`
