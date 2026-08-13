from langgraph.graph import StateGraph, START, END

from app.graph.state import TravelState
from app.agents.supervisor import run_supervisor
from app.agents.placeholders import (
    research_node,
    weather_node,
    transport_node,
    accommodation_node,
    activities_node,
    budget_node,
)
from app.agents.clarification import clarification_node

def supervisor_node(state: TravelState):
    decision = run_supervisor(
        state.trip_request.model_dump_json()
    )

    execution = state.execution.model_copy(
        update={
            "current_agent": "supervisor",
            "status": "running",
            "completed_agents": ["supervisor"],
        }
    )

    return {
        "supervisor_decision": decision,
        "execution": execution,
    }


def route_from_supervisor(state: TravelState):

    decision = state.supervisor_decision

    if decision.needs_clarification:
        return "clarification"

    routes = []

    if decision.invoke_research:
        routes.append("research")

    if decision.invoke_weather:
        routes.append("weather")

    if decision.invoke_transport:
        routes.append("transport")

    if decision.invoke_accommodation:
        routes.append("accommodation")

    if decision.invoke_activities:
        routes.append("activities")

    if decision.invoke_budget:
        routes.append("budget")

    return routes


builder = StateGraph(TravelState)

builder.add_node("supervisor", supervisor_node)
builder.add_node("research", research_node)
builder.add_node("weather", weather_node)
builder.add_node("transport", transport_node)
builder.add_node("accommodation", accommodation_node)
builder.add_node("activities", activities_node)
builder.add_node("budget", budget_node)
builder.add_node("clarification", clarification_node)
builder.add_edge(START, "supervisor")

builder.add_conditional_edges(
    "supervisor",
    route_from_supervisor,
    {
        "clarification": "clarification",
        "research": "research",
        "weather": "weather",
        "transport": "transport",
        "accommodation": "accommodation",
        "activities": "activities",
        "budget": "budget",
    },
)

builder.add_edge("research", END)
builder.add_edge("weather", END)
builder.add_edge("transport", END)
builder.add_edge("accommodation", END)
builder.add_edge("activities", END)
builder.add_edge("budget", END)
builder.add_edge("clarification", END)


graph = builder.compile()