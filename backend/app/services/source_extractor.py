from tavily import TavilyClient

from app.config.settings import settings


class TavilySourceExtractor:
    """
    Extract page content from selected research sources using Tavily.
    """

    def __init__(self):
        self.client = TavilyClient(
            api_key=settings.TAVILY_API_KEY
        )

    def extract(self, urls: list[str]) -> list[dict]:
        """
        Extract content from a list of URLs.
        """

        if not urls:
            return []

        response = self.client.extract(
            urls=urls
        )

        return response.get("results", [])


source_extractor = TavilySourceExtractor()