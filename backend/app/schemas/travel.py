from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class TripRequest(BaseModel):
    destination: str
    duration_days: int
    budget: Decimal | None = None
    start_date: date | None = None

    companions: list[str] = Field(default_factory=list)
    interests: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)