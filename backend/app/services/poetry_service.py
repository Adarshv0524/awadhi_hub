from typing import Optional

from fastapi import HTTPException
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from app.db.models import ClassicalAuthor, ClassicalWork, PoetryNode, PoetryTypeRegistry, WorkChapter
from app.schemas.poetry import PoetryTypeOut


def _active_poetry_query(db: Session):
    return (
        db.query(PoetryNode)
        .options(
            joinedload(PoetryNode.author),
            joinedload(PoetryNode.work),
            joinedload(PoetryNode.chapter),
        )
        .filter(
            PoetryNode.is_deleted == False,
            PoetryNode.status == "active",
            PoetryNode.visibility == "public",
        )
    )


def _serialize_hierarchy(node: PoetryNode) -> dict:
    return {
        "author": {
            "id": node.author.id,
            "slug": node.author.slug,
            "name": node.author.name,
        },
        "work": {
            "id": node.work.id,
            "slug": node.work.slug,
            "title": node.work.title,
        },
        "chapter": {
            "id": node.chapter.id,
            "slug": node.chapter.slug,
            "number": node.chapter.number,
            "title": node.chapter.title,
        },
    }


def _serialize_nav_summary(node: Optional[PoetryNode]) -> Optional[dict]:
    if not node:
        return None
    return {
        "id": node.id,
        "poetry_type": node.poetry_type,
        "sequence_no": node.sequence_no,
    }


def _serialize_current(node: PoetryNode) -> dict:
    return {
        "id": node.id,
        "poetry_type": node.poetry_type,
        "sequence_no": node.sequence_no,
        "main_text": node.main_text,
        "text_devanagari": node.text_devanagari,
        "text_romanized": node.text_romanized,
        "meaning": node.meaning,
        "prosody_metadata": node.prosody_metadata,
    }


def get_poetry_stream(db: Session, chapter_id: int, offset: int, limit: int = 100) -> dict:
    if chapter_id <= 0:
        raise HTTPException(status_code=400, detail="chapter_id must be positive")

    bounded_limit = max(1, min(limit, 100))

    chapter_exists = (
        db.query(WorkChapter)
        .filter(WorkChapter.id == chapter_id, WorkChapter.is_deleted == False)
        .first()
    )
    if not chapter_exists:
        raise HTTPException(status_code=404, detail="Chapter not found")

    base_q = _active_poetry_query(db).filter(PoetryNode.chapter_id == chapter_id)
    total = base_q.count()
    rows = (
        base_q.order_by(PoetryNode.sequence_no.asc(), PoetryNode.id.asc())
        .offset(offset)
        .limit(bounded_limit)
        .all()
    )

    hierarchy = None
    if rows:
        hierarchy = _serialize_hierarchy(rows[0])
    else:
        chapter_row = (
            db.query(WorkChapter, ClassicalWork, ClassicalAuthor)
            .join(ClassicalWork, ClassicalWork.id == WorkChapter.work_id)
            .join(ClassicalAuthor, ClassicalAuthor.id == ClassicalWork.author_id)
            .filter(
                WorkChapter.id == chapter_id,
                WorkChapter.is_deleted == False,
                ClassicalWork.is_deleted == False,
                ClassicalAuthor.is_deleted == False,
            )
            .first()
        )
        if chapter_row:
            chapter, work, author = chapter_row
            hierarchy = {
                "author": {"id": author.id, "slug": author.slug, "name": author.name},
                "work": {"id": work.id, "slug": work.slug, "title": work.title},
                "chapter": {
                    "id": chapter.id,
                    "slug": chapter.slug,
                    "number": chapter.number,
                    "title": chapter.title,
                },
            }

    return {
        "hierarchy": hierarchy,
        "total": total,
        "offset": offset,
        "limit": bounded_limit,
        "items": [_serialize_current(row) for row in rows],
    }


def get_poetry_nav(db: Session, chapter_id: int, sequence_no: int) -> dict:
    if chapter_id <= 0 or sequence_no <= 0:
        raise HTTPException(status_code=400, detail="chapter_id and sequence_no must be positive")

    # Navigation intentionally resolves only by chapter_id + sequence_no.
    chapter_scope = _active_poetry_query(db).filter(PoetryNode.chapter_id == chapter_id)

    current = chapter_scope.filter(PoetryNode.sequence_no == sequence_no).first()
    if not current:
        raise HTTPException(status_code=404, detail="Poetry node not found at requested chapter sequence")

    previous = (
        chapter_scope.filter(PoetryNode.sequence_no < sequence_no)
        .order_by(PoetryNode.sequence_no.desc(), PoetryNode.id.desc())
        .first()
    )
    next_item = (
        chapter_scope.filter(PoetryNode.sequence_no > sequence_no)
        .order_by(PoetryNode.sequence_no.asc(), PoetryNode.id.asc())
        .first()
    )

    return {
        "hierarchy": _serialize_hierarchy(current),
        "current": _serialize_current(current),
        "previous": _serialize_nav_summary(previous),
        "next": _serialize_nav_summary(next_item),
    }


def get_poetry_node(db: Session, poetry_node_id: int) -> dict:
    row = (
        _active_poetry_query(db)
        .filter(PoetryNode.id == poetry_node_id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Poetry node not found")

    chapter_scope = _active_poetry_query(db).filter(PoetryNode.chapter_id == row.chapter_id)
    previous = (
        chapter_scope.filter(PoetryNode.sequence_no < row.sequence_no)
        .order_by(PoetryNode.sequence_no.desc(), PoetryNode.id.desc())
        .first()
    )
    next_item = (
        chapter_scope.filter(PoetryNode.sequence_no > row.sequence_no)
        .order_by(PoetryNode.sequence_no.asc(), PoetryNode.id.asc())
        .first()
    )

    return {
        "hierarchy": _serialize_hierarchy(row),
        "current": _serialize_current(row),
        "previous": _serialize_nav_summary(previous),
        "next": _serialize_nav_summary(next_item),
    }


def get_poetry_types(db: Session) -> list[PoetryTypeOut]:
    rows = (
        db.query(PoetryTypeRegistry)
        .filter(PoetryTypeRegistry.is_active == True)
        .order_by(PoetryTypeRegistry.poetry_type.asc())
        .all()
    )

    if rows:
        return [
            PoetryTypeOut(
                id=row.id,
                poetry_type=row.poetry_type,
                display_name=row.display_name,
                family=row.family,
                is_user_defined=bool(row.is_user_defined),
                is_active=bool(row.is_active),
            )
            for row in rows
        ]

    # Fallback enum-style response if registry is empty.
    fallback = [
        ("doha", "Doha", "classical", False),
        ("chaupai", "Chaupai", "classical", False),
        ("jhulana", "Jhulana", "classical", False),
        ("sorath", "Sorath", "classical", False),
        ("savaiya", "Savaiya", "classical", False),
        ("ghanakshari", "Ghanakshari", "classical", False),
        ("chappay", "Chappay", "classical", False),
        ("other_poetry", "Other Poetry", "user_defined", True),
    ]
    return [
        PoetryTypeOut(
            poetry_type=poetry_type,
            display_name=display_name,
            family=family,
            is_user_defined=is_user_defined,
            is_active=True,
        )
        for poetry_type, display_name, family, is_user_defined in fallback
    ]


def search_poetry(
    db: Session,
    q: Optional[str],
    author_slug: Optional[str] = None,
    work_slug: Optional[str] = None,
    chapter_slug: Optional[str] = None,
    poetry_type: Optional[str] = None,
    sort: str = "relevance",
    limit: int = 20,
    offset: int = 0,
) -> dict:
    bounded_limit = max(1, min(limit, 200))

    base = (
        db.query(PoetryNode, ClassicalAuthor.slug, ClassicalWork.slug, WorkChapter.slug)
        .join(ClassicalAuthor, ClassicalAuthor.id == PoetryNode.author_id)
        .join(ClassicalWork, ClassicalWork.id == PoetryNode.work_id)
        .join(WorkChapter, WorkChapter.id == PoetryNode.chapter_id)
        .filter(
            PoetryNode.is_deleted == False,
            PoetryNode.status == "active",
            PoetryNode.visibility == "public",
            ClassicalAuthor.is_deleted == False,
            ClassicalWork.is_deleted == False,
            WorkChapter.is_deleted == False,
        )
    )

    if author_slug:
        base = base.filter(func.lower(ClassicalAuthor.slug) == author_slug.lower())
    if work_slug:
        base = base.filter(func.lower(ClassicalWork.slug) == work_slug.lower())
    if chapter_slug:
        base = base.filter(func.lower(WorkChapter.slug) == chapter_slug.lower())
    if poetry_type:
        base = base.filter(func.lower(PoetryNode.poetry_type) == poetry_type.lower())

    if q:
        q_like = f"%{q.lower()}%"
        base = base.filter(
            or_(
                func.lower(PoetryNode.main_text).like(q_like),
                func.lower(PoetryNode.meaning).like(q_like),
                func.lower(PoetryNode.text_devanagari).like(q_like),
                func.lower(PoetryNode.text_romanized).like(q_like),
            )
        )

    if sort == "recent":
        base = base.order_by(PoetryNode.created_at.desc(), PoetryNode.id.desc())
    else:
        base = base.order_by(PoetryNode.sequence_no.asc(), PoetryNode.id.asc())

    total = base.count()
    rows = base.offset(offset).limit(bounded_limit).all()

    results = []
    for node, a_slug, w_slug, c_slug in rows:
        hierarchy_path = f"{a_slug}/{w_slug}/{c_slug}/{node.sequence_no}"
        results.append(
            {
                "id": node.id,
                "poetry_type": node.poetry_type,
                "hierarchy_path": hierarchy_path,
                "chapter_path": f"{a_slug}/{w_slug}/{c_slug}",
                "sequence_no": node.sequence_no,
                "main_text": node.main_text,
                "meaning": node.meaning,
                "relevance_score": 1.0,
            }
        )

    return {"total": total, "results": results}
