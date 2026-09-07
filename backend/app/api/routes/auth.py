import secrets

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.config import settings
from app.core.redis import get_redis
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models import User
from app.schemas import (
    EmailCodeRequest,
    EmailCodeResponse,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserRead,
)
from app.services.email_sender import send_verification_email
from app.services.email_verification import EmailVerificationService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/email-code", response_model=EmailCodeResponse)
def send_email_code(
    payload: EmailCodeRequest,
    db: Session = Depends(get_db),
) -> EmailCodeResponse:
    email = payload.email.lower()
    if db.scalar(select(User).where(User.email == email, User.is_deleted.is_(False))):
        raise HTTPException(status_code=409, detail="该邮箱已经注册")

    code = f"{secrets.randbelow(1_000_000):06d}"
    verification = EmailVerificationService(get_redis())
    verification.save_code(email, payload.scene, code)
    try:
        send_verification_email(email, code)
    except Exception as exc:
        verification.remove_code(email, payload.scene)
        raise HTTPException(status_code=503, detail="验证码邮件发送失败") from exc

    return EmailCodeResponse(
        expires_in=settings.email_code_expire_seconds,
        cooldown=settings.email_code_cooldown_seconds,
    )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> TokenResponse:
    email = payload.email.lower()
    if db.scalar(select(User).where(User.email == email, User.is_deleted.is_(False))):
        raise HTTPException(status_code=409, detail="该邮箱已经注册")

    EmailVerificationService(get_redis()).verify_and_consume(
        email,
        "register",
        payload.email_code,
    )

    user = User(
        email=email,
        nickname=payload.nickname.strip(),
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.flush()
    user.created_by = user.id
    user.updated_by = user.id
    db.commit()
    db.refresh(user)
    return TokenResponse(access_token=create_access_token(user.id), user=user)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.scalar(
        select(User).where(
            User.email == payload.email.lower(),
            User.is_deleted.is_(False),
        )
    )
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="邮箱或密码错误")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="账号已停用")
    return TokenResponse(access_token=create_access_token(user.id), user=user)


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user
