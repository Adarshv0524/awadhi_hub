# app/api/v1/analytics.py

import asyncio
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func

from app.db.session import get_db
from app.core.security import require_role
from app.core.permissions import Role
from app.db.models import Submission, ModerationLog, User, UserInteraction
from app.services.analytics_service import (
    get_top_content,
    get_growth_trends,
    get_demand_distribution,
)
from app.services.admin_telemetry_service import (
    action_throughput,
    moderation_cycle_time_percentiles,
    rbac_denials_by_role_path,
    event_timeline,
)
from app.db.models import AdminTelemetryEvent

router = APIRouter(
    prefix="/analytics",
    tags=["analytics"],
    dependencies=[Depends(require_role(Role.MODERATOR))],
)

public_router = APIRouter(
    prefix="/analytics",
    tags=["analytics-live"],
)

# Backward-compatible admin-prefixed analytics routes
admin_router = APIRouter(
    prefix="/admin/analytics",
    tags=["analytics"],
    dependencies=[Depends(require_role(Role.ADMIN))],
)


# =====================================================
# Pydantic Response Models
# =====================================================

class TopContentItem(BaseModel):
    content_type: str
    content_id: int
    title_or_text: str
    score: float
    views: int
    likes: int
    search_hits: int


class GrowthSeries(BaseModel):
    dates: List[str]
    series: Dict[str, List[int]]


class DemandItem(BaseModel):
    count: int
    percent: float


class AnalyticsSummaryOut(BaseModel):
    today_approved: int = 0
    pending_review: int = 0
    total_approved: int = 0


class LeaderboardEntryOut(BaseModel):
    user_id: int
    username: str
    likes_given: int = 0
    bookmarks_given: int = 0
    approved_submissions: int = 0
    score: int = 0


class LeaderboardOut(BaseModel):
    generated_at: str
    results: List[LeaderboardEntryOut]


class ActionThroughputOut(BaseModel):
    module: str
    action: str
    events: int
    avg_latency_ms: float


class ModerationLatencyOut(BaseModel):
    start: str
    end: str
    count: int
    p50_ms: float
    p90_ms: float
    p95_ms: float
    p99_ms: float
    max_ms: float


class RbacDenialOut(BaseModel):
    actor_role: str
    path: str
    denials: int


class AdminEventTrailOut(BaseModel):
    event_id: str
    event_ts_utc: str | None
    actor_user_id: int | None
    actor_role: str
    session_id: str | None
    request_id: str | None
    module: str
    action: str
    resource_type: str | None
    resource_id: str | None
    result: str
    error_code: str | None
    latency_ms: float | None
    client_meta: Dict[str, Any]


class GraphNodeOut(BaseModel):
    id: str
    category: str
    label: str
    weight: float


class GraphEdgeOut(BaseModel):
    source: str
    target: str
    value: float
    last_seen: str | None


class ForceGraph3DOut(BaseModel):
    nodes: List[GraphNodeOut]
    links: List[GraphEdgeOut]


class SurfacePointOut(BaseModel):
    endpoint: str
    bucket_ts: str
    latency_ms: float
    error_rate: float
    density: int


# ✅ FIX: Remove DemandDistribution wrapper, return plain dict


# =====================================================
# Helper
# =====================================================

def _date_range(start: str | None, end: str | None):
    """
    Parse date strings and return naive UTC datetimes.
    Default: last 30 days.
    """
    if end:
        end = end.strip()
        end_dt = datetime.fromisoformat(end)
    else:
        # ✅ Use naive UTC datetime
        end_dt = datetime.now(timezone.utc)

    if start:
        start = start.strip()
        start_dt = datetime.fromisoformat(start)
    else:
        start_dt = end_dt - timedelta(days=30)
    
    # ✅ Ensure naive datetimes (remove tzinfo if present)
    if start_dt.tzinfo is not None:
        start_dt = start_dt.replace(tzinfo=None)
    if end_dt.tzinfo is not None:
        end_dt = end_dt.replace(tzinfo=None)

    return start_dt, end_dt


def _aware_date_range(start: str | None, end: str | None):
    if end:
        end_dt = datetime.fromisoformat(end.strip())
    else:
        end_dt = datetime.now(timezone.utc)

    if start:
        start_dt = datetime.fromisoformat(start.strip())
    else:
        start_dt = end_dt - timedelta(days=30)

    if start_dt.tzinfo is None:
        start_dt = start_dt.replace(tzinfo=timezone.utc)
    if end_dt.tzinfo is None:
        end_dt = end_dt.replace(tzinfo=timezone.utc)

    return start_dt, end_dt


def _build_leaderboard_rows(db, limit: int) -> List[LeaderboardEntryOut]:
    like_counts = (
        db.query(
            UserInteraction.user_id.label("user_id"),
            func.count(UserInteraction.id).label("likes_given"),
        )
        .filter(
            UserInteraction.interaction_type == "like",
            UserInteraction.is_active == True,
        )
        .group_by(UserInteraction.user_id)
        .subquery()
    )

    bookmark_counts = (
        db.query(
            UserInteraction.user_id.label("user_id"),
            func.count(UserInteraction.id).label("bookmarks_given"),
        )
        .filter(
            UserInteraction.interaction_type == "bookmark",
            UserInteraction.is_active == True,
        )
        .group_by(UserInteraction.user_id)
        .subquery()
    )

    approved_submissions = (
        db.query(
            Submission.contributor_id.label("user_id"),
            func.count(Submission.id).label("approved_submissions"),
        )
        .filter(
            Submission.status == "approved",
            Submission.is_deleted == False,
        )
        .group_by(Submission.contributor_id)
        .subquery()
    )

    rows = (
        db.query(
            User.id,
            User.username,
            func.coalesce(like_counts.c.likes_given, 0).label("likes_given"),
            func.coalesce(bookmark_counts.c.bookmarks_given, 0).label("bookmarks_given"),
            func.coalesce(approved_submissions.c.approved_submissions, 0).label("approved_submissions"),
        )
        .outerjoin(like_counts, like_counts.c.user_id == User.id)
        .outerjoin(bookmark_counts, bookmark_counts.c.user_id == User.id)
        .outerjoin(approved_submissions, approved_submissions.c.user_id == User.id)
        .filter(User.is_active == True)
        .all()
    )

    entries: List[LeaderboardEntryOut] = []
    for row in rows:
        score = int(row.likes_given) + int(row.bookmarks_given) + (int(row.approved_submissions) * 3)
        if score == 0:
            continue
        entries.append(
            LeaderboardEntryOut(
                user_id=int(row.id),
                username=row.username or f"user-{row.id}",
                likes_given=int(row.likes_given or 0),
                bookmarks_given=int(row.bookmarks_given or 0),
                approved_submissions=int(row.approved_submissions or 0),
                score=score,
            )
        )

    entries.sort(key=lambda item: (-item.score, -item.approved_submissions, -item.likes_given, item.username))
    return entries[:limit]


@router.get("/summary", response_model=AnalyticsSummaryOut)
def analytics_summary(db=Depends(get_db)):
    start_of_day = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    try:
        today_approved = (
            db.query(func.count(ModerationLog.id))
            .filter(
                ModerationLog.action.like("approve%"),
                ModerationLog.created_at >= start_of_day,
            )
            .scalar()
            or 0
        )
        pending_review = (
            db.query(func.count(Submission.id))
            .filter(
                Submission.status == "pending_review",
                Submission.is_deleted == False,
            )
            .scalar()
            or 0
        )
        total_approved = (
            db.query(func.count(Submission.id))
            .filter(
                Submission.status == "approved",
                Submission.is_deleted == False,
            )
            .scalar()
            or 0
        )
        return AnalyticsSummaryOut(
            today_approved=int(today_approved),
            pending_review=int(pending_review),
            total_approved=int(total_approved),
        )
    except SQLAlchemyError:
        return AnalyticsSummaryOut(today_approved=0, pending_review=0, total_approved=0)


@admin_router.get("/summary", response_model=AnalyticsSummaryOut)
def admin_analytics_summary(db=Depends(get_db)):
    return analytics_summary(db)


@admin_router.get("/v2/summary", response_model=AnalyticsSummaryOut)
def admin_analytics_summary_v2(db=Depends(get_db)):
    return analytics_summary(db)


@admin_router.get("/v2/top", response_model=List[TopContentItem])
def admin_top_content_v2(
    content_type: str | None = None,
    limit: int = Query(20, ge=1, le=100),
    start_date: str | None = None,
    end_date: str | None = None,
    db=Depends(get_db),
):
    start, end = _date_range(start_date, end_date)
    try:
        return get_top_content(db, content_type, limit, start, end)
    except SQLAlchemyError:
        return []


@admin_router.get("/v2/growth", response_model=GrowthSeries)
def admin_growth_trends_v2(
    start_date: str | None = None,
    end_date: str | None = None,
    db=Depends(get_db),
):
    start, end = _date_range(start_date, end_date)
    try:
        return get_growth_trends(db, start, end)
    except SQLAlchemyError:
        return GrowthSeries(dates=[], series={})


@admin_router.get("/v2/demand", response_model=Dict[str, DemandItem])
def admin_demand_distribution_v2(db=Depends(get_db)):
    try:
        return get_demand_distribution(db)
    except SQLAlchemyError:
        return {}


@admin_router.get("/v2/action-throughput", response_model=List[ActionThroughputOut])
def admin_action_throughput_v2(
    start_date: str | None = None,
    end_date: str | None = None,
    db=Depends(get_db),
):
    start, end = _aware_date_range(start_date, end_date)
    try:
        return action_throughput(db, start, end)
    except SQLAlchemyError:
        return []


@admin_router.get("/v2/moderation-cycle-time", response_model=ModerationLatencyOut)
def admin_moderation_cycle_time_v2(
    start_date: str | None = None,
    end_date: str | None = None,
    db=Depends(get_db),
):
    start, end = _aware_date_range(start_date, end_date)
    try:
        return moderation_cycle_time_percentiles(db, start, end)
    except SQLAlchemyError:
        return ModerationLatencyOut(
            start=start.isoformat(),
            end=end.isoformat(),
            count=0,
            p50_ms=0,
            p90_ms=0,
            p95_ms=0,
            p99_ms=0,
            max_ms=0,
        )


@admin_router.get("/v2/rbac-denials", response_model=List[RbacDenialOut])
def admin_rbac_denials_v2(
    start_date: str | None = None,
    end_date: str | None = None,
    db=Depends(get_db),
):
    start, end = _aware_date_range(start_date, end_date)
    try:
        return rbac_denials_by_role_path(db, start, end)
    except SQLAlchemyError:
        return []


@admin_router.get("/v2/events", response_model=List[AdminEventTrailOut])
def admin_event_trail_v2(
    start_date: str | None = None,
    end_date: str | None = None,
    module: str | None = None,
    action: str | None = None,
    result: str | None = None,
    limit: int = Query(200, ge=1, le=1000),
    db=Depends(get_db),
):
    start, end = _aware_date_range(start_date, end_date)
    try:
        return event_timeline(db, start, end, module=module, action=action, result=result, limit=limit)
    except SQLAlchemyError:
        return []


@admin_router.get("/v2/3d/actor-resource-graph", response_model=ForceGraph3DOut)
def admin_actor_resource_force_graph_v2(
    start_date: str | None = None,
    end_date: str | None = None,
    db=Depends(get_db),
):
    start, end = _aware_date_range(start_date, end_date)
    rows = (
        db.query(AdminTelemetryEvent)
        .filter(
            AdminTelemetryEvent.event_ts_utc >= start,
            AdminTelemetryEvent.event_ts_utc <= end,
            AdminTelemetryEvent.actor_user_id.isnot(None),
            AdminTelemetryEvent.resource_type.isnot(None),
        )
        .limit(8000)
        .all()
    )

    actor_weights: dict[str, float] = {}
    resource_weights: dict[str, float] = {}
    edge_weights: dict[tuple[str, str], dict[str, Any]] = {}

    for row in rows:
        actor_id = f"actor:{row.actor_user_id}"
        resource_id = f"resource:{row.resource_type}:{row.resource_id or '-'}"
        actor_weights[actor_id] = actor_weights.get(actor_id, 0.0) + 1.0
        resource_weights[resource_id] = resource_weights.get(resource_id, 0.0) + 1.0

        key = (actor_id, resource_id)
        if key not in edge_weights:
            edge_weights[key] = {"value": 0.0, "last_seen": None}
        edge_weights[key]["value"] += 1.0
        ts = row.event_ts_utc.isoformat() if row.event_ts_utc else None
        edge_weights[key]["last_seen"] = max(edge_weights[key]["last_seen"], ts) if edge_weights[key]["last_seen"] else ts

    nodes = [
        GraphNodeOut(id=node_id, category="actor", label=node_id.replace("actor:", ""), weight=weight)
        for node_id, weight in actor_weights.items()
    ]
    nodes.extend(
        GraphNodeOut(id=node_id, category="resource", label=node_id.replace("resource:", ""), weight=weight)
        for node_id, weight in resource_weights.items()
    )

    links = [
        GraphEdgeOut(source=src, target=dst, value=meta["value"], last_seen=meta["last_seen"])
        for (src, dst), meta in edge_weights.items()
    ]
    return ForceGraph3DOut(nodes=nodes, links=links)


@admin_router.get("/v2/3d/latency-error-surface", response_model=List[SurfacePointOut])
def admin_latency_error_surface_v2(
    start_date: str | None = None,
    end_date: str | None = None,
    bucket_minutes: int = Query(30, ge=5, le=240),
    db=Depends(get_db),
):
    start, end = _aware_date_range(start_date, end_date)
    rows = (
        db.query(AdminTelemetryEvent)
        .filter(AdminTelemetryEvent.event_ts_utc >= start, AdminTelemetryEvent.event_ts_utc <= end)
        .limit(12000)
        .all()
    )

    agg: dict[tuple[str, str], dict[str, float]] = {}
    for row in rows:
        path = row.resource_type or "unknown"
        ts = row.event_ts_utc or start
        bucket_start = ts.replace(minute=(ts.minute // bucket_minutes) * bucket_minutes, second=0, microsecond=0)
        bucket_key = bucket_start.isoformat()
        key = (path, bucket_key)
        if key not in agg:
            agg[key] = {"latency_sum": 0.0, "errors": 0.0, "count": 0.0}
        agg[key]["count"] += 1.0
        agg[key]["latency_sum"] += float(row.latency_ms or 0.0)
        if (row.result or "").lower() == "failure":
            agg[key]["errors"] += 1.0

    out: list[SurfacePointOut] = []
    for (endpoint, bucket_ts), v in agg.items():
        count = int(v["count"])
        out.append(
            SurfacePointOut(
                endpoint=endpoint,
                bucket_ts=bucket_ts,
                latency_ms=round(v["latency_sum"] / max(1, count), 3),
                error_rate=round((v["errors"] / max(1, count)) * 100.0, 3),
                density=count,
            )
        )
    return out


@public_router.get("/leaderboard", response_model=LeaderboardOut)
def get_public_leaderboard(limit: int = Query(20, ge=1, le=100), db=Depends(get_db)):
    rows = _build_leaderboard_rows(db, limit)
    return LeaderboardOut(
        generated_at=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        results=rows,
    )


@public_router.websocket("/ws/leaderboard")
async def leaderboard_websocket(websocket: WebSocket):
    await websocket.accept()
    db_gen = get_db()
    db = next(db_gen)
    last_payload: Dict[str, Any] | None = None
    try:
        while True:
            rows = _build_leaderboard_rows(db, limit=20)
            payload = {
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "results": [entry.model_dump() for entry in rows],
            }
            if payload != last_payload:
                await websocket.send_json(payload)
                last_payload = payload
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        return
    finally:
        db.close()
