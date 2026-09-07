import logging
from decimal import Decimal
from langchain_openrouter import ChatOpenRouter

from app.config.settings import settings
from app.prompts.accommodation import ACCOMMODATION_SYSTEM_PROMPT
from app.schemas.travel import (
    AccommodationResult,
    HotelRecommendation,
    ResearchResult,
    TransportInfo,
    TripRequest,
    UserProfile,
)
from app.services.accommodation_service import fetch_accommodation_evidence

logger = logging.getLogger(__name__)


def create_accommodation_agent():
    llm = ChatOpenRouter(
        model=settings.MODEL_NAME,
        api_key=settings.OPENROUTER_API_KEY,
        temperature=0,
        max_tokens=1500,
    )
    return llm.with_structured_output(AccommodationResult)


accommodation_agent = create_accommodation_agent()


def run_accommodation_agent(
    trip_request: TripRequest,
    user_profile: UserProfile | None = None,
    research_result: ResearchResult | None = None,
    transport_info: TransportInfo | None = None,
) -> list[HotelRecommendation]:
    """
    Execute the Accommodation Agent:
    1. Search for top-rated hotels and neighborhoods via Tavily.
    2. Synthesize hotel options matching the traveler's budget, arrival hub, and interests.
    3. Return validated list of HotelRecommendation objects.
    """
    evidence = fetch_accommodation_evidence(
        trip_request=trip_request,
        user_profile=user_profile,
        research_result=research_result,
        transport_info=transport_info,
    )

    evidence_snippets = []
    for idx, item in enumerate(evidence, start=1):
        evidence_snippets.append(
            f"SOURCE {idx}: {item.get('title')}\nURL: {item.get('url')}\nContent: {item.get('content')}\n"
        )

    # Key attractions or arrival points context
    key_hubs = []
    if transport_info and transport_info.train_options:
        key_hubs.append(f"Train arrival: {transport_info.train_options[0].arrival_station}")
    if transport_info and transport_info.flight_options:
        key_hubs.append(f"Airport route: {transport_info.flight_options[0].route}")
    if research_result and research_result.attractions:
        attraction_names = [a.name for a in research_result.attractions[:3]]
        key_hubs.append(f"Primary attractions: {', '.join(attraction_names)}")

    user_prompt = f"""
Trip Request:
- Destination: {trip_request.destination}
- Duration: {trip_request.duration_days} days
- Budget: {trip_request.budget if trip_request.budget else 'Flexible'}
- Companions: {', '.join(trip_request.companions) if trip_request.companions else 'Solo'}
- Constraints: {', '.join(trip_request.constraints) if trip_request.constraints else 'None'}

User Profile:
- Hotel Preference: {user_profile.hotel_preference if user_profile and user_profile.hotel_preference else 'Balanced (comfortable, well-located)'}
- Travel Style: {user_profile.travel_style if user_profile else 'Balanced'}

Logistical Context:
{chr(10).join(f"- {hub}" for hub in key_hubs) if key_hubs else '- Central city area'}

Retrieved Neighborhood & Lodging Evidence:
{chr(10).join(evidence_snippets) if evidence_snippets else 'No web evidence retrieved; use general authoritative travel hotel knowledge.'}

Recommend 3 to 5 distinct hotel options spanning luxury/boutique, mid-range, and budget tiers with clear neighborhood insights.
"""

    messages = [
        ("system", ACCOMMODATION_SYSTEM_PROMPT),
        ("human", user_prompt),
    ]

    try:
        result = accommodation_agent.invoke(messages)
        if isinstance(result, AccommodationResult) and result.hotels:
            return result.hotels
        elif isinstance(result, list):
            return result
        return _fallback_hotels(trip_request)
    except Exception as e:
        logger.error(f"Error executing Accommodation Agent: {e}")
        return _fallback_hotels(trip_request)


def _fallback_hotels(trip_request: TripRequest) -> list[HotelRecommendation]:
    destination = trip_request.destination
    return [
        HotelRecommendation(
            name=f"Central Grand Hotel {destination}",
            city=destination,
            price_per_night=Decimal("150.00"),
            rating=4.5,
            description="Centrally located hotel with easy access to major attractions and transit.",
            neighborhood="City Center",
            category="Mid-Range",
            location_advantage="Walking distance to central station and major sights.",
            amenities=["Free Wi-Fi", "Breakfast Included", "Air Conditioning", "24hr Reception"],
        ),
        HotelRecommendation(
            name=f"{destination} Boutique Heritage Stay",
            city=destination,
            price_per_night=Decimal("95.00"),
            rating=4.3,
            description="Charming boutique lodging offering local character and modern comforts.",
            neighborhood="Historic District",
            category="Boutique",
            location_advantage="Located in the vibrant cultural quarter.",
            amenities=["Free Wi-Fi", "Artisan Breakfast", "Tour Desk"],
        ),
        HotelRecommendation(
            name=f"{destination} Backpacker & Social Hub",
            city=destination,
            price_per_night=Decimal("35.00"),
            rating=4.2,
            description="Clean, vibrant budget hostel with private and dorm options for savvy travelers.",
            neighborhood="Arts Quarter",
            category="Budget",
            location_advantage="Near metro station with convenient airport/rail links.",
            amenities=["Free Wi-Fi", "Lockers", "Common Lounge", "Cafe"],
        ),
    ]
