# app/api/v1/article.py
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from app.db.session import get_db
from app.db.models import ArticleEntry, EngagementKPI, User
from app.core.security import get_current_user, require_role
from app.core.permissions import Role

router = APIRouter(prefix="/articles", tags=["articles"])

# ----------------------------
# KPI helpers
# ----------------------------

def _inc_search_kpi(db: Session, article_id: int):
    """Increment search hit count for article in engagement KPIs."""
    kpi = db.query(EngagementKPI).filter_by(
        content_type="article", content_id=article_id
    ).first()
    if not kpi:
        kpi = EngagementKPI(
            content_type="article",
            content_id=article_id,
            search_hits_count=0,
            views_count=0,
            likes_count=0,
            shares_count=0,
            weight_score=0.0,
        )
        db.add(kpi)
        db.flush()
    
    kpi.search_hits_count = (kpi.search_hits_count or 0) + 1


def _inc_view_kpi(db: Session, article_id: int):
    """Increment view count for article in engagement KPIs."""
    kpi = db.query(EngagementKPI).filter_by(
        content_type="article", content_id=article_id
    ).first()
    if not kpi:
        kpi = EngagementKPI(
            content_type="article",
            content_id=article_id,
            search_hits_count=0,
            views_count=0,
            likes_count=0,
            shares_count=0,
            weight_score=0.0,
        )
        db.add(kpi)
        db.flush()
    
    kpi.views_count = (kpi.views_count or 0) + 1

# Pydantic models
class ArticleListOut(BaseModel):
    id: int
    title: str
    title_devanagari: Optional[str]
    title_roman: Optional[str]
    excerpt: Optional[str]
    author_name: Optional[str]
    tags: Optional[List[str]]
    version: int
    created_at: Optional[str]
    views_count: int = 0
    likes_count: int = 0
    shares_count: int = 0
    bookmarks_count: int = 0
    
    class Config:
        from_attributes = True

class ArticleDetailOut(BaseModel):
    id: int
    title: str
    title_devanagari: Optional[str]
    title_roman: Optional[str]
    title_roman_norm: Optional[str]
    body: str
    excerpt: Optional[str]
    author_id: Optional[int]
    author_name: Optional[str]
    tags: Optional[List[str]]
    contributor_id: Optional[int]
    source_submission_id: Optional[int]
    visibility: str
    version: int
    created_at: Optional[str]
    updated_at: Optional[str]
    views_count: int = 0
    likes_count: int = 0
    shares_count: int = 0
    bookmarks_count: int = 0
    
    class Config:
        from_attributes = True

class ArticleStatsOut(BaseModel):
    total_articles: int
    by_tag: dict
    recent_count: int


def _article_kpi_map(db: Session, article_ids: List[int]) -> dict[int, dict]:
    if not article_ids:
        return {}

    rows = (
        db.query(EngagementKPI)
        .filter(
            EngagementKPI.content_type == "article",
            EngagementKPI.content_id.in_(article_ids),
        )
        .all()
    )
    return {
        r.content_id: {
            "views_count": r.views_count or 0,
            "likes_count": r.likes_count or 0,
            "shares_count": r.shares_count or 0,
            "bookmarks_count": r.bookmarks_count or 0,
        }
        for r in rows
    }


def _article_author_map(db: Session, author_ids: List[int]) -> dict[int, str]:
    if not author_ids:
        return {}

    rows = db.query(User.id, User.username, User.email).filter(User.id.in_(author_ids)).all()
    return {r.id: (r.username or r.email) for r in rows}

# Routes
@router.get("", response_model=List[ArticleListOut])
def list_articles(
    q: Optional[str] = Query(None, description="Search query for title or body"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
    offset: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    List articles with optional search and filtering.
    - Public visibility only
    - Ordered by creation date (newest first)
    - Tracks search hits in engagement KPIs when q is provided
    """
    query = db.query(ArticleEntry).filter(ArticleEntry.visibility == "public")
    
    if tag:
        # Filter by tag (assuming tags is a JSON array)
        query = query.filter(ArticleEntry.tags.contains([tag]))
    
    if q:
        q_norm = q.strip().lower()
        # Try exact title match first
        exact = query.filter(
            or_(
                ArticleEntry.title == q,
                ArticleEntry.title_devanagari == q,
                ArticleEntry.title_roman_norm == q_norm
            )
        ).all()
        
        if exact:
            # Track search hits in KPIs
            for e in exact:
                _inc_search_kpi(db, e.id)
            db.commit()

            article_ids = [e.id for e in exact]
            author_ids = [
                (e.author_id if e.author_id is not None else e.contributor_id)
                for e in exact
                if (e.author_id is not None or e.contributor_id is not None)
            ]
            kpi_map = _article_kpi_map(db, article_ids)
            author_map = _article_author_map(db, author_ids)
            
            return [ArticleListOut(
                id=e.id,
                title=e.title,
                title_devanagari=e.title_devanagari,
                title_roman=e.title_roman,
                excerpt=e.excerpt,
                author_name=author_map.get(e.author_id if e.author_id is not None else e.contributor_id),
                tags=e.tags,
                version=e.version,
                created_at=e.created_at.isoformat() if e.created_at else None,
                **kpi_map.get(e.id, {
                    "views_count": 0,
                    "likes_count": 0,
                    "shares_count": 0,
                    "bookmarks_count": 0,
                }),
            ) for e in exact]
        
        # Fallback to LIKE search in title and body
        like_q = f"%{q}%"
        rows = query.filter(
            or_(
                ArticleEntry.title.ilike(like_q),
                ArticleEntry.title_devanagari.ilike(like_q),
                ArticleEntry.title_roman.ilike(like_q),
                ArticleEntry.body.ilike(like_q)
            )
        ).order_by(ArticleEntry.created_at.desc()).offset(offset).limit(limit).all()
        
        # Track search hits in KPIs
        for r in rows:
            _inc_search_kpi(db, r.id)
        db.commit()
    else:
        rows = query.order_by(ArticleEntry.created_at.desc()).offset(offset).limit(limit).all()
    
    article_ids = [r.id for r in rows]
    author_ids = [
        (r.author_id if r.author_id is not None else r.contributor_id)
        for r in rows
        if (r.author_id is not None or r.contributor_id is not None)
    ]
    kpi_map = _article_kpi_map(db, article_ids)
    author_map = _article_author_map(db, author_ids)

    return [ArticleListOut(
        id=r.id,
        title=r.title,
        title_devanagari=r.title_devanagari,
        title_roman=r.title_roman,
        excerpt=r.excerpt,
        author_name=author_map.get(r.author_id if r.author_id is not None else r.contributor_id),
        tags=r.tags,
        version=r.version,
        created_at=r.created_at.isoformat() if r.created_at else None,
        **kpi_map.get(r.id, {
            "views_count": 0,
            "likes_count": 0,
            "shares_count": 0,
            "bookmarks_count": 0,
        }),
    ) for r in rows]

@router.get("/stats", response_model=ArticleStatsOut)
def get_article_stats(db: Session = Depends(get_db)):
    """
    Get statistics about articles.
    """
    total = db.query(func.count(ArticleEntry.id)).filter(
        ArticleEntry.visibility == "public"
    ).scalar()
    
    # Count by tag (this is simplified - proper implementation would unnest JSON arrays)
    all_articles = db.query(ArticleEntry).filter(
        ArticleEntry.visibility == "public",
        ArticleEntry.tags.isnot(None)
    ).all()
    
    tag_counts = {}
    for article in all_articles:
        if article.tags and isinstance(article.tags, list):
            for tag in article.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    # Recent entries (last 30 days)
    from datetime import datetime, timedelta
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent = db.query(func.count(ArticleEntry.id)).filter(
        ArticleEntry.visibility == "public",
        ArticleEntry.created_at >= thirty_days_ago
    ).scalar()
    
    return ArticleStatsOut(
        total_articles=total or 0,
        by_tag=tag_counts,
        recent_count=recent or 0
    )

@router.get("/search/advanced")
def advanced_search_articles(
    title: Optional[str] = Query(None),
    body: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Advanced search with multiple filters.
    """
    query = db.query(ArticleEntry).filter(ArticleEntry.visibility == "public")
    
    if title:
        like_t = f"%{title}%"
        query = query.filter(
            or_(
                ArticleEntry.title.ilike(like_t),
                ArticleEntry.title_devanagari.ilike(like_t),
                ArticleEntry.title_roman.ilike(like_t)
            )
        )
    
    if body:
        like_b = f"%{body}%"
        query = query.filter(ArticleEntry.body.ilike(like_b))
    
    if tag:
        query = query.filter(ArticleEntry.tags.contains([tag]))
    
    rows = query.order_by(ArticleEntry.created_at.desc()).offset(offset).limit(limit).all()
    
    return [
        {
            "id": r.id,
            "title": r.title,
            "title_devanagari": r.title_devanagari,
            "title_roman": r.title_roman,
            "excerpt": r.excerpt,
            "tags": r.tags,
            "version": r.version,
            "created_at": r.created_at.isoformat() if r.created_at else None
        }
        for r in rows
    ]

@router.get("/{article_id}")
def get_article(article_id: int, db: Session = Depends(get_db)):
    """
    Get detailed information about a specific article.
    Increments view count in engagement KPIs.
    """
    row = db.query(ArticleEntry).filter(
        ArticleEntry.id == article_id,
        ArticleEntry.visibility == "public"
    ).first()
    
    if not row:
        raise HTTPException(status_code=404, detail="Article not found")
    
    # Track view in engagement KPIs
    _inc_view_kpi(db, article_id)
    db.commit()

    kpi = db.query(EngagementKPI).filter_by(content_type="article", content_id=article_id).first()
    author_name = None
    display_user_id = row.author_id if row.author_id is not None else row.contributor_id
    if display_user_id is not None:
        author = db.query(User.id, User.username, User.email).filter(User.id == display_user_id).first()
        if author:
            author_name = author.username or author.email
    
    return {
        "id": row.id,
        "title": row.title,
        "title_devanagari": row.title_devanagari,
        "title_roman": row.title_roman,
        "title_roman_norm": row.title_roman_norm,
        "body": row.body,
        "excerpt": row.excerpt,
        "author_id": row.author_id,
        "author_name": author_name,
        "tags": row.tags,
        "contributor_id": row.contributor_id,
        "source_submission_id": row.source_submission_id,
        "visibility": row.visibility,
        "version": row.version,
        "created_at": row.created_at.isoformat() if row.created_at else None,
        "updated_at": row.updated_at.isoformat() if row.updated_at else None,
        "views_count": (kpi.views_count if kpi else 0) or 0,
        "likes_count": (kpi.likes_count if kpi else 0) or 0,
        "shares_count": (kpi.shares_count if kpi else 0) or 0,
        "bookmarks_count": (kpi.bookmarks_count if kpi else 0) or 0,
    }

@router.get("/by-tag/{tag}")
def get_articles_by_tag(
    tag: str,
    offset: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Get all articles with a specific tag.
    """
    rows = db.query(ArticleEntry).filter(
        ArticleEntry.tags.contains([tag]),
        ArticleEntry.visibility == "public"
    ).order_by(ArticleEntry.created_at.desc()).offset(offset).limit(limit).all()
    
    return [
        {
            "id": r.id,
            "title": r.title,
            "title_devanagari": r.title_devanagari,
            "title_roman": r.title_roman,
            "excerpt": r.excerpt,
            "tags": r.tags,
            "created_at": r.created_at.isoformat() if r.created_at else None
        }
        for r in rows
    ]

@router.get("/recent/list")
def get_recent_articles(
    days: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """
    Get recently published articles.
    """
    from datetime import datetime, timedelta
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    rows = db.query(ArticleEntry).filter(
        ArticleEntry.visibility == "public",
        ArticleEntry.created_at >= cutoff_date
    ).order_by(ArticleEntry.created_at.desc()).limit(limit).all()
    
    return [
        {
            "id": r.id,
            "title": r.title,
            "excerpt": r.excerpt,
            "tags": r.tags,
            "created_at": r.created_at.isoformat() if r.created_at else None
        }
        for r in rows
    ]

@router.get("/tags/list")
def list_all_tags(db: Session = Depends(get_db)):
    """
    Get a list of all unique tags used in articles.
    """
    articles = db.query(ArticleEntry).filter(
        ArticleEntry.visibility == "public",
        ArticleEntry.tags.isnot(None)
    ).all()
    
    all_tags = set()
    for article in articles:
        if article.tags and isinstance(article.tags, list):
            all_tags.update(article.tags)
    
    return {"tags": sorted(list(all_tags))}