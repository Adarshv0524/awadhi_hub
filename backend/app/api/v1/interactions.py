# app/api/v1/interactions.py

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Literal

from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import get_current_user, require_role
from app.core.permissions import Role
from app.services.interaction_service import (
    toggle_interaction,
    record_share,
    create_report,
    list_user_bookmarks,
    list_user_likes,
)

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


class UserInteractionOut(BaseModel):
    id: int
    content_type: str
    content_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    content_title: str
    content_snippet: Optional[str] = None
    content_path: Optional[str] = None


class UserBookmarkOut(UserInteractionOut):
    pass


class UserLikeOut(UserInteractionOut):
    pass


class UserBookmarksListOut(BaseModel):
    total_count: int
    count: int
    results: List[UserBookmarkOut]


class UserLikesListOut(BaseModel):
    total_count: int
    count: int
    results: List[UserLikeOut]


class MasterInteractionIn(BaseModel):
    action: Literal["toggle", "share", "report", "list_bookmarks", "list_likes"]
    content_type: Optional[str] = None
    content_id: Optional[int] = None
    interaction: Optional[Literal["like", "bookmark"]] = None
    reason: Optional[str] = Field(default=None, pattern="^(spam|abuse|copyright|other)$")
    note: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    user_id: Optional[int] = None
    offset: int = 0
    limit: int = 50


def _normalize_content_type(content_type: str) -> str:
    return (content_type or "").strip().lower()


def _ensure_owner_or_admin(current_user, user_id: int):
    if current_user.id != user_id and current_user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Not allowed")


@router.post("/master")
def api_interaction_master(
    payload: MasterInteractionIn,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    action = payload.action

    if action in {"toggle", "share", "report"}:
        if not payload.content_type or payload.content_id is None:
            raise HTTPException(status_code=400, detail="content_type and content_id are required")
        content_type = _normalize_content_type(payload.content_type)
        content_id = int(payload.content_id)

        if action == "toggle":
            if payload.interaction not in ("like", "bookmark"):
                raise HTTPException(status_code=400, detail="interaction must be 'like' or 'bookmark'")
            return toggle_interaction(
                db=db,
                user_id=current_user.id,
                content_type=content_type,
                content_id=content_id,
                interaction_type=payload.interaction,
                metadata=payload.metadata,
            )

        if action == "share":
            return record_share(
                db=db,
                user_id=current_user.id,
                content_type=content_type,
                content_id=content_id,
                metadata=payload.metadata,
            )

        return create_report(
            db=db,
            user_id=current_user.id,
            content_type=content_type,
            content_id=content_id,
            reason=payload.reason or "other",
            note=payload.note,
            metadata=payload.metadata,
        )

    target_user_id = int(payload.user_id or current_user.id)
    _ensure_owner_or_admin(current_user, target_user_id)
    limit = max(1, min(int(payload.limit or 50), 200))
    offset = max(0, int(payload.offset or 0))

    if action == "list_bookmarks":
        res = list_user_bookmarks(db=db, user_id=target_user_id, limit=limit, offset=offset)
        return {
            "total_count": res["total_count"],
            "count": len(res["results"]),
            "results": res["results"],
        }

    res = list_user_likes(db=db, user_id=target_user_id, limit=limit, offset=offset)
    return {
        "total_count": res["total_count"],
        "count": len(res["results"]),
        "results": res["results"],
    }


@router.post("/toggle")
def api_toggle_interaction(payload: ToggleIn, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if payload.interaction not in ("like", "bookmark"):
        raise HTTPException(status_code=400, detail="interaction must be 'like' or 'bookmark'")
    return api_interaction_master(
        MasterInteractionIn(
            action="toggle",
            content_type=payload.content_type,
            content_id=payload.content_id,
            interaction=payload.interaction,
            metadata=payload.metadata,
        ),
        db,
        current_user,
    )


@router.post("/share")
def api_record_share(payload: ShareIn, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return api_interaction_master(
        MasterInteractionIn(
            action="share",
            content_type=payload.content_type,
            content_id=payload.content_id,
            metadata=payload.metadata,
        ),
        db,
        current_user,
    )


@router.post("/report")
def api_create_report(payload: ReportIn, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return api_interaction_master(
        MasterInteractionIn(
            action="report",
            content_type=payload.content_type,
            content_id=payload.content_id,
            reason=payload.reason,
            note=payload.note,
            metadata=payload.metadata,
        ),
        db,
        current_user,
    )


@router.get("/users/{user_id}/bookmarks", response_model=UserBookmarksListOut)
def api_list_user_bookmarks(user_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user), offset: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=200)):
    return api_interaction_master(
        MasterInteractionIn(action="list_bookmarks", user_id=user_id, limit=limit, offset=offset),
        db,
        current_user,
    )


@router.get("/users/{user_id}/likes", response_model=UserLikesListOut)
def api_list_user_likes(user_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user), offset: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=200)):
    return api_interaction_master(
        MasterInteractionIn(action="list_likes", user_id=user_id, limit=limit, offset=offset),
        db,
        current_user,
    )
