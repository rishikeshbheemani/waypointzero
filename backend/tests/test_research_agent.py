from unittest.mock import patch

from app.agents.research import run_research_agent
from app.schemas.travel import ResearchResult, TripRequest


def test_research_agent():

    trip_request = TripRequest(
        destination="Japan",
        duration_days=10,
        interests=[
            "hiking",
            "photography",
        ],
        constraints=[
            "avoid crowds",
        ],
    )

    mock_evidence = [
        {
            "title": "Official Japan Tourism Guide",
            "url": "https://example.com/japan",
            "source_type": "official",
            "source_role": "factual",
            "verification_status": "verified",
            "score": 0.95,
            "raw_content": (
                "Japan has many historic temples and cultural sites. "
                "Kyoto is known for traditional neighborhoods and temples."
            ),
        },
        {
            "title": "Kyoto Photography Guide",
            "url": "https://example.com/kyoto-photo",
            "source_type": "blog",
            "source_role": "experiential",
            "verification_status": "unverified",
            "score": 0.82,
            "raw_content": (
                "Early morning walks around traditional Kyoto streets "
                "can provide quieter conditions and good photography."
            ),
        },
    ]

    with patch(
        "app.agents.research.collect_research_evidence",
        return_value=mock_evidence,
    ):

        result = run_research_agent(
            trip_request
        )

    assert isinstance(
        result,
        ResearchResult,
    )

    assert len(result.sources) == 2

    assert result.sources[0].url == (
        "https://example.com/japan"
    )

    assert result.sources[0].verification_status == (
        "verified"
    )

    assert result.sources[1].source_type == "blog"

    assert result.sources[1].verification_status == (
        "unverified"
    )