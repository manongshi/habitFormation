from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models import Certificate, DailySummary, StudyPlan, StudyPlanDay, StudyTask, User
from app.schemas import (
    DailySummaryRead,
    DailySummaryWrite,
    PlanGenerateRequest,
    StudyPlanListItem,
    StudyPlanRead,
    StudyCalendarDayRead,
    StudyTaskRead,
    StudyTaskStatusUpdate,
)
from app.services.study_planner import generate_study_plan, plan_response

router = APIRouter(prefix="/study-plans", tags=["study-plans"])


def latest_active_plans(db: Session, user_id: int) -> list[StudyPlan]:
    plans = db.scalars(
        select(StudyPlan)
        .where(
            StudyPlan.user_id == user_id,
            StudyPlan.is_deleted.is_(False),
            StudyPlan.status == "active",
        )
        .order_by(StudyPlan.created_at.desc(), StudyPlan.id.desc())
    ).all()
    latest_by_certificate = {}
    for plan in plans:
        latest_by_certificate.setdefault(plan.certificate_id, plan)
    return list(latest_by_certificate.values())


@router.post("/generate", response_model=StudyPlanRead, status_code=status.HTTP_201_CREATED)
def create_plan(
    payload: PlanGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StudyPlanRead:
    certificate = db.scalar(
        select(Certificate).where(
            Certificate.id == payload.certificate_id,
            Certificate.status == "active",
            Certificate.is_deleted.is_(False),
        )
    )
    if certificate is None:
        raise HTTPException(status_code=404, detail="证书不存在或已下架")

    study_days = sum(
        1
        for offset in range((payload.target_exam_date - payload.study_start_date).days)
        if (payload.study_start_date + timedelta(days=offset)).isoweekday()
        in payload.available_weekdays
    )
    if study_days < 3:
        raise HTTPException(status_code=400, detail="至少需要安排 3 个学习日")

    plan = generate_study_plan(db, current_user, certificate, payload)
    plan = db.scalar(
        select(StudyPlan)
        .options(selectinload(StudyPlan.days).selectinload(StudyPlanDay.tasks))
        .where(StudyPlan.id == plan.id)
    )
    return plan_response(plan, certificate.name)


@router.get("", response_model=list[StudyPlanListItem])
def list_plans(
    study_date: date | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[StudyPlanListItem]:
    latest_plans = latest_active_plans(db, current_user.id)
    if not latest_plans:
        return []
    plan_ids = [plan.id for plan in latest_plans]
    certificates = {
        certificate.id: certificate
        for certificate in db.scalars(
            select(Certificate).where(Certificate.id.in_([plan.certificate_id for plan in latest_plans]))
        ).all()
    }
    selected_date = study_date or date.today()
    today_days = {
        day.plan_id: day
        for day in db.scalars(
            select(StudyPlanDay)
            .options(selectinload(StudyPlanDay.tasks))
            .where(
                StudyPlanDay.plan_id.in_(plan_ids),
                StudyPlanDay.study_date == selected_date,
                StudyPlanDay.is_deleted.is_(False),
            )
        ).all()
    }

    items = []
    for plan in latest_plans:
        certificate = certificates[plan.certificate_id]
        duration = max((plan.end_date - plan.start_date).days, 1)
        elapsed = min(max((selected_date - plan.start_date).days, 0), duration)
        items.append(
            StudyPlanListItem(
                id=plan.id,
                name=plan.name,
                certificate_id=plan.certificate_id,
                certificate_name=certificate.name,
                certificate_image_url=certificate.image_url,
                start_date=plan.start_date,
                end_date=plan.end_date,
                total_days=plan.total_days,
                total_study_minutes=plan.total_study_minutes,
                generation_mode=plan.generation_mode,
                status=plan.status,
                progress_percent=round(elapsed / duration * 100),
                today=today_days.get(plan.id),
            )
        )
    return items


@router.get("/calendar", response_model=list[StudyCalendarDayRead])
def get_study_calendar(
    month: str = Query(..., pattern=r"^\d{4}-\d{2}$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[StudyCalendarDayRead]:
    try:
        month_start = date.fromisoformat(f"{month}-01")
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="月份格式不正确") from exc
    month_end = (
        date(month_start.year + 1, 1, 1)
        if month_start.month == 12
        else date(month_start.year, month_start.month + 1, 1)
    )
    plans = latest_active_plans(db, current_user.id)
    if not plans:
        return []

    days = db.scalars(
        select(StudyPlanDay)
        .options(selectinload(StudyPlanDay.tasks))
        .where(
            StudyPlanDay.plan_id.in_([plan.id for plan in plans]),
            StudyPlanDay.study_date >= month_start,
            StudyPlanDay.study_date < month_end,
            StudyPlanDay.is_deleted.is_(False),
        )
        .order_by(StudyPlanDay.study_date)
    ).all()
    status_by_date: dict[date, dict[str, int]] = {}
    for day in days:
        tasks = [task for task in day.tasks if not task.is_break and not task.is_deleted]
        if not tasks:
            continue
        status_item = status_by_date.setdefault(day.study_date, {"total": 0, "completed": 0})
        status_item["total"] += len(tasks)
        status_item["completed"] += sum(task.status == "completed" for task in tasks)

    return [
        StudyCalendarDayRead(
            study_date=study_date,
            total_tasks=status_item["total"],
            completed_tasks=status_item["completed"],
            is_completed=status_item["completed"] == status_item["total"],
        )
        for study_date, status_item in status_by_date.items()
    ]


@router.patch("/tasks/{task_id}", response_model=StudyTaskRead)
def update_task_status(
    task_id: int,
    payload: StudyTaskStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StudyTaskRead:
    task = db.scalar(
        select(StudyTask)
        .join(StudyPlanDay, StudyTask.day_id == StudyPlanDay.id)
        .join(StudyPlan, StudyPlanDay.plan_id == StudyPlan.id)
        .where(
            StudyTask.id == task_id,
            StudyPlan.user_id == current_user.id,
            StudyTask.is_deleted.is_(False),
        )
    )
    if task is None:
        raise HTTPException(status_code=404, detail="任务不存在")
    task.status = "completed" if payload.completed else "pending"
    task.updated_by = current_user.id
    db.commit()
    db.refresh(task)
    return task


@router.get("/daily-summary", response_model=DailySummaryRead | None)
def get_daily_summary(
    study_date: date = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DailySummaryRead | None:
    return db.scalar(
        select(DailySummary).where(
            DailySummary.user_id == current_user.id,
            DailySummary.summary_date == study_date,
            DailySummary.is_deleted.is_(False),
        )
    )


@router.put("/daily-summary", response_model=DailySummaryRead)
def save_daily_summary(
    study_date: date,
    payload: DailySummaryWrite,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DailySummaryRead:
    summary = db.scalar(
        select(DailySummary).where(
            DailySummary.user_id == current_user.id,
            DailySummary.summary_date == study_date,
            DailySummary.is_deleted.is_(False),
        )
    )
    if summary is None:
        summary = DailySummary(
            user_id=current_user.id,
            summary_date=study_date,
            content=payload.content.strip(),
            content_format=payload.content_format,
            created_by=current_user.id,
            updated_by=current_user.id,
        )
        db.add(summary)
    else:
        summary.content = payload.content.strip()
        summary.content_format = payload.content_format
        summary.updated_by = current_user.id
    db.commit()
    db.refresh(summary)
    return summary


@router.get("/{plan_id}", response_model=StudyPlanRead)
def get_plan(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StudyPlanRead:
    plan = db.scalar(
        select(StudyPlan)
        .options(selectinload(StudyPlan.days).selectinload(StudyPlanDay.tasks))
        .where(
            StudyPlan.id == plan_id,
            StudyPlan.user_id == current_user.id,
            StudyPlan.is_deleted.is_(False),
        )
    )
    if plan is None:
        raise HTTPException(status_code=404, detail="学习计划不存在")
    certificate = db.get(Certificate, plan.certificate_id)
    return plan_response(plan, certificate.name)
