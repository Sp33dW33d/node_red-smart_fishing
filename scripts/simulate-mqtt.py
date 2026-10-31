"""Publish synthetic Smart Fishing telemetry to a local MQTT broker."""

from __future__ import annotations

import argparse
import json
import logging
import math
import os
import random
import signal
import threading
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt


LOGGER = logging.getLogger("smart-fishing-simulator")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--host",
        default=os.getenv("MQTT_PUBLISHER_HOST", "127.0.0.1"),
        help="Broker address from the machine running this script (default: 127.0.0.1).",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("MQTT_PUBLISHER_PORT", os.getenv("MQTT_PORT", "1883"))),
        help="Broker port (default: MQTT_PORT or 1883).",
    )
    parser.add_argument(
        "--topic-prefix",
        default=os.getenv("MQTT_TOPIC_PREFIX", "smartfishing"),
        help="Root of the telemetry topic (default: smartfishing).",
    )
    parser.add_argument(
        "--device-id",
        default=os.getenv("MQTT_DEVICE_ID", "demo-01"),
        help="Simulated device identifier (default: demo-01).",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=5.0,
        help="Seconds between messages; must be greater than zero (default: 5).",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=0,
        help="Number of messages to publish; 0 runs until interrupted (default: 0).",
    )
    return parser


def make_payload(device_id: str, sequence: int, catch_count: int) -> dict[str, object]:
    """Build one realistic-looking, timestamped sample for development only."""
    phase = sequence / 5.0
    return {
        "device_id": device_id,
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds").replace(
            "+00:00", "Z"
        ),
        "water_temperature_c": round(27.0 + math.sin(phase) * 0.6 + random.uniform(-0.15, 0.15), 2),
        "water_level_m": round(1.4 + math.sin(phase / 1.5) * 0.08 + random.uniform(-0.02, 0.02), 3),
        "catch_count": catch_count,
        "battery_voltage_v": round(3.75 + random.uniform(-0.04, 0.04), 2),
    }


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    args = build_parser().parse_args()
    if not args.host.strip():
        LOGGER.error("Broker host cannot be empty")
        return 2
    if not 1 <= args.port <= 65535:
        LOGGER.error("Broker port must be between 1 and 65535")
        return 2
    if not args.topic_prefix.strip("/") or not args.device_id.strip("/"):
        LOGGER.error("Topic prefix and device ID cannot be empty")
        return 2
    if args.interval <= 0:
        LOGGER.error("Interval must be greater than zero")
        return 2
    if args.count < 0:
        LOGGER.error("Count cannot be negative")
        return 2

    topic = f"{args.topic_prefix.strip('/')}/{args.device_id.strip('/')}/telemetry"
    if "+" in topic or "#" in topic:
        LOGGER.error("MQTT publish topics cannot contain '+' or '#' wildcards")
        return 2
    connection_result = threading.Event()
    connection_failed = threading.Event()

    def on_connect(
        _client: mqtt.Client,
        _userdata: object,
        _flags: mqtt.ConnectFlags,
        reason_code: mqtt.ReasonCode,
        _properties: mqtt.Properties | None,
    ) -> None:
        if reason_code.is_failure:
            connection_failed.set()
            connection_result.set()
            LOGGER.error("Broker rejected the connection: %s", reason_code)
        else:
            connection_result.set()
            LOGGER.info("Connected to MQTT broker at %s:%d", args.host, args.port)

    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id=f"smart-fishing-{args.device_id}",
        protocol=mqtt.MQTTv311,
    )
    client.on_connect = on_connect

    try:
        client.connect(args.host, args.port, keepalive=60)
        client.loop_start()
        if not connection_result.wait(timeout=10):
            LOGGER.error("Timed out waiting for the broker connection")
            return 1
        if connection_failed.is_set():
            return 1

        catch_count = 0
        sequence = 0
        stopping = threading.Event()

        def request_stop(_signum: int, _frame: object) -> None:
            stopping.set()

        signal.signal(signal.SIGINT, request_stop)
        if hasattr(signal, "SIGTERM"):
            signal.signal(signal.SIGTERM, request_stop)

        while not stopping.is_set() and (args.count == 0 or sequence < args.count):
            if random.random() < 0.08:
                catch_count += 1
            payload = make_payload(args.device_id, sequence, catch_count)
            info = client.publish(topic, json.dumps(payload), qos=1, retain=False)
            if info.rc != mqtt.MQTT_ERR_SUCCESS:
                LOGGER.error("Publish failed for %s: %s", topic, mqtt.error_string(info.rc))
                return 1
            info.wait_for_publish(timeout=10)
            if not info.is_published():
                LOGGER.error("Timed out waiting for publish acknowledgement on %s", topic)
                return 1
            sequence += 1
            LOGGER.info("Published %s (%d): %s", topic, sequence, json.dumps(payload))
            if args.count == 0 or sequence < args.count:
                stopping.wait(args.interval)
    except (OSError, ValueError, mqtt.MQTTException) as exc:
        LOGGER.error("Could not connect or publish to %s:%d: %s", args.host, args.port, exc)
        return 1
    except KeyboardInterrupt:
        LOGGER.info("Stopping telemetry publisher")
    finally:
        if client.is_connected():
            client.disconnect()
        client.loop_stop()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
