import logging
from decimal import Decimal
from langchain_openrouter import ChatOpenRouter

from app.config.settings import settings
from app.prompts.budget import BUDGET_SYSTEM_PROMPT
from app.schemas.travel import (
    BudgetInfo,
    HotelRecommendation,
    Itinerary,
    TransportInfo,
    TripRequest,
    UserProfile,
)

logger = logging.getLogger(__name__)


def create_budget_agent():
    llm = ChatOpenRouter(
        model=settings.MODEL_NAME,
        api_key=settings.OPENROUTER_API_KEY,
        temperature=0.1,
        max_tokens=1000,
    )
    return llm.with_structured_output(BudgetInfo)


budget_agent = create_budget_agent()


def calculate_base_budget(
    trip_request: TripRequest,
    transport_info: TransportInfo | None = None,
    hotels: list[HotelRecommendation] | None = None,
    itinerary: Itinerary | None = None,
    user_profile: UserProfile | None = None,
) -> BudgetInfo:
    """
    Deterministically calculate base budget using exact Decimal arithmetic:
    1. Flights: from transport_info.flight_options
    2. Accommodation: primary hotel price_per_night * nights
    3. Transportation: transit pass or daily local transport
    4. Activities: sum of activity cost estimates in itinerary
    5. Food: estimated daily meal allowance based on destination and travel style
    """
    duration = max(1, trip_request.duration_days)
    nights = max(1, duration - 1) if duration > 1 else 1

    # 1. Flights
    flights = Decimal("0")
    if transport_info and transport_info.flight_options:
        for f in transport_info.flight_options:
            if f.estimated_price_usd is not None and f.estimated_price_usd > 0:
                flights = Decimal(str(f.estimated_price_usd))
                break
    elif transport_info and transport_info.train_options:
        for t in transport_info.train_options:
            if t.estimated_price_usd is not None and t.estimated_price_usd > 0:
                flights = Decimal(str(t.estimated_price_usd))
                break

    # 2. Accommodation
    accommodation = Decimal("0")
    if hotels and len(hotels) > 0:
        primary_hotel = hotels[0]
        hotel_price = getattr(primary_hotel, "price_per_night", None) or getattr(primary_hotel, "price_per_night_usd", None)
        if hotel_price is not None and hotel_price > 0:
            accommodation = Decimal(str(hotel_price)) * Decimal(nights)
        else:
            accommodation = _estimate_hotel_cost(primary_hotel.category or "", nights)
    else:
        style = (user_profile.travel_style or "").lower() if user_profile else ""
        if "luxury" in style:
            accommodation = Decimal("300") * Decimal(nights)
        elif "budget" in style or "backpacker" in style:
            accommodation = Decimal("50") * Decimal(nights)
        else:
            accommodation = Decimal("130") * Decimal(nights)

    # 3. Local Transportation
    transportation = Decimal("0")
    if transport_info and transport_info.pass_options:
        pass_opt = transport_info.pass_options[0]
        if pass_opt.estimated_price is not None and pass_opt.estimated_price > 0:
            transportation = Decimal(str(pass_opt.estimated_price))
        else:
            transportation = Decimal("15") * Decimal(duration)
    elif transport_info and transport_info.transit_options:
        transit_opt = transport_info.transit_options[0]
        if transit_opt.estimated_cost is not None and transit_opt.estimated_cost > 0:
            transportation = Decimal(str(transit_opt.estimated_cost)) * Decimal(duration)
        else:
            transportation = Decimal("15") * Decimal(duration)
    else:
        transportation = Decimal("15") * Decimal(duration)

    # 4. Activities
    activities = Decimal("0")
    has_explicit_activity_costs = False
    if itinerary and itinerary.days:
        for day in itinerary.days:
            for act in day.activities:
                if act.cost_estimate is not None and act.cost_estimate > 0:
                    activities += Decimal(str(act.cost_estimate))
                    has_explicit_activity_costs = True

    if not has_explicit_activity_costs:
        # Benchmark $25/day for paid sight/museum entries
        activities = Decimal("25") * Decimal(duration)

    # 5. Food & Dining
    style = (user_profile.travel_style or "").lower() if user_profile else ""
    if "luxury" in style:
        daily_food = Decimal("150")
    elif "budget" in style or "backpacker" in style:
        daily_food = Decimal("35")
    else:
        daily_food = Decimal("65")
    food = daily_food * Decimal(duration)

    # Total & Remaining
    total = flights + accommodation + food + transportation + activities
    remaining = None
    status = "flexible"
    if trip_request.budget is not None and trip_request.budget > 0:
        budget_dec = Decimal(str(trip_request.budget))
        remaining = budget_dec - total
        status = "within_budget" if remaining >= 0 else "over_budget"

    tips = _generate_default_cost_tips(
        destination=trip_request.destination,
        status=status,
        remaining=remaining,
    )

    return BudgetInfo(
        flights=flights,
        accommodation=accommodation,
        food=food,
        transportation=transportation,
        activities=activities,
        total=total,
        remaining=remaining,
        status=status,
        currency="USD",
        cost_saving_tips=tips,
    )


def run_budget_agent(
    trip_request: TripRequest,
    transport_info: TransportInfo | None = None,
    hotels: list[HotelRecommendation] | None = None,
    itinerary: Itinerary | None = None,
    user_profile: UserProfile | None = None,
) -> BudgetInfo:
    """
    Execute the Budget Agent:
    1. Compute deterministic base expenses with exact Decimal math.
    2. Invoke the LLM to refine categories, generate contextual cost-saving tips, and assess budget status.
    3. Validate arithmetic integrity and return BudgetInfo.
    """
    base_budget = calculate_base_budget(
        trip_request=trip_request,
        transport_info=transport_info,
        hotels=hotels,
        itinerary=itinerary,
        user_profile=user_profile,
    )

    user_prompt = f"""
Trip Request:
- Destination: {trip_request.destination}
- Duration: {trip_request.duration_days} days
- Stated Budget: ${trip_request.budget if trip_request.budget else 'Flexible / None specified'}
- Travel Style: {user_profile.travel_style if user_profile else 'Balanced'}

Computed Base Expenses:
- Flights/Intercity Transit: ${base_budget.flights}
- Accommodation: ${base_budget.accommodation}
- Daily Food & Dining: ${base_budget.food}
- Local Transportation & Passes: ${base_budget.transportation}
- Sightseeing & Activities: ${base_budget.activities}
- Total Estimated Cost: ${base_budget.total}
- Remaining Budget: ${base_budget.remaining if base_budget.remaining is not None else 'N/A'}
- Initial Status: {base_budget.status}

Please analyze this spending distribution for {trip_request.destination}. Provide 2 to 4 concrete, destination-specific cost-saving recommendations and confirm or refine the final BudgetInfo. Ensure all expense values remain exact and realistic.
"""

    messages = [
        ("system", BUDGET_SYSTEM_PROMPT),
        ("human", user_prompt),
    ]

    try:
        result = budget_agent.invoke(messages)
        if isinstance(result, BudgetInfo):
            # Enforce mathematical consistency with base numbers if LLM deviated wildly
            result.flights = result.flights if result.flights > 0 else base_budget.flights
            result.accommodation = result.accommodation if result.accommodation > 0 else base_budget.accommodation
            result.food = result.food if result.food > 0 else base_budget.food
            result.transportation = result.transportation if result.transportation > 0 else base_budget.transportation
            result.activities = result.activities if result.activities > 0 else base_budget.activities
            result.total = (
                result.flights
                + result.accommodation
                + result.food
                + result.transportation
                + result.activities
            )
            if trip_request.budget is not None and trip_request.budget > 0:
                result.remaining = Decimal(str(trip_request.budget)) - result.total
                result.status = "within_budget" if result.remaining >= 0 else "over_budget"
            else:
                result.remaining = None
                result.status = "flexible"

            if not result.cost_saving_tips:
                result.cost_saving_tips = base_budget.cost_saving_tips

            return result

        return base_budget
    except Exception as e:
        logger.error(f"Error executing Budget Agent: {e}")
        return base_budget


def _estimate_hotel_cost(category: str, nights: int) -> Decimal:
    cat = category.lower()
    if "luxury" in cat or "5-star" in cat:
        return Decimal("300") * Decimal(nights)
    if "budget" in cat or "hostel" in cat or "1-star" in cat or "2-star" in cat:
        return Decimal("50") * Decimal(nights)
    return Decimal("130") * Decimal(nights)


def _generate_default_cost_tips(
    destination: str,
    status: str,
    remaining: Decimal | None,
) -> list[str]:
    tips = [
        f"Consider local transit IC cards or multi-day tourist passes to save on intra-city transit in {destination}.",
        "Opt for lunch specials at sit-down restaurants, which often offer identical menus at 30-50% less than dinner.",
        f"Pre-book major attractions and museums online to avoid surcharge ticketing at entry points in {destination}.",
    ]
    if status == "over_budget" and remaining is not None:
        tips.insert(
            0,
            f"Currently estimated at ${abs(remaining)} over your target budget; consider accommodations 1-2 metro stops outside central districts to reduce lodging costs significantly.",
        )
    return tips
