from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models import ExamGoal, KnowledgePoint, User
from app.schemas import DashboardOverview

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/overview", response_model=DashboardOverview)
def get_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DashboardOverview:
    goal = db.scalar(
        select(ExamGoal)
        .where(
            ExamGoal.status == "active",
            ExamGoal.user_id == current_user.id,
            ExamGoal.is_deleted.is_(False),
        )
        .order_by(ExamGoal.created_at.desc())
    )
    if goal is None:
        return DashboardOverview(
            active_goal=None,
            days_remaining=None,
            mastery_rate=0,
            pending_reviews=0,
            completed_today=0,
        )

    mastery_rate = db.scalar(
        select(func.coalesce(func.avg(KnowledgePoint.mastery_level), 0)).where(
            KnowledgePoint.goal_id == goal.id,
            KnowledgePoint.is_deleted.is_(False),
        )
    )
    pending_reviews = db.scalar(
        select(func.count(KnowledgePoint.id)).where(
            KnowledgePoint.goal_id == goal.id,
            KnowledgePoint.next_review_at <= func.now(),
            KnowledgePoint.is_deleted.is_(False),
        )
    )

    return DashboardOverview(
        active_goal=goal,
        days_remaining=max((goal.exam_date - date.today()).days, 0),
        mastery_rate=round(float(mastery_rate or 0)),
        pending_reviews=int(pending_reviews or 0),
        completed_today=0,
    )
