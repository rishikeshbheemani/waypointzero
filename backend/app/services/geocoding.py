import requests


GEOCODING_URL = (
    "https://geocoding-api.open-meteo.com/v1/search"
)


def geocode_location(
    location: str,
) -> list[dict]:
    """
    Resolve a user-provided location into
    possible geographic matches.

    Returns a list because a location name can have
    multiple possible matches.

    Example:
        "Springfield"
        → multiple possible locations

        "Cherrapunji"
        → likely one relevant match
    """

    if not location.strip():
        return []

    params = {
        "name": location.strip(),
        "count": 5,
        "language": "en",
        "format": "json",
    }

    response = requests.get(
        GEOCODING_URL,
        params=params,
        timeout=10,
    )

    response.raise_for_status()

    data = response.json()

    results = data.get(
        "results",
        []
    )

    return [
        {
            "name": result.get("name"),
            "latitude": result.get("latitude"),
            "longitude": result.get("longitude"),
            "timezone": result.get("timezone"),
            "country": result.get("country"),
            "admin1": result.get("admin1"),
        }
        for result in results
    ]