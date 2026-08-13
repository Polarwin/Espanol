"""Private friend-group API schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class GroupCreate(BaseModel):
    name: str = Field(min_length=2, max_length=80)


class GroupJoin(BaseModel):
    invite_code: str = Field(min_length=6, max_length=16)


class EncouragementCreate(BaseModel):
    to_user_id: int
    message: str = Field(min_length=1, max_length=120)


class GroupMemberOut(BaseModel):
    user_id: int
    display_name: str
    role: str


class EncouragementOut(BaseModel):
    id: int
    from_display_name: str
    to_user_id: int
    message: str
    created_at: datetime


class GroupOut(BaseModel):
    id: int
    name: str
    invite_code: str
    members: list[GroupMemberOut]
    encouragements: list[EncouragementOut]
