# Project Specification: Smart Fishing

## 1. Executive Summary & Goals

The Smart Fishing project provides anglers, environmental researchers, and local fisheries with a unified dashboard monitoring key aquatic and atmospheric variables. 

### Core Goals:
1. Aggregate online atmospheric and marine API data into Node-RED.
2. Ingest low-latency local telemetry via MQTT.
3. Normalize and validate incoming heterogeneous payloads into unified schema structures.
4. Present actionable insights via standard Node-RED dashboard widgets.
5. Provide standard containerization for consistent deployment across platforms.

---

## 2. Functional Requirements

### Dashboard Sections & Visualizations

| Section | Target Metric | Component Type | Source |
|---|---|---|---|
| **Overview** | Last System Sync Time | Numeric Card / Text | System Timestamp |
| **Overview** | System Status & Connection | Status LED Indicator | Node-RED Flow State |
| **Weather & Environment** | Air Temperature & Wind Speed | Gauge Widget | External REST API |
| **Weather & Environment** | 5-Day Rainfall Forecast | Line Chart | External REST API |
| **Water Conditions** | Water Temperature (°C) | Line Chart | MQTT / Ocean API |
| **Water Conditions** | Tidal Water Level (m) | Gauge / Chart | MQTT / Marine API |
| **Catch Information** | Daily Catch Count | Bar Chart | MQTT / Data Input |
| **Catch Information** | Species Distribution | Doughnut Chart | Simulated/Static Dataset |

---

## 3. Non-Functional Requirements

- **Portability:** Full stack run capability on Linux, macOS, and Windows via Docker Compose.
- **Security:** Strict separation of source code and sensitive API credentials via `.env` injection.
- **Reliability:** Data flow resilience preventing dashboard crashes upon API network failure or missing payload keys.
- **Performance:** UI updates render within $<100\text{ ms}$ upon receiving ingested payloads.

---

## 4. Acceptance Criteria Checklist

- [ ] Node-RED starts and runs without throwing unhandled exceptions.
- [ ] Exported `flows/smart-fishing.json` imports cleanly into a fresh instance.
- [ ] Minimum of 1 active HTTP REST data source updating dashboard widgets.
- [ ] Incoming data undergoes schema validation prior to UI rendering.
- [ ] Simulated or real MQTT telemetry operates on defined topic namespaces.
- [ ] Zero API keys or secrets committed to git source control.