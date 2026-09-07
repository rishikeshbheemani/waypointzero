import logging
from app.schemas.travel import (
    ResearchResult,
    TransportInfo,
    TripRequest,
    UserProfile,
)
from app.services.tavily_service import tavily_service

logger = logging.getLogger(__name__)


def build_accommodation_queries(
    trip_request: TripRequest,
    user_profile: UserProfile | None = None,
    research_result: ResearchResult | None = None,
    transport_info: TransportInfo | None = None,
) -> list[str]:
    """
    Construct targeted search queries for accommodations and best neighborhoods.
    """
    destination = trip_request.destination
    queries = []

    # 1. Best neighborhoods to stay
    queries.append(f"best neighborhoods to stay in {destination} safety tourist locations")

    # 2. Key area from transport or research
    key_area = None
    if transport_info and transport_info.train_options:
        # If train arrival is specified, search near terminal station
        key_area = transport_info.train_options[0].arrival_station
    elif research_result and research_result.attractions:
        key_area = research_result.attractions[0].name

    if key_area:
        queries.append(f"top hotels near {key_area} in {destination} reviews price")
    else:
        queries.append(f"best boutique and budget hotels in {destination} reviews")

    # 3. User style preference
    if user_profile and user_profile.hotel_preference:
        pref = user_profile.hotel_preference
        queries.append(f"top {pref} accommodations in {destination} recommendations")

    return queries


def fetch_accommodation_evidence(
    trip_request: TripRequest,
    user_profile: UserProfile | None = None,
    research_result: ResearchResult | None = None,
    transport_info: TransportInfo | None = None,
) -> list[dict]:
    """
    Fetch real-world lodging evidence via Tavily search.
    """
    queries = build_accommodation_queries(
        trip_request,
        user_profile,
        research_result,
        transport_info,
    )
    evidence = []

    for query in queries:
        try:
            results = tavily_service.search(query=query, max_results=3)
            for res in results:
                evidence.append({
                    "title": res.get("title", ""),
                    "url": res.get("url", ""),
                    "content": res.get("content", "")[:1200],
                    "query": query,
                })
        except Exception as e:
            logger.warning(f"Failed to fetch accommodation evidence for query '{query}': {e}")

    return evidence
