from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


# ==========================================================
# User Input Models
# ==========================================================

class TripRequest(BaseModel):
    destination: str
    duration_days: int
    budget: Decimal | None = None
    start_date: date | None = None

    companions: list[str] = Field(default_factory=list)
    interests: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)


class UserProfile(BaseModel):
    travel_style: str | None = None
    budget_range: Decimal | None = None
    hotel_preference: str | None = None
    walking_tolerance: str | None = None

    food_preferences: list[str] = Field(default_factory=list)
    interests: list[str] = Field(default_factory=list)
    preferred_airlines: list[str] = Field(default_factory=list)
    visited_countries: list[str] = Field(default_factory=list)


# ==========================================================
# Knowledge Models
# ==========================================================

class Attraction(BaseModel):
    name: str
    city: str
    category: str
    description: str

    estimated_duration_minutes: int
    best_visit_time: str


class FoodRecommendation(BaseModel):
    name: str
    city: str
    cuisine: str
    meal_type: str
    description: str

    vegetarian_available: bool = False


class Festival(BaseModel):
    name: str
    city: str
    month: str
    description: str

class ResearchSource(BaseModel):
    title: str
    url: str
    source_type: str
    relevance: float | None = None
    verification_status: str = "unverified"

class ResearchResult(BaseModel):
    attractions: list[Attraction] = Field(default_factory=list)
    hidden_gems: list[Attraction] = Field(default_factory=list)

    foods: list[FoodRecommendation] = Field(default_factory=list)
    festivals: list[Festival] = Field(default_factory=list)

    local_customs: list[str] = Field(default_factory=list)
    travel_tips: list[str] = Field(default_factory=list)
    safety_notes: list[str] = Field(default_factory=list)

    sources: list[ResearchSource] = Field(default_factory=list)
    verification_notes: list[str] = Field(default_factory=list)

class WeatherInfo(BaseModel):
    temperature_celsius: float | None = None
    condition: str | None = None
    rain_probability: int | None = None

    sunrise: str | None = None
    sunset: str | None = None

    warnings: list[str] = Field(default_factory=list)

class TransportInfo(BaseModel):
    recommended_flights: list[str] = Field(default_factory=list)
    local_transport: list[str] = Field(default_factory=list)
    travel_passes: list[str] = Field(default_factory=list)

class HotelRecommendation(BaseModel):
    name: str
    city: str

    price_per_night: Decimal

    rating: float

    description: str

class BudgetInfo(BaseModel):
    flights: Decimal = Decimal("0")
    accommodation: Decimal = Decimal("0")
    food: Decimal = Decimal("0")
    transportation: Decimal = Decimal("0")
    activities: Decimal = Decimal("0")

    total: Decimal = Decimal("0")
    remaining: Decimal | None = None

class DailyActivity(BaseModel):
    time: str
    title: str
    location: str
    description: str

class DailyPlan(BaseModel):
    day: int

    activities: list[DailyActivity] = Field(default_factory=list)

class Itinerary(BaseModel):
    days: list[DailyPlan] = Field(default_factory=list)

class ExecutionState(BaseModel):
    current_agent: str | None = None

    completed_agents: list[str] = Field(default_factory=list)

    failed_agents: list[str] = Field(default_factory=list)

    status: str = "idle"

    error_message: str | None = None