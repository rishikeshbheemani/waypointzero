from datetime import date

from app.schemas.travel import WeatherForecast, WeatherInfo


def test_weather_models():

    forecast = WeatherForecast(
        date=date(2026, 10, 10),
        temperature_max_celsius=28.5,
        temperature_min_celsius=21.0,
        precipitation_probability=70,
        precipitation_mm=12.4,
        humidity_percent=82,
        wind_speed_kmh=14.5,
        weather_description="Light rain",
    )

    weather = WeatherInfo(
        location="Cherrapunji",
        latitude=25.27,
        longitude=91.73,
        timezone="Asia/Kolkata",
        forecast=[forecast],
        seasonal_context=[
            "Frequent rainfall is typical during the monsoon."
        ],
        travel_impact=[
            "Outdoor activities may be affected by rain."
        ],
        recommendations=[
            "Carry waterproof clothing."
        ],
    )

    assert weather.location == "Cherrapunji"
    assert len(weather.forecast) == 1
    assert weather.forecast[0].precipitation_probability == 70