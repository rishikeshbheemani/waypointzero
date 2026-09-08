from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.trip import Base, ChatMessageRecord, TripRecord
from app.schemas.travel import TripRequest


def test_database_trip_and_message_persistence():
    # Use in-memory SQLite for test isolation
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    db = TestingSessionLocal()
    try:
        trip = TripRecord(
            id="test-session-db-1",
            destination="Kyoto",
            duration_days=4,
            budget="2500.00",
            status="completed",
            trip_request_json=TripRequest(destination="Kyoto", duration_days=4).model_dump_json(),
        )
        db.add(trip)
        db.commit()

        # Add chat message
        msg1 = ChatMessageRecord(
            session_id="test-session-db-1",
            role="user",
            content="Can we add a visit to Arashiyama Bamboo Grove?",
        )
        msg2 = ChatMessageRecord(
            session_id="test-session-db-1",
            role="assistant",
            content="Added Arashiyama Bamboo Grove to Day 2 morning.",
        )
        db.add_all([msg1, msg2])
        db.commit()

        # Query and verify
        retrieved_trip = db.query(TripRecord).filter(TripRecord.id == "test-session-db-1").first()
        assert retrieved_trip is not None
        assert retrieved_trip.destination == "Kyoto"
        assert retrieved_trip.duration_days == 4
        assert len(retrieved_trip.messages) == 2
        assert retrieved_trip.messages[0].role == "user"
        assert "Arashiyama" in retrieved_trip.messages[0].content
        assert retrieved_trip.messages[1].role == "assistant"
    finally:
        db.close()