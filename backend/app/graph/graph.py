from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from app.graph.state import TravelState
from app.schemas.travel import Itinerary

from app.agents.supervisor import run_supervisor
from app.agents.preferences import preference_node
from app.agents.clarification import clarification_node
from app.agents.research import run_research_agent
from app.agents.weather import run_weather_agent
from app.agents.transport import run_transport_agent
from app.agents.accommodation import run_accommodation_agent
from app.agents.master_planner import run_master_planner

from app.agents.placeholders import (
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

    if decision and decision.needs_clarification:
        return "clarification"

    return "preference"


# Preference Routing

def route_after_preference(state: TravelState):
    """
    Decide which specialized agents should run after
    the Preference Agent.
    """

    # Multi-turn refinement: if itinerary already exists in memory and user provided feedback,
    # route straight to master_planner for surgical update without re-running all search agents.
    if state.itinerary and state.itinerary.days and state.messages:
        return ["master_planner"]

    decision = state.supervisor_decision
    if not decision:
        return ["research", "weather", "transport"]

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


# Transport Node

def transport_node(state: TravelState):
    """
    Execute the Transport Agent.

    This node writes to the transport field.
    """

    transport_result = run_transport_agent(
        state.trip_request,
        state.user_profile,
    )

    return {
        "transport": transport_result,
    }


# Accommodation Node

def accommodation_node(state: TravelState):
    """
    Execute the Accommodation Agent.

    This node writes to the hotels field.
    """

    hotels = run_accommodation_agent(
        trip_request=state.trip_request,
        user_profile=state.user_profile,
        research_result=state.research,
        transport_info=state.transport,
    )

    return {
        "hotels": hotels,
    }


# Master Planner Node

def master_planner_node(state: TravelState):
    """
    Execute the Master Planner Agent.

    Synthesizes research, weather, transport, and hotels
    into the day-by-day itinerary. Supports multi-turn refinement
    if an itinerary already exists in session memory and user feedback is supplied.
    """

    user_feedback: str | None = None
    if state.messages:
        for msg in reversed(state.messages):
            if isinstance(msg, dict):
                content = msg.get("content")
                role = msg.get("role") or msg.get("type")
                if role in ("user", "human") and content:
                    user_feedback = str(content)
                    break
            elif hasattr(msg, "content") and msg.content:
                msg_type = getattr(msg, "type", None) or type(msg).__name__
                if msg_type in ("human", "HumanMessage", "user"):
                    if isinstance(msg.content, str):
                        user_feedback = msg.content
                    elif isinstance(msg.content, list):
                        user_feedback = " ".join(
                            str(item.get("text", item) if isinstance(item, dict) else item)
                            for item in msg.content
                        )
                    else:
                        user_feedback = str(msg.content)
                    break

    existing_itinerary: Itinerary | None = (
        state.itinerary if (state.itinerary and state.itinerary.days) else None
    )

    itinerary = run_master_planner(
        trip_request=state.trip_request,
        user_profile=state.user_profile,
        research_result=state.research,
        weather_info=state.weather,
        transport_info=state.transport,
        hotels=state.hotels,
        current_itinerary=existing_itinerary,
        user_feedback=user_feedback if existing_itinerary is not None else None,
    )

    return {
        "itinerary": itinerary,
    }


def activities_node(state: TravelState):
    """Delegate to master_planner_node for backward compatibility."""
    return master_planner_node(state)


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
    "master_planner",
    master_planner_node,
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
        "master_planner": "master_planner",
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
    "master_planner",
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


# Compile with Session Memory Checkpointer

checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)