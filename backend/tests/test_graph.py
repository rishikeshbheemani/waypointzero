from app.graph.graph import graph
from app.schemas.travel import TripRequest


def test_graph_execution():

    trip_request = TripRequest(
        destination="Japan",
        duration_days=10,
    )

    initial_state = {
        "trip_request": trip_request
    }

    result = graph.invoke(initial_state)

    assert result["execution"].status == "running"
    assert result["execution"].current_agent == "test_node"