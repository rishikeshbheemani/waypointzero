from app.schemas.travel import TripRequest
from app.services.research_search import search_research_sources


def test_research_search():

    trip_request = TripRequest(
        destination="Japan",
        duration_days=10,
        interests=["hiking"],
    )

    results = search_research_sources(trip_request)

    assert isinstance(results, list)
    assert len(results) > 0

    first_result = results[0]

    assert "title" in first_result
    assert "url" in first_result
    assert "query" in first_result