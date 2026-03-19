# app/services/audit_service.py
import logging
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.db.models import AuditLog

logger = logging.getLogger(__name__)

# keys to redact in before/after payloads
_DEFAULT_REDACT_KEYS = {"password", "password_hash", "refresh_token", "access_token", "jwt_secret", "sentry_dsn", "secret", "api_key"}

def _redact(obj: Optional[Dict[str, Any]], redact_keys=_DEFAULT_REDACT_KEYS) -> Optional[Dict[str, Any]]:
    if obj is None:
        return None
    try:
        # shallow redact: if dict, copy and redact keys; nested fields with those keys will also be replaced if present at top-level
        if isinstance(obj, dict):
            out = {}
            for k, v in obj.items():
                if k.lower() in redact_keys:
                    out[k] = "[REDACTED]"
                else:
                    # do not deep-copy large nested structures to avoid heavy processing; keep them as-is
                    out[k] = v
            return out
        else:
            # not a dict — return as-is
            return obj
    except Exception as e:
        logger.exception("Failed to redact audit payload")
        return None

def record_audit(
    db: Session,
    actor_user_id: Optional[int],
    action: str,
    resource_type: Optional[str] = None,
    resource_id: Optional[int] = None,
    before: Optional[Dict[str, Any]] = None,
    after: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> AuditLog:
    """
    Record an audit row synchronously inside the provided DB session.
    Note: This function DOES NOT commit. It adds the AuditLog instance and flushes, so that it is
    persisted in the current transaction and will be committed by the caller.
    """
    try:
        red_before = _redact(before)
        red_after = _redact(after)
        # ensure metadata keys are basic types (e.g., ip_address, user_agent, request_id)
        meta = metadata or {}
        if not isinstance(meta, dict):
            # try convert to dict
            meta = {"value": str(meta)}

        audit = AuditLog(
            actor_user_id=int(actor_user_id) if actor_user_id is not None else None,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            audit_before=red_before,
            after=red_after,
            audit_metadata=meta,
            # created_at will be server default; set explicitly for SQLite tests
            created_at=datetime.now(timezone.utc),
        )
        db.add(audit)
        # flush so id is available and row is in DB in same txn
        db.flush()
        return audit
    except Exception:
        logger.exception("Failed to record audit log")
        # do not raise to avoid blocking main transaction; caller can decide
        raise
