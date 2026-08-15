from app.services.weather_codes import (
    describe_weather_code,
)


def test_clear_sky():

    assert (
        describe_weather_code(0)
        == "Clear sky"
    )


def test_moderate_rain():

    assert (
        describe_weather_code(63)
        == "Moderate rain"
    )


def test_heavy_rain():

    assert (
        describe_weather_code(65)
        == "Heavy rain"
    )


def test_thunderstorm():

    assert (
        describe_weather_code(95)
        == "Thunderstorm"
    )


def test_unknown_code():

    assert (
        describe_weather_code(999)
        == "Unknown weather condition"
    )


def test_none_code():

    assert (
        describe_weather_code(None)
        is None
    )