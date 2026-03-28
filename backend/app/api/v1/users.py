# app/api/v1/users.py

from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, func, literal, cast, Float

from app.db.session import get_db
from app.db.models import (
    User,
    Submission,
    EngagementKPI,
    DohaEntry,
    DictionaryEntry,
    IdiomEntry,
    ArticleEntry,
)

router = APIRouter(prefix="/users", tags=["users"])


class PublicUserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: Optional[str]
    role: str

class UserStatsOut(BaseModel):
    username: str = Field(..., description="Public username for the profile.")
    contributions_count: int = Field(
        ...,
        description="Total approved public canonical contributions authored by this user.",
    )
    likes_received: int = Field(
        ...,
        description="Total likes received on approved public contributions.",
    )
    most_liked_content_id: Optional[int] = Field(
        None,
        description="Content ID of the user's most-liked approved public contribution.",
    )
    average_engagement_score: float = Field(
        ...,
        description="Average engagement score across approved public contributions.",
    )
    joined_date: datetime = Field(..., description="Account creation timestamp.")


@router.get("/{username}", response_model=PublicUserOut)
def get_public_user(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def _contribution_content_union_for_user(user_id: int):
    doha_q = (
        select(
            literal("doha").label("content_type"),
            DohaEntry.id.label("content_id"),
        )
        .join(Submission, Submission.id == DohaEntry.source_submission_id)
        .where(
            Submission.contributor_id == user_id,
            Submission.status == "approved",
            Submission.visibility == "public",
            Submission.is_deleted == False,
            DohaEntry.visibility == "public",
            DohaEntry.status == "active",
            DohaEntry.is_canonical == True,
            DohaEntry.is_deleted == False,
        )
    )
    dictionary_q = (
        select(
            literal("dictionary").label("content_type"),
            DictionaryEntry.id.label("content_id"),
        )
        .join(Submission, Submission.id == DictionaryEntry.source_submission_id)
        .where(
            Submission.contributor_id == user_id,
            Submission.status == "approved",
            Submission.visibility == "public",
            Submission.is_deleted == False,
            DictionaryEntry.source_submission_id.isnot(None),
            DictionaryEntry.visibility == "public",
        )
    )
    idiom_q = (
        select(
            literal("idiom").label("content_type"),
            IdiomEntry.id.label("content_id"),
        )
        .join(Submission, Submission.id == IdiomEntry.source_submission_id)
        .where(
            Submission.contributor_id == user_id,
            Submission.status == "approved",
            Submission.visibility == "public",
            Submission.is_deleted == False,
            IdiomEntry.source_submission_id.isnot(None),
            IdiomEntry.visibility == "public",
        )
    )
    article_q = (
        select(
            literal("article").label("content_type"),
            ArticleEntry.id.label("content_id"),
        )
        .join(Submission, Submission.id == ArticleEntry.source_submission_id)
        .where(
            Submission.contributor_id == user_id,
            Submission.status == "approved",
            Submission.visibility == "public",
            Submission.is_deleted == False,
            ArticleEntry.source_submission_id.isnot(None),
            ArticleEntry.visibility == "public",
        )
    )
    return doha_q.union_all(dictionary_q, idiom_q, article_q).subquery("contrib_content")


@router.get("/{username}/stats", response_model=UserStatsOut)
def get_user_stats(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    contrib_content = _contribution_content_union_for_user(user.id)

    contributions_count = db.execute(
        select(func.count()).select_from(contrib_content)
    ).scalar_one()
    kpi_join = contrib_content.outerjoin(
        EngagementKPI,
        (EngagementKPI.content_type == contrib_content.c.content_type)
        & (EngagementKPI.content_id == contrib_content.c.content_id),
    )

    likes_received = db.execute(
        select(func.coalesce(func.sum(EngagementKPI.likes_count), 0)).select_from(kpi_join)
    ).scalar_one()

    average_engagement_score = db.execute(
        select(func.coalesce(cast(func.avg(EngagementKPI.weight_score), Float), 0.0)).select_from(kpi_join)
    ).scalar_one()

    most_liked_content_id = db.execute(
        select(
            contrib_content.c.content_id,
            func.coalesce(EngagementKPI.likes_count, 0).label("likes_count"),
        )
        .select_from(kpi_join)
        .order_by(func.coalesce(EngagementKPI.likes_count, 0).desc(), contrib_content.c.content_id.asc())
        .limit(1)
    ).first()

    return UserStatsOut(
        username=user.username or username,
        contributions_count=int(contributions_count or 0),
        likes_received=int(likes_received or 0),
        most_liked_content_id=int(most_liked_content_id.content_id) if most_liked_content_id else None,
        average_engagement_score=float(average_engagement_score or 0.0),
        joined_date=user.created_at,
    )
