# Technology Stack

This document records the current Phase 2 API flow and seven-day history cache, Phase 3 MQTT broker/publisher/ingestion flow, and Phase 4 Dashboard 2 pages and live metrics. MQTT telemetry and Open-Meteo responses feed dashboard summary values, gauges, and charts.

## Implemented stack

| Component | Current choice | Use |
|---|---|---|
| Flow runtime | Node-RED `5.0.9` container image | Runs the exported flow; image tag is pinned in `compose.yaml`. |
| Runtime language | JavaScript in Function nodes | Builds API URLs and validates/normalizes response objects. Node.js is supplied by the base image. |
| Weather data | Open-Meteo Forecast API | Current air temperature and wind speed, plus five daily rainfall values. |
| Marine data | Open-Meteo Marine API | Hourly sea-surface temperature, sea-level height, and wave height. |
| Historical cache worker | Python `3.13.18` standard library | Maintains seven completed UTC days of weather and marine summaries in `cache/history-7d.json`; only missing date/source data are fetched. |
| Runtime configuration | Docker Compose and `.env` | Provides location, endpoints, timezone, credential secret, and IPv4 setting. |
| MQTT broker | Eclipse Mosquitto `2.1.2-alpine` | Phase 3.1 broker service; persistent state uses a Docker named volume. |
| MQTT publisher | Python `3.13.18` container and `paho-mqtt==2.1.0` | Compose `telemetry-simulator` service runs `scripts/simulate-mqtt.py` and publishes to Mosquitto every five seconds. |
| Dashboard UI package | FlowFuse Dashboard `@flowfuse/node-red-dashboard` `1.34.1` | Pinned in `node-red/package.json`; compatible with the selected Node-RED runtime. |
| Node types | Node-RED built-ins | Inject, Function, HTTP Request, MQTT In, Catch, and Debug. |
| Dashboard nodes | FlowFuse Dashboard 2 | One UI base/theme, three pages, ten groups, six Markdown widgets, eight gauges, eight text values, nine charts, and cross-tab Link nodes. |

MQTT In is supplied by the Node-RED core nodes. FlowFuse Dashboard is installed as a pinned Node-RED user dependency. Its Overview, Environment, and Water Conditions pages are in `flows/smart-fishing.json`. Live API data and MQTT simulator samples feed the text values, gauges, rainfall forecast chart, and sensor trend charts. The history-cache service exposes its local cache to Node-RED at `history-cache:8080/history`; six additional charts display seven-day weather and marine trends.

## Planned implementation

| Component | Planned use | Phase |
|---|---|---|
| Show error, missing-value, and stale-data states | Make data quality visible in the dashboard | 4.8 |

Select and pin versions when planned dependencies are implemented. Draft dependency names and versions are not current requirements.

## Deployment details

- Docker Compose v2 is used; the Compose Specification does not require a legacy top-level `version` field.
- The Node-RED editor is published to loopback only (`127.0.0.1`) using configurable host `PORT` and container port `1880`.
- Flow, settings, and runtime data use bind mounts under `node-red/` and `flows/`.
- Historical API summaries use a `./cache:/cache` bind mount, separate from Node-RED flow/runtime state; the generated JSON cache is ignored by Git.
- `NODE_RED_FORCE_IPV4=true` configures Node.js HTTPS to prefer IPv4 for the verified Docker/WSL networking case.
- Current Open-Meteo requests use HTTPS and require no project API key.
