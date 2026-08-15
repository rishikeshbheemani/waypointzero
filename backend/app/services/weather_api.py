from datetime import date, timedelta

import requests


WEATHER_URL = (
    "https://api.open-meteo.com/v1/forecast"
)


DAILY_VARIABLES = ",".join(
    [
        "temperature_2m_max",
        "temperature_2m_min",
        "precipitation_probability_max",
        "precipitation_sum",
        "relative_humidity_2m_max",
        "wind_speed_10m_max",
        "weather_code",
        "sunrise",
        "sunset",
    ]
)


def get_weather_forecast(
    latitude: float,
    longitude: float,
    start_date: date,
    duration_days: int,
) -> list[dict]:
    """
    Retrieve daily weather forecast for a trip.

    The forecast API is intended for near-term forecasting.
    If the requested trip extends beyond the available
    forecast window, the API may not be able to provide
    the requested dates.

    Returns a list of daily weather dictionaries.
    """

    if duration_days <= 0:
        raise ValueError(
            "duration_days must be greater than 0"
        )

    end_date = (
        start_date
        + timedelta(days=duration_days - 1)
    )

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": DAILY_VARIABLES,
        "timezone": "auto",
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "temperature_unit": "celsius",
        "wind_speed_unit": "kmh",
        "precipitation_unit": "mm",
    }

    response = requests.get(
        WEATHER_URL,
        params=params,
        timeout=15,
    )

    response.raise_for_status()

    data = response.json()

    daily = data.get("daily")

    if not daily:
        return []

    dates = daily.get("time", [])

    forecasts = []

    for index, forecast_date in enumerate(
        dates
    ):
        forecasts.append(
            {
                "date": forecast_date,
                "temperature_max_celsius": _get_value(
                    daily,
                    "temperature_2m_max",
                    index,
                ),
                "temperature_min_celsius": _get_value(
                    daily,
                    "temperature_2m_min",
                    index,
                ),
                "precipitation_probability": _get_value(
                    daily,
                    "precipitation_probability_max",
                    index,
                ),
                "precipitation_mm": _get_value(
                    daily,
                    "precipitation_sum",
                    index,
                ),
                "humidity_percent": _get_value(
                    daily,
                    "relative_humidity_2m_max",
                    index,
                ),
                "wind_speed_kmh": _get_value(
                    daily,
                    "wind_speed_10m_max",
                    index,
                ),
                "weather_code": _get_value(
                    daily,
                    "weather_code",
                    index,
                ),
                "sunrise": _get_value(
                    daily,
                    "sunrise",
                    index,
                ),
                "sunset": _get_value(
                    daily,
                    "sunset",
                    index,
                ),
            }
        )

    return forecasts


def _get_value(
    data: dict,
    key: str,
    index: int,
):
    """
    Safely retrieve an indexed value from
    an Open-Meteo response.
    """

    values = data.get(key, [])

    if index >= len(values):
        return None

    return values[index]