from datetime import datetime

from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class EmailCodeRequest(BaseModel):
    email: EmailStr
    scene: Literal["register"] = "register"


class EmailCodeResponse(BaseModel):
    sent: bool = True
    expires_in: int
    cooldown: int


class RegisterRequest(BaseModel):
    email: EmailStr
    email_code: str = Field(pattern=r"^\d{6}$")
    nickname: str = Field(min_length=2, max_length=60)
    password: str = Field(min_length=8, max_length=72)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    nickname: str
    is_active: bool
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead
