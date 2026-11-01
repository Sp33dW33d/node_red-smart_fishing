"""Maintain a local rolling cache of recent Open-Meteo weather and marine history."""

from __future__ import annotations

import json
import logging
import math
import os
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen


LOGGER = logging.getLogger("smart-fishing-history-cache")
CACHE_PATH = Path(os.getenv("HISTORY_CACHE_PATH", "/cache/history-7d.json"))
WINDOW_DAYS = 7
TIMEZONE = "UTC"
USER_AGENT = "smart-fishing-history-cache/1.0"


def api_url(base: str, params: dict[str, str]) -> str:
    parsed = urlsplit(base)
    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    query.update(params)
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urlencode(query), parsed.fragment))


def get_json(url: str) -> dict[str, Any]:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(request, timeout=30) as response:
            payload = json.load(response)
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"Open-Meteo returned HTTP {exc.code}: {detail}") from exc
    except (URLError, TimeoutError) as exc:
        raise RuntimeError(f"Open-Meteo request failed: {exc}") from exc
    if not isinstance(payload, dict) or payload.get("error"):
        reason = payload.get("reason", "invalid JSON response") if isinstance(payload, dict) else "invalid JSON response"
        raise RuntimeError(f"Open-Meteo returned an error: {reason}")
    return payload


def number(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def stats(values: list[Any]) -> dict[str, float | int] | None:
    clean = [value for raw in values if (value := number(raw)) is not None]
    if not clean:
        return None
    return {
        "mean": round(sum(clean) / len(clean), 3),
        "min": round(min(clean), 3),
        "max": round(max(clean), 3),
        "samples": len(clean),
    }


def api_base(name: str, default: str) -> str:
    return os.getenv(name, default).strip()


def location_info() -> dict[str, Any]:
    latitude = number(os.getenv("LOCATION_LATITUDE", "18.9110"))
    longitude = number(os.getenv("LOCATION_LONGITUDE", "72.8253"))
    if latitude is None or longitude is None or not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
        raise ValueError("LOCATION_LATITUDE and LOCATION_LONGITUDE must be valid coordinates")
    return {
        "name": os.getenv("LOCATION_NAME", "Sassoon Dock, Mumbai"),
        "latitude": latitude,
        "longitude": longitude,
    }


def new_cache(location: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": 1,
        "windowDays": WINDOW_DAYS,
        "timezone": TIMEZONE,
        "location": location,
        "windowStart": None,
        "windowEnd": None,
        "updatedAt": None,
        "days": [],
    }


def load_cache(location: dict[str, Any]) -> dict[str, Any]:
    if not CACHE_PATH.exists():
        LOGGER.info("No history cache found; bootstrapping the seven-day window")
        return new_cache(location)
    try:
        cache = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        LOGGER.warning("Cannot read history cache; rebuilding it: %s", exc)
        return new_cache(location)
    if (
        not isinstance(cache, dict)
        or cache.get("schemaVersion") != 1
        or cache.get("location") != location
        or not isinstance(cache.get("days"), list)
    ):
        LOGGER.info("History cache schema or location changed; rebuilding the window")
        return new_cache(location)
    return cache


def missing_ranges(missing_dates: list[date]) -> list[tuple[date, date]]:
    if not missing_dates:
        return []
    ordered = sorted(set(missing_dates))
    ranges: list[tuple[date, date]] = []
    start = previous = ordered[0]
    for current in ordered[1:]:
        if current == previous + timedelta(days=1):
            previous = current
            continue
        ranges.append((start, previous))
        start = previous = current
    ranges.append((start, previous))
    return ranges


def date_keys(start: date, end: date) -> list[str]:
    result: list[str] = []
    current = start
    while current <= end:
        result.append(current.isoformat())
        current += timedelta(days=1)
    return result


def weather_records(start: date, end: date, location: dict[str, Any]) -> dict[str, dict[str, Any]]:
    base = api_base("WEATHER_API_URL", "https://api.open-meteo.com/v1/forecast")
    params = {
        "latitude": str(location["latitude"]),
        "longitude": str(location["longitude"]),
        "daily": "temperature_2m_mean,temperature_2m_min,temperature_2m_max,wind_speed_10m_max,rain_sum,precipitation_sum",
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "timezone": TIMEZONE,
        "temperature_unit": "celsius",
        "wind_speed_unit": "kmh",
        "precipitation_unit": "mm",
    }
    payload = get_json(api_url(base, params))
    daily = payload.get("daily")
    if not isinstance(daily, dict) or not isinstance(daily.get("time"), list):
        raise RuntimeError("Weather history response is missing daily dates")
    records: dict[str, dict[str, Any]] = {}
    for index, key in enumerate(daily["time"]):
        if key not in date_keys(start, end):
            continue

        def value(field: str) -> Any:
            values = daily.get(field)
            return values[index] if isinstance(values, list) and index < len(values) else None

        weather = {
            "airTemperatureC": {
                "mean": number(value("temperature_2m_mean")),
                "min": number(value("temperature_2m_min")),
                "max": number(value("temperature_2m_max")),
            },
            "windSpeedKmh": {
                "max": number(value("wind_speed_10m_max")),
            },
            "rainfallMm": number(value("rain_sum")),
            "precipitationMm": number(value("precipitation_sum")),
        }
        if any(metric_value is not None for metric in weather.values() for metric_value in (metric.values() if isinstance(metric, dict) else [metric])):
            records[key] = weather
    return records


def marine_records(start: date, end: date, location: dict[str, Any]) -> dict[str, dict[str, Any]]:
    base = api_base("MARINE_API_URL", "https://marine-api.open-meteo.com/v1/marine")
    params = {
        "latitude": str(location["latitude"]),
        "longitude": str(location["longitude"]),
        "hourly": "sea_surface_temperature,sea_level_height_msl,wave_height",
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "timezone": TIMEZONE,
        "cell_selection": "sea",
    }
    payload = get_json(api_url(base, params))
    hourly = payload.get("hourly")
    times = hourly.get("time") if isinstance(hourly, dict) else None
    if not isinstance(hourly, dict) or not isinstance(times, list):
        raise RuntimeError("Marine history response is missing hourly timestamps")
    allowed_dates = set(date_keys(start, end))
    by_date: dict[str, dict[str, list[Any]]] = {}
    variables = ("sea_surface_temperature", "sea_level_height_msl", "wave_height")
    for index, timestamp in enumerate(times):
        key = timestamp[:10] if isinstance(timestamp, str) else ""
        if key not in allowed_dates:
            continue
        samples = by_date.setdefault(key, {variable: [] for variable in variables})
        for variable in variables:
            values = hourly.get(variable)
            samples[variable].append(values[index] if isinstance(values, list) and index < len(values) else None)

    records: dict[str, dict[str, Any]] = {}
    for key, samples in by_date.items():
        marine = {
            "seaSurfaceTemperatureC": stats(samples["sea_surface_temperature"]),
            "seaLevelHeightMslM": stats(samples["sea_level_height_msl"]),
            "waveHeightM": stats(samples["wave_height"]),
        }
        if any(marine.values()):
            records[key] = marine
    return records


def save_cache(cache: dict[str, Any]) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CACHE_PATH.open("w", encoding="utf-8", newline="\n") as output:
        json.dump(cache, output, indent=2, ensure_ascii=False, allow_nan=False)
        output.write("\n")


def refresh_cache() -> None:
    location = location_info()
    today = datetime.now(timezone.utc).date()
    # Keep seven completed UTC calendar days; today's partial values are not historical reports.
    expected_dates = [today - timedelta(days=offset) for offset in range(WINDOW_DAYS, 0, -1)]
    expected_keys = {day.isoformat() for day in expected_dates}
    cache = load_cache(location)
    old_days = cache.get("days", [])
    records = {
        row["date"]: row
        for row in old_days
        if isinstance(row, dict) and row.get("date") in expected_keys
    }
    changed = len(records) != len(old_days)
    for key in expected_keys:
        records.setdefault(key, {"date": key})

    weather_missing = [day for day in expected_dates if not isinstance(records[day.isoformat()].get("weather"), dict)]
    marine_missing = [day for day in expected_dates if not isinstance(records[day.isoformat()].get("marine"), dict)]

    for start, end in missing_ranges(weather_missing):
        LOGGER.info("Weather history cache miss: fetching %s through %s", start, end)
        try:
            fetched = weather_records(start, end, location)
            for key, weather in fetched.items():
                records[key]["weather"] = weather
                changed = True
            absent = set(date_keys(start, end)) - set(fetched)
            if absent:
                LOGGER.warning("Weather API has no data yet for: %s", ", ".join(sorted(absent)))
        except Exception:
            LOGGER.exception("Weather history fetch failed for %s through %s", start, end)

    for start, end in missing_ranges(marine_missing):
        LOGGER.info("Marine history cache miss: fetching %s through %s", start, end)
        try:
            fetched = marine_records(start, end, location)
            for key, marine in fetched.items():
                records[key]["marine"] = marine
                changed = True
            absent = set(date_keys(start, end)) - set(fetched)
            if absent:
                LOGGER.warning("Marine API has no data yet for: %s", ", ".join(sorted(absent)))
        except Exception:
            LOGGER.exception("Marine history fetch failed for %s through %s", start, end)

    cache["schemaVersion"] = 1
    cache["windowDays"] = WINDOW_DAYS
    cache["timezone"] = TIMEZONE
    cache["location"] = location
    cache["windowStart"] = expected_dates[0].isoformat()
    cache["windowEnd"] = expected_dates[-1].isoformat()
    cache["days"] = [records[key] for key in sorted(expected_keys)]
    if changed or not CACHE_PATH.exists():
        cache["updatedAt"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        save_cache(cache)
    weather_count = sum(isinstance(row.get("weather"), dict) for row in cache["days"])
    marine_count = sum(isinstance(row.get("marine"), dict) for row in cache["days"])
    LOGGER.info(
        "History cache coverage: weather %d/%d days, marine %d/%d days (%s to %s)",
        weather_count,
        WINDOW_DAYS,
        marine_count,
        WINDOW_DAYS,
        cache["windowStart"],
        cache["windowEnd"],
    )


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    try:
        interval = max(300, int(os.getenv("HISTORY_CACHE_INTERVAL_SECONDS", "3600")))
    except ValueError:
        LOGGER.error("HISTORY_CACHE_INTERVAL_SECONDS must be an integer")
        return 2
    LOGGER.info("Starting seven-day history cache; refresh check every %d seconds", interval)
    while True:
        try:
            refresh_cache()
        except Exception:
            LOGGER.exception("History cache refresh failed")
        time.sleep(interval)


if __name__ == "__main__":
    raise SystemExit(main())
