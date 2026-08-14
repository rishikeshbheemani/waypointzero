from langchain_openrouter import ChatOpenRouter

from app.config.settings import settings
from app.prompts.research import RESEARCH_SYSTEM_PROMPT
from app.schemas.travel import (
    ResearchResult,
    ResearchSource,
    TripRequest,
)
from app.services.research_pipeline import collect_research_evidence


def create_research_agent():
    llm = ChatOpenRouter(
        model=settings.MODEL_NAME,
        api_key=settings.OPENROUTER_API_KEY,
        temperature=0,
        max_tokens=3000,
    )

    return llm.with_structured_output(ResearchResult)


research_agent = create_research_agent()


def run_research_agent(
    trip_request: TripRequest,
) -> ResearchResult:
    """
    Execute the complete Research Agent.

    1. Retrieve evidence.
    2. Give evidence to the LLM.
    3. Produce structured ResearchResult.
    4. Attach the actual retrieved sources.
    """

    evidence = collect_research_evidence(
        trip_request
    )

    if not evidence:
        return ResearchResult()

    # Build evidence prompt

    evidence_text = []

    for index, item in enumerate(evidence, start=1):

        evidence_text.append(
            f"""
SOURCE {index}

Title:
{item.get("title", "")}

URL:
{item.get("url", "")}

Source type:
{item.get("source_type", "unknown")}

Source role:
{item.get("source_role", "unknown")}

Verification status:
{item.get(
    "verification_status",
    "unverified",
)}

Relevance score:
{item.get("score", 0.0)}

Content:
{item.get("raw_content", "")}
"""
        )

    # Build LLM prompt

    user_prompt = f"""
Destination:
{trip_request.destination}

Trip duration:
{trip_request.duration_days} days

Interests:
{", ".join(trip_request.interests)}

Constraints:
{", ".join(trip_request.constraints)}

Retrieved evidence:

{chr(10).join(evidence_text)}

Using ONLY this evidence, produce a structured ResearchResult.

Research the following where evidence supports them:

- attractions
- hidden gems
- food recommendations
- festivals
- local customs
- travel tips
- safety notes

Do not invent information.
"""

    messages = [
        (
            "system",
            RESEARCH_SYSTEM_PROMPT,
        ),
        (
            "human",
            user_prompt,
        ),
    ]

    # LLM synthesis

    result = research_agent.invoke(
        messages
    )

    # Attach actual sources

    result.sources = [
        ResearchSource(
            title=item.get(
                "title",
                "",
            ),
            url=item.get(
                "url",
                "",
            ),
            source_type=item.get(
                "source_type",
                "unknown",
            ),
            verification_status=item.get(
                "verification_status",
                "unverified",
            ),
        )
        for item in evidence
        if item.get("url")
    ]

    return result