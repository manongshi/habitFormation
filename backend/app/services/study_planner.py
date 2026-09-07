import json
from datetime import date, datetime, time, timedelta

import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import (
    Certificate,
    ExamPreparationProfile,
    StudyPlan,
    StudyPlanDay,
    StudyTask,
    User,
)
from app.schemas import PlanGenerateRequest, StudyPlanRead


def _ai_advice(certificate: Certificate, payload: PlanGenerateRequest) -> tuple[dict, str]:
    default = {
        "subject_order": payload.weak_subjects + [
            subject for subject in certificate.subjects if subject not in payload.weak_subjects
        ],
        "foundation_ratio": 0.45,
        "intensive_ratio": 0.35,
    }
    if payload.ai_provider == "qwen":
        api_key = settings.qwen_api_key
        base_url = settings.qwen_base_url
        model = settings.qwen_model
    else:
        api_key = settings.ai_api_key
        base_url = settings.ai_base_url
        model = settings.ai_model

    if not all([api_key, base_url, model]):
        return default, "rules"

    prompt = {
        "certificate": certificate.name,
        "subjects": certificate.subjects,
        "current_level": payload.current_level,
        "weak_subjects": payload.weak_subjects,
        "days": (payload.target_exam_date - payload.study_start_date).days,
        "instruction": (
            "只返回JSON对象，不要返回其他文字。格式示例："
            '{"subject_order":["科目一","科目二"],'
            '"foundation_ratio":0.45,"intensive_ratio":0.35}。'
            "subject_order为科目顺序；foundation_ratio和intensive_ratio为0到1之间比例，"
            "二者之和不大于0.9。"
        ),
    }
    try:
        request_body = {
            "model": model,
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": "你是严谨的中国职业资格考试学习规划师。请输出JSON。"},
                {"role": "user", "content": json.dumps(prompt, ensure_ascii=False)},
            ],
        }
        if payload.ai_provider == "qwen":
            request_body["enable_thinking"] = False
        else:
            request_body["thinking"] = {"type": "disabled"}
            request_body["max_tokens"] = 800

        response = httpx.post(
            f"{base_url.rstrip('/')}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json=request_body,
            timeout=45,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"].strip()
        content = content.removeprefix("```json").removesuffix("```").strip()
        advice = json.loads(content)
        valid_subjects = [item for item in advice.get("subject_order", []) if item in certificate.subjects]
        if valid_subjects:
            default["subject_order"] = valid_subjects + [
                item for item in certificate.subjects if item not in valid_subjects
            ]
        foundation = float(advice.get("foundation_ratio", default["foundation_ratio"]))
        intensive = float(advice.get("intensive_ratio", default["intensive_ratio"]))
        if 0.2 <= foundation <= 0.7 and 0.15 <= intensive <= 0.6 and foundation + intensive <= 0.9:
            default["foundation_ratio"] = foundation
            default["intensive_ratio"] = intensive
        return default, payload.ai_provider
    except (httpx.HTTPError, KeyError, TypeError, ValueError, json.JSONDecodeError):
        return default, "rules"


def _start_time(period: str, is_weekend: bool) -> time:
    if period == "morning":
        return time(8, 30) if is_weekend else time(7, 0)
    if period == "afternoon":
        return time(14, 0) if is_weekend else time(18, 30)
    return time(19, 30) if not is_weekend else time(19, 0)


def _task_kind(index: int, total: int, phase: str) -> tuple[str, str]:
    if phase == "冲刺复盘":
        return ("mock" if index == 0 else "review", "模拟训练" if index == 0 else "错题复盘")
    if index == 0:
        return "learn", "知识学习"
    if index == total - 1:
        return "review", "回顾整理"
    return "practice", "专项练习"


def generate_study_plan(
    db: Session,
    user: User,
    certificate: Certificate,
    payload: PlanGenerateRequest,
) -> StudyPlan:
    advice, generation_mode = _ai_advice(certificate, payload)
    subjects = advice["subject_order"] or certificate.subjects or [certificate.name]
    all_dates = []
    cursor = payload.study_start_date
    allowed = set(payload.available_weekdays)
    while cursor < payload.target_exam_date:
        if cursor.isoweekday() in allowed:
            all_dates.append(cursor)
        cursor += timedelta(days=1)

    profile = ExamPreparationProfile(
        user_id=user.id,
        certificate_id=certificate.id,
        created_by=user.id,
        updated_by=user.id,
        **payload.model_dump(exclude={"certificate_id", "ai_provider"}),
    )
    db.add(profile)
    db.flush()

    plan = StudyPlan(
        user_id=user.id,
        profile_id=profile.id,
        certificate_id=certificate.id,
        name=f"{certificate.short_name or certificate.name}备考计划",
        start_date=payload.study_start_date,
        end_date=payload.target_exam_date,
        total_days=len(all_dates),
        total_study_minutes=0,
        generation_mode=generation_mode,
        created_by=user.id,
        updated_by=user.id,
    )
    db.add(plan)
    db.flush()

    foundation_end = max(round(len(all_dates) * advice["foundation_ratio"]), 1)
    intensive_end = max(
        round(len(all_dates) * (advice["foundation_ratio"] + advice["intensive_ratio"])),
        foundation_end + 1,
    )

    for day_index, study_date in enumerate(all_dates):
        if day_index < foundation_end:
            phase = "基础构建"
        elif day_index < intensive_end:
            phase = "强化训练"
        else:
            phase = "冲刺复盘"

        subject = subjects[day_index % len(subjects)]
        study_minutes = payload.weekend_minutes if study_date.isoweekday() >= 6 else payload.weekday_minutes
        session_count = max((study_minutes + payload.session_minutes - 1) // payload.session_minutes, 1)
        chunks = []
        remaining = study_minutes
        for _ in range(session_count):
            chunk = min(payload.session_minutes, remaining)
            chunks.append(chunk)
            remaining -= chunk

        total_break_minutes = payload.break_minutes * max(len(chunks) - 1, 0)
        plan.total_study_minutes += study_minutes
        day = StudyPlanDay(
            plan_id=plan.id,
            study_date=study_date,
            day_number=day_index + 1,
            phase=phase,
            focus=subject,
            study_minutes=study_minutes,
            break_minutes=total_break_minutes,
            created_by=user.id,
            updated_by=user.id,
        )
        db.add(day)
        db.flush()

        current = datetime.combine(study_date, _start_time(payload.preferred_period, study_date.isoweekday() >= 6))
        sort_order = 1
        for chunk_index, duration in enumerate(chunks):
            task_type, task_label = _task_kind(chunk_index, len(chunks), phase)
            end = current + timedelta(minutes=duration)
            db.add(
                StudyTask(
                    day_id=day.id,
                    task_type=task_type,
                    title=f"{task_label} · {subject}",
                    description=f"围绕{subject}完成{phase}阶段的{task_label}。",
                    subject=subject,
                    scheduled_start=current.time(),
                    scheduled_end=end.time(),
                    duration_minutes=duration,
                    is_break=False,
                    sort_order=sort_order,
                    created_by=user.id,
                    updated_by=user.id,
                )
            )
            sort_order += 1
            current = end
            if chunk_index < len(chunks) - 1:
                break_end = current + timedelta(minutes=payload.break_minutes)
                db.add(
                    StudyTask(
                        day_id=day.id,
                        task_type="break",
                        title="离屏休息",
                        description="起身活动、补水并让眼睛离开屏幕。",
                        scheduled_start=current.time(),
                        scheduled_end=break_end.time(),
                        duration_minutes=payload.break_minutes,
                        is_break=True,
                        sort_order=sort_order,
                        created_by=user.id,
                        updated_by=user.id,
                    )
                )
                sort_order += 1
                current = break_end

    db.commit()
    db.refresh(plan)
    return plan


def plan_response(plan: StudyPlan, certificate_name: str) -> StudyPlanRead:
    outline_by_phase = {}
    for day in plan.days:
        phase = outline_by_phase.setdefault(
            day.phase,
            {
                "phase": day.phase,
                "start_date": day.study_date,
                "end_date": day.study_date,
                "study_days": 0,
                "study_minutes": 0,
                "break_minutes": 0,
                "subjects": [],
            },
        )
        phase["end_date"] = day.study_date
        phase["study_days"] += 1
        phase["study_minutes"] += day.study_minutes
        phase["break_minutes"] += day.break_minutes
        if day.focus not in phase["subjects"]:
            phase["subjects"].append(day.focus)

    return StudyPlanRead(
        id=plan.id,
        name=plan.name,
        certificate_id=plan.certificate_id,
        certificate_name=certificate_name,
        start_date=plan.start_date,
        end_date=plan.end_date,
        total_days=plan.total_days,
        total_study_minutes=plan.total_study_minutes,
        generation_mode=plan.generation_mode,
        status=plan.status,
        outline=list(outline_by_phase.values()),
        days=plan.days,
    )
