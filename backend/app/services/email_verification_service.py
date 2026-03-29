# app/services/email_verification_service.py
import random
import string
import logging
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from app.db.models import EmailVerificationToken, User
from app.auth.jwt import create_email_verification_token as create_email_verification_jwt
from app.services.email_service import send_email_verification_otp

logger = logging.getLogger(__name__)

EMAIL_VERIFICATION_TOKEN_EXPIRES_SECONDS = 900  # 15 minutes


def _utc_now_naive() -> datetime:
    """Return UTC now as timezone-naive datetime for DB portability."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def generate_otp(length: int = 6) -> str:
    """Generate a random 6-digit OTP."""
    return "".join(random.choices(string.digits, k=length))


def create_email_verification_token(
    db: Session,
    user_id: int,
    email_to_verify: str,
    expires_seconds: int = EMAIL_VERIFICATION_TOKEN_EXPIRES_SECONDS,
) -> tuple[str, str]:
    """
    Create an email verification token with OTP.
    Returns (token, otp) tuple.
    """
    otp = generate_otp()
    token = create_email_verification_jwt(user_id, expires_seconds)
    expires_at = _utc_now_naive() + timedelta(seconds=expires_seconds)

    verification = EmailVerificationToken(
        token=token,
        user_id=user_id,
        email_to_verify=email_to_verify,
        otp=otp,
        attempts=0,
        expires_at=expires_at,
    )
    db.add(verification)
    db.commit()

    return token, otp


def send_verification_otp(
    db: Session,
    user_id: int,
    email_to_verify: str,
) -> bool:
    """
    Create and send email verification OTP to user.
    Returns True if email was sent successfully.
    """
    # Check for existing active token (prevent spam)
    now_utc = _utc_now_naive()
    existing = (
        db.query(EmailVerificationToken)
        .filter(
            EmailVerificationToken.user_id == user_id,
            EmailVerificationToken.email_to_verify == email_to_verify,
            EmailVerificationToken.verified_at.is_(None),
            EmailVerificationToken.expires_at > now_utc,
        )
        .first()
    )

    if existing:
        # Delete old token and create new one
        db.delete(existing)
        db.commit()

    _, otp = create_email_verification_token(db, user_id, email_to_verify)

    # Send OTP email
    success = send_email_verification_otp(
        email_to_verify,
        otp,
        expires_minutes=int(EMAIL_VERIFICATION_TOKEN_EXPIRES_SECONDS // 60),
    )

    if not success:
        logger.warning(f"Failed to send verification OTP for user {user_id}")

    return success


def verify_email_otp(
    db: Session,
    user_id: int,
    email_to_verify: str,
    otp: str,
    max_attempts: int = 5,
) -> tuple[bool, str]:
    """
    Verify email with OTP.
    Returns (success, message) tuple.
    """
    verification = (
        db.query(EmailVerificationToken)
        .filter(
            EmailVerificationToken.user_id == user_id,
            EmailVerificationToken.email_to_verify == email_to_verify,
            EmailVerificationToken.verified_at.is_(None),
        )
        .first()
    )

    if not verification:
        return False, "No pending verification request found"

    if verification.expires_at < _utc_now_naive():
        db.delete(verification)
        db.commit()
        return False, "Verification code has expired. Please request a new one."

    if verification.attempts >= max_attempts:
        db.delete(verification)
        db.commit()
        return False, "Too many failed attempts. Please request a new code."

    if verification.otp != otp:
        verification.attempts += 1
        db.commit()
        return False, f"Invalid code. {max_attempts - verification.attempts} attempts remaining."

    # Verification successful
    verification.verified_at = _utc_now_naive()
    db.commit()

    # Update user email
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.email = email_to_verify
        user.email_verified = True
        user.pending_email = None
        db.commit()

    return True, "Email verified successfully"


def get_pending_email_verification(db: Session, user_id: int) -> str | None:
    """Get the pending email verification for a user."""
    now_utc = _utc_now_naive()
    verification = (
        db.query(EmailVerificationToken)
        .filter(
            EmailVerificationToken.user_id == user_id,
            EmailVerificationToken.verified_at.is_(None),
            EmailVerificationToken.expires_at > now_utc,
        )
        .order_by(EmailVerificationToken.created_at.desc())
        .first()
    )

    return verification.email_to_verify if verification else None
