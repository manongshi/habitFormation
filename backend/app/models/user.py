from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.mixins import AuditMixin


class User(AuditMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(190), unique=True, index=True)
    nickname: Mapped[str] = mapped_column(String(60))
    password_hash: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    goals: Mapped[list["ExamGoal"]] = relationship(back_populates="user")
    orders: Mapped[list["PaymentOrder"]] = relationship(back_populates="user")
    subscriptions: Mapped[list["Subscription"]] = relationship(back_populates="user")
