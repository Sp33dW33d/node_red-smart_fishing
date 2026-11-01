# System Architecture

## Current stack (Phase 2 API flow and history cache, Phase 3 MQTT path, Phase 4.3 live dashboard)

```text
Docker Compose
├── Node-RED 5.0.9 (host 127.0.0.1:<PORT> → container 1880)
│   ├── Weather and marine API flows → normalized values/errors → Debug and Dashboard
│   ├── MQTT In → validate and normalize sensor telemetry/errors → Debug and Dashboard
│   └── FlowFuse Dashboard 2 → Overview, Environment, Water Conditions pages
├── History cache (Python 3.13 standard library)
│   └── Open-Meteo history on cache miss → ./cache/history-7d.json (seven completed UTC days)
└── Mosquitto 2.1.2 (host 127.0.0.1:<MQTT_PORT> → container 1883)
    └── persistent broker state (Docker named volume)

Python telemetry simulator (host process)
└── MQTT QoS 1 publish → <MQTT_TOPIC_PREFIX>/<device_id>/telemetry
    └── Mosquitto (localhost:<MQTT_PORT>)
```

The Mosquitto listener is reachable to Compose services as `mosquitto:1883` and is published to the host on loopback only. Anonymous MQTT access is enabled for local assignment development. FlowFuse Dashboard 2.0 serves the Overview, Environment, and Water Conditions pages at `/dashboard/overview`, `/dashboard/environment`, and `/dashboard/water-conditions`. The Overview page has a shared update-frequency selector (15 seconds, 30 seconds, 1 minute, 5 minutes, or 15 minutes; default 1 minute). Its scheduler refreshes weather and marine requests and throttles sensor messages sent to dashboard widgets. The MQTT simulator itself remains a separate process and must be running to provide sensor data. Dashboard Link nodes bridge the source flow tab to the dashboard tab. The Environment page separates the weather header, weather gauges, and rainfall chart within the forecast display. The Water Conditions page has a separate introduction, a Marine forecast panel with three gauges, a Sensor telemetry readings panel, and a Sensor trends panel containing the water-temperature and water-level charts. Weather feeds the air-temperature and wind gauges, overview values, rainfall bar chart, and rainfall total. Marine feeds sea-temperature, sea-level, and wave-height gauges plus overview values. MQTT telemetry feeds sensor gauges, catch-count summaries, and one-hour trend charts. Missing-value, stale-data, and API-error states are planned for Phase 4.4.

The Phase 3.2 host-side publisher uses `paho-mqtt==2.1.0`. By default it publishes to `smartfishing/demo-01/telemetry` every five seconds with QoS 1 and no retained message. Each JSON payload contains `device_id`, a UTC `timestamp`, `water_temperature_c`, `water_level_m`, cumulative `catch_count`, and `battery_voltage_v`. All values are synthetic.

The Node-RED MQTT In node subscribes at QoS 1 to `${MQTT_TOPIC_PREFIX}/+/telemetry` and parses JSON. Its Function node requires a non-empty device ID, parseable timestamp, finite numeric measurements, and a non-negative integer catch count. Valid messages use `msg.topic = sensor/telemetry/<device_id>` and a normalized payload with `source`, `status`, `deviceId`, `observedAt`, `receivedAt`, `waterTemperatureC`, `waterLevelM`, `catchCount`, and `batteryVoltageV`. MQTT JSON parse/validation errors are tagged `source: mqtt` and routed to the shared ingestion error output.

Weather and marine paths are Inject → request builder → HTTP Request → validation/normalization → Debug. Their Catch nodes format failures for Debug.

## Rolling API history cache

The Compose `history-cache` service stores daily Open-Meteo Forecast API and Marine API summaries in `cache/history-7d.json`. It maintains the seven completed UTC calendar days in ascending date order. At each hourly check it removes expired dates, requests only a missing date/source range, merges successful results, and leaves cached weather or marine data intact if the other API is unavailable. A location or schema change invalidates the previous cache. Cached weather and marine values are summaries of archived model forecasts, not measured harbor observations. The cache is prepared for future dashboard use and is not wired to UI widgets.

Weather records contain daily mean/min/max air temperature, maximum wind speed, rain, and precipitation. Marine records aggregate hourly sea-surface temperature, mean-sea-level height, and wave height into per-day mean/min/max/sample counts. UTC is used consistently for the cache keys.

## Request and schedule behavior

- Both Inject nodes run shortly after deployment. The Overview scheduler then refreshes both APIs at the selected dashboard interval (default 60 seconds) and triggers an immediate fetch whenever the selection changes.
- Weather requests specify configured latitude/longitude, current `temperature_2m` and `wind_speed_10m`, daily `rain_sum`, five forecast days, automatic timezone, Celsius, and km/h.
- Marine requests specify configured latitude/longitude and hourly `sea_surface_temperature`, `sea_level_height_msl`, and `wave_height` for two forecast days.
- Endpoints, location name, and coordinates come from environment variables passed by `compose.yaml`. The normalized weather location object feeds the Overview introduction, so the displayed name and coordinates follow `LOCATION_NAME`, `LOCATION_LATITUDE`, and `LOCATION_LONGITUDE`; the linked weather-normalization flow is the backend source.
- `NODE_RED_FORCE_IPV4` optionally sets the Node.js global HTTPS agent to IPv4 family 4; it is enabled by default for the verified Docker/WSL networking setup.

## Normalized output contracts

Weather uses `msg.topic = environment/weather` and a payload shaped as:

```json
{
  "source": "Open-Meteo Forecast API",
  "status": "OK",
  "fetchedAt": "ISO-8601 timestamp",
  "observedAt": "provider timestamp or null",
  "location": { "name": "Sassoon Dock, Mumbai", "latitude": 18.911, "longitude": 72.8253 },
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
  "location": { "name": "Sassoon Dock, Mumbai", "latitude": 18.911, "longitude": 72.8253 },
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

Errors use `msg.topic = environment/<source>/error` and include `source`, `status: ERROR`, `error`, and `failedAt`. `<source>` is `weather` or `marine` after request construction, and `environmental-api` if configuration fails before the source is set. Non-success HTTP responses, API error objects, missing required structures, invalid numeric values, and invalid location configuration are sent through the Catch/error path. Errors are visible in Debug; user-facing error, missing-value, and stale-data states are not implemented yet.

## Later phases

The live MQTT path was verified with simulator samples, including values displayed in the dashboard gauges and charts; malformed-payload error handling remains to be checked. The three Dashboard 2 pages and their normalized data connections are deployed and verified. Phase 4.4 will present missing, stale, and failed data states. Earlier draft examples are not active interfaces.
