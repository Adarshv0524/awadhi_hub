# app/api/v1/analytics.py

import asyncio
from datetime import datetime, timedelta
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
import logging

logger = logging.getLogger("app.api.analytics")

router = APIRouter(
    prefix="/analytics",
    tags=["analytics"],
    dependencies=[Depends(require_role(Role.ADMIN))],
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
        end_dt = datetime.utcnow()

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


# =====================================================
# TOP CONTENT
# =====================================================

@router.get("/top", response_model=List[TopContentItem], deprecated=True)
def top_content(
    content_type: str | None = None,
    limit: int = Query(20, ge=1, le=100),
    start_date: str | None = None,
    end_date: str | None = None,
    db=Depends(get_db),
):
    """
    Get top performing content by engagement score.
    
    - **content_type**: Filter by type (doha, dictionary, idiom, article)
    - **limit**: Max results (1-100, default 20)
    - **start_date**: ISO format UTC (default: 30 days ago)
    - **end_date**: ISO format UTC (default: now)
    """
    start, end = _date_range(start_date, end_date)
    logger.warning("Deprecated endpoint hit: GET /analytics/top")
    try:
        return get_top_content(db, content_type, limit, start, end)
    except SQLAlchemyError:
        return []


# =====================================================
# GROWTH TRENDS
# =====================================================

@router.get("/growth", response_model=GrowthSeries, deprecated=True)
def growth_trends(
    start_date: str | None = None,
    end_date: str | None = None,
    db=Depends(get_db),
):
    """
    Get daily content creation and user registration trends.
    
    Returns time series data for doha, dictionary, idiom, article, and users.
    """
    start, end = _date_range(start_date, end_date)
    logger.warning("Deprecated endpoint hit: GET /analytics/growth")
    try:
        return get_growth_trends(db, start, end)
    except SQLAlchemyError:
        return GrowthSeries(dates=[], series={})


# =====================================================
# DEMAND DISTRIBUTION
# =====================================================

@router.get("/demand", response_model=Dict[str, DemandItem], deprecated=True)
def demand_distribution(db=Depends(get_db)):
    """
    Get search demand distribution across content types.
    
    Returns count and percentage of total search hits by type.
    """
    logger.warning("Deprecated endpoint hit: GET /analytics/demand")
    try:
        return get_demand_distribution(db)
    except SQLAlchemyError:
        return {}


@router.get("/summary", response_model=AnalyticsSummaryOut)
def analytics_summary(db=Depends(get_db)):
    start_of_day = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
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


@admin_router.get("/contributor-trends", deprecated=True)
def admin_contributor_trends(start_date: str | None = None, end_date: str | None = None, db=Depends(get_db)):
    logger.warning("Deprecated endpoint hit: GET /admin/analytics/contributor-trends")
    start, end = _date_range(start_date, end_date)
    try:
        return get_growth_trends(db, start, end)
    except SQLAlchemyError:
        return GrowthSeries(dates=[], series={})


@admin_router.get("/content-performance")
def admin_content_performance(limit: int = Query(20, ge=1, le=100), db=Depends(get_db)):
    end = datetime.utcnow()
    start = end - timedelta(days=30)
    try:
        return get_top_content(db, None, limit, start, end)
    except SQLAlchemyError:
        return []


@public_router.get("/leaderboard", response_model=LeaderboardOut)
def get_public_leaderboard(limit: int = Query(20, ge=1, le=100), db=Depends(get_db)):
    rows = _build_leaderboard_rows(db, limit)
    return LeaderboardOut(
        generated_at=datetime.utcnow().isoformat() + "Z",
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
