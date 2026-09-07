import logging
from app.schemas.travel import TripRequest, UserProfile
from app.services.tavily_service import tavily_service

logger = logging.getLogger(__name__)


def build_transport_queries(
    trip_request: TripRequest,
    user_profile: UserProfile | None = None,
) -> list[str]:
    """
    Construct high-signal search queries for flights, trains, road transit, and city passes.
    """
    destination = trip_request.destination
    origin = trip_request.origin

    # Inspect constraints and interests for preferred transit modes
    all_notes = " ".join(trip_request.constraints + trip_request.interests).lower()
    prefers_train = any(
        kw in all_notes
        for kw in ["train", "rail", "shinkansen", "irctc", "amtrak", "eurostar", "railway"]
    )
    prefers_road = any(
        kw in all_notes
        for kw in ["bus", "drive", "road trip", "car rental", "cab"]
    )
    avoid_flights = any(
        kw in all_notes
        for kw in ["no flight", "avoid flight", "train only", "no flying"]
    )

    queries = []

    # 1. Intercity Transit (Trains vs Flights vs Road)
    if origin:
        if prefers_train or not avoid_flights:
            queries.append(f"trains from {origin} to {destination} routes duration timetable")

        if not avoid_flights and not (prefers_train and "train only" in all_notes):
            queries.append(f"flights from {origin} to {destination} airlines routes")

        if prefers_road:
            queries.append(f"bus and driving routes from {origin} to {destination} travel time")
    else:
        queries.append(f"flights to {destination} major airlines routes")

    # 2. Destination Public Transit & City Travel Passes
    queries.append(f"{destination} public transportation guide metro subway bus local train tourist pass")
    queries.append(f"{destination} railway station and airport transfer to city center transit")

    # 3. User Airline Preferences (if flights are applicable)
    if user_profile and user_profile.preferred_airlines and not avoid_flights:
        airlines = " or ".join(user_profile.preferred_airlines)
        queries.append(f"{airlines} flights to {destination}")

    return queries


def fetch_transport_evidence(
    trip_request: TripRequest,
    user_profile: UserProfile | None = None,
) -> list[dict]:
    """
    Fetch web evidence for travel transportation options.
    Gracefully handles network errors or missing API keys.
    """
    queries = build_transport_queries(trip_request, user_profile)
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
            logger.warning(f"Failed to fetch transport evidence for query '{query}': {e}")

    return evidence
