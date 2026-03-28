# tests/test_dictionary_idiom_article.py

import uuid
from datetime import datetime, timedelta

from app.db.models import Submission, DictionaryEntry, IdiomEntry, ArticleEntry, DohaEntry, EngagementKPI, User
from app.auth.hash import hash_password
from app.auth.jwt import create_access_token

def create_user(db, role="registered"):
    """Create user with unique username to avoid collisions"""
    unique_suffix = uuid.uuid4().hex[:8]
    username = f"{role}_{unique_suffix}"
    u = User(
        email=f"{username}@ex.com",
        username=username,
        password_hash=hash_password("Pass123!"),
        role=role
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u
def create_dictionary_submission(db, user_id, senses):
    sub = Submission(
        content_type="dictionary",
        main_text="मुख्य शब्द",
        meaning=None,
        external_references={"lemma_devanagari": "मुख्य शब्द", "lemma_roman": "mukhya shabd", "senses": senses},
        status="pending_review",
        visibility="public",
        version=1,
        contributor_id=user_id,
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub

def create_idiom_submission(db, user_id):
    sub = Submission(
        content_type="idiom",
        main_text="अंधों में काना राजा",
        meaning="Among blind people, one-eyed is king",
        external_references={"text_devanagari": "अंधों में काना राजा", "text_roman": "andhon mein kana raja"},
        status="pending_review",
        visibility="public",
        version=1,
        contributor_id=user_id,
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub

def create_article_submission(db, user_id):
    sub = Submission(
        content_type="article",
        main_text="Test Article Body Content",
        meaning=None,
        external_references={"title": "Test Article", "body": "Test Article Body Content", "tags": ["test", "sample"]},
        status="pending_review",
        visibility="public",
        version=1,
        contributor_id=user_id,
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub

# Dictionary Tests
def test_single_approve_dictionary(client, db):
    admin = create_user(db, role="admin")
    token = create_access_token(admin.id)
    headers = {"Authorization": f"Bearer {token}"}
    senses = [{"definition": "primary word", "pos": "noun"}]
    sub = create_dictionary_submission(db, admin.id, senses)
    
    # call moderator approve endpoint
    r = client.post(f"/moderation/submissions/{sub.id}/approve", json={}, headers=headers)
    assert r.status_code in (200, 201)
    
    # check dictionary entry created
    de = db.query(DictionaryEntry).filter(DictionaryEntry.source_submission_id == sub.id).first()
    assert de is not None
    assert de.lemma_roman == "mukhya shabd"

def test_batch_approve_dictionary(client, db):
    admin = create_user(db, role="admin")
    token = create_access_token(admin.id)
    headers = {"Authorization": f"Bearer {token}"}
    senses1 = [{"definition": "word one", "pos": "noun"}]
    senses2 = [{"definition": "word two", "pos": "verb"}]
    sub1 = create_dictionary_submission(db, admin.id, senses1)
    sub2 = create_dictionary_submission(db, admin.id, senses2)
    
    # batch approve
    r = client.post("/moderation/batch_approve", json={"submission_ids": [sub1.id, sub2.id]}, headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert len(data["created"]) == 2
    assert len(data["skipped"]) == 0
    
    # verify both created
    de1 = db.query(DictionaryEntry).filter(DictionaryEntry.source_submission_id == sub1.id).first()
    de2 = db.query(DictionaryEntry).filter(DictionaryEntry.source_submission_id == sub2.id).first()
    assert de1 is not None
    assert de2 is not None

def test_dictionary_idempotency(client, db):
    admin = create_user(db, role="admin")
    token = create_access_token(admin.id)
    headers = {"Authorization": f"Bearer {token}"}
    senses = [{"definition": "test word", "pos": "noun"}]
    sub = create_dictionary_submission(db, admin.id, senses)
    
    # approve once
    r1 = client.post(f"/moderation/submissions/{sub.id}/approve", json={}, headers=headers)
    assert r1.status_code in (200, 201)
    
    # approve again - should be idempotent
    r2 = client.post(f"/moderation/submissions/{sub.id}/approve", json={}, headers=headers)
    assert r2.status_code in (200, 400)  # may reject already approved
    
    # should still have only one entry
    entries = db.query(DictionaryEntry).filter(DictionaryEntry.source_submission_id == sub.id).all()
    assert len(entries) == 1

def test_list_dictionary_entries(client, db):
    admin = create_user(db, role="admin")
    token = create_access_token(admin.id)
    headers = {"Authorization": f"Bearer {token}"}
    
    # create and approve a dictionary entry
    senses = [{"definition": "test", "pos": "noun"}]
    sub = create_dictionary_submission(db, admin.id, senses)
    client.post(f"/moderation/submissions/{sub.id}/approve", json={}, headers=headers)
    
    # list entries
    r = client.get("/dictionary")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) >= 1

def test_get_dictionary_entry(client, db):
    admin = create_user(db, role="admin")
    token = create_access_token(admin.id)
    headers = {"Authorization": f"Bearer {token}"}
    
    # create and approve
    senses = [{"definition": "test definition", "pos": "noun"}]
    sub = create_dictionary_submission(db, admin.id, senses)
    client.post(f"/moderation/submissions/{sub.id}/approve", json={}, headers=headers)
    
    de = db.query(DictionaryEntry).filter(DictionaryEntry.source_submission_id == sub.id).first()
    assert de is not None
    
    # get detail
    r = client.get(f"/dictionary/{de.id}")
    assert r.status_code == 200
    data = r.json()
    assert data["lemma_devanagari"] == "मुख्य शब्द"
    assert data["lemma_roman"] == "mukhya shabd"
    assert "created_at" in data
    assert "updated_at" in data
    assert data["views_count"] >= 1
    assert data["likes_count"] >= 0
    assert data["shares_count"] >= 0
    assert data["bookmarks_count"] >= 0
    assert "author_name" in data
    assert "work_name" in data
    assert "chapter_name" in data

# Idiom Tests
def test_single_approve_idiom(client, db):
    admin = create_user(db, role="admin")
    token = create_access_token(admin.id)
    headers = {"Authorization": f"Bearer {token}"}
    sub = create_idiom_submission(db, admin.id)
    
    r = client.post(f"/moderation/submissions/{sub.id}/approve", json={}, headers=headers)
    assert r.status_code in (200, 201)
    
    ie = db.query(IdiomEntry).filter(IdiomEntry.source_submission_id == sub.id).first()
    assert ie is not None
    assert ie.text_devanagari == "अंधों में काना राजा"
    assert ie.text_roman == "andhon mein kana raja"

def test_idiom_submission_to_canonical_contract(client, db):
    contributor = create_user(db, role="registered")
    moderator = create_user(db, role="moderator")

    contributor_token = create_access_token(contributor.id)
    moderator_token = create_access_token(moderator.id)

    submit_headers = {"Authorization": f"Bearer {contributor_token}"}
    approve_headers = {"Authorization": f"Bearer {moderator_token}"}

    create_payload = {
        "content_type": "idiom",
        "main_text": "आसमान से गिरा खजूर में अटका",
        "meaning": "From one problem into another",
        "external_references": {
            "text_devanagari": "आसमान से गिरा खजूर में अटका",
            "text_roman": "aasman se gira khajur mein atka",
            "examples": ["वो नौकरी से निकला और कर्ज में फंस गया।"],
        },
        "visibility": "public",
        "submit_for_review": True,
    }

    create_res = client.post("/submissions", json=create_payload, headers=submit_headers)
    assert create_res.status_code == 200
    submission_id = create_res.json()["id"]

    approve_res = client.post(
        f"/moderation/submissions/{submission_id}/approve",
        json={"note": "Contract alignment check"},
        headers=approve_headers,
    )
    assert approve_res.status_code in (200, 201)

    idiom_entry = db.query(IdiomEntry).filter(IdiomEntry.source_submission_id == submission_id).first()
    assert idiom_entry is not None
    assert idiom_entry.text_roman == "aasman se gira khajur mein atka"

def test_batch_approve_idiom(client, db):
    admin = create_user(db, role="admin")
    token = create_access_token(admin.id)
    headers = {"Authorization": f"Bearer {token}"}
    sub1 = create_idiom_submission(db, admin.id)
    sub2 = create_idiom_submission(db, admin.id)
    
    r = client.post("/moderation/batch_approve", json={"submission_ids": [sub1.id, sub2.id]}, headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert len(data["created"]) == 2

def test_list_idioms(client, db):
    admin = create_user(db, role="admin")
    token = create_access_token(admin.id)
    headers = {"Authorization": f"Bearer {token}"}
    
    sub = create_idiom_submission(db, admin.id)
    client.post(f"/moderation/submissions/{sub.id}/approve", json={}, headers=headers)
    
    r = client.get("/idioms")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) >= 1

def test_get_idiom(client, db):
    admin = create_user(db, role="admin")
    token = create_access_token(admin.id)
    headers = {"Authorization": f"Bearer {token}"}
    
    sub = create_idiom_submission(db, admin.id)
    client.post(f"/moderation/submissions/{sub.id}/approve", json={}, headers=headers)
    
    ie = db.query(IdiomEntry).filter(IdiomEntry.source_submission_id == sub.id).first()
    assert ie is not None
    
    r = client.get(f"/idioms/{ie.id}")
    assert r.status_code == 200
    data = r.json()
    assert data["text_devanagari"] == "अंधों में काना राजा"
    assert "created_at" in data
    assert "updated_at" in data
    assert data["views_count"] >= 1
    assert data["likes_count"] >= 0
    assert data["shares_count"] >= 0
    assert data["bookmarks_count"] >= 0
    assert "author_name" in data
    assert "work_name" in data
    assert "chapter_name" in data

# Article Tests
def test_single_approve_article(client, db):
    admin = create_user(db, role="admin")
    token = create_access_token(admin.id)
    headers = {"Authorization": f"Bearer {token}"}
    sub = create_article_submission(db, admin.id)
    
    r = client.post(f"/moderation/submissions/{sub.id}/approve", json={}, headers=headers)
    assert r.status_code in (200, 201)
    
    ae = db.query(ArticleEntry).filter(ArticleEntry.source_submission_id == sub.id).first()
    assert ae is not None
    assert ae.title == "Test Article"

def test_batch_approve_article(client, db):
    admin = create_user(db, role="admin")
    token = create_access_token(admin.id)
    headers = {"Authorization": f"Bearer {token}"}
    sub1 = create_article_submission(db, admin.id)
    sub2 = create_article_submission(db, admin.id)
    
    r = client.post("/moderation/batch_approve", json={"submission_ids": [sub1.id, sub2.id]}, headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert len(data["created"]) == 2

def test_list_articles(client, db):
    admin = create_user(db, role="admin")
    token = create_access_token(admin.id)
    headers = {"Authorization": f"Bearer {token}"}
    
    sub = create_article_submission(db, admin.id)
    client.post(f"/moderation/submissions/{sub.id}/approve", json={}, headers=headers)
    
    r = client.get("/articles")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) >= 1

def test_get_article(client, db):
    admin = create_user(db, role="admin")
    token = create_access_token(admin.id)
    headers = {"Authorization": f"Bearer {token}"}

    sub = create_article_submission(db, admin.id)
    client.post(f"/moderation/submissions/{sub.id}/approve", json={}, headers=headers)

    ae = db.query(ArticleEntry).filter(ArticleEntry.source_submission_id == sub.id).first()
    assert ae is not None

    r = client.get(f"/articles/{ae.id}")
    assert r.status_code == 200
    data = r.json()
    assert data["title"] == "Test Article"
    assert data["body"] == "Test Article Body Content"
    assert "author_name" in data
    assert data["views_count"] >= 1
    assert data["likes_count"] >= 0
    assert data["shares_count"] >= 0
    assert data["bookmarks_count"] >= 0


def test_articles_list_defaults_to_created_at_desc_and_supports_explicit_sort(client, db):
    now = datetime.utcnow()
    older = ArticleEntry(
        title="Older Article",
        body="older",
        visibility="public",
        tags=["sort-order-test"],
        created_at=now - timedelta(days=2),
        updated_at=now - timedelta(days=2),
    )
    newer = ArticleEntry(
        title="Newer Article",
        body="newer",
        visibility="public",
        tags=["sort-order-test"],
        created_at=now - timedelta(hours=1),
        updated_at=now - timedelta(hours=1),
    )
    db.add_all([older, newer])
    db.commit()
    db.refresh(older)
    db.refresh(newer)

    db.add_all([
        EngagementKPI(content_type="article", content_id=older.id, views_count=100),
        EngagementKPI(content_type="article", content_id=newer.id, views_count=10),
    ])
    db.commit()

    default_resp = client.get("/articles", params={"tag": "sort-order-test", "limit": 2})
    assert default_resp.status_code == 200
    default_items = default_resp.json()
    assert len(default_items) == 2
    assert default_items[0]["id"] == newer.id
    assert default_items[1]["id"] == older.id

    views_sorted = client.get(
        "/articles",
        params={"tag": "sort-order-test", "sort": "views_count", "order": "desc", "limit": 2},
    )
    assert views_sorted.status_code == 200
    views_items = views_sorted.json()
    assert len(views_items) == 2
    assert views_items[0]["id"] == older.id
    assert views_items[1]["id"] == newer.id


def test_doha_list_defaults_to_created_at_desc(client, db):
    now = datetime.utcnow()
    older = DohaEntry(
        main_text="older doha",
        status="active",
        visibility="sort-order-test",
        is_canonical=True,
        is_deleted=False,
        created_at=now - timedelta(days=3),
        updated_at=now - timedelta(days=3),
    )
    newer = DohaEntry(
        main_text="newer doha",
        status="active",
        visibility="sort-order-test",
        is_canonical=True,
        is_deleted=False,
        created_at=now - timedelta(minutes=30),
        updated_at=now - timedelta(minutes=30),
    )
    db.add_all([older, newer])
    db.commit()
    db.refresh(older)
    db.refresh(newer)

    resp = client.get("/content/doha", params={"visibility": "sort-order-test", "limit": 2})
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) == 2
    assert items[0]["id"] == newer.id
    assert items[1]["id"] == older.id


# Batch approve atomic abort test
def test_batch_approve_atomic_abort(client, db):
    admin = create_user(db, role="admin")
    token = create_access_token(admin.id)
    headers = {"Authorization": f"Bearer {token}"}
    
    senses = [{"definition": "test", "pos": "noun"}]
    sub1 = create_dictionary_submission(db, admin.id, senses)
    invalid_id = 99999  # non-existent submission
    
    # batch approve with one invalid - should fail
    r = client.post("/moderation/batch_approve", json={"submission_ids": [sub1.id, invalid_id]}, headers=headers)
    assert r.status_code == 400
    
    # verify nothing was created (atomic rollback)
    de = db.query(DictionaryEntry).filter(DictionaryEntry.source_submission_id == sub1.id).first()
    assert de is None