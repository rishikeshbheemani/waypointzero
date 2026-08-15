from datetime import date

import requests


HISTORICAL_WEATHER_URL = (
    "https://archive-api.open-meteo.com/v1/archive"
)


def get_historical_weather(
    latitude: float,
    longitude: float,
    start_date: date,
    end_date: date,
) -> dict:
    """
    Retrieve historical weather data for a location.

    Used to understand typical weather patterns,
    not to make a future point forecast.
    """

    if end_date < start_date:
        raise ValueError(
            "end_date must be after start_date"
        )

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "daily": (
            "temperature_2m_mean,"
            "temperature_2m_max,"
            "temperature_2m_min,"
            "precipitation_sum,"
            "rain_sum"
        ),
        "timezone": "auto",
        "temperature_unit": "celsius",
        "precipitation_unit": "mm",
    }

    response = requests.get(
        HISTORICAL_WEATHER_URL,
        params=params,
        timeout=20,
    )

    response.raise_for_status()

    data = response.json()

    return data.get(
        "daily",
        {},
    )