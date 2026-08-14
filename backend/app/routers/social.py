"""Small private friend groups and encouragements."""

import secrets

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Encouragement, Group, GroupMember, User
from ..schemas.social import EncouragementCreate, GroupCreate, GroupJoin, GroupOut
from ..services.security import get_current_user

router = APIRouter(prefix="/api/groups", tags=["groups"])


def _member(db: Session, group_id: int, user_id: int) -> GroupMember | None:
    return db.scalar(select(GroupMember).where(GroupMember.group_id == group_id, GroupMember.user_id == user_id))


def _preferred_name(user: User) -> str:
    return user.nickname or user.display_name


def _out(db: Session, group: Group) -> dict:
    members = db.scalars(select(GroupMember).where(GroupMember.group_id == group.id)).all()
    notes = db.scalars(select(Encouragement).where(Encouragement.group_id == group.id).order_by(Encouragement.created_at.desc()).limit(20)).all()
    return {"id": group.id, "name": group.name, "invite_code": group.invite_code,
            "members": [{"user_id": m.user_id, "display_name": _preferred_name(db.get(User, m.user_id)), "role": m.role} for m in members],
            "encouragements": [{"id": n.id, "from_display_name": _preferred_name(db.get(User, n.from_user_id)), "to_user_id": n.to_user_id, "message": n.message, "created_at": n.created_at} for n in notes]}


@router.get("", response_model=list[GroupOut])
def list_groups(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[dict]:
    groups = db.scalars(select(Group).join(GroupMember).where(GroupMember.user_id == user.id)).all()
    return [_out(db, group) for group in groups]


@router.post("", response_model=GroupOut, status_code=status.HTTP_201_CREATED)
def create_group(payload: GroupCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    group = Group(name=payload.name.strip(), invite_code=secrets.token_urlsafe(6).upper(), created_by=user.id)
    db.add(group); db.flush(); db.add(GroupMember(group_id=group.id, user_id=user.id, role="owner")); db.commit()
    return _out(db, group)


@router.post("/join", response_model=GroupOut)
def join_group(payload: GroupJoin, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    group = db.scalar(select(Group).where(Group.invite_code == payload.invite_code.strip().upper()))
    if group is None: raise HTTPException(status_code=404, detail="Group not found")
    if _member(db, group.id, user.id) is None: db.add(GroupMember(group_id=group.id, user_id=user.id)); db.commit()
    return _out(db, group)


@router.post("/{group_id}/encouragements", response_model=GroupOut)
def encourage(group_id: int, payload: EncouragementCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    group = db.get(Group, group_id)
    if group is None or _member(db, group_id, user.id) is None: raise HTTPException(status_code=404, detail="Group not found")
    if _member(db, group_id, payload.to_user_id) is None: raise HTTPException(status_code=400, detail="Recipient is not a group member")
    db.add(Encouragement(group_id=group_id, from_user_id=user.id, to_user_id=payload.to_user_id, message=payload.message.strip())); db.commit()
    return _out(db, group)
