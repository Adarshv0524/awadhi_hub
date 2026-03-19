# app/api/v1/analytics.py

from datetime import datetime, timedelta
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from app.db.session import get_db
from app.core.security import require_role
from app.core.permissions import Role
from app.services.analytics_service import (
    get_top_content,
    get_growth_trends,
    get_demand_distribution,
)

router = APIRouter(
    prefix="/analytics",
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


# =====================================================
# TOP CONTENT
# =====================================================

@router.get("/top", response_model=List[TopContentItem])
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
    return get_top_content(db, content_type, limit, start, end)


# =====================================================
# GROWTH TRENDS
# =====================================================

@router.get("/growth", response_model=GrowthSeries)
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
    return get_growth_trends(db, start, end)


# =====================================================
# DEMAND DISTRIBUTION
# =====================================================

@router.get("/demand", response_model=Dict[str, DemandItem])
def demand_distribution(db=Depends(get_db)):
    """
    Get search demand distribution across content types.
    
    Returns count and percentage of total search hits by type.
    """
    return get_demand_distribution(db)
