from urllib.parse import urlparse


OFFICIAL_DOMAINS = {
    "japan.travel",
    "kyoto.travel",
    "gov.in",
    "gov.uk",
    "gov.sg",
    "go.jp",
}


REPUTABLE_DOMAINS = {
    "lonelyplanet.com",
    "nationalgeographic.com",
    "tripadvisor.com",
}


COMMUNITY_DOMAINS = {
    "reddit.com",
    "medium.com",
}


def classify_source(url: str) -> str:
    """
    Classify a source based on its domain.
    """

    hostname = urlparse(url).hostname

    if not hostname:
        return "unknown"

    hostname = hostname.lower().removeprefix("www.")

    if hostname in OFFICIAL_DOMAINS:
        return "official"

    if hostname in REPUTABLE_DOMAINS:
        return "reputable"

    if hostname in COMMUNITY_DOMAINS:
        return "community"

    return "unknown"

def filter_sources(
    results: list[dict],
    min_score: float = 0.5,
) -> list[dict]:
    """
    Filter and classify Tavily search results.
    """

    filtered = []

    for result in results:

        url = result.get("url", "")
        score = result.get("score", 0.0)

        if not url:
            continue

        if score < min_score:
            continue

        source_type = classify_source(url)

        result = {
            **result,
            "source_type": source_type,
        }

        filtered.append(result)

    return filtered