from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field

from app.schemas.travel import (
    BudgetInfo,
    HotelRecommendation,
    Itinerary,
    ResearchResult,
    TransportInfo,
    TripRequest,
    UserProfile,
    WeatherInfo,
)


class PlanTripRequest(BaseModel):
    """Payload to initiate an autonomous travel planning workflow."""

    trip_request: TripRequest
    user_profile: UserProfile = Field(default_factory=UserProfile)
    session_id: str = Field(default_factory=lambda: str(uuid4()))


class ChatRefinementRequest(BaseModel):
    """Payload to refine an existing plan via conversational feedback."""

    session_id: str
    message: str = Field(..., min_length=1, description="User's feedback or revision request")


class TripResponse(BaseModel):
    """Complete response returned after graph execution."""

    session_id: str
    status: Literal["completed", "needs_clarification", "error"] = "completed"
    clarification_question: str | None = None

    itinerary: Itinerary | None = None
    budget: BudgetInfo | None = None
    hotels: list[HotelRecommendation] = Field(default_factory=list)
    transport: TransportInfo | None = None
    weather: WeatherInfo | None = None
    research: ResearchResult | None = None


class TripStatusResponse(BaseModel):
    """Current state snapshot for a given trip session."""

    session_id: str
    destination: str | None = None
    duration_days: int | None = None
    has_itinerary: bool = False
    itinerary: Itinerary | None = None
    budget: BudgetInfo | None = None
    hotels: list[HotelRecommendation] = Field(default_factory=list)
    transport: TransportInfo | None = None
    weather: WeatherInfo | None = None
    research: ResearchResult | None = None


class StreamEvent(BaseModel):
    """Event payload emitted over Server-Sent Events (SSE)."""

    event_type: Literal[
        "agent_start",
        "agent_complete",
        "clarification_needed",
        "pipeline_complete",
        "error",
    ]
    agent_name: str | None = None
    data: dict[str, Any] = Field(default_factory=dict)
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
