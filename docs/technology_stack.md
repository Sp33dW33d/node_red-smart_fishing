# Technology Stack

This document records the current Phase 2 implementation. Future components are listed separately and are not installed or deployed yet.

## Implemented stack

| Component | Current choice | Use |
|---|---|---|
| Flow runtime | Node-RED `5.0.9` container image | Runs the exported flow; image tag is pinned in `compose.yaml`. |
| Runtime language | JavaScript in Function nodes | Builds API URLs and validates/normalizes response objects. Node.js is supplied by the base image. |
| Weather data | Open-Meteo Forecast API | Current air temperature and wind speed, plus five daily rainfall values. |
| Marine data | Open-Meteo Marine API | Hourly sea-surface temperature, sea-level height, and wave height. |
| Runtime configuration | Docker Compose and `.env` | Provides location, endpoints, timezone, credential secret, and IPv4 setting. |
| Node types | Node-RED built-ins | Inject, Function, HTTP Request, Catch, and Debug. |

`node-red/package.json` has no additional npm node dependencies. The current flow has no MQTT broker nodes, dashboard nodes, or third-party chart widgets.

## Planned stack (not installed/configured yet)

| Component | Planned use | Phase |
|---|---|---|
| MQTT broker and Node-RED MQTT nodes | Sensor telemetry ingestion | 3 |
| Python MQTT publisher and its client dependency | Synthetic telemetry for development | 3 |
| Node-RED dashboard UI nodes | Overview, weather, and water condition screens | 4 |

Select and pin versions when planned dependencies are implemented. Draft dependency names and versions are not current requirements.

## Deployment details

- Docker Compose v2 is used; the Compose Specification does not require a legacy top-level `version` field.
- The Node-RED editor is published to loopback only (`127.0.0.1`) using configurable host `PORT` and container port `1880`.
- Flow, settings, and runtime data use bind mounts under `node-red/` and `flows/`.
- `NODE_RED_FORCE_IPV4=true` configures Node.js HTTPS to prefer IPv4 for the verified Docker/WSL networking case.
- Current Open-Meteo requests use HTTPS and require no project API key.
