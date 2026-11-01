# System Architecture

## Current stack (Phase 2 API flow, Phase 3 MQTT path, Phase 4.2 dashboard views)

```text
Docker Compose
├── Node-RED 5.0.9 (host 127.0.0.1:<PORT> → container 1880)
│   ├── Weather and marine API flows → normalized payloads/errors → Debug sidebar
│   ├── MQTT In → validate and normalize sensor telemetry/errors → Debug sidebar
│   └── FlowFuse Dashboard 2 → Overview, Environment, Water Conditions pages
└── Mosquitto 2.1.2 (host 127.0.0.1:<MQTT_PORT> → container 1883)
    └── persistent broker state (Docker named volume)

Python telemetry simulator (host process)
└── MQTT QoS 1 publish → <MQTT_TOPIC_PREFIX>/<device_id>/telemetry
    └── Mosquitto (localhost:<MQTT_PORT>)
```

The Mosquitto listener is reachable to Compose services as `mosquitto:1883` and is published to the host on loopback only. Anonymous MQTT access is enabled for local assignment development. FlowFuse Dashboard 2.0 serves the Overview, Environment, and Water Conditions pages at `/dashboard/overview`, `/dashboard/environment`, and `/dashboard/water-conditions`. Each page currently has a descriptive Markdown widget. Live metrics and failure/stale states are not connected yet; those are planned for Phases 4.3 and 4.4.

The Phase 3.2 host-side publisher uses `paho-mqtt==2.1.0`. By default it publishes to `smartfishing/demo-01/telemetry` every five seconds with QoS 1 and no retained message. Each JSON payload contains `device_id`, a UTC `timestamp`, `water_temperature_c`, `water_level_m`, cumulative `catch_count`, and `battery_voltage_v`. All values are synthetic.

The Node-RED MQTT In node subscribes at QoS 1 to `${MQTT_TOPIC_PREFIX}/+/telemetry` and parses JSON. Its Function node requires a non-empty device ID, parseable timestamp, finite numeric measurements, and a non-negative integer catch count. Valid messages use `msg.topic = sensor/telemetry/<device_id>` and a normalized payload with `source`, `status`, `deviceId`, `observedAt`, `receivedAt`, `waterTemperatureC`, `waterLevelM`, `catchCount`, and `batteryVoltageV`. MQTT JSON parse/validation errors are tagged `source: mqtt` and routed to the shared ingestion error output.

Weather and marine paths are Inject → request builder → HTTP Request → validation/normalization → Debug. Their Catch nodes format failures for Debug.

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

Errors use `msg.topic = environment/<source>/error` and include `source`, `status: ERROR`, `error`, and `failedAt`. `<source>` is `weather` or `marine` after request construction, and `environmental-api` if configuration fails before the source is set. Non-success HTTP responses, API error objects, missing required structures, invalid numeric values, and invalid location configuration are sent through the Catch/error path. Errors are visible in Debug; dashboard error states and persistent history are not implemented yet.

## Later phases

The live MQTT path was verified with a simulator message; malformed-payload error handling remains to be checked. The three Dashboard 2 pages are deployed and verified. Phase 4.3 will connect them to normalized outputs, and Phase 4.4 will present missing, stale, and failed data states. Earlier draft examples are not active interfaces.
