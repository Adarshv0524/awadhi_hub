import logging
import smtplib
from email.message import EmailMessage

from app.core.settings import settings

logger = logging.getLogger(__name__)


def _smtp_configured() -> bool:
    return bool(
        settings.SMTP_HOST
        and settings.SMTP_PORT
        and settings.SMTP_USERNAME
        and settings.SMTP_PASSWORD
        and settings.SMTP_FROM_EMAIL
    )


def send_password_reset_email(to_email: str, reset_link: str) -> bool:
    """Send password reset email. Returns True on success, False otherwise."""
    if not settings.SMTP_ENABLED:
        logger.info("SMTP disabled; skipping password reset email send")
        return False

    if not _smtp_configured():
        logger.warning("SMTP is enabled but configuration is incomplete")
        return False

    msg = EmailMessage()
    msg["Subject"] = "Reset your Awadhi New password"
    msg["From"] = settings.SMTP_FROM_EMAIL
    msg["To"] = to_email

    text_body = (
        "We received a request to reset your password for Awadhi New.\n\n"
        f"Reset link: {reset_link}\n\n"
        f"This link expires in {int(settings.PASSWORD_RESET_TOKEN_EXPIRES_SECONDS // 60)} minutes.\n"
        "If you did not request this, you can ignore this email."
    )

    html_body = f"""
    <html>
      <body style=\"font-family: Arial, sans-serif; line-height: 1.6; color: #111827;\">
        <h2 style=\"margin-bottom: 12px;\">Reset your Awadhi New password</h2>
        <p>We received a request to reset your password.</p>
        <p>
          <a href=\"{reset_link}\" style=\"display:inline-block;padding:10px 16px;background:#0ea5e9;color:#ffffff;text-decoration:none;border-radius:6px;\">Reset Password</a>
        </p>
        <p>If the button does not work, copy this link:</p>
        <p><a href=\"{reset_link}\">{reset_link}</a></p>
        <p style=\"margin-top: 16px; color: #6b7280;\">This link expires in {int(settings.PASSWORD_RESET_TOKEN_EXPIRES_SECONDS // 60)} minutes. If you did not request this, ignore this email.</p>
      </body>
    </html>
    """.strip()

    msg.set_content(text_body)
    msg.add_alternative(html_body, subtype="html")

    try:
        if settings.SMTP_USE_SSL:
            with smtplib.SMTP_SSL(
                settings.SMTP_HOST,
                settings.SMTP_PORT,
                timeout=settings.SMTP_TIMEOUT_SECONDS,
            ) as server:
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                server.send_message(msg)
        else:
            with smtplib.SMTP(
                settings.SMTP_HOST,
                settings.SMTP_PORT,
                timeout=settings.SMTP_TIMEOUT_SECONDS,
            ) as server:
                if settings.SMTP_USE_TLS:
                    server.starttls()
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                server.send_message(msg)

        return True
    except Exception:
        logger.exception("Failed to send password reset email")
        return False
