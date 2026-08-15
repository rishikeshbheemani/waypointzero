from datetime import date

from app.schemas.travel import WeatherForecast
from app.services.weather_codes import describe_weather_code


def process_weather_forecast(
    raw_forecasts: list[dict],
) -> list[WeatherForecast]:
    """
    Convert raw Open-Meteo forecast dictionaries into
    validated WeatherForecast Pydantic objects.

    Also converts the numerical WMO weather code into
    a human-readable description.
    """

    processed_forecasts = []

    for item in raw_forecasts:
        raw_date = item.get("date")

        if not raw_date:
            continue

        if isinstance(raw_date, str):
            forecast_date = date.fromisoformat(
                raw_date
            )
        else:
            forecast_date = raw_date

        weather_code = item.get(
            "weather_code"
        )

        forecast = WeatherForecast(
            date=forecast_date,

            temperature_max_celsius=item.get(
                "temperature_max_celsius"
            ),

            temperature_min_celsius=item.get(
                "temperature_min_celsius"
            ),

            precipitation_probability=item.get(
                "precipitation_probability"
            ),

            precipitation_mm=item.get(
                "precipitation_mm"
            ),

            humidity_percent=item.get(
                "humidity_percent"
            ),

            wind_speed_kmh=item.get(
                "wind_speed_kmh"
            ),

            weather_code=weather_code,

            weather_description=(
                describe_weather_code(
                    weather_code
                )
            ),
        )

        processed_forecasts.append(
            forecast
        )

    return processed_forecasts