# app/services/recommendation_service.py

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.db.models import (
    DohaEntry,
    DictionaryEntry,
    IdiomEntry,
    ArticleEntry,
    PoetryNode,
    EngagementKPI,
    SystemSetting,
)

# -------------------------------------------------
# Configuration
# -------------------------------------------------

MAX_LIMIT = 50
DEFAULT_LIMIT = 5
DB_CANDIDATE_CAP = 50  # hard DB cap

# -------------------------------------------------
# Weights
# -------------------------------------------------

def _get_weights(db: Session) -> Dict[str, float]:
    defaults = {
        "views": 1.0,
        "likes": 2.0,
        "search_hits": 0.5,
    }

    setting = (
        db.query(SystemSetting)
        .filter(SystemSetting.setting_key == "recommendation_weights")
        .first()
    )

    if not setting or not isinstance(setting.value, dict):
        return defaults

    return {**defaults, **setting.value}


def _score(kpi: EngagementKPI | None, w: Dict[str, float]) -> float:
    if not kpi:
        return 0.0

    return (
        (kpi.views_count * w["views"])
        + (kpi.likes_count * w["likes"])
        + (kpi.search_hits_count * w["search_hits"])
    )


# -------------------------------------------------
# Token Handling (STRICT)
# -------------------------------------------------

def _extract_tokens(norm_text: str | None) -> List[str]:
    if not norm_text:
        return []
    return [t for t in norm_text.split(" ") if len(t) > 2]


# -------------------------------------------------
# Core Entry
# -------------------------------------------------

def get_recommendations(
    db: Session,
    content_type: str,
    content_id: int,
    limit: int = DEFAULT_LIMIT,
) -> List[Dict[str, Any]]:

    limit = min(limit or DEFAULT_LIMIT, MAX_LIMIT)
    weights = _get_weights(db)

    # -------------------------
    # Fetch source + tokens
    # -------------------------
    source = None
    tokens: List[str] = []

    if content_type == "dictionary":
        source = db.query(DictionaryEntry).filter(
            DictionaryEntry.id == content_id,
            DictionaryEntry.visibility == "public",
        ).first()
        tokens = _extract_tokens(source.lemma_roman_norm if source else None)

    elif content_type == "idiom":
        source = db.query(IdiomEntry).filter(
            IdiomEntry.id == content_id,
            IdiomEntry.visibility == "public",
        ).first()
        tokens = _extract_tokens(source.text_roman_norm if source else None)

    elif content_type == "article":
        source = db.query(ArticleEntry).filter(
            ArticleEntry.id == content_id,
            ArticleEntry.visibility == "public",
        ).first()
        tokens = _extract_tokens(source.title_roman_norm if source else None)

    elif content_type == "doha":
        source = db.query(DohaEntry).filter(
            DohaEntry.id == content_id,
            DohaEntry.visibility == "public",
        ).first()
        tokens = _extract_tokens(source.text_romanized if source else None)

    else:
        source = db.query(PoetryNode).filter(
            PoetryNode.id == content_id,
            PoetryNode.poetry_type == content_type,
            PoetryNode.visibility == "public",
            PoetryNode.status == "active",
            PoetryNode.is_deleted == False,
        ).first()
        tokens = _extract_tokens((source.text_romanized or source.main_text) if source else None)

    if not source or not tokens:
        return []

    # -------------------------
    # Candidate retrieval
    # -------------------------
    candidates: list[tuple[str, Any]] = []

    def _or_like(column):
        return or_(*[column.like(f"%{t}%") for t in tokens])

    # Doha → Dictionary (core linguistic link)
    if content_type == "doha":
        q = (
            db.query(DictionaryEntry)
            .filter(
                DictionaryEntry.visibility == "public",
                DictionaryEntry.id != content_id,
                _or_like(DictionaryEntry.lemma_roman_norm),
            )
            .limit(DB_CANDIDATE_CAP)
        )
        candidates = [("dictionary", x) for x in q]

    # Same-type semantic matching
    elif content_type == "dictionary":
        q = (
            db.query(DictionaryEntry)
            .filter(
                DictionaryEntry.visibility == "public",
                DictionaryEntry.id != content_id,
                _or_like(DictionaryEntry.lemma_roman_norm),
            )
            .limit(DB_CANDIDATE_CAP)
        )
        candidates = [("dictionary", x) for x in q]

    elif content_type == "idiom":
        q = (
            db.query(IdiomEntry)
            .filter(
                IdiomEntry.visibility == "public",
                IdiomEntry.id != content_id,
                _or_like(IdiomEntry.text_roman_norm),
            )
            .limit(DB_CANDIDATE_CAP)
        )
        candidates = [("idiom", x) for x in q]

    elif content_type == "article":
        q = (
            db.query(ArticleEntry)
            .filter(
                ArticleEntry.visibility == "public",
                ArticleEntry.id != content_id,
                _or_like(ArticleEntry.title_roman_norm),
            )
            .limit(DB_CANDIDATE_CAP)
        )
        candidates = [("article", x) for x in q]

    else:
        q = (
            db.query(PoetryNode)
            .filter(
                PoetryNode.poetry_type == content_type,
                PoetryNode.visibility == "public",
                PoetryNode.status == "active",
                PoetryNode.is_deleted == False,
                PoetryNode.id != content_id,
                _or_like(PoetryNode.main_text),
            )
            .limit(DB_CANDIDATE_CAP)
        )
        candidates = [(content_type, x) for x in q]

    if not candidates:
        return []

    # -------------------------
    # Score + Rank
    # -------------------------
    results: List[Dict[str, Any]] = []

    for ctype, ent in candidates:
        kpi = (
            db.query(EngagementKPI)
            .filter(
                EngagementKPI.content_type == ctype,
                EngagementKPI.content_id == ent.id,
            )
            .first()
        )

        preview_text = (
            ent.lemma_devanagari if ctype == "dictionary"
            else ent.text_devanagari if ctype == "idiom"
            else ent.title if ctype == "article"
            else ent.main_text[:120]
        )

        results.append(
            {
                "content_type": ctype,
                "id": ent.id,
                "title_or_text": preview_text,
                "score": _score(kpi, weights),
            }
        )

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:limit]
