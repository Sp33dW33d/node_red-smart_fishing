# Project Specification: Smart Fishing

## Purpose

Smart Fishing is an IND4 assignment being developed in phases as a Node-RED environmental monitoring application. Phase 2 implements scheduled Open-Meteo ingestion and normalization. Phase 3.1–3.2 add the local Mosquitto configuration and Python synthetic telemetry publisher; Phase 3.3 connects the telemetry topic to Node-RED normalization. A live sample has been verified. Phase 4.2 adds user-facing Overview, Environment, and Water Conditions dashboard pages; wiring live values is the next step.

## Current implementation requirements

| ID | Requirement | Status |
|---|---|---|
| P2-1 | Fetch weather at startup and every 15 minutes. | Implemented |
| P2-2 | Fetch marine forecast at startup and every 15 minutes. | Implemented |
| P2-3 | Read endpoints and coordinates from environment configuration. | Implemented |
| P2-4 | Validate response structure, HTTP status, and required numeric values before emitting normalized data. | Implemented |
| P2-5 | Emit timestamped normalized weather, marine, and error messages for inspection. | Implemented via Debug nodes |
| P2-6 | Keep the Node-RED host port configurable and loopback-bound by default. | Implemented in Compose |
| P3-1 | Provide a persistent local Mosquitto broker with a loopback-bound host port. | Implemented and verified |
| P3-2 | Provide a configurable Python publisher for synthetic MQTT telemetry. | Implemented and verified against Mosquitto |

## Requirements and implementation roadmap

| ID | Target behavior | Status / phase |
|---|---|---|
| P3-3 | Subscribe to the telemetry topic in Node-RED and validate/normalize the payload. | Implemented and live sample verified |
| P4-1 | Select and pin a maintained dashboard package compatible with the runtime. | Implemented: FlowFuse Dashboard 1.34.1 |
| P4-2 | Provide overview and weather/water dashboard views. | Implemented; pages deployed and verified, live values pending P4-3 |
| P4-3 | Connect normalized data to dashboard gauges, charts, and summary values. | Planned: Phase 4.3 |
| P4-4 | Indicate API failures, missing values, and stale data in the UI. | Planned: Phase 4.4 |
| P5-1 | Document and verify clean deployment of the completed implementation. | Phase 5 |

## Data and behavior

- The sample location is Sassoon Dock, Colaba, Mumbai (`18.9110, 72.8253`). Set coordinates for the intended forecast area.
- Weather data includes current air temperature and wind speed plus up to five daily rainfall forecast values.
- Marine data includes hourly sea-surface temperature, sea-level height relative to mean sea level, and wave height for the requested model location.
- Forecast/model values are not measurements from physical harbor sensors and may be unavailable for some coordinates.
- Normalized payload and error contracts are documented in [system_architecture.md](system_architecture.md).
- Requests use HTTPS. The configured Open-Meteo endpoints require no API key.

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

### Phase 3.1–3.2 (verified)

- [x] Mosquitto starts with the project configuration and accepts a local MQTT connection.
- [x] Python simulator publishes telemetry that a subscriber receives on the documented topic.

### Phase 3.3–3.4 (live sample verified)

- [x] Node-RED subscribes to the configured telemetry topic and emits normalized sensor payloads.
- [ ] Malformed JSON/schema messages reach the MQTT error output.

### Phase 4.1–4.2 (package and page structure verified)

- [x] FlowFuse Dashboard `1.34.1` is pinned and its UI node types load in the Node-RED editor.
- [x] Overview, Environment, and Water Conditions pages render at their configured dashboard routes.
- [ ] Live normalized signals are connected to widgets (Phase 4.3).
- [ ] Stale-data and API-error states are shown to users (Phase 4.4).

### Whole project (pending later phases)

- [ ] Dashboard views and widgets are connected to validated signals.
- [ ] Stale-data and API-error states are visible to dashboard users.
- [ ] Final deployment and repository hygiene are verified against the completed setup documentation.
