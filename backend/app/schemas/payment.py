from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PlanRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    description: str
    price_cents: int
    duration_days: int


class CreateOrderRequest(BaseModel):
    plan_code: str


class OrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    order_no: str
    amount_cents: int
    provider: str
    status: str
    paid_at: datetime | None
    created_at: datetime


class SubscriptionRead(BaseModel):
    plan_code: str
    plan_name: str
    status: str
    starts_at: datetime
    expires_at: datetime


class PaymentStatus(BaseModel):
    order: OrderRead
    subscription: SubscriptionRead | None = None

