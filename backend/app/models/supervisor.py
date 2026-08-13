from pydantic import BaseModel, Field


class SupervisorDecision(BaseModel):
    """Decision produced by the Supervisor Agent."""

    needs_clarification: bool = False
    clarification_question: str | None = None

    invoke_preference: bool = True
    invoke_research: bool = False
    invoke_weather: bool = False
    invoke_transport: bool = False
    invoke_accommodation: bool = False
    invoke_activities: bool = False
    invoke_budget: bool = False

    reasoning: str = Field(default="")