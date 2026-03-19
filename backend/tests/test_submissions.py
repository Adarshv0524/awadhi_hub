# tests/test_submissions.py

from app.db.models import User, ClassicalAuthor, ClassicalWork, WorkChapter, Submission
from app.auth.hash import hash_password
from app.auth.jwt import create_access_token
from app.core.permissions import Role
import uuid # <-- NEW IMPORT

def create_user(db, email: str, role: str = Role.REGISTERED, username: str = "user") -> User:
    u = User(
        email=email,
        username=username,
        password_hash=hash_password("UserPass123!"),
        role=role,
        permissions=0,
        is_active=True,
        is_banned=False,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


def create_hierarchy_for_classical(db):
    # Generate unique slugs using a UUID prefix to prevent UNIQUE constraint errors
    unique_prefix = str(uuid.uuid4())[:8]
    
    author_slug = f"test-author-{unique_prefix}"
    work_slug = f"test-work-{unique_prefix}"
    chapter_slug = f"test-chapter-{unique_prefix}"
    
    author = ClassicalAuthor(
        slug=author_slug,
        name=f"Test Author {unique_prefix}",
        language="awadhi",
    )
    db.add(author)
    db.commit()
    db.refresh(author)

    work = ClassicalWork(
        author_id=author.id,
        slug=work_slug,
        title=f"Test Work {unique_prefix}",
        work_type="epic",
    )
    db.add(work)
    db.commit()
    db.refresh(work)

    chapter = WorkChapter(
        work_id=work.id,
        slug=chapter_slug,
        title=f"Test Chapter {unique_prefix}",
        number=2,
    )
    db.add(chapter)
    db.commit()
    db.refresh(chapter)

    # Return the new unique slugs along with the hierarchy objects
    return author, work, chapter, author_slug, work_slug, chapter_slug # <-- UPDATED RETURN VALUE


def test_create_draft_and_list_me_submissions(client, db):
    user = create_user(db, "s1@example.com", username="s1")
    token = create_access_token(user.id)

    # create draft
    r = client.post(
        "/submissions",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "content_type": "doha",
            "main_text": "राम सिया राम सिया राम जय जय राम",
            "meaning": "Glory to Lord Rama",
            "is_classical": False,
            "submit_for_review": False
        },
    )
    assert r.status_code == 200
    sub = r.json()
    assert sub["status"] == "draft"
    assert sub["version"] == 1
    assert sub["contributor_id"] == user.id

    # list my submissions
    r = client.get(
        "/submissions/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 1
    assert items[0]["id"] == sub["id"]


def test_create_pending_review_and_forbid_edit_while_pending(client, db):
    user = create_user(db, "s2@example.com", username="s2")
    token = create_access_token(user.id)

    # create directly as pending_review
    r = client.post(
        "/submissions",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "content_type": "doha",
            "main_text": "श्रीरामचन्द्र कृपालु भजु मन",
            "meaning": "Worship kind-hearted Shri Ramchandra",
            "is_classical": False,
            "submit_for_review": True
        },
    )
    assert r.status_code == 200
    sub = r.json()
    assert sub["status"] == "pending_review"

    # try to edit while pending_review
    r = client.put(
        f"/submissions/{sub['id']}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "main_text": "changed text",
            "expected_version": sub["version"],
        },
    )
    assert r.status_code == 400
    assert "Cannot edit submission in status" in r.json()["detail"]


def test_optimistic_locking_version_conflict(client, db):
    user = create_user(db, "s3@example.com", username="s3")
    token = create_access_token(user.id)

    # create draft
    r = client.post(
        "/submissions",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "content_type": "doha",
            "main_text": "first version",
            "is_classical": False,
            "submit_for_review": False
        },
    )
    assert r.status_code == 200
    sub = r.json()
    sub_id = sub["id"]
    version = sub["version"]

    # first update OK
    r = client.put(
        f"/submissions/{sub_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "main_text": "second version",
            "expected_version": version,
        },
    )
    assert r.status_code == 200
    updated = r.json()
    assert updated["main_text"] == "second version"
    assert updated["version"] == version + 1

    # second update with stale version -> conflict
    r = client.put(
        f"/submissions/{sub_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "main_text": "third version",
            "expected_version": version,  # stale
        },
    )
    assert r.status_code == 409
    assert "Version conflict" in r.json()["detail"]


def test_classical_submission_validates_hierarchy(client, db):
    # set up hierarchy: author/work/chapter
    _, _, _, author_slug, work_slug, chapter_slug = create_hierarchy_for_classical(db) # <-- UPDATED CALL TO GET UNIQUE SLUGS

    user = create_user(db, "s4@example.com", username="s4")
    token = create_access_token(user.id)

    # valid classical submission
    r = client.post(
        "/submissions",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "content_type": "doha",
            "main_text": "doha text",
            "meaning": "some meaning",
            "is_classical": True,
            "author_slug": author_slug,   # <-- USE UNIQUE SLUG
            "work_slug": work_slug,       # <-- USE UNIQUE SLUG
            "chapter_slug": chapter_slug, # <-- USE UNIQUE SLUG
            "number_in_chapter": 23,
            "submit_for_review": False
        },
    )
    assert r.status_code == 200
    sub = r.json()
    assert sub["is_classical"] is True
    assert sub["author_slug"] == author_slug # <-- USE UNIQUE SLUG


def test_classical_submission_rejects_invalid_slugs(client, db):
    # We still need to create a hierarchy here so the test database is consistent
    # even though this test doesn't use the slugs directly for the negative check.
    # It's good practice to ensure setup functions are called when needed.
    create_hierarchy_for_classical(db) 
    
    user = create_user(db, "s5@example.com", username="s5")
    token = create_access_token(user.id)

    r = client.post(
        "/submissions",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "content_type": "doha",
            "main_text": "doha text",
            "is_classical": True,
            "author_slug": "unknown-author", # Still testing a known-bad slug
            "work_slug": "w",
            "chapter_slug": "c",
            "number_in_chapter": 1,
            "submit_for_review": False
        },
    )
    assert r.status_code == 400
    assert "Invalid author_slug" in r.json()["detail"]


def test_delete_submission_soft_delete(client, db):
    user = create_user(db, "s6@example.com", username="s6")
    token = create_access_token(user.id)

    # create draft
    r = client.post(
        "/submissions",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "content_type": "doha",
            "main_text": "to be deleted",
            "is_classical": False,
            "submit_for_review": False
        },
    )
    assert r.status_code == 200
    sub = r.json()
    sub_id = sub["id"]

    # delete
    r = client.delete(
        f"/submissions/{sub_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    assert r.json()["ok"] is True

    # it should disappear from /submissions/me
    r = client.get(
        "/submissions/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    items = r.json()
    assert all(s["id"] != sub_id for s in items)