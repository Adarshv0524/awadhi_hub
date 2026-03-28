# app/api/v1/auth.py
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from urllib.parse import quote, urlencode
import secrets
from starlette.status import HTTP_429_TOO_MANY_REQUESTS

from fastapi.responses import RedirectResponse

from app.db.session import get_db
from app.db.models import User, RefreshToken, OAuthAccount, SystemSetting
from app.auth.hash import hash_password, verify_password
from app.auth.jwt import create_access_token, create_refresh_token, create_password_reset_token, decode_token
from app.auth.google import exchange_code_for_tokens, fetch_google_profile
from app.core.settings import settings
from app.core.security import get_current_user
from app.services.rate_limit import check_and_increment
from app.services.email_service import send_password_reset_email

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterIn(BaseModel):
    email: EmailStr
    password: str
    username: str | None = None


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class RefreshIn(BaseModel):
    refresh_token: str


class LogoutIn(BaseModel):
    refresh_token: str


class ForgotPasswordIn(BaseModel):
    email: EmailStr


class ResetPasswordIn(BaseModel):
    token: str
    new_password: str


def _frontend_oauth_callback_url() -> str:
    return f"{settings.FRONTEND_BASE_URL.rstrip('/')}/oauth/callback"


def _frontend_login_url() -> str:
    return f"{settings.FRONTEND_BASE_URL.rstrip('/')}/login"


@router.post("/register")
def register(data: RegisterIn, db: Session = Depends(get_db)):
    # 1. Check if Email already exists
    existing_email = db.query(User).filter(User.email == data.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # 2. Check if Username already exists
    if data.username:
        existing_username = db.query(User).filter(User.username == data.username).first()
        if existing_username:
            raise HTTPException(status_code=400, detail="Username already taken")

    # 3. Create the user object
    user = User(
        email=data.email,
        username=data.username,
        password_hash=hash_password(data.password),
        role="registered",
    )
    
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
    except Exception as e:
        # 4. Rollback in case of any race conditions or other DB errors
        db.rollback()
        raise HTTPException(
            status_code=500, 
            detail="An internal error occurred during registration."
        )
        
    return {"id": user.id, "email": user.email, "username": user.username}

@router.post("/login")
def login(data: LoginIn, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()

    # Admin login bypasses rate limiting by requirement.
    # Non-admin/unknown-user attempts remain rate-limited to protect auth endpoints.
    is_admin_login = bool(user and user.role == "admin")
    if not is_admin_login:
        rate_limits_row = db.query(SystemSetting).filter(SystemSetting.setting_key == "rate_limits").first()
        rate_limits = rate_limits_row.value if rate_limits_row and isinstance(rate_limits_row.value, dict) else {}
        login_limits = rate_limits.get("login", {}) if isinstance(rate_limits, dict) else {}
        login_limit = int(login_limits.get("limit", 100))
        login_window_seconds = int(login_limits.get("window_seconds", 3600))

        ip = request.client.host if request.client else None
        allowed, retry_after = check_and_increment(
            db=db,
            user_id=user.id if user else None,
            ip_address=ip,
            action_key="login",
            window_seconds=login_window_seconds,
            limit=login_limit,
            granularity=60,
        )
        if not allowed:
            raise HTTPException(
                status_code=HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests",
                headers={"Retry-After": str(retry_after)},
            )

    if not user or not user.password_hash or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_active or user.is_banned:
        raise HTTPException(status_code=403, detail="User not allowed")
    access = create_access_token(user.id)
    refresh = create_refresh_token(user.id)
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=int(settings.JWT_REFRESH_TOKEN_EXPIRES_SECONDS))
    rt = RefreshToken(token=refresh, user_id=user.id, expires_at=expires_at)
    db.add(rt)
    user.last_login = datetime.now(timezone.utc)
    db.commit()
    return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}


@router.post("/refresh")
def refresh_token(data: RefreshIn, db: Session = Depends(get_db)):
    token = data.refresh_token
    try:
        payload = decode_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")
    rt = db.query(RefreshToken).filter(RefreshToken.token == token).first()
    if not rt:
        raise HTTPException(status_code=401, detail="Refresh token revoked")
    access = create_access_token(int(payload["sub"]))
    return {"access_token": access, "token_type": "bearer"}


@router.post("/logout")
def logout(data: LogoutIn, db: Session = Depends(get_db)):
    token = data.refresh_token
    db.query(RefreshToken).filter(RefreshToken.token == token).delete()
    db.commit()
    return {"ok": True}


@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordIn, db: Session = Depends(get_db)):
    # Always return generic success to prevent account enumeration.
    user = db.query(User).filter(User.email == data.email).first()
    if user and user.is_active and not user.is_banned:
        token = create_password_reset_token(user.id)
        token_param = quote(token, safe="")
        reset_link = f"{settings.FRONTEND_BASE_URL.rstrip('/')}/reset-password?token={token_param}"
        send_password_reset_email(user.email, reset_link)

    return {"ok": True, "message": "If an account exists for this email, a reset link has been sent."}


@router.post("/reset-password")
def reset_password(data: ResetPasswordIn, db: Session = Depends(get_db)):
    if len(data.new_password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    try:
        payload = decode_token(data.token)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    if payload.get("type") != "password_reset":
        raise HTTPException(status_code=400, detail="Invalid reset token")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid reset token")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid reset token")
    if not user.is_active or user.is_banned:
        raise HTTPException(status_code=403, detail="Account is not allowed to reset password")

    user.password_hash = hash_password(data.new_password)
    # Revoke all refresh tokens after password reset to force re-authentication everywhere.
    db.query(RefreshToken).filter(RefreshToken.user_id == user.id).delete()
    db.commit()

    return {"ok": True, "message": "Password reset successful"}


@router.get("/me")
def me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "role": current_user.role,
        "permissions": current_user.permissions,
        "permission_scopes": current_user.permission_scopes,
    }


@router.get("/oauth/google/login")
def google_login(next: str = Query("/")):
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=500, detail="Google OAuth is not configured")

    safe_next = next if next.startswith("/") else "/"
    state = secrets.token_urlsafe(24)
    packed_state = f"{state}.{safe_next}"

    auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth?"
        + urlencode(
            {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "response_type": "code",
                "scope": "openid email profile",
                "state": packed_state,
                "access_type": "online",
                "prompt": "select_account",
            }
        )
    )

    response = RedirectResponse(url=auth_url, status_code=302)
    response.set_cookie(
        key="oauth_google_state",
        value=state,
        httponly=True,
        secure=settings.APP_ENV == "production",
        samesite="lax",
        max_age=600,
    )
    return response


@router.get("/oauth/google/callback")
async def google_callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    db: Session = Depends(get_db),
):
    if not code:
        return RedirectResponse(url=f"{_frontend_login_url()}?oauth_error=missing_code", status_code=302)
    if not state:
        return RedirectResponse(url=f"{_frontend_login_url()}?oauth_error=missing_state", status_code=302)

    try:
        expected_state, next_path = state.split(".", 1)
    except Exception:
        return RedirectResponse(url=f"{_frontend_login_url()}?oauth_error=invalid_state", status_code=302)

    cookie_state = request.cookies.get("oauth_google_state")
    if not cookie_state or cookie_state != expected_state:
        return RedirectResponse(url=f"{_frontend_login_url()}?oauth_error=invalid_state", status_code=302)

    redirect_target = next_path if next_path.startswith("/") else "/"

    try:
        token_resp = await exchange_code_for_tokens(code)
    except Exception:
        return RedirectResponse(url=f"{_frontend_login_url()}?oauth_error=token_exchange_failed", status_code=302)

    access_token = token_resp.get("access_token")
    if not access_token:
        return RedirectResponse(url=f"{_frontend_login_url()}?oauth_error=token_exchange_failed", status_code=302)

    try:
        profile = await fetch_google_profile(access_token)
    except Exception:
        return RedirectResponse(url=f"{_frontend_login_url()}?oauth_error=profile_fetch_failed", status_code=302)

    provider_user_id = profile.get("sub")
    email = profile.get("email")
    if not provider_user_id or not email:
        return RedirectResponse(url=f"{_frontend_login_url()}?oauth_error=incomplete_profile", status_code=302)

    oauth = db.query(OAuthAccount).filter(
        OAuthAccount.provider == "google",
        OAuthAccount.provider_user_id == provider_user_id,
    ).first()
    if oauth:
        user = db.query(User).filter(User.id == oauth.user_id).first()
    else:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(email=email, username=None, password_hash=None, role="registered")
            db.add(user)
            db.flush()
        oauth = OAuthAccount(
            provider="google",
            provider_user_id=provider_user_id,
            user_id=user.id,
            raw_profile=profile,
        )
        db.add(oauth)
        db.commit()

    if not user or not user.is_active or user.is_banned:
        return RedirectResponse(url=f"{_frontend_login_url()}?oauth_error=account_not_allowed", status_code=302)

    access = create_access_token(user.id)
    refresh = create_refresh_token(user.id)
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=int(settings.JWT_REFRESH_TOKEN_EXPIRES_SECONDS))
    db.add(RefreshToken(token=refresh, user_id=user.id, expires_at=expires_at))
    db.commit()

    fragment = urlencode(
        {
            "access_token": access,
            "refresh_token": refresh,
            "next": redirect_target,
        }
    )
    response = RedirectResponse(url=f"{_frontend_oauth_callback_url()}#{fragment}", status_code=302)
    response.delete_cookie("oauth_google_state")
    return response
