from datetime import date
from unittest.mock import patch

from app.agents.weather import run_weather_agent
from app.schemas.travel import TripRequest, WeatherInfo


def test_weather_agent_with_date():

    trip_request = TripRequest(
        destination="Hyderabad",
        duration_days=3,
        start_date=date.today(),
    )

    mock_location = [
        {
            "name": "Hyderabad",
            "latitude": 17.3850,
            "longitude": 78.4867,
            "timezone": "Asia/Kolkata",
            "country": "India",
            "admin1": "Telangana",
        }
    ]

    mock_forecast = [
        {
            "date": date.today().isoformat(),
            "temperature_max_celsius": 32.0,
            "temperature_min_celsius": 24.0,
            "precipitation_probability": 70,
            "precipitation_mm": 8.0,
            "humidity_percent": 80,
            "wind_speed_kmh": 15.0,
            "weather_code": 63,
        }
    ]

    mock_history = {
        "time": [
            date.today().isoformat()
        ],
        "temperature_2m_mean": [28.0],
        "precipitation_sum": [12.0],
        "rain_sum": [12.0],
    }

    with patch(
        "app.agents.weather.geocode_location",
        return_value=mock_location,
    ), patch(
        "app.agents.weather.get_weather_forecast",
        return_value=mock_forecast,
    ), patch(
        "app.agents.weather.get_historical_weather",
        return_value=mock_history,
    ):

        result = run_weather_agent(
            trip_request
        )

    assert isinstance(
        result,
        WeatherInfo,
    )

    assert result.location == "Hyderabad"

    assert len(result.forecast) == 1

    assert (
        result.forecast[0]
        .weather_description
        == "Moderate rain"
    )

    assert len(
        result.seasonal_context
    ) > 0

    assert len(
        result.travel_impact
    ) > 0

    assert len(
        result.recommendations
    ) > 0


def test_weather_agent_without_date():

    trip_request = TripRequest(
        destination="Cherrapunji",
        duration_days=5,
    )

    mock_location = [
        {
            "name": "Cherrapunji",
            "latitude": 25.27,
            "longitude": 91.73,
            "timezone": "Asia/Kolkata",
            "country": "India",
            "admin1": "Meghalaya",
        }
    ]

    with patch(
        "app.agents.weather.geocode_location",
        return_value=mock_location,
    ):

        result = run_weather_agent(
            trip_request
        )

    assert isinstance(
        result,
        WeatherInfo,
    )

    assert result.location == "Cherrapunji"

    assert result.forecast == []

    assert len(
        result.warnings
    ) > 0

    assert any(
        "travel date" in warning.lower()
        for warning in result.warnings
    )