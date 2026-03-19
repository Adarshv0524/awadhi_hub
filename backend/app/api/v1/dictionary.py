# app/api/v1/dictionary.py
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import DictionaryEntry, EngagementKPI
from app.utils.text_normalize import normalize_roman

router = APIRouter(prefix="/dictionary", tags=["dictionary"])


# ----------------------------
# Pydantic Schemas
# ----------------------------

class DictionaryOut(BaseModel):
    id: int
    lemma_devanagari: str
    lemma_roman: Optional[str]
    language: str
    version: int

    class Config:
        orm_mode = True


class DictionaryDetailOut(DictionaryOut):
    senses: list
    pronunciation: Optional[str]
    examples: Optional[list]


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
    q: Optional[str] = Query(None, min_length=1),  # ← Make optional
    db: Session = Depends(get_db),
    offset: int = 0,
    limit: int = 20,
):
    """
    Search or list dictionary entries.
    - If q is provided: search by lemma (devanagari or roman)
    - If q is None: list all public entries (paginated)
    """
    query = db.query(DictionaryEntry).filter(
        DictionaryEntry.visibility == "public"
    )
    
    # Apply search filter only if q is provided
    if q:
        q_norm = normalize_roman(q)
        query = query.filter(
            (
                DictionaryEntry.lemma_devanagari.ilike(f"%{q}%")
                | (DictionaryEntry.lemma_roman_norm == q_norm)
                | DictionaryEntry.lemma_roman_norm.ilike(f"%{q_norm}%")
            )
        )
    
    results = query.order_by(DictionaryEntry.id.asc()).offset(offset).limit(limit).all()

    # Only increment search KPI when actually searching (q provided)
    if q:
        for r in results:
            _inc_search_kpi(db, r.id)
        db.commit()
    
    return results

@router.get("/{entry_id}", response_model=DictionaryDetailOut)
def get_dictionary_entry(entry_id: int, db: Session = Depends(get_db)):
    entry = (
        db.query(DictionaryEntry)
        .filter(
            DictionaryEntry.id == entry_id,
            DictionaryEntry.visibility == "public",
        )
        .first()
    )
    if not entry:
        raise HTTPException(status_code=404, detail="Dictionary entry not found")  # ✅ Fix

    _inc_view_kpi(db, entry.id)
    db.commit()
    return entry

