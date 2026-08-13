from app.graph.graph import graph
from app.schemas.travel import TripRequest
from datetime import date

from app.graph.graph import graph
from app.schemas.travel import TripRequest

def test_supervisor_routes_full_trip():

    trip_request = TripRequest(
    destination="Japan",
    duration_days=10,
    budget=200000,
    start_date=date(2026, 10, 10),
    interests=[
        "hiking",
        "photography",
        "anime",
    ],
    constraints=[
        "avoid crowds",
    ],
)

    initial_state = {
        "trip_request": trip_request
    }

    result = graph.invoke(initial_state)

    decision = result["supervisor_decision"]

    assert decision.invoke_research is True
    assert decision.invoke_weather is True
    assert decision.invoke_transport is True
    assert decision.invoke_accommodation is True
    assert decision.invoke_activities is True
    assert decision.invoke_budget is True