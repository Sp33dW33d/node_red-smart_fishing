# Implementation Plan

This checklist tracks repository state. A task is complete only when implementation exists and its stated verification has been performed.

## Phase 1: Foundation and setup

- [x] 1.1 Initialize repository structure and Git history.
- [x] 1.2 Configure Docker Compose, environment example, and Node-RED settings.
- [x] 1.3 Run the project with Docker Compose.

## Phase 2: Environmental API ingestion

- [x] 2.1 Fetch current weather and daily rainfall from Open-Meteo Forecast API.
- [x] 2.2 Fetch marine hourly values from Open-Meteo Marine API.
- [x] 2.3 Validate response structures and normalize data in Function nodes.
- [x] 2.4 Format request and validation failures for inspection.
- [x] 2.5 Verify live normalized outputs for the Sassoon Dock sample coordinates.
- [x] 2.6 Build a local rolling seven-day weather and marine history cache; request only missing date/source data and prune expired dates; verify the populated local cache.

## Phase 3: MQTT sensor integration

- [x] 3.1 Add and configure a Mosquitto broker service in Docker Compose.
- [x] 3.1a Verify broker startup and local MQTT connectivity.
- [x] 3.2 Implement a Python telemetry publisher and pin its MQTT client dependency.
- [x] 3.2a Install the dependency and verify messages reach a running broker.
- [x] 3.2b Start the simulator as a Compose service with the launcher and verify it publishes to Mosquitto.
- [x] 3.3 Add Node-RED MQTT input and validate/normalize the simulator's documented topic/payload schema.
- [x] 3.3a Deploy the updated flow and verify a live message appears in Node-RED output.
- [x] 3.4 Verify simulated telemetry reaches the normalized downstream flow.

## Phase 4: Dashboard

- [x] 4.1 Select and pin FlowFuse Dashboard `@flowfuse/node-red-dashboard` `1.34.1` for the selected runtime.
- [x] 4.2 Build overview, weather, and water condition views; deploy and verify all three Dashboard 2 pages.
- [x] 4.3 Connect normalized weather data to the Environment and Overview dashboard widgets; verify the live weather values.
- [x] 4.4 Connect normalized marine data to the Water Conditions and Overview dashboard widgets; verify the live marine values.
- [x] 4.5 Connect normalized MQTT telemetry to the Water Conditions and Overview dashboard widgets; verify live simulator values.
- [x] 4.6 Display combined weather, marine, and telemetry summary values on the Overview dashboard.
- [x] 4.7 Add separate selectable API polling and sensor display intervals; API options are 15 seconds, 30 seconds, 1 minute, 5 minutes, or 15 minutes, while sensor display defaults to every simulator message and can be slowed independently.
- [x] 4.8 Show weather and marine API status in the dashboard, including failed requests, missing or invalid values, last successful update times, and stale-data alerts based on the selected API polling interval.
- [x] 4.9 Display cached seven-day weather and marine history metrics in dashboard charts.
- [x] 4.10 Build the backend fishing-conditions recommendation flow and publish a condition status, score, reasons, and catch-rate multiplier over MQTT.
- [x] 4.11 Add the fishing-conditions recommendation and explanation to the dashboard, including a dashboard-only manual preview for Favorable, Caution, and Poor states.
- [x] 4.12 Add a rolling catches-per-hour chart to Sensor trends using cumulative simulator catch-count changes.

## Phase 5: Packaging and release checks

- [x] 5.1 Export the complete working flow to `flows/smart-fishing.json`.
- [x] 5.2 Follow setup documentation on a clean environment and record the result.
  - Clean setup verified 2026-11-03 in an isolated fresh Compose project. Initial verification exposed that a fresh Node-RED `/data` volume did not install the pinned Dashboard package; startup now installs from `package-lock.json`. Rerun passed: all four services started, Node-RED connected to Mosquitto, the simulator published telemetry, the history cache populated all 7/7 weather and marine days, and all three dashboard routes returned HTTP 200.
- [x] 5.3 Check tracked files for secrets, ignored runtime data, and stack consistency.
  - Audit verified 2026-11-03: no tracked secrets found; runtime data is ignored, and Compose settings and dependency pins align. Added the cache interval to `.env.example` and ignored the generated flow backup.
- [x] 5.4 Reconcile the root README and all project documents in `docs/` with the completed application, including current requirements, architecture, dependencies, dashboard features, setup, and verification status.
  - Reconciled the README and `docs/` with the current services, flows, dependencies, dashboard, and setup; checked for stale phase claims and whitespace errors.
