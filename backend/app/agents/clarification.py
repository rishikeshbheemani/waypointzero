from app.graph.state import TravelState


def clarification_node(state: TravelState):
    decision = state.supervisor_decision

    return {
        "execution": state.execution.model_copy(
            update={
                "current_agent": "clarification",
                "status": "waiting_for_user",
            }
        ),
        "messages": [
            {
                "role": "assistant",
                "content": (
                    decision.clarification_question
                    or "I need a little more information before planning your trip."
                ),
            }
        ],
    }