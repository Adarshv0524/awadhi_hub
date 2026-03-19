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


class RateLimitAction(BaseModel):
    limit: int = Field(ge=1)
    window_seconds: int = Field(ge=1)


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
    if key in _VALIDATORS:
        validator = _VALIDATORS[key]
        try:
            if validator is int:
                if not isinstance(value, int):
                    raise ValidationError.from_exception_data("value_error", [{"type": "int_type", "loc": ("value",), "input": value}])
            elif validator is bool:
                if not isinstance(value, bool):
                    raise ValidationError.from_exception_data("value_error", [{"type": "bool_type", "loc": ("value",), "input": value}])
            elif validator is str:
                if not isinstance(value, str):
                    raise ValidationError.from_exception_data("value_error", [{"type": "str_type", "loc": ("value",), "input": value}])
            else:
                validator.model_validate(value)
        except ValidationError as e:
            raise

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
