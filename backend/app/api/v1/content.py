# app/api/v1/content.py

from datetime import datetime
from typing import Optional, List, Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy import and_, asc, desc
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import (
    DohaEntry,
    DictionaryEntry,
    IdiomEntry,
    ArticleEntry,
    ContentVersion,
    ClassicalAuthor,
    ClassicalWork,
    WorkChapter,
    EngagementKPI,
)
from app.schemas.content_navigation import ContentNavigationOut
from app.schemas.content_chapter import ChapterDohaItem, ChapterDohasOut
from app.services.content_service import get_content_navigation
from app.services.engagement_service import record_view

router = APIRouter(prefix="/content", tags=["content"])


class DohaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    hierarchy_path: Optional[str]
    author_id: Optional[int]
    author_name: Optional[str]
    work_id: Optional[int]
    work_name: Optional[str]
    chapter_id: Optional[int]
    chapter_name: Optional[str]
    number_in_chapter: Optional[int]
    main_text: str
    meaning: Optional[str]
    text_devanagari: Optional[str]
    text_romanized: Optional[str]
    status: str
    visibility: str
    version: int
    is_canonical: bool
    confidence_level: Optional[int]
    source_reference: Optional[dict]
    verified_by: Optional[int]
    verified_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    views_count: int = 0
    likes_count: int = 0
    shares_count: int = 0
    bookmarks_count: int = 0
    search_hits_count: int = 0
    weight_score: float = 0.0

class ContentVersionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    content_type: str
    content_id: int
    version_number: int
    main_text: Optional[str]
    meaning: Optional[str]
    text_devanagari: Optional[str]
    text_romanized: Optional[str]
    created_by: Optional[int]

def _doha_query_with_metadata(db: Session):
    return (
        db.query(
            DohaEntry,
            ClassicalAuthor.name.label("author_name"),
            ClassicalWork.title.label("work_name"),
            WorkChapter.title.label("chapter_name"),
            EngagementKPI.views_count.label("views_count"),
            EngagementKPI.likes_count.label("likes_count"),
            EngagementKPI.shares_count.label("shares_count"),
            EngagementKPI.bookmarks_count.label("bookmarks_count"),
            EngagementKPI.search_hits_count.label("search_hits_count"),
            EngagementKPI.weight_score.label("weight_score"),
        )
        .outerjoin(ClassicalAuthor, ClassicalAuthor.id == DohaEntry.author_id)
        .outerjoin(ClassicalWork, ClassicalWork.id == DohaEntry.work_id)
        .outerjoin(WorkChapter, WorkChapter.id == DohaEntry.chapter_id)
        .outerjoin(
            EngagementKPI,
            and_(
                EngagementKPI.content_type == "doha",
                EngagementKPI.content_id == DohaEntry.id,
            ),
        )
    )


def _serialize_doha_with_metadata(row) -> dict:
    (
        doha,
        author_name,
        work_name,
        chapter_name,
        views_count,
        likes_count,
        shares_count,
        bookmarks_count,
        search_hits_count,
        weight_score,
    ) = row

    return {
        "id": doha.id,
        "hierarchy_path": doha.hierarchy_path,
        "author_id": doha.author_id,
        "author_name": author_name,
        "work_id": doha.work_id,
        "work_name": work_name,
        "chapter_id": doha.chapter_id,
        "chapter_name": chapter_name,
        "number_in_chapter": doha.number_in_chapter,
        "main_text": doha.main_text,
        "meaning": doha.meaning,
        "text_devanagari": doha.text_devanagari,
        "text_romanized": doha.text_romanized,
        "status": doha.status,
        "visibility": doha.visibility,
        "version": doha.version,
        "is_canonical": doha.is_canonical,
        "confidence_level": doha.confidence_level,
        "source_reference": doha.source_reference,
        "verified_by": doha.verified_by,
        "verified_at": doha.verified_at,
        "created_at": doha.created_at,
        "updated_at": doha.updated_at,
        "views_count": views_count or 0,
        "likes_count": likes_count or 0,
        "shares_count": shares_count or 0,
        "bookmarks_count": bookmarks_count or 0,
        "search_hits_count": search_hits_count or 0,
        "weight_score": weight_score or 0.0,
    }


def _serialize_chapter_doha(doha: DohaEntry) -> ChapterDohaItem:
    return ChapterDohaItem(
        id=doha.id,
        hierarchy_path=doha.hierarchy_path,
        chapter_id=doha.chapter_id,
        number_in_chapter=doha.number_in_chapter,
        main_text=doha.main_text,
        meaning=doha.meaning,
        text_devanagari=doha.text_devanagari,
        text_romanized=doha.text_romanized,
    )


def _get_chapter_dohas_payload(
    db: Session,
    chapter: WorkChapter,
    offset: int,
    limit: int,
) -> ChapterDohasOut:
    q = db.query(DohaEntry).filter(
        DohaEntry.chapter_id == chapter.id,
        DohaEntry.is_deleted == False,
        DohaEntry.status == "active",
    )
    total = q.count()
    items = (
        q.order_by(DohaEntry.number_in_chapter.asc(), DohaEntry.id.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return ChapterDohasOut(
        chapter_id=chapter.id,
        chapter_slug=chapter.slug,
        total=total,
        offset=offset,
        limit=limit,
        items=[_serialize_chapter_doha(i) for i in items],
    )



@router.get("/poetry", response_model=List[DohaOut])
@router.get("/doha", response_model=List[DohaOut], include_in_schema=False)
def list_poetry(
    db: Session = Depends(get_db),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    visibility: Optional[str] = Query(None),
    sort: Literal[
        "created_at",
        "updated_at",
        "views_count",
        "likes_count",
        "shares_count",
        "bookmarks_count",
        "search_hits_count",
        "weight_score",
    ] = Query("created_at"),
    order: Literal["asc", "desc"] = Query("desc"),
):
    """List canonical poetry entries from the legacy canonical table."""
    q = _doha_query_with_metadata(db).filter(
        DohaEntry.is_deleted == False,
        DohaEntry.status == "active",
    )
    if visibility:
        q = q.filter(DohaEntry.visibility == visibility)

    sort_columns = {
        "created_at": DohaEntry.created_at,
        "updated_at": DohaEntry.updated_at,
        "views_count": EngagementKPI.views_count,
        "likes_count": EngagementKPI.likes_count,
        "shares_count": EngagementKPI.shares_count,
        "bookmarks_count": EngagementKPI.bookmarks_count,
        "search_hits_count": EngagementKPI.search_hits_count,
        "weight_score": EngagementKPI.weight_score,
    }
    order_fn = desc if order == "desc" else asc
    sort_col = sort_columns[sort]

    rows = q.order_by(order_fn(sort_col), DohaEntry.id.desc()).offset(offset).limit(limit).all()
    return [_serialize_doha_with_metadata(row) for row in rows]


@router.get("/poetry/{poetry_id}", response_model=DohaOut)
@router.get("/doha/{poetry_id}", response_model=DohaOut, include_in_schema=False)
def get_poetry(poetry_id: int, db: Session = Depends(get_db)):
    doha_id = poetry_id
    row = (
        _doha_query_with_metadata(db)
        .filter(
            DohaEntry.id == doha_id,
            DohaEntry.is_deleted == False,
        )
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Poetry not found")

    doha = row[0]
    if doha.status != "active":
        raise HTTPException(status_code=404, detail="Poetry not found")
    record_view(db, "doha", int(doha.id))
    db.commit()
    return _serialize_doha_with_metadata(row)


@router.get("/poetry/{poetry_id}/navigation", response_model=ContentNavigationOut)
@router.get("/doha/{poetry_id}/navigation", response_model=ContentNavigationOut, include_in_schema=False)
def get_poetry_navigation_endpoint(poetry_id: int, db: Session = Depends(get_db)):
    """Return previous/current/next poetry cards based on chapter sequence."""
    doha_id = poetry_id
    nav = get_content_navigation(db, "doha", doha_id)
    record_view(db, "doha", int(doha_id))
    db.commit()
    return nav


@router.get("/dictionary/{entry_id}/navigation", response_model=ContentNavigationOut)
def get_dictionary_navigation_endpoint(entry_id: int, db: Session = Depends(get_db)):
    nav = get_content_navigation(db, "dictionary", entry_id)
    record_view(db, "dictionary", int(entry_id))
    db.commit()
    return nav


@router.get("/idiom/{entry_id}/navigation", response_model=ContentNavigationOut)
def get_idiom_navigation_endpoint(entry_id: int, db: Session = Depends(get_db)):
    nav = get_content_navigation(db, "idiom", entry_id)
    record_view(db, "idiom", int(entry_id))
    db.commit()
    return nav


@router.get("/article/{entry_id}/navigation", response_model=ContentNavigationOut)
def get_article_navigation_endpoint(entry_id: int, db: Session = Depends(get_db)):
    nav = get_content_navigation(db, "article", entry_id)
    record_view(db, "article", int(entry_id))
    db.commit()
    return nav


@router.get("/chapters/{chapter_id}/poetry", response_model=ChapterDohasOut)
@router.get("/chapters/{chapter_id}/dohas", response_model=ChapterDohasOut, include_in_schema=False)
def list_chapter_poetry(
    chapter_id: int,
    db: Session = Depends(get_db),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
):
    chapter = (
        db.query(WorkChapter)
        .filter(WorkChapter.id == chapter_id, WorkChapter.is_deleted == False)
        .first()
    )
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")

    return _get_chapter_dohas_payload(db, chapter, offset, limit)


@router.get(
    "/by-path/{author_slug}/{work_slug}/{chapter_slug}/poetry",
    response_model=ChapterDohasOut,
)
@router.get(
    "/by-path/{author_slug}/{work_slug}/{chapter_slug}/dohas",
    response_model=ChapterDohasOut,
    include_in_schema=False,
)
def list_chapter_poetry_by_path(
    author_slug: str,
    work_slug: str,
    chapter_slug: str,
    db: Session = Depends(get_db),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
):
    author = (
        db.query(ClassicalAuthor)
        .filter(ClassicalAuthor.slug == author_slug, ClassicalAuthor.is_deleted == False)
        .first()
    )
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

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
        raise HTTPException(status_code=404, detail="Work not found")

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
        raise HTTPException(status_code=404, detail="Chapter not found")

    return _get_chapter_dohas_payload(db, chapter, offset, limit)


@router.get("/poetry/{poetry_id}/history", response_model=List[ContentVersionOut])
@router.get("/doha/{poetry_id}/history", response_model=List[ContentVersionOut], include_in_schema=False)
def get_poetry_history(poetry_id: int, db: Session = Depends(get_db)):
    doha_id = poetry_id
    # Optional: ensure doha exists first
    doha = db.query(DohaEntry).filter(DohaEntry.id == doha_id, DohaEntry.is_deleted == False).first()
    if not doha:
        raise HTTPException(status_code=404, detail="Poetry not found")

    versions = (
        db.query(ContentVersion)
        .filter(
            ContentVersion.content_type == "doha",
            ContentVersion.content_id == doha_id,
        )
        .order_by(ContentVersion.version_number.asc())
        .all()
    )
    return versions


@router.get("/poetry/by-path/{hierarchy_path:path}", response_model=DohaOut)
@router.get("/by-path/{hierarchy_path:path}", response_model=DohaOut, include_in_schema=False)
def get_poetry_by_path(hierarchy_path: str, db: Session = Depends(get_db)):
    row = (
        _doha_query_with_metadata(db)
        .filter(
            DohaEntry.hierarchy_path == hierarchy_path,
            DohaEntry.is_deleted == False,
        )
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Poetry not found for this path")

    doha = row[0]
    if doha.status != "active":
        raise HTTPException(status_code=404, detail="Poetry not found for this path")
    return _serialize_doha_with_metadata(row)
