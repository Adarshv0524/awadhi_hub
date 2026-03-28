# app/api/v1/dictionary.py
from datetime import datetime
from typing import List, Optional, Literal
from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session
from sqlalchemy import and_, asc, desc

from app.db.session import get_db
from app.db.models import (
    DictionaryEntry,
    EngagementKPI,
    ClassicalAuthor,
    ClassicalWork,
    WorkChapter,
)
from app.utils.text_normalize import normalize_roman

router = APIRouter(prefix="/dictionary", tags=["dictionary"])


# ----------------------------
# Pydantic Schemas
# ----------------------------

class DictionaryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    lemma_devanagari: str
    lemma_roman: Optional[str]
    language: str
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

class DictionaryDetailOut(DictionaryOut):
    senses: list
    pronunciation: Optional[str]
    examples: Optional[list]


def _dictionary_query_with_metadata(db: Session):
    return (
        db.query(
            DictionaryEntry,
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
        .outerjoin(ClassicalAuthor, ClassicalAuthor.id == DictionaryEntry.author_id)
        .outerjoin(ClassicalWork, ClassicalWork.id == DictionaryEntry.work_id)
        .outerjoin(WorkChapter, WorkChapter.id == DictionaryEntry.chapter_id)
        .outerjoin(
            EngagementKPI,
            and_(
                EngagementKPI.content_type == "dictionary",
                EngagementKPI.content_id == DictionaryEntry.id,
            ),
        )
    )


def _serialize_dictionary_with_metadata(row) -> dict:
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
        "lemma_devanagari": entry.lemma_devanagari,
        "lemma_roman": entry.lemma_roman,
        "language": entry.language,
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
        "senses": entry.senses,
        "pronunciation": entry.pronunciation,
        "examples": entry.examples,
        "views_count": views_count or 0,
        "likes_count": likes_count or 0,
        "shares_count": shares_count or 0,
        "bookmarks_count": bookmarks_count or 0,
        "search_hits_count": search_hits_count or 0,
        "weight_score": weight_score or 0.0,
    }


# ----------------------------
# Helpers
# ----------------------------

def _inc_search_kpi(db: Session, entry_id: int):
    kpi = (
        db.query(EngagementKPI)
        .filter_by(content_type="dictionary", content_id=entry_id)
        .first()
    )
    if not kpi:
        kpi = EngagementKPI(
            content_type="dictionary",
            content_id=entry_id,
            search_hits_count=0,  # ✅ Explicit init
            views_count=0,
            likes_count=0,
            shares_count=0,
            weight_score=0.0,
        )
        db.add(kpi)
        db.flush()  # ✅ Ensure kpi.id is set before incrementing
    
    # ✅ Handle None safely
    kpi.search_hits_count = (kpi.search_hits_count or 0) + 1


def _inc_view_kpi(db: Session, entry_id: int):
    kpi = (
        db.query(EngagementKPI)
        .filter_by(content_type="dictionary", content_id=entry_id)
        .first()
    )
    if not kpi:
        kpi = EngagementKPI(
            content_type="dictionary",
            content_id=entry_id,
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

@router.get("", response_model=List[DictionaryOut])
def search_dictionary(
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
    Search or list dictionary entries.
    - If q is provided: search by lemma (devanagari or roman)
    - If q is None: list all public entries (paginated)
    """
    query = _dictionary_query_with_metadata(db).filter(
        DictionaryEntry.visibility == "public"
    )

    if q:
        q_norm = normalize_roman(q)
        query = query.filter(
            (
                DictionaryEntry.lemma_devanagari.ilike(f"%{q}%")
                | (DictionaryEntry.lemma_roman_norm == q_norm)
                | DictionaryEntry.lemma_roman_norm.ilike(f"%{q_norm}%")
            )
        )

    sort_columns = {
        "created_at": DictionaryEntry.created_at,
        "updated_at": DictionaryEntry.updated_at,
        "views_count": EngagementKPI.views_count,
        "likes_count": EngagementKPI.likes_count,
        "shares_count": EngagementKPI.shares_count,
        "bookmarks_count": EngagementKPI.bookmarks_count,
        "search_hits_count": EngagementKPI.search_hits_count,
        "weight_score": EngagementKPI.weight_score,
    }
    order_fn = desc if order == "desc" else asc
    results = query.order_by(order_fn(sort_columns[sort]), DictionaryEntry.id.desc()).offset(offset).limit(limit).all()

    # Only increment search KPI when actually searching (q provided)
    if q:
        for r in results:
            _inc_search_kpi(db, r[0].id)
        db.commit()
    
    return [_serialize_dictionary_with_metadata(r) for r in results]

@router.get("/{entry_id}", response_model=DictionaryDetailOut)
def get_dictionary_entry(entry_id: int, db: Session = Depends(get_db)):
    row = (
        _dictionary_query_with_metadata(db)
        .filter(
            DictionaryEntry.id == entry_id,
            DictionaryEntry.visibility == "public",
        )
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Dictionary entry not found")  # ✅ Fix

    _inc_view_kpi(db, row[0].id)
    db.commit()

    refreshed = (
        _dictionary_query_with_metadata(db)
        .filter(
            DictionaryEntry.id == entry_id,
            DictionaryEntry.visibility == "public",
        )
        .first()
    )
    return _serialize_dictionary_with_metadata(refreshed)

