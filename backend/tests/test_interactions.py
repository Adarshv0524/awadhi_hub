import uuid

from app.auth.hash import hash_password
from app.auth.jwt import create_access_token
from app.core.permissions import Role
from app.db.models import User, ClassicalAuthor, ClassicalWork, WorkChapter, DohaEntry


def create_user(db, email: str, role: str, username: str) -> User:
    user = User(
        email=email,
        username=username,
        password_hash=hash_password("Pass123!"),
        role=role,
        permissions=0,
        is_active=True,
        is_banned=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_doha(db):
    suffix = uuid.uuid4().hex[:8]
    source_submission_id = int(uuid.uuid4().int % 1_000_000_000)
    author = ClassicalAuthor(slug=f"author-like-{suffix}", name="Author", language="awadhi")
    db.add(author)
    db.commit()
    db.refresh(author)

    work = ClassicalWork(
        author_id=author.id,
        slug=f"work-like-{suffix}",
        title="Work",
        work_type="poetry",
    )
    db.add(work)
    db.commit()
    db.refresh(work)

    chapter = WorkChapter(
        work_id=work.id,
        slug=f"chapter-like-{suffix}",
        title="Chapter",
        number=1,
    )
    db.add(chapter)
    db.commit()
    db.refresh(chapter)

    doha = DohaEntry(
        hierarchy_path=f"author-like-{suffix}/work-like-{suffix}/chapter-like-{suffix}/1",
        author_id=author.id,
        work_id=work.id,
        chapter_id=chapter.id,
        number_in_chapter=1,
        main_text="liked doha text for dashboard",
        status="active",
        visibility="public",
        version=1,
        is_canonical=True,
        source_submission_id=source_submission_id,
    )
    db.add(doha)
    db.commit()
    db.refresh(doha)
    return doha


def test_user_likes_endpoint_owner_access_and_payload(client, db):
    owner = create_user(db, "likes-owner@example.com", Role.REGISTERED, "likes-owner")
    token = create_access_token(owner.id)
    doha = create_doha(db)

    toggle = client.post(
        "/interactions/toggle",
        headers={"Authorization": f"Bearer {token}"},
        json={"content_type": "doha", "content_id": doha.id, "interaction": "like"},
    )
    assert toggle.status_code == 200

    r = client.get(
        f"/interactions/users/{owner.id}/likes?limit=10&offset=0",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    body = r.json()

    assert body["total_count"] >= 1
    assert body["count"] >= 1
    assert len(body["results"]) >= 1
    first = body["results"][0]
    assert first["content_type"] == "doha"
    assert first["content_id"] == doha.id
    assert "content_title" in first


def test_user_likes_endpoint_forbidden_for_other_user(client, db):
    owner = create_user(db, "likes-owner-2@example.com", Role.REGISTERED, "likes-owner-2")
    other = create_user(db, "likes-other@example.com", Role.REGISTERED, "likes-other")
    owner_token = create_access_token(owner.id)
    other_token = create_access_token(other.id)
    doha = create_doha(db)

    toggle = client.post(
        "/interactions/toggle",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"content_type": "doha", "content_id": doha.id, "interaction": "like"},
    )
    assert toggle.status_code == 200

    forbidden = client.get(
        f"/interactions/users/{owner.id}/likes",
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert forbidden.status_code == 403


def test_user_likes_endpoint_admin_access(client, db):
    owner = create_user(db, "likes-owner-3@example.com", Role.REGISTERED, "likes-owner-3")
    admin = create_user(db, "likes-admin@example.com", Role.ADMIN, "likes-admin")
    owner_token = create_access_token(owner.id)
    admin_token = create_access_token(admin.id)
    doha = create_doha(db)

    toggle = client.post(
        "/interactions/toggle",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"content_type": "doha", "content_id": doha.id, "interaction": "like"},
    )
    assert toggle.status_code == 200

    allowed = client.get(
        f"/interactions/users/{owner.id}/likes?limit=10&offset=0",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert allowed.status_code == 200
    payload = allowed.json()
    assert payload["total_count"] >= 1
