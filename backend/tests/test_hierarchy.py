# tests/test_hierarchy.py

import uuid # Import UUID for generating unique identifiers
from app.db.models import User
from app.auth.hash import hash_password
from app.auth.jwt import create_access_token
from app.core.permissions import Role


def create_admin_user(db) -> User:
    admin = User(
        email="admin_hierarchy@example.com",
        username="admin_h",
        password_hash=hash_password("AdminPass123!"),
        role=Role.ADMIN,
        permissions=0,
        is_active=True,
        is_banned=False,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


def create_regular_user(db) -> User:
    user = User(
        email="user_h@example.com",
        username="user_h",
        password_hash=hash_password("UserPass123!"),
        role=Role.REGISTERED,
        permissions=0,
        is_active=True,
        is_banned=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_admin_can_create_author_work_chapter_and_public_can_browse(client, db):
    admin = create_admin_user(db)
    admin_token = create_access_token(admin.id)

    # --- Initial Author Data ---
    author_data = {
        "slug": "tulsidas",
        "name": "Goswami Tulsidas",
        "short_bio": "Bhakti poet",
        "long_bio": "Long bio...",
        "language": "awadhi",
    }
    
    # 1) Create author (Attempt 1)
    r = client.post(
        "/admin/hierarchy/authors",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=author_data,
    )

    # Check for failure due to pre-existing slug (400 Bad Request)
    if r.status_code == 400 and r.json().get('detail') == 'Author slug already exists':
        # If the slug exists, generate a unique one and try again (Attempt 2)
        unique_slug = f"test-author-{uuid.uuid4().hex[:8]}"
        author_data["slug"] = unique_slug
        author_data["name"] = f"Test Author {unique_slug}"
        
        r = client.post(
            "/admin/hierarchy/authors",
            headers={"Authorization": f"Bearer {admin_token}"},
            json=author_data,
        )
    
    # Assert successful creation (either on 1st or 2nd attempt)
    assert r.status_code == 200
    
    # Use the slug and name from the successful attempt for subsequent checks
    final_author_slug = author_data["slug"]
    final_author_name = author_data["name"]
    
    author = r.json()
    author_id = author["id"]

    # 2) Create work under author
    r = client.post(
        f"/admin/hierarchy/authors/{author_id}/works",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "slug": "ramcharitmanas",
            "title": "Ramcharitmanas",
            "description": "Epic Awadhi retelling of Ramayana",
            "work_type": "epic",
            "original_script": "devanagari",
        },
    )
    assert r.status_code == 200
    work = r.json()
    work_id = work["id"]

    # 3) Create chapter under work
    r = client.post(
        f"/admin/hierarchy/works/{work_id}/chapters",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "slug": "ayodhya-kand",
            "title": "अयोध्या काण्ड",
            "number": 2,
        },
    )
    assert r.status_code == 200
    chapter = r.json()
    assert chapter["number"] == 2

    # 4) Public: list authors
    r = client.get("/authors")
    assert r.status_code == 200
    authors = r.json()
    assert any(a["slug"] == final_author_slug for a in authors)

    # 5) Public: get author details
    r = client.get(f"/authors/{final_author_slug}")
    assert r.status_code == 200
    assert r.json()["name"] == final_author_name

    # 6) Public: list works for author
    r = client.get(f"/authors/{final_author_slug}/works")
    assert r.status_code == 200
    works = r.json()
    assert any(w["slug"] == "ramcharitmanas" for w in works)

    # 7) Public: get work detail
    r = client.get(f"/authors/{final_author_slug}/works/ramcharitmanas")
    assert r.status_code == 200
    assert r.json()["title"] == "Ramcharitmanas"

    # 8) Public: list chapters
    r = client.get(f"/authors/{final_author_slug}/works/ramcharitmanas/chapters")
    assert r.status_code == 200
    chapters = r.json()
    assert any(c["slug"] == "ayodhya-kand" for c in chapters)


def test_non_admin_cannot_access_hierarchy_admin_endpoints(client, db):
    user = create_regular_user(db)
    token = create_access_token(user.id)

    r = client.post(
        "/admin/hierarchy/authors",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "slug": "kabir",
            "name": "Kabir",
        },
    )
    assert r.status_code == 403