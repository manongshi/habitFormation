from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ExamGoalCreate(BaseModel):
    exam_name: str = Field(min_length=2, max_length=120)
    exam_date: date
    target_score: Decimal = Field(gt=0, le=1000)
    daily_minutes: int = Field(ge=10, le=720)
    current_level: str | None = Field(default=None, max_length=100)


class ExamGoalRead(ExamGoalCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    created_at: datetime
    updated_at: datetime


class DashboardOverview(BaseModel):
    active_goal: ExamGoalRead | None
    days_remaining: int | None
    mastery_rate: int
    pending_reviews: int
    completed_today: int

