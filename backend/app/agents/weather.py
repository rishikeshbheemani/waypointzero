from datetime import date, timedelta

from app.schemas.travel import (
    TripRequest,
    WeatherInfo,
)
from app.services.geocoding import geocode_location
from app.services.weather_api import get_weather_forecast
from app.services.weather_history import (
    get_historical_weather,
)
from app.services.weather_processor import (
    process_weather_forecast,
)


def _build_seasonal_context(
    historical_data: dict,
) -> list[str]:
    """
    Build simple seasonal observations from
    historical weather data.

    This is intentionally deterministic.
    """

    precipitation = historical_data.get(
        "precipitation_sum",
        [],
    )

    temperatures = historical_data.get(
        "temperature_2m_mean",
        [],
    )

    context = []

    valid_precipitation = [
        value
        for value in precipitation
        if value is not None
    ]

    valid_temperatures = [
        value
        for value in temperatures
        if value is not None
    ]

    if valid_precipitation:

        average_precipitation = (
            sum(valid_precipitation)
            / len(valid_precipitation)
        )

        if average_precipitation >= 10:
            context.append(
                "This period has historically "
                "experienced frequent or substantial "
                "precipitation."
            )

        elif average_precipitation >= 3:
            context.append(
                "This period has historically "
                "experienced moderate precipitation."
            )

        else:
            context.append(
                "This period has historically "
                "experienced relatively low "
                "precipitation."
            )

    if valid_temperatures:

        average_temperature = (
            sum(valid_temperatures)
            / len(valid_temperatures)
        )

        context.append(
            f"Historical average temperature "
            f"for the analyzed period is approximately "
            f"{average_temperature:.1f}°C."
        )

    return context


def _build_travel_impact(
    forecasts,
) -> list[str]:
    """
    Identify weather conditions that may affect
    travel plans.
    """

    impacts = []

    heavy_rain_days = [
        forecast
        for forecast in forecasts
        if (
            forecast.precipitation_probability
            is not None
            and forecast.precipitation_probability
            >= 70
        )
    ]

    high_wind_days = [
        forecast
        for forecast in forecasts
        if (
            forecast.wind_speed_kmh
            is not None
            and forecast.wind_speed_kmh
            >= 40
        )
    ]

    severe_weather_days = [
        forecast
        for forecast in forecasts
        if forecast.weather_code in {
            95,
            96,
            99,
        }
    ]

    if heavy_rain_days:
        impacts.append(
            "Rain may affect outdoor activities "
            "during some days of the trip."
        )

    if high_wind_days:
        impacts.append(
            "Strong winds may affect some outdoor "
            "activities and transportation."
        )

    if severe_weather_days:
        impacts.append(
            "Thunderstorm conditions are possible "
            "during part of the trip."
        )

    return impacts


def _build_recommendations(
    forecasts,
) -> list[str]:
    """
    Generate simple deterministic travel
    recommendations from forecast data.
    """

    recommendations = []

    rain_days = [
        forecast
        for forecast in forecasts
        if (
            forecast.precipitation_probability
            is not None
            and forecast.precipitation_probability
            >= 60
        )
    ]

    cold_days = [
        forecast
        for forecast in forecasts
        if (
            forecast.temperature_min_celsius
            is not None
            and forecast.temperature_min_celsius
            <= 10
        )
    ]

    hot_days = [
        forecast
        for forecast in forecasts
        if (
            forecast.temperature_max_celsius
            is not None
            and forecast.temperature_max_celsius
            >= 35
        )
    ]

    if rain_days:
        recommendations.append(
            "Carry suitable rain protection "
            "and keep outdoor activities flexible."
        )

    if cold_days:
        recommendations.append(
            "Pack warm clothing for colder periods."
        )

    if hot_days:
        recommendations.append(
            "Stay hydrated and plan demanding "
            "outdoor activities around cooler periods."
        )

    return recommendations


def run_weather_agent(
    trip_request: TripRequest,
) -> WeatherInfo:
    """
    Execute the Weather Agent.

    The agent:
        1. Resolves the destination.
        2. Retrieves near-term forecast data when
           a travel date is available.
        3. Retrieves historical weather data to
           provide seasonal context.
        4. Produces a structured WeatherInfo object.

    No LLM is used here.
    """

    # 1. Geocode destination

    locations = geocode_location(
        trip_request.destination
    )

    if not locations:
        return WeatherInfo(
            location=trip_request.destination,
            warnings=[
                "Could not resolve the destination."
            ],
        )

    # Use the strongest geocoding result.
    location = locations[0]

    latitude = location.get(
        "latitude"
    )

    longitude = location.get(
        "longitude"
    )

    timezone = location.get(
        "timezone"
    )

    if (
        latitude is None
        or longitude is None
    ):
        return WeatherInfo(
            location=trip_request.destination,
            warnings=[
                "Destination coordinates "
                "could not be determined."
            ],
        )

    # 2. Prepare WeatherInfo

    weather = WeatherInfo(
        location=location.get(
            "name",
            trip_request.destination,
        ),
        latitude=latitude,
        longitude=longitude,
        timezone=timezone,
    )

    # 3. Date-specific weather

    if trip_request.start_date:

        today = date.today()

        # Open-Meteo's forecast endpoint is intended
        # for near-term forecasting.
        forecast_horizon = (
            today + timedelta(days=16)
        )

        if (
            trip_request.start_date
            <= forecast_horizon
        ):

            raw_forecasts = get_weather_forecast(
                latitude=latitude,
                longitude=longitude,
                start_date=trip_request.start_date,
                duration_days=trip_request.duration_days,
            )

            weather.forecast = (
                process_weather_forecast(
                    raw_forecasts
                )
            )

        else:

            weather.warnings.append(
                "The trip is outside the reliable "
                "near-term forecast window. "
                "Historical weather is used instead."
            )

            # 4. Historical context
    
        requested_start = (
            trip_request.start_date
        )

        # The historical API cannot be queried for
        # future dates.
        #
        # For a future trip, use the same calendar
        # period from the most recent completed year.
        #
        # Example:
        #
        # Trip:
        # 2026-10-10 → 2026-10-19
        #
        # Historical:
        # 2025-10-10 → 2025-10-19

        if requested_start >= today:

            try:
                historical_start = (
                    requested_start.replace(
                        year=today.year - 1
                    )
                )

            except ValueError:
                # Handles February 29 when the
                # previous year is not a leap year.
                historical_start = (
                    requested_start.replace(
                        year=today.year - 1,
                        day=28,
                    )
                )

        else:

            # For dates already in the past,
            # use the requested historical period.
            historical_start = requested_start

        historical_end = (
            historical_start
            + timedelta(
                days=trip_request.duration_days - 1
            )
        )

        historical_data = (
            get_historical_weather(
                latitude=latitude,
                longitude=longitude,
                start_date=historical_start,
                end_date=historical_end,
            )
        )

        weather.seasonal_context = (
            _build_seasonal_context(
                historical_data
            )
        )

    else:

            # 5. No travel date
    
        weather.warnings.append(
            "No travel date was provided, so "
            "a specific forecast cannot be generated."
        )

        weather.seasonal_context.append(
            "A travel date is required for a "
            "date-specific weather forecast."
        )

    # 6. Travel impact

    weather.travel_impact = (
        _build_travel_impact(
            weather.forecast
        )
    )

    # 7. Recommendations

    weather.recommendations = (
        _build_recommendations(
            weather.forecast
        )
    )

    return weather