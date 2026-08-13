from app.agents.preferences import preference_node
from app.schemas.travel import TripRequest, UserProfile
from app.graph.state import TravelState


def test_preference_agent():

    profile = UserProfile(
        travel_style="slow travel",
        hotel_preference="boutique hotels",
        walking_tolerance="low",
        food_preferences=["vegetarian"],
        interests=["photography", "hiking"],
    )

    trip_request = TripRequest(
        destination="Japan",
        duration_days=10,
    )

    state = TravelState(
        user_profile=profile,
        trip_request=trip_request,
    )

    result = preference_node(state)

    assert result.user_profile.travel_style == "slow travel"
    assert result.user_profile.hotel_preference == "boutique hotels"
    assert result.user_profile.walking_tolerance == "low"

    assert "vegetarian" in result.user_profile.food_preferences
    assert "photography" in result.user_profile.interests

    assert result.execution.current_agent == "preference"
    assert "preference" in result.execution.completed_agents