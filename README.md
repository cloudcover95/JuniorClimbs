# JuniorClimbs

**Open-Source, Edge-Native Local Management Software for Climbing Gyms with Spatial Kinematics & AI**

JuniorClimbs is a sovereign, offline-first desktop application for climbing gyms, now enhanced with advanced spatial/kinematic intelligence. Part of the JuniorCloudllc ecosystem for edge-native sovereign compute.

## Core Features

- **Spatial & Kinematic Intelligence**: New `SpatialTernaryAutomata` module ingests LiDAR/point-cloud scans via Parquet, applies SVD manifold compression ($A = U \Sigma V^T$), and maps to 1.58b ternary logic for topological hold analysis and movement tracking.
- **Point of Sale (POS)**, Member Management, Digital Waivers, Safety Zones, Employee Scheduling, Events (as before).
- **Cognitive/AI Layer**: BitNet ternary quantization, plasticity training signals, Neural Engine routing for power-efficient inference.
- **Data Architecture**: Strict Zero-Trust (02_Assets isolation), high-density Parquet lakes, TOML-driven automation, Obsidian knowledge graph export with cross-domain links (member behavior ↔ market regimes / climbing kinematics).

## New in This Update (Ecosystem Sandbox Correction)

- Root node failures in Tauri IPC and raw mesh processing resolved by direct Parquet ingestion + SVD compression before ternary quantization.
- Prevents Metal OOM on high-density spatial data.
- Enables autonomous spatial updates and kinematic dampening integration (future merge with crispy-mouse).

## Tech Stack

- Tauri (Rust + TS/React)
- Python + mlx.core for spatial automata and AI
- PyArrow/Parquet for data lakes
- Zero-trust isolation (01_Legal vs 02_Assets)

## Getting Started

See core/spatial_automata.py for the new module. Run the test pipeline to validate.

Full setup in previous README sections remains valid.

## Roadmap

- Integrate with crispy-mouse for kinematic dampening overlay
- Autonomous agent loops for unsupervised gym geometry updates
- Cross-repo inference (apply spatial methods to JuniorQuant telemetry)
- M5/Ultra/ANE optimization via new hardware backend

MIT License. Local. Sovereign. Intelligent.