# Project Specification: Smart Fishing

## Purpose

Smart Fishing is an IND4 assignment being developed in phases as a Node-RED environmental monitoring application. Phase 2 implements scheduled Open-Meteo ingestion and normalization. Phase 3.1–3.2 add the local Mosquitto configuration and Python synthetic telemetry publisher; publishing and Node-RED MQTT subscription are pending runtime verification and Phase 3.3 work. A user-facing dashboard remains planned.

## Current implementation requirements (Phase 2)

| ID | Requirement | Status |
|---|---|---|
| P2-1 | Fetch weather at startup and every 15 minutes. | Implemented |
| P2-2 | Fetch marine forecast at startup and every 15 minutes. | Implemented |
| P2-3 | Read endpoints and coordinates from environment configuration. | Implemented |
| P2-4 | Validate response structure, HTTP status, and required numeric values before emitting normalized data. | Implemented |
| P2-5 | Emit timestamped normalized weather, marine, and error messages for inspection. | Implemented via Debug nodes |
| P2-6 | Keep the Node-RED host port configurable and loopback-bound by default. | Implemented in Compose |
| P3-1 | Provide a persistent local Mosquitto broker with a loopback-bound host port. | Configured in Compose; startup verification pending |
| P3-2 | Provide a configurable Python publisher for synthetic MQTT telemetry. | Implemented; broker publish verification pending |

## Target requirements (not implemented yet)

| ID | Target behavior | Planned phase |
|---|---|---|
| P3-3 | Subscribe to the telemetry topic in Node-RED and validate/normalize the payload. | Phase 3 |
| P4-1 | Provide overview and weather/water dashboard views using validated messages. | Phase 4 |
| P4-2 | Indicate API connectivity, missing values, and stale data in the UI. | Phase 4 |
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
- **Observability:** Keep normalized payloads and ingestion errors inspectable through Debug while the dashboard is not implemented.

## Acceptance criteria

### Phase 2 (verified)

- [x] Node-RED 5.0.9 starts and loads the exported flow.
- [x] Weather and marine requests return data for the configured Sassoon Dock coordinates.
- [x] Both outputs pass through validation/normalization and are visible in the Debug sidebar.
- [x] Error paths format failures for Debug inspection.
- [x] No API secrets are needed for the configured Open-Meteo endpoints.

### Phase 3.1–3.2 (implemented; runtime verification pending)

- [ ] Mosquitto starts and accepts a local MQTT connection; runtime verification pending.
- [ ] Python simulator publishes telemetry to Mosquitto; runtime verification pending.

### Whole project (pending later phases)

- [ ] Node-RED MQTT ingestion is configured and verified against the simulator contract.
- [ ] Dashboard views and widgets are connected to validated signals.
- [ ] Stale-data and API-error states are visible to dashboard users.
- [ ] Final deployment and repository hygiene are verified against the completed setup documentation.
