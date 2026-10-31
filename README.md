# Smart Fishing — IoT & Data Monitoring Dashboard

**Course:** IND4 Assignment  
**Primary Platform:** Node-RED  
**Project Type:** IoT / Environmental & Data Monitoring Dashboard  

Smart Fishing is an interactive Node-RED data-monitoring dashboard that collects environmental, weather, water, and catch-related information from online APIs and optional MQTT sensors. It transforms raw data into real-time visualisations including line charts, bar charts, gauges, and summary indicators.

---

## Features

- **Multi-Source Ingestion:** Automated HTTP polling of weather, oceanographic, and marine APIs.
- **Optional Real-Time Ingestion (MQTT):** Live or simulated telemetry for water temperature, water level, and catch counters.
- **Interactive Visualizations:** Gauges for immediate readings, line charts for trends, bar charts for categorical metrics, and numeric summary cards.
- **Data Validation & Resiliency:** Graceful handling of API rate limits, missing fields, and connectivity loss without UI disruption.
- **Containerized Deployment:** Pre-configured Docker Compose setup for portable, single-command deployment.

---

## Tech Stack & Dependencies

- **Runtime:** Node.js (v18+)
- **Core Engine:** Node-RED (v3.0+)
- **UI Framework:** `@node-red/node-red-dashboard`
- **Protocols:** HTTP/HTTPS REST, MQTT (via Mosquitto Broker)
- **Containerization:** Docker & Docker Compose
- **Simulation Scripting:** Python 3 (for optional MQTT sensor emulator)

---

## Project Structure

```text
smart-fishing/
├── README.md
├── LICENSE
├── .env.example
├── compose.yaml
├── flows/
│   └── smart-fishing.json     # Node-RED flow definition
├── node-red/
│   ├── package.json           # Node-RED custom nodes/dependencies
│   └── settings.js            # Node-RED configuration
├── docs/
│   ├── project_spec.md
│   ├── architecture.md
│   ├── tech_stack.md
│   ├── implementation_plan.md
│   └── chatgpt_codex.md
└── scripts/
    └── simulate-mqtt.py       # MQTT simulator script
```

---

## Quick Start (Docker Compose)

### Prerequisites

- [Docker Desktop](https://www.docker.com/) (v20.10+)
- [Docker Compose](https://docs.docker.com/compose/) (v2.0+)

### Setup & Run

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/smart-fishing.git
   cd smart-fishing
   ```

2. **Configure Environment Variables:**
   ```bash
   cp .env.example .env
   # Edit .env to add your API keys (e.g., OpenWeatherMap, Stormglass)
   ```

3. **Launch Containers:**
   ```bash
   docker compose up -d
   ```

4. **Access Applications:**
   - **Node-RED Flow Editor:** [http://localhost:1880](http://localhost:1880)
   - **Smart Fishing UI:** [http://localhost:1880/ui](http://localhost:1880/ui)

5. **Stop Containers:**
   ```bash
   docker compose down
   ```

---

## Environment Variables Configuration

Copy `.env.example` to `.env` and configure your API credentials and endpoints:

```env
# Node-RED Configuration
PORT=1880
TZ=Asia/Calcutta
NODE_RED_CREDENTIAL_SECRET=replace_with_a_long_random_secret

# API Configuration
WEATHER_API_KEY=your_weather_api_key
WEATHER_API_URL=https://api.openweathermap.org/data/2.5/weather

# MQTT Configuration (Optional)
MQTT_BROKER_HOST=mosquitto
MQTT_BROKER_PORT=1883
MQTT_TOPIC_PREFIX=smartfishing
```

---

## Troubleshooting & FAQ

* **Dashboard shows "Disconnected":** Ensure the Node-RED container is running via `docker compose logs -f node-red`.
* **API Nodes returning 401/403:** Verify that your `.env` contains valid credentials and restart the container (`docker compose restart node-red`).
* **MQTT Data Not Updating:** Ensure Mosquitto broker container is running and that `scripts/simulate-mqtt.py` is targeting the correct port (`1883`).

---

## License & Attribution

Distributed under the MIT License. Data sourced from public marine and weather API providers in accordance with their respective usage terms.
