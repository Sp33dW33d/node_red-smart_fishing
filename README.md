# Smart Fishing

Smart Fishing is an IND4 assignment project built with Node-RED. It polls Open-Meteo weather and marine forecast APIs and ingests simulated MQTT sensor messages, validating and normalizing the data for downstream use. Phase 4 adds a FlowFuse Dashboard interface. Overview, Environment, and Water Conditions now show live values from Open-Meteo and simulated MQTT telemetry.

## Current status

- Weather and marine API flows run on startup and at the interval selected on the Overview dashboard (15 seconds, 30 seconds, 1 minute, 5 minutes, or 15 minutes; default 1 minute).
- Sensor display cadence is independent from API polling: the Overview defaults to forwarding every simulator message (about 5 seconds), while users can choose a slower display interval without changing MQTT ingestion. Compose starts the Python simulator automatically.
- A separate Python service maintains a local seven-day cache of weather and marine daily summaries in `cache/history-7d.json`. It fetches only dates and sources missing from the cache, trims dates outside the seven completed UTC-day window, and serves the cached metrics to dashboard history charts.
- Weather output contains air temperature, wind speed, and up to five daily rainfall forecast values.
- Marine output contains the nearest hourly sea-surface temperature, sea-level height relative to mean sea level, and wave height values available from the response.
- API, HTTP, and validation failures are formatted into error messages and sent to the Debug sidebar.
- Node-RED combines the latest weather and marine values into a fishing-conditions recommendation (`favorable`, `caution`, or `poor`) with a score, reasons, and catch-rate multiplier, then publishes it on `smartfishing/conditions`.
- The simulator subscribes to that recommendation and models catch events as a time-based process: favorable conditions increase the rate, caution reduces it, and poor conditions reduce it substantially. Telemetry includes the active recommendation status and multiplier.
- Phase 3.1–3.4 provide a Mosquitto broker, Python simulator, and Node-RED MQTT ingestion flow. A live simulator message has been received and normalized.
- The sample location is Sassoon Dock, Mumbai (`18.9110, 72.8253`). The Overview displays the configured location name and coordinates from `LOCATION_NAME`, `LOCATION_LATITUDE`, and `LOCATION_LONGITUDE`; the weather normalization node supplies these values to the dashboard. Coordinates represent a forecast grid location near the harbor, not a dockside sensor.
- FlowFuse Dashboard `1.34.1` provides Overview, Environment, and Water Conditions pages at `/dashboard/overview`, `/dashboard/environment`, and `/dashboard/water-conditions`. Overview includes API health/freshness indicators, a fishing-conditions recommendation with a dashboard-only preview override, and metric cards. Environment shows weather forecasts and seven-day history; Water Conditions shows marine forecasts, MQTT telemetry, one-hour sensor trends, a rolling 60-minute catches-per-hour chart, and seven-day marine history.

## Repository layout

```text
.
├── README.md
├── start-smart-fishing.bat
├── LICENSE
├── .env.example
├── compose.yaml
├── cache/
│   └── .gitkeep
├── flows/
│   └── smart-fishing.json
├── node-red/
│   ├── start.sh
│   ├── package-lock.json
│   ├── package.json
│   └── settings.js
├── mosquitto/
│   └── config/
│       └── mosquitto.conf
├── docs/
│   ├── project_specification.md
│   ├── system_architecture.md
│   ├── technology_stack.md
│   ├── implementation_plan.md
│   └── chatgpt_codex_directives.md
└── scripts/
    ├── Dockerfile.simulator
    ├── history-cache.py
    ├── simulate-mqtt.py
    └── requirements.txt
```

Node-RED's generated runtime configuration, credentials, and installed modules are stored under `node-red/` and ignored by Git where appropriate.

## Requirements

- Docker Engine with the Docker Compose v2 plugin.
- A working outbound HTTPS connection from the Node-RED container to Open-Meteo.
- A working outbound HTTPS connection from the history-cache container to Open-Meteo; the service uses Python 3.13's standard library and no additional Python packages.
- The Compose file pins `nodered/node-red:5.0.9`, matching the runtime used to verify the current flow.
- The MQTT service uses the official Eclipse Mosquitto image `2.1.2-alpine`.
- Compose builds the telemetry simulator with Python 3.13 and the pinned `paho-mqtt` dependency in `scripts/requirements.txt`; no host Python install is needed for the launcher.
- FlowFuse Dashboard `1.34.1` is pinned in `node-red/package.json`; it supports Node-RED `3.0+`, including this project’s `5.0.9` runtime.

No Open-Meteo API key is required for the configured forecast endpoints. Use coordinates appropriate to your forecast area; marine forecasts are model data and may not be available at every coordinate.

## Start the project

1. Copy the example environment file and replace the credential secret:

   ```sh
   cp .env.example .env
   ```

   On PowerShell, use `Copy-Item .env.example .env`.

2. Set `NODE_RED_CREDENTIAL_SECRET` in `.env` to a long, private value. Set `LOCATION_NAME`, `LOCATION_LATITUDE`, and `LOCATION_LONGITUDE` together for the desired location. Set `PORT` if local port `1880` is already occupied.

3. Start Node-RED:

   ```sh
   docker compose up -d --build
   ```

   The Node-RED container installs the pinned dashboard dependency from `node-red/package-lock.json` before starting the flows. On a fresh setup, allow a short time for this first install before opening the dashboard.

   On Windows with Docker running in WSL, double-click `start-smart-fishing.bat` to build/start the Compose services, including the MQTT simulator, keep the WSL Docker engine alive while the launcher is open, wait for the dashboard, and open the Node-RED editor and Overview dashboard in your default browser. Press `q` in the launcher terminal to stop the project containers and close it after the WSL keepalive exits.

4. Open the Node-RED editor at `http://localhost:<PORT>` (default `http://localhost:1880`) to inspect flows and Debug output. Open the dashboard at `http://localhost:<PORT>/dashboard/overview`; use the API polling selector to set weather/marine request frequency and the sensor display selector to control how often MQTT readings are forwarded to widgets. Forecast values may remain unchanged when the underlying model has not updated. The 15-second API setting makes two forecast requests every 15 seconds (11,520/day if left on continuously); use it only briefly because Open-Meteo's free limit is 10,000 calls per day. The Compose simulator supplies MQTT sensor readings automatically; check `docker compose logs --tail=50 telemetry-simulator` if they do not appear.

The `history-cache` Compose service populates `cache/history-7d.json` when a weather or marine date is missing, then checks hourly for newly available dates. It retains the seven completed UTC calendar days and fetches only missing source/date data. Node-RED reads the cache over the Compose-only `history-cache:8080/history` endpoint and refreshes the dashboard history charts every minute. Environment shows daily mean air temperature, maximum wind, and rainfall; Water Conditions shows daily mean sea-surface temperature, sea level, and wave height. The history charts display archived model output, not observations from physical harbor instruments. Cache files remain local runtime data and are ignored by Git.

The fishing-conditions recommendation is calculated from the latest weather and marine forecast values and reports a status, score out of 100, explanatory reasons, and catch-rate multiplier. The simulator consumes that MQTT recommendation to adjust its synthetic catch-arrival rate. The Overview manual preview lets users preview Favorable, Caution, and Poor presentation states; it changes only the dashboard display and does not publish or alter backend/simulator data. Overview API health cards report waiting, current, missing, request-failed, or stale states and show the last successful update where available.

5. Stop the container while retaining its runtime data:

   ```sh
   docker compose down
   ```

The service is bound to `127.0.0.1` by default. It is intended for local development and is not configured for public exposure or authenticated remote access.

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `PORT` | `1880` | Host port mapped to Node-RED's container port `1880`. |
| `TZ` | `Asia/Calcutta` | Container timezone. |
| `NODE_RED_CREDENTIAL_SECRET` | Required | Secret used by Node-RED to encrypt stored credentials. |
| `NODE_RED_FORCE_IPV4` | `true` | Prefer IPv4 for outbound HTTPS; set to `false` if the Docker host has working IPv6 routing. |
| `LOCATION_NAME` | `Sassoon Dock, Mumbai` | Name displayed for the configured forecast location. |
| `LOCATION_LATITUDE` | `18.9110` | Forecast latitude (Sassoon Dock sample). |
| `LOCATION_LONGITUDE` | `72.8253` | Forecast longitude (Sassoon Dock sample). |
| `WEATHER_API_URL` | Open-Meteo Forecast API | Weather endpoint. |
| `MARINE_API_URL` | Open-Meteo Marine API | Marine endpoint. |
| `HISTORY_CACHE_INTERVAL_SECONDS` | `3600` | How often the local cache checks for missing or newly available history dates. |
| `MQTT_PORT` | `1883` | Host port for the local Mosquitto listener, bound to loopback. |
| `MQTT_BROKER_HOST` | `mosquitto` | Compose service hostname for clients in the Compose network. |
| `MQTT_BROKER_PORT` | `1883` | Mosquitto listener port for Compose-network clients. |
| `MQTT_TOPIC_PREFIX` | `smartfishing` | Root topic for simulated telemetry. |
| `MQTT_DEVICE_ID` | `demo-01` | Device identifier used by the Compose telemetry simulator. |
| `MQTT_CONDITIONS_TOPIC` | `smartfishing/conditions` | Topic carrying Node-RED's fishing-conditions recommendation to the simulator. |

The broker currently allows anonymous MQTT connections for local assignment development. Its host port is bound to `127.0.0.1`; do not expose it publicly or reuse this authentication setting in a production deployment.

## MQTT telemetry simulator

The Phase 3.2 Python publisher runs as the `telemetry-simulator` Compose service and sends synthetic data to `<MQTT_TOPIC_PREFIX>/<MQTT_DEVICE_ID>/telemetry` (defaults: `smartfishing/demo-01/telemetry`) at QoS 1 without retaining messages. It connects to Mosquitto by the Compose hostname `mosquitto` and publishes every five seconds. The JSON payload includes a UTC timestamp, water temperature, water level, cumulative simulated catch count, active conditions status and catch-rate multiplier, and battery voltage. Catch arrivals use a time-based probability model adjusted by the latest fishing-conditions recommendation. Generated values are synthetic and for development only.

For a one-off manual publisher test, create a virtual environment, install the pinned dependency, and run ten messages from the repository root. Normal launcher use runs this publisher inside the Compose stack automatically.

On macOS/Linux:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r scripts/requirements.txt
python scripts/simulate-mqtt.py --host 127.0.0.1 --port 1883 --count 10
```

On PowerShell, use `py -m venv .venv`, ` .\.venv\Scripts\Activate.ps1`, then the same `pip install` and `python` commands. Use `--count 0` (the default) to publish until interrupted. Override `--host`, `--port`, `--topic-prefix`, or `--device-id` as needed; defaults target a broker published to loopback on port 1883. `MQTT_PUBLISHER_HOST`, `MQTT_PUBLISHER_PORT`, `MQTT_TOPIC_PREFIX`, and `MQTT_DEVICE_ID` may also be set in the shell environment.

The local `.env` file is ignored by Git. Keep secrets out of the flow export and other tracked files.

## Troubleshooting

- **Editor does not open:** Check `docker compose ps` and `docker compose logs --tail=100 node-red`. Confirm that the chosen host `PORT` is free.
- **No normalized API messages:** Open the Debug sidebar, then inspect container logs and configured coordinates. The marine model may not return data for every location.
- **HTTPS connection failures in WSL/Docker:** Keep `NODE_RED_FORCE_IPV4=true` when IPv6 resolves but is not routable from the container.
- **Dashboard page does not load:** Check `docker compose logs --tail=100 node-red` and confirm the Dashboard 2 package finished installing. Open `/dashboard/overview`, `/dashboard/environment`, or `/dashboard/water-conditions` under the configured host port. Weather and marine widgets wait for the API refresh, and MQTT widgets wait for simulator messages. The Overview polling section shows request failures, missing values, and stale API data.

## Data attribution and license

Weather and marine forecast data come from [Open-Meteo](https://open-meteo.com/). See the [Forecast API](https://open-meteo.com/en/docs) and [Marine API](https://open-meteo.com/en/docs/marine-weather-api) documentation for variables, model sources, attribution, and usage terms. Project code is distributed under the MIT License; see [LICENSE](LICENSE).
