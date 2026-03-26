# tests/test_dictionary_idiom_article.py

import uuid
from app.db.models import Submission, DictionaryEntry, IdiomEntry, ArticleEntry, User
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