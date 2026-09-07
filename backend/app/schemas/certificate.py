from datetime import date, datetime, time
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    description: str
    image_url: str | None


class CertificateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    short_name: str | None
    level: str | None
    issuer: str
    exam_type: str
    exam_cycle: str
    difficulty: int
    recommended_days: int
    recommended_daily_minutes: int
    description: str
    eligibility_summary: str | None
    subjects: list[str]
    tags: list[str]
    official_url: str | None
    image_url: str | None
    is_featured: bool
    category: CategoryRead


class CertificatePage(BaseModel):
    items: list[CertificateRead]
    total: int
    page: int
    page_size: int


class PlanGenerateRequest(BaseModel):
    certificate_id: int
    ai_provider: Literal["deepseek", "qwen"] = "deepseek"
    target_exam_date: date
    study_start_date: date
    weekday_minutes: int = Field(ge=30, le=360)
    weekend_minutes: int = Field(ge=30, le=480)
    current_level: Literal["beginner", "basic", "intermediate", "advanced"]
    weak_subjects: list[str] = Field(default_factory=list, max_length=20)
    preferred_period: Literal["morning", "afternoon", "evening"] = "evening"
    session_minutes: int = Field(default=40, ge=20, le=90)
    break_minutes: int = Field(default=10, ge=5, le=30)
    available_weekdays: list[int] = Field(default_factory=lambda: [1, 2, 3, 4, 5, 6, 7])

    @model_validator(mode="after")
    def validate_schedule(self):
        if self.target_exam_date <= self.study_start_date:
            raise ValueError("考试日期必须晚于开始复习日期")
        if (self.target_exam_date - self.study_start_date).days > 730:
            raise ValueError("单次计划跨度不能超过两年")
        weekdays = set(self.available_weekdays)
        if not weekdays or not weekdays.issubset(set(range(1, 8))):
            raise ValueError("每周学习日必须在 1 到 7 之间")
        return self


class StudyTaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    task_type: str
    title: str
    description: str | None
    subject: str | None
    scheduled_start: time
    scheduled_end: time
    duration_minutes: int
    is_break: bool
    status: str


class StudyDayRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    study_date: date
    day_number: int
    phase: str
    focus: str
    study_minutes: int
    break_minutes: int
    status: str
    tasks: list[StudyTaskRead]


class StudyPhaseOutline(BaseModel):
    phase: str
    start_date: date
    end_date: date
    study_days: int
    study_minutes: int
    break_minutes: int
    subjects: list[str]


class StudyPlanRead(BaseModel):
    id: int
    name: str
    certificate_id: int
    certificate_name: str
    start_date: date
    end_date: date
    total_days: int
    total_study_minutes: int
    generation_mode: str
    status: str
    outline: list[StudyPhaseOutline]
    days: list[StudyDayRead]


class StudyPlanListItem(BaseModel):
    id: int
    name: str
    certificate_id: int
    certificate_name: str
    certificate_image_url: str | None
    start_date: date
    end_date: date
    total_days: int
    total_study_minutes: int
    generation_mode: str
    status: str
    progress_percent: int
    today: StudyDayRead | None


class StudyTaskStatusUpdate(BaseModel):
    completed: bool


class StudyCalendarDayRead(BaseModel):
    study_date: date
    total_tasks: int
    completed_tasks: int
    is_completed: bool


class DailySummaryWrite(BaseModel):
    content: str = Field(max_length=50000)
    content_format: Literal["markdown", "word"] = "markdown"


class DailySummaryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    summary_date: date
    content: str
    content_format: Literal["markdown", "word"]
    updated_at: datetime
