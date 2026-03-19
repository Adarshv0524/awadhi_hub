# app/api/v1/interactions.py

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import get_current_user, require_role
from app.core.permissions import Role
from app.services.interaction_service import toggle_interaction, record_share, create_report, list_user_bookmarks

router = APIRouter(prefix="/interactions", tags=["interactions"])


class ToggleIn(BaseModel):
    content_type: str
    content_id: int
    interaction: str  # 'like' or 'bookmark'
    metadata: Optional[Dict[str, Any]] = None


class ShareIn(BaseModel):
    content_type: str
    content_id: int
    metadata: Optional[Dict[str, Any]] = None


class ReportIn(BaseModel):
    content_type: str
    content_id: int
    reason: str = Field(..., pattern="^(spam|abuse|copyright|other)$")  # ✅ CHANGED: regex → pattern
    note: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@router.post("/toggle")
def api_toggle_interaction(payload: ToggleIn, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if payload.interaction not in ("like", "bookmark"):
        raise HTTPException(status_code=400, detail="interaction must be 'like' or 'bookmark'")
    res = toggle_interaction(db=db, user_id=current_user.id, content_type=payload.content_type, content_id=payload.content_id, interaction_type=payload.interaction, metadata=payload.metadata)
    return res


@router.post("/share")
def api_record_share(payload: ShareIn, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    res = record_share(db=db, user_id=current_user.id, content_type=payload.content_type, content_id=payload.content_id, metadata=payload.metadata)
    return res


@router.post("/report")
def api_create_report(payload: ReportIn, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    res = create_report(db=db, user_id=current_user.id, content_type=payload.content_type, content_id=payload.content_id, reason=payload.reason, note=payload.note, metadata=payload.metadata)
    return res


@router.get("/users/{user_id}/bookmarks")
def api_list_user_bookmarks(user_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user), offset: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=200)):
    # Owner-only or admin
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not allowed")
    res = list_user_bookmarks(db=db, user_id=user_id, limit=limit, offset=offset)
    return {"count": len(res), "results": res}
