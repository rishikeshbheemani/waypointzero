from app.services.geocoding import geocode_location


def test_geocode_normal_location():

    results = geocode_location(
        "Hyderabad"
    )

    assert len(results) > 0

    result = results[0]

    assert result["name"]
    assert result["latitude"] is not None
    assert result["longitude"] is not None
    assert result["timezone"]
    assert result["country"]


def test_geocode_unknown_location():

    results = geocode_location(
        "thisplacedefinitelydoesnotexist123456"
    )

    assert results == []