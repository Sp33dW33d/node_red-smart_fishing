# Implementation & Development Plan

## Phase 1: Foundation & Setup
- [x] Task 1.1: Initialize git repository structure.
- [x] Task 1.2: Configure `compose.yaml`, `.env.example`, and Node-RED user directory settings.
- [x] Task 1.3: Verify standard local container execution via Docker Compose.

## Phase 2: Ingestion Pipeline Development
- [ ] Task 2.1: Implement HTTP Request flow to fetch atmospheric data (e.g., OpenWeatherMap API).
- [ ] Task 2.2: Implement HTTP Request flow to fetch oceanographic data.
- [ ] Task 2.3: Build Function/Change nodes to parse and sanitize HTTP JSON responses.

## Phase 3: MQTT Sensor Integration
- [ ] Task 3.1: Configure Mosquitto broker service in Docker Compose.
- [ ] Task 3.2: Create Python emulator script (`scripts/simulate-mqtt.py`) publishing synthetic telemetry.
- [ ] Task 3.3: Wire Node-RED MQTT input nodes to parse incoming topic messages.

## Phase 4: UI & Dashboard Assembly
- [ ] Task 4.1: Construct Overview, Environment, and Water condition UI tabs.
- [ ] Task 4.2: Connect validated signals to gauges, line graphs, and numeric cards.
- [ ] Task 4.3: Implement error handling logic and stale data indicator visual flags.

## Phase 5: Packaging & Testing
- [ ] Task 5.1: Export final complete flow to `flows/smart-fishing.json`.
- [ ] Task 5.2: Test clean project deployment on an isolated host using setup documentation.
- [ ] Task 5.3: Ensure repository cleanliness (secrets check, `.gitignore` validation).
