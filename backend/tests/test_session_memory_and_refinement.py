from decimal import Decimal
from unittest.mock import patch
from langchain_core.messages import HumanMessage

from app.agents.master_planner import _fallback_refinement, run_master_planner
from app.graph.graph import graph, route_after_preference
from app.graph.state import TravelState
from app.schemas.travel import (
    DailyActivity,
    DailyPlan,
    Itinerary,
    TripRequest,
)


def test_master_planner_refinement_mode():
    trip = TripRequest(
        destination="Tokyo",
        duration_days=3,
        budget=Decimal("2000.00"),
    )

    base_itinerary = Itinerary(
        trip_title="3-Day Tokyo Journey",
        summary="A cultural journey in Tokyo.",
        days=[
            DailyPlan(
                day=1,
                theme="Arrival in Shinjuku",
                activities=[
                    DailyActivity(
                        time="03:00 PM",
                        title="Check-in",
                        location="Shinjuku",
                        description="Check into hotel.",
                    )
                ],
            ),
            DailyPlan(
                day=2,
                theme="Shibuya Exploration",
                activities=[
                    DailyActivity(
                        time="07:00 PM",
                        title="Yakitori Dinner",
                        location="Omoide Yokocho",
                        description="Traditional chicken skewers.",
                        activity_type="food",
                    )
                ],
            ),
            DailyPlan(
                day=3,
                theme="Departure",
                activities=[
                    DailyActivity(
                        time="11:00 AM",
                        title="Checkout",
                        location="Shinjuku",
                        description="Transit to airport.",
                    )
                ],
            ),
        ],
    )

    revised_itinerary = base_itinerary.model_copy(deep=True)
    revised_itinerary.days[1].activities[0] = DailyActivity(
        time="07:00 PM",
        title="Vegan Sushi Dinner",
        location="Shibuya",
        description="Plant-based sushi tasting menu.",
        activity_type="food",
    )

    with patch("app.agents.master_planner.master_planner_agent") as mock_agent:
        mock_agent.invoke.return_value = revised_itinerary

        result = run_master_planner(
            trip_request=trip,
            current_itinerary=base_itinerary,
            user_feedback="Change Day 2 dinner to vegan sushi in Shibuya",
        )

        assert result.days[1].activities[0].title == "Vegan Sushi Dinner"
        # Verify refinement prompt contains the existing itinerary and user feedback
        assert mock_agent.invoke.call_args is not None
        call_args = mock_agent.invoke.call_args[0][0]
        prompt_content = call_args[1][1]
        assert "Existing Itinerary to Revise:" in prompt_content
        assert "Change Day 2 dinner to vegan sushi in Shibuya" in prompt_content


def test_master_planner_fallback_refinement():
    base_itinerary = Itinerary(
        trip_title="Trip to Paris",
        summary="Classic Paris trip.",
        days=[DailyPlan(day=1, activities=[DailyActivity(time="10:00 AM", title="Louvre", location="Paris", description="Museum")])],
    )

    result = _fallback_refinement(base_itinerary, "Make Day 1 start at 11 AM")
    assert result.summary is not None
    assert "[Updated: Make Day 1 start at 11 AM]" in result.summary
    assert len(result.days) == 1


def test_route_after_preference_multi_turn_refinement():
    trip = TripRequest(
        destination="Rome",
        duration_days=3,
    )
    existing_itinerary = Itinerary(
        trip_title="Rome",
        days=[DailyPlan(day=1, activities=[DailyActivity(time="10:00 AM", title="Colosseum", location="Rome", description="History")])],
    )

    state_with_itinerary = TravelState(
        trip_request=trip,
        itinerary=existing_itinerary,
        messages=[HumanMessage(content="Can we swap Day 1 afternoon for a gelato tour?")],
    )

    routes = route_after_preference(state_with_itinerary)
    # Should route directly to master_planner without re-running search agents
    assert routes == ["master_planner"]


def test_graph_session_memory_checkpointer():
    from app.schemas.travel import ResearchResult, WeatherInfo, TransportInfo
    from app.models.supervisor import SupervisorDecision

    trip = TripRequest(
        destination="Singapore",
        duration_days=2,
    )

    config = {"configurable": {"thread_id": "session-memory-test-thread"}}

    mock_itinerary = Itinerary(
        trip_title="Singapore 2-Day",
        days=[DailyPlan(day=1, activities=[DailyActivity(time="10:00 AM", title="Marina Bay", location="Singapore", description="Walk")])],
    )

    supervisor_mock = SupervisorDecision(
        invoke_preference=True,
        invoke_research=True,
        invoke_weather=True,
        invoke_transport=True,
        invoke_accommodation=True,
        invoke_activities=True,
    )

    with (
        patch("app.graph.graph.run_supervisor", return_value=supervisor_mock),
        patch("app.graph.graph.run_research_agent", return_value=ResearchResult()),
        patch("app.graph.graph.run_weather_agent", return_value=WeatherInfo()),
        patch("app.graph.graph.run_transport_agent", return_value=TransportInfo()),
        patch("app.graph.graph.run_accommodation_agent", return_value=[]),
        patch("app.graph.graph.run_master_planner", return_value=mock_itinerary) as mock_master_planner,
    ):
        initial_input = {
            "trip_request": trip,
            "messages": [HumanMessage(content="Plan a 2-day trip to Singapore")],
        }

        # Turn 1
        result_turn_1 = graph.invoke(initial_input, config=config)
        assert result_turn_1["itinerary"] is not None
        assert result_turn_1["itinerary"].trip_title == "Singapore 2-Day"

        # Check that checkpointer saved the state under the thread_id
        checkpoint_state = graph.get_state(config)
        assert checkpoint_state.values["trip_request"].destination == "Singapore"
        assert checkpoint_state.values["itinerary"].trip_title == "Singapore 2-Day"

        # Turn 2: User requests refinement on the same thread_id
        refinement_itinerary = Itinerary(
            trip_title="Singapore 2-Day (Updated)",
            days=[DailyPlan(day=1, activities=[DailyActivity(time="10:00 AM", title="Gardens by the Bay", location="Singapore", description="Flowers")])],
        )
        mock_master_planner.return_value = refinement_itinerary
        turn_2_input = {
            "messages": [HumanMessage(content="Swap Marina Bay for Gardens by the Bay")],
        }
        result_turn_2 = graph.invoke(turn_2_input, config=config)
        assert result_turn_2["itinerary"].trip_title == "Singapore 2-Day (Updated)"

        # Verify checkpoint has preserved both trip_request from Turn 1 and updated itinerary from Turn 2!
        updated_checkpoint = graph.get_state(config)
        assert updated_checkpoint.values["trip_request"].destination == "Singapore"
        assert updated_checkpoint.values["itinerary"].trip_title == "Singapore 2-Day (Updated)"
