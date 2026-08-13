from app.schemas.travel import ResearchResult, ResearchSource


def test_research_source():

    source = ResearchSource(
        title="Kyoto Official Travel Guide",
        url="https://example.com",
        source_type="tourism_board",
        relevance=0.95,
        verification_status="verified",
    )

    assert source.title == "Kyoto Official Travel Guide"
    assert source.source_type == "tourism_board"
    assert source.verification_status == "verified"


def test_research_result_contains_sources():

    result = ResearchResult(
        sources=[
            ResearchSource(
                title="Official Tourism Website",
                url="https://example.com",
                source_type="official",
                verification_status="verified",
            )
        ],
        verification_notes=[
            "Opening information was confirmed by an official source."
        ],
    )

    assert len(result.sources) == 1
    assert result.sources[0].verification_status == "verified"
    assert len(result.verification_notes) == 1