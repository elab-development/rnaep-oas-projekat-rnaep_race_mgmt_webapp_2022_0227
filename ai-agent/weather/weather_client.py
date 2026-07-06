"""Second external data source: a sync client for the same Open-Meteo API used by
RaceService's own weather_service.py, kept independent here since this agent is a
standalone tool with its own dependency footprint.
"""
import requests

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

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


class WeatherUnavailableError(Exception):
    pass


def get_forecast(location: str, date_str: str) -> dict:
    """date_str must be 'YYYY-MM-DD'. Raises WeatherUnavailableError if it can't be fetched."""
    try:
        geo_resp = requests.get(GEOCODING_URL, params={"name": location, "count": 1}, timeout=10)
        geo_resp.raise_for_status()
        results = geo_resp.json().get("results")
        if not results:
            raise WeatherUnavailableError(f"Could not find location '{location}'")
        lat, lon = results[0]["latitude"], results[0]["longitude"]

        forecast_resp = requests.get(
            FORECAST_URL,
            params={
                "latitude": lat,
                "longitude": lon,
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max,weathercode",
                "timezone": "auto",
                "start_date": date_str,
                "end_date": date_str,
            },
            timeout=10,
        )
        forecast_resp.raise_for_status()
        daily = forecast_resp.json().get("daily")
        if not daily or not daily.get("time"):
            raise WeatherUnavailableError(
                "Forecast not available for this date (likely more than 16 days out, or in the past)"
            )

        return {
            "temperature_max_c": daily["temperature_2m_max"][0],
            "temperature_min_c": daily["temperature_2m_min"][0],
            "precipitation_probability_percent": daily["precipitation_probability_max"][0],
            "weather_description": WEATHER_CODE_DESCRIPTIONS.get(daily["weathercode"][0], "Unknown"),
        }
    except requests.RequestException as e:
        raise WeatherUnavailableError(f"Weather service request failed: {e}") from e
