from decimal import Decimal
from unittest.mock import MagicMock, patch

from app.agents.transport import run_transport_agent
from app.graph.graph import transport_node
from app.graph.state import TravelState
from app.schemas.travel import (
    FlightOption,
    TrainOption,
    TransitOption,
    TransportInfo,
    TransportPass,
    TripRequest,
    UserProfile,
)
from app.services.transport_service import (
    build_transport_queries,
    fetch_transport_evidence,
)


def test_build_transport_queries():
    trip = TripRequest(
        destination="Tokyo",
        origin="San Francisco",
        duration_days=7,
    )
    profile = UserProfile(
        preferred_airlines=["ANA", "Japan Airlines"],
    )

    queries = build_transport_queries(trip, profile)

    assert any("San Francisco" in q for q in queries)
    assert any("Tokyo" in q for q in queries)
    assert any("ANA" in q for q in queries)


def test_build_transport_queries_train_preference():
    trip = TripRequest(
        destination="Mumbai",
        origin="Hyderabad",
        duration_days=3,
        constraints=["travel by train", "no flights"],
    )

    queries = build_transport_queries(trip)

    assert any("trains from Hyderabad to Mumbai" in q for q in queries)
    assert not any("flights" in q for q in queries)


def test_fetch_transport_evidence_mocked():
    trip = TripRequest(destination="Kyoto", duration_days=5)

    mock_search_results = [
        {
            "title": "Kyoto Transit Guide",
            "url": "https://example.com/kyoto-transit",
            "content": "Take the JR Haruka Express from Kansai Airport to Kyoto station.",
        }
    ]

    with patch("app.services.transport_service.tavily_service.search", return_value=mock_search_results):
        evidence = fetch_transport_evidence(trip)

        assert len(evidence) >= 1
        assert evidence[0]["title"] == "Kyoto Transit Guide"
        assert "Haruka Express" in evidence[0]["content"]


def test_run_transport_agent_mocked():
    trip = TripRequest(
        destination="Paris",
        origin="New York",
        duration_days=5,
    )

    expected_info = TransportInfo(
        recommended_flights=["Direct flights via Air France or Delta"],
        flight_options=[
            FlightOption(
                airline="Air France",
                route="JFK -> CDG",
                estimated_price_usd=Decimal("650"),
                notes="Non-stop",
            )
        ],
        local_transport=["Paris Metro and RER"],
        transit_options=[
            TransitOption(
                mode="Metro",
                route_or_system="RATP Metro",
                estimated_cost=Decimal("2.15"),
                description="Comprehensive subway network",
            )
        ],
        travel_passes=["Navigo Easy Pass"],
        pass_options=[
            TransportPass(
                name="Navigo Easy",
                coverage="Zones 1-2 central Paris",
                is_recommended=True,
            )
        ],
        airport_transfers=["RER B train from CDG to Châtelet - Les Halles (~45 min)"],
        tips=["Validate tickets before boarding the RER."],
    )

    with patch("app.agents.transport.fetch_transport_evidence", return_value=[]), \
         patch("app.agents.transport.transport_agent") as mock_agent:
        mock_agent.invoke.return_value = expected_info
        result = run_transport_agent(trip)

        assert result.recommended_flights == ["Direct flights via Air France or Delta"]
        assert len(result.flight_options) == 1
        assert result.flight_options[0].airline == "Air France"
        assert result.flight_options[0].estimated_price_usd == Decimal("650")
        assert len(result.pass_options) == 1
        assert result.pass_options[0].name == "Navigo Easy"


def test_transport_node_in_graph_state():
    trip = TripRequest(destination="Rome", duration_days=4)
    state = TravelState(trip_request=trip)

    mock_info = TransportInfo(
        recommended_flights=["Flights into FCO Leonardo da Vinci"],
        local_transport=["Rome Metro Line A and B"],
    )

    with patch("app.graph.graph.run_transport_agent", return_value=mock_info):
        node_output = transport_node(state)

        assert "transport" in node_output
        assert node_output["transport"].local_transport == ["Rome Metro Line A and B"]


def test_transport_agent_with_train_and_flight_options():
    trip = TripRequest(
        destination="Mumbai",
        origin="Hyderabad",
        duration_days=3,
    )

    expected_info = TransportInfo(
        flight_options=[
            FlightOption(
                airline="IndiGo (6E 5384)",
                route="HYD -> BOM",
                estimated_price_usd=Decimal("45"),
                notes="Early morning 06:15 departure; non-stop 1h 25m",
            ),
            FlightOption(
                airline="Air India (AI 620)",
                route="HYD -> BOM",
                estimated_price_usd=Decimal("65"),
                notes="Afternoon 14:30 departure; full-service baggage included",
            ),
        ],
        train_options=[
            TrainOption(
                train_name_or_number="Vande Bharat Express (20705)",
                departure_station="Secunderabad (SC)",
                arrival_station="Mumbai CSMT",
                duration="8h 30m",
                estimated_price_usd=Decimal("20"),
                travel_class="Executive / CC",
                trade_offs="Fastest daytime train, scenic Western Ghats descent",
            ),
            TrainOption(
                train_name_or_number="Hussain Sagar Express (12702)",
                departure_station="Hyderabad Deccan (HYB)",
                arrival_station="Mumbai CSMT",
                duration="13h 45m",
                estimated_price_usd=Decimal("15"),
                travel_class="2A / 3A / Sleeper",
                trade_offs="Overnight train; saves 1 night hotel accommodation",
            ),
        ],
        local_transport=["Mumbai Local suburban trains", "Metro Line 1/2/7", "BEST AC Buses"],
    )

    with patch("app.agents.transport.fetch_transport_evidence", return_value=[]), \
         patch("app.agents.transport.transport_agent") as mock_agent:
        mock_agent.invoke.return_value = expected_info
        result = run_transport_agent(trip)

        assert len(result.flight_options) == 2
        assert len(result.train_options) == 2
        assert "IndiGo" in result.flight_options[0].airline
        assert "Air India" in result.flight_options[1].airline
        assert "Vande Bharat" in result.train_options[0].train_name_or_number
        assert result.train_options[1].trade_offs is not None and "Overnight" in result.train_options[1].trade_offs
