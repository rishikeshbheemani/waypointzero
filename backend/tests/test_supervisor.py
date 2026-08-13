from app.agents.supervisor import run_supervisor
from app.models.supervisor import SupervisorDecision


def test_supervisor():

    request = """
    Plan a 10-day solo trip to Japan in October.

    My budget is ₹2,00,000.
    I enjoy hiking, photography, Japanese food, and anime.
    I want to avoid crowded tourist places.
    """

    decision = run_supervisor(request)

    assert isinstance(decision, SupervisorDecision)

    assert decision.invoke_preference is True
    assert decision.invoke_research is True
    assert decision.invoke_weather is True
    assert decision.invoke_transport is True
    assert decision.invoke_accommodation is True
    assert decision.invoke_activities is True
    assert decision.invoke_budget is True