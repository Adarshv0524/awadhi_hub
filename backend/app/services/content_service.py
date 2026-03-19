# app/services/content_service.py
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from fastapi import HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, ValidationError

from app.db.models import (
    Submission,
    DohaEntry,
    DictionaryEntry,
    IdiomEntry,
    ArticleEntry,
    ContentVersion,
    ClassicalAuthor,
    ClassicalWork,
    WorkChapter,
    User,
    ModerationLog,
)
from app.services.audit_service import record_audit
from app.utils.text_normalize import normalize_roman

logger = logging.getLogger("app.content_service")

# ---- Validators (pydantic) ----
class DictionarySense(BaseModel):
    definition: str
    pos: Optional[str] = None
    examples: Optional[list] = None
    synonyms: Optional[list] = None

class DictionaryPayload(BaseModel):
    lemma_devanagari: str
    lemma_roman: Optional[str] = None
    language: Optional[str] = "hi"
    senses: list[DictionarySense]
    pronunciation: Optional[str] = None
    examples: Optional[list] = None

class IdiomPayload(BaseModel):
    # Per your instruction text_roman is MANDATORY
    text_devanagari: str
    text_roman: str
    meaning: Optional[str] = None
    examples: Optional[list] = None
    region: Optional[str] = None

class ArticlePayload(BaseModel):
    title: str
    body: str
    title_devanagari: Optional[str] = None
    title_roman: Optional[str] = None
    tags: Optional[list] = None
    excerpt: Optional[str] = None

# ---- Helpers ----
def _resolve_classical_hierarchy_for_submission(db: Session, submission: Submission):
    """
    Resolve classical hierarchy for a submission.
    Auto-creates missing authors, works, and chapters based on submission metadata.
    """
    if not submission.is_classical:
        return None, None, None, None
    
    if not (
        submission.author_slug
        and submission.work_slug
        and submission.chapter_slug
        and submission.number_in_chapter is not None
    ):
        logger.error("Classical submission missing hierarchy fields: submission_id=%s", submission.id)
        raise HTTPException(
            status_code=400,
            detail="Approved classical submission is missing hierarchy slugs/number",
        )
    
    # 1. Get or create author
    author = (
        db.query(ClassicalAuthor)
        .filter(
            ClassicalAuthor.slug == submission.author_slug,
            ClassicalAuthor.is_deleted == False,
        )
        .first()
    )
    
    if not author:
        logger.info("Author not found, creating: %s (submission_id=%s)", submission.author_slug, submission.id)
        # Create author from slug (convert slug to title case name)
        author_name = submission.author_slug.replace('-', ' ').title()
        author = ClassicalAuthor(
            slug=submission.author_slug,
            name=author_name,
            short_bio=f"Auto-created from submission {submission.id}",
            language="hi",  # default to Hindi
            is_deleted=False,
        )
        db.add(author)
        db.flush()  # Get author.id
        logger.info("Created author: id=%s, slug=%s, name=%s", author.id, author.slug, author.name)
    
    # 2. Get or create work
    work = (
        db.query(ClassicalWork)
        .filter(
            ClassicalWork.author_id == author.id,
            ClassicalWork.slug == submission.work_slug,
            ClassicalWork.is_deleted == False,
        )
        .first()
    )
    
    if not work:
        logger.info("Work not found, creating: %s (author_id=%s) (submission_id=%s)", 
                   submission.work_slug, author.id, submission.id)
        # Create work from slug
        work_title = submission.work_slug.replace('-', ' ').title()
        work = ClassicalWork(
            author_id=author.id,
            slug=submission.work_slug,
            title=work_title,
            description=f"Auto-created from submission {submission.id}",
            work_type="classical",
            original_script="devanagari",
            is_deleted=False,
        )
        db.add(work)
        db.flush()  # Get work.id
        logger.info("Created work: id=%s, slug=%s, title=%s", work.id, work.slug, work.title)
    
    # 3. Get or create chapter
    chapter = (
        db.query(WorkChapter)
        .filter(
            WorkChapter.work_id == work.id,
            WorkChapter.slug == submission.chapter_slug,
            WorkChapter.is_deleted == False,
        )
        .first()
    )
    
    if not chapter:
        logger.info("Chapter not found, creating: %s (work_id=%s) (submission_id=%s)", 
                   submission.chapter_slug, work.id, submission.id)
        # Create chapter from slug
        chapter_title = submission.chapter_slug.replace('-', ' ').title()
        
        # Determine chapter number - use existing max + 1 or default to 1
        max_chapter = (
            db.query(WorkChapter)
            .filter(WorkChapter.work_id == work.id)
            .order_by(WorkChapter.number.desc())
            .first()
        )
        chapter_number = (max_chapter.number + 1) if max_chapter else 1
        
        chapter = WorkChapter(
            work_id=work.id,
            slug=submission.chapter_slug,
            title=chapter_title,
            number=chapter_number,
            is_deleted=False,
        )
        db.add(chapter)
        db.flush()  # Get chapter.id
        logger.info("Created chapter: id=%s, slug=%s, title=%s, number=%s", 
                   chapter.id, chapter.slug, chapter.title, chapter.number)
    
    hierarchy_path = f"{author.slug}/{work.slug}/{chapter.slug}/{submission.number_in_chapter}"
    logger.info("Resolved hierarchy: %s (author_id=%s, work_id=%s, chapter_id=%s)", 
               hierarchy_path, author.id, work.id, chapter.id)
    
    return author, work, chapter, hierarchy_path



# ---- Creation functions ----
def create_canonical_doha_from_submission(
    db: Session,
    submission: Submission,
    moderator: User,
) -> Optional[DohaEntry]:
    """
    Idempotent: if a DohaEntry already exists for this submission, return it.
    Only supports submission.content_type == 'doha' for now.
    """
    try:
        logger.info("create_canonical_doha_from_submission called for submission_id=%s", submission.id)
        if submission.content_type != "doha":
            logger.debug("Skipping creation - not a doha. submission_id=%s content_type=%s", submission.id, submission.content_type)
            return None
        existing = (
            db.query(DohaEntry)
            .filter(
                DohaEntry.source_submission_id == submission.id,
                DohaEntry.is_deleted == False,
            )
            .first()
        )
        if existing:
            logger.info("DohaEntry already exists for submission_id=%s doha_id=%s", submission.id, existing.id)
            return existing
        author = work = chapter = None
        hierarchy_path = None
        author_id = work_id = chapter_id = None
        if submission.is_classical:
            author, work, chapter, hierarchy_path = _resolve_classical_hierarchy_for_submission(db, submission)
            author_id = author.id
            work_id = work.id
            chapter_id = chapter.id
        logger.info(
            "Inserting doha entry for submission=%s classical=%s hierarchy_path=%s",
            submission.id,
            submission.is_classical,
            hierarchy_path,
        )
        doha = DohaEntry(
            hierarchy_path=hierarchy_path,
            author_id=author_id,
            work_id=work_id,
            chapter_id=chapter_id,
            number_in_chapter=submission.number_in_chapter,
            main_text=submission.main_text,
            meaning=submission.meaning,
            text_devanagari=submission.main_text,  # assume Devanagari for now
            text_romanized=None,
            status="active",
            visibility="public",
            version=1,
            is_canonical=True,
            variant_group_id=None,
            confidence_level=100,
            source_reference=None,
            source_submission_id=submission.id,
            created_by=submission.contributor_id,
            verified_by=int(moderator.id) if moderator and moderator.id else None,
        )
        db.add(doha)
        logger.debug("Flushing session to get doha.id (submission=%s)", submission.id)
        db.flush()  # to get doha.id
        logger.info("Inserted doha row (submission=%s) temporary id=%s", submission.id, getattr(doha, "id", None))
        version = ContentVersion(
            content_type="doha",
            content_id=doha.id,
            version_number=1,
            main_text=submission.main_text,
            meaning=submission.meaning,
            text_devanagari=submission.main_text,
            text_romanized=None,
            created_by=submission.contributor_id,
            notes=f"Created from submission {submission.id}",
        )
        db.add(version)
        logger.info("Inserted content_version (submission=%s) for doha_id=%s", submission.id, doha.id)
        # Do NOT commit here — caller will commit the transaction.
        return doha
    except Exception as e:
        logger.exception("Failed to create canonical doha for submission %s: %s", getattr(submission, "id", None), e)
        # Re-raise so caller sees it (and transaction will be rolled back)
        raise

def create_canonical_dictionary_from_submission(db: Session, submission, moderator_user) -> int:
    """
    Validate submission references and create DictionaryEntry.
    Returns created dictionary id.
    Raises ValidationError (pydantic) on invalid payload.
    """
    # Accept both new and legacy keys
    refs = submission.external_references or getattr(submission, "references", None) or {}
    # accept structured payload or fallback to main_text as lemma_devanagari
    payload_dict = {
        "lemma_devanagari": refs.get("lemma_devanagari") or submission.main_text,
        "lemma_roman": refs.get("lemma_roman") or refs.get("lemmaRoman"),
        "language": refs.get("language") or "hi",
        "senses": refs.get("senses") or refs.get("definitions") or [],
        "pronunciation": refs.get("pronunciation"),
        "examples": refs.get("examples"),
    }
    payload = DictionaryPayload(**payload_dict)
    if len(payload.senses) > 10:
        raise ValidationError("Too many senses (max 10)")
    # check duplicate
    existing = db.query(DictionaryEntry).filter(DictionaryEntry.source_submission_id == submission.id).first()
    if existing:
        return existing.id
    ent = DictionaryEntry(
        lemma_devanagari=payload.lemma_devanagari,
        lemma_roman=payload.lemma_roman,
        lemma_roman_norm=normalize_roman(payload.lemma_roman),
        language=payload.language,
        senses=[s.model_dump() for s in payload.senses],
        pronunciation=payload.pronunciation,
        examples=payload.examples,
        contributor_id=submission.contributor_id,
        author_id=getattr(submission, "author_id", None),
        work_id=getattr(submission, "work_id", None),
        chapter_id=getattr(submission, "chapter_id", None),
        number_in_chapter=getattr(submission, "number_in_chapter", None),
        source_submission_id=submission.id,
        visibility=submission.visibility or "public",
        version=1,
    )
    db.add(ent)
    db.flush()
    # snapshot content_version if model exists
    try:
        if ContentVersion is not None:
            snapshot = {
                "lemma_devanagari": ent.lemma_devanagari,
                "lemma_roman": ent.lemma_roman,
                "senses": ent.senses,
            }
            cv = ContentVersion(
                content_type="dictionary",
                content_id=ent.id,
                version_number=1,
                main_text=ent.lemma_devanagari,
                meaning=None,
                text_devanagari=ent.lemma_devanagari,
                text_romanized=ent.lemma_roman,
                created_by=submission.contributor_id,
                notes=f"Created from submission {submission.id}",
                created_at=datetime.now(timezone.utc),
            )
            db.add(cv)
            db.flush()
    except Exception:
        logger.exception("ContentVersion write failed for dictionary entry; continuing")
    # moderation log
    try:
        ml = ModerationLog(
            submission_id=submission.id,
            moderator_id=int(getattr(moderator_user, "id", 0)) if moderator_user else 0,
            action="approve:create_dictionary",
            from_status=submission.status,
            to_status="approved",
            guideline_version=None,
            note=f"Created dictionary id {ent.id}",
        )
        db.add(ml)
    except Exception:
        logger.exception("Failed to write moderation log for dictionary creation")
    # audit
    try:
        record_audit(
            db=db,
            actor_user_id=getattr(moderator_user, "id", None),
            action="canonical:create:dictionary",
            resource_type="dictionary",
            resource_id=ent.id,
            before={"submission_id": submission.id},
            after={"dictionary_id": ent.id},
            metadata={"submission_id": submission.id},
        )
    except Exception:
        logger.exception("audit write failed for dictionary")
    return ent.id

def create_canonical_idiom_from_submission(db: Session, submission, moderator_user) -> int:
    # accept both new and legacy keys
    refs = submission.external_references or getattr(submission, "references", None) or {}
    payload_dict = {
        "text_devanagari": refs.get("text_devanagari") or submission.main_text,
        "text_roman": refs.get("text_roman") or refs.get("textRoman"),
        "meaning": submission.meaning or refs.get("meaning"),
        "examples": refs.get("examples"),
        "region": refs.get("region"),
    }
    # Pydantic will validate text_roman mandatory as per updated IdiomPayload
    payload = IdiomPayload(**payload_dict)
    # check duplicate
    existing = db.query(IdiomEntry).filter(IdiomEntry.source_submission_id == submission.id).first()
    if existing:
        return existing.id
    ent = IdiomEntry(
        text_devanagari=payload.text_devanagari,
        text_roman=payload.text_roman,
        text_roman_norm=normalize_roman(payload.text_roman),
        meaning=payload.meaning,
        examples=payload.examples,
        region=payload.region,
        contributor_id=submission.contributor_id,
        author_id=getattr(submission, "author_id", None),
        work_id=getattr(submission, "work_id", None),
        chapter_id=getattr(submission, "chapter_id", None),
        number_in_chapter=getattr(submission, "number_in_chapter", None),
        source_submission_id=submission.id,
        visibility=submission.visibility or "public",
        version=1,
    )
    db.add(ent)
    db.flush()
    # content version
    try:
        if ContentVersion is not None:
            snapshot = {"text_devanagari": ent.text_devanagari, "meaning": ent.meaning}
            cv = ContentVersion(
                content_type="idiom",
                content_id=ent.id,
                version_number=1,
                main_text=ent.text_devanagari,
                meaning=ent.meaning,
                text_devanagari=ent.text_devanagari,
                text_romanized=ent.text_roman,
                created_by=submission.contributor_id,
                notes=f"Created from submission {submission.id}",
                created_at=datetime.now(timezone.utc)
            )
            db.add(cv)
            db.flush()
    except Exception:
        logger.exception("ContentVersion write failed for idiom entry; continuing")
    # moderation log + audit
    try:
        ml = ModerationLog(submission_id=submission.id, moderator_id=int(getattr(moderator_user, "id", 0)), action="approve:create_idiom", from_status=submission.status, to_status="approved", guideline_version=None, note=f"Created idiom id {ent.id}")
        db.add(ml)
    except Exception:
        logger.exception("Failed to write moderation log for idiom creation")
    try:
        record_audit(db=db, actor_user_id=getattr(moderator_user, "id", None), action="canonical:create:idiom", resource_type="idiom", resource_id=ent.id, before={"submission_id": submission.id}, after={"idiom_id": ent.id}, metadata={"submission_id": submission.id})
    except Exception:
        logger.exception("audit write failed for idiom")
    return ent.id

def create_canonical_article_from_submission(db: Session, submission, moderator_user) -> int:
    refs = submission.external_references or getattr(submission, "references", None) or {}
    title = refs.get("title") or (submission.main_text.splitlines()[0] if submission.main_text else None)
    body = submission.main_text or refs.get("body")
    if not title or not body:
        # pydantic.ValidationError typically used elsewhere; raise general error so calling batch fails (atomic)
        raise ValueError("Article requires title and body")
    payload = ArticlePayload(title=title, body=body, title_devanagari=refs.get("title_devanagari"), title_roman=refs.get("title_roman"), tags=refs.get("tags"), excerpt=refs.get("excerpt"))
    existing = db.query(ArticleEntry).filter(ArticleEntry.source_submission_id == submission.id).first()
    if existing:
        return existing.id
    # Auto-generate excerpt if not supplied (per requirement)
    excerpt = payload.excerpt
    if not excerpt and payload.body:
        excerpt = payload.body.strip()[:300]
    ent = ArticleEntry(
        title=payload.title,
        title_devanagari=payload.title_devanagari,
        title_roman=payload.title_roman,
        title_roman_norm=normalize_roman(payload.title_roman),
        body=payload.body,
        excerpt=excerpt,
        author_id=None,  # Keep as user-level author link if needed elsewhere
        tags=payload.tags,
        contributor_id=submission.contributor_id,
        source_submission_id=submission.id,
        visibility=submission.visibility or "public",
        version=1,
    )
    db.add(ent)
    db.flush()
    # content version
    try:
        if ContentVersion is not None:
            snapshot = {"title": ent.title, "body": ent.body}
            cv = ContentVersion(
                content_type="article",
                content_id=ent.id,
                version_number=1,
                main_text=ent.title,
                meaning=ent.body[:500] if ent.body else None,  # Store excerpt in meaning
                text_devanagari=ent.title_devanagari,
                text_romanized=ent.title_roman,
                created_by=submission.contributor_id,
                notes=f"Created from submission {submission.id}",
                created_at=datetime.now(timezone.utc)
            )
            db.add(cv)
            db.flush()
    except Exception:
        logger.exception("ContentVersion write failed for article; continuing")
    # moderation log + audit
    try:
        ml = ModerationLog(submission_id=submission.id, moderator_id=int(getattr(moderator_user, "id", 0)), action="approve:create_article", from_status=submission.status, to_status="approved", guideline_version=None, note=f"Created article id {ent.id}")
        db.add(ml)
    except Exception:
        logger.exception("Failed to write moderation log for article creation")
    try:
        record_audit(db=db, actor_user_id=getattr(moderator_user, "id", None), action="canonical:create:article", resource_type="article", resource_id=ent.id, before={"submission_id": submission.id}, after={"article_id": ent.id}, metadata={"submission_id": submission.id})
    except Exception:
        logger.exception("audit write failed for article")
    return ent.id