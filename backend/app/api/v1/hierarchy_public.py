# app/api/v1/hierarchy_public.py

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.session import get_db
from app.db.models import ClassicalAuthor, ClassicalWork, WorkChapter, PoetryNode
from app.services.hierarchy_cache import (
    get_cached_value,
    set_cached_value,
    make_works_cache_key,
    make_chapters_cache_key,
)

router = APIRouter(prefix="/authors", tags=["authors"])


# ---------- Pydantic response models ----------

class AuthorListOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    name: str
    short_bio: Optional[str]
    language: Optional[str]

class AuthorDetailOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    name: str
    short_bio: Optional[str]
    long_bio: Optional[str]
    language: Optional[str]

class WorkOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    title: str
    description: Optional[str]
    work_type: Optional[str]
    poetry_nodes_count: int = 0

class WorkDetailOut(WorkOut):
    original_script: Optional[str]


class ChapterOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    title: str
    number: int
    poetry_nodes_count: int = 0

# ---------- Public endpoints ----------

@router.get("", response_model=List[AuthorListOut])
def list_authors(
    db: Session = Depends(get_db),
    q: Optional[str] = Query(None, description="Search in author name"),
    language: Optional[str] = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    """
    Public: list authors, with optional search and language filter.
    """
    query = db.query(ClassicalAuthor).filter(ClassicalAuthor.is_deleted == False)

    if language:
        query = query.filter(ClassicalAuthor.language == language)

    if q:
        pattern = f"%{q}%"
        query = query.filter(ClassicalAuthor.name.ilike(pattern))

    authors = (
        query.order_by(ClassicalAuthor.name.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return authors


@router.get("/{author_slug}", response_model=AuthorDetailOut)
def get_author(author_slug: str, db: Session = Depends(get_db)):
    """
    Public: details of a single author by slug.
    """
    author = (
        db.query(ClassicalAuthor)
        .filter(
            ClassicalAuthor.slug == author_slug,
            ClassicalAuthor.is_deleted == False,
        )
        .first()
    )
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    return author


@router.get("/{author_slug}/works", response_model=List[WorkOut])
def list_works_for_author(
    author_slug: str,
    db: Session = Depends(get_db),
    work_type: Optional[str] = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    """
    Public: list works for an author.
    """
    author = (
        db.query(ClassicalAuthor)
        .filter(
            ClassicalAuthor.slug == author_slug,
            ClassicalAuthor.is_deleted == False,
        )
        .first()
    )
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    cache_key = make_works_cache_key(author_slug=author_slug, work_type=work_type, offset=offset, limit=limit)
    cached = get_cached_value(cache_key)
    if cached is not None:
        return cached

    q = (
        db.query(
            ClassicalWork,
            func.count(PoetryNode.id).label("poetry_nodes_count"),
        )
        .outerjoin(
            PoetryNode,
            (PoetryNode.work_id == ClassicalWork.id)
            & (PoetryNode.is_deleted == False)
            & (PoetryNode.status == "active")
            & (PoetryNode.visibility == "public"),
        )
        .filter(
            ClassicalWork.author_id == author.id,
            ClassicalWork.is_deleted == False,
        )
    )
    if work_type:
        q = q.filter(ClassicalWork.work_type == work_type)

    works = (
        q.group_by(ClassicalWork.id)
        .order_by(ClassicalWork.title.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    response = [
        WorkOut(
            id=work.id,
            slug=work.slug,
            title=work.title,
            description=work.description,
            work_type=work.work_type,
            poetry_nodes_count=int(poetry_nodes_count or 0),
        )
        for work, poetry_nodes_count in works
    ]
    set_cached_value(cache_key, response)
    return response


@router.get("/{author_slug}/works/{work_slug}", response_model=WorkDetailOut)
def get_work(author_slug: str, work_slug: str, db: Session = Depends(get_db)):
    """
    Public: details of a single work under an author.
    """
    author = (
        db.query(ClassicalAuthor)
        .filter(
            ClassicalAuthor.slug == author_slug,
            ClassicalAuthor.is_deleted == False,
        )
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
    return work


@router.get("/{author_slug}/works/{work_slug}/chapters", response_model=List[ChapterOut])
def list_chapters(
    author_slug: str,
    work_slug: str,
    db: Session = Depends(get_db),
    offset: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=500),
):
    """
    Public: list chapters for a given work.
    """
    author = (
        db.query(ClassicalAuthor)
        .filter(
            ClassicalAuthor.slug == author_slug,
            ClassicalAuthor.is_deleted == False,
        )
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

    cache_key = make_chapters_cache_key(author_slug=author_slug, work_slug=work_slug, offset=offset, limit=limit)
    cached = get_cached_value(cache_key)
    if cached is not None:
        return cached

    chapters = (
        db.query(
            WorkChapter,
            func.count(PoetryNode.id).label("poetry_nodes_count"),
        )
        .outerjoin(
            PoetryNode,
            (PoetryNode.chapter_id == WorkChapter.id)
            & (PoetryNode.is_deleted == False)
            & (PoetryNode.status == "active")
            & (PoetryNode.visibility == "public"),
        )
        .filter(
            WorkChapter.work_id == work.id,
            WorkChapter.is_deleted == False,
        )
        .group_by(WorkChapter.id)
        .order_by(WorkChapter.number.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    response = [
        ChapterOut(
            id=chapter.id,
            slug=chapter.slug,
            title=chapter.title,
            number=chapter.number,
            poetry_nodes_count=int(poetry_nodes_count or 0),
        )
        for chapter, poetry_nodes_count in chapters
    ]
    set_cached_value(cache_key, response)
    return response
