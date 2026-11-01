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

## Phase 3: MQTT sensor integration

- [x] 3.1 Add and configure a Mosquitto broker service in Docker Compose.
- [x] 3.1a Verify broker startup and local MQTT connectivity.
- [x] 3.2 Implement a Python telemetry publisher and pin its MQTT client dependency.
- [x] 3.2a Install the dependency and verify messages reach a running broker.
- [x] 3.3 Add Node-RED MQTT input and validate/normalize the simulator's documented topic/payload schema.
- [x] 3.3a Deploy the updated flow and verify a live message appears in Node-RED output.
- [x] 3.4 Verify simulated telemetry reaches the normalized downstream flow.

## Phase 4: Dashboard

- [x] 4.1 Select and pin FlowFuse Dashboard `@flowfuse/node-red-dashboard` `1.34.1` for the selected runtime.
- [x] 4.2 Build overview, weather, and water condition views; deploy and verify all three Dashboard 2 pages.
- [x] 4.3 Connect normalized weather, marine, and MQTT data to dashboard gauges, charts, and summary values; verify live API and simulator values.
- [ ] 4.4 Show API failures, missing values, and stale-data state in the UI.

## Phase 5: Packaging and release checks

- [ ] 5.1 Export the complete working flow to `flows/smart-fishing.json`.
- [ ] 5.2 Follow setup documentation on a clean environment and record the result.
- [ ] 5.3 Check tracked files for secrets, ignored runtime data, and stack consistency.
- [ ] 5.4 Update specifications and architecture documentation to describe the completed application.
