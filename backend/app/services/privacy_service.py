from __future__ import annotations

from typing import Any

PII_KEYS = {
    "email",
    "username",
    "ip",
    "ip_address",
    "user_agent",
    "phone",
    "address",
    "token",
    "password",
    "password_hash",
    "refresh_token",
    "access_token",
}


def redact_pii(value: Any) -> Any:
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for k, v in value.items():
            if k.lower() in PII_KEYS:
                out[k] = "[REDACTED]"
            else:
                out[k] = redact_pii(v)
        return out
    if isinstance(value, list):
        return [redact_pii(v) for v in value]
    return value


def mask_identifier(value: Any) -> Any:
    if value is None:
        return None
    text = str(value)
    if len(text) <= 4:
        return "****"
    return f"{text[:2]}***{text[-2:]}"
