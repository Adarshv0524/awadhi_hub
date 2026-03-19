# app/services/search_service.py
from typing import List, Dict, Any, Optional
import logging

from sqlalchemy import text, or_, func
from sqlalchemy.orm import Session

# Import models
from app.db.models import DohaEntry, EngagementKPI, ClassicalAuthor, ClassicalWork, WorkChapter
from app.services.engagement_service import record_search_hits

logger = logging.getLogger("app.search_service")


def _mysql_match_query(
    q: str, 
    limit: int, 
    offset: int, 
    where_clause: str = "", 
    sort: str = "relevance"
) -> str:
    """
    Returns a raw SQL snippet for MySQL MATCH AGAINST query.
    Handles joining engagement_kpis if sort is 'popular'.
    Now includes joins with classical_authors for proper filtering.
    """
    
    # Base join with authors for filtering
    join_clause = """
        LEFT JOIN classical_authors ca ON doha_entries.author_id = ca.id
        LEFT JOIN classical_works cw ON doha_entries.work_id = cw.id
        LEFT JOIN work_chapters wc ON doha_entries.chapter_id = wc.id
    """
    
    # Add engagement join if sorting by popularity
    if sort == "popular":
        join_clause += """
        LEFT JOIN engagement_kpis ek ON doha_entries.id = ek.content_id AND ek.content_type = 'doha'
        """
        order_clause = "COALESCE(ek.weight_score, 0) DESC, relevance DESC"
    elif sort == "recent":
        order_clause = "doha_entries.created_at DESC"
    else:
        order_clause = "relevance DESC"

    sql = f"""
    SELECT
        doha_entries.id,
        doha_entries.hierarchy_path,
        doha_entries.author_id,
        doha_entries.work_id,
        doha_entries.chapter_id,
        doha_entries.number_in_chapter,
        doha_entries.main_text,
        doha_entries.meaning,
        doha_entries.text_devanagari,
        doha_entries.text_romanized,
        MATCH(doha_entries.main_text, doha_entries.meaning, doha_entries.text_devanagari, doha_entries.text_romanized) AGAINST (:q IN NATURAL LANGUAGE MODE) AS relevance
    FROM doha_entries
    {join_clause}
    WHERE doha_entries.is_deleted = 0 AND doha_entries.status = 'active'
    {where_clause}
    HAVING relevance > 0
    ORDER BY {order_clause}
    LIMIT :limit OFFSET :offset
    """
    return sql


def search_dohas(
    db: Session,
    q: Optional[str],
    author_slug: Optional[str] = None,
    work_slug: Optional[str] = None,
    chapter_slug: Optional[str] = None,
    sort: str = "relevance",
    limit: int = 20,
    offset: int = 0,
) -> Dict[str, Any]:
    
    if limit < 1:
        limit = 1
    if limit > 200:
        limit = 200

    bind = db.get_bind()
    dialect = getattr(bind.dialect, "name", None)
    results: List[Dict[str, Any]] = []
    total = 0

    # Build parameters
    params = {}

    # -------------------------------------------------------------------------
    # SCENARIO A: q is empty -> return recent/popular items (no MATCH)
    # -------------------------------------------------------------------------
    if not q:
        base = db.query(DohaEntry).filter(
            DohaEntry.is_deleted == False, 
            DohaEntry.status == "active"
        )
        
        # ✅ FIX: Use outerjoin (LEFT JOIN) instead of join (INNER JOIN)
        # This allows dohas without author_id to still be returned
        if author_slug:
            base = base.outerjoin(
                ClassicalAuthor, 
                DohaEntry.author_id == ClassicalAuthor.id
            ).filter(
                func.lower(ClassicalAuthor.slug) == author_slug.lower()
            )
        
        if work_slug:
            base = base.outerjoin(
                ClassicalWork, 
                DohaEntry.work_id == ClassicalWork.id
            ).filter(func.lower(ClassicalWork.slug) == work_slug.lower())
        
        if chapter_slug:
            base = base.outerjoin(
                WorkChapter, 
                DohaEntry.chapter_id == WorkChapter.id
            ).filter(
                func.lower(WorkChapter.slug) == chapter_slug.lower()
            )

        # Sorting logic
        if sort == "popular":
            base = base.outerjoin(
                EngagementKPI, 
                (EngagementKPI.content_id == DohaEntry.id) & 
                (EngagementKPI.content_type == "doha")
            ).order_by(EngagementKPI.weight_score.desc())
        elif sort == "recent":
            base = base.order_by(DohaEntry.created_at.desc())
        else:
            base = base.order_by(DohaEntry.id.desc())

        total = base.count()
        rows = base.offset(offset).limit(limit).all()
        
        for r in rows:
            results.append({
                "id": r.id,
                "hierarchy_path": r.hierarchy_path,
                "main_text": r.main_text,
                "meaning": r.meaning,
                "relevance_score": 0.0,
            })
        
        _record_hits_safe(db, results)
        return {"total": total, "results": results}

    # -------------------------------------------------------------------------
    # SCENARIO B: q is present -> MySQL MATCH or Fallback
    # -------------------------------------------------------------------------
    if dialect == "mysql":
        where_clause = ""
        
        # Build WHERE clause for filters using proper joins
        if author_slug:
            where_clause += " AND LOWER(ca.slug) = :author_slug"
            params["author_slug"] = author_slug.lower()
        
        if work_slug:
            where_clause += " AND LOWER(cw.slug) = :work_slug"
            params["work_slug"] = work_slug.lower()
        
        if chapter_slug:
            where_clause += " AND LOWER(wc.slug) = :chapter_slug"
            params["chapter_slug"] = chapter_slug.lower()

        sql = _mysql_match_query(q, limit, offset, where_clause=where_clause, sort=sort)
        
        params_exec = {"q": q, "limit": limit, "offset": offset, **params}

        logger.debug("Executing MySQL fulltext search SQL with sort=%s", sort)

        # Count query
        count_join = """
            LEFT JOIN classical_authors ca ON doha_entries.author_id = ca.id
            LEFT JOIN classical_works cw ON doha_entries.work_id = cw.id
            LEFT JOIN work_chapters wc ON doha_entries.chapter_id = wc.id
        """
        
        if sort == "popular":
            count_join += " LEFT JOIN engagement_kpis ek ON doha_entries.id = ek.content_id AND ek.content_type = 'doha'"

        count_sql = f"""
        SELECT COUNT(*) as total FROM (
            SELECT doha_entries.id FROM doha_entries
            {count_join}
            WHERE doha_entries.is_deleted = 0 AND doha_entries.status = 'active' {where_clause}
            AND MATCH(doha_entries.main_text, doha_entries.meaning, doha_entries.text_devanagari, doha_entries.text_romanized) 
            AGAINST (:q IN NATURAL LANGUAGE MODE)
        ) t
        """
        
        total_row = db.execute(text(count_sql), params_exec).fetchone()
        total = int(total_row[0]) if total_row is not None else 0

        rows = db.execute(text(sql), params_exec).fetchall()
        
        for r in rows:
            results.append({
                "id": r.id,  
                "hierarchy_path": r.hierarchy_path,
                "main_text": r.main_text,
                "meaning": r.meaning,
                "relevance_score": float(r.relevance) if r.relevance is not None else 0.0,
            })

    else:
        # Fallback (SQLite/Tests)
        q_like = f"%{q}%"
        base = db.query(DohaEntry).filter(
            DohaEntry.is_deleted == False, 
            DohaEntry.status == "active"
        )
        
        # ✅ FIX: Use outerjoin instead of join for filters
        if author_slug:
            base = base.outerjoin(
                ClassicalAuthor, 
                DohaEntry.author_id == ClassicalAuthor.id
            ).filter(func.lower(ClassicalAuthor.slug) == author_slug.lower())
        
        if work_slug:
            base = base.outerjoin(
                ClassicalWork, 
                DohaEntry.work_id == ClassicalWork.id
            ).filter(func.lower(ClassicalWork.slug) == work_slug.lower())
        
        if chapter_slug:
            base = base.outerjoin(
                WorkChapter, 
                DohaEntry.chapter_id == WorkChapter.id
            ).filter(func.lower(WorkChapter.slug) == chapter_slug.lower())

        # Text search
        base = base.filter(
            or_(
                func.lower(DohaEntry.main_text).like(q_like.lower()),
                func.lower(DohaEntry.meaning).like(q_like.lower()),
                func.lower(DohaEntry.text_devanagari).like(q_like.lower()),
                func.lower(DohaEntry.text_romanized).like(q_like.lower()),
            )
        )

        # Sorting
        if sort == "popular":
            base = base.outerjoin(
                EngagementKPI, 
                (EngagementKPI.content_id == DohaEntry.id) & 
                (EngagementKPI.content_type == "doha")
            ).order_by(EngagementKPI.weight_score.desc())
        elif sort == "recent":
            base = base.order_by(DohaEntry.created_at.desc())
        else:
            base = base.order_by(DohaEntry.id.desc())

        total = base.count()
        rows = base.offset(offset).limit(limit).all()
        
        for r in rows:
            results.append({
                "id": r.id,
                "hierarchy_path": r.hierarchy_path,
                "main_text": r.main_text,
                "meaning": r.meaning,
                "relevance_score": 1.0,
            })

    _record_hits_safe(db, results)
    return {"total": total, "results": results}


def _record_hits_safe(db: Session, results: List[Dict[str, Any]]):
    """
    Helper to record search hits without crashing the search request 
    if analytics fails.
    """
    if not results:
        return

    try:
        result_ids = [int(r["id"]) for r in results if r.get("id") is not None]
        if not result_ids:
            return
        record_search_hits(db, "doha", result_ids, increment=1)
    except Exception:
        logger.exception("Failed to record search hits")
