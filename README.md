# JuniorClimbs

**Open-Source, Edge-Native Local Management Software for Climbing Gyms**

JuniorClimbs is a sovereign, offline-first desktop application built for climbing gyms. As part of the JuniorCloudllc ecosystem, it delivers a complete, local management solution with no cloud dependency — everything runs on your hardware.

## Key Features

- **Point of Sale (POS)**: Fast presets for day passes, merch, food & drinks; custom sales; multiple payment methods including account balance top-ups.
- **Member Management**: Profiles, current balances, membership expiry tracking with warnings, auto-renewal logic, and quick top-ups.
- **Digital Waivers & Onboarding**: Secure liability waiver system with digital signature; seamless check-in for returning members and guided flow for new climbers.
- **Safety & Operations**: Real-time wall/area status management (open / restricted / closed), maintenance logging, and staff override controls.
- **Employee Scheduling**: Shift planning with built-in break rules (e.g., 8-hour shifts include 30-min lunch), legends, and notifications.
- **Events & Sponsorships**: Create and manage events, partner booths, incentives, and marketing deployments.
- **Intelligent Cognitive Layer**: Powered by BitNet ternary quantization and advanced plasticity models. Provides smart member insights, training recommendations, operational optimization, and self-improving signals.
- **Rich Reporting**: Daily revenue tracking, expiring memberships, activity logs, and cross-domain analysis ready for Obsidian second-brain integration.

## Why JuniorClimbs?

- **Fully Local & Sovereign**: No subscriptions, no data leaving your gym. Runs entirely offline on your machine or local network.
- **Edge-Native & Hardware Optimized**: Built for Apple Silicon (M-series) with efficient Metal/MPS performance. Ready for M5, Ultra, and future A-series mobile/edge devices.
- **Staff-Friendly**: Clean point-and-click desktop interface (Tauri + TypeScript) designed for real gym employees — no terminal required for daily use.
- **Intelligent but Lightweight**: AI features enhance daily operations without bloat or external API calls.
- **Production Beta Ready**: Designed for real-world in-gym testing and live deployment.

## Tech Stack

- **Desktop App**: Tauri (Rust core + TypeScript/React frontend)
- **Backend & Logic**: Python with modern frameworks
- **Database & Persistence**: Alembic migrations + high-density Parquet data lakes
- **AI & Cognitive**: Custom BitNet-mlx 1.58-bit ternary models, CognitiveBlackBox for plasticity & training signals, SVD manifold compression
- **Automation**: TOML-driven jobs, nightly consolidation & Obsidian export with knowledge graph links

## Getting Started

Clone the repo and follow the setup in `docs/` or run the desktop app directly. Full installation and configuration guides are available in the repository.

For production use, deploy via Docker or native binary on your gym's hardware.

## Roadmap & Vision

- Expand intelligent recommendations for personalized training plans and member engagement
- Deeper integration with JuniorHome for full ecosystem orchestration (POS + power telemetry + automation)
- Advanced topological kinematics and movement analysis in JuniorClimbs
- Cross-platform support and Linux beta for gym testing
- Sovereign node farm scaling across Apple Silicon clusters

JuniorClimbs is part of the broader JuniorCloudllc vision for edge-native, air-gapped, intelligent infrastructure.

## License

MIT License — free to use, modify, and distribute.

---

Built with ❤️ for the climbing community by JuniorCloudllc. Local. Sovereign. Intelligent.