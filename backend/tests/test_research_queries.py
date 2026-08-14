from app.schemas.travel import TripRequest
from app.services.research_queries import build_research_queries


def test_build_research_queries():

    trip_request = TripRequest(
        destination="Japan",
        duration_days=10,
        interests=["hiking", "photography"],
        constraints=["avoid crowds"],
    )

    queries = build_research_queries(trip_request)

    assert isinstance(queries, list)
    assert len(queries) > 0

    assert any(
        "top attractions" in query
        for query in queries
    )

    assert any(
        "hidden gems" in query
        for query in queries
    )

    assert any(
        "food" in query
        for query in queries
    )

    assert any(
        "festivals" in query
        for query in queries
    )

    assert any(
        "hiking" in query and "photography" in query
        for query in queries
    )

    assert any(
        "avoid crowds" in query
        for query in queries
    )