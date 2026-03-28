# app/api/v1/idiom.py
from datetime import datetime
from typing import List, Optional, Literal
from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session
from sqlalchemy import and_, asc, desc

from app.db.session import get_db
from app.db.models import (
    IdiomEntry,
    EngagementKPI,
    ClassicalAuthor,
    ClassicalWork,
    WorkChapter,
)
from app.utils.text_normalize import normalize_roman

router = APIRouter(prefix="/idioms", tags=["idioms"])


# ----------------------------
# Pydantic Schemas
# ----------------------------

class IdiomOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    text_devanagari: str
    text_roman: str
    meaning: Optional[str]
    author_id: Optional[int]
    author_name: Optional[str]
    work_id: Optional[int]
    work_name: Optional[str]
    chapter_id: Optional[int]
    chapter_name: Optional[str]
    number_in_chapter: Optional[int]
    version: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    views_count: int = 0
    likes_count: int = 0
    shares_count: int = 0
    bookmarks_count: int = 0
    search_hits_count: int = 0
    weight_score: float = 0.0

def _idiom_query_with_metadata(db: Session):
    return (
        db.query(
            IdiomEntry,
            ClassicalAuthor.name.label("author_name"),
            ClassicalWork.title.label("work_name"),
            WorkChapter.title.label("chapter_name"),
            EngagementKPI.views_count.label("views_count"),
            EngagementKPI.likes_count.label("likes_count"),
            EngagementKPI.shares_count.label("shares_count"),
            EngagementKPI.bookmarks_count.label("bookmarks_count"),
            EngagementKPI.search_hits_count.label("search_hits_count"),
            EngagementKPI.weight_score.label("weight_score"),
        )
        .outerjoin(ClassicalAuthor, ClassicalAuthor.id == IdiomEntry.author_id)
        .outerjoin(ClassicalWork, ClassicalWork.id == IdiomEntry.work_id)
        .outerjoin(WorkChapter, WorkChapter.id == IdiomEntry.chapter_id)
        .outerjoin(
            EngagementKPI,
            and_(
                EngagementKPI.content_type == "idiom",
                EngagementKPI.content_id == IdiomEntry.id,
            ),
        )
    )


def _serialize_idiom_with_metadata(row) -> dict:
    (
        entry,
        author_name,
        work_name,
        chapter_name,
        views_count,
        likes_count,
        shares_count,
        bookmarks_count,
        search_hits_count,
        weight_score,
    ) = row

    return {
        "id": entry.id,
        "text_devanagari": entry.text_devanagari,
        "text_roman": entry.text_roman,
        "meaning": entry.meaning,
        "author_id": entry.author_id,
        "author_name": author_name,
        "work_id": entry.work_id,
        "work_name": work_name,
        "chapter_id": entry.chapter_id,
        "chapter_name": chapter_name,
        "number_in_chapter": entry.number_in_chapter,
        "version": entry.version,
        "created_at": entry.created_at,
        "updated_at": entry.updated_at,
        "views_count": views_count or 0,
        "likes_count": likes_count or 0,
        "shares_count": shares_count or 0,
        "bookmarks_count": bookmarks_count or 0,
        "search_hits_count": search_hits_count or 0,
        "weight_score": weight_score or 0.0,
    }


# ----------------------------
# KPI helpers
# ----------------------------

def _inc_search_kpi(db: Session, idiom_id: int):
    kpi = db.query(EngagementKPI).filter_by(
        content_type="idiom", content_id=idiom_id
    ).first()
    if not kpi:
        kpi = EngagementKPI(
            content_type="idiom",
            content_id=idiom_id,
            search_hits_count=0,
            views_count=0,
            likes_count=0,
            shares_count=0,
            weight_score=0.0,
        )
        db.add(kpi)
        db.flush()
    
    kpi.search_hits_count = (kpi.search_hits_count or 0) + 1


def _inc_view_kpi(db: Session, idiom_id: int):
    kpi = db.query(EngagementKPI).filter_by(
        content_type="idiom", content_id=idiom_id
    ).first()
    if not kpi:
        kpi = EngagementKPI(
            content_type="idiom",
            content_id=idiom_id,
            search_hits_count=0,
            views_count=0,
            likes_count=0,
            shares_count=0,
            weight_score=0.0,
        )
        db.add(kpi)
        db.flush()
    
    kpi.views_count = (kpi.views_count or 0) + 1


# ----------------------------
# Routes
# ----------------------------

@router.get("", response_model=List[IdiomOut])
def search_idioms(
    q: Optional[str] = Query(None, min_length=1),
    sort: Literal[
        "created_at",
        "updated_at",
        "views_count",
        "likes_count",
        "shares_count",
        "bookmarks_count",
        "search_hits_count",
        "weight_score",
    ] = Query("created_at"),
    order: Literal["asc", "desc"] = Query("desc"),
    db: Session = Depends(get_db),
    offset: int = 0,
    limit: int = 20,
):
    """
    Search or list idiom entries.
    - If q is provided: search by text (devanagari or roman)
    - If q is None: list all public entries (paginated)
    """
    query = _idiom_query_with_metadata(db).filter(
        IdiomEntry.visibility == "public"
    )

    if q:
        q_norm = normalize_roman(q)
        query = query.filter(
            (
                IdiomEntry.text_devanagari.ilike(f"%{q}%")
                | (IdiomEntry.text_roman_norm == q_norm)
                | IdiomEntry.text_roman_norm.ilike(f"%{q_norm}%")
            )
        )

    sort_columns = {
        "created_at": IdiomEntry.created_at,
        "updated_at": IdiomEntry.updated_at,
        "views_count": EngagementKPI.views_count,
        "likes_count": EngagementKPI.likes_count,
        "shares_count": EngagementKPI.shares_count,
        "bookmarks_count": EngagementKPI.bookmarks_count,
        "search_hits_count": EngagementKPI.search_hits_count,
        "weight_score": EngagementKPI.weight_score,
    }
    order_fn = desc if order == "desc" else asc
    results = query.order_by(order_fn(sort_columns[sort]), IdiomEntry.id.desc()).offset(offset).limit(limit).all()

    # Only increment search KPI when actually searching
    if q:
        for r in results:
            _inc_search_kpi(db, r[0].id)
        db.commit()
    
    return [_serialize_idiom_with_metadata(r) for r in results]

@router.get("/{idiom_id}", response_model=IdiomOut)
def get_idiom(idiom_id: int, db: Session = Depends(get_db)):
    row = (
        _idiom_query_with_metadata(db)
        .filter(
            IdiomEntry.id == idiom_id,
            IdiomEntry.visibility == "public",
        )
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Idiom not found")  # ✅ Fix

    _inc_view_kpi(db, row[0].id)
    db.commit()

    refreshed = (
        _idiom_query_with_metadata(db)
        .filter(
            IdiomEntry.id == idiom_id,
            IdiomEntry.visibility == "public",
        )
        .first()
    )
    return _serialize_idiom_with_metadata(refreshed)
