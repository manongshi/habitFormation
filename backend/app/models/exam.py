from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.mixins import AuditMixin


class ExamGoal(AuditMixin, Base):
    __tablename__ = "exam_goals"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    exam_name: Mapped[str] = mapped_column(String(120), index=True)
    exam_date: Mapped[date] = mapped_column(Date)
    target_score: Mapped[Decimal] = mapped_column(Numeric(6, 2))
    daily_minutes: Mapped[int] = mapped_column(Integer, default=60)
    current_level: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active", index=True)
    knowledge_points: Mapped[list["KnowledgePoint"]] = relationship(
        back_populates="goal",
        cascade="all, delete-orphan",
    )
    user: Mapped["User"] = relationship(back_populates="goals")


class KnowledgePoint(AuditMixin, Base):
    __tablename__ = "knowledge_points"

    goal_id: Mapped[int] = mapped_column(ForeignKey("exam_goals.id"), index=True)
    name: Mapped[str] = mapped_column(String(160))
    category: Mapped[str | None] = mapped_column(String(120), nullable=True)
    mastery_level: Mapped[int] = mapped_column(Integer, default=0)
    next_review_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    goal: Mapped[ExamGoal] = relationship(back_populates="knowledge_points")
    attempts: Mapped[list["PracticeAttempt"]] = relationship(
        back_populates="knowledge_point",
        cascade="all, delete-orphan",
    )


class PracticeAttempt(AuditMixin, Base):
    __tablename__ = "practice_attempts"

    knowledge_point_id: Mapped[int] = mapped_column(
        ForeignKey("knowledge_points.id"),
        index=True,
    )
    question_text: Mapped[str] = mapped_column(Text)
    user_answer: Mapped[str] = mapped_column(Text)
    is_correct: Mapped[int] = mapped_column(Integer, default=0)
    error_type: Mapped[str | None] = mapped_column(String(60), nullable=True)
    ai_feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    knowledge_point: Mapped[KnowledgePoint] = relationship(back_populates="attempts")
