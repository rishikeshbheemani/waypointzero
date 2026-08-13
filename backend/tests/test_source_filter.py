from app.services.source_filter import (
    classify_source,
    filter_sources,
)


def test_classify_source():

    assert classify_source(
        "https://www.japan.travel/en/"
    ) == "official"

    assert classify_source(
        "https://www.reddit.com/r/JapanTravel/"
    ) == "community"

    assert classify_source(
        "https://example-random-blog.com/japan"
    ) == "unknown"


def test_filter_sources():

    results = [
        {
            "title": "Official Japan Travel",
            "url": "https://www.japan.travel/en/",
            "score": 0.95,
        },
        {
            "title": "Random Blog",
            "url": "https://example.com/japan",
            "score": 0.30,
        },
    ]

    filtered = filter_sources(results)

    assert len(filtered) == 1
    assert filtered[0]["source_type"] == "official"