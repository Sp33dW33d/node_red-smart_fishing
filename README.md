# Smart Fishing

Smart Fishing is an IND4 assignment project built with Node-RED. The current implementation is the Phase 2 environmental ingestion pipeline: it polls Open-Meteo weather and marine forecast APIs, validates and normalizes each response, and sends the results to Node-RED's Debug sidebar.

## Current status

- Two API flows run on startup and every 15 minutes.
- Weather output contains air temperature, wind speed, and up to five daily rainfall forecast values.
- Marine output contains the nearest hourly sea-surface temperature, sea-level height relative to mean sea level, and wave height values available from the response.
- API, HTTP, and validation failures are formatted into error messages and sent to the Debug sidebar.
- The sample coordinates are Sassoon Dock, Colaba, Mumbai (`18.9110, 72.8253`). They are configurable and represent a forecast grid location near the harbor, not a dockside sensor.
- MQTT ingestion and a user-facing dashboard are planned phases and are not implemented yet. The `/ui` path is not available in the current flow.

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
├── docs/
│   ├── project_specification.md
│   ├── system_architecture.md
│   ├── technology_stack.md
│   ├── implementation_plan.md
│   └── chatgpt_codex_directives.md
└── scripts/
    └── simulate-mqtt.py  # Phase 3 placeholder
```

Node-RED's generated runtime configuration, credentials, and installed modules are stored under `node-red/` and ignored by Git where appropriate.

## Requirements

- Docker Engine with the Docker Compose v2 plugin.
- A working outbound HTTPS connection from the Node-RED container to Open-Meteo.
- The Compose file pins `nodered/node-red:5.0.9`, matching the runtime used to verify the current flow.

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

4. Open `http://localhost:<PORT>` (default `http://localhost:1880`). Open the **Environment Ingestion** tab and select the Debug sidebar to inspect normalized weather, marine, or error payloads. Both API flows trigger shortly after startup and repeat every 15 minutes.

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

The local `.env` file is ignored by Git. Keep secrets out of the flow export and other tracked files.

## Troubleshooting

- **Editor does not open:** Check `docker compose ps` and `docker compose logs --tail=100 node-red`. Confirm that the chosen host `PORT` is free.
- **No normalized API messages:** Open the Debug sidebar, then inspect container logs and configured coordinates. The marine model may not return data for every location.
- **HTTPS connection failures in WSL/Docker:** Keep `NODE_RED_FORCE_IPV4=true` when IPv6 resolves but is not routable from the container.
- **A dashboard at `/ui` is missing:** This is expected until the dashboard phase adds dashboard nodes and an implemented UI flow.

## Data attribution and license

Weather and marine forecast data come from [Open-Meteo](https://open-meteo.com/). See the [Forecast API](https://open-meteo.com/en/docs) and [Marine API](https://open-meteo.com/en/docs/marine-weather-api) documentation for variables, model sources, attribution, and usage terms. Project code is distributed under the MIT License; see [LICENSE](LICENSE).
