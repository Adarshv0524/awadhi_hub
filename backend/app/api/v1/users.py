# app/api/v1/users.py

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session, aliased
from sqlalchemy import select, func

from app.db.session import get_db
from app.db.models import (
    User,
    Submission,
    UserInteraction,
    DohaEntry,
    DictionaryEntry,
    IdiomEntry,
    ArticleEntry,
)

router = APIRouter(prefix="/users", tags=["users"])


class PublicUserOut(BaseModel):
    id: int
    username: Optional[str]
    role: str

    class Config:
        orm_mode = True


class UserPublicStatsOut(BaseModel):
    public_submissions: int
    approved_count: int
    likes_received: int
    bookmarks_received: int


@router.get("/{username}", response_model=PublicUserOut)
def get_public_user(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def _interaction_count_subquery_for_content(
    interaction_type: str,
    content_model,
    content_type: str,
):
    sub = aliased(Submission)
    return (
        select(func.count(UserInteraction.id))
        .select_from(UserInteraction)
        .join(content_model, content_model.id == UserInteraction.content_id)
        .join(sub, sub.id == content_model.source_submission_id)
        .where(
            UserInteraction.interaction_type == interaction_type,
            UserInteraction.is_active == True,
            UserInteraction.content_type == content_type,
            sub.contributor_id == User.id,
            sub.status == "approved",
            sub.visibility == "public",
            sub.is_deleted == False,
        )
        .scalar_subquery()
    )


@router.get("/{username}/stats", response_model=UserPublicStatsOut)
def get_user_stats(username: str, db: Session = Depends(get_db)):
    sub_public = aliased(Submission)
    public_submissions_sq = (
        select(func.count(sub_public.id))
        .where(
            sub_public.contributor_id == User.id,
            sub_public.status == "approved",
            sub_public.visibility == "public",
            sub_public.is_deleted == False,
        )
        .scalar_subquery()
    )

    # Public profile aggregates should only include approved + public contributions.
    approved_count_sq = public_submissions_sq

    likes_received_sq = (
        _interaction_count_subquery_for_content("like", DohaEntry, "doha")
        + _interaction_count_subquery_for_content("like", DictionaryEntry, "dictionary")
        + _interaction_count_subquery_for_content("like", IdiomEntry, "idiom")
        + _interaction_count_subquery_for_content("like", ArticleEntry, "article")
    )
    bookmarks_received_sq = (
        _interaction_count_subquery_for_content("bookmark", DohaEntry, "doha")
        + _interaction_count_subquery_for_content("bookmark", DictionaryEntry, "dictionary")
        + _interaction_count_subquery_for_content("bookmark", IdiomEntry, "idiom")
        + _interaction_count_subquery_for_content("bookmark", ArticleEntry, "article")
    )

    row = db.execute(
        select(
            User.id.label("user_id"),
            public_submissions_sq.label("public_submissions"),
            approved_count_sq.label("approved_count"),
            likes_received_sq.label("likes_received"),
            bookmarks_received_sq.label("bookmarks_received"),
        ).where(User.username == username)
    ).first()

    if not row:
        raise HTTPException(status_code=404, detail="User not found")

    return UserPublicStatsOut(
        public_submissions=int(row.public_submissions or 0),
        approved_count=int(row.approved_count or 0),
        likes_received=int(row.likes_received or 0),
        bookmarks_received=int(row.bookmarks_received or 0),
    )
