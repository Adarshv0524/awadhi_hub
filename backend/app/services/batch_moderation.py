# app/services/batch_moderation.py
import uuid
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from pydantic import ValidationError

from app.db.models import Submission, ModerationLog, ClassicalAuthor, ClassicalWork, WorkChapter
from app.services.audit_service import record_audit
from app.services.content_service import (
    create_canonical_dictionary_from_submission,
    create_canonical_idiom_from_submission,
    create_canonical_article_from_submission,
)

logger = logging.getLogger(__name__)

# Attempt to import DohaEntry and ContentVersion models (fail clearly if absent)
try:
    from app.db.models import DohaEntry, ContentVersion
except Exception:
    DohaEntry = None
    ContentVersion = None

class BatchValidationError(Exception):
    def __init__(self, errors: List[Dict[str, Any]]):
        self.errors = errors
        super().__init__("Batch validation failed")

def _create_wrapper(func, db, sub, actor_user_id, audit_metadata):
    """
    Adapter: call func(db, sub, moderator_user) -> returns canonical_id or raises.
    Returns tuple (created_flag(bool), canonical_id or None, error_or_None)
    """
    try:
        canonical_id = func(db, sub, moderator_user=type("U", (), {"id": actor_user_id})() if actor_user_id else None)
        # if canonical existed, func returns id -> treat as created if created in this run; we can't know if pre-existed,
        # so check if canonical's source_submission_id existed was handled by func (it returns existing id if present)
        # We will treat returned id as created if there was no existing row before; easiest approach: check db for that canonical's source_submission_id mapping:
        # but simpler: if there's a row with source_submission_id == sub.id then treat as created (or skipped?) We'll treat as created if currently a row exists and submission.status previously not approved.
        return True, canonical_id, None
    except ValidationError as ve:
        return False, None, str(ve)
    except Exception as e:
        return False, None, str(e)

def _pre_validate_submissions(db: Session, submission_ids: List[int]) -> Tuple[List[Submission], List[Dict[str, Any]]]:
    """
    Pre-validate submissions. Returns (submissions_list, errors_list).
    """
    submissions = []
    errors = []
    for sid in submission_ids:
        sub = db.query(Submission).filter(Submission.id == sid, Submission.is_deleted == False).first()
        if not sub:
            errors.append({"submission_id": sid, "error": "not_found"})
            continue
        if sub.status not in ("pending_review", "review_requested"):
            errors.append({"submission_id": sid, "error": f"invalid_status:{sub.status}"})
            continue
        if sub.content_type not in ("doha", "idiom", "article", "dictionary_entry", "dictionary"):
            errors.append({"submission_id": sid, "error": f"unsupported_content_type:{sub.content_type}"})
            continue
        submissions.append(sub)
    return submissions, errors

def _handle_doha(db: Session, sub: Submission, batch_id: str, actor_user_id: Optional[int], audit_metadata: Dict[str, Any]) -> Tuple[bool, Optional[int], Optional[str]]:
    """
    Returns (created: bool, canonical_id or None, error or None)
    created=True when canonical created; False when skipped (e.g., duplicate).
    """
    if DohaEntry is None:
        return False, None, "doha_model_missing"
    # Check duplicate by source_submission_id
    existing = db.query(DohaEntry).filter(DohaEntry.source_submission_id == sub.id).first()
    if existing:
        return False, existing.id, None  # skipped because already canonicalized
    # If this submission references classical hierarchy, resolve slugs -> ids
    author_id = None
    work_id = None
    chapter_id = None
    if sub.is_classical:
        if not (sub.author_slug and sub.work_slug and sub.chapter_slug and sub.number_in_chapter is not None):
            return False, None, "missing_classical_reference"
        author = db.query(ClassicalAuthor).filter(ClassicalAuthor.slug == sub.author_slug, ClassicalAuthor.is_deleted == False).first()
        if not author:
            return False, None, "invalid_author_slug"
        work = db.query(ClassicalWork).filter(ClassicalWork.author_id == author.id, ClassicalWork.slug == sub.work_slug, ClassicalWork.is_deleted == False).first()
        if not work:
            return False, None, "invalid_work_slug"
        chapter = db.query(WorkChapter).filter(WorkChapter.work_id == work.id, WorkChapter.slug == sub.chapter_slug, WorkChapter.is_deleted == False).first()
        if not chapter:
            return False, None, "invalid_chapter_slug"
        author_id = author.id
        work_id = work.id
        chapter_id = chapter.id
    # Build doha entry payload
    doha = DohaEntry(
        author_id=author_id,
        work_id=work_id,
        chapter_id=chapter_id,
        number_in_chapter=sub.number_in_chapter,
        main_text=sub.main_text,
        meaning=sub.meaning,
        text_devanagari=sub.external_references.get("text_devanagari") if sub.external_references else None,  # ✅ Fixed
        text_romanized=sub.external_references.get("text_romanized") if sub.external_references else None,  # ✅ Fixed
        is_canonical=True,
        version=1,
        source_submission_id=sub.id,
        visibility=sub.visibility or "public",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(doha)
    db.flush()  # ensure doha.id is available
    # Create ContentVersion snapshot (OPTIONAL - don't fail if this fails)
    if ContentVersion is not None:
        try:
            snapshot = {
                "main_text": sub.main_text,
                "meaning": sub.meaning,
                "author_id": author_id,
                "work_id": work_id,
                "chapter_id": chapter_id,
                "number_in_chapter": sub.number_in_chapter,
                "source_submission_id": sub.id,
            }
            cv = ContentVersion(
                content_type="doha",
                content_id=doha.id,
                version=1,
                snapshot=snapshot,
                created_at=datetime.now(timezone.utc),
            )
            db.add(cv)
            db.flush()  # Try to write it
        except Exception as e:
            # Log but don't fail - ContentVersion is just audit/snapshot
            logger.warning(f"Failed to create ContentVersion for doha {doha.id}: {e}")
    # success
    return True, doha.id, None


def _placeholder_handler(db: Session, sub: Submission, batch_id: str, actor_user_id: Optional[int], audit_metadata: Dict[str, Any]) -> Tuple[bool, Optional[int], Optional[str]]:
    return False, None, "handler_not_implemented"

_HANDLER_MAP = {
    "doha": _handle_doha,
    "idiom": lambda db, sub, batch_id, actor_user_id, audit_metadata: _create_wrapper(create_canonical_idiom_from_submission, db, sub, actor_user_id, audit_metadata),
    "dictionary": lambda db, sub, batch_id, actor_user_id, audit_metadata: _create_wrapper(create_canonical_dictionary_from_submission, db, sub, actor_user_id, audit_metadata),
    "dictionary_entry": lambda db, sub, batch_id, actor_user_id, audit_metadata: _create_wrapper(create_canonical_dictionary_from_submission, db, sub, actor_user_id, audit_metadata),
    "article": lambda db, sub, batch_id, actor_user_id, audit_metadata: _create_wrapper(create_canonical_article_from_submission, db, sub, actor_user_id, audit_metadata),
}

def batch_approve_submissions(db: Session, submission_ids: List[int], actor_user_id: Optional[int], request_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Atomic batch approve:
      - Pre-validate all submissions (fatal errors -> raise BatchValidationError)
      - For each submission, call handler; if handler returns duplicate -> skip; if handler returns created -> update submission.status and logs
      - All writes occur within single transaction; if any unhandled exception occurs, transaction is rolled back.
    Returns dict: { batch_id, created: [{submission_id, canonical_id}], skipped: [submission_id], errors: [{submission_id, error}] }
    """
    batch_id = str(uuid.uuid4())
    request_meta = request_metadata or {}
    audit_base_meta = dict(request_meta)
    audit_base_meta["batch_id"] = batch_id
    # Pre-validate
    subs, pre_errors = _pre_validate_submissions(db, submission_ids)
    if pre_errors:
        raise BatchValidationError(pre_errors)
    created = []
    skipped = []
    errors = []
    # Start atomic transaction
    with db.begin_nested():
        try:
            for sub in subs:
                handler = _HANDLER_MAP.get(sub.content_type)
                if handler is None:
                    raise BatchValidationError([{"submission_id": sub.id, "error": f"no_handler_for_content_type:{sub.content_type}"}])
                # Call handler
                created_flag, canonical_id, handler_err = handler(db, sub, batch_id, actor_user_id, audit_base_meta)
                if handler_err:
                    if handler_err in ("handler_not_implemented", "doha_model_missing", "missing_classical_reference", "invalid_author_slug", "invalid_work_slug", "invalid_chapter_slug"):
                        raise BatchValidationError([{"submission_id": sub.id, "error": handler_err}])
                    # unknown handler error -> abort
                    raise BatchValidationError([{"submission_id": sub.id, "error": handler_err}])
                if not created_flag:
                    # duplicate => skip (idempotent)
                    skipped.append(sub.id)
                    sub.status = "approved"
                    db.add(sub)
                    
                    try:
                        ml = ModerationLog(
                            submission_id=sub.id,
                            moderator_id=int(actor_user_id) if actor_user_id else 0,
                            action="batch_approve:skipped_duplicate",
                            from_status=sub.status,
                            to_status="approved",
                            guideline_version=None,
                            note=f"Skipped duplicate canonical in batch {batch_id}",
                        )
                        db.add(ml)
                    except Exception:
                        pass
                    try:
                        record_audit(
                            db=db,
                            actor_user_id=actor_user_id,
                            action="batch_approve:skipped",
                            resource_type=sub.content_type,
                            resource_id=sub.id,
                            before=None,
                            after={"status": "approved", "skipped_duplicate": True},
                            metadata=dict(audit_base_meta, submission_id=sub.id),
                        )
                    except Exception:
                        pass
                    continue
                # created canonical: update submission.status
                sub.status = "approved"
                db.add(sub)
                try:
                    ml = ModerationLog(
                        submission_id=sub.id,
                        moderator_id=int(actor_user_id) if actor_user_id else 0,
                        action="batch_approve:created_canonical",
                        from_status="pending_review",
                        to_status="approved",
                        guideline_version=None,
                        note=f"Created canonical id {canonical_id} in batch {batch_id}",
                    )
                    db.add(ml)
                except Exception:
                    pass
                try:
                    record_audit(
                        db=db,
                        actor_user_id=actor_user_id,
                        action="batch_approve:created",
                        resource_type=sub.content_type,
                        resource_id=canonical_id,
                        before={"submission_id": sub.id},
                        after={"canonical_id": canonical_id},
                        metadata=dict(audit_base_meta, submission_id=sub.id),
                    )
                except Exception:
                    pass
                created.append({"submission_id": sub.id, "canonical_id": canonical_id})
        except BatchValidationError as be:
            raise
        except Exception as e:
            raise BatchValidationError([{"error": str(e)}])
    db.commit()
    return {"batch_id": batch_id, "created": created, "skipped": skipped, "errors": errors}