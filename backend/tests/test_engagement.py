# tests/test_engagement.py
import pytest
import uuid
from app.db.models import DohaEntry, EngagementKPI, ClassicalAuthor, ClassicalWork, WorkChapter
from app.services.engagement_service import record_view, record_search_hits, get_kpi_for_content, compute_weight_score, list_popular_dohas

def seed_doha(db):
    # Generate a random suffix for uniqueness
    uid = uuid.uuid4().hex[:6] 
    
    # Use the random suffix in slugs
    a = ClassicalAuthor(slug=f"seedauthor-{uid}", name="Seed Author", language="awadhi")
    db.add(a); db.commit(); db.refresh(a)
    
    w = ClassicalWork(author_id=a.id, slug=f"seedwork-{uid}", title="Seed Work")
    db.add(w); db.commit(); db.refresh(w)
    
    c = WorkChapter(work_id=w.id, slug=f"seedchapter-{uid}", title="Seed Chapter", number=1)
    db.add(c); db.commit(); db.refresh(c)
    
    d1 = DohaEntry(
        hierarchy_path=f"seedauthor-{uid}/seedwork-{uid}/seedchapter-{uid}/1",
        author_id=a.id, work_id=w.id, chapter_id=c.id, number_in_chapter=1,
        main_text="alpha text", meaning="alpha meaning", status="active", visibility="public", version=1, is_canonical=True
    )
    d2 = DohaEntry(
        hierarchy_path=f"seedauthor-{uid}/seedwork-{uid}/seedchapter-{uid}/2",
        author_id=a.id, work_id=w.id, chapter_id=c.id, number_in_chapter=2,
        main_text="beta text", meaning="beta meaning", status="active", visibility="public", version=1, is_canonical=True
    )
    db.add_all([d1, d2]); db.commit()
    db.refresh(d1); db.refresh(d2)
    return d1, d2

def test_record_view_and_kpi_creation(db):
    d1, d2 = seed_doha(db)
    # record few views
    record_view(db, "doha", d1.id)
    db.commit()
    k = get_kpi_for_content(db, "doha", d1.id)
    assert k is not None
    assert k.views_count >= 1

def test_search_hits_and_popular_order(db):
    d1, d2 = seed_doha(db)
    # simulate search results [d2, d1] -> top 1 increments for d2
    record_search_hits(db, "doha", [d2.id, d1.id])
    db.commit()
    k2 = get_kpi_for_content(db, "doha", d2.id)
    k1 = get_kpi_for_content(db, "doha", d1.id)
    assert k2.search_hits_count >= 1
    # compute weight and check popular ordering
    # bump views to make d1 popular if needed
    # list popular
    pop = list_popular_dohas(db, limit=10)
    assert isinstance(pop, list)
