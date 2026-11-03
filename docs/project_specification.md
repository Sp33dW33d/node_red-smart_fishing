# Project Specification: Smart Fishing

## Purpose and current scope

Smart Fishing is an IND4 assignment implemented as a local Node-RED environmental monitoring and fishing-conditions demonstration. Docker Compose runs Node-RED, a local Mosquitto broker, a Python MQTT telemetry simulator, and a Python standard-library history-cache service. Node-RED fetches and normalizes Open-Meteo weather and marine forecasts, consumes validated simulator telemetry, calculates a fishing-conditions recommendation, and serves the FlowFuse Dashboard. The implementation through Phase 5.4 is complete; [implementation_plan.md](implementation_plan.md) records the delivered scope and verification.

## Current implementation requirements

| ID | Requirement | Status |
|---|---|---|
| P2-1 | Fetch weather at startup and at a selectable interval (15 seconds, 30 seconds, 1 minute, 5 minutes, or 15 minutes; default 1 minute). | Implemented |
| P2-2 | Fetch marine forecast at startup and at the selected API interval. | Implemented |
| P2-3 | Read API endpoints and coordinates from environment configuration. | Implemented |
| P2-4 | Validate response structure, HTTP status, and required numeric values before emitting normalized data. | Implemented |
| P2-5 | Emit timestamped normalized weather, marine, and error messages for inspection and downstream dashboard use. | Implemented |
| P2-6 | Keep the Node-RED host port configurable and loopback-bound by default. | Implemented in Compose |
| P2-7 | Maintain a local cache of seven completed UTC days of weather and marine summaries; fetch only missing date/source data and prune dates outside the window. | Implemented; clean Compose setup verified |
| P3-1 | Provide a persistent local Mosquitto broker with a loopback-bound host port. | Implemented |
| P3-2 | Provide a configurable Python publisher for synthetic MQTT telemetry, including weather-dependent catch rate. | Implemented and verified against Mosquitto |
| P3-3 | Subscribe to telemetry in Node-RED and validate/normalize payloads, routing malformed messages to the ingestion error path. | Implemented; valid live sample verified |

## Dashboard and recommendation requirements

| ID | Requirement | Status |
|---|---|---|
| P4-1 | Select and pin a maintained dashboard package compatible with the runtime. | Implemented: FlowFuse Dashboard 1.34.1 |
| P4-2 | Provide Overview, Environment, and Water Conditions pages. | Implemented and verified |
| P4-3 | Display normalized weather values in gauges, forecast charts, summaries, and seven-day history. | Implemented |
| P4-4 | Display normalized marine values in gauges, summaries, and seven-day history. | Implemented |
| P4-5 | Display normalized MQTT telemetry in gauges, summaries, and trends. | Implemented |
| P4-6 | Combine current weather, marine, and telemetry readings in Overview. | Implemented |
| P4-7 | Let users select independent API polling and sensor display intervals. | Implemented |
| P4-8 | Indicate API waiting/current/error/missing/stale states and last-success timestamps. | Implemented |
| P4-9 | Show cached seven-day weather and marine history charts. | Implemented |
| P4-10 | Calculate a fishing-conditions status, score, reasons, and catch-rate multiplier, and publish the result over MQTT. | Implemented |
| P4-11 | Display the recommendation and explanation with a dashboard-only condition preview. | Implemented |
| P4-12 | Chart rolling 60-minute catches per hour from cumulative simulator counts. | Implemented |
| P5 | Document and verify clean deployment, repository hygiene, and current architecture/specifications. | Implemented through 5.4 |

## Data and behavior

- The sample forecast location is Sassoon Dock, Mumbai (`18.9110, 72.8253`). Set `LOCATION_NAME`, `LOCATION_LATITUDE`, and `LOCATION_LONGITUDE` together for another forecast area.
- Weather data contains current air temperature and wind speed plus up to five daily rainfall forecast values.
- Marine data contains hourly sea-surface temperature, sea-level height relative to mean sea level, and wave height for the requested model location.
- Forecast and archived-history values are model output, not observations from physical harbor instruments; marine data may be unavailable at some coordinates.
- The recommendation considers wind speed, wave height, the first daily rainfall forecast value, and sea-surface temperature. Status is `favorable`, `caution`, or `poor`, with a score from 0 to 100, human-readable reasons, location, generation time, input values, and catch-rate multiplier. The default multiplier is 1.5 for favorable, 0.7 for caution, and 0.2 for poor conditions.
- Recommendation messages are published to `MQTT_CONDITIONS_TOPIC` (default `smartfishing/conditions`). The simulator subscribes and adjusts a time-based catch-arrival model; telemetry readings remain synthetic.
- The manual recommendation preview on Overview is browser/dashboard-only. It changes the displayed condition card for demonstration and does not change the backend recommendation or simulator.
- API status cards on Overview distinguish waiting, current, missing values, request failure, and stale readings. The stale threshold is the greater of two minutes or 2.5 times the selected API polling interval.
- Environment shows current weather, a five-day rainfall forecast, and daily mean air temperature, maximum wind speed, and rainfall history. Water Conditions shows marine and sensor readings, one-hour sensor trends, rolling 60-minute catches per hour, and daily mean marine temperature, sea level, and wave height history.
- Historical data is stored in the ignored local file `cache/history-7d.json`. The history service checks hourly by default, serves `GET /history` at `history-cache:8080` inside the Compose network, and refreshes Dashboard history charts every minute.
- Requests use HTTPS. The configured Open-Meteo endpoints require no API key.
- Normalized payload and error contracts are documented in [system_architecture.md](system_architecture.md).

## Non-functional requirements

- **Portability:** Run the application with Docker Engine and Docker Compose v2.
- **Configuration:** Keep location, ports, endpoints, timezone, and runtime credential secret outside the exported flow.
- **Resilience:** Route failed requests and invalid API responses into error paths without crashing the runtime; report API freshness to dashboard users.
- **Security:** Do not commit `.env`, credentials, or generated Node-RED runtime files. Bind the editor and MQTT listener to loopback by default. Anonymous MQTT access is for local development only.
- **Observability:** Keep normalized payloads and ingestion errors inspectable through Debug; expose current data and health through the dashboard.

## Acceptance criteria

### Phase 2: API ingestion and history cache

- [x] Weather and marine requests start automatically and use the selected API interval.
- [x] Responses are validated and normalized, and failures are sent through error paths.
- [x] Live normalized readings were verified for the Sassoon Dock sample coordinates.
- [x] The seven-day cache populates seven completed UTC dates for each source, and the clean setup check confirms 7/7 coverage for weather and marine.

### Phase 3: MQTT integration

- [x] Mosquitto starts with the project configuration and accepts local MQTT connections.
- [x] The Python simulator publishes telemetry on the documented topic and consumes condition recommendations.
- [x] Node-RED normalizes live telemetry and includes validation/error routing for malformed payloads.

### Phase 4: Dashboard and fishing conditions

- [x] FlowFuse Dashboard 1.34.1 loads; all three dashboard routes returned HTTP 200 in a clean isolated Compose setup.
- [x] Normalized weather, marine, and MQTT values reach their dashboard gauges, summaries, and charts.
- [x] Overview controls API cadence independently from sensor display cadence and presents API health/freshness states.
- [x] The dashboard displays cached seven-day weather and marine history.
- [x] The recommendation is published over MQTT, displayed on Overview, and can be previewed in three dashboard-only states.
- [x] Water Conditions includes the rolling catches-per-hour chart.

### Phase 5: Packaging and documentation

- [x] A clean isolated Compose run started all four services, populated the seven-day history cache, and served all dashboard pages.
- [x] Tracked files, ignored runtime data, environment examples, and dependency/image pins were audited.
- [x] README and all project documents in `docs/` describe the current implemented system.
