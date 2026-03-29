from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

from sqlalchemy.orm import Session

from app.db.models import ModelGovernanceEvent, DataRetentionPolicy, AuditLog, AdminTelemetryEvent


DEFAULT_POLICIES: dict[str, int] = {
    "admin_telemetry": 180,
    "audit_log": 365,
    "model_governance": 540,
}


def append_model_event(
    db: Session,
    *,
    use_case: str,
    event_type: str,
    model_name: str,
    model_version: str,
    payload: dict[str, Any],
    recommendation_id: str | None = None,
    actor_user_id: int | None = None,
) -> str:
    rec_id = recommendation_id or str(uuid4())
    row = ModelGovernanceEvent(
        recommendation_id=rec_id,
        event_type=event_type,
        use_case=use_case,
        model_name=model_name,
        model_version=model_version,
        actor_user_id=actor_user_id,
        payload=payload,
    )
    db.add(row)
    db.flush()
    return rec_id


def score_settings_change_risk(
    db: Session,
    *,
    setting_key: str,
    old_value: Any,
    new_value: Any,
    actor_user_id: int | None,
) -> dict[str, Any]:
    now = datetime.now(timezone.utc)
    last_30d = now - timedelta(days=30)

    historical_changes = (
        db.query(AuditLog)
        .filter(
            AuditLog.action.like("setting:%"),
            AuditLog.resource_type == "system_setting",
            AuditLog.created_at >= last_30d,
        )
        .all()
    )

    historical_failures = (
        db.query(AdminTelemetryEvent)
        .filter(
            AdminTelemetryEvent.result == "failure",
            AdminTelemetryEvent.event_ts_utc >= last_30d,
        )
        .count()
    )

    magnitude = 0.0
    if isinstance(old_value, (int, float)) and isinstance(new_value, (int, float)):
        denominator = abs(float(old_value)) + 1.0
        magnitude = min(1.0, abs(float(new_value) - float(old_value)) / denominator)
    else:
        magnitude = 1.0 if str(old_value) != str(new_value) else 0.0

    blast_proxy = min(1.0, historical_failures / max(1, len(historical_changes) * 2))
    risk_score = max(0.0, min(1.0, 0.55 * magnitude + 0.45 * blast_proxy))

    rationale = [
        f"Historical failures in last 30d: {historical_failures}",
        f"Historical settings changes in last 30d: {len(historical_changes)}",
        f"Normalized magnitude delta: {round(magnitude, 3)}",
        f"Estimated blast proxy: {round(blast_proxy, 3)}",
    ]

    rec_payload = {
        "setting_key": setting_key,
        "risk_score": round(risk_score, 4),
        "rationale": rationale,
        "features": {
            "historical_failures_30d": historical_failures,
            "historical_changes_30d": len(historical_changes),
            "magnitude": magnitude,
            "blast_proxy": blast_proxy,
        },
        "input": {
            "old_value": old_value,
            "new_value": new_value,
            "actor_user_id": actor_user_id,
        },
    }

    recommendation_id = append_model_event(
        db,
        use_case="settings_risk_scoring",
        event_type="recommendation",
        model_name="settings-blast-radius-heuristic",
        model_version="v0.1.0",
        payload=rec_payload,
        actor_user_id=actor_user_id,
    )

    return {
        "recommendation_id": recommendation_id,
        "risk_score": rec_payload["risk_score"],
        "rationale": rationale,
        "features": rec_payload["features"],
    }


def moderation_triage_recommendation(submission: Any) -> tuple[float, list[str], dict[str, Any]]:
    confidence = 0.5
    reasons: list[str] = []

    text = (getattr(submission, "main_text", "") or "").strip()
    text_len = len(text)
    if text_len > 120:
        confidence += 0.15
        reasons.append("Rich textual context present")
    else:
        confidence -= 0.1
        reasons.append("Short content body")

    if getattr(submission, "is_classical", False):
        confidence += 0.05
        reasons.append("Classical context supplied")

    priority = int(getattr(submission, "priority", 0) or 0)
    confidence += min(0.2, priority * 0.05)
    reasons.append(f"Queue priority contributes +{min(0.2, priority * 0.05):.2f}")

    status = getattr(submission, "status", "")
    if status != "pending_review":
        confidence = 0.0
        reasons = ["Submission is not pending review"]

    confidence = max(0.0, min(1.0, confidence))
    explain = {
        "text_length": text_len,
        "priority": priority,
        "is_classical": bool(getattr(submission, "is_classical", False)),
        "status": status,
    }
    return confidence, reasons, explain


def ensure_retention_defaults(db: Session) -> None:
    for event_class, days in DEFAULT_POLICIES.items():
        row = db.query(DataRetentionPolicy).filter(DataRetentionPolicy.event_class == event_class).first()
        if row:
            continue
        db.add(
            DataRetentionPolicy(
                event_class=event_class,
                retention_days=days,
                delete_mode="hard",
                is_active=True,
            )
        )
    db.flush()


def run_retention_job(db: Session, now: datetime | None = None) -> dict[str, int]:
    ensure_retention_defaults(db)
    ts = now or datetime.now(timezone.utc)
    result = {"admin_telemetry_deleted": 0, "audit_log_deleted": 0, "model_governance_deleted": 0}

    policies = db.query(DataRetentionPolicy).filter(DataRetentionPolicy.is_active == True).all()
    for policy in policies:
        cutoff = ts - timedelta(days=max(1, int(policy.retention_days)))
        if policy.event_class == "admin_telemetry":
            deleted = db.query(AdminTelemetryEvent).filter(AdminTelemetryEvent.event_ts_utc < cutoff).delete()
            result["admin_telemetry_deleted"] += int(deleted or 0)
        elif policy.event_class == "audit_log":
            deleted = db.query(AuditLog).filter(AuditLog.created_at < cutoff).delete()
            result["audit_log_deleted"] += int(deleted or 0)
        elif policy.event_class == "model_governance":
            deleted = db.query(ModelGovernanceEvent).filter(ModelGovernanceEvent.created_at < cutoff).delete()
            result["model_governance_deleted"] += int(deleted or 0)

    db.commit()
    return result
