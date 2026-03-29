# app/api/v1/hierarchy_admin.py

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Any, Dict
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import ClassicalAuthor, ClassicalWork, WorkChapter, User
from app.core.security import require_role
from app.core.permissions import Role
from app.services.hierarchy_cache import invalidate_hierarchy_cache

router = APIRouter(prefix="/admin/hierarchy", tags=["admin-hierarchy"])


# ---------- Pydantic models ----------

class AuthorCreateIn(BaseModel):
    slug: str
    name: str
    short_bio: Optional[str] = None
    long_bio: Optional[str] = None
    language: Optional[str] = None


class AuthorUpdateIn(BaseModel):
    name: Optional[str] = None
    short_bio: Optional[str] = None
    long_bio: Optional[str] = None
    language: Optional[str] = None
    is_deleted: Optional[bool] = None


class WorkCreateIn(BaseModel):
    slug: str
    title: str
    description: Optional[str] = None
    work_type: Optional[str] = None
    original_script: Optional[str] = None


class WorkUpdateIn(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    work_type: Optional[str] = None
    original_script: Optional[str] = None
    is_deleted: Optional[bool] = None


class ChapterCreateIn(BaseModel):
    slug: str
    title: str
    number: int


class ChapterUpdateIn(BaseModel):
    title: Optional[str] = None
    number: Optional[int] = None
    is_deleted: Optional[bool] = None


# ---------- Admin endpoints ----------


@router.post("/authors", dependencies=[Depends(require_role(Role.ADMIN))])
def create_author(
    data: AuthorCreateIn,
    db: Session = Depends(get_db),
):
    existing = db.query(ClassicalAuthor).filter(ClassicalAuthor.slug == data.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="Author slug already exists")

    author = ClassicalAuthor(
        slug=data.slug,
        name=data.name,
        short_bio=data.short_bio,
        long_bio=data.long_bio,
        language=data.language,
    )
    db.add(author)
    db.commit()
    db.refresh(author)
    return {
        "id": author.id,
        "slug": author.slug,
        "name": author.name,
        "language": author.language,
    }


@router.patch("/authors/{author_id}", dependencies=[Depends(require_role(Role.ADMIN))])
def update_author(
    author_id: int,
    data: AuthorUpdateIn,
    db: Session = Depends(get_db),
):
    author = db.query(ClassicalAuthor).filter(ClassicalAuthor.id == author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    if data.name is not None:
        author.name = data.name
    if data.short_bio is not None:
        author.short_bio = data.short_bio
    if data.long_bio is not None:
        author.long_bio = data.long_bio
    if data.language is not None:
        author.language = data.language
    if data.is_deleted is not None:
        author.is_deleted = data.is_deleted

    db.commit()
    db.refresh(author)
    return {
        "id": author.id,
        "slug": author.slug,
        "name": author.name,
        "language": author.language,
        "is_deleted": author.is_deleted,
    }


@router.post("/authors/{author_id}/works", dependencies=[Depends(require_role(Role.ADMIN))])
def create_work(
    author_id: int,
    data: WorkCreateIn,
    db: Session = Depends(get_db),
):
    author = db.query(ClassicalAuthor).filter(ClassicalAuthor.id == author_id, ClassicalAuthor.is_deleted == False).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    existing = (
        db.query(ClassicalWork)
        .filter(
            ClassicalWork.author_id == author_id,
            ClassicalWork.slug == data.slug,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Work slug already exists for this author")

    work = ClassicalWork(
        author_id=author_id,
        slug=data.slug,
        title=data.title,
        description=data.description,
        work_type=data.work_type,
        original_script=data.original_script,
    )
    db.add(work)
    db.commit()
    db.refresh(work)
    invalidate_hierarchy_cache(author_slug=author.slug)
    return {
        "id": work.id,
        "author_id": work.author_id,
        "slug": work.slug,
        "title": work.title,
        "work_type": work.work_type,
    }


@router.patch("/works/{work_id}", dependencies=[Depends(require_role(Role.ADMIN))])
def update_work(
    work_id: int,
    data: WorkUpdateIn,
    db: Session = Depends(get_db),
):
    work = db.query(ClassicalWork).filter(ClassicalWork.id == work_id).first()
    if not work:
        raise HTTPException(status_code=404, detail="Work not found")

    if data.title is not None:
        work.title = data.title
    if data.description is not None:
        work.description = data.description
    if data.work_type is not None:
        work.work_type = data.work_type
    if data.original_script is not None:
        work.original_script = data.original_script
    if data.is_deleted is not None:
        work.is_deleted = data.is_deleted

    db.commit()
    db.refresh(work)
    return {
        "id": work.id,
        "author_id": work.author_id,
        "slug": work.slug,
        "title": work.title,
        "work_type": work.work_type,
        "is_deleted": work.is_deleted,
    }


@router.post("/works/{work_id}/chapters", dependencies=[Depends(require_role(Role.ADMIN))])
def create_chapter(
    work_id: int,
    data: ChapterCreateIn,
    db: Session = Depends(get_db),
):
    work = db.query(ClassicalWork).filter(ClassicalWork.id == work_id, ClassicalWork.is_deleted == False).first()
    if not work:
        raise HTTPException(status_code=404, detail="Work not found")

    # Check slug uniqueness within work
    exists_slug = (
        db.query(WorkChapter)
        .filter(
            WorkChapter.work_id == work_id,
            WorkChapter.slug == data.slug,
        )
        .first()
    )
    if exists_slug:
        raise HTTPException(status_code=400, detail="Chapter slug already exists for this work")

    # Check number uniqueness
    exists_num = (
        db.query(WorkChapter)
        .filter(
            WorkChapter.work_id == work_id,
            WorkChapter.number == data.number,
        )
        .first()
    )
    if exists_num:
        raise HTTPException(status_code=400, detail="Chapter number already exists for this work")

    chapter = WorkChapter(
        work_id=work_id,
        slug=data.slug,
        title=data.title,
        number=data.number,
    )
    db.add(chapter)
    db.commit()
    db.refresh(chapter)
    invalidate_hierarchy_cache(author_slug=work.author.slug, work_slug=work.slug)
    return {
        "id": chapter.id,
        "work_id": chapter.work_id,
        "slug": chapter.slug,
        "title": chapter.title,
        "number": chapter.number,
    }


@router.patch("/chapters/{chapter_id}", dependencies=[Depends(require_role(Role.ADMIN))])
def update_chapter(
    chapter_id: int,
    data: ChapterUpdateIn,
    db: Session = Depends(get_db),
):
    chapter = db.query(WorkChapter).filter(WorkChapter.id == chapter_id).first()
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")

    if data.title is not None:
        chapter.title = data.title

    if data.number is not None:
        if data.number != chapter.number:
            raise HTTPException(
                status_code=400,
                detail="Renumbering chapters is not supported. Create chapters in contiguous sequence.",
            )
        # enforce uniqueness per work
        exists_num = (
            db.query(WorkChapter)
            .filter(
                WorkChapter.work_id == chapter.work_id,
                WorkChapter.number == data.number,
                WorkChapter.id != chapter.id,
            )
            .first()
        )
        if exists_num:
            raise HTTPException(status_code=400, detail="Chapter number already exists for this work")
        chapter.number = data.number

    if data.is_deleted is not None:
        chapter.is_deleted = data.is_deleted

    db.commit()
    db.refresh(chapter)
    return {
        "id": chapter.id,
        "work_id": chapter.work_id,
        "slug": chapter.slug,
        "title": chapter.title,
        "number": chapter.number,
        "is_deleted": chapter.is_deleted,
    }
