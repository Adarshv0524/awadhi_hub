# app/services/system_settings.py
from typing import Any, Optional, Dict
import json
import logging
from cachetools import TTLCache
from pydantic import BaseModel, Field, ValidationError
from sqlalchemy.orm import Session
from app.db.models import SystemSetting, ModerationLog
from app.core.settings import settings
from datetime import datetime, timezone
from app.services.audit_service import record_audit

logger = logging.getLogger(__name__)

_SETTINGS_CACHE = TTLCache(maxsize=1024, ttl=30)
SETTINGS_IMPORT_SCHEMA_VERSION = 1
CRITICAL_SETTING_KEYS = {
    "rate_limits",
    "ft_min_word_len",
    "prometheus_enabled",
    "enable_elasticsearch",
    "audit_log_retention_days",
    "backup_retention_days",
    "backup_s3_bucket",
    "sentry_dsn",
}


class RateLimitAction(BaseModel):
    limit: int = Field(default=60, ge=1)
    window_seconds: int = Field(default=3600, ge=1)


class RateLimitsModel(BaseModel):
    login: RateLimitAction = Field(default_factory=lambda: RateLimitAction(limit=10, window_seconds=3600))
    search: RateLimitAction = Field(default_factory=lambda: RateLimitAction(limit=120, window_seconds=60))
    submission_create: RateLimitAction = Field(default_factory=lambda: RateLimitAction(limit=20, window_seconds=86400))


_VALIDATORS = {
    "rate_limits": RateLimitsModel,
    "ft_min_word_len": int,
    "prometheus_enabled": bool,
    "sentry_dsn": str,
    "audit_log_retention_days": int,
    "backup_s3_bucket": str,
    "backup_retention_days": int,
    "enable_elasticsearch": bool,
}


def _validate_setting_value(key: str, value: Any) -> list[str]:
    errors: list[str] = []
    if key not in _VALIDATORS:
        return errors

    validator = _VALIDATORS[key]
    try:
        if validator is int:
            if not isinstance(value, int):
                errors.append("expected integer value")
        elif validator is bool:
            if not isinstance(value, bool):
                errors.append("expected boolean value")
        elif validator is str:
            if not isinstance(value, str):
                errors.append("expected string value")
        else:
            validator.model_validate(value)
    except ValidationError as e:
        errors.append(str(e))

    return errors


def validate_setting_value(key: str, value: Any) -> list[str]:
    return _validate_setting_value(key, value)


def _from_env_if_exists(key: str) -> Optional[Any]:
    env_key = key.upper().replace(".", "_")
    val = getattr(settings, env_key, None)
    if val is not None:
        return val
    import os
    if env_key in os.environ:
        raw = os.environ[env_key]
        try:
            return json.loads(raw)
        except Exception:
            return raw
    return None


def _load_all_settings_into_cache(db: Session):
    rows = db.query(SystemSetting).all()
    for r in rows:
        _SETTINGS_CACHE[r.setting_key] = r.value  # ✅ Changed from r.key


def get_setting(
    db: Session,
    key: str,
    default: Optional[Any] = None,
    allow_env_override: bool = True,
) -> Any:
    if allow_env_override:
        ev = _from_env_if_exists(key)
        if ev is not None:
            return ev

    if key in _SETTINGS_CACHE:
        return _SETTINGS_CACHE[key]

    try:
        row = db.query(SystemSetting).filter(SystemSetting.setting_key == key).first()  # ✅ Changed from .key
        if row:
            _SETTINGS_CACHE[key] = row.value
            return row.value
        _SETTINGS_CACHE[key] = default
        return default
    except Exception as e:
        logger.exception("Failed to load system setting %s", key)
        return default


def set_setting(db: Session, key: str, value: Any, actor_user_id: Optional[int] = None, metadata: Optional[Dict] = None) -> None:
    validation_errors = _validate_setting_value(key, value)
    if validation_errors:
        raise ValueError("; ".join(validation_errors))

    try:
        existing = db.query(SystemSetting).filter(SystemSetting.setting_key == key).first()  # ✅ Changed from .key
        before_val = existing.value if existing else None

        if existing:
            existing.value = value
            existing.updated_at = datetime.now(timezone.utc)
        else:
            s = SystemSetting(setting_key=key, value=value)  # ✅ Changed from key=key
            db.add(s)

        try:
            note_text = json.dumps({"key": key, "value": value}, default=str)
            ml = ModerationLog(
                submission_id=0,
                moderator_id=int(actor_user_id) if actor_user_id else 0,
                action="system_setting:update",
                from_status=None,
                to_status=None,
                guideline_version=None,
                note=note_text,
            )
            db.add(ml)
        except Exception:
            logger.exception("Failed to record moderation log for system setting change")

        try:
            audit_meta = metadata or {}
            audit_meta = audit_meta if isinstance(audit_meta, dict) else {"info": str(audit_meta)}
            record_audit(
                db=db,
                actor_user_id=actor_user_id,
                action="system_setting:update",
                resource_type="system_setting",
                resource_id=None,
                before=before_val,
                after=value,
                metadata=audit_meta,
            )
        except Exception:
            logger.exception("Failed to write audit log for system setting change")

        db.commit()
        _SETTINGS_CACHE[key] = value
    except Exception:
        db.rollback()
        logger.exception("Failed to set system setting %s", key)
        raise


def delete_setting(db: Session, key: str, actor_user_id: Optional[int] = None) -> None:
    try:
        db.query(SystemSetting).filter(SystemSetting.setting_key == key).delete()  # ✅ Changed from .key
        try:
            ml = ModerationLog(
                submission_id=0,
                moderator_id=int(actor_user_id) if actor_user_id else 0,
                action="system_setting:delete",
                from_status=None,
                to_status=None,
                guideline_version=None,
                note=json.dumps({"key": key}, default=str),
            )
            db.add(ml)
        except Exception:
            logger.exception("Failed to write moderation log for system setting delete")
        db.commit()
        if key in _SETTINGS_CACHE:
            del _SETTINGS_CACHE[key]
    except Exception:
        db.rollback()
        logger.exception("Failed to delete system setting %s", key)
        raise


def seed_defaults(db: Session):
    defaults = {
        "rate_limits": {
            "login": {"limit": 10, "window_seconds": 3600},
            "search": {"limit": 120, "window_seconds": 60},
            "submission_create": {"limit": 20, "window_seconds": 86400},
        },
        "ft_min_word_len": 2,
        "prometheus_enabled": False,
        "audit_log_retention_days": 365,
        "backup_retention_days": 90,
        "enable_elasticsearch": False,
    }
    for k, v in defaults.items():
        existing = db.query(SystemSetting).filter(SystemSetting.setting_key == k).first()  # ✅ Changed from .key
        if not existing:
            db.add(SystemSetting(setting_key=k, value=v))  # ✅ Changed from key=k
    db.commit()


def bulk_import_settings(
    db: Session,
    settings_payload: list[dict[str, Any]],
    actor_user_id: Optional[int] = None,
    metadata: Optional[Dict[str, Any]] = None,
    dry_run: bool = True,
) -> dict[str, Any]:
    existing_rows = db.query(SystemSetting).all()
    existing_map = {row.setting_key: row for row in existing_rows}

    report_items: list[dict[str, Any]] = []
    invalid_count = 0
    critical_count = 0

    for idx, item in enumerate(settings_payload):
        key = item.get("key")
        value = item.get("value")
        item_errors: list[str] = []

        if not isinstance(key, str) or not key.strip():
            item_errors.append("key must be a non-empty string")
            key = f"__invalid_key_{idx}"

        validation_errors = _validate_setting_value(key, value)
        item_errors.extend(validation_errors)

        current_row = existing_map.get(key)
        current_value = current_row.value if current_row else None
        is_critical = key in CRITICAL_SETTING_KEYS
        if is_critical:
            critical_count += 1

        if item_errors:
            invalid_count += 1
            action = "invalid"
        elif current_row is None:
            action = "create"
        elif current_value == value:
            action = "noop"
        else:
            action = "update"

        report_items.append(
            {
                "key": key,
                "action": action,
                "is_critical": is_critical,
                "errors": item_errors,
                "current_value": current_value,
                "incoming_value": value,
            }
        )

    valid_items = [it for it in report_items if not it["errors"]]
    applyable_items = [it for it in valid_items if it["action"] in {"create", "update"}]

    if dry_run:
        return {
            "summary": {
                "total": len(report_items),
                "valid": len(valid_items),
                "invalid": invalid_count,
                "critical": critical_count,
                "applyable": len(applyable_items),
            },
            "items": report_items,
            "applied": False,
        }

    if invalid_count > 0:
        raise ValueError("Validation failed for one or more settings. Apply aborted.")

    audit_meta = metadata or {}
    audit_meta = audit_meta if isinstance(audit_meta, dict) else {"info": str(audit_meta)}

    try:
        for item in applyable_items:
            key = item["key"]
            value = item["incoming_value"]
            existing = existing_map.get(key)
            before_val = existing.value if existing else None

            if existing:
                existing.value = value
                existing.updated_at = datetime.now(timezone.utc)
            else:
                new_row = SystemSetting(setting_key=key, value=value)
                db.add(new_row)
                existing_map[key] = new_row

            try:
                note_text = json.dumps({"key": key, "value": value, "bulk_import": True}, default=str)
                db.add(
                    ModerationLog(
                        submission_id=0,
                        moderator_id=int(actor_user_id) if actor_user_id else 0,
                        action="system_setting:bulk_update",
                        from_status=None,
                        to_status=None,
                        guideline_version=None,
                        note=note_text,
                    )
                )
            except Exception:
                logger.exception("Failed to write moderation log during bulk import")

            try:
                record_audit(
                    db=db,
                    actor_user_id=actor_user_id,
                    action="system_setting:bulk_update",
                    resource_type="system_setting",
                    resource_id=None,
                    before=before_val,
                    after=value,
                    metadata={**audit_meta, "bulk_import": True},
                )
            except Exception:
                logger.exception("Failed to write audit log during bulk import")

            _SETTINGS_CACHE[key] = value

        db.commit()
    except Exception:
        db.rollback()
        raise

    return {
        "summary": {
            "total": len(report_items),
            "valid": len(valid_items),
            "invalid": invalid_count,
            "critical": critical_count,
            "applyable": len(applyable_items),
        },
        "items": report_items,
        "applied": True,
    }
