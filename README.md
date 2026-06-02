# JuniorClimbs

**Edge-native, local-first climbing gym & coaching management platform.**

A sovereign, open-source system built for independent climbing gyms, routesetters, and coaches who want full data ownership, offline reliability, and powerful local intelligence.

JuniorClimbs combines deep athlete coaching tools, modern gym operations, rich route setting intelligence, community features, and spatial awareness into one unified local-first platform.

## Core Philosophy

- **Local-first & Sovereign** — Works completely offline. Your data stays yours.
- **Climbing-native** — Built from the ground up for bouldering and sport climbing gyms.
- **Setter-first intelligence** — Monthly planning, proactive recommendations, terrain projection, and optical analysis.
- **Low-power edge computing** — Runs efficiently on Apple Silicon and small clusters.
- **Community-powered** — Supports crowd-sourced routes and climber feedback.

## Key Capabilities

### Operations & Membership
- Member profiles and lifecycle management
- Digital waivers with e-signature
- Fast check-in (search, QR, hardware triggers)
- Point of Sale (POS) with inventory management
- Bookings, classes, and capacity tools
- Strong audit logging and exportable reports for compliance & taxes

### Coaching & Athlete Development
- Training plans and practice scheduling
- Detailed ascent logging (sends, attempts, style, notes)
- Progress tracking with grade history and volume analytics
- Personalized insights and recommendations

### Route Setting Intelligence (Standout Feature)
- Comprehensive route database (grade, color, sector, setter, dates, popularity)
- Monthly setting plans with historical tracking
- Proactive BitNet-powered recommendations (grade balance, rotation, style gaps)
- **Route Setting Sandbox** — Project and plan new problems virtually
- Whole-room terrain visualization and projection tools
- Optical analysis from photos, scans, or point clouds (hold identification, move types, beta suggestions)

### Spatial & Optical Tools
- Import scans from iPad LiDAR, drones, trail cams, or phone photos
- JuniorOmega integration for point clouds and AR overlays
- BitNet vision engine for:
  - Grade estimation from images
  - Move type detection (dyno, slab, compression, overhang)
  - Hold cluster identification
  - Auto-generated setter notes and beta suggestions

### Community Features
- Rich send logging and climber feedback
- Crowd-sourced route submissions via web dashboard
- New set awareness and engagement tools

### Hardware & Edge Integration
- **crispy-mouse** deterministic macros for setters (physical buttons → instant analysis)
- Local BitNet-mlx inference (runs entirely on-device)
- Support for multi-node Apple Silicon clusters

## Tech Stack

- **Backend**: Python + FastAPI + SQLAlchemy 2.0
- **Database**: SQLite (local) or PostgreSQL (production)
- **Intelligence**: BitNet-mlx (local 1.58-bit models)
- **Spatial**: JuniorOmega point cloud & AR integration
- **Frontend**: Modern local dashboard (expandable to Tauri/React)
- **Macros & Hardware**: crispy-mouse deterministic input layer

## Quick Start

```bash
git clone https://github.com/cloudcover95/JuniorClimbs.git
cd JuniorClimbs

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python backend/database.py
uvicorn backend.main:app --reload --port 8000