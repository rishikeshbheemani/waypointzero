import json
from collections.abc import AsyncGenerator
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage

from app.graph.graph import graph
from app.schemas.api import (
    ChatRefinementRequest,
    PlanTripRequest,
    StreamEvent,
    TripResponse,
    TripStatusResponse,
)

router = APIRouter(prefix="/api/trips", tags=["Trips"])


def _serialize_for_event(obj: Any) -> Any:
    """Helper to convert Pydantic models or complex objects to JSON-serializable primitives."""
    if hasattr(obj, "model_dump"):
        return obj.model_dump(mode="json")
    if isinstance(obj, dict):
        return {k: _serialize_for_event(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_serialize_for_event(v) for v in obj]
    return obj


@router.post("/plan", response_model=TripResponse)
def plan_trip(request: PlanTripRequest):
    """
    Initiate the multi-agent travel planning workflow.
    Fans out discovery agents, synthesizes a daily itinerary, and evaluates the budget.
    """
    config = {"configurable": {"thread_id": request.session_id}}

    initial_state = {
        "trip_request": request.trip_request,
        "user_profile": request.user_profile,
        "messages": [
            HumanMessage(
                content=f"Plan a {request.trip_request.duration_days}-day trip to {request.trip_request.destination}."
            )
        ],
    }

    try:
        result = graph.invoke(initial_state, config=config)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Planning pipeline failed: {str(e)}") from e

    supervisor_decision = result.get("supervisor_decision")
    status = "completed"
    clarification_question = None
    if supervisor_decision and supervisor_decision.needs_clarification:
        status = "needs_clarification"
        clarification_question = supervisor_decision.clarification_question

    return TripResponse(
        session_id=request.session_id,
        status=status,
        clarification_question=clarification_question,
        itinerary=result.get("itinerary"),
        budget=result.get("budget"),
        hotels=result.get("hotels", []),
        transport=result.get("transport"),
        weather=result.get("weather"),
        research=result.get("research"),
    )


@router.post("/chat", response_model=TripResponse)
def chat_refinement(request: ChatRefinementRequest):
    """
    Submit conversational user feedback to refine an existing itinerary in session memory.
    Executes the Master Planner in refinement mode and recalculates the budget.
    """
    config = {"configurable": {"thread_id": request.session_id}}

    # Verify session existence in checkpointer
    checkpoint = graph.get_state(config)
    if not checkpoint or not checkpoint.values:
        raise HTTPException(
            status_code=404,
            detail=f"Session '{request.session_id}' not found. Please plan a trip first.",
        )

    turn_input = {
        "messages": [HumanMessage(content=request.message)],
    }

    try:
        result = graph.invoke(turn_input, config=config)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Refinement pipeline failed: {str(e)}") from e

    return TripResponse(
        session_id=request.session_id,
        status="completed",
        itinerary=result.get("itinerary"),
        budget=result.get("budget"),
        hotels=result.get("hotels", []),
        transport=result.get("transport"),
        weather=result.get("weather"),
        research=result.get("research"),
    )


@router.get("/{session_id}", response_model=TripStatusResponse)
def get_trip_state(session_id: str):
    """
    Retrieve the current persisted trip state and itinerary for an active session.
    """
    config = {"configurable": {"thread_id": session_id}}
    checkpoint = graph.get_state(config)

    if not checkpoint or not checkpoint.values:
        raise HTTPException(
            status_code=404,
            detail=f"Session '{session_id}' not found.",
        )

    vals = checkpoint.values
    trip_req = vals.get("trip_request")
    itinerary = vals.get("itinerary")

    return TripStatusResponse(
        session_id=session_id,
        destination=trip_req.destination if trip_req else None,
        duration_days=trip_req.duration_days if trip_req else None,
        has_itinerary=bool(itinerary and itinerary.days),
        itinerary=itinerary,
        budget=vals.get("budget"),
        hotels=vals.get("hotels", []),
        transport=vals.get("transport"),
        weather=vals.get("weather"),
        research=vals.get("research"),
    )


@router.post("/plan/stream")
async def plan_trip_stream(request: PlanTripRequest):
    """
    Stream real-time progress events over Server-Sent Events (SSE) as each agent executes.
    """
    config = {"configurable": {"thread_id": request.session_id}}

    initial_state = {
        "trip_request": request.trip_request,
        "user_profile": request.user_profile,
        "messages": [
            HumanMessage(
                content=f"Plan a {request.trip_request.duration_days}-day trip to {request.trip_request.destination}."
            )
        ],
    }

    async def event_generator() -> AsyncGenerator[str, None]:
        # Initial event
        start_event = StreamEvent(
            event_type="agent_start",
            agent_name="pipeline",
            data={"session_id": request.session_id, "destination": request.trip_request.destination},
        )
        yield f"data: {json.dumps(start_event.model_dump(mode='json'))}\n\n"

        try:
            for step in graph.stream(initial_state, config=config, stream_mode="updates"):
                for node_name, node_update in step.items():
                    event_data = _serialize_for_event(node_update)
                    event = StreamEvent(
                        event_type="agent_complete",
                        agent_name=node_name,
                        data=event_data if isinstance(event_data, dict) else {"output": event_data},
                    )
                    yield f"data: {json.dumps(event.model_dump(mode='json'))}\n\n"

            complete_event = StreamEvent(
                event_type="pipeline_complete",
                agent_name="pipeline",
                data={"session_id": request.session_id, "status": "completed"},
            )
            yield f"data: {json.dumps(complete_event.model_dump(mode='json'))}\n\n"

        except Exception as err:
            err_event = StreamEvent(
                event_type="error",
                agent_name="pipeline",
                data={"error": str(err)},
            )
            yield f"data: {json.dumps(err_event.model_dump(mode='json'))}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
