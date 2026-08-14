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
        Extract content from URLs in batches of 20.
        """

        if not urls:
            return []

        all_results = []

        for i in range(0, len(urls), 20):
            batch = urls[i:i + 20]

            response = self.client.extract(
                urls=batch
            )

            all_results.extend(
                response.get("results", [])
            )

        return all_results


source_extractor = TavilySourceExtractor()