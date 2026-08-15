from app.services.weather_processor import (
    process_weather_forecast,
)


def test_process_weather_forecast():

    raw_forecasts = [
        {
            "date": "2026-10-10",
            "temperature_max_celsius": 28.5,
            "temperature_min_celsius": 21.0,
            "precipitation_probability": 70,
            "precipitation_mm": 12.4,
            "humidity_percent": 82,
            "wind_speed_kmh": 14.5,
            "weather_code": 63,
        }
    ]

    result = process_weather_forecast(
        raw_forecasts
    )

    assert len(result) == 1

    forecast = result[0]

    assert (
        forecast.temperature_max_celsius
        == 28.5
    )

    assert (
        forecast.temperature_min_celsius
        == 21.0
    )

    assert (
        forecast.precipitation_probability
        == 70
    )

    assert forecast.weather_code == 63

    assert (
        forecast.weather_description
        == "Moderate rain"
    )


def test_process_empty_forecast():

    result = process_weather_forecast([])

    assert result == []


def test_process_missing_date():

    raw_forecasts = [
        {
            "temperature_max_celsius": 30.0,
            "weather_code": 0,
        }
    ]

    result = process_weather_forecast(
        raw_forecasts
    )

    assert result == []