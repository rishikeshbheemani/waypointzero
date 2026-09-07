import logging
from langchain_openrouter import ChatOpenRouter

from app.config.settings import settings
from app.prompts.transport import TRANSPORT_SYSTEM_PROMPT
from app.schemas.travel import (
    TransportInfo,
    TripRequest,
    UserProfile,
)
from app.services.transport_service import fetch_transport_evidence

logger = logging.getLogger(__name__)


def create_transport_agent():
    llm = ChatOpenRouter(
        model=settings.MODEL_NAME,
        api_key=settings.OPENROUTER_API_KEY,
        temperature=0,
        max_tokens=1500,
    )
    return llm.with_structured_output(TransportInfo)


transport_agent = create_transport_agent()


def run_transport_agent(
    trip_request: TripRequest,
    user_profile: UserProfile | None = None,
) -> TransportInfo:
    """
    Execute the Transport Agent:
    1. Retrieve real-world transit & flight evidence.
    2. Synthesize options via LLM with structured TransportInfo schema.
    3. Return validated TransportInfo.
    """
    evidence = fetch_transport_evidence(trip_request, user_profile)

    evidence_snippets = []
    for idx, item in enumerate(evidence, start=1):
        evidence_snippets.append(
            f"SOURCE {idx}: {item.get('title')}\nURL: {item.get('url')}\nContent: {item.get('content')}\n"
        )

    user_prompt = f"""
Trip Request:
- Destination: {trip_request.destination}
- Origin: {trip_request.origin or 'Not specified (assume major international airport)'}
- Duration: {trip_request.duration_days} days
- Budget: {trip_request.budget if trip_request.budget else 'Flexible'}
- Constraints: {', '.join(trip_request.constraints) if trip_request.constraints else 'None'}

User Profile:
- Preferred Airlines: {', '.join(user_profile.preferred_airlines) if user_profile and user_profile.preferred_airlines else 'None'}
- Travel Style: {user_profile.travel_style if user_profile else 'Not specified'}

Retrieved Transit Evidence:
{chr(10).join(evidence_snippets) if evidence_snippets else 'No specific web evidence retrieved; use general reliable travel transit knowledge.'}

Produce a complete, structured TransportInfo recommendation. Ensure legacy string lists (recommended_flights, local_transport, travel_passes) are populated alongside the structured options.
"""

    messages = [
        ("system", TRANSPORT_SYSTEM_PROMPT),
        ("human", user_prompt),
    ]

    try:
        result = transport_agent.invoke(messages)
        if isinstance(result, TransportInfo):
            return result
        return TransportInfo()
    except Exception as e:
        logger.error(f"Error executing Transport Agent: {e}")
        return TransportInfo(
            recommended_flights=[f"Standard international flights to {trip_request.destination}"],
            local_transport=["Local metro, buses, and licensed taxis"],
            travel_passes=["City transit travel pass or rechargeable IC card"],
            tips=["Verify transit passes at airport arrival stations."],
        )
