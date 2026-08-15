from datetime import date

from app.services.weather_history import (
    get_historical_weather,
)


def test_get_historical_weather():

    result = get_historical_weather(
        latitude=17.3850,
        longitude=78.4867,
        start_date=date(2024, 6, 1),
        end_date=date(2024, 6, 7),
    )

    assert result

    assert "time" in result

    assert (
        "temperature_2m_mean"
        in result
    )

    assert (
        "precipitation_sum"
        in result
    )