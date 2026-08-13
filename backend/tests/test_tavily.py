from tavily import TavilyClient

from app.config.settings import settings


def test_tavily_connection():

    client = TavilyClient(
        api_key=settings.TAVILY_API_KEY
    )

    response = client.search(
        query="Japan tourism official travel guide",
        max_results=3,
    )

    assert response is not None
    assert "results" in response
    assert len(response["results"]) > 0