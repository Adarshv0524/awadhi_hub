# tests/test_canonical_doha.py

from app.db.models import (
    User,
    ClassicalAuthor,
    ClassicalWork,
    WorkChapter,
    Submission,
    DohaEntry,
    ContentVersion,
)
from app.auth.hash import hash_password
from app.auth.jwt import create_access_token
from app.core.permissions import Role


def create_user(db, email: str, role: str, username: str) -> User:
    u = User(
        email=email,
        username=username,
        password_hash=hash_password("Pass123!"),
        role=role,
        permissions=0,
        is_active=True,
        is_banned=False,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


def create_hierarchy(db):
    author = ClassicalAuthor(slug="tulsidas", name="Goswami Tulsidas", language="awadhi")
    db.add(author)
    db.commit()
    db.refresh(author)

    work = ClassicalWork(
        author_id=author.id,
        slug="ramcharitmanas",
        title="Ramcharitmanas",
        work_type="epic",
    )
    db.add(work)
    db.commit()
    db.refresh(work)

    chapter = WorkChapter(
        work_id=work.id,
        slug="ayodhya-kand",
        title="अयोध्या काण्ड",
        number=2,
    )
    db.add(chapter)
    db.commit()
    db.refresh(chapter)

    return author, work, chapter


def test_approval_creates_canonical_doha_and_version(client, db):
    # hierarchy, contributor, moderator
    create_hierarchy(db)
    contributor = create_user(db, "cont1@example.com", Role.REGISTERED, "cont1")
    moderator = create_user(db, "modc1@example.com", Role.MODERATOR, "modc1")

    contrib_token = create_access_token(contributor.id)
    mod_token = create_access_token(moderator.id)

    # contributor submits classical doha, pending_review
    r = client.post(
        "/submissions",
        headers={"Authorization": f"Bearer {contrib_token}"},
        json={
            "content_type": "doha",
            "main_text": "श्रीरामचन्द्र कृपालु भजु मन",
            "meaning": "Worship kind-hearted Shri Ramchandra",
            "is_classical": True,
            "author_slug": "tulsidas",
            "work_slug": "ramcharitmanas",
            "chapter_slug": "ayodhya-kand",
            "number_in_chapter": 23,
            "submit_for_review": True,
        },
    )
    assert r.status_code == 200
    sub = r.json()
    sub_id = sub["id"]
    assert sub["status"] == "pending_review"

    # moderator approves
    r = client.post(
        f"/moderation/submissions/{sub_id}/approve",
        headers={"Authorization": f"Bearer {mod_token}"},
        json={"note": "canonical", "guideline_version": "v1"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "approved"

    # canonical doha must exist
    doha = (
        db.query(DohaEntry)
        .filter(DohaEntry.source_submission_id == sub_id, DohaEntry.is_deleted == False)
        .first()
    )
    assert doha is not None
    assert doha.main_text == "श्रीरामचन्द्र कृपालु भजु मन"
    assert doha.author_id is not None
    assert doha.work_id is not None
    assert doha.chapter_id is not None
    assert doha.number_in_chapter == 23
    assert doha.hierarchy_path == "tulsidas/ramcharitmanas/ayodhya-kand/23"

    # content_versions row must exist
    versions = (
        db.query(ContentVersion)
        .filter(
            ContentVersion.content_type == "doha",
            ContentVersion.content_id == doha.id,
        )
        .all()
    )
    assert len(versions) == 1
    assert versions[0].version_number == 1
    assert versions[0].main_text == "श्रीरामचन्द्र कृपालु भजु मन"

    # test /content APIs
    # 1) by id
    r = client.get(f"/content/doha/{doha.id}")
    assert r.status_code == 200
    doha_api = r.json()
    assert doha_api["main_text"] == "श्रीरामचन्द्र कृपालु भजु मन"

    # 2) history
    r = client.get(f"/content/doha/{doha.id}/history")
    assert r.status_code == 200
    hist = r.json()
    assert len(hist) == 1
    assert hist[0]["version_number"] == 1

    # 3) by path
    path = "tulsidas/ramcharitmanas/ayodhya-kand/23"
    r = client.get(f"/content/by-path/{path}")
    assert r.status_code == 200
    assert r.json()["id"] == doha.id


def test_non_classical_approval_creates_doha_without_path(client, db):
    contributor = create_user(db, "cont2@example.com", Role.REGISTERED, "cont2")
    moderator = create_user(db, "modc2@example.com", Role.MODERATOR, "modc2")

    contrib_token = create_access_token(contributor.id)
    mod_token = create_access_token(moderator.id)

    # non-classical doha
    r = client.post(
        "/submissions",
        headers={"Authorization": f"Bearer {contrib_token}"},
        json={
            "content_type": "doha",
            "main_text": "non classical doha",
            "meaning": "some meaning",
            "is_classical": False,
            "submit_for_review": True,
        },
    )
    assert r.status_code == 200
    sub = r.json()
    sub_id = sub["id"]
    assert sub["status"] == "pending_review"

    # approve
    r = client.post(
        f"/moderation/submissions/{sub_id}/approve",
        headers={"Authorization": f"Bearer {mod_token}"},
        json={},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "approved"

    doha = (
        db.query(DohaEntry)
        .filter(DohaEntry.source_submission_id == sub_id, DohaEntry.is_deleted == False)
        .first()
    )
    assert doha is not None
    assert doha.main_text == "non classical doha"
    # no classical linking
    assert doha.hierarchy_path is None
    assert doha.author_id is None
    assert doha.work_id is None
    assert doha.chapter_id is None
