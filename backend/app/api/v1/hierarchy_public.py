# app/api/v1/hierarchy_public.py

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import ClassicalAuthor, ClassicalWork, WorkChapter

router = APIRouter(prefix="/authors", tags=["authors"])


# ---------- Pydantic response models ----------

class AuthorListOut(BaseModel):
    id: int
    slug: str
    name: str
    short_bio: Optional[str]
    language: Optional[str]

    class Config:
        orm_mode = True


class AuthorDetailOut(BaseModel):
    id: int
    slug: str
    name: str
    short_bio: Optional[str]
    long_bio: Optional[str]
    language: Optional[str]

    class Config:
        orm_mode = True


class WorkOut(BaseModel):
    id: int
    slug: str
    title: str
    description: Optional[str]
    work_type: Optional[str]

    class Config:
        orm_mode = True


class WorkDetailOut(WorkOut):
    original_script: Optional[str]


class ChapterOut(BaseModel):
    id: int
    slug: str
    title: str
    number: int

    class Config:
        orm_mode = True


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

    q = db.query(ClassicalWork).filter(
        ClassicalWork.author_id == author.id,
        ClassicalWork.is_deleted == False,
    )
    if work_type:
        q = q.filter(ClassicalWork.work_type == work_type)

    works = (
        q.order_by(ClassicalWork.title.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return works


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

    chapters = (
        db.query(WorkChapter)
        .filter(
            WorkChapter.work_id == work.id,
            WorkChapter.is_deleted == False,
        )
        .order_by(WorkChapter.number.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return chapters
