# Project Specification: Smart Fishing

## Purpose

Smart Fishing is an IND4 assignment being developed in phases as a Node-RED environmental monitoring application. Phase 2 implements scheduled Open-Meteo ingestion and normalization. Phase 3.1–3.2 add the local Mosquitto configuration and Python synthetic telemetry publisher; Phase 3.3 connects the telemetry topic to Node-RED normalization. A live sample has been verified. Phase 4.2 adds Overview, Environment, and Water Conditions dashboard pages. Phases 4.3–4.7 connect weather, marine, and MQTT data, provide summary values, and add a selectable update interval.

## Current implementation requirements

| ID | Requirement | Status |
|---|---|---|
| P2-1 | Fetch weather at startup and every 15 minutes. | Implemented |
| P2-2 | Fetch marine forecast at startup and every 15 minutes. | Implemented |
| P2-3 | Read endpoints and coordinates from environment configuration. | Implemented |
| P2-4 | Validate response structure, HTTP status, and required numeric values before emitting normalized data. | Implemented |
| P2-5 | Emit timestamped normalized weather, marine, and error messages for inspection. | Implemented via Debug nodes |
| P2-6 | Keep the Node-RED host port configurable and loopback-bound by default. | Implemented in Compose |
| P2-7 | Keep a local rolling cache of the last seven completed UTC days of weather and marine summaries; fetch only missing date/source data and remove dates outside the window. | Implemented and verified in `cache/history-7d.json` |
| P3-1 | Provide a persistent local Mosquitto broker with a loopback-bound host port. | Implemented and verified |
| P3-2 | Provide a configurable Python publisher for synthetic MQTT telemetry. | Implemented and verified against Mosquitto |

## Requirements and implementation roadmap

| ID | Target behavior | Status / phase |
|---|---|---|
| P3-3 | Subscribe to the telemetry topic in Node-RED and validate/normalize the payload. | Implemented and live sample verified |
| P4-1 | Select and pin a maintained dashboard package compatible with the runtime. | Implemented: FlowFuse Dashboard 1.34.1 |
| P4-2 | Provide overview and weather/water dashboard views. | Implemented and verified; pages deployed |
| P4-3 | Display normalized weather values in dashboard gauges, charts, and summaries. | Implemented and live values verified; Phase 4.3 |
| P4-4 | Display normalized marine values in dashboard gauges and summaries. | Implemented and live values verified; Phase 4.4 |
| P4-5 | Display normalized MQTT telemetry in dashboard gauges, trends, and summaries. | Implemented and simulator values verified; Phase 4.5 |
| P4-6 | Combine weather, marine, and telemetry readings in Overview summary values. | Implemented and verified; Phase 4.6 |
| P4-7 | Let users select the dashboard update interval. | Implemented and verified; Phase 4.7 |
| P4-8 | Indicate API failures, missing values, and stale data in the UI. | Planned: Phase 4.8 |
| P4-9 | Show cached seven-day weather and marine history charts. | In progress; Phase 4.9 |
| P5-1 | Document and verify clean deployment of the completed implementation. | Phase 5 |

## Data and behavior

- The sample location is Sassoon Dock, Mumbai (`18.9110, 72.8253`). Set `LOCATION_NAME`, `LOCATION_LATITUDE`, and `LOCATION_LONGITUDE` together for the intended forecast area.
- Weather data includes current air temperature and wind speed plus up to five daily rainfall forecast values.
- Marine data includes hourly sea-surface temperature, sea-level height relative to mean sea level, and wave height for the requested model location.
- Forecast/model values are not measurements from physical harbor sensors and may be unavailable for some coordinates.
- Normalized payload and error contracts are documented in [system_architecture.md](system_architecture.md).
- Requests use HTTPS. The configured Open-Meteo endpoints require no API key.
- Historical cache values are daily summaries of recent archived model forecasts, not physical sensor measurements; the JSON cache is at `cache/history-7d.json` and feeds the seven-day trend charts.

## Non-functional requirements

- **Portability:** Run the current application with Docker Engine and Docker Compose v2.
- **Configuration:** Keep location, ports, endpoints, timezone, and runtime credential secret outside the exported flow.
- **Resilience:** Route failed requests and invalid API responses into the error path without crashing the runtime.
- **Security:** Do not commit `.env`, credentials, or generated Node-RED runtime files. Bind the editor to loopback by default.
- **Observability:** Keep normalized payloads and ingestion errors inspectable through Debug; expose user-facing views through the dashboard.

## Acceptance criteria

### Phase 2 (verified)

- [x] Node-RED 5.0.9 starts and loads the exported flow.
- [x] Weather and marine requests return data for the configured Sassoon Dock coordinates.
- [x] Both outputs pass through validation/normalization and are visible in the Debug sidebar.
- [x] Error paths format failures for Debug inspection.
- [x] No API secrets are needed for the configured Open-Meteo endpoints.

### Phase 2.6 (cache populated and cache-hit behavior verified)

- [x] Cache contains seven completed UTC dates with weather and marine summaries for the configured location.
- [x] A second refresh reports 7/7 dates for both sources without logging a cache-miss fetch.

### Phase 3.1–3.2 (verified)

- [x] Mosquitto starts with the project configuration and accepts a local MQTT connection.
- [x] Python simulator publishes telemetry that a subscriber receives on the documented topic.

### Phase 3.3–3.4 (live sample verified)

- [x] Node-RED subscribes to the configured telemetry topic and emits normalized sensor payloads.
- [ ] Malformed JSON/schema messages reach the MQTT error output.

### Phase 4.1–4.7 (dashboard package, pages, live data, and update interval verified)

- [x] FlowFuse Dashboard `1.34.1` is pinned and its UI node types load in the Node-RED editor.
- [x] Overview, Environment, and Water Conditions pages render at their configured dashboard routes.
- [x] Normalized weather values reach their dashboard gauges, charts, and summaries (Phase 4.3).
- [x] Normalized marine values reach their dashboard gauges and summaries (Phase 4.4).
- [x] Normalized MQTT values reach their dashboard gauges, trends, and summaries (Phase 4.5).
- [x] Combined summary values are shown on Overview and the update interval is selectable (Phases 4.6–4.7).
- [ ] Stale-data and API-error states are shown to users (Phase 4.8).

### Phase 4.9 (historical charts)

- [ ] Seven-day weather and marine history charts render from the local cache endpoint.

### Whole project (pending later phases)

- [x] Dashboard views and widgets are connected to validated signals.
- [ ] Stale-data and API-error states are visible to dashboard users (Phase 4.8).
- [ ] Final deployment and repository hygiene are verified against the completed setup documentation.
