# tests/test_search.py

from app.db.models import DohaEntry, ClassicalAuthor, ClassicalWork, WorkChapter
from app.auth.hash import hash_password
from app.auth.jwt import create_access_token
from app.core.permissions import Role

def seed_hierarchy(db):
    """
    Creates the hierarchy (Author -> Work -> Chapter) if it doesn't exist.
    This prevents 'Unique constraint failed' errors if the data persists 
    from previous tests.
    """
    # 1. Check or Create Author
    author = db.query(ClassicalAuthor).filter(ClassicalAuthor.slug == "tulsidas").first()
    if not author:
        author = ClassicalAuthor(
            slug="tulsidas", 
            name="Goswami Tulsidas", 
            language="awadhi"
        )
        db.add(author)
        db.commit()
        db.refresh(author)

    # 2. Check or Create Work
    work = db.query(ClassicalWork).filter(
        ClassicalWork.slug == "ramcharitmanas", 
        ClassicalWork.author_id == author.id
    ).first()
    
    if not work:
        work = ClassicalWork(
            author_id=author.id, 
            slug="ramcharitmanas", 
            title="Ramcharitmanas", 
            work_type="epic"
        )
        db.add(work)
        db.commit()
        db.refresh(work)

    # 3. Check or Create Chapter
    chapter = db.query(WorkChapter).filter(
        WorkChapter.slug == "ayodhya-kand", 
        WorkChapter.work_id == work.id
    ).first()

    if not chapter:
        chapter = WorkChapter(
            work_id=work.id, 
            slug="ayodhya-kand", 
            title="अयोध्या काण्ड", 
            number=2
        )
        db.add(chapter)
        db.commit()
        db.refresh(chapter)

    return author, work, chapter


def test_search_fallback_basic(client, db):
    # seed authors/works/chapters securely
    author, work, chapter = seed_hierarchy(db)

    # create canonical dohas directly in DB
    # We use a unique ID or clean up logic usually, but for simple tests
    # creating them directly is fine as long as hierarchy exists.
    d1 = DohaEntry(
        hierarchy_path="tulsidas/ramcharitmanas/ayodhya-kand/23",
        author_id=author.id,
        work_id=work.id,
        chapter_id=chapter.id,
        number_in_chapter=23,
        main_text="श्रीरामचन्द्र कृपालु भजु मन",
        meaning="Worship kind-hearted Shri Ramchandra",
        text_devanagari="श्रीरामचन्द्र कृपालु भजु मन",
        status="active",
        visibility="public",
        version=1,
        is_canonical=True,
        source_submission_id=9999,
    )
    db.add(d1)

    d2 = DohaEntry(
        hierarchy_path=None,
        author_id=None,
        work_id=None,
        chapter_id=None,
        number_in_chapter=None,
        main_text="दुख में सुमिरन सब करे, सुख में करे न कोय।",
        meaning="Everyone remembers God in sorrow",
        status="active",
        visibility="public",
        version=1,
        is_canonical=True,
        source_submission_id=10000,
    )
    db.add(d2)
    db.commit()

    # simple search by a Devanagari snippet - should match first doha
    r = client.get("/search", params={"q": "श्रीरामचन्द्र"})
    assert r.status_code == 200
    body = r.json()
    # Note: total might be > 1 if previous tests left data, so we check >= 1
    assert body["total"] >= 1
    ids = [item["id"] for item in body["results"]]
    assert d1.id in ids

    # search English meaning snippet
    r = client.get("/search", params={"q": "Worship"})
    assert r.status_code == 200
    body = r.json()
    assert body["total"] >= 1
    ids = [item["id"] for item in body["results"]]
    assert d1.id in ids

    # search by author filter (should match doha with hierarchy)
    r = client.get("/search", params={"author": "tulsidas"})
    assert r.status_code == 200
    body = r.json()
    # Ensure we found at least one result with the correct path
    assert any(item["hierarchy_path"] and item["hierarchy_path"].startswith("tulsidas/") for item in body["results"])