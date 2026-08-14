from app.schemas.travel import TripRequest
from app.services.research_pipeline import collect_research_evidence


def test_collect_research_evidence():

    trip_request = TripRequest(
        destination="Japan",
        duration_days=10,
        interests=["hiking"],
    )

    evidence = collect_research_evidence(
        trip_request
    )

    assert isinstance(evidence, list)
    assert len(evidence) > 0

    first = evidence[0]

    assert "title" in first
    assert "url" in first
    assert "source_type" in first
    assert "verification_status" in first
    assert "source_role" in first
    assert "raw_content" in first