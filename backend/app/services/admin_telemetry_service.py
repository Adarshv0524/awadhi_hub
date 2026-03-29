from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.models import AdminTelemetryEvent


@dataclass
class AdminTelemetryEventData:
    event_id: str | None = None
    event_ts_utc: datetime | None = None
    session_id: str | None = None
    request_id: str | None = None
    actor_user_id: int | None = None
    actor_role: str = "unknown"
    module: str = "analytics"
    action: str = "view"
    resource_type: str | None = None
    resource_id: str | None = None
    before_state_hash: str | None = None
    after_state_hash: str | None = None
    result: str = "success"
    error_code: str | None = None
    latency_ms: float | None = None
    client_meta: dict[str, Any] | None = None


def persist_admin_telemetry_event(db: Session, event: AdminTelemetryEventData) -> AdminTelemetryEvent:
    row = AdminTelemetryEvent(
        event_id=event.event_id or str(uuid4()),
        event_ts_utc=event.event_ts_utc or datetime.now(timezone.utc),
        session_id=event.session_id,
        request_id=event.request_id,
        actor_user_id=event.actor_user_id,
        actor_role=event.actor_role or "unknown",
        module=event.module or "analytics",
        action=event.action or "view",
        resource_type=event.resource_type,
        resource_id=event.resource_id,
        before_state_hash=event.before_state_hash,
        after_state_hash=event.after_state_hash,
        result=event.result or "success",
        error_code=event.error_code,
        latency_ms=event.latency_ms,
        client_meta=event.client_meta or {},
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def _percentile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    if len(values) == 1:
        return float(values[0])

    values_sorted = sorted(values)
    rank = (len(values_sorted) - 1) * q
    low = int(rank)
    high = min(low + 1, len(values_sorted) - 1)
    weight = rank - low
    return float(values_sorted[low] * (1.0 - weight) + values_sorted[high] * weight)


def get_admin_slo_summary(db: Session, window_minutes: int = 60) -> dict[str, Any]:
    now = datetime.now(timezone.utc)
    since = now - timedelta(minutes=max(1, window_minutes))

    rows = (
        db.query(AdminTelemetryEvent)
        .filter(AdminTelemetryEvent.event_ts_utc >= since)
        .all()
    )

    total = len(rows)
    success_count = sum(1 for row in rows if (row.result or "").lower() == "success")
    failure_count = sum(1 for row in rows if (row.result or "").lower() == "failure")

    latencies = [float(row.latency_ms) for row in rows if row.latency_ms is not None]

    failure_classes: dict[str, int] = {}
    for row in rows:
        if not row.error_code:
            continue
        failure_classes[row.error_code] = failure_classes.get(row.error_code, 0) + 1

    top_failure_classes = [
        {"error_code": name, "count": count}
        for name, count in sorted(failure_classes.items(), key=lambda item: item[1], reverse=True)
    ]

    error_rate = (failure_count / total * 100.0) if total else 0.0
    action_success_rate = (success_count / total * 100.0) if total else 0.0

    return {
        "window_minutes": max(1, window_minutes),
        "total_events": total,
        "success_events": success_count,
        "failed_events": failure_count,
        "error_rate": round(error_rate, 2),
        "action_success_rate": round(action_success_rate, 2),
        "latency_ms": {
            "p50": round(_percentile(latencies, 0.50), 2),
            "p95": round(_percentile(latencies, 0.95), 2),
            "max": round(max(latencies), 2) if latencies else 0.0,
        },
        "top_failure_classes": top_failure_classes[:5],
        "generated_at": now.isoformat(),
    }


def event_completeness_ratio(db: Session, window_minutes: int = 60) -> dict[str, Any]:
    required_fields = [
        "event_id",
        "event_ts_utc",
        "actor_user_id",
        "actor_role",
        "session_id",
        "request_id",
        "module",
        "action",
        "resource_type",
        "resource_id",
        "before_state_hash",
        "after_state_hash",
        "result",
        "error_code",
        "latency_ms",
        "client_meta",
    ]

    since = datetime.now(timezone.utc) - timedelta(minutes=max(1, window_minutes))
    rows = (
        db.query(AdminTelemetryEvent)
        .filter(AdminTelemetryEvent.event_ts_utc >= since)
        .all()
    )
    if not rows:
        return {
            "window_minutes": max(1, window_minutes),
            "required_fields": required_fields,
            "events": 0,
            "completeness_percent": 100.0,
            "meets_target": True,
            "target_percent": 95.0,
        }

    total_expected = len(rows) * len(required_fields)
    completed = 0
    for row in rows:
        for field in required_fields:
            val = getattr(row, field)
            if val is None:
                continue
            if isinstance(val, str) and not val.strip():
                continue
            completed += 1

    completeness = round((completed / total_expected) * 100.0, 2)
    return {
        "window_minutes": max(1, window_minutes),
        "required_fields": required_fields,
        "events": len(rows),
        "completeness_percent": completeness,
        "meets_target": completeness >= 95.0,
        "target_percent": 95.0,
    }


def action_throughput(db: Session, start: datetime, end: datetime) -> list[dict[str, Any]]:
    q = (
        db.query(
            AdminTelemetryEvent.module,
            AdminTelemetryEvent.action,
            func.count(AdminTelemetryEvent.id).label("events"),
            func.avg(AdminTelemetryEvent.latency_ms).label("avg_latency_ms"),
        )
        .filter(AdminTelemetryEvent.event_ts_utc >= start, AdminTelemetryEvent.event_ts_utc <= end)
        .group_by(AdminTelemetryEvent.module, AdminTelemetryEvent.action)
        .order_by(func.count(AdminTelemetryEvent.id).desc())
    )
    rows = []
    for module, action, events, avg_latency in q.all():
        rows.append(
            {
                "module": module,
                "action": action,
                "events": int(events or 0),
                "avg_latency_ms": float(avg_latency or 0.0),
            }
        )
    return rows


def moderation_cycle_time_percentiles(db: Session, start: datetime, end: datetime) -> dict[str, Any]:
    rows = (
        db.query(AdminTelemetryEvent)
        .filter(
            AdminTelemetryEvent.event_ts_utc >= start,
            AdminTelemetryEvent.event_ts_utc <= end,
            AdminTelemetryEvent.module == "moderation",
            AdminTelemetryEvent.action.in_(["approve", "reject"]),
            AdminTelemetryEvent.latency_ms.isnot(None),
        )
        .all()
    )
    latencies = [float(r.latency_ms) for r in rows if r.latency_ms is not None]
    return {
        "start": start.isoformat(),
        "end": end.isoformat(),
        "count": len(latencies),
        "p50_ms": round(_percentile(latencies, 0.5), 2),
        "p90_ms": round(_percentile(latencies, 0.9), 2),
        "p95_ms": round(_percentile(latencies, 0.95), 2),
        "p99_ms": round(_percentile(latencies, 0.99), 2),
        "max_ms": round(max(latencies), 2) if latencies else 0.0,
    }


def rbac_denials_by_role_path(db: Session, start: datetime, end: datetime) -> list[dict[str, Any]]:
    role_expr = func.coalesce(AdminTelemetryEvent.actor_role, "unknown")
    path_expr = func.coalesce(AdminTelemetryEvent.resource_type, "unknown")
    rows = (
        db.query(
            role_expr.label("actor_role"),
            path_expr.label("path"),
            func.count(AdminTelemetryEvent.id).label("denials"),
        )
        .filter(
            AdminTelemetryEvent.event_ts_utc >= start,
            AdminTelemetryEvent.event_ts_utc <= end,
            AdminTelemetryEvent.result == "failure",
            AdminTelemetryEvent.error_code == "permission",
        )
        .group_by(role_expr, path_expr)
        .order_by(func.count(AdminTelemetryEvent.id).desc())
        .all()
    )
    return [
        {
            "actor_role": actor_role,
            "path": path,
            "denials": int(denials or 0),
        }
        for actor_role, path, denials in rows
    ]


def event_timeline(
    db: Session,
    start: datetime,
    end: datetime,
    module: str | None = None,
    action: str | None = None,
    result: str | None = None,
    limit: int = 200,
) -> list[dict[str, Any]]:
    q = db.query(AdminTelemetryEvent).filter(
        AdminTelemetryEvent.event_ts_utc >= start,
        AdminTelemetryEvent.event_ts_utc <= end,
    )
    if module:
        q = q.filter(AdminTelemetryEvent.module == module)
    if action:
        q = q.filter(AdminTelemetryEvent.action == action)
    if result:
        q = q.filter(AdminTelemetryEvent.result == result)

    rows = q.order_by(AdminTelemetryEvent.event_ts_utc.desc()).limit(max(1, min(limit, 1000))).all()
    return [
        {
            "event_id": r.event_id,
            "event_ts_utc": r.event_ts_utc.isoformat() if r.event_ts_utc else None,
            "actor_user_id": r.actor_user_id,
            "actor_role": r.actor_role,
            "session_id": r.session_id,
            "request_id": r.request_id,
            "module": r.module,
            "action": r.action,
            "resource_type": r.resource_type,
            "resource_id": r.resource_id,
            "result": r.result,
            "error_code": r.error_code,
            "latency_ms": r.latency_ms,
            "client_meta": r.client_meta or {},
        }
        for r in rows
    ]
