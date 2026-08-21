"""Password hashing, JWT tokens, and the get_current_user dependency."""

import base64
import binascii
import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import settings
from ..db import get_db
from ..models import User

# Password hashing: PBKDF2-HMAC-SHA256 via stdlib hashlib. New hashes use our
# own ``vamos-pbkdf2$rounds$salt$checksum`` format; legacy
# ``$pbkdf2-sha256$rounds$salt$checksum`` hashes from the old dependency are
# still verified so existing accounts keep working. That legacy format encodes
# salt and checksum with an adapted base64 variant: standard base64, no
# padding, ``+`` → ``.``.
_PBKDF2_ROUNDS = 29000  # matches the legacy pbkdf2_sha256 default
_SALT_BYTES = 16


def _ab64_encode(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii").rstrip("=").replace("+", ".")


def _ab64_decode(data: str) -> bytes:
    return base64.b64decode(
        data.replace(".", "+") + "=" * (-len(data) % 4), validate=True
    )


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(_SALT_BYTES)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _PBKDF2_ROUNDS)
    return f"vamos-pbkdf2${_PBKDF2_ROUNDS}${_ab64_encode(salt)}${_ab64_encode(digest)}"


def verify_password(password: str, password_hash: str) -> bool:
    if password_hash.startswith("vamos-pbkdf2$"):
        parts = password_hash.split("$")
        if len(parts) != 4:
            return False
        _, rounds, salt, checksum = parts
    elif password_hash.startswith("$pbkdf2-sha256$"):  # legacy format
        parts = password_hash.split("$")
        if len(parts) != 5:
            return False
        _, _, rounds, salt, checksum = parts
    else:
        return False
    try:
        rounds_int = int(rounds)
        salt_bytes = _ab64_decode(salt)
        expected = _ab64_decode(checksum)
    except (ValueError, binascii.Error):
        return False
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt_bytes, rounds_int)
    return hmac.compare_digest(digest, expected)


bearer = HTTPBearer(auto_error=False)


def create_token(user_id: int) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(minutes=settings.jwt_expire_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
    )
    if credentials is None:
        raise unauthorized
    try:
        payload = jwt.decode(
            credentials.credentials, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
        user_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise unauthorized from None
    user = db.get(User, user_id)
    if user is None:
        raise unauthorized
    return user
