from typing import Any, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.poetry import PoetryTypeOut
from app.services.poetry_service import (
    get_poetry_nav,
    get_poetry_node,
    get_poetry_stream,
    get_poetry_types,
    search_poetry,
)


router = APIRouter(prefix="/poetry", tags=["poetry"])


class HierarchyAuthorOut(BaseModel):
    id: int
    slug: str
    name: str


class HierarchyWorkOut(BaseModel):
    id: int
    slug: str
    title: str


class HierarchyChapterOut(BaseModel):
    id: int
    slug: str
    number: int
    title: str


class HierarchyOut(BaseModel):
    author: HierarchyAuthorOut
    work: HierarchyWorkOut
    chapter: HierarchyChapterOut


class PoetryCurrentOut(BaseModel):
    id: int
    poetry_type: str
    sequence_no: int
    main_text: str
    text_devanagari: Optional[str] = None
    text_romanized: Optional[str] = None
    meaning: Optional[str] = None
    prosody_metadata: Optional[dict[str, Any]] = None
    views_count: int = 0
    likes_count: int = 0
    shares_count: int = 0
    bookmarks_count: int = 0
    search_hits_count: int = 0
    weight_score: float = 0.0


class PoetryNavSummaryOut(BaseModel):
    id: int
    poetry_type: str
    sequence_no: int


class PoetryNavContractOut(BaseModel):
    hierarchy: HierarchyOut
    current: PoetryCurrentOut
    previous: Optional[PoetryNavSummaryOut] = None
    next: Optional[PoetryNavSummaryOut] = None


class PoetryStreamOut(BaseModel):
    hierarchy: Optional[HierarchyOut] = None
    total: int
    offset: int
    limit: int
    items: list[PoetryCurrentOut]


class PoetrySearchItemOut(BaseModel):
    id: int
    poetry_type: str
    hierarchy_path: str
    chapter_path: str
    sequence_no: int
    main_text: str
    meaning: Optional[str] = None
    relevance_score: float = 0.0


class PoetrySearchOut(BaseModel):
    total: int
    results: list[PoetrySearchItemOut]


@router.get("/chapters/{chapter_id}/stream", response_model=PoetryStreamOut)
def poetry_stream_endpoint(
    chapter_id: int,
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return get_poetry_stream(db=db, chapter_id=chapter_id, offset=offset, limit=limit)


@router.get("/chapters/{chapter_id}/nav", response_model=PoetryNavContractOut)
def poetry_nav_endpoint(
    chapter_id: int,
    sequence_no: int = Query(..., ge=1),
    db: Session = Depends(get_db),
):
    return get_poetry_nav(db=db, chapter_id=chapter_id, sequence_no=sequence_no)


@router.get("/types", response_model=list[PoetryTypeOut])
def poetry_types_endpoint(db: Session = Depends(get_db)):
    return get_poetry_types(db=db)


@router.get("/search", response_model=PoetrySearchOut)
def poetry_search_endpoint(
    q: Optional[str] = Query(None),
    author: Optional[str] = Query(None),
    work: Optional[str] = Query(None),
    chapter: Optional[str] = Query(None),
    poetry_type: Optional[str] = Query(None),
    sort: str = Query("relevance"),
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    return search_poetry(
        db=db,
        q=q,
        author_slug=author,
        work_slug=work,
        chapter_slug=chapter,
        poetry_type=poetry_type,
        sort=sort,
        limit=limit,
        offset=offset,
    )


@router.get("/{poetry_node_id}", response_model=PoetryNavContractOut)
def poetry_node_detail_endpoint(poetry_node_id: int, db: Session = Depends(get_db)):
    return get_poetry_node(db=db, poetry_node_id=poetry_node_id)
