from decimal import Decimal
from unittest.mock import MagicMock, patch

from app.agents.accommodation import run_accommodation_agent
from app.graph.graph import accommodation_node
from app.graph.state import TravelState
from app.schemas.travel import (
    AccommodationResult,
    HotelRecommendation,
    TrainOption,
    TransportInfo,
    TripRequest,
    UserProfile,
)
from app.services.accommodation_service import (
    build_accommodation_queries,
    fetch_accommodation_evidence,
)


def test_build_accommodation_queries():
    trip = TripRequest(
        destination="Mumbai",
        duration_days=4,
    )
    profile = UserProfile(
        hotel_preference="boutique heritage",
    )
    transport = TransportInfo(
        train_options=[
            TrainOption(
                train_name_or_number="Vande Bharat Express (20705)",
                departure_station="Secunderabad (SC)",
                arrival_station="Mumbai CSMT",
                duration="8h 30m",
                estimated_price_usd=Decimal("35.00"),
            )
        ]
    )

    queries = build_accommodation_queries(
        trip_request=trip,
        user_profile=profile,
        transport_info=transport,
    )

    assert any("Mumbai" in q for q in queries)
    assert any("Mumbai CSMT" in q for q in queries)
    assert any("boutique heritage" in q for q in queries)


def test_fetch_accommodation_evidence_mocked():
    trip = TripRequest(destination="Tokyo", duration_days=5)

    mock_search_results = [
        {
            "title": "Tokyo Hotel Guide",
            "url": "https://example.com/tokyo-hotels",
            "content": "Stay near Shinjuku for nightlife or Asakusa for traditional culture.",
        }
    ]

    with patch("app.services.accommodation_service.tavily_service.search", return_value=mock_search_results):
        evidence = fetch_accommodation_evidence(trip)

        assert len(evidence) >= 1
        assert evidence[0]["title"] == "Tokyo Hotel Guide"
        assert "Shinjuku" in evidence[0]["content"]


def test_run_accommodation_agent_mocked():
    trip = TripRequest(
        destination="Mumbai",
        duration_days=3,
        budget=Decimal("500.00"),
    )

    expected_hotels = [
        HotelRecommendation(
            name="Taj Mahal Tower",
            city="Mumbai",
            price_per_night=Decimal("220.00"),
            rating=4.8,
            description="Iconic luxury stay overlooking the Gateway of India and Arabian Sea.",
            neighborhood="Colaba",
            category="Luxury",
            location_advantage="Close to South Mumbai heritage landmarks and CSMT station.",
            amenities=["Free Wi-Fi", "Pool", "Spa", "Sea View"],
        ),
        HotelRecommendation(
            name="Residency Hotel Fort",
            city="Mumbai",
            price_per_night=Decimal("75.00"),
            rating=4.4,
            description="Comfortable mid-range stay within walking distance of Victoria Terminus.",
            neighborhood="Fort",
            category="Mid-Range",
            location_advantage="5-minute walk to CSMT train terminus.",
            amenities=["Free Wi-Fi", "Breakfast", "AC"],
        ),
    ]

    mock_result = AccommodationResult(
        hotels=expected_hotels,
        neighborhood_insights=["Colaba and Fort are great for heritage sightseeing and rail access."],
    )

    with (
        patch("app.agents.accommodation.fetch_accommodation_evidence", return_value=[]),
        patch("app.agents.accommodation.accommodation_agent") as mock_agent,
    ):
        mock_agent.invoke.return_value = mock_result
        result = run_accommodation_agent(trip)

        assert len(result) == 2
        assert result[0].name == "Taj Mahal Tower"
        assert result[0].neighborhood == "Colaba"
        assert result[0].price_per_night == Decimal("220.00")
        assert result[1].category == "Mid-Range"


def test_accommodation_node_in_graph():
    trip = TripRequest(
        destination="Rome",
        duration_days=4,
    )
    initial_state = TravelState(trip_request=trip)

    mock_hotels = [
        HotelRecommendation(
            name="Hotel Artemide",
            city="Rome",
            price_per_night=Decimal("180.00"),
            rating=4.7,
            description="Elegant hotel on Via Nazionale near Termini Station.",
            neighborhood="Monti / Termini",
            category="Boutique",
            location_advantage="Walking distance to Roma Termini and Colosseum.",
            amenities=["Free Wi-Fi", "Rooftop Bar", "Spa"],
        )
    ]

    with patch("app.graph.graph.run_accommodation_agent", return_value=mock_hotels):
        output = accommodation_node(initial_state)

        assert "hotels" in output
        assert len(output["hotels"]) == 1
        assert output["hotels"][0].name == "Hotel Artemide"


def test_accommodation_fallback_on_error():
    trip = TripRequest(
        destination="Singapore",
        duration_days=3,
    )

    with (
        patch("app.agents.accommodation.fetch_accommodation_evidence", return_value=[]),
        patch("app.agents.accommodation.accommodation_agent") as mock_agent,
    ):
        mock_agent.invoke.side_effect = RuntimeError("LLM failed")
        result = run_accommodation_agent(trip)

        assert len(result) >= 1
        assert result[0].city == "Singapore"
        assert result[0].category in ["Mid-Range", "Luxury", "Boutique", "Budget"]
