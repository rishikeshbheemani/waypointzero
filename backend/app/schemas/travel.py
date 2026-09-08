from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


# ==========================================================
# User Input Models
# ==========================================================

class TripRequest(BaseModel):
    destination: str
    origin: str | None = None
    duration_days: int
    budget: Decimal | None = None
    start_date: date | None = None

    companions: list[str] = Field(default_factory=list)
    interests: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)

    @property
    def travelers(self) -> str:
        return ", ".join(self.companions) if self.companions else "Solo"


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

class WeatherForecast(BaseModel):
    date: date

    temperature_max_celsius: float | None = None
    temperature_min_celsius: float | None = None

    precipitation_probability: int | None = None
    precipitation_mm: float | None = None

    humidity_percent: float | None = None
    wind_speed_kmh: float | None = None

    weather_code: int | None = None

    weather_description: str | None = None
    
class WeatherInfo(BaseModel):
    location: str | None = None

    latitude: float | None = None
    longitude: float | None = None
    timezone: str | None = None

    forecast: list[WeatherForecast] = Field(
        default_factory=list
    )

    seasonal_context: list[str] = Field(
        default_factory=list
    )

    travel_impact: list[str] = Field(
        default_factory=list
    )

    recommendations: list[str] = Field(
        default_factory=list
    )

    warnings: list[str] = Field(
        default_factory=list
    )

class FlightOption(BaseModel):
    airline: str
    route: str
    estimated_price_usd: Decimal | None = None
    notes: str | None = None


class TrainOption(BaseModel):
    train_name_or_number: str
    departure_station: str
    arrival_station: str
    duration: str
    estimated_price_usd: Decimal | None = None
    travel_class: str | None = None
    trade_offs: str | None = None


class TransitOption(BaseModel):
    mode: str
    route_or_system: str
    estimated_cost: Decimal | None = None
    description: str


class TransportPass(BaseModel):
    name: str
    coverage: str
    estimated_price: Decimal | None = None
    is_recommended: bool = True
    tips: str | None = None


class TransportInfo(BaseModel):
    recommended_flights: list[str] = Field(default_factory=list)
    flight_options: list[FlightOption] = Field(default_factory=list)

    train_options: list[TrainOption] = Field(default_factory=list)

    local_transport: list[str] = Field(default_factory=list)
    transit_options: list[TransitOption] = Field(default_factory=list)

    travel_passes: list[str] = Field(default_factory=list)
    pass_options: list[TransportPass] = Field(default_factory=list)

    airport_transfers: list[str] = Field(default_factory=list)
    estimated_transport_cost: Decimal | None = None
    tips: list[str] = Field(default_factory=list)

class HotelRecommendation(BaseModel):
    name: str
    city: str
    price_per_night: Decimal
    rating: float
    description: str

    neighborhood: str | None = None
    category: str | None = None
    location_advantage: str | None = None
    amenities: list[str] = Field(default_factory=list)
    booking_url: str | None = None


class AccommodationResult(BaseModel):
    hotels: list[HotelRecommendation] = Field(default_factory=list)
    neighborhood_insights: list[str] = Field(default_factory=list)

class BudgetInfo(BaseModel):
    flights: Decimal = Decimal("0")
    accommodation: Decimal = Decimal("0")
    food: Decimal = Decimal("0")
    transportation: Decimal = Decimal("0")
    activities: Decimal = Decimal("0")

    total: Decimal = Decimal("0")
    remaining: Decimal | None = None
    status: str = "within_budget"
    currency: str = "USD"
    cost_saving_tips: list[str] = Field(default_factory=list)

class DailyActivity(BaseModel):
    time: str
    title: str
    location: str
    description: str

    activity_type: str | None = None
    cost_estimate: Decimal | None = None


class DailyPlan(BaseModel):
    day: int
    theme: str | None = None
    day_summary: str | None = None

    activities: list[DailyActivity] = Field(
        default_factory=list,
        description="Chronological list of 3 to 5 activities for this day (morning sightseeing, lunch, afternoon experience, dinner).",
    )


class Itinerary(BaseModel):
    trip_title: str | None = None
    summary: str | None = None
    days: list[DailyPlan] = Field(default_factory=list)

class ExecutionState(BaseModel):
    current_agent: str | None = None

    completed_agents: list[str] = Field(default_factory=list)

    failed_agents: list[str] = Field(default_factory=list)

    status: str = "idle"

    error_message: str | None = None