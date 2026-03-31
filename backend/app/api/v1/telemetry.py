import logging
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.permissions import Role
from app.core.security import get_current_user, require_role
from app.db.models import User
from app.db.session import get_db
from app.services.admin_telemetry_service import (
    AdminTelemetryEventData,
    event_completeness_ratio,
    get_admin_slo_summary,
    persist_admin_telemetry_event,
)


logger = logging.getLogger("app.api.telemetry")

router = APIRouter(prefix="/telemetry", tags=["telemetry"])


class RendererFallbackEventIn(BaseModel):
    event_name: str = Field(..., min_length=1)
    poetry_type: str = Field(..., min_length=1)
    chapter_id: int | None = None
    sequence_no: int = Field(..., ge=0)


class AdminAnalyticsCutoverEventIn(BaseModel):
    event_name: str = Field(..., min_length=1)
    strategy: str = Field(..., min_length=1)
    endpoint_family: str = Field(..., min_length=1)
    details: dict = Field(default_factory=dict)


class AuthPolicyEventIn(BaseModel):
    event_name: str = Field(..., min_length=1)
    route: str = Field(..., min_length=1)
    min_role: str = Field(..., min_length=1)
    decision: str = Field(..., min_length=1)
    reason: str = Field(..., min_length=1)
    status_code: int | None = None
    details: dict = Field(default_factory=dict)


class AdminTelemetryEventIn(BaseModel):
    event_id: str | None = Field(default=None, min_length=8)
    event_ts_utc: datetime | None = None
    session_id: str | None = None
    request_id: str | None = None
    module: str = Field(..., min_length=1)
    action: str = Field(..., min_length=1)
    resource_type: str | None = None
    resource_id: str | None = None
    before_state_hash: str | None = None
    after_state_hash: str | None = None
    result: str = Field(..., min_length=1)
    error_code: str | None = None
    latency_ms: float | None = Field(default=None, ge=0)
    client_meta: dict = Field(default_factory=dict)


@router.post("/renderer-fallback", status_code=202)
async def renderer_fallback_event(payload: RendererFallbackEventIn):
    logger.info(
        "renderer_fallback_event",
        extra={
            "event_name": payload.event_name,
            "poetry_type": payload.poetry_type,
            "chapter_id": payload.chapter_id,
            "sequence_no": payload.sequence_no,
        },
    )
    return {"accepted": True}


@router.post("/admin-analytics-cutover", status_code=202)
async def admin_analytics_cutover_event(payload: AdminAnalyticsCutoverEventIn):
    logger.info(
        "admin_analytics_cutover_event",
        extra={
            "event_name": payload.event_name,
            "strategy": payload.strategy,
            "endpoint_family": payload.endpoint_family,
            "details": payload.details,
        },
    )
    return {"accepted": True}


@router.post("/auth-policy", status_code=202)
async def auth_policy_event(payload: AuthPolicyEventIn):
    logger.info(
        "auth_policy_event",
        extra={
            "event_name": payload.event_name,
            "route": payload.route,
            "min_role": payload.min_role,
            "decision": payload.decision,
            "reason": payload.reason,
            "status_code": payload.status_code,
            "details": payload.details,
        },
    )
    return {"accepted": True}


@router.post("/admin-events", status_code=202, dependencies=[Depends(require_role(Role.ADMIN))])
async def ingest_admin_event(
    payload: AdminTelemetryEventIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    persist_admin_telemetry_event(
        db,
        AdminTelemetryEventData(
            event_id=payload.event_id,
            event_ts_utc=payload.event_ts_utc,
            session_id=payload.session_id,
            request_id=payload.request_id,
            actor_user_id=current_user.id,
            actor_role=current_user.role,
            module=payload.module,
            action=payload.action,
            resource_type=payload.resource_type,
            resource_id=payload.resource_id,
            before_state_hash=payload.before_state_hash,
            after_state_hash=payload.after_state_hash,
            result=payload.result,
            error_code=payload.error_code,
            latency_ms=payload.latency_ms,
            client_meta=payload.client_meta,
        ),
    )
    return {"accepted": True}


@router.get("/admin-observability/slo", dependencies=[Depends(require_role(Role.ADMIN))])
def admin_observability_slo(
    window_minutes: int = Query(60, ge=1, le=7 * 24 * 60),
    db: Session = Depends(get_db),
):
    return get_admin_slo_summary(db, window_minutes=window_minutes)


@router.get("/admin-observability/completeness", dependencies=[Depends(require_role(Role.ADMIN))])
def admin_observability_completeness(
    window_minutes: int = Query(60, ge=1, le=7 * 24 * 60),
    db: Session = Depends(get_db),
):
    return event_completeness_ratio(db, window_minutes=window_minutes)
