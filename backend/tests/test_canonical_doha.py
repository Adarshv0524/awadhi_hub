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
import uuid


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


def test_doha_navigation_returns_prev_current_next(client, db):
    suffix = uuid.uuid4().hex[:8]

    author = ClassicalAuthor(slug=f"author-{suffix}", name="Author", language="awadhi")
    db.add(author)
    db.commit()
    db.refresh(author)

    work = ClassicalWork(
        author_id=author.id,
        slug=f"work-{suffix}",
        title="Work",
        work_type="poetry",
    )
    db.add(work)
    db.commit()
    db.refresh(work)

    chapter = WorkChapter(
        work_id=work.id,
        slug=f"chapter-{suffix}",
        title="Chapter",
        number=1,
    )
    db.add(chapter)
    db.commit()
    db.refresh(chapter)

    d_prev = DohaEntry(
        hierarchy_path=f"author-{suffix}/work-{suffix}/chapter-{suffix}/10",
        author_id=author.id,
        work_id=work.id,
        chapter_id=chapter.id,
        number_in_chapter=10,
        main_text="prev doha text",
        status="active",
        visibility="public",
        version=1,
        is_canonical=True,
        source_submission_id=900001,
    )
    d_cur = DohaEntry(
        hierarchy_path=f"author-{suffix}/work-{suffix}/chapter-{suffix}/11",
        author_id=author.id,
        work_id=work.id,
        chapter_id=chapter.id,
        number_in_chapter=11,
        main_text="current doha text",
        status="active",
        visibility="public",
        version=1,
        is_canonical=True,
        source_submission_id=900002,
    )
    d_next = DohaEntry(
        hierarchy_path=f"author-{suffix}/work-{suffix}/chapter-{suffix}/12",
        author_id=author.id,
        work_id=work.id,
        chapter_id=chapter.id,
        number_in_chapter=12,
        main_text="next doha text",
        status="active",
        visibility="public",
        version=1,
        is_canonical=True,
        source_submission_id=900003,
    )
    db.add_all([d_prev, d_cur, d_next])
    db.commit()
    db.refresh(d_prev)
    db.refresh(d_cur)
    db.refresh(d_next)

    r = client.get(f"/content/doha/{d_cur.id}/navigation")
    assert r.status_code == 200
    body = r.json()

    assert body["current"]["id"] == d_cur.id
    assert body["current"]["number_in_chapter"] == 11
    assert body["previous"]["id"] == d_prev.id
    assert body["next"]["id"] == d_next.id


def test_doha_navigation_handles_chapter_edges_and_missing_id(client, db):
    suffix = uuid.uuid4().hex[:8]

    author = ClassicalAuthor(slug=f"author-edge-{suffix}", name="Author", language="awadhi")
    db.add(author)
    db.commit()
    db.refresh(author)

    work = ClassicalWork(
        author_id=author.id,
        slug=f"work-edge-{suffix}",
        title="Work",
        work_type="poetry",
    )
    db.add(work)
    db.commit()
    db.refresh(work)

    chapter = WorkChapter(
        work_id=work.id,
        slug=f"chapter-edge-{suffix}",
        title="Chapter",
        number=1,
    )
    db.add(chapter)
    db.commit()
    db.refresh(chapter)

    first = DohaEntry(
        hierarchy_path=f"author-edge-{suffix}/work-edge-{suffix}/chapter-edge-{suffix}/1",
        author_id=author.id,
        work_id=work.id,
        chapter_id=chapter.id,
        number_in_chapter=1,
        main_text="first doha text",
        status="active",
        visibility="public",
        version=1,
        is_canonical=True,
        source_submission_id=900101,
    )
    second = DohaEntry(
        hierarchy_path=f"author-edge-{suffix}/work-edge-{suffix}/chapter-edge-{suffix}/2",
        author_id=author.id,
        work_id=work.id,
        chapter_id=chapter.id,
        number_in_chapter=2,
        main_text="second doha text",
        status="active",
        visibility="public",
        version=1,
        is_canonical=True,
        source_submission_id=900102,
    )
    db.add_all([first, second])
    db.commit()
    db.refresh(first)
    db.refresh(second)

    r = client.get(f"/content/doha/{first.id}/navigation")
    assert r.status_code == 200
    body = r.json()
    assert body["previous"] is None
    assert body["current"]["id"] == first.id
    assert body["next"]["id"] == second.id

    not_found = client.get("/content/doha/99999999/navigation")
    assert not_found.status_code == 404


def test_chapter_dohas_endpoint_sorted_and_paginated(client, db):
    suffix = uuid.uuid4().hex[:8]

    author = ClassicalAuthor(slug=f"author-list-{suffix}", name="Author", language="awadhi")
    db.add(author)
    db.commit()
    db.refresh(author)

    work = ClassicalWork(
        author_id=author.id,
        slug=f"work-list-{suffix}",
        title="Work",
        work_type="poetry",
    )
    db.add(work)
    db.commit()
    db.refresh(work)

    chapter = WorkChapter(
        work_id=work.id,
        slug=f"chapter-list-{suffix}",
        title="Chapter",
        number=1,
    )
    db.add(chapter)
    db.commit()
    db.refresh(chapter)

    # Intentionally insert out of order to validate explicit sorting by number_in_chapter.
    d2 = DohaEntry(
        hierarchy_path=f"author-list-{suffix}/work-list-{suffix}/chapter-list-{suffix}/2",
        author_id=author.id,
        work_id=work.id,
        chapter_id=chapter.id,
        number_in_chapter=2,
        main_text="verse two",
        status="active",
        visibility="public",
        version=1,
        is_canonical=True,
        source_submission_id=910001,
    )
    d1 = DohaEntry(
        hierarchy_path=f"author-list-{suffix}/work-list-{suffix}/chapter-list-{suffix}/1",
        author_id=author.id,
        work_id=work.id,
        chapter_id=chapter.id,
        number_in_chapter=1,
        main_text="verse one",
        status="active",
        visibility="public",
        version=1,
        is_canonical=True,
        source_submission_id=910002,
    )
    d3 = DohaEntry(
        hierarchy_path=f"author-list-{suffix}/work-list-{suffix}/chapter-list-{suffix}/3",
        author_id=author.id,
        work_id=work.id,
        chapter_id=chapter.id,
        number_in_chapter=3,
        main_text="verse three",
        status="active",
        visibility="public",
        version=1,
        is_canonical=True,
        source_submission_id=910003,
    )
    db.add_all([d2, d1, d3])
    db.commit()

    r = client.get(f"/content/chapters/{chapter.id}/dohas?offset=0&limit=2")
    assert r.status_code == 200
    body = r.json()

    assert body["chapter_id"] == chapter.id
    assert body["chapter_slug"] == chapter.slug
    assert body["total"] == 3
    assert len(body["items"]) == 2
    assert [i["number_in_chapter"] for i in body["items"]] == [1, 2]

    r2 = client.get(f"/content/chapters/{chapter.id}/dohas?offset=2&limit=2")
    assert r2.status_code == 200
    body2 = r2.json()
    assert len(body2["items"]) == 1
    assert body2["items"][0]["number_in_chapter"] == 3


def test_chapter_dohas_by_path_and_not_found(client, db):
    suffix = uuid.uuid4().hex[:8]

    author = ClassicalAuthor(slug=f"author-path-{suffix}", name="Author", language="awadhi")
    db.add(author)
    db.commit()
    db.refresh(author)

    work = ClassicalWork(
        author_id=author.id,
        slug=f"work-path-{suffix}",
        title="Work",
        work_type="poetry",
    )
    db.add(work)
    db.commit()
    db.refresh(work)

    chapter = WorkChapter(
        work_id=work.id,
        slug=f"chapter-path-{suffix}",
        title="Chapter",
        number=1,
    )
    db.add(chapter)
    db.commit()
    db.refresh(chapter)

    d1 = DohaEntry(
        hierarchy_path=f"author-path-{suffix}/work-path-{suffix}/chapter-path-{suffix}/1",
        author_id=author.id,
        work_id=work.id,
        chapter_id=chapter.id,
        number_in_chapter=1,
        main_text="path verse one",
        status="active",
        visibility="public",
        version=1,
        is_canonical=True,
        source_submission_id=920001,
    )
    db.add(d1)
    db.commit()

    ok = client.get(
        f"/content/by-path/{author.slug}/{work.slug}/{chapter.slug}/dohas?offset=0&limit=100"
    )
    assert ok.status_code == 200
    payload = ok.json()
    assert payload["chapter_id"] == chapter.id
    assert payload["total"] == 1
    assert payload["items"][0]["number_in_chapter"] == 1

    missing = client.get(
        f"/content/by-path/{author.slug}/{work.slug}/missing-{suffix}/dohas"
    )
    assert missing.status_code == 404
