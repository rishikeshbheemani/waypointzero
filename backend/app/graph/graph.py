from langgraph.graph import StateGraph, START, END

from app.graph.state import TravelState

from app.agents.supervisor import run_supervisor
from app.agents.preferences import preference_node
from app.agents.clarification import clarification_node
from app.agents.research import run_research_agent
from app.agents.weather import run_weather_agent

from app.agents.placeholders import (
    transport_node,
    accommodation_node,
    activities_node,
    budget_node,
)


# Supervisor Node

def supervisor_node(state: TravelState):
    """
    Run the Supervisor Agent and store its decision
    in the shared TravelState.
    """

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


# Supervisor Routing

def route_from_supervisor(state: TravelState):
    """
    Route incomplete requests to clarification.

    Complete requests continue to the Preference Agent.
    """

    decision = state.supervisor_decision

    if decision.needs_clarification:
        return "clarification"

    return "preference"


# Preference Routing

def route_after_preference(state: TravelState):
    """
    Decide which specialized agents should run after
    the Preference Agent.
    """

    decision = state.supervisor_decision

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


# Research Node

def research_node(state: TravelState):
    """
    Execute the Research Agent.

    This node only writes to the research field.

    It does NOT update execution because multiple
    specialized agents can run in parallel.
    """

    research_result = run_research_agent(
        state.trip_request
    )

    return {
        "research": research_result,
    }


# Weather Node

def weather_node(state: TravelState):
    """
    Execute the Weather Agent.

    This node only writes to the weather field.

    It does NOT update execution because multiple
    specialized agents can run in parallel.
    """

    weather_result = run_weather_agent(
        state.trip_request
    )

    return {
        "weather": weather_result,
    }


# Build Graph

builder = StateGraph(TravelState)


# Nodes

builder.add_node(
    "supervisor",
    supervisor_node,
)

builder.add_node(
    "preference",
    preference_node,
)

builder.add_node(
    "clarification",
    clarification_node,
)

builder.add_node(
    "research",
    research_node,
)

builder.add_node(
    "weather",
    weather_node,
)

builder.add_node(
    "transport",
    transport_node,
)

builder.add_node(
    "accommodation",
    accommodation_node,
)

builder.add_node(
    "activities",
    activities_node,
)

builder.add_node(
    "budget",
    budget_node,
)


# START → Supervisor

builder.add_edge(
    START,
    "supervisor",
)


# Supervisor → Clarification / Preference

builder.add_conditional_edges(
    "supervisor",
    route_from_supervisor,
    {
        "clarification": "clarification",
        "preference": "preference",
    },
)


# Preference → Specialized Agents

builder.add_conditional_edges(
    "preference",
    route_after_preference,
    {
        "research": "research",
        "weather": "weather",
        "transport": "transport",
        "accommodation": "accommodation",
        "activities": "activities",
        "budget": "budget",
    },
)


# Specialized Agents → END

builder.add_edge(
    "research",
    END,
)

builder.add_edge(
    "weather",
    END,
)

builder.add_edge(
    "transport",
    END,
)

builder.add_edge(
    "accommodation",
    END,
)

builder.add_edge(
    "activities",
    END,
)

builder.add_edge(
    "budget",
    END,
)

builder.add_edge(
    "clarification",
    END,
)


# Compile

graph = builder.compile()