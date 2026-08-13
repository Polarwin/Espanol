"""Private friend groups: groups, members, cooperative goals, encouragements."""

from datetime import date, datetime

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from ..db import Base


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    invite_code: Mapped[str] = mapped_column(unique=True, index=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))


class GroupMember(Base):
    __tablename__ = "group_members"
    __table_args__ = (UniqueConstraint("group_id", "user_id", name="uq_group_members_group_user"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    role: Mapped[str] = mapped_column(default="member")  # "owner" | "member"
    joined_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


class GroupGoal(Base):
    __tablename__ = "group_goals"

    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), index=True)
    kind: Mapped[str]
    target: Mapped[int]
    current: Mapped[int] = mapped_column(default=0)
    week_start: Mapped[date]


class Encouragement(Base):
    __tablename__ = "encouragements"

    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), index=True)
    from_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    to_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    message: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
