from app.agents.research import run_research_agent
from app.schemas.travel import (
    ResearchResult,
    TripRequest,
)


def test_research_end_to_end():

    trip_request = TripRequest(
        destination="Japan",
        duration_days=10,
        budget=200000,
        interests=["hiking", "photography"],
        constraints=["avoid crowds"],
    )

    result = run_research_agent(
        trip_request
    )

    assert isinstance(
        result,
        ResearchResult,
    )

    assert len(result.sources) > 0

    assert any(
        source.url
        for source in result.sources
    )