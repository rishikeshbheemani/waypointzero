from datetime import date

from app.graph.graph import graph
from app.schemas.travel import TripRequest


def test_preference_runs_before_other_agents():

    trip_request = TripRequest(
        destination="Japan",
        duration_days=10,
        budget=200000,
        start_date=date(2026, 10, 10),
        interests=["hiking", "photography"],
        constraints=["avoid crowds"],
    )

    result = graph.invoke({
        "trip_request": trip_request
    })

    assert "preference" in result["execution"].completed_agents