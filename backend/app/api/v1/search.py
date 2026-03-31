# app/api/v1/search.py
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.poetry_service import search_poetry
from app.services.rate_limit import rate_limit_dependency
from app.services.search_service import search_dohas

router = APIRouter(prefix="", tags=["search"])


class SearchItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    hierarchy_path: Optional[str]
    main_text: str
    meaning: Optional[str]
    relevance_score: Optional[float] = 0.0

class SearchOut(BaseModel):
    total: int
    results: List[SearchItem]

search_rate_limit = rate_limit_dependency(action_key="search", limit=10, window_seconds=60, granularity=60)

@router.get("/search", dependencies=[Depends(search_rate_limit)])
def search_endpoint(
    q: Optional[str] = Query(None, description="Search query"),
    author: Optional[str] = Query(None, description="Author slug"),
    work: Optional[str] = Query(None, description="Work slug"),
    chapter: Optional[str] = Query(None, description="Chapter slug"),
    poetry_type: Optional[str] = Query(None, description="Poetry form slug, e.g. doha"),
    type_: Optional[str] = Query(None, alias="type", description="Legacy alias for poetry_type"),
    sort: str = Query("relevance", description="Sort by 'relevance' or 'recent'"),
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """
    Search poetry content. Doha is treated as a poetry_type.
    Falls back to legacy doha search when poetry index has no match.
    """
    effective_poetry_type = poetry_type or type_

    res = search_poetry(
        db=db,
        q=q,
        author_slug=author,
        work_slug=work,
        chapter_slug=chapter,
        poetry_type=effective_poetry_type,
        sort=sort,
        limit=limit,
        offset=offset,
    )

    if int(res.get("total", 0) or 0) == 0 and (effective_poetry_type in (None, "", "doha")):
        return search_dohas(
            db=db,
            q=q,
            author_slug=author,
            work_slug=work,
            chapter_slug=chapter,
            sort=sort,
            limit=limit,
            offset=offset,
        )

    return res
