from datetime import date
from unittest.mock import patch

from app.graph.graph import graph
from app.schemas.travel import (
    TripRequest,
    WeatherInfo,
)


def test_weather_agent_graph():

    trip_request = TripRequest(
        destination="Japan",
        duration_days=5,
        budget=200000,
        start_date=date.today(),
        interests=[
            "hiking",
            "photography",
        ],
        constraints=[
            "avoid crowds",
        ],
    )

    mock_weather = WeatherInfo(
        location="Japan",
        latitude=35.6762,
        longitude=139.6503,
        timezone="Asia/Tokyo",
    )

    with patch(
        "app.graph.graph.run_weather_agent",
        return_value=mock_weather,
    ):

        result = graph.invoke(
            {
                "trip_request": trip_request
            }
        )

    assert "weather" in result

    assert result["weather"] is not None

    assert (
        result["weather"].location
        == "Japan"
    )