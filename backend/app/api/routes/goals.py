from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models import ExamGoal, User
from app.schemas import ExamGoalCreate, ExamGoalRead

router = APIRouter(prefix="/goals", tags=["goals"])


@router.get("", response_model=list[ExamGoalRead])
def list_goals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ExamGoal]:
    return list(
        db.scalars(
            select(ExamGoal)
            .where(
                ExamGoal.user_id == current_user.id,
                ExamGoal.is_deleted.is_(False),
            )
            .order_by(ExamGoal.created_at.desc())
        ).all()
    )


@router.post("", response_model=ExamGoalRead, status_code=status.HTTP_201_CREATED)
def create_goal(
    payload: ExamGoalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ExamGoal:
    goal = ExamGoal(
        user_id=current_user.id,
        created_by=current_user.id,
        updated_by=current_user.id,
        **payload.model_dump(),
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal


@router.get("/{goal_id}", response_model=ExamGoalRead)
def get_goal(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ExamGoal:
    goal = db.scalar(
        select(ExamGoal).where(
            ExamGoal.id == goal_id,
            ExamGoal.user_id == current_user.id,
            ExamGoal.is_deleted.is_(False),
        )
    )
    if goal is None:
        raise HTTPException(status_code=404, detail="考试目标不存在")
    return goal
