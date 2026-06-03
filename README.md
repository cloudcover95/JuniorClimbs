# README.md
# JuniorClimbs

**Edge-native local-first coaching + climbing gym POS platform**  
*(Built under JuniorCloud LLC — enterprise Linux-first package for Mac Minis & Windows with NVIDIA AI chips)*

Zero-terminal, offline-first, BitNet-powered (1.58-bit LLM) for gyms. Designed to obsolete legacy systems with deterministic local compute.

## Production Quick Start (Linux recommended first)

```bash
git clone https://github.com/cloudcover95/JuniorClimbs.git
cd JuniorClimbs
docker compose up -d --build
# or native: pip install -e ".[dev]" && alembic upgrade head && python -m backend.main
**Edge-native local-first coaching + climbing gym POS platform**  
*(Built under JuniorCloudllc)*

Zero-terminal, offline-first, BitNet-powered (1-bit LLM) for gyms and junior coaching orgs.

## Quick Start (MacBook Air M4)

```bash
cd /Users/nico/Documents/JuniorCloud/JuniorClimbs
python3 -m backend.main
Coach login: coach / juniorclimbs2026
Full OpenAPI: http://localhost:8000/docs
Features

Coaching Suite: Athletes + Practices
POS Domain: Day Pass, Chalk, Shoes with UUID offline ledger
BitNet IoT: RFID ascent logging + camera hold-wear prediction (local only)
Clean Architecture ready for Tauri desktop + automerge CRDT

Location: /Users/nico/Documents/JuniorCloud/JuniorClimbs
Built for MacBook Air M4. Local-first. Always on.
