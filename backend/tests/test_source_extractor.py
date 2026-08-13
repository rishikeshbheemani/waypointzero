from app.services.source_extractor import source_extractor


def test_source_extractor():

    urls = [
        "https://www.japan.travel/en/"
    ]

    results = source_extractor.extract(urls)

    assert isinstance(results, list)
    assert len(results) > 0

    first_result = results[0]

    assert "url" in first_result
    assert "raw_content" in first_result