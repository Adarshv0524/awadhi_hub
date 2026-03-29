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
            <body style="margin:0;background:#f6f7f9;padding:28px 16px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;color:#111827;">
                <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width:560px;margin:0 auto;background:#ffffff;border:1px solid #e5e7eb;border-radius:12px;overflow:hidden;">
                    <tr>
                        <td style="padding:28px 24px 8px 24px;">
                            <div style="font-size:12px;letter-spacing:0.08em;text-transform:uppercase;color:#6b7280;">Awadhi New</div>
                            <h1 style="margin:10px 0 0 0;font-size:22px;line-height:1.3;font-weight:600;color:#111827;">Reset your password</h1>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding:8px 24px 0 24px;font-size:15px;line-height:1.7;color:#374151;">
                            We received a request to reset your password.
                        </td>
                    </tr>
                    <tr>
                        <td style="padding:20px 24px 0 24px;">
                            <a href="{reset_link}" style="display:inline-block;background:#111827;color:#ffffff;text-decoration:none;padding:11px 18px;border-radius:8px;font-size:14px;font-weight:600;">Reset Password</a>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding:18px 24px 0 24px;font-size:13px;line-height:1.6;color:#6b7280;word-break:break-all;">
                            If the button does not work, use this link:<br />
                            <a href="{reset_link}" style="color:#2563eb;text-decoration:none;">{reset_link}</a>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding:20px 24px 26px 24px;font-size:13px;line-height:1.6;color:#6b7280;">
                            This link expires in {int(settings.PASSWORD_RESET_TOKEN_EXPIRES_SECONDS // 60)} minutes. If you did not request this, you can safely ignore this email.
                        </td>
                    </tr>
                </table>
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


def send_email_verification_otp(to_email: str, otp: str, expires_minutes: int = 15) -> bool:
    """Send email verification OTP. Returns True on success, False otherwise."""
    if not settings.SMTP_ENABLED:
        logger.info("SMTP disabled; skipping email verification OTP send")
        return False

    if not _smtp_configured():
        logger.warning("SMTP is enabled but configuration is incomplete")
        return False

    msg = EmailMessage()
    msg["Subject"] = "Verify your Awadhi New email address"
    msg["From"] = settings.SMTP_FROM_EMAIL
    msg["To"] = to_email

    text_body = (
        "Welcome to Awadhi New!\n\n"
        f"Your email verification code is: {otp}\n\n"
        f"This code expires in {expires_minutes} minutes.\n"
        "If you did not request this, please ignore this email."
    )

    html_body = f"""
        <html>
            <body style="margin:0;background:#f6f7f9;padding:28px 16px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;color:#111827;">
                <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width:560px;margin:0 auto;background:#ffffff;border:1px solid #e5e7eb;border-radius:12px;overflow:hidden;">
                    <tr>
                        <td style="padding:28px 24px 8px 24px;">
                            <div style="font-size:12px;letter-spacing:0.08em;text-transform:uppercase;color:#6b7280;">Awadhi New</div>
                            <h1 style="margin:10px 0 0 0;font-size:22px;line-height:1.3;font-weight:600;color:#111827;">Verify your email</h1>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding:8px 24px 0 24px;font-size:15px;line-height:1.7;color:#374151;">
                            Use the code below to complete verification.
                        </td>
                    </tr>
                    <tr>
                        <td style="padding:18px 24px 0 24px;">
                            <div style="display:inline-block;background:#f3f4f6;border:1px solid #e5e7eb;border-radius:10px;padding:12px 16px;font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace;font-size:26px;letter-spacing:0.18em;font-weight:700;color:#111827;">
                                {otp}
                            </div>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding:20px 24px 26px 24px;font-size:13px;line-height:1.6;color:#6b7280;">
                            This code expires in {expires_minutes} minutes. If you did not request this, you can safely ignore this email.
                        </td>
                    </tr>
                </table>
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
        logger.exception("Failed to send email verification OTP")
        return False
