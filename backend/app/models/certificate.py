from datetime import date, time

from sqlalchemy import Boolean, Date, ForeignKey, Integer, JSON, String, Text, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.mixins import AuditMixin


class CertificateCategory(AuditMixin, Base):
    __tablename__ = "certificate_categories"

    code: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(80))
    description: Mapped[str] = mapped_column(String(255))
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default="active", index=True)

    certificates: Mapped[list["Certificate"]] = relationship(back_populates="category")


class Certificate(AuditMixin, Base):
    __tablename__ = "certificates"

    category_id: Mapped[int] = mapped_column(
        ForeignKey("certificate_categories.id"),
        index=True,
    )
    code: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(160), index=True)
    short_name: Mapped[str | None] = mapped_column(String(80), nullable=True)
    level: Mapped[str | None] = mapped_column(String(40), nullable=True)
    issuer: Mapped[str] = mapped_column(String(200))
    exam_type: Mapped[str] = mapped_column(String(40), default="水平评价类")
    exam_cycle: Mapped[str] = mapped_column(String(100), default="以官方公告为准")
    difficulty: Mapped[int] = mapped_column(Integer, default=3)
    recommended_days: Mapped[int] = mapped_column(Integer, default=90)
    recommended_daily_minutes: Mapped[int] = mapped_column(Integer, default=90)
    description: Mapped[str] = mapped_column(Text)
    eligibility_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    subjects: Mapped[list[str]] = mapped_column(JSON, default=list)
    tags: Mapped[list[str]] = mapped_column(JSON, default=list)
    official_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default="active", index=True)

    category: Mapped[CertificateCategory] = relationship(back_populates="certificates")


class ExamPreparationProfile(AuditMixin, Base):
    __tablename__ = "exam_preparation_profiles"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    certificate_id: Mapped[int] = mapped_column(ForeignKey("certificates.id"), index=True)
    target_exam_date: Mapped[date] = mapped_column(Date)
    study_start_date: Mapped[date] = mapped_column(Date)
    weekday_minutes: Mapped[int] = mapped_column(Integer)
    weekend_minutes: Mapped[int] = mapped_column(Integer)
    current_level: Mapped[str] = mapped_column(String(30))
    weak_subjects: Mapped[list[str]] = mapped_column(JSON, default=list)
    preferred_period: Mapped[str] = mapped_column(String(20), default="evening")
    session_minutes: Mapped[int] = mapped_column(Integer, default=40)
    break_minutes: Mapped[int] = mapped_column(Integer, default=10)
    available_weekdays: Mapped[list[int]] = mapped_column(JSON, default=lambda: [1, 2, 3, 4, 5, 6, 7])
    status: Mapped[str] = mapped_column(String(20), default="active", index=True)


class StudyPlan(AuditMixin, Base):
    __tablename__ = "study_plans"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("exam_preparation_profiles.id"), index=True)
    certificate_id: Mapped[int] = mapped_column(ForeignKey("certificates.id"), index=True)
    name: Mapped[str] = mapped_column(String(160))
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    total_days: Mapped[int] = mapped_column(Integer)
    total_study_minutes: Mapped[int] = mapped_column(Integer)
    generation_mode: Mapped[str] = mapped_column(String(20), default="rules")
    status: Mapped[str] = mapped_column(String(20), default="active", index=True)

    days: Mapped[list["StudyPlanDay"]] = relationship(
        back_populates="plan",
        cascade="all, delete-orphan",
        order_by="StudyPlanDay.day_number",
    )


class StudyPlanDay(AuditMixin, Base):
    __tablename__ = "study_plan_days"

    plan_id: Mapped[int] = mapped_column(ForeignKey("study_plans.id"), index=True)
    study_date: Mapped[date] = mapped_column(Date, index=True)
    day_number: Mapped[int] = mapped_column(Integer)
    phase: Mapped[str] = mapped_column(String(30))
    focus: Mapped[str] = mapped_column(String(200))
    study_minutes: Mapped[int] = mapped_column(Integer)
    break_minutes: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)

    plan: Mapped[StudyPlan] = relationship(back_populates="days")
    tasks: Mapped[list["StudyTask"]] = relationship(
        back_populates="day",
        cascade="all, delete-orphan",
        order_by="StudyTask.sort_order",
    )


class StudyTask(AuditMixin, Base):
    __tablename__ = "study_tasks"

    day_id: Mapped[int] = mapped_column(ForeignKey("study_plan_days.id"), index=True)
    task_type: Mapped[str] = mapped_column(String(30))
    title: Mapped[str] = mapped_column(String(160))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    subject: Mapped[str | None] = mapped_column(String(120), nullable=True)
    scheduled_start: Mapped[time] = mapped_column(Time)
    scheduled_end: Mapped[time] = mapped_column(Time)
    duration_minutes: Mapped[int] = mapped_column(Integer)
    is_break: Mapped[bool] = mapped_column(Boolean, default=False)
    sort_order: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)

    day: Mapped[StudyPlanDay] = relationship(back_populates="tasks")


class DailySummary(AuditMixin, Base):
    __tablename__ = "daily_summaries"
    __table_args__ = (UniqueConstraint("user_id", "summary_date", name="uq_daily_summary_user_date"),)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    summary_date: Mapped[date] = mapped_column(Date, index=True)
    content: Mapped[str] = mapped_column(Text)
    content_format: Mapped[str] = mapped_column(String(20), default="markdown")
    status: Mapped[str] = mapped_column(String(20), default="active", index=True)
