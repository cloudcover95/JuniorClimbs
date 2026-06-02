# JuniorClimbs
edge native local management open source software
# JuniorClimbs

**Edge-native, local-first climbing gym & coaching management platform**  
Sovereign open-source powerhouse combining the best of JuniorCoach + Rock Gym Pro + Clava + **KAYA** + **Join It** membership power.

> Local-first. Coaching-first. Route-setting intelligent. Spatially aware. Community-powered.

JuniorClimbs is the **sovereign, edge-native** evolution of climbing gym software. It cross-pollinates **every major feature** from:

- **JuniorCoach** — deep coaching, athlete tracking, training plans, rosters, progress
- **Rock Gym Pro** — waivers, memberships, POS, fast check-in, bookings, analytics
- **Clava** — modern climbing-gym UX, multisite thinking, strong operational tools
- **KAYA (the climber’s app)** — beta videos, community logging/ratings/feedback, new set notifications, progress tracking, setter analytics
- **Join It** — robust membership management, recurring billing concepts, automated workflows, self-service, auditing & reporting foundation

**Plus unique superpowers**:
- Full **Route Setting Sandbox** with monthly planning, historical tracking + proactive/future-pushing recommendations
- **Whole-room boulder views** and terrain projection sandbox (via JuniorOmega spatial + visualization)
- **Crowd-sourced route submissions** via clean web dashboard (HTML port, hostable on your .brave domain)
- **BitNet-powered on-device intelligence** for smart recommendations and planning
- Deep integration with **JuniorOmega** (spatial LiDAR/ARKit point clouds, AR, fabrication) and **crispy-mouse** (deterministic PIO input & macros)
- Production-grade **PostgreSQL** backend for auditing, taxes, complex reporting & efficiency
- Hybrid **Python (core) + Node.js (services/web)** architecture

Built for independent gyms, routesetters, coaches, and communities who want **full data ownership**, offline reliability, low-power edge deployment, and AI that runs locally.

**JuniorCloud LLC** • MIT License • Python-first + Node.js + PostgreSQL • Edge Native

## Why JuniorClimbs Now?

Traditional tools force you into the cloud. KAYA is great for climbers but limited for full gym ops. Rock Gym Pro and Clava are powerful but cloud/SaaS. Join It excels at memberships but isn't climbing-native.

**JuniorClimbs gives you everything in one sovereign, local-first system** — with climbing-specific depth, route setter superpowers, spatial awareness, community features (KAYA-style), and strong membership/audit tools (Join It-style) — all running on your hardware with optional sovereign federation.

## Core Philosophy & Stack

- **Python best foot forward** — FastAPI + SQLAlchemy core (clean, fast, ecosystem-friendly)
- **PostgreSQL** for production (auditing triggers, JSONB for flexible climbing data, powerful reporting/tax exports, complex queries)
- **Node.js** for complementary services (real-time web dashboard, crowd-sourced submissions, potential Socket.io live updates for setters)
- **BitNet-mlx** (ternary 1.58-bit) hooks for on-device intelligence without heavy GPUs
- **JuniorOmega** integration for spatial point clouds, whole-room visualization, AR route projection, and fabrication pipelines
- **crispy-mouse** for deterministic input, kiosk macros, and low-latency hardware triggers
- Local-first by default. Optional sovereign multi-node sync via Junior ecosystem patterns.

## Major Feature Areas (Fully Cross-Pollinated + Enhanced)

### 1. Membership & Operations Power (Rock Gym Pro + Clava + Join It)
- Rich member profiles + membership lifecycle
- Digital waivers with e-signature + archival
- Fast multi-method check-in (QR, search, hardware via crispy-mouse)
- Full POS + inventory
- Bookings, classes, events, capacity management
- **Join It-style**: Self-service portal concepts, recurring membership logic, automated reminders (local), digital cards, strong audit logging for compliance/taxes

### 2. Coaching & Athlete Development (JuniorCoach + KAYA progress)
- Training plans, rosters, practice planning
- Detailed progress tracking with grade history, volume, style balance
- **KAYA-style logging**: Sends + attempts + beta notes + ratings + (future) beta video links
- Community feedback loop on climbs

### 3. Route Setting Intelligence & Sandbox (Unique + KAYA setter tools)
- Comprehensive **Route** model (grade, color, sector, setter, set/removal dates, hold types, popularity, feedback)
- **Monthly Route Setting Plans** — plan sets historically and proactively push future sets
- Historical tracking of what was set when + performance data (sends, ratings, feedback)
- **Proactive recommendations** (BitNet-powered): "Balance grades this month", "Add more V4-V6 overhangs based on member data", "Rotate these popular problems"
- **Route Setting Sandbox**:
  - Project new terrains and route concepts in a virtual sandbox
  - Whole-room boulder gym visualization (dashboard views)
  - Integration points for JuniorOmega point clouds (import real gym scans)
  - Planning tools for setters with G-code/fabrication hooks (via JuniorOmega)

### 4. Spatial & Visualization Layer (JuniorOmega powered)
- Whole-room boulder views in the dashboard
- Project/preview new route terrains and layouts in sandbox mode
- Future: AR overlays on iPad (JuniorOmega LiDAR + ARKit)
- Point cloud ingestion for accurate gym digital twins

### 5. Community & Crowd-Sourcing (KAYA-inspired + self-hosted)
- Climbers can log sends with rich data (beta, rating, style)
- **Crowd-sourced route submissions** via dedicated web dashboard (HTML/JS port)
- New set notifications (local or push when federated)
- Beta video / photo upload support (local storage)
- Setter analytics: Which problems get the most love? What grades/styles are underserved?

### 6. Auditing, Taxes, Reporting & Efficiency (Join It + PostgreSQL strength)
- Full audit logging on sensitive actions
- Membership billing history + export-ready data for taxes
- Advanced reporting: Revenue, setter performance, route utilization, tax-friendly summaries

### 7. On-Device Intelligence (BitNet + Junior ecosystem)
- Local recommendations for training plans, next routes, and monthly setting balance
- Deterministic automation via crispy-mouse macros

## Tech Stack Details

**Core Backend (Python)**
- FastAPI + Uvicorn
- SQLAlchemy 2.0 (PostgreSQL recommended for prod; SQLite for pure local dev)
- Pydantic
- Alembic for migrations

**Intelligence**
- BitNet-mlx integration points for local LLM-style recommendations

**Spatial & Hardware**
- JuniorOmega: Point cloud ingestion, spatial math, ARKit pipelines
- crispy-mouse: PIO input, deterministic macros, kiosk/automation layer

## Quick Start

```bash
git clone https://github.com/cloudcover95/JuniorClimbs.git
cd JuniorClimbs

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python backend/database.py
uvicorn backend.main:app --reload --port 8000