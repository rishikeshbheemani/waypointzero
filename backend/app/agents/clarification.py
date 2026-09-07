from app.graph.state import TravelState


def clarification_node(state: TravelState):
    decision = state.supervisor_decision

    question = (
        decision.clarification_question
        if decision and decision.clarification_question
        else "I need a little more information before planning your trip."
    )

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
                "content": question,
            }
        ],
    }