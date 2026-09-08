import json
import logging
from collections.abc import AsyncGenerator
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.graph.graph import graph
from app.models.trip import ChatMessageRecord, TripRecord
from app.schemas.api import (
    ChatRefinementRequest,
    PlanTripRequest,
    StreamEvent,
    TripResponse,
    TripStatusResponse,
)
from app.schemas.travel import (
    BudgetInfo,
    HotelRecommendation,
    Itinerary,
    ResearchResult,
    TransportInfo,
    TripRequest,
    WeatherInfo,
)

logger = logging.getLogger(__name__)

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


def _save_trip_record(
    db: Session,
    session_id: str,
    trip_request: TripRequest,
    result: dict[str, Any],
    status: str = "completed",
    clarification_question: str | None = None,
) -> TripRecord | None:
    """Persist or update TripRecord in the database."""
    try:
        itinerary = result.get("itinerary")
        budget = result.get("budget")
        hotels = result.get("hotels", [])
        transport = result.get("transport")
        weather = result.get("weather")
        research = result.get("research")

        record = db.query(TripRecord).filter(TripRecord.id == session_id).first()
        if not record:
            record = TripRecord(
                id=session_id,
                destination=trip_request.destination,
                duration_days=trip_request.duration_days,
            )
            db.add(record)

        record.destination = trip_request.destination
        record.duration_days = trip_request.duration_days
        record.budget = str(trip_request.budget) if trip_request.budget is not None else None
        record.status = status
        record.clarification_question = clarification_question
        record.trip_request_json = trip_request.model_dump_json()

        if itinerary and hasattr(itinerary, "model_dump_json"):
            record.itinerary_json = itinerary.model_dump_json()
        if budget and hasattr(budget, "model_dump_json"):
            record.budget_json = budget.model_dump_json()
        if hotels:
            record.hotels_json = json.dumps(
                [h.model_dump(mode="json") if hasattr(h, "model_dump") else h for h in hotels]
            )
        if transport and hasattr(transport, "model_dump_json"):
            record.transport_json = transport.model_dump_json()
        if weather and hasattr(weather, "model_dump_json"):
            record.weather_json = weather.model_dump_json()
        if research and hasattr(research, "model_dump_json"):
            record.research_json = research.model_dump_json()

        db.commit()
        db.refresh(record)
        return record
    except Exception as e:
        logger.error(f"Failed to persist trip record to database: {e}")
        db.rollback()
        return None


def _parse_trip_record_to_response(record: TripRecord) -> TripStatusResponse:
    """Convert a database TripRecord into a TripStatusResponse."""
    itinerary: Itinerary | None = None
    if record.itinerary_json:
        try:
            itinerary = Itinerary.model_validate_json(record.itinerary_json)
        except Exception:
            pass

    budget: BudgetInfo | None = None
    if record.budget_json:
        try:
            budget = BudgetInfo.model_validate_json(record.budget_json)
        except Exception:
            pass

    hotels: list[HotelRecommendation] = []
    if record.hotels_json:
        try:
            raw_hotels = json.loads(record.hotels_json)
            hotels = [HotelRecommendation.model_validate(h) for h in raw_hotels]
        except Exception:
            pass

    transport: TransportInfo | None = None
    if record.transport_json:
        try:
            transport = TransportInfo.model_validate_json(record.transport_json)
        except Exception:
            pass

    weather: WeatherInfo | None = None
    if record.weather_json:
        try:
            weather = WeatherInfo.model_validate_json(record.weather_json)
        except Exception:
            pass

    research: ResearchResult | None = None
    if record.research_json:
        try:
            research = ResearchResult.model_validate_json(record.research_json)
        except Exception:
            pass

    return TripStatusResponse(
        session_id=str(record.id),
        destination=str(record.destination) if record.destination else None,
        duration_days=int(record.duration_days) if record.duration_days is not None else None,
        has_itinerary=bool(itinerary and getattr(itinerary, "days", None)),
        itinerary=itinerary,
        budget=budget,
        hotels=hotels,
        transport=transport,
        weather=weather,
        research=research,
    )


@router.get("", response_model=list[TripStatusResponse])
def list_trips(limit: int = 20, db: Session = Depends(get_db)):
    """
    List all previously generated trips ordered by creation date.
    """
    records = db.query(TripRecord).order_by(TripRecord.created_at.desc()).limit(limit).all()
    return [_parse_trip_record_to_response(r) for r in records]


@router.post("/plan", response_model=TripResponse)
def plan_trip(request: PlanTripRequest, db: Session = Depends(get_db)):
    """
    Initiate the multi-agent travel planning workflow.
    Fans out discovery agents, synthesizes a daily itinerary, evaluates the budget,
    and persists the result in the database.
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
    status: Literal["completed", "needs_clarification", "error"] = "completed"
    clarification_question: str | None = None
    if supervisor_decision and supervisor_decision.needs_clarification:
        status = "needs_clarification"
        clarification_question = supervisor_decision.clarification_question

    # Persist in DB
    _save_trip_record(
        db=db,
        session_id=request.session_id,
        trip_request=request.trip_request,
        result=result,
        status=status,
        clarification_question=clarification_question,
    )

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
def chat_refinement(request: ChatRefinementRequest, db: Session = Depends(get_db)):
    """
    Submit conversational user feedback to refine an existing itinerary in session memory.
    Executes the Master Planner in refinement mode and updates the database record.
    """
    config = {"configurable": {"thread_id": request.session_id}}

    checkpoint = graph.get_state(config)
    trip_record = db.query(TripRecord).filter(TripRecord.id == request.session_id).first()

    if (checkpoint is None or not getattr(checkpoint, "values", None)) and trip_record is None:
        raise HTTPException(
            status_code=404,
            detail=f"Session '{request.session_id}' not found. Please plan a trip first.",
        )

    # Save user message to database
    try:
        user_msg = ChatMessageRecord(
            session_id=request.session_id,
            role="user",
            content=request.message,
        )
        db.add(user_msg)
        db.commit()
    except Exception as e:
        logger.error(f"Failed to save user chat message: {e}")
        db.rollback()

    turn_input = {
        "messages": [HumanMessage(content=request.message)],
    }

    try:
        result = graph.invoke(turn_input, config=config)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Refinement pipeline failed: {str(e)}") from e

    # Update database record with refined itinerary and budget
    if trip_record is not None:
        try:
            itinerary = result.get("itinerary")
            budget = result.get("budget")
            if itinerary and hasattr(itinerary, "model_dump_json"):
                trip_record.itinerary_json = itinerary.model_dump_json()
            if budget and hasattr(budget, "model_dump_json"):
                trip_record.budget_json = budget.model_dump_json()
            db.commit()
        except Exception as e:
            logger.error(f"Failed to update trip record with refined state: {e}")
            db.rollback()

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
def get_trip_state(session_id: str, db: Session = Depends(get_db)):
    """
    Retrieve current trip state. Checks active in-memory checkpointer first,
    and falls back seamlessly to the database if the server restarted.
    """
    config = {"configurable": {"thread_id": session_id}}
    checkpoint = graph.get_state(config)

    if checkpoint and getattr(checkpoint, "values", None) and checkpoint.values.get("trip_request"):
        vals = checkpoint.values
        trip_req = vals.get("trip_request")
        itinerary = vals.get("itinerary")

        return TripStatusResponse(
            session_id=session_id,
            destination=trip_req.destination if trip_req else None,
            duration_days=trip_req.duration_days if trip_req else None,
            has_itinerary=bool(itinerary and getattr(itinerary, "days", None)),
            itinerary=itinerary,
            budget=vals.get("budget"),
            hotels=vals.get("hotels", []),
            transport=vals.get("transport"),
            weather=vals.get("weather"),
            research=vals.get("research"),
        )

    # Fallback to database
    record = db.query(TripRecord).filter(TripRecord.id == session_id).first()
    if not record:
        raise HTTPException(
            status_code=404,
            detail=f"Session '{session_id}' not found.",
        )

    return _parse_trip_record_to_response(record)


@router.post("/plan/stream")
async def plan_trip_stream(request: PlanTripRequest, db: Session = Depends(get_db)):
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
