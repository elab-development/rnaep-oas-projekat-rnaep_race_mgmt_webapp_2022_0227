from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock

import httpx
import pytest

from app.services import weather_service


async def test_returns_unavailable_for_race_too_far_in_the_future(monkeypatch):
    geocode = AsyncMock()
    monkeypatch.setattr(weather_service, "_geocode_location", geocode)

    race_date = datetime.now(timezone.utc) + timedelta(days=30)
    result = await weather_service.get_race_day_weather("Belgrade", race_date)

    assert result["available"] is False
    assert "16 days" in result["reason"]
    geocode.assert_not_awaited()


async def test_returns_unavailable_for_race_in_the_past(monkeypatch):
    geocode = AsyncMock()
    monkeypatch.setattr(weather_service, "_geocode_location", geocode)

    race_date = datetime.now(timezone.utc) - timedelta(days=1)
    result = await weather_service.get_race_day_weather("Belgrade", race_date)

    assert result["available"] is False
    geocode.assert_not_awaited()


async def test_returns_unavailable_when_location_cannot_be_geocoded(monkeypatch):
    monkeypatch.setattr(weather_service, "_geocode_location", AsyncMock(return_value=None))
    monkeypatch.setattr(weather_service, "_fetch_forecast", AsyncMock())

    race_date = datetime.now(timezone.utc) + timedelta(days=2)
    result = await weather_service.get_race_day_weather("Nowhereville", race_date)

    assert result["available"] is False
    assert "Nowhereville" in result["reason"]


async def test_returns_forecast_when_available(monkeypatch):
    monkeypatch.setattr(weather_service, "_geocode_location", AsyncMock(return_value=(44.8, 20.4)))
    monkeypatch.setattr(
        weather_service,
        "_fetch_forecast",
        AsyncMock(
            return_value={
                "temperature_max_c": 28.5,
                "temperature_min_c": 16.2,
                "precipitation_probability_percent": 20,
                "weather_code": 1,
            }
        ),
    )

    race_date = datetime.now(timezone.utc) + timedelta(days=2)
    result = await weather_service.get_race_day_weather("Belgrade", race_date)

    assert result["available"] is True
    assert result["temperature_max_c"] == 28.5
    assert result["weather_description"] == "Mostly clear"


async def test_returns_unavailable_on_http_error(monkeypatch):
    async def _raise(*args, **kwargs):
        raise httpx.ConnectError("network down")

    monkeypatch.setattr(weather_service, "_geocode_location", _raise)

    race_date = datetime.now(timezone.utc) + timedelta(days=2)
    result = await weather_service.get_race_day_weather("Belgrade", race_date)

    assert result["available"] is False
    assert "unavailable" in result["reason"]


async def test_geocode_and_fetch_forecast_build_correct_requests():
    # Exercises the real request/response handling against a fake transport,
    # without touching the real Open-Meteo API.
    def handler(request: httpx.Request) -> httpx.Response:
        if "geocoding-api" in str(request.url):
            assert request.url.params["name"] == "Belgrade"
            return httpx.Response(200, json={"results": [{"latitude": 44.8, "longitude": 20.4}]})
        assert request.url.params["latitude"] == "44.8"
        assert request.url.params["longitude"] == "20.4"
        return httpx.Response(
            200,
            json={
                "daily": {
                    "time": ["2026-01-01"],
                    "temperature_2m_max": [10.0],
                    "temperature_2m_min": [2.0],
                    "precipitation_probability_max": [5],
                    "weathercode": [0],
                }
            },
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        coordinates = await weather_service._geocode_location(client, "Belgrade")
        assert coordinates == (44.8, 20.4)

        forecast = await weather_service._fetch_forecast(client, 44.8, 20.4, datetime(2026, 1, 1).date())
        assert forecast == {
            "temperature_max_c": 10.0,
            "temperature_min_c": 2.0,
            "precipitation_probability_percent": 5,
            "weather_code": 0,
        }
