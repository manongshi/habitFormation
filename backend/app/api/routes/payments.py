from datetime import datetime, timedelta
from secrets import token_hex

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.config import settings
from app.db.session import get_db
from app.models import PaymentOrder, Subscription, SubscriptionPlan, User
from app.schemas import (
    CreateOrderRequest,
    OrderRead,
    PaymentStatus,
    PlanRead,
    SubscriptionRead,
)

router = APIRouter(prefix="/payments", tags=["payments"])


def subscription_schema(subscription: Subscription) -> SubscriptionRead:
    return SubscriptionRead(
        plan_code=subscription.plan.code,
        plan_name=subscription.plan.name,
        status=subscription.status,
        starts_at=subscription.starts_at,
        expires_at=subscription.expires_at,
    )


@router.get("/plans", response_model=list[PlanRead])
def list_plans(db: Session = Depends(get_db)) -> list[SubscriptionPlan]:
    return list(
        db.scalars(
            select(SubscriptionPlan)
            .where(
                SubscriptionPlan.status == "active",
                SubscriptionPlan.is_deleted.is_(False),
            )
            .order_by(SubscriptionPlan.price_cents)
        ).all()
    )


@router.get("/subscription", response_model=SubscriptionRead | None)
def current_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SubscriptionRead | None:
    subscription = db.scalar(
        select(Subscription)
        .where(
            Subscription.user_id == current_user.id,
            Subscription.status == "active",
            Subscription.expires_at > datetime.now(),
            Subscription.is_deleted.is_(False),
        )
        .order_by(Subscription.expires_at.desc())
    )
    return subscription_schema(subscription) if subscription else None


@router.post("/orders", response_model=OrderRead, status_code=201)
def create_order(
    payload: CreateOrderRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PaymentOrder:
    plan = db.scalar(
        select(SubscriptionPlan).where(
            SubscriptionPlan.code == payload.plan_code,
            SubscriptionPlan.status == "active",
            SubscriptionPlan.is_deleted.is_(False),
        )
    )
    if plan is None:
        raise HTTPException(status_code=404, detail="套餐不存在或已下架")

    order = PaymentOrder(
        order_no=f"EC{datetime.now():%Y%m%d%H%M%S}{token_hex(4).upper()}",
        user_id=current_user.id,
        plan_id=plan.id,
        amount_cents=plan.price_cents,
        provider=settings.payment_provider,
        created_by=current_user.id,
        updated_by=current_user.id,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


@router.get("/orders/{order_no}", response_model=PaymentStatus)
def get_order(
    order_no: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PaymentStatus:
    order = db.scalar(
        select(PaymentOrder).where(
            PaymentOrder.order_no == order_no,
            PaymentOrder.user_id == current_user.id,
            PaymentOrder.is_deleted.is_(False),
        )
    )
    if order is None:
        raise HTTPException(status_code=404, detail="订单不存在")
    subscription = db.scalar(select(Subscription).where(Subscription.order_id == order.id))
    return PaymentStatus(
        order=order,
        subscription=subscription_schema(subscription) if subscription else None,
    )


@router.post("/orders/{order_no}/mock-pay", response_model=PaymentStatus)
def mock_pay(
    order_no: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PaymentStatus:
    if settings.payment_provider != "mock" or settings.app_env == "production":
        raise HTTPException(status_code=404, detail="模拟支付未启用")

    order = db.scalar(
        select(PaymentOrder).where(
            PaymentOrder.order_no == order_no,
            PaymentOrder.user_id == current_user.id,
            PaymentOrder.is_deleted.is_(False),
        )
    )
    if order is None:
        raise HTTPException(status_code=404, detail="订单不存在")

    subscription = db.scalar(select(Subscription).where(Subscription.order_id == order.id))
    if subscription is None:
        now = datetime.now()
        active_subscription = db.scalar(
            select(Subscription)
            .where(
                Subscription.user_id == current_user.id,
                Subscription.status == "active",
                Subscription.expires_at > now,
                Subscription.is_deleted.is_(False),
            )
            .order_by(Subscription.expires_at.desc())
        )
        starts_at = active_subscription.expires_at if active_subscription else now
        subscription = Subscription(
            user_id=current_user.id,
            plan_id=order.plan_id,
            order_id=order.id,
            starts_at=starts_at,
            expires_at=starts_at + timedelta(days=order.plan.duration_days),
            created_by=current_user.id,
            updated_by=current_user.id,
        )
        order.status = "paid"
        order.paid_at = now
        order.provider_trade_no = f"MOCK-{token_hex(6).upper()}"
        db.add(subscription)
        db.commit()
        db.refresh(order)
        db.refresh(subscription)

    return PaymentStatus(order=order, subscription=subscription_schema(subscription))
