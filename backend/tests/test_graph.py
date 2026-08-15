from datetime import date

from app.graph.graph import graph
from app.schemas.travel import TripRequest


def test_graph_execution():

    trip_request = TripRequest(
        destination="Japan",
        duration_days=10,
        budget=200000,
        start_date=date(2026, 10, 10),
        interests=["hiking", "photography"],
        constraints=["avoid crowds"],
    )

    initial_state = {
        "trip_request": trip_request
    }

    result = graph.invoke(initial_state)

    assert result["execution"].status == "running"
    assert result["execution"].current_agent == "preference"
    assert result["supervisor_decision"] is not None

    # Specialized agent results should be present.
    assert "research" in result
    assert result["research"] is not None

    assert "weather" in result
    assert result["weather"] is not None