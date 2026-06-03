# JuniorClimbs

**Multi-Modal Performance Imaging & Extraneous Sensing System**

JuniorClimbs is evolving into a sovereign, edge-native platform for **room-scale multi-optical imaging** and **WiFi CSI movement tracking**, focused on high-performance sports analytics and human movement understanding.

It serves as the vision and spatial sensing layer for the JuniorCloud LLC stack, feeding rich environmental and biometric data into reasoning engines (BitNet-mlx) and deterministic execution layers (crispy-mouse).

## New Direction: Extraneous Imaging

- Multi-camera / multi-LiDAR room mapping
- WiFi CSI-based non-visual movement and presence detection
- Sensor fusion across optical and RF modalities
- Designed for real-time sports performance analysis and AI coaching systems

## Architecture

```text
Optical Sensors (Cameras, LiDAR, TrueDepth)
          ↓
    MultiOpticalFusion (crispy-mouse)
          ↓
WiFi CSI Tracker (room movement)
          ↓
SpatialSensingPipeline (BitNet-mlx)
          ↓
JuniorAGI / JuniorMemSys (memory)
          ↓
JuniorStock / crispy-mouse (action)
```

## Integration with JuniorCloud LLC

| Component       | Role                                      |
|-----------------|-------------------------------------------|
| **crispy-mouse**| Multi-optical fusion + WiFi CSI input layer |
| **BitNet-mlx**  | Converts spatial data into reasoning state  |
| **JuniorAGI_SDK** | Long-term memory of movement patterns    |
| **JuniorHome**  | Orchestration of the full sensing stack     |

## Technical Goals

- Edge-first (Apple Silicon + embedded)
- Low write amplification
- Deterministic output where possible
- Clean black-box interfaces for sensor drivers

Part of building a complete sovereign spatial computing and performance intelligence stack.