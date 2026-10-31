# Project Specification: Smart Fishing

## Purpose

Smart Fishing is an IND4 assignment being developed in phases as a Node-RED environmental monitoring application. The current deliverable is Phase 2: scheduled ingestion and normalization of Open-Meteo weather and marine forecast data for configurable coordinates. MQTT telemetry and a user-facing dashboard are planned work.

## Current implementation requirements (Phase 2)

| ID | Requirement | Status |
|---|---|---|
| P2-1 | Fetch weather at startup and every 15 minutes. | Implemented |
| P2-2 | Fetch marine forecast at startup and every 15 minutes. | Implemented |
| P2-3 | Read endpoints and coordinates from environment configuration. | Implemented |
| P2-4 | Validate response structure, HTTP status, and required numeric values before emitting normalized data. | Implemented |
| P2-5 | Emit timestamped normalized weather, marine, and error messages for inspection. | Implemented via Debug nodes |
| P2-6 | Keep the Node-RED host port configurable and loopback-bound by default. | Implemented in Compose |

## Target requirements (not implemented yet)

| ID | Target behavior | Planned phase |
|---|---|---|
| P3-1 | Accept real or simulated telemetry using documented MQTT topics and payload schema. | Phase 3 |
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

### Whole project (pending later phases)

- [ ] MQTT broker, publisher/emulator, and Node-RED MQTT ingestion are configured and verified.
- [ ] Dashboard views and widgets are connected to validated signals.
- [ ] Stale-data and API-error states are visible to dashboard users.
- [ ] Final deployment and repository hygiene are verified against the completed setup documentation.
