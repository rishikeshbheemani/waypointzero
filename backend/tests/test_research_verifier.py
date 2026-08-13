from app.services.research_verifier import verify_sources


def test_official_source_is_verified():

    results = [{
        "title": "Japan Official Tourism",
        "url": "https://japan.travel",
        "source_type": "official",
        "score": 0.9,
    }]

    verified = verify_sources(results)

    assert verified[0]["verification_status"] == "verified"
    assert verified[0]["source_role"] == "factual"


def test_reputable_source_is_partially_verified():

    results = [{
        "title": "Japan Travel Guide",
        "url": "https://example.com",
        "source_type": "reputable",
        "score": 0.8,
    }]

    verified = verify_sources(results)

    assert verified[0]["verification_status"] == "partially_verified"
    assert verified[0]["source_role"] == "factual_and_experiential"


def test_blog_is_experiential_not_bad():

    results = [{
        "title": "My Hidden Kyoto Spots",
        "url": "https://example-blog.com",
        "source_type": "blog",
        "score": 0.8,
    }]

    verified = verify_sources(results)

    assert verified[0]["verification_status"] == "unverified"
    assert verified[0]["source_role"] == "experiential"


def test_community_source_is_experiential():

    results = [{
        "title": "Local Kyoto Recommendations",
        "url": "https://reddit.com/example",
        "source_type": "community",
        "score": 0.9,
    }]

    verified = verify_sources(results)

    assert verified[0]["verification_status"] == "unverified"
    assert verified[0]["source_role"] == "experiential"