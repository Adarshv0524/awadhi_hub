# app/services/interaction_service.py
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.models import UserInteraction, ShareLog, Report, EngagementKPI
from app.services.engagement_service import _get_or_create_kpi, compute_weight_score
logger = logging.getLogger("app.interaction_service")
def toggle_interaction(
    db: Session,
    user_id: int,
    content_type: str,
    content_id: int,
    interaction_type: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Toggle 'like' or 'bookmark' for user -> content.
    Returns: { "ok": True, "interaction": "like"/"bookmark", "active": bool, "<likes|bookmarks>_count": int }
    Behavior:
      - If row exists and is_active True -> set is_active False and decrement KPI.
      - If row exists and is_active False -> set is_active True and increment KPI.
      - If not exists -> create active True and increment KPI.
    """
    assert interaction_type in ("like", "bookmark"), "Invalid interaction_type"
    ui = (
        db.query(UserInteraction)
        .filter(
            UserInteraction.user_id == user_id,
            UserInteraction.content_type == content_type,
            UserInteraction.content_id == content_id,
            UserInteraction.interaction_type == interaction_type,
        )
        .with_for_update()
        .first()
    )
    created_now = False
    if ui:
        # toggle
        new_state = not bool(ui.is_active)
        ui.is_active = new_state
        ui.interaction_metadata = metadata or ui.interaction_metadata  # UPDATED
        ui.updated_at = datetime.now(timezone.utc)
        db.add(ui)
    else:
        ui = UserInteraction(
            user_id=user_id,
            content_type=content_type,
            content_id=content_id,
            interaction_type=interaction_type,
            is_active=True,
            interaction_metadata=metadata,  # UPDATED
        )
        db.add(ui)
        db.flush()
        new_state = True
        created_now = True
    # Ensure KPI exists and update counts
    kpi = _get_or_create_kpi(db, content_type, content_id)
    # decide which count to change
    if interaction_type == "like":
        if new_state:
            kpi.likes_count = (kpi.likes_count or 0) + 1
        else:
            kpi.likes_count = max(0, (kpi.likes_count or 0) - 1)
    else:  # bookmark
        if new_state:
            kpi.bookmarks_count = (kpi.bookmarks_count or 0) + 1
        else:
            kpi.bookmarks_count = max(0, (kpi.bookmarks_count or 0) - 1)
    # recompute weight_score
    kpi.weight_score = compute_weight_score(kpi)
    db.add(kpi)
    # commit is caller's responsibility (controller may commit)
    # But this function will commit to keep behaviour simple and atomic
    try:
        db.commit()
    except Exception:
        logger.exception("toggle_interaction: commit failed")
        db.rollback()
        raise
    result = {
        "ok": True,
        "interaction": interaction_type,
        "active": bool(new_state),
        "likes_count": kpi.likes_count,
        "bookmarks_count": kpi.bookmarks_count,
        "weight_score": float(kpi.weight_score),
    }
    return result
def record_share(
    db: Session,
    user_id: int,
    content_type: str,
    content_id: int,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Record an append-only share event; increments shares_count on KPI.
    Returns basic stats.
    """
    sl = ShareLog(
        user_id=user_id,
        content_type=content_type,
        content_id=content_id,
        share_metadata=metadata,  # UPDATED
    )
    db.add(sl)
    kpi = _get_or_create_kpi(db, content_type, content_id)
    kpi.shares_count = (kpi.shares_count or 0) + 1
    kpi.weight_score = compute_weight_score(kpi)
    db.add(kpi)
    try:
        db.commit()
    except Exception:
        logger.exception("record_share: commit failed")
        db.rollback()
        raise
    return {
        "ok": True,
        "shares_count": kpi.shares_count,
        "weight_score": float(kpi.weight_score),
    }
def create_report(
    db: Session,
    user_id: int,
    content_type: str,
    content_id: int,
    reason: str,
    note: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Create a report/flag row (open by default).
    """
    rpt = Report(
        user_id=user_id,
        content_type=content_type,
        content_id=content_id,
        reason=reason,
        note=note,
        report_metadata=metadata,  # UPDATED
        status="open",
    )
    db.add(rpt)
    try:
        db.commit()
    except Exception:
        logger.exception("create_report: commit failed")
        db.rollback()
        raise
    return {"ok": True, "report_id": rpt.id, "status": rpt.status}
def list_user_bookmarks(db: Session, user_id: int, limit: int = 50, offset: int = 0):
    """
    Return list of active bookmarks for a user, with preview fields:
    - content_type, content_id, created_at
    """
    q = (
        db.query(UserInteraction)
        .filter(
            UserInteraction.user_id == user_id,
            UserInteraction.interaction_type == "bookmark",
            UserInteraction.is_active == True,
        )
        .order_by(UserInteraction.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    rows = q.all()
    out = []
    for r in rows:
        out.append({
            "content_type": r.content_type,
            "content_id": r.content_id,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "metadata": r.interaction_metadata,  # UPDATED
        })
    return out