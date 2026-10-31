# System Architecture

## Current Phase 2 data path

```text
Docker Compose
└── Node-RED 5.0.9 (host 127.0.0.1:<PORT> → container 1880)
    ├── Weather: Inject (startup, every 15 min)
    │   → build Open-Meteo Forecast URL from environment
    │   → HTTP Request (JSON) → validate and normalize
    │   → Debug sidebar: normalized weather payload
    └── Marine: Inject (startup, every 15 min)
        → build Open-Meteo Marine URL from environment
        → HTTP Request (JSON) → validate and normalize
        → Debug sidebar: normalized marine payload

Weather and marine Catch nodes
    → format request/validation error → Debug sidebar
```

There is no MQTT broker, sensor publisher, dashboard UI, database, or external state store in the current deployment. The Node-RED editor is the inspection interface. `/ui` is not expected to exist until a dashboard phase implements it.

## Request and schedule behavior

- Both Inject nodes run shortly after deployment and every 900 seconds.
- Weather requests specify configured latitude/longitude, current `temperature_2m` and `wind_speed_10m`, daily `rain_sum`, five forecast days, automatic timezone, Celsius, and km/h.
- Marine requests specify configured latitude/longitude and hourly `sea_surface_temperature`, `sea_level_height_msl`, and `wave_height` for two forecast days.
- Endpoints and coordinates come from environment variables passed by `compose.yaml`.
- `NODE_RED_FORCE_IPV4` optionally sets the Node.js global HTTPS agent to IPv4 family 4; it is enabled by default for the verified Docker/WSL networking setup.

## Normalized output contracts

Weather uses `msg.topic = environment/weather` and a payload shaped as:

```json
{
  "source": "Open-Meteo Forecast API",
  "status": "OK",
  "fetchedAt": "ISO-8601 timestamp",
  "observedAt": "provider timestamp or null",
  "location": { "latitude": 18.911, "longitude": 72.8253 },
  "current": { "airTemperatureC": 30.7, "windSpeedKmh": 13.2 },
  "rainfallForecast": [{ "date": "YYYY-MM-DD", "rainfallMm": 0.0 }]
}
```

`rainfallForecast` contains up to five entries. `observedAt` is supplied by the provider; `fetchedAt` is assigned during normalization.

Marine uses `msg.topic = environment/marine` and a payload shaped as:

```json
{
  "source": "Open-Meteo Marine API",
  "status": "OK",
  "fetchedAt": "ISO-8601 timestamp",
  "location": { "latitude": 18.911, "longitude": 72.8253 },
  "current": {
    "waterTemperatureC": 30.1,
    "seaLevelHeightMslM": 0.58,
    "waveHeightM": 0.4
  },
  "sampleTimes": {
    "waterTemperature": "provider timestamp or null",
    "seaLevel": "provider timestamp or null",
    "waveHeight": "provider timestamp or null"
  }
}
```

The numeric values are examples from a verified run, not constants. For each marine variable, the flow selects the hourly value whose timestamp is nearest to normalization time. Marine status is `OK` when temperature and sea level are present, `PARTIAL` when at least one measurement exists but one of those two is missing. Missing measurements are `null`.

Errors use `msg.topic = environment/<source>/error` and include `source`, `status: ERROR`, `error`, and `failedAt`. `<source>` is `weather` or `marine` after request construction, and `environmental-api` if configuration fails before the source is set. Non-success HTTP responses, API error objects, missing required structures, invalid numeric values, and invalid location configuration are sent through the Catch/error path. Errors are visible in Debug; there is no dashboard or persistent error history yet.

## Later phases

Phase 3 adds MQTT ingestion; Phase 4 adds a dashboard. Their topic/payload contracts and UI wiring should be documented when implemented. Earlier draft examples are not active interfaces.
