"""Auth schemas."""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class RegisterRequest(BaseModel):
    email: str = Field(
        max_length=254,
        pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
    )
    password: str = Field(min_length=8, max_length=128)
    display_name: str = Field(min_length=1, max_length=60)
    interests: list[str] = Field(default=[], max_length=10)

    @field_validator("display_name")
    @classmethod
    def trim_display_name(cls, value: str) -> str:
        cleaned = " ".join(value.split())
        if not cleaned:
            raise ValueError("Name cannot be blank")
        return cleaned

    @field_validator("interests")
    @classmethod
    def trim_interests(cls, value: list[str]) -> list[str]:
        cleaned = [" ".join(interest.split()) for interest in value]
        if any(len(interest) > 40 for interest in cleaned):
            raise ValueError("Interests must be 40 characters or fewer")
        return [interest for interest in cleaned if interest]


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
