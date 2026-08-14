from app.schemas.travel import TripRequest

from app.services.research_search import search_research_sources
from app.services.source_filter import filter_sources
from app.services.source_extractor import source_extractor
from app.services.research_verifier import verify_sources


def collect_research_evidence(
    trip_request: TripRequest,
) -> list[dict]:
    """
    Execute the complete research retrieval pipeline.

    Search → Filter → Limit → Extract → Verify
    """

    # 1. Search

    search_results = search_research_sources(
        trip_request
    )

    # 2. Filter sources

    filtered_results = filter_sources(
        search_results
    )

    # Keep only the strongest sources.
    filtered_results = sorted(
        filtered_results,
        key=lambda x: x.get("score", 0.0),
        reverse=True,
    )[:8]

    if not filtered_results:
        return []

    # 3. Extract source content

    # Remove duplicate URLs before extraction.
    urls = list(
        dict.fromkeys(
            result["url"]
            for result in filtered_results
            if result.get("url")
        )
    )

    extracted_results = source_extractor.extract(
        urls
    )

    # 4. Combine metadata + extracted content

    extracted_by_url = {
        result.get("url"): result
        for result in extracted_results
    }

    enriched_results = []

    for result in filtered_results:

        url = result.get("url")

        extracted = extracted_by_url.get(
            url,
            {}
        )

        raw_content = extracted.get(
            "raw_content",
            ""
        )

        # Prevent extremely large webpages from consuming the LLM context window.
        raw_content = raw_content[:3000]

        enriched_results.append(
            {
                **result,
                "raw_content": raw_content,
            }
        )

    # 5. Evidence classification

    verified_results = verify_sources(
        enriched_results
    )

    return verified_results