# app/services/analytics_service.py

import math
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.models import (
    EngagementKPI,
    DohaEntry,
    DictionaryEntry,
    IdiomEntry,
    ArticleEntry,
    User,
)

# -----------------------------
# Helpers
# -----------------------------

CONTENT_TABLES = {
    "doha": DohaEntry,
    "dictionary": DictionaryEntry,
    "idiom": IdiomEntry,
    "article": ArticleEntry,
}


def _log_score(v: int, s: int, l: int) -> float:
    """
    score = 1*log(views+1) + 2*log(search_hits+1) + 5*log(likes+1)
    """
    return (
        1.0 * math.log(v + 1)
        + 2.0 * math.log(s + 1)
        + 5.0 * math.log(l + 1)
    )


# =====================================================
# 1. TOP PERFORMING CONTENT
# =====================================================

def get_top_content(
    db: Session,
    content_type: str | None,
    limit: int,
    start_date: datetime,
    end_date: datetime,
) -> List[Dict[str, Any]]:
    
    # ✅ FIX: Make datetimes naive for MySQL comparison
    if start_date.tzinfo is not None:
        start_date = start_date.replace(tzinfo=None)
    if end_date.tzinfo is not None:
        end_date = end_date.replace(tzinfo=None)
    
    q = (
        db.query(
            EngagementKPI.content_type,
            EngagementKPI.content_id,
            EngagementKPI.views_count,
            EngagementKPI.search_hits_count,
            EngagementKPI.likes_count,
        )
        .filter(
            EngagementKPI.updated_at >= start_date,
            EngagementKPI.updated_at <= end_date,
        )
    )

    if content_type:
        q = q.filter(EngagementKPI.content_type == content_type)

    raw = q.all()

    scored = []
    for r in raw:
        score_val = _log_score(r.views_count, r.search_hits_count, r.likes_count)
        scored.append({
            "content_type": r.content_type,
            "content_id": r.content_id,
            "views": r.views_count,
            "likes": r.likes_count,
            "search_hits": r.search_hits_count,
            "score": round(score_val, 4)
        })

    top = sorted(scored, key=lambda x: x["score"], reverse=True)[:limit]

    # ---- Fetch preview metadata in batch ----
    by_type: dict[str, list[int]] = {}
    for r in top:
        by_type.setdefault(r["content_type"], []).append(r["content_id"])

    previews = {}

    if "doha" in by_type:
        rows = db.query(DohaEntry.id, DohaEntry.main_text).filter(
            DohaEntry.id.in_(by_type["doha"]),
            DohaEntry.is_deleted == False,
            DohaEntry.visibility == "public",
        ).all()
        previews.update({r.id: r.main_text[:100] if r.main_text else "[no text]" for r in rows})

    if "dictionary" in by_type:
        rows = db.query(DictionaryEntry.id, DictionaryEntry.lemma_devanagari).filter(
            DictionaryEntry.id.in_(by_type["dictionary"]),
            DictionaryEntry.visibility == "public",
        ).all()
        previews.update({r.id: r.lemma_devanagari or "[no lemma]" for r in rows})

    if "idiom" in by_type:
        rows = db.query(IdiomEntry.id, IdiomEntry.text_devanagari).filter(
            IdiomEntry.id.in_(by_type["idiom"]),
            IdiomEntry.visibility == "public",
        ).all()
        previews.update({r.id: r.text_devanagari or "[no text]" for r in rows})

    if "article" in by_type:
        rows = db.query(ArticleEntry.id, ArticleEntry.title).filter(
            ArticleEntry.id.in_(by_type["article"]),
            ArticleEntry.visibility == "public",
        ).all()
        previews.update({r.id: r.title or "[no title]" for r in rows})

    # ---- attach preview ----
    for r in top:
        r["title_or_text"] = previews.get(r["content_id"], "[deleted or private]")

    return top


# =====================================================
# 2. GROWTH TRENDS (CONTENT + USERS)
# =====================================================

def get_growth_trends(
    db: Session,
    start_date: datetime,
    end_date: datetime,
) -> Dict[str, Any]:
    
    # ✅ FIX: Make datetimes naive
    if start_date.tzinfo is not None:
        start_date = start_date.replace(tzinfo=None)
    if end_date.tzinfo is not None:
        end_date = end_date.replace(tzinfo=None)

    dates = []
    cursor = start_date
    while cursor <= end_date:
        dates.append(cursor.date().isoformat())
        cursor += timedelta(days=1)

    series = {}

    # --- Content growth ---
    for ctype, model in CONTENT_TABLES.items():
        q = db.query(
            func.date(model.created_at).label("day"),
            func.count(model.id),
        ).filter(
            model.created_at >= start_date,
            model.created_at <= end_date,
        )

        # apply soft-delete only if present
        if hasattr(model, "is_deleted"):
            q = q.filter(model.is_deleted == False)

        q = q.group_by("day")

        counts = {str(r[0]): r[1] for r in q.all()}
        series[ctype] = [counts.get(d, 0) for d in dates]

    # --- User registrations ---
    uq = (
        db.query(
            func.date(User.created_at).label("day"),
            func.count(User.id),
        )
        .filter(
            User.created_at >= start_date,
            User.created_at <= end_date,
        )
        .group_by("day")
    )
    user_counts = {str(r[0]): r[1] for r in uq.all()}
    series["users"] = [user_counts.get(d, 0) for d in dates]

    return {
        "dates": dates,
        "series": series,
    }


# =====================================================
# 3. DEMAND DISTRIBUTION
# =====================================================

def get_demand_distribution(db: Session) -> Dict[str, Dict[str, Any]]:

    q = (
        db.query(
            EngagementKPI.content_type,
            func.sum(EngagementKPI.search_hits_count),
        )
        .group_by(EngagementKPI.content_type)
    )

    rows = q.all()
    total = sum(r[1] or 0 for r in rows)

    out = {}
    for ctype, count in rows:
        pct = (count / total * 100) if total > 0 else 0
        out[ctype] = {
            "count": int(count or 0),
            "percent": round(pct, 2),
        }

    return out
