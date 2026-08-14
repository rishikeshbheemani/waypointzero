from app.schemas.travel import TripRequest


def build_research_queries(trip_request: TripRequest) -> list[str]:
    """
    Build focused research queries for a trip request.
    """

    destination = trip_request.destination

    queries = [
        f"{destination} top attractions official tourism",
        f"{destination} hidden gems local experiences",
        f"{destination} best local food restaurants",
        f"{destination} festivals events travel",
        f"{destination} local customs etiquette",
        f"{destination} travel tips",
        f"{destination} travel safety",
    ]

    if trip_request.interests:
        interests = ", ".join(trip_request.interests)

        queries.append(
            f"{destination} {interests} best places activities"
        )

    if trip_request.constraints:
        constraints = ", ".join(trip_request.constraints)

        queries.append(
            f"{destination} travel {constraints}"
        )

    return queries