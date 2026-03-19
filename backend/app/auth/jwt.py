# app/auth/jwt.py
import jwt
from datetime import datetime, timedelta
from app.core.settings import settings
from typing import Dict, Any

def create_access_token(user_id: int, expires_seconds: int | None = None) -> str:
    expires_seconds = expires_seconds or settings.JWT_ACCESS_TOKEN_EXPIRES_SECONDS
    exp = datetime.utcnow() + timedelta(seconds=int(expires_seconds))
    payload: Dict[str, Any] = {"sub": str(user_id), "exp": exp, "type": "access"}
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token

def create_refresh_token(user_id: int, expires_seconds: int | None = None) -> str:
    expires_seconds = expires_seconds or settings.JWT_REFRESH_TOKEN_EXPIRES_SECONDS
    exp = datetime.utcnow() + timedelta(seconds=int(expires_seconds))
    payload: Dict[str, Any] = {"sub": str(user_id), "exp": exp, "type": "refresh"}
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token


def create_password_reset_token(user_id: int, expires_seconds: int | None = None) -> str:
    expires_seconds = expires_seconds or settings.PASSWORD_RESET_TOKEN_EXPIRES_SECONDS
    exp = datetime.utcnow() + timedelta(seconds=int(expires_seconds))
    payload: Dict[str, Any] = {
        "sub": str(user_id),
        "exp": exp,
        "type": "password_reset",
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token

def decode_token(token: str) -> dict:
    """
    Decode a token and return payload. Raises jwt exceptions on failure.
    """
    payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    return payload


# when issuing refresh token , store it in refresh_token table with expires_at, on logout or revoke , delete the refresh