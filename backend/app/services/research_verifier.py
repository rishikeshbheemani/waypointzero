from collections import defaultdict


VERIFIED_SOURCE_TYPES = {
    "official",
    "government",
    "tourism_board",
}

REPUTABLE_SOURCE_TYPES = {
    "reputable",
}

EXPERIENCE_SOURCE_TYPES = {
    "community",
    "blog",
}


def verify_sources(results: list[dict]) -> list[dict]:
    """
    Classify evidence strength without treating experiential
    sources as bad or useless.
    """

    verified_results = []

    for result in results:
        source_type = result.get("source_type", "unknown")
        score = result.get("score", 0.0)

        if source_type in VERIFIED_SOURCE_TYPES and score >= 0.5:
            verification_status = "verified"
            source_role = "factual"

        elif source_type in REPUTABLE_SOURCE_TYPES and score >= 0.7:
            verification_status = "partially_verified"
            source_role = "factual_and_experiential"

        elif source_type in EXPERIENCE_SOURCE_TYPES:
            verification_status = "unverified"
            source_role = "experiential"

        else:
            verification_status = "unverified"
            source_role = "unknown"

        verified_results.append(
            {
                **result,
                "verification_status": verification_status,
                "source_role": source_role,
            }
        )

    return verified_results