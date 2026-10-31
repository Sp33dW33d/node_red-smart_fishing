# Technology Stack Reference

## Core Stack Components

| Technology | Category | Purpose | Version / Specifications |
|---|---|---|---|
| **Node-RED** | Application Platform | Flow-based programming & dashboard orchestration | `v3.0+` |
| **Node.js** | Runtime Environment | JavaScript runtime executing Node-RED core | `v18 LTS` or `v20 LTS` |
| **Mosquitto** | Messaging Broker | Lightweight MQTT Broker for sensor ingestion | `v2.0+` (Eclipse Mosquitto) |
| **Node-RED Dashboard** | UI Framework | Component library (`@node-red/node-red-dashboard`) | `v3.4+` |
| **Docker Compose** | Infrastructure | Container orchestration for reproducible deployment | Format Specification `3.8` / `Compose v2` |
| **Python** | Scripting | Simulator for MQTT sensor payload publishing | `v3.9+` (`paho-mqtt` dependency) |

---

## Node-RED Custom Nodes Dependencies (`node-red/package.json`)

```json
{
  "name": "smart-fishing-nodered",
  "version": "1.0.0",
  "description": "Custom node dependencies for Smart Fishing dashboard",
  "dependencies": {
    "node-red-dashboard": "^3.6.0",
    "node-red-node-rbe": "^0.5.0"
  }
}
```