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
from app.core.security import get_current_user
from app.services.email_verification_service import send_verification_otp

router = APIRouter(prefix="/users", tags=["users"])


class PublicUserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: Optional[str] = None
    bio: Optional[str] = None
    username: Optional[str]
    role: str
    created_at: Optional[datetime] = None


class UserProfileUpdateIn(BaseModel):
    """User profile update model for self-service edits (username, name, bio, email)."""
    username: Optional[str] = None
    name: Optional[str] = None
    bio: Optional[str] = None
    email: Optional[str] = None


class UserProfileUpdateOut(BaseModel):
    id: int
    username: Optional[str]
    name: Optional[str] = None
    bio: Optional[str] = None
    email: str
    role: str
    pending_email: Optional[str] = None
    email_verification_required: bool = False
    message: Optional[str] = None

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


@router.patch("/me", response_model=UserProfileUpdateOut)
def update_own_profile(
    data: UserProfileUpdateIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Allow authenticated users to update their own profile (username and email only)."""
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    email_changed = False

    if data.username is not None:
        normalized_username = data.username.strip() if isinstance(data.username, str) else data.username
        if normalized_username == "":
            normalized_username = None

        if normalized_username != user.username and normalized_username is not None:
            username_taken = (
                db.query(User)
                .filter(User.username == normalized_username, User.id != user.id)
                .first()
            )
            if username_taken:
                raise HTTPException(status_code=400, detail="Username already taken")

        user.username = normalized_username

    if data.name is not None:
        normalized_name = data.name.strip() if isinstance(data.name, str) else data.name
        if normalized_name == "":
            normalized_name = None
        user.name = normalized_name

    if data.bio is not None:
        normalized_bio = data.bio.strip() if isinstance(data.bio, str) else data.bio
        if normalized_bio == "":
            normalized_bio = None
        # Keep bio concise for profile rendering and payload hygiene.
        if normalized_bio and len(normalized_bio) > 600:
            raise HTTPException(status_code=400, detail="Bio must be 600 characters or fewer")
        user.bio = normalized_bio
    
    if data.email is not None and data.email != user.email:
        email_taken = db.query(User).filter(User.email == data.email, User.id != user.id).first()
        if email_taken:
            raise HTTPException(status_code=400, detail="Email already in use")

        # Email is changing - stage it for verification instead of updating directly
        user.pending_email = data.email
        email_changed = True
        
        # Send verification OTP to new email address
        try:
            send_verification_otp(db, user.id, data.email)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send verification OTP for user {user.id}: {e}")
            raise HTTPException(status_code=500, detail="Failed to send verification email")
    
    db.commit()
    db.refresh(user)
    
    response = {
        "id": user.id,
        "username": user.username,
        "name": user.name,
        "bio": user.bio,
        "email": user.email,
        "role": user.role,
        "pending_email": user.pending_email,
        "email_verification_required": False,
    }
    
    if email_changed:
        response["email_verification_required"] = True
        response["message"] = f"Verification OTP sent to {data.email}. Please verify it to complete email change."
    
    return response


@router.get("/id/{user_id}", response_model=PublicUserOut)
def get_public_user_by_id(user_id: int, db: Session = Depends(get_db)):
    """Get public user info by numeric ID (for moderation contributor lookup)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


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
