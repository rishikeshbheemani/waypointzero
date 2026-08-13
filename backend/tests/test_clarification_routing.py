from app.graph.graph import graph
from app.schemas.travel import TripRequest


def test_graph_routes_to_clarification():

    trip_request = TripRequest(
        destination="Japan",
        duration_days=0,
    )

    result = graph.invoke({
        "trip_request": trip_request
    })

    decision = result["supervisor_decision"]

    assert decision.needs_clarification is True
    assert result["execution"].current_agent == "clarification"
    assert result["execution"].status == "waiting_for_user"