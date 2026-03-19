# app/api/v1/idiom.py
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import IdiomEntry, EngagementKPI
from app.utils.text_normalize import normalize_roman

router = APIRouter(prefix="/idioms", tags=["idioms"])


# ----------------------------
# Pydantic Schemas
# ----------------------------

class IdiomOut(BaseModel):
    id: int
    text_devanagari: str
    text_roman: str
    meaning: Optional[str]
    version: int

    class Config:
        orm_mode = True


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
    q: Optional[str] = Query(None, min_length=1),  # ← Make optional
    db: Session = Depends(get_db),
    offset: int = 0,
    limit: int = 20,
):
    """
    Search or list idiom entries.
    - If q is provided: search by text (devanagari or roman)
    - If q is None: list all public entries (paginated)
    """
    query = db.query(IdiomEntry).filter(
        IdiomEntry.visibility == "public"
    )
    
    # Apply search filter only if q is provided
    if q:
        q_norm = normalize_roman(q)
        query = query.filter(
            (
                IdiomEntry.text_devanagari.ilike(f"%{q}%")
                | (IdiomEntry.text_roman_norm == q_norm)
                | IdiomEntry.text_roman_norm.ilike(f"%{q_norm}%")
            )
        )
    
    results = query.order_by(IdiomEntry.id.asc()).offset(offset).limit(limit).all()

    # Only increment search KPI when actually searching
    if q:
        for r in results:
            _inc_search_kpi(db, r.id)
        db.commit()
    
    return results

@router.get("/{idiom_id}", response_model=IdiomOut)
def get_idiom(idiom_id: int, db: Session = Depends(get_db)):
    entry = (
        db.query(IdiomEntry)
        .filter(
            IdiomEntry.id == idiom_id,
            IdiomEntry.visibility == "public",
        )
        .first()
    )
    if not entry:
        raise HTTPException(status_code=404, detail="Idiom not found")  # ✅ Fix

    _inc_view_kpi(db, entry.id)
    db.commit()
    return entry
