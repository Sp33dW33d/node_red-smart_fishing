# Smart Fishing

Smart Fishing is an IND4 assignment project built with Node-RED. It polls Open-Meteo weather and marine forecast APIs and ingests simulated MQTT sensor messages, validating and normalizing the data for downstream use. Phase 4 adds a FlowFuse Dashboard interface. The Overview, Environment, and Water Conditions pages are built; live metrics are the next implementation step.

## Current status

- Two API flows run on startup and every 15 minutes.
- Weather output contains air temperature, wind speed, and up to five daily rainfall forecast values.
- Marine output contains the nearest hourly sea-surface temperature, sea-level height relative to mean sea level, and wave height values available from the response.
- API, HTTP, and validation failures are formatted into error messages and sent to the Debug sidebar.
- Phase 3.1–3.4 provide a Mosquitto broker, Python simulator, and Node-RED MQTT ingestion flow. A live simulator message has been received and normalized.
- The sample coordinates are Sassoon Dock, Colaba, Mumbai (`18.9110, 72.8253`). They are configurable and represent a forecast grid location near the harbor, not a dockside sensor.
- FlowFuse Dashboard `1.34.1` provides Overview, Environment, and Water Conditions pages at `/dashboard/overview`, `/dashboard/environment`, and `/dashboard/water-conditions`. The pages currently describe their intended data; live values and status indicators are pending Phase 4.3–4.4.

## Repository layout

```text
.
├── README.md
├── LICENSE
├── .env.example
├── compose.yaml
├── flows/
│   └── smart-fishing.json
├── node-red/
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
    ├── simulate-mqtt.py
    └── requirements.txt
```

Node-RED's generated runtime configuration, credentials, and installed modules are stored under `node-red/` and ignored by Git where appropriate.

## Requirements

- Docker Engine with the Docker Compose v2 plugin.
- A working outbound HTTPS connection from the Node-RED container to Open-Meteo.
- The Compose file pins `nodered/node-red:5.0.9`, matching the runtime used to verify the current flow.
- The MQTT service uses the official Eclipse Mosquitto image `2.1.2-alpine`.
- The telemetry publisher requires Python 3.10+ and the pinned `paho-mqtt` dependency in `scripts/requirements.txt`.
- FlowFuse Dashboard `1.34.1` is pinned in `node-red/package.json`; it supports Node-RED `3.0+`, including this project’s `5.0.9` runtime.

No Open-Meteo API key is required for the configured forecast endpoints. Use coordinates appropriate to your forecast area; marine forecasts are model data and may not be available at every coordinate.

## Start the project

1. Copy the example environment file and replace the credential secret:

   ```sh
   cp .env.example .env
   ```

   On PowerShell, use `Copy-Item .env.example .env`.

2. Set `NODE_RED_CREDENTIAL_SECRET` in `.env` to a long, private value. Set `LOCATION_LATITUDE` and `LOCATION_LONGITUDE` to the desired location if needed. Set `PORT` if local port `1880` is already occupied.

3. Start Node-RED:

   ```sh
   docker compose up -d
   ```

4. Open the Node-RED editor at `http://localhost:<PORT>` (default `http://localhost:1880`) to inspect flows and Debug output. Open the dashboard at `http://localhost:<PORT>/dashboard/overview`; use its navigation menu to switch between Overview, Environment, and Water Conditions. Live metric widgets will be connected in Phase 4.3. Both API flows trigger shortly after startup and repeat every 15 minutes.

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
| `LOCATION_LATITUDE` | `18.9110` | Forecast latitude (Sassoon Dock sample). |
| `LOCATION_LONGITUDE` | `72.8253` | Forecast longitude (Sassoon Dock sample). |
| `WEATHER_API_URL` | Open-Meteo Forecast API | Weather endpoint. |
| `MARINE_API_URL` | Open-Meteo Marine API | Marine endpoint. |
| `MQTT_PORT` | `1883` | Host port for the local Mosquitto listener, bound to loopback. |
| `MQTT_BROKER_HOST` | `mosquitto` | Compose service hostname for clients in the Compose network. |
| `MQTT_BROKER_PORT` | `1883` | Mosquitto listener port for Compose-network clients. |
| `MQTT_TOPIC_PREFIX` | `smartfishing` | Root topic for simulated telemetry. |

The broker currently allows anonymous MQTT connections for local assignment development. Its host port is bound to `127.0.0.1`; do not expose it publicly or reuse this authentication setting in a production deployment.

## MQTT telemetry simulator

The Phase 3.2 Python publisher sends synthetic data to `<MQTT_TOPIC_PREFIX>/<MQTT_DEVICE_ID>/telemetry` (defaults: `smartfishing/demo-01/telemetry`) at QoS 1 without retaining messages. The JSON payload includes a UTC timestamp, water temperature, water level, cumulative simulated catch count, and battery voltage. Generated values are for development only.

After starting the Compose broker, create a virtual environment, install the pinned dependency, and run ten messages from the repository root.

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
- **Dashboard page does not load:** Check `docker compose logs --tail=100 node-red` and confirm the Dashboard 2 package is installed. Open `/dashboard/overview`, `/dashboard/environment`, or `/dashboard/water-conditions` under the configured host port. The current pages are structure and intro text; live widgets are added in Phase 4.3–4.4.

## Data attribution and license

Weather and marine forecast data come from [Open-Meteo](https://open-meteo.com/). See the [Forecast API](https://open-meteo.com/en/docs) and [Marine API](https://open-meteo.com/en/docs/marine-weather-api) documentation for variables, model sources, attribution, and usage terms. Project code is distributed under the MIT License; see [LICENSE](LICENSE).
