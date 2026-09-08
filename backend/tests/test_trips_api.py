from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.supervisor import SupervisorDecision
from app.schemas.travel import (
    BudgetInfo,
    DailyActivity,
    DailyPlan,
    HotelRecommendation,
    Itinerary,
    TripRequest,
)

client = TestClient(app)


@pytest.fixture
def sample_itinerary():
    return Itinerary(
        trip_title="Tokyo 3-Day Explorer",
        summary="A cultural trip to Tokyo.",
        days=[
            DailyPlan(
                day=1,
                theme="Arrival & Shinjuku",
                activities=[
                    DailyActivity(
                        time="03:00 PM",
                        title="Hotel Check-in",
                        location="Shinjuku",
                        description="Check into Gracery Shinjuku",
                    )
                ],
            )
        ],
    )


@pytest.fixture
def sample_budget():
    return BudgetInfo(
        flights=Decimal("800.00"),
        accommodation=Decimal("450.00"),
        food=Decimal("200.00"),
        transportation=Decimal("50.00"),
        activities=Decimal("75.00"),
        total=Decimal("1575.00"),
        remaining=Decimal("425.00"),
        status="within_budget",
        currency="USD",
        cost_saving_tips=["Buy Tokyo Subway 72hr pass"],
    )


def test_plan_trip_endpoint_success(sample_itinerary, sample_budget):
    payload = {
        "trip_request": {
            "destination": "Tokyo",
            "duration_days": 3,
            "budget": 2000.0,
            "interests": ["culture", "food"],
        },
        "user_profile": {
            "travel_style": "Comfortable",
        },
        "session_id": "test-plan-session-123",
    }

    mock_graph_result = {
        "supervisor_decision": SupervisorDecision(needs_clarification=False),
        "itinerary": sample_itinerary,
        "budget": sample_budget,
        "hotels": [
            HotelRecommendation(
                name="Hotel Gracery Shinjuku",
                city="Tokyo",
                price_per_night=Decimal("150.00"),
                rating=4.4,
                description="Mid-range hotel",
            )
        ],
        "transport": None,
        "weather": None,
        "research": None,
    }

    with patch("app.api.trips.graph.invoke", return_value=mock_graph_result):
        response = client.post("/api/trips/plan", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "test-plan-session-123"
        assert data["status"] == "completed"
        assert data["itinerary"]["trip_title"] == "Tokyo 3-Day Explorer"
        assert data["budget"]["status"] == "within_budget"
        assert len(data["hotels"]) == 1
        assert data["hotels"][0]["name"] == "Hotel Gracery Shinjuku"


def test_plan_trip_clarification_endpoint():
    payload = {
        "trip_request": {
            "destination": "Europe",
            "duration_days": 5,
        },
        "session_id": "test-clarification-session",
    }

    mock_graph_result = {
        "supervisor_decision": SupervisorDecision(
            needs_clarification=True,
            clarification_question="Which countries or cities in Europe would you like to visit?",
        ),
        "itinerary": None,
        "budget": None,
    }

    with patch("app.api.trips.graph.invoke", return_value=mock_graph_result):
        response = client.post("/api/trips/plan", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "needs_clarification"
        assert "Which countries or cities" in data["clarification_question"]


def test_chat_refinement_endpoint_success(sample_itinerary, sample_budget):
    refined_itinerary = sample_itinerary.model_copy(deep=True)
    refined_itinerary.trip_title = "Tokyo 3-Day Explorer (Refined)"

    mock_checkpoint = MagicMock()
    mock_checkpoint.values = {
        "trip_request": TripRequest(destination="Tokyo", duration_days=3),
        "itinerary": sample_itinerary,
        "budget": sample_budget,
    }

    mock_graph_result = {
        "itinerary": refined_itinerary,
        "budget": sample_budget,
        "hotels": [],
    }

    with (
        patch("app.api.trips.graph.get_state", return_value=mock_checkpoint),
        patch("app.api.trips.graph.invoke", return_value=mock_graph_result),
    ):
        response = client.post(
            "/api/trips/chat",
            json={
                "session_id": "existing-session-456",
                "message": "Add a ramen tour on Day 1 evening",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "existing-session-456"
        assert data["itinerary"]["trip_title"] == "Tokyo 3-Day Explorer (Refined)"


def test_chat_refinement_session_not_found():
    with patch("app.api.trips.graph.get_state", return_value=None):
        response = client.post(
            "/api/trips/chat",
            json={
                "session_id": "nonexistent-session",
                "message": "Update my trip",
            },
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


def test_get_trip_state_endpoint(sample_itinerary, sample_budget):
    mock_checkpoint = MagicMock()
    mock_checkpoint.values = {
        "trip_request": TripRequest(destination="Tokyo", duration_days=3),
        "itinerary": sample_itinerary,
        "budget": sample_budget,
        "hotels": [],
        "transport": None,
        "weather": None,
        "research": None,
    }

    with patch("app.api.trips.graph.get_state", return_value=mock_checkpoint):
        response = client.get("/api/trips/session-789")
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "session-789"
        assert data["destination"] == "Tokyo"
        assert data["duration_days"] == 3
        assert data["has_itinerary"] is True
        assert data["itinerary"]["trip_title"] == "Tokyo 3-Day Explorer"

    # Test 404 when session does not exist
    with patch("app.api.trips.graph.get_state", return_value=None):
        response = client.get("/api/trips/unknown-session")
        assert response.status_code == 404


def test_plan_trip_stream_endpoint():
    payload = {
        "trip_request": {
            "destination": "Kyoto",
            "duration_days": 2,
        },
        "session_id": "stream-session-999",
    }

    mock_stream_steps = [
        {"supervisor": {"supervisor_decision": {"needs_clarification": False}}},
        {"research": {"attractions": []}},
        {"master_planner": {"itinerary": {"trip_title": "Kyoto Trip"}}},
    ]

    with patch("app.api.trips.graph.stream", return_value=iter(mock_stream_steps)):
        response = client.post("/api/trips/plan/stream", json=payload)
        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]

        content = response.text
        assert "agent_start" in content
        assert "pipeline_complete" in content
        assert "supervisor" in content
        assert "master_planner" in content
