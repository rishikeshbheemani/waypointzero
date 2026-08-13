from langchain_openrouter import ChatOpenRouter

from app.config.settings import settings
from app.models.supervisor import SupervisorDecision
from app.prompts.supervisor import SUPERVISOR_SYSTEM_PROMPT


def create_supervisor():
    llm = ChatOpenRouter(
        model=settings.MODEL_NAME,
        api_key=settings.OPENROUTER_API_KEY,
        temperature=0,
        max_tokens=1000,
    )

    return llm.with_structured_output(SupervisorDecision)


supervisor = create_supervisor()


def run_supervisor(user_request: str) -> SupervisorDecision:
    """
    Analyze a user's travel request and determine
    which specialized agents should run.
    """

    messages = [
        (
            "system",
            SUPERVISOR_SYSTEM_PROMPT,
        ),
        (
            "human",
            user_request,
        ),
    ]

    return supervisor.invoke(messages)