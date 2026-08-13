from app.agents.supervisor import run_supervisor


def test_supervisor_requests_clarification():

    request = "Plan a trip to Japan."

    decision = run_supervisor(request)

    assert decision.needs_clarification is True
    assert decision.clarification_question is not None