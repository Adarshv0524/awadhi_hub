# app/api/v1/moderation.py
import logging
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import Submission, ModerationLog, User
from app.core.security import require_role, get_current_user
from app.core.permissions import Role
from app.services.content_service import (
    create_canonical_doha_from_submission,
    create_canonical_poetry_node_from_submission,
)
from app.services.batch_moderation import batch_approve_submissions, BatchValidationError
from app.services.model_governance_service import append_model_event

router = APIRouter(prefix="/moderation", tags=["moderation"])

# ------- Pydantic models -------
class ModerationSubmissionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    content_type: str
    main_text: str
    meaning: Optional[str]
    status: str
    is_classical: bool
    author_slug: Optional[str]
    work_slug: Optional[str]
    chapter_slug: Optional[str]
    number_in_chapter: Optional[int]
    contributor_id: int
    assigned_moderator_id: Optional[int]
    priority: int
    version: int
class ModerationActionIn(BaseModel):
    note: Optional[str] = None
    guideline_version: Optional[str] = None
    approved_by_human: bool = False
    model_recommendation_id: Optional[str] = None
    model_confidence: Optional[float] = None
    model_rationale_snippets: List[str] = Field(default_factory=list)

class ModerationBatchIn(BaseModel):
    action: str  # "approve" or "reject"
    submission_ids: List[int]
    note: Optional[str] = None
    guideline_version: Optional[str] = None

class BatchApproveIn(BaseModel):
    submission_ids: List[int]

class BatchApproveOut(BaseModel):
    batch_id: str
    created: List[Dict[str, Any]]
    skipped: List[int]
    errors: List[Dict[str, Any]]

# ------- Helpers -------
def _ensure_can_moderate(submission: Submission):
    if submission.is_deleted:
        raise HTTPException(status_code=400, detail="Cannot moderate deleted submission")
    if submission.status != "pending_review":
        raise HTTPException(
            status_code=400,
            detail=f"Can only moderate submissions in 'pending_review' status (current: {submission.status})",
        )

def _log_moderation(
    db: Session,
    submission_id: int,
    moderator_id: int,
    action: str,
    from_status: Optional[str],
    to_status: Optional[str],
    guideline_version: Optional[str],
    note: Optional[str],
):
    log = ModerationLog(
        submission_id=submission_id,
        moderator_id=moderator_id,
        action=action,
        from_status=from_status,
        to_status=to_status,
        guideline_version=guideline_version,
        note=note,
    )
    db.add(log)

# ------- Endpoints -------
@router.get(
    "/submissions",
    response_model=List[ModerationSubmissionOut],
)
def list_pending_submissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(Role.MODERATOR)),
    assigned_to_me: bool = Query(False, description="If true, only show submissions assigned to me"),
    unassigned_only: bool = Query(False, description="If true, only show unassigned submissions"),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    """
    List moderation queue.
    - Only moderators/admins can see this.
    - Default: all pending_review submissions (regardless of assignment).
    - If `assigned_to_me=true` -> only those assigned to current_user.
    - If `unassigned_only=true` -> only those with assigned_moderator_id = NULL.
    """
    q = db.query(Submission).filter(
        Submission.status == "pending_review",
        Submission.is_deleted == False,
    )
    if assigned_to_me:
        q = q.filter(Submission.assigned_moderator_id == current_user.id)
    elif unassigned_only:
        q = q.filter(Submission.assigned_moderator_id.is_(None))
    subs = (
        q.order_by(Submission.priority.desc(), Submission.created_at.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return subs

@router.get(
    "/submissions/{submission_id}",
    response_model=ModerationSubmissionOut,
)
def get_submission_for_moderation(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(Role.MODERATOR)),
):
    sub = db.query(Submission).filter(Submission.id == submission_id, Submission.is_deleted == False).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")
    return sub


@router.post(
    "/submissions/{submission_id}/approve",
    response_model=ModerationSubmissionOut,
)
def approve_submission(
    submission_id: int,
    data: ModerationActionIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(Role.MODERATOR)),
):
    sub = db.query(Submission).filter(Submission.id == submission_id, Submission.is_deleted == False).with_for_update().first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")
    if not data.approved_by_human:
        raise HTTPException(status_code=400, detail="Human approval is required for irreversible moderation actions")
    _ensure_can_moderate(sub)
    from_status = sub.status
    sub.status = "approved"
    if sub.assigned_moderator_id is None:
        sub.assigned_moderator_id = current_user.id
    _log_moderation(
        db=db,
        submission_id=sub.id,
        moderator_id=current_user.id,
        action="approve",
        from_status=from_status,
        to_status=sub.status,
        guideline_version=data.guideline_version,
        note=data.note,
    )

    if data.model_recommendation_id:
        append_model_event(
            db,
            recommendation_id=data.model_recommendation_id,
            use_case="moderation_triage",
            event_type="human_decision",
            model_name="human-review",
            model_version="v1",
            actor_user_id=current_user.id,
            payload={
                "submission_id": sub.id,
                "decision": "approve",
                "approved_by_human": data.approved_by_human,
                "model_confidence": data.model_confidence,
                "model_rationale_snippets": data.model_rationale_snippets,
                "note": data.note,
            },
        )
    
    # Create canonical content based on content_type
    logger = logging.getLogger("app.moderation")
    logger.info("Approving submission %s (type=%s) by moderator %s", sub.id, sub.content_type, current_user.id)
    
    try:
        if sub.content_type == "doha":
            create_canonical_doha_from_submission(db=db, submission=sub, moderator=current_user)
            logger.info("Created canonical doha for submission %s", sub.id)
        elif sub.content_type == "dictionary":
            from app.services.content_service import create_canonical_dictionary_from_submission
            dict_id = create_canonical_dictionary_from_submission(db=db, submission=sub, moderator_user=current_user)
            logger.info("Created dictionary entry id=%s for submission %s", dict_id, sub.id)
        elif sub.content_type == "idiom":
            from app.services.content_service import create_canonical_idiom_from_submission
            idiom_id = create_canonical_idiom_from_submission(db=db, submission=sub, moderator_user=current_user)
            logger.info("Created idiom entry id=%s for submission %s", idiom_id, sub.id)
        elif sub.content_type == "article":
            from app.services.content_service import create_canonical_article_from_submission
            article_id = create_canonical_article_from_submission(db=db, submission=sub, moderator_user=current_user)
            logger.info("Created article entry id=%s for submission %s", article_id, sub.id)
        else:
            # Non-doha poetry forms are canonically represented via poetry_nodes.
            poetry_node_id = create_canonical_poetry_node_from_submission(db=db, submission=sub, moderator_user=current_user)
            if poetry_node_id:
                logger.info("Created poetry node id=%s for submission %s", poetry_node_id, sub.id)
            else:
                logger.warning("Unknown content_type '%s' for submission %s - no canonical content created", sub.content_type, sub.id)
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        logger.exception("Failed to create canonical content for submission %s: %s", sub.id, e)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create canonical content: {str(e)}")
    
    db.commit()
    db.refresh(sub)
    return sub



@router.post(
    "/submissions/{submission_id}/reject",
    response_model=ModerationSubmissionOut,
)
def reject_submission(
    submission_id: int,
    data: ModerationActionIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(Role.MODERATOR)),
):
    sub = db.query(Submission).filter(Submission.id == submission_id, Submission.is_deleted == False).with_for_update().first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")
    if not data.approved_by_human:
        raise HTTPException(status_code=400, detail="Human approval is required for irreversible moderation actions")
    _ensure_can_moderate(sub)
    from_status = sub.status
    sub.status = "rejected"
    if sub.assigned_moderator_id is None:
        sub.assigned_moderator_id = current_user.id
    _log_moderation(
        db=db,
        submission_id=sub.id,
        moderator_id=current_user.id,
        action="reject",
        from_status=from_status,
        to_status=sub.status,
        guideline_version=data.guideline_version,
        note=data.note,
    )

    if data.model_recommendation_id:
        append_model_event(
            db,
            recommendation_id=data.model_recommendation_id,
            use_case="moderation_triage",
            event_type="human_decision",
            model_name="human-review",
            model_version="v1",
            actor_user_id=current_user.id,
            payload={
                "submission_id": sub.id,
                "decision": "reject",
                "approved_by_human": data.approved_by_human,
                "model_confidence": data.model_confidence,
                "model_rationale_snippets": data.model_rationale_snippets,
                "note": data.note,
            },
        )
    db.commit()
    db.refresh(sub)
    return sub

@router.post("/batch")
def batch_moderate(
    data: ModerationBatchIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(Role.MODERATOR)),
):
    if data.action not in {"approve", "reject"}:
        raise HTTPException(status_code=400, detail="action must be 'approve' or 'reject'")
    if not data.submission_ids:
        raise HTTPException(status_code=400, detail="submission_ids cannot be empty")
    to_status = "approved" if data.action == "approve" else "rejected"
    # Wrap in single transaction: all or nothing
    subs = (
        db.query(Submission)
        .filter(
            Submission.id.in_(data.submission_ids),
            Submission.is_deleted == False,
        )
        .with_for_update()
        .all()
    )
    found_ids = {s.id for s in subs}
    missing = set(data.submission_ids) - found_ids
    if missing:
        raise HTTPException(status_code=400, detail=f"Some submissions not found: {sorted(missing)}")
    for sub in subs:
        _ensure_can_moderate(sub)
        from_status = sub.status
        sub.status = to_status
        if sub.assigned_moderator_id is None:
            sub.assigned_moderator_id = current_user.id
        _log_moderation(
            db=db,
            submission_id=sub.id,
            moderator_id=current_user.id,
            action=data.action,
            from_status=from_status,
            to_status=sub.status,
            guideline_version=data.guideline_version,
            note=data.note,
        )
    db.commit()
    return {"ok": True, "action": data.action, "count": len(subs)}

@router.post("/batch_approve", response_model=BatchApproveOut, dependencies=[Depends(require_role(Role.MODERATOR))])
def batch_approve(data: BatchApproveIn, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    Batch approve submissions (Admin only).
    Returns batch_id, created canonical content, skipped submissions, and any errors.
    """
    try:
        # gather metadata from request context if available; here we only pass moderator id as metadata
        metadata = {"moderator_id": current_user.id if current_user else None}
        res = batch_approve_submissions(db, data.submission_ids, actor_user_id=current_user.id if current_user else None, request_metadata=metadata)
        return {
            "batch_id": res.get("batch_id"),
            "created": res.get("created", []),
            "skipped": res.get("skipped", []),
            "errors": res.get("errors", []),
        }
    except BatchValidationError as be:
        # return 400 with details
        raise HTTPException(status_code=400, detail=be.errors)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))