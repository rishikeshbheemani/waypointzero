from typing import Annotated

from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field

from app.schemas.travel import (
    BudgetInfo,
    ExecutionState,
    HotelRecommendation,
    Itinerary,
    ResearchResult,
    TransportInfo,
    TripRequest,
    UserProfile,
    WeatherInfo,
)

class TravelState(BaseModel):
    """
    Shared state passed between every LangGraph node.
    """

    # ==========================
    # User Information
    # ==========================

    user_profile: UserProfile = Field(default_factory=UserProfile)
    trip_request: TripRequest

    # ==========================
    # Knowledge Produced
    # ==========================

    research: ResearchResult = Field(default_factory=ResearchResult)
    weather: WeatherInfo = Field(default_factory=WeatherInfo)
    transport: TransportInfo = Field(default_factory=TransportInfo)

    hotels: list[HotelRecommendation] = Field(default_factory=list)

    budget: BudgetInfo = Field(default_factory=BudgetInfo)

    itinerary: Itinerary = Field(default_factory=Itinerary)

    # ==========================
    # Workflow
    # ==========================

    execution: ExecutionState = Field(default_factory=ExecutionState)

    approved: bool = False

    # ==========================
    # Conversation
    # ==========================

    messages: Annotated[
        list[BaseMessage],
        add_messages,
    ] = Field(default_factory=list)