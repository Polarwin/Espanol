"""Auth routes: register, login, and the current user's profile."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import User
from ..schemas import AuthResponse, LoginRequest, ProfileUpdate, RegisterRequest, UserOut
from ..services.progress import init_skill_progress
from ..services.security import create_token, get_current_user, hash_password, verify_password
from ..services.streak import get_or_create_streak

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> AuthResponse:
    existing = db.scalar(select(User).where(User.email == payload.email))
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
        )
    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        display_name=payload.display_name,
        interests=payload.interests,
    )
    db.add(user)
    db.flush()
    init_skill_progress(db, user)
    get_or_create_streak(db, user)
    db.commit()
    return AuthResponse(token=create_token(user.id), user=UserOut.model_validate(user))


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> AuthResponse:
    user = db.scalar(select(User).where(User.email == payload.email))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )
    return AuthResponse(token=create_token(user.id), user=UserOut.model_validate(user))


me_router = APIRouter(tags=["auth"])


@me_router.get("/api/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)) -> UserOut:
    return UserOut.model_validate(user)


@me_router.patch("/api/me", response_model=UserOut)
def update_me(
    payload: ProfileUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserOut:
    user.display_name = payload.display_name
    user.nickname = payload.nickname
    db.commit()
    db.refresh(user)
    return UserOut.model_validate(user)
