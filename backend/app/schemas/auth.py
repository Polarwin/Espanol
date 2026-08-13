"""Auth schemas."""

from datetime import datetime

from pydantic import BaseModel


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
    interests: list[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class AuthResponse(BaseModel):
    token: str
    user: UserOut
