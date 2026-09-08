from decimal import Decimal
from unittest.mock import patch

from app.agents.budget import (
    calculate_base_budget,
    run_budget_agent,
)
from app.graph.graph import budget_node
from app.graph.state import TravelState
from app.schemas.travel import (
    BudgetInfo,
    DailyActivity,
    DailyPlan,
    FlightOption,
    HotelRecommendation,
    Itinerary,
    TransportInfo,
    TripRequest,
    UserProfile,
)


def test_calculate_base_budget_within_budget():
    trip = TripRequest(
        destination="Tokyo",
        duration_days=5,
        budget=Decimal("3000.00"),
    )
    transport = TransportInfo(
        flight_options=[
            FlightOption(
                airline="ANA",
                route="SEA -> HND",
                estimated_price_usd=Decimal("850.00"),
            )
        ]
    )
    hotels = [
        HotelRecommendation(
            name="Hotel Gracery Shinjuku",
            city="Tokyo",
            price_per_night=Decimal("150.00"),
            rating=4.4,
            description="Comfortable mid-range hotel in Shinjuku",
            category="Mid-Range",
        )
    ]
    itinerary = Itinerary(
        trip_title="Tokyo 5-Day",
        days=[
            DailyPlan(
                day=1,
                activities=[
                    DailyActivity(
                        time="10:00 AM",
                        title="Tokyo Skytree",
                        location="Oshiage",
                        description="Observation deck",
                        cost_estimate=Decimal("25.00"),
                    ),
                    DailyActivity(
                        time="02:00 PM",
                        title="Senso-ji",
                        location="Asakusa",
                        description="Historic temple",
                        cost_estimate=Decimal("0.00"),
                    ),
                ],
            )
        ],
    )
    profile = UserProfile(travel_style="Comfortable")

    budget = calculate_base_budget(
        trip_request=trip,
        transport_info=transport,
        hotels=hotels,
        itinerary=itinerary,
        user_profile=profile,
    )

    # 4 nights * $150 = $600
    assert budget.accommodation == Decimal("600.00")
    # Flight = $850
    assert budget.flights == Decimal("850.00")
    # Food = 5 days * $65 = $325
    assert budget.food == Decimal("325")
    # Transport = 5 days * $15 = $75
    assert budget.transportation == Decimal("75")
    # Activity = $25 (explicit)
    assert budget.activities == Decimal("25.00")

    expected_total = Decimal("850.00") + Decimal("600.00") + Decimal("325") + Decimal("75") + Decimal("25.00")
    assert budget.total == expected_total
    assert budget.remaining == Decimal("3000.00") - expected_total
    assert budget.status == "within_budget"
    assert len(budget.cost_saving_tips) > 0


def test_calculate_base_budget_over_budget():
    trip = TripRequest(
        destination="Paris",
        duration_days=7,
        budget=Decimal("1000.00"),  # Low budget for 7 days in Paris
    )
    transport = TransportInfo(
        flight_options=[
            FlightOption(
                airline="Air France",
                route="JFK -> CDG",
                estimated_price_usd=Decimal("700.00"),
            )
        ]
    )
    hotels = [
        HotelRecommendation(
            name="Parisian Boutique Hotel",
            city="Paris",
            price_per_night=Decimal("180.00"),
            rating=4.5,
            description="Charming boutique hotel in Paris",
            category="Boutique",
        )
    ]

    budget = calculate_base_budget(
        trip_request=trip,
        transport_info=transport,
        hotels=hotels,
    )

    assert budget.total > Decimal("1000.00")
    assert budget.remaining is not None
    assert budget.remaining < 0
    assert budget.status == "over_budget"
    # First tip should mention being over budget
    assert any("over your target budget" in tip for tip in budget.cost_saving_tips)


def test_calculate_base_budget_flexible_no_budget():
    trip = TripRequest(
        destination="Rome",
        duration_days=3,
        budget=None,
    )
    budget = calculate_base_budget(trip_request=trip)

    assert budget.remaining is None
    assert budget.status == "flexible"
    assert budget.total > 0


def test_run_budget_agent_with_llm():
    trip = TripRequest(
        destination="Kyoto",
        duration_days=4,
        budget=Decimal("2000.00"),
    )
    mock_llm_budget = BudgetInfo(
        flights=Decimal("600.00"),
        accommodation=Decimal("400.00"),
        food=Decimal("250.00"),
        transportation=Decimal("60.00"),
        activities=Decimal("100.00"),
        total=Decimal("1410.00"),
        remaining=Decimal("590.00"),
        status="within_budget",
        currency="USD",
        cost_saving_tips=["Buy the 1-day Kyoto bus pass", "Visit Fushimi Inari early for free entry"],
    )

    with patch("app.agents.budget.budget_agent") as mock_agent:
        mock_agent.invoke.return_value = mock_llm_budget

        result = run_budget_agent(trip_request=trip)

        assert result.status == "within_budget"
        assert result.remaining == Decimal("590.00")
        assert "Buy the 1-day Kyoto bus pass" in result.cost_saving_tips


def test_run_budget_agent_fallback_on_exception():
    trip = TripRequest(
        destination="Kyoto",
        duration_days=4,
        budget=Decimal("2000.00"),
    )

    with patch("app.agents.budget.budget_agent") as mock_agent:
        mock_agent.invoke.side_effect = RuntimeError("OpenRouter timeout")

        result = run_budget_agent(trip_request=trip)

        assert isinstance(result, BudgetInfo)
        assert result.total > 0
        assert result.status == "within_budget"
        assert len(result.cost_saving_tips) > 0


def test_budget_node_in_graph_state():
    trip = TripRequest(
        destination="Berlin",
        duration_days=3,
        budget=Decimal("1500.00"),
    )
    state = TravelState(trip_request=trip)

    mock_budget = BudgetInfo(
        flights=Decimal("300.00"),
        accommodation=Decimal("300.00"),
        food=Decimal("150.00"),
        transportation=Decimal("45.00"),
        activities=Decimal("75.00"),
        total=Decimal("870.00"),
        remaining=Decimal("630.00"),
        status="within_budget",
    )

    with patch("app.graph.graph.run_budget_agent", return_value=mock_budget):
        result_dict = budget_node(state)
        assert "budget" in result_dict
        assert isinstance(result_dict["budget"], BudgetInfo)
        assert result_dict["budget"].total == Decimal("870.00")
        assert result_dict["budget"].status == "within_budget"
