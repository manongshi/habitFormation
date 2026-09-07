from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from sqlalchemy import inspect, select, text

from app.db.session import Base, SessionLocal, engine
from app.models import SubscriptionPlan


def seed_subscription_plans() -> None:
    plans = [
        {
            "code": "coach_monthly",
            "name": "教练月卡",
            "description": "每日训练、错因诊断、变式复测与完整掌握地图",
            "price_cents": 3900,
            "duration_days": 30,
        },
        {
            "code": "coach_yearly",
            "name": "教练年卡",
            "description": "全年持续备考，多考试目标管理，包含全部教练能力",
            "price_cents": 29900,
            "duration_days": 365,
        },
    ]
    with SessionLocal() as db:
        existing_codes = set(db.scalars(select(SubscriptionPlan.code)).all())
        for plan in plans:
            if plan["code"] not in existing_codes:
                db.add(SubscriptionPlan(**plan))
        db.commit()


def ensure_schema_compatibility() -> None:
    inspector = inspect(engine)
    if not inspector.has_table("daily_summaries"):
        return
    columns = {column["name"] for column in inspector.get_columns("daily_summaries")}
    if "content_format" not in columns:
        with engine.begin() as connection:
            connection.execute(
                text(
                    "ALTER TABLE daily_summaries "
                    "ADD COLUMN content_format VARCHAR(20) NOT NULL DEFAULT 'markdown' AFTER content"
                )
            )


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    ensure_schema_compatibility()
    seed_subscription_plans()
    yield


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.frontend_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/", tags=["root"])
def root() -> dict[str, str]:
    return {"name": settings.app_name, "docs": "/docs"}
