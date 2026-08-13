from tavily import TavilyClient

from app.config.settings import settings


class TavilySearchService:
    """
    Wrapper around Tavily used by Voyager's Research Agent.
    """

    def __init__(self):
        self.client = TavilyClient(
            api_key=settings.TAVILY_API_KEY
        )

    def search(
        self,
        query: str,
        max_results: int = 5,
    ) -> list[dict]:
        """
        Search the web and return normalized search results.
        """

        response = self.client.search(
            query=query,
            max_results=max_results,
        )

        return response.get("results", [])


tavily_service = TavilySearchService()