# app/services/engagement_service.py
from typing import List
import math
import logging

from sqlalchemy.orm import Session
from sqlalchemy import select, insert, update, func, text
from sqlalchemy.exc import SQLAlchemyError

from app.db.models import EngagementKPI, DohaEntry

logger = logging.getLogger("app.engagement_service")

# top-N search hits to increment per search (Option B)
TOP_SEARCH_HITS_TO_INCREMENT = 5


def _get_or_create_kpi(db: Session, content_type: str, content_id: int) -> EngagementKPI:
    kpi = db.query(EngagementKPI).filter(
        EngagementKPI.content_type == content_type,
        EngagementKPI.content_id == content_id,
    ).with_for_update(read=False).first()
    if not kpi:
        kpi = EngagementKPI(
            content_type=content_type,
            content_id=content_id,
            views_count=0,
            search_hits_count=0,
            likes_count=0,
            bookmarks_count=0,
            shares_count=0,
        )
        db.add(kpi)
        db.flush()  # create row
    return kpi


def record_view(db: Session, content_type: str, content_id: int) -> None:
    """Increment views_count atomically"""
    # Use upsert pattern for DBs that support it; otherwise safe within transaction
    kpi = _get_or_create_kpi(db, content_type, content_id)
    kpi.views_count = (kpi.views_count or 0) + 1
    # recompute weight lazily; or compute here
    kpi.weight_score = compute_weight_score(kpi)
    db.add(kpi)
    logger.debug("Recorded view for %s/%s -> views=%s", content_type, content_id, kpi.views_count)


def record_search_hits(db: Session, content_type: str, content_id_or_ids, increment: int = 1) -> None:
    """
    Accept either a single int content_id or a list of ints.
    Performs an atomic bulk upsert compatible with MySQL (Prod) and SQLite (Tests).
    """
    # normalize input to list of ints
    if content_id_or_ids is None:
        return
    if isinstance(content_id_or_ids, (list, tuple)):
        ids = [int(x) for x in content_id_or_ids if x is not None]
        if not ids:
            return
    else:
        ids = [int(content_id_or_ids)]

    # 1. Check if we are running on SQLite (Test Mode)
    is_sqlite = "sqlite" in str(db.get_bind().url)

    if is_sqlite:
        # ---- SQLite Logic (Simulated Upsert via Loop) ----
        try:
            for cid in ids:
                # Try UPDATE first
                res = db.execute(
                    text("UPDATE engagement_kpis SET search_hits_count = search_hits_count + :inc, updated_at = CURRENT_TIMESTAMP WHERE content_type = :ct AND content_id = :cid"),
                    {"inc": increment, "ct": content_type, "cid": cid}
                )
                # If no row updated, INSERT
                if res.rowcount == 0:
                    db.execute(
                        text("INSERT INTO engagement_kpis (content_type, content_id, views_count, search_hits_count, likes_count, bookmarks_count, shares_count, weight_score, updated_at) VALUES (:ct, :cid, 0, :inc, 0, 0, 0, 0.0, CURRENT_TIMESTAMP)"),
                        {"ct": content_type, "cid": cid, "inc": increment}
                    )
            db.commit()
        except SQLAlchemyError:
            logger.exception("record_search_hits: DB error (SQLite fallback)")
            db.rollback()
            raise

    else:
        # ---- MySQL Logic (Original Bulk Upsert) ----
        # Build multi-row VALUES list and params
        values_sql_parts = []
        params = {}
        for idx, cid in enumerate(ids):
            values_sql_parts.append(f"(:ct{idx}, :cid{idx}, 0, :inc{idx}, 0, 0, 0, 0.0, NOW())")
            params[f"ct{idx}"] = content_type
            params[f"cid{idx}"] = cid
            params[f"inc{idx}"] = increment

        values_sql = ",\n".join(values_sql_parts)

        sql = text(f"""
            INSERT INTO engagement_kpis
                (content_type, content_id, views_count, search_hits_count, likes_count, bookmarks_count, shares_count, weight_score, updated_at)
            VALUES
            {values_sql}
            ON DUPLICATE KEY UPDATE
                search_hits_count = engagement_kpis.search_hits_count + VALUES(search_hits_count),
                updated_at = NOW();
        """)

        try:
            db.execute(sql, params)
            db.commit()
            logger.debug("record_search_hits: incremented search_hits for %d ids (type=%s) by %s", len(ids), content_type, increment)
        except SQLAlchemyError:
            logger.exception("record_search_hits: DB error when incrementing search hits for %s ids", len(ids))
            try:
                db.rollback()
            except Exception:
                logger.exception("record_search_hits: rollback failed")
            raise


def compute_weight_score(kpi: EngagementKPI) -> float:
    """
    weight_score =
        0.6 * log(views_count + 1)
      + 0.3 * log(search_hits_count + 1)
      + 0.1 * log(likes_count + 1)
    """
    v = kpi.views_count or 0
    s = kpi.search_hits_count or 0
    l = kpi.likes_count or 0
    score = 0.6 * math.log(v + 1) + 0.3 * math.log(s + 1) + 0.1 * math.log(l + 1)
    return float(score)


def recompute_all_kpis(db: Session, batch_limit: int = 1000):
    """
    Recompute weight_score for all KPIs in DB.
    Used by reconcile job.
    """
    q = db.query(EngagementKPI).order_by(EngagementKPI.id.asc()).limit(batch_limit).all()
    for k in q:
        k.weight_score = compute_weight_score(k)
        db.add(k)
    db.commit()
    logger.info("Recomputed %d KPI rows", len(q))
    return len(q)


def get_kpi_for_content(db: Session, content_type: str, content_id: int):
    return db.query(EngagementKPI).filter(
        EngagementKPI.content_type == content_type,
        EngagementKPI.content_id == content_id,
    ).first()


def list_popular_dohas(db: Session, limit: int = 20, offset: int = 0):
    # join doha_entries with engagement_kpis
    q = (
        db.query(DohaEntry, EngagementKPI)
        .outerjoin(
            EngagementKPI,
            (EngagementKPI.content_type == "doha") & (EngagementKPI.content_id == DohaEntry.id),
        )
        .filter(DohaEntry.is_deleted == False, DohaEntry.status == "active")
        .order_by(EngagementKPI.weight_score.desc(), DohaEntry.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    rows = q.all()
    # normalize to list of dicts
    out = []
    for doha, kpi in rows:
        out.append({
            "id": doha.id,
            "hierarchy_path": doha.hierarchy_path,
            "main_text": doha.main_text,
            "meaning": doha.meaning,
            "views": kpi.views_count if kpi else 0,
            "search_hits": kpi.search_hits_count if kpi else 0,
            "likes": kpi.likes_count if kpi else 0,
            "weight_score": float(kpi.weight_score) if kpi else 0.0,
        })
    return out