from datetime import date

from app.services.weather_api import (
    get_weather_forecast,
)


def test_get_weather_forecast():

    forecasts = get_weather_forecast(
        latitude=17.3850,
        longitude=78.4867,
        start_date=date.today(),
        duration_days=3,
    )

    assert len(forecasts) > 0

    first_day = forecasts[0]

    assert first_day["date"]
    assert (
        first_day["temperature_max_celsius"]
        is not None
    )
    assert (
        first_day["temperature_min_celsius"]
        is not None
    )
    assert (
        first_day["precipitation_probability"]
        is not None
    )