# app/services/interaction_service.py
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.db.models import (
    UserInteraction,
    ShareLog,
    Report,
    User,
    EngagementKPI,
    DohaEntry,
    DictionaryEntry,
    IdiomEntry,
    ArticleEntry,
    PoetryNode,
    ClassicalAuthor,
    ClassicalWork,
    WorkChapter,
)
from app.services.engagement_service import _get_or_create_kpi, compute_weight_score
logger = logging.getLogger("app.interaction_service")


def _build_content_preview(db: Session, content_type: str, content_id: int) -> Dict[str, Any]:
    if content_type == "doha":
        row = db.query(DohaEntry).filter(DohaEntry.id == content_id, DohaEntry.is_deleted == False).first()
        if not row:
            return {"content_title": f"doha #{content_id}", "content_snippet": None}
        text = (row.main_text or "").strip()
        return {
            "content_title": text[:80] if text else f"doha #{content_id}",
            "content_snippet": text[:180] if text else None,
        }

    if content_type == "dictionary":
        row = db.query(DictionaryEntry).filter(DictionaryEntry.id == content_id).first()
        if not row:
            return {"content_title": f"dictionary #{content_id}", "content_snippet": None}
        lemma = (row.lemma_devanagari or row.lemma_roman or "").strip()
        first_def = None
        if isinstance(row.senses, list) and row.senses:
            first = row.senses[0] or {}
            if isinstance(first, dict):
                first_def = first.get("definition")
        return {
            "content_title": lemma or f"dictionary #{content_id}",
            "content_snippet": first_def,
        }

    if content_type == "idiom":
        row = db.query(IdiomEntry).filter(IdiomEntry.id == content_id).first()
        if not row:
            return {"content_title": f"idiom #{content_id}", "content_snippet": None}
        text = (row.text_devanagari or row.text_roman or "").strip()
        return {
            "content_title": text or f"idiom #{content_id}",
            "content_snippet": row.meaning,
        }

    if content_type == "article":
        row = db.query(ArticleEntry).filter(ArticleEntry.id == content_id).first()
        if not row:
            return {"content_title": f"article #{content_id}", "content_snippet": None}
        return {
            "content_title": row.title or f"article #{content_id}",
            "content_snippet": row.excerpt or (row.body[:180] if row.body else None),
        }

    row = (
        db.query(PoetryNode, ClassicalAuthor.slug, ClassicalWork.slug, WorkChapter.slug)
        .join(ClassicalAuthor, ClassicalAuthor.id == PoetryNode.author_id)
        .join(ClassicalWork, ClassicalWork.id == PoetryNode.work_id)
        .join(WorkChapter, WorkChapter.id == PoetryNode.chapter_id)
        .filter(
            PoetryNode.id == content_id,
            PoetryNode.poetry_type == content_type,
            PoetryNode.is_deleted == False,
        )
        .first()
    )
    if row:
        node, author_slug, work_slug, chapter_slug = row
        return {
            "content_title": (node.main_text or f"{content_type} #{content_id}")[:80],
            "content_snippet": node.meaning or node.main_text,
            "content_path": f"/{author_slug}/{work_slug}/{chapter_slug}",
        }

    return {"content_title": f"{content_type} #{content_id}", "content_snippet": None}


def list_user_interactions(
    db: Session,
    user_id: int,
    interaction_type: str,
    limit: int = 50,
    offset: int = 0,
) -> Dict[str, Any]:
    filters = (
        UserInteraction.user_id == user_id,
        UserInteraction.interaction_type == interaction_type,
        UserInteraction.is_active == True,
    )

    total_count = db.query(func.count(UserInteraction.id)).filter(*filters).scalar() or 0

    rows = (
        db.query(
            UserInteraction.id.label("id"),
            UserInteraction.content_type.label("content_type"),
            UserInteraction.content_id.label("content_id"),
            UserInteraction.created_at.label("created_at"),
            UserInteraction.updated_at.label("updated_at"),
            UserInteraction.interaction_metadata.label("metadata"),
            DohaEntry.main_text.label("doha_text"),
            DohaEntry.meaning.label("doha_meaning"),
            DictionaryEntry.lemma_devanagari.label("dict_lemma_devanagari"),
            DictionaryEntry.lemma_roman.label("dict_lemma_roman"),
            IdiomEntry.text_devanagari.label("idiom_text_devanagari"),
            IdiomEntry.text_roman.label("idiom_text_roman"),
            IdiomEntry.meaning.label("idiom_meaning"),
            ArticleEntry.title.label("article_title"),
            ArticleEntry.excerpt.label("article_excerpt"),
            ArticleEntry.body.label("article_body"),
            PoetryNode.main_text.label("poetry_main_text"),
            PoetryNode.meaning.label("poetry_meaning"),
            ClassicalAuthor.slug.label("poetry_author_slug"),
            ClassicalWork.slug.label("poetry_work_slug"),
            WorkChapter.slug.label("poetry_chapter_slug"),
        )
        .outerjoin(
            DohaEntry,
            and_(
                UserInteraction.content_type == "doha",
                UserInteraction.content_id == DohaEntry.id,
                DohaEntry.is_deleted == False,
            ),
        )
        .outerjoin(
            DictionaryEntry,
            and_(
                UserInteraction.content_type == "dictionary",
                UserInteraction.content_id == DictionaryEntry.id,
            ),
        )
        .outerjoin(
            IdiomEntry,
            and_(
                UserInteraction.content_type == "idiom",
                UserInteraction.content_id == IdiomEntry.id,
            ),
        )
        .outerjoin(
            ArticleEntry,
            and_(
                UserInteraction.content_type == "article",
                UserInteraction.content_id == ArticleEntry.id,
            ),
        )
        .outerjoin(
            PoetryNode,
            and_(
                UserInteraction.content_id == PoetryNode.id,
                UserInteraction.content_type == PoetryNode.poetry_type,
                PoetryNode.is_deleted == False,
            ),
        )
        .outerjoin(
            ClassicalAuthor,
            PoetryNode.author_id == ClassicalAuthor.id,
        )
        .outerjoin(
            ClassicalWork,
            PoetryNode.work_id == ClassicalWork.id,
        )
        .outerjoin(
            WorkChapter,
            PoetryNode.chapter_id == WorkChapter.id,
        )
        .filter(*filters)
        .order_by(UserInteraction.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    results = []
    for r in rows:
        if r.content_type == "doha":
            title = (r.doha_text or "").strip() or f"doha #{r.content_id}"
            snippet = (r.doha_meaning or r.doha_text or None)
        elif r.content_type == "dictionary":
            title = (r.dict_lemma_devanagari or r.dict_lemma_roman or "").strip() or f"dictionary #{r.content_id}"
            snippet = None
        elif r.content_type == "idiom":
            title = (r.idiom_text_devanagari or r.idiom_text_roman or "").strip() or f"idiom #{r.content_id}"
            snippet = r.idiom_meaning
        elif r.content_type == "article":
            title = (r.article_title or "").strip() or f"article #{r.content_id}"
            snippet = r.article_excerpt or ((r.article_body or "")[:180] if r.article_body else None)
        else:
            title = (r.poetry_main_text or "").strip() or f"{r.content_type} #{r.content_id}"
            snippet = r.poetry_meaning or r.poetry_main_text or None

        content_path = None
        if r.poetry_author_slug and r.poetry_work_slug and r.poetry_chapter_slug:
            content_path = f"/{r.poetry_author_slug}/{r.poetry_work_slug}/{r.poetry_chapter_slug}"

        results.append(
            {
                "id": r.id,
                "content_type": r.content_type,
                "content_id": r.content_id,
                "created_at": r.created_at,
                "updated_at": r.updated_at,
                "metadata": r.metadata,
                "content_title": title,
                "content_snippet": snippet,
                "content_path": content_path,
            }
        )

    return {
        "total_count": total_count,
        "results": results,
    }
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


def list_reports_for_moderation(
    db: Session,
    status: Optional[str] = None,
    content_type: Optional[str] = None,
    reason: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> Dict[str, Any]:
    q = (
        db.query(
            Report.id,
            Report.user_id,
            User.username,
            User.email,
            Report.content_type,
            Report.content_id,
            Report.reason,
            Report.note,
            Report.status,
            Report.report_metadata,
            Report.created_at,
            Report.updated_at,
        )
        .outerjoin(User, User.id == Report.user_id)
    )

    if status:
        q = q.filter(Report.status == status)
    if content_type:
        q = q.filter(Report.content_type == content_type)
    if reason:
        q = q.filter(Report.reason == reason)

    total_count = q.with_entities(func.count(Report.id)).scalar() or 0

    rows = (
        q.order_by(Report.created_at.desc(), Report.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    results = []
    for r in rows:
        preview = _build_content_preview(db, str(r.content_type), int(r.content_id))
        results.append(
            {
                "id": int(r.id),
                "user_id": int(r.user_id),
                "reporter_username": r.username,
                "reporter_email": r.email,
                "content_type": str(r.content_type),
                "content_id": int(r.content_id),
                "reason": str(r.reason),
                "note": r.note,
                "status": str(r.status),
                "metadata": r.report_metadata,
                "created_at": r.created_at,
                "updated_at": r.updated_at,
                "content_title": preview.get("content_title"),
                "content_snippet": preview.get("content_snippet"),
                "content_path": preview.get("content_path"),
            }
        )

    return {
        "total_count": int(total_count),
        "results": results,
    }


def list_user_bookmarks(db: Session, user_id: int, limit: int = 50, offset: int = 0):
    return list_user_interactions(
        db=db,
        user_id=user_id,
        interaction_type="bookmark",
        limit=limit,
        offset=offset,
    )


def list_user_likes(db: Session, user_id: int, limit: int = 50, offset: int = 0):
    return list_user_interactions(
        db=db,
        user_id=user_id,
        interaction_type="like",
        limit=limit,
        offset=offset,
    )