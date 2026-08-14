"""Auth schemas."""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class RegisterRequest(BaseModel):
    email: str
    password: str
    display_name: str
    interests: list[str] = []


class LoginRequest(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    id: int
    email: str
    display_name: str
    nickname: str | None
    interests: list[str]
    placement_completed: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ProfileUpdate(BaseModel):
    display_name: str = Field(min_length=1, max_length=60)
    nickname: str | None = Field(default=None, max_length=30)

    @field_validator("display_name")
    @classmethod
    def trim_display_name(cls, value: str) -> str:
        cleaned = " ".join(value.split())
        if not cleaned:
            raise ValueError("Name cannot be blank")
        return cleaned

    @field_validator("nickname")
    @classmethod
    def trim_nickname(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return " ".join(value.split()) or None


class AuthResponse(BaseModel):
    token: str
    user: UserOut
