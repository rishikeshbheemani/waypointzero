from langgraph.graph import StateGraph, START, END

from app.graph.state import TravelState


def test_state_node(state: TravelState) -> TravelState:
    """
    Simple test node to verify that TravelState
    can pass through a LangGraph workflow.
    """

    state.execution.status = "running"
    state.execution.current_agent = "test_node"

    return state


# Create the graph
builder = StateGraph(TravelState)

# Add our test node
builder.add_node("test_state", test_state_node)

# Define the flow
builder.add_edge(START, "test_state")
builder.add_edge("test_state", END)

# Compile the graph
graph = builder.compile()