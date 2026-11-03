# Technology Stack

This document records the implemented stack through Phase 5: Open-Meteo ingestion and history cache, MQTT simulation and ingestion, fishing-conditions recommendations, and the FlowFuse Dashboard.

## Implemented stack

| Component | Current choice | Use |
|---|---|---|
| Flow runtime | Node-RED `5.0.9` container image | Runs the exported flow; image tag is pinned in `compose.yaml`. |
| Runtime language | JavaScript in Node-RED Function nodes | Builds API requests and validates, normalizes, and routes data. Node.js comes from the base image. |
| Weather data | Open-Meteo Forecast API | Current air temperature and wind speed plus five daily rainfall forecast values. |
| Marine data | Open-Meteo Marine API | Hourly sea-surface temperature, sea level, and wave height. |
| Historical cache | Python `3.13.18` standard library | Maintains daily weather/marine summaries for seven completed UTC days in `cache/history-7d.json`; requests missing date/source ranges only. |
| Runtime configuration | Docker Compose and ignored `.env` | Provides location, API endpoints, timezone, credential secret, ports, MQTT settings, and cache interval. |
| MQTT broker | Eclipse Mosquitto `2.1.2-alpine` | Local broker with persistent state in a Docker named volume. |
| MQTT publisher | Python `3.13.18` and `paho-mqtt==2.1.0` | `telemetry-simulator` publishes synthetic sensor readings and weather-adjusted catch counts every five seconds. |
| Dashboard package | FlowFuse Dashboard `@flowfuse/node-red-dashboard` `1.34.1` | Pinned in `node-red/package.json` and `package-lock.json`. |
| Core flow nodes | Node-RED built-ins | Inject, Function, HTTP Request, MQTT In, Catch, Debug, and Link nodes. |
| Dashboard flow nodes | FlowFuse Dashboard 2 | Three pages, eleven groups, ten charts, eight gauges, eight text values, three dropdowns, one switch, three templates, and fourteen Markdown widgets. |

Dashboard chart count includes a five-day rainfall chart, two one-hour sensor charts, six seven-day history charts, and a rolling 60-minute catches-per-hour chart. Counts describe the current `flows/smart-fishing.json` export and may change as the UI evolves.

The dashboard pages are Overview, Environment, and Water Conditions. The Overview presents location details, API health/freshness status, independent API and sensor-display intervals, a fishing-condition recommendation, a dashboard-only preview control, and current metrics. Environment presents weather readings and seven-day weather history. Water Conditions presents marine readings, MQTT telemetry, sensor trends, catch rate, and seven-day marine history.

## Dependency installation

The Node-RED service starts through `node-red/start.sh`, which installs production dependencies from the pinned `node-red/package-lock.json` into the mounted `/data` directory before executing the Node-RED entrypoint. This supports fresh as well as existing runtime volumes. The simulator image installs its pinned client from `scripts/requirements.txt`. The history-cache service uses Python's standard library and has no third-party package requirements.

## Deployment details

- Docker Compose v2 is used; the Compose Specification does not require a legacy top-level `version` field.
- The Node-RED editor is published to loopback (`127.0.0.1`) on configurable host `PORT` and container port `1880`.
- Node-RED runtime state and flows use bind mounts under `node-red/` and `flows/`.
- The history cache uses a separate `./cache:/cache` bind mount; generated cache JSON is ignored by Git.
- Mosquitto configuration is mounted read-only, while broker state uses a named volume. The host listener is loopback-bound; anonymous access is for local assignment use only.
- `NODE_RED_FORCE_IPV4=true` configures Node.js HTTPS to prefer IPv4 for Docker/WSL networking.
- Open-Meteo requests use HTTPS and require no API key for the configured endpoints.
- The history-cache API listens on port 8080 inside the Compose network and is not exposed on a host port.

Runtime image and dependency versions are pinned in `compose.yaml`, `node-red/package.json`, `node-red/package-lock.json`, and `scripts/requirements.txt`.
