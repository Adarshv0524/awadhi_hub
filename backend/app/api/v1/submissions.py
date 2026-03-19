# app/api/v1/submissions.py

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict

from sqlalchemy.orm import Session
from sqlalchemy import and_, update

from app.db.session import get_db
from app.db.models import Submission, ClassicalAuthor, ClassicalWork, WorkChapter, User
from app.core.security import get_current_user
from app.core.permissions import Role, role_at_least
from app.services.rate_limit import rate_limit_dependency

router = APIRouter(prefix="/submissions", tags=["submissions"])


# --------- Pydantic models ---------

class SubmissionCreateIn(BaseModel):
    content_type: str = Field(..., max_length=50)
    main_text: str
    meaning: Optional[str] = None
    is_classical: bool = False
    author_slug: Optional[str] = None
    work_slug: Optional[str] = None
    chapter_slug: Optional[str] = None
    number_in_chapter: Optional[int] = None
    external_references: Optional[Dict[str, Any]] = None  # ✅ Changed from "references"
    visibility: Optional[str] = Field("private", max_length=20)
    submit_for_review: bool = False

class SubmissionUpdateIn(BaseModel):
    main_text: Optional[str] = None
    meaning: Optional[str] = None
    external_references: Optional[Dict[str, Any]] = None  # ✅ Changed from "references"
    visibility: Optional[str] = Field(None, max_length=20)
    submit_for_review: Optional[bool] = None
    expected_version: int

class SubmissionOut(BaseModel):
    id: int
    content_type: str
    main_text: str
    meaning: Optional[str]
    is_classical: bool
    author_slug: Optional[str]
    work_slug: Optional[str]
    chapter_slug: Optional[str]
    number_in_chapter: Optional[int]
    external_references: Optional[Dict[str, Any]]  # ✅ Changed from "references"
    status: str
    visibility: str
    version: int
    contributor_id: int
    priority: int

    class Config:
        orm_mode = True


# --------- Helpers ---------

ALLOWED_STATUSES_FOR_USER_EDIT = {"draft", "rejected"}


def _validate_classical_reference(
    db: Session,
    is_classical: bool,
    author_slug: Optional[str],
    work_slug: Optional[str],
    chapter_slug: Optional[str],
    number_in_chapter: Optional[int],
):
    """
    If is_classical=True, ensure provided slugs exist in the hierarchy.
    We do *not* auto-create anything here.
    """
    if not is_classical:
        return

    if not (author_slug and work_slug and chapter_slug and number_in_chapter is not None):
        raise HTTPException(
            status_code=400,
            detail="For classical submissions, author_slug, work_slug, chapter_slug and number_in_chapter are required",
        )

    author = (
        db.query(ClassicalAuthor)
        .filter(
            ClassicalAuthor.slug == author_slug,
            ClassicalAuthor.is_deleted == False,
        )
        .first()
    )
    if not author:
        raise HTTPException(status_code=400, detail="Invalid author_slug for classical submission")

    work = (
        db.query(ClassicalWork)
        .filter(
            ClassicalWork.author_id == author.id,
            ClassicalWork.slug == work_slug,
            ClassicalWork.is_deleted == False,
        )
        .first()
    )
    if not work:
        raise HTTPException(status_code=400, detail="Invalid work_slug for this author")

    chapter = (
        db.query(WorkChapter)
        .filter(
            WorkChapter.work_id == work.id,
            WorkChapter.slug == chapter_slug,
            WorkChapter.is_deleted == False,
        )
        .first()
    )
    if not chapter:
        raise HTTPException(status_code=400, detail="Invalid chapter_slug for this work")

    if number_in_chapter <= 0:
        raise HTTPException(status_code=400, detail="number_in_chapter must be positive")


def _ensure_can_access_submission(user: User, submission: Submission):
    # Admins can access everything
    if role_at_least(user.role, Role.ADMIN):
        return
    # Contributor can access own submission
    if submission.contributor_id == user.id:
        return
    raise HTTPException(status_code=403, detail="Not allowed to access this submission")


def _ensure_user_can_edit_submission(user: User, submission: Submission):
    _ensure_can_access_submission(user, submission)
    if submission.status not in ALLOWED_STATUSES_FOR_USER_EDIT:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot edit submission in status '{submission.status}'. Allowed: {', '.join(ALLOWED_STATUSES_FOR_USER_EDIT)}",
        )


# --------- Endpoints ---------

_submission_rl = rate_limit_dependency(action_key="submission_create", limit=20, window_seconds=86400, granularity=3600)

@router.post("", response_model=SubmissionOut, dependencies=[Depends(_submission_rl)])
def create_submission(
    data: SubmissionCreateIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _validate_classical_reference(
        db,
        data.is_classical,
        data.author_slug,
        data.work_slug,
        data.chapter_slug,
        data.number_in_chapter,
    )

    status = "pending_review" if data.submit_for_review else "draft"

    submission = Submission(
        content_type=data.content_type,
        main_text=data.main_text,
        meaning=data.meaning,
        is_classical=data.is_classical,
        author_slug=data.author_slug,
        work_slug=data.work_slug,
        chapter_slug=data.chapter_slug,
        number_in_chapter=data.number_in_chapter,
        external_references=data.external_references,
        status=status,
        visibility=data.visibility or "private",
        version=1,
        contributor_id=current_user.id,
        priority=0,
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission


@router.get("/me", response_model=List[SubmissionOut])
def list_my_submissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    status: Optional[str] = Query(None),
    content_type: Optional[str] = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    q = db.query(Submission).filter(
        Submission.contributor_id == current_user.id,
        Submission.is_deleted == False,
    )
    if status:
        q = q.filter(Submission.status == status)
    if content_type:
        q = q.filter(Submission.content_type == content_type)

    subs = (
        q.order_by(Submission.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return subs


@router.get("/{submission_id}", response_model=SubmissionOut)
def get_submission(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sub = db.query(Submission).filter(Submission.id == submission_id, Submission.is_deleted == False).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")
    _ensure_can_access_submission(current_user, sub)
    return sub


@router.put("/{submission_id}", response_model=SubmissionOut)
def update_submission(
    submission_id: int,
    data: SubmissionUpdateIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sub = db.query(Submission).filter(Submission.id == submission_id, Submission.is_deleted == False).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")

    _ensure_user_can_edit_submission(current_user, sub)

    # optimistic locking
    if sub.version != data.expected_version:
        raise HTTPException(
            status_code=409,
            detail=f"Version conflict. Current version is {sub.version}",
        )

    if data.main_text is not None:
        sub.main_text = data.main_text
    if data.meaning is not None:
        sub.meaning = data.meaning
    if data.external_references is not None:
        sub.external_references = data.external_references
    if data.visibility is not None:
        sub.visibility = data.visibility

    if data.submit_for_review is True:
        sub.status = "pending_review"

    sub.version = sub.version + 1
    db.commit()
    db.refresh(sub)
    return sub


@router.delete("/{submission_id}")
def delete_submission(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sub = db.query(Submission).filter(Submission.id == submission_id, Submission.is_deleted == False).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")

    _ensure_can_access_submission(current_user, sub)

    sub.is_deleted = True
    sub.status = "archived"
    db.commit()
    return {"ok": True}
