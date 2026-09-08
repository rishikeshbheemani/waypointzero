from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock, patch

from app.agents.master_planner import _fallback_itinerary, run_master_planner
from app.graph.graph import master_planner_node
from app.graph.state import TravelState
from app.schemas.travel import (
    Attraction,
    DailyActivity,
    DailyPlan,
    FlightOption,
    FoodRecommendation,
    HotelRecommendation,
    Itinerary,
    ResearchResult,
    TrainOption,
    TransportInfo,
    TripRequest,
    UserProfile,
    WeatherForecast,
    WeatherInfo,
)


def test_run_master_planner_mocked():
    trip = TripRequest(
        destination="Kyoto",
        duration_days=3,
        budget=Decimal("1200.00"),
        interests=["temples", "tea ceremonies", "local cuisine"],
    )

    mock_itinerary = Itinerary(
        trip_title="3-Day Kyoto Cultural Journey",
        summary="A balanced cultural exploration of historic Kyoto.",
        days=[
            DailyPlan(
                day=1,
                theme="Arrival & Gion Evening",
                activities=[
                    DailyActivity(
                        time="02:00 PM",
                        title="Arrival at Kyoto Station & Hotel Check-in",
                        location="Kyoto Station",
                        description="Arrive by Shinkansen, check into hotel.",
                        activity_type="transit",
                    ),
                    DailyActivity(
                        time="05:30 PM",
                        title="Evening Gion Stroll",
                        location="Gion",
                        description="Walk through preserved wooden machiya streets.",
                        activity_type="sightseeing",
                    ),
                ],
            ),
            DailyPlan(
                day=2,
                theme="Arashiyama & Golden Pavilion",
                activities=[
                    DailyActivity(
                        time="09:00 AM",
                        title="Kinkaku-ji (Golden Pavilion)",
                        location="Kita Ward",
                        description="Marvel at the gold-leaf Zen temple.",
                        activity_type="sightseeing",
                    ),
                ],
            ),
            DailyPlan(
                day=3,
                theme="Fushimi Inari & Departure",
                activities=[
                    DailyActivity(
                        time="08:30 AM",
                        title="Fushimi Inari Taisha",
                        location="Fushimi Ward",
                        description="Walk through the thousands of vermilion torii gates.",
                        activity_type="sightseeing",
                    ),
                ],
            ),
        ],
    )

    with patch("app.agents.master_planner.master_planner_agent") as mock_agent:
        mock_agent.invoke.return_value = mock_itinerary
        result = run_master_planner(trip)

        assert isinstance(result, Itinerary)
        assert len(result.days) == 3
        assert result.days[0].day == 1
        assert result.days[0].theme == "Arrival & Gion Evening"
        assert len(result.days[0].activities) == 2
        assert result.days[0].activities[0].activity_type == "transit"


def test_run_master_planner_with_all_domain_pillars():
    trip = TripRequest(
        destination="Rome",
        duration_days=4,
        budget=Decimal("1500.00"),
    )
    profile = UserProfile(
        travel_style="Cultural & Foodie",
        walking_tolerance="High",
        food_preferences=["Authentic pasta", "Gelato"],
    )
    research = ResearchResult(
        attractions=[
            Attraction(
                name="Colosseum",
                city="Rome",
                category="Ancient History",
                description="Iconic Roman amphitheater.",
                estimated_duration_minutes=120,
                best_visit_time="Morning",
            ),
            Attraction(
                name="Vatican Museums",
                city="Rome",
                category="Art & History",
                description="Home to the Sistine Chapel.",
                estimated_duration_minutes=180,
                best_visit_time="Early morning",
            ),
        ],
        foods=[
            FoodRecommendation(
                name="Cacio e Pepe",
                city="Rome",
                cuisine="Roman",
                meal_type="Dinner",
                description="Classic Roman pepper and pecorino pasta.",
            )
        ],
    )
    weather = WeatherInfo(
        forecast=[
            WeatherForecast(
                date=date(2026, 10, 10),
                weather_description="Sunny",
                temperature_max_celsius=22.0,
                temperature_min_celsius=14.0,
                precipitation_probability=5,
            ),
            WeatherForecast(
                date=date(2026, 10, 11),
                weather_description="Light Rain",
                temperature_max_celsius=19.0,
                temperature_min_celsius=12.0,
                precipitation_probability=70,
            ),
        ]
    )
    transport = TransportInfo(
        flight_options=[
            FlightOption(airline="ITA Airways", route="FCO to Central Rome")
        ],
        train_options=[
            TrainOption(
                train_name_or_number="Leonardo Express",
                departure_station="FCO Airport",
                arrival_station="Roma Termini",
                duration="32m",
            )
        ],
    )
    hotels = [
        HotelRecommendation(
            name="Hotel Artemide",
            city="Rome",
            price_per_night=Decimal("180.00"),
            rating=4.8,
            description="Boutique stay on Via Nazionale.",
            neighborhood="Monti",
        )
    ]

    with patch("app.agents.master_planner.master_planner_agent") as mock_agent:
        mock_agent.invoke.return_value = Itinerary(
            trip_title="4-Day Rome Journey",
            days=[DailyPlan(day=1), DailyPlan(day=2), DailyPlan(day=3), DailyPlan(day=4)],
        )

        result = run_master_planner(
            trip_request=trip,
            user_profile=profile,
            research_result=research,
            weather_info=weather,
            transport_info=transport,
            hotels=hotels,
        )

        assert len(result.days) == 4
        # Verify prompt received all context
        call_messages = mock_agent.invoke.call_args[0][0]
        prompt_text = call_messages[1][1]
        assert "Rome" in prompt_text
        assert "Colosseum" in prompt_text
        assert "Cacio e Pepe" in prompt_text
        assert "Hotel Artemide" in prompt_text
        assert "Roma Termini" in prompt_text
        assert "Light Rain" in prompt_text


def test_master_planner_fallback_on_error():
    trip = TripRequest(
        destination="Barcelona",
        duration_days=3,
    )
    research = ResearchResult(
        attractions=[
            Attraction(
                name="Sagrada Familia",
                city="Barcelona",
                category="Architecture",
                description="Gaudi masterpiece basilica.",
                estimated_duration_minutes=90,
                best_visit_time="Morning",
            ),
            Attraction(
                name="Park Guell",
                city="Barcelona",
                category="Park",
                description="Whimsical public park by Gaudi.",
                estimated_duration_minutes=120,
                best_visit_time="Late afternoon",
            ),
        ],
        foods=[
            FoodRecommendation(
                name="Tapas & Paella",
                city="Barcelona",
                cuisine="Spanish",
                meal_type="Dinner",
                description="Fresh seafood paella in Barceloneta.",
            )
        ],
    )

    with patch("app.agents.master_planner.master_planner_agent") as mock_agent:
        mock_agent.invoke.side_effect = RuntimeError("OpenRouter credit limit reached")
        result = run_master_planner(trip, research_result=research)

        assert isinstance(result, Itinerary)
        assert len(result.days) == 3
        # Day 1: Arrival & check-in
        assert result.days[0].day == 1
        assert any(a.activity_type == "transit" for a in result.days[0].activities)
        assert any(a.activity_type == "food" for a in result.days[0].activities)
        # Day 2: Full exploration
        assert result.days[1].day == 2
        assert len(result.days[1].activities) >= 3
        # Day 3: Final day / departure
        assert result.days[2].day == 3
        assert any("Checkout" in a.title or "Departure" in a.title or a.activity_type == "transit" for a in result.days[2].activities)


def test_master_planner_node_in_graph():
    trip = TripRequest(
        destination="Paris",
        duration_days=2,
    )
    initial_state = TravelState(trip_request=trip)

    mock_itinerary = Itinerary(
        trip_title="2-Day Paris Highlights",
        days=[
            DailyPlan(
                day=1,
                theme="Eiffel Tower & Seine Cruise",
                activities=[
                    DailyActivity(
                        time="10:00 AM",
                        title="Eiffel Tower",
                        location="Champ de Mars",
                        description="Ascend to the summit.",
                    )
                ],
            ),
            DailyPlan(
                day=2,
                theme="Louvre & Le Marais",
                activities=[
                    DailyActivity(
                        time="09:00 AM",
                        title="Louvre Museum",
                        location="1st Arr.",
                        description="Explore classic art masterworks.",
                    )
                ],
            ),
        ],
    )

    with patch("app.graph.graph.run_master_planner", return_value=mock_itinerary):
        output = master_planner_node(initial_state)

        assert "itinerary" in output
        assert len(output["itinerary"].days) == 2
        assert output["itinerary"].days[0].theme == "Eiffel Tower & Seine Cruise"
