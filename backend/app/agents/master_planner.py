import logging
from decimal import Decimal
from langchain_openrouter import ChatOpenRouter

from app.config.settings import settings
from app.prompts.master_planner import (
    MASTER_PLANNER_REFINEMENT_PROMPT,
    MASTER_PLANNER_SYSTEM_PROMPT,
)
from app.schemas.travel import (
    DailyActivity,
    DailyPlan,
    HotelRecommendation,
    Itinerary,
    ResearchResult,
    TransportInfo,
    TripRequest,
    UserProfile,
    WeatherInfo,
)

logger = logging.getLogger(__name__)


def create_master_planner_agent():
    llm = ChatOpenRouter(
        model=settings.MODEL_NAME,
        api_key=settings.OPENROUTER_API_KEY,
        temperature=0.2,
        max_tokens=1200,
    )
    return llm.with_structured_output(Itinerary)


master_planner_agent = create_master_planner_agent()


def run_master_planner(
    trip_request: TripRequest,
    user_profile: UserProfile | None = None,
    research_result: ResearchResult | None = None,
    weather_info: WeatherInfo | None = None,
    transport_info: TransportInfo | None = None,
    hotels: list[HotelRecommendation] | None = None,
    current_itinerary: Itinerary | None = None,
    user_feedback: str | None = None,
) -> Itinerary:
    """
    Execute the Master Planner Agent:
    1. Ingest all intelligence: Research (attractions, foods), Weather, Transport, and Hotels.
    2. If an existing itinerary and user feedback are present, perform surgical multi-turn refinement.
    3. Otherwise, synthesize a fresh day-by-day Itinerary from scratch.
    4. Fall back safely if LLM execution fails.
    """

    # 1. Transport context
    transport_lines = []
    if transport_info:
        if transport_info.flight_options:
            flight = transport_info.flight_options[0]
            transport_lines.append(f"Inbound/Outbound Flight: {flight.airline} ({flight.route})")
        if transport_info.train_options:
            train = transport_info.train_options[0]
            transport_lines.append(f"Arrival Train: {train.train_name_or_number} at {train.arrival_station}")
        if transport_info.transit_options:
            modes = ", ".join(t.mode for t in transport_info.transit_options[:3])
            transport_lines.append(f"Local Transit: {modes}")
        if transport_info.pass_options:
            passes = ", ".join(p.name for p in transport_info.pass_options[:2])
            transport_lines.append(f"Transit Passes: {passes}")
        elif transport_info.travel_passes:
            passes = ", ".join(transport_info.travel_passes[:2])
            transport_lines.append(f"Transit Passes: {passes}")

    # 2. Hotel context
    hotel_lines = []
    if hotels:
        selected_hotel = hotels[0]
        hotel_lines.append(
            f"Primary Lodging: {selected_hotel.name} in {selected_hotel.neighborhood or 'City Center'} "
            f"({selected_hotel.location_advantage or selected_hotel.category or 'Convenient'})"
        )
        if len(hotels) > 1:
            alt_neighborhoods = {h.neighborhood for h in hotels[1:] if h.neighborhood}
            if alt_neighborhoods:
                hotel_lines.append(f"Key Neighborhoods: {', '.join(alt_neighborhoods)}")

    # 3. Weather context
    weather_lines = []
    if weather_info and weather_info.forecast:
        for idx, f in enumerate(weather_info.forecast[: trip_request.duration_days], start=1):
            desc = f.weather_description or "Fair"
            max_t = f"{f.temperature_max_celsius}°C" if f.temperature_max_celsius is not None else "N/A"
            min_t = f"{f.temperature_min_celsius}°C" if f.temperature_min_celsius is not None else "N/A"
            rain = f"{f.precipitation_probability}%" if f.precipitation_probability is not None else "0%"
            weather_lines.append(
                f"Day {idx} ({f.date}): {desc}, High {max_t} / Low {min_t}, Precipitation {rain}"
            )
        if weather_info.travel_impact:
            weather_lines.append(f"Impact: {', '.join(weather_info.travel_impact)}")
    elif weather_info and weather_info.seasonal_context:
        weather_lines.append(f"Seasonal: {', '.join(weather_info.seasonal_context)}")

    # 4. Research (attractions, hidden gems, food spots)
    attraction_lines = []
    if research_result:
        for a in research_result.attractions[:8]:
            attraction_lines.append(f"- {a.name} ({a.category}): {a.description} [Best time: {a.best_visit_time}]")
        for g in research_result.hidden_gems[:4]:
            attraction_lines.append(f"- [Hidden Gem] {g.name}: {g.description}")

    food_lines = []
    if research_result and research_result.foods:
        for f in research_result.foods[:6]:
            veg = " (Vegetarian available)" if f.vegetarian_available else ""
            food_lines.append(f"- {f.name} ({f.cuisine} {f.meal_type}): {f.description}{veg}")

    # Build prompt
    user_prompt = f"""
Trip Request:
- Destination: {trip_request.destination}
- Duration: {trip_request.duration_days} days
- Budget: {trip_request.budget if trip_request.budget else 'Flexible'}
- Companions: {', '.join(trip_request.companions) if trip_request.companions else 'Solo'}
- Interests: {', '.join(trip_request.interests) if trip_request.interests else 'General exploration'}
- Constraints: {', '.join(trip_request.constraints) if trip_request.constraints else 'None'}

User Profile:
- Travel Style: {user_profile.travel_style if user_profile and user_profile.travel_style else 'Balanced'}
- Walking Tolerance: {user_profile.walking_tolerance if user_profile and user_profile.walking_tolerance else 'Moderate'}
- Food Preferences: {', '.join(user_profile.food_preferences) if user_profile and user_profile.food_preferences else 'Open to local specialties'}

Transport Logistics:
{chr(10).join(f"- {l}" for l in transport_lines) if transport_lines else '- Standard local city transport (metro, taxi)'}

Accommodation Context:
{chr(10).join(f"- {l}" for l in hotel_lines) if hotel_lines else f'- Centrally located accommodation in {trip_request.destination}'}

Weather Intelligence:
{chr(10).join(f"- {l}" for l in weather_lines) if weather_lines else '- Pleasant travel weather; plan outdoor & indoor activities evenly.'}

Curated Attractions & Experiences:
{chr(10).join(attraction_lines) if attraction_lines else f'- Major iconic sights and cultural centers of {trip_request.destination}'}

Curated Dining & Food Recommendations:
{chr(10).join(food_lines) if food_lines else f'- Local regional specialties and central markets of {trip_request.destination}'}

Synthesize all the above inputs into an authentic, seamless day-by-day Itinerary for all {trip_request.duration_days} days.
"""

    # Multi-turn Refinement Branch
    if current_itinerary and current_itinerary.days and user_feedback:
        refinement_prompt = f"""
Existing Itinerary to Revise:
{current_itinerary.model_dump_json()}

User's Modification Request:
"{user_feedback}"

Hotel & Neighborhood Context:
{chr(10).join(f"- {l}" for l in hotel_lines) if hotel_lines else f'- Centrally located in {trip_request.destination}'}

Available Alternative Research & Food Options:
{chr(10).join(attraction_lines[:5]) if attraction_lines else '- General top city attractions'}
{chr(10).join(food_lines[:5]) if food_lines else '- General authentic regional food'}

Apply the user's modification request surgically. Keep all non-targeted days and activities exactly as they are. Return the complete revised Itinerary.
"""
        messages = [
            ("system", MASTER_PLANNER_REFINEMENT_PROMPT),
            ("human", refinement_prompt),
        ]
        try:
            result = master_planner_agent.invoke(messages)
            if isinstance(result, Itinerary) and result.days and any(len(d.activities) > 0 for d in result.days):
                return result
            return _fallback_refinement(current_itinerary, user_feedback)
        except Exception as e:
            logger.error(f"Error refining Itinerary: {e}")
            return _fallback_refinement(current_itinerary, user_feedback)

    # Initial Synthesis Branch
    messages = [
        ("system", MASTER_PLANNER_SYSTEM_PROMPT),
        ("human", user_prompt),
    ]

    try:
        result = master_planner_agent.invoke(messages)
        if isinstance(result, Itinerary) and result.days and any(len(d.activities) > 0 for d in result.days):
            return result
        return _fallback_itinerary(trip_request, research_result, hotels)
    except Exception as e:
        logger.error(f"Error executing Master Planner Agent: {e}")
        return _fallback_itinerary(trip_request, research_result, hotels)


def _fallback_refinement(current_itinerary: Itinerary, user_feedback: str) -> Itinerary:
    updated = current_itinerary.model_copy(deep=True)
    suffix = f" [Updated: {user_feedback}]"
    if updated.summary:
        updated.summary += suffix
    else:
        updated.summary = suffix.strip()
    return updated


def _fallback_itinerary(
    trip_request: TripRequest,
    research_result: ResearchResult | None = None,
    hotels: list[HotelRecommendation] | None = None,
) -> Itinerary:
    destination = trip_request.destination
    days_count = max(1, trip_request.duration_days)
    hotel_name = hotels[0].name if hotels else f"Central {destination} Hotel"
    neighborhood = hotels[0].neighborhood if hotels and hotels[0].neighborhood else "City Center"

    attractions = list(research_result.attractions) if research_result and research_result.attractions else []
    hidden_gems = list(research_result.hidden_gems) if research_result and research_result.hidden_gems else []
    foods = list(research_result.foods) if research_result and research_result.foods else []

    all_sights = attractions + hidden_gems

    daily_plans = []

    for day_num in range(1, days_count + 1):
        activities = []

        if day_num == 1:
            theme = f"Arrival & {neighborhood} Orientation"
            summary = f"Arrive in {destination}, settle into {hotel_name}, and explore the local neighborhood."
            activities.append(
                DailyActivity(
                    time="11:00 AM - 01:00 PM",
                    title=f"Arrival & Transit to {neighborhood}",
                    location=f"{destination} Transit Terminal",
                    description=f"Arrive in {destination} and take local transport to {hotel_name} in {neighborhood}.",
                    activity_type="transit",
                )
            )
            activities.append(
                DailyActivity(
                    time="01:30 PM - 03:00 PM",
                    title="Hotel Check-in & Neighborhood Lunch",
                    location=neighborhood,
                    description=f"Check into {hotel_name}, unpack, and enjoy lunch at a local cafe in {neighborhood}.",
                    activity_type="food",
                )
            )
            sight_title = all_sights[0].name if all_sights else f"{destination} Central Promenade"
            sight_desc = all_sights[0].description if all_sights else f"Scenic introductory walk in {neighborhood}."
            activities.append(
                DailyActivity(
                    time="04:00 PM - 06:30 PM",
                    title=f"Introductory Visit: {sight_title}",
                    location=sight_title,
                    description=sight_desc,
                    activity_type="sightseeing",
                )
            )
            food_title = foods[0].name if foods else "Traditional Welcome Dinner"
            activities.append(
                DailyActivity(
                    time="07:30 PM - 09:30 PM",
                    title=f"Welcome Dinner: {food_title}",
                    location=neighborhood,
                    description=f"Enjoy dinner featuring {destination} specialties in {neighborhood}.",
                    activity_type="food",
                )
            )

        elif day_num == days_count:
            theme = f"Final Sightseeing & Departure from {destination}"
            summary = f"Wrap up your journey in {destination} with a relaxed morning before heading to the departure hub."
            activities.append(
                DailyActivity(
                    time="09:00 AM - 10:30 AM",
                    title="Breakfast & Local Artisanal Market",
                    location=neighborhood,
                    description=f"Morning breakfast and souvenir shopping near {hotel_name}.",
                    activity_type="food",
                )
            )
            sight_idx = (day_num - 1) % len(all_sights) if all_sights else 0
            sight_title = all_sights[sight_idx].name if all_sights else f"{destination} Heritage Quarter"
            activities.append(
                DailyActivity(
                    time="11:00 AM - 01:00 PM",
                    title=f"Farewell Visit: {sight_title}",
                    location=sight_title,
                    description=f"Final exploration of {sight_title} before hotel checkout.",
                    activity_type="sightseeing",
                )
            )
            activities.append(
                DailyActivity(
                    time="01:30 PM - 03:30 PM",
                    title=f"Hotel Checkout & Transit to Airport/Station",
                    location=f"{destination} Transit Terminal",
                    description=f"Check out from {hotel_name} and transit to the departure terminal for onward journey.",
                    activity_type="transit",
                )
            )

        else:
            theme = f"Cultural Highlights & Exploration - Day {day_num}"
            summary = f"Full day exploring key attractions, cultural landmarks, and authentic culinary stops."
            morning_sight = all_sights[(day_num * 2 - 2) % len(all_sights)] if all_sights else f"{destination} Historic Landmark"
            activities.append(
                DailyActivity(
                    time="09:30 AM - 12:00 PM",
                    title=f"Morning Exploration: {morning_sight.name if hasattr(morning_sight, 'name') else morning_sight}",
                    location=morning_sight.name if hasattr(morning_sight, "name") else str(morning_sight),
                    description=morning_sight.description if hasattr(morning_sight, "description") else f"Guided tour of {morning_sight}.",
                    activity_type="sightseeing",
                )
            )
            food_idx = (day_num - 1) % len(foods) if foods else 0
            lunch_spot = foods[food_idx].name if foods else "Local Specialties Lunch"
            activities.append(
                DailyActivity(
                    time="12:30 PM - 02:00 PM",
                    title=f"Lunch: {lunch_spot}",
                    location=neighborhood,
                    description=f"Savor regional dishes at {lunch_spot}.",
                    activity_type="food",
                )
            )
            afternoon_sight = all_sights[(day_num * 2 - 1) % len(all_sights)] if all_sights else f"{destination} Cultural Museum"
            activities.append(
                DailyActivity(
                    time="02:30 PM - 05:00 PM",
                    title=f"Afternoon Discovery: {afternoon_sight.name if hasattr(afternoon_sight, 'name') else afternoon_sight}",
                    location=afternoon_sight.name if hasattr(afternoon_sight, "name") else str(afternoon_sight),
                    description=afternoon_sight.description if hasattr(afternoon_sight, "description") else f"Experience {afternoon_sight}.",
                    activity_type="culture",
                )
            )
            activities.append(
                DailyActivity(
                    time="07:30 PM - 09:30 PM",
                    title=f"Dinner & Evening Stroll in {destination}",
                    location=neighborhood,
                    description=f"Relaxing dinner and evening atmosphere in {destination}.",
                    activity_type="food",
                )
            )

        daily_plans.append(
            DailyPlan(
                day=day_num,
                theme=theme,
                day_summary=summary,
                activities=activities,
            )
        )

    return Itinerary(
        trip_title=f"{days_count}-Day Journey to {destination}",
        summary=f"A curated {days_count}-day itinerary for {destination} balancing cultural highlights, authentic dining, and effortless pacing.",
        days=daily_plans,
    )
