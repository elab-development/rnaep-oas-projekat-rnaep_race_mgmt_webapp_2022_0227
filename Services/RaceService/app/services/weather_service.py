import logging
from datetime import date, datetime, timedelta, timezone

import httpx

logger = logging.getLogger(__name__)

# Open-Meteo (https://github.com/open-meteo/open-meteo) - open-source, free,
# no API key required. Used to show a weather forecast for race day.
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
FORECAST_HORIZON_DAYS = 16

WEATHER_CODE_DESCRIPTIONS = {
    0: "Clear sky",
    1: "Mostly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


async def _geocode_location(client: httpx.AsyncClient, location: str) -> tuple[float, float] | None:
    response = await client.get(GEOCODING_URL, params={"name": location, "count": 1})
    response.raise_for_status()
    results = response.json().get("results")
    if not results:
        return None
    return results[0]["latitude"], results[0]["longitude"]


async def _fetch_forecast(
    client: httpx.AsyncClient, latitude: float, longitude: float, target_date: date
) -> dict | None:
    response = await client.get(
        FORECAST_URL,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max,weathercode",
            "timezone": "auto",
            "start_date": target_date.isoformat(),
            "end_date": target_date.isoformat(),
        },
    )
    response.raise_for_status()
    daily = response.json().get("daily")
    if not daily or not daily.get("time"):
        return None
    return {
        "temperature_max_c": daily["temperature_2m_max"][0],
        "temperature_min_c": daily["temperature_2m_min"][0],
        "precipitation_probability_percent": daily["precipitation_probability_max"][0],
        "weather_code": daily["weathercode"][0],
    }


async def get_race_day_weather(location: str, race_date: datetime) -> dict:
    target_date = race_date.date()
    today = datetime.now(timezone.utc).date()

    if target_date < today or (target_date - today) > timedelta(days=FORECAST_HORIZON_DAYS):
        return {
            "available": False,
            "reason": f"Weather forecast is only available within {FORECAST_HORIZON_DAYS} days of the race date.",
        }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            coordinates = await _geocode_location(client, location)
            if not coordinates:
                return {"available": False, "reason": f"Could not find location '{location}'."}

            forecast = await _fetch_forecast(client, coordinates[0], coordinates[1], target_date)
    except httpx.HTTPError:
        logger.error("Open-Meteo request failed", exc_info=True)
        return {"available": False, "reason": "Weather service is temporarily unavailable."}

    if not forecast:
        return {"available": False, "reason": "Forecast data is not available for this date."}

    return {
        "available": True,
        "date": target_date.isoformat(),
        "location": location,
        "temperature_max_c": forecast["temperature_max_c"],
        "temperature_min_c": forecast["temperature_min_c"],
        "precipitation_probability_percent": forecast["precipitation_probability_percent"],
        "weather_description": WEATHER_CODE_DESCRIPTIONS.get(forecast["weather_code"], "Unknown"),
    }
