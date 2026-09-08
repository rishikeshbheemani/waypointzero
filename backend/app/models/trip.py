from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class TripRecord(Base):
    """SQLAlchemy model for persisting planned trips across server restarts."""

    __tablename__ = "trips"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, index=True)  # session_id
    destination: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    duration_days: Mapped[int] = mapped_column(Integer, nullable=False)
    budget: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="completed")  # "completed", "needs_clarification"
    clarification_question: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Serialized JSON blobs for state components
    trip_request_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    itinerary_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    budget_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    hotels_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    transport_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    weather_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    research_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationship to conversation history
    messages: Mapped[List["ChatMessageRecord"]] = relationship(
        "ChatMessageRecord",
        back_populates="trip",
        cascade="all, delete-orphan",
    )


class ChatMessageRecord(Base):
    """SQLAlchemy model for persisting conversational refinement messages."""

    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("trips.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[str] = mapped_column(String(16), nullable=False)  # "user" or "assistant"
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    trip: Mapped["TripRecord"] = relationship("TripRecord", back_populates="messages")
