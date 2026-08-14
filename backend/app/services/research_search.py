from app.services.tavily_service import tavily_service
from app.services.research_queries import build_research_queries
from app.schemas.travel import TripRequest


def search_research_sources(
    trip_request: TripRequest,
) -> list[dict]:
    """
    Build focused research queries and execute them
    through Tavily.
    """

    queries = build_research_queries(trip_request)

    all_results = []

    for query in queries:
        results = tavily_service.search(
            query=query,
            max_results=5,
        )

        for result in results:
            all_results.append(
                {
                    **result,
                    "query": query,
                }
            )

    return all_results