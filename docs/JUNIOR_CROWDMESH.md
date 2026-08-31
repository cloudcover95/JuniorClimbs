# JuniorCrowdMesh + JuniorFieldBitNet

Decentralized, crowdsourced field intelligence that **lives on the device first**.
Not Mountain Project, not a hosted forum, not a cloud sync product.

## Forum model

| Piece | Behavior |
|-------|----------|
| **JuniorCrowdEnvelope** | One signed-style post (author, topic, body, optional GPS) |
| **Local store** | SQLite append-only — works at 0 bars |
| **Bundle** | JSON export/import for USB, SD, Meshtastic, AirDrop, sneakernet |
| **Peer merge** | Import is idempotent on `envelope_id` (content hash) |
| **No hub** | There is no JuniorCloud forum server required |

Topics: `beta` `conditions` `access` `overland` `nav` `general`

This is an open forum in the *protocol* sense: anyone with the app can write envelopes and trade bundles. It is not a public website you must reach.

## BitNet discipline (JuniorFieldBitNet)

Original ternary core aimed at StoneField + NavMesh — not the gym RFID loop.

Heads:
- **beta_trust** — is this envelope usable beta vs noise
- **access_caution** — private land / gate / closure language
- **tenure_hint** — usfs / blm / private / unknown from text+bbox context
- **nav_priority** — should this pin be a waypoint

Weights clamped to {-1, 0, +1}. Torch if present, deterministic hash fallback if not.

## Endpoints

- `GET/POST /crowd/envelopes`
- `GET /crowd/envelopes/{id}`
- `GET /crowd/bundle` — export all (or filtered) as JSON
- `POST /crowd/bundle` — merge a peer bundle
- `POST /crowd/score/{id}` — run JuniorFieldBitNet on one envelope
- `GET /fieldbitnet/status`
- `POST /fieldbitnet/infer` — raw text + optional geo
