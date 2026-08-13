from app.graph.state import TravelState


def preference_node(state: TravelState) -> TravelState:
    """
    Load and apply the user's travel preferences.

    For the initial implementation, preferences already live
    inside TravelState.user_profile, so this node validates that
    the profile is available and marks the Preference Agent as
    completed.
    """

    state.execution.current_agent = "preference"
    state.execution.completed_agents.append("preference")

    return state