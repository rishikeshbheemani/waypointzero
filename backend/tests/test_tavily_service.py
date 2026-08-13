from app.services.tavily_service import tavily_service


def test_tavily_search_service():

    results = tavily_service.search(
        query="Japan official tourism",
        max_results=3,
    )

    assert isinstance(results, list)
    assert len(results) > 0

    first_result = results[0]

    assert "title" in first_result
    assert "url" in first_result