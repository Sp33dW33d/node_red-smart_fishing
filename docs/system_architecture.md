# System Architecture Specification

## 1. High-Level Architecture Diagram

```text
+------------------------------------+     +----------------------------------+
|  Online REST APIs (Weather, Tide)  |     |   MQTT Sensors / Python Emulator |
+------------------------------------+     +----------------------------------+
                  |                                         |
            (HTTP GET)                                (MQTT Publish)
                  |                                         |
                  v                                         v
+-----------------------------------------------------------------------------+
|                               Node-RED Core                                 |
|                                                                             |
|   +-----------------------+                 +---------------------------+   |
|   |  HTTP Request Nodes   |                 |      MQTT In Nodes        |   |
|   +-----------------------+                 +---------------------------+   |
|               |                                           |                 |
|               +---------------------+---------------------+                 |
|                                     |                                       |
|                                     v                                       |
|                       +---------------------------+                         |
|                       |  Data Processing Node     |                         |
|                       |  (Validate & Transform)   |                         |
|                       +---------------------------+                         |
|                                     |                                       |
|                                     v                                       |
|                       +---------------------------+                         |
|                       | Node-RED Dashboard Engine |                         |
|                       +---------------------------+                         |
+-----------------------------------------------------------------------------+
                                      |
                             (WebSocket Streaming)
                                      |
                                      v
                        +---------------------------+
                        |   Dashboard UI (/ui)      |
                        +---------------------------+
```

---

## 2. Component Breakdown

1. **Node-RED Runtime:** Flow orchestration engine managing scheduling, data transformations, and state persistence.
2. **Mosquitto MQTT Broker:** Message broker running on port `1883` handling pub/sub message transfer for local or simulated sensor feeds.
3. **Data Ingestion Pipeline:**
   - **HTTP Nodes:** Poll remote weather/ocean APIs at scheduled intervals (e.g., every 15 minutes).
   - **MQTT In Nodes:** Subscribe to `smartfishing/#` topics for incoming sensor readings.
4. **Validation & Transformation Layer:** Function nodes running ECMAScript routines to scrub missing values, format dates, convert units, and handle errors gracefully.
5. **UI Rendering Engine:** `@node-red/node-red-dashboard` serving dynamic frontend components via WebSockets.

---

## 3. Data Schema & Topics

### MQTT Telemetry Topic Convention

`smartfishing/<location_id>/<metric_type>`

#### Sample Payload (`smartfishing/node-01/telemetry`)

```json
{
  "device_id": "sensor-01",
  "timestamp": "2026-10-31T10:30:00Z",
  "water_temperature": 27.4,
  "water_level": 1.8,
  "battery_voltage": 3.7
}
```

### Flow Schema Transformation

Incoming payloads are standardizing into internal unified msg format before UI emission:

```javascript
msg.payload = {
    value: Number(msg.payload.water_temperature),
    unit: "C",
    timestamp: new Date().toISOString(),
    status: "OK"
};
return msg;
```