# tests/test_auth_endpoints.py

from app.auth.jwt import create_access_token, create_password_reset_token
from app.auth.hash import hash_password, verify_password
from app.db.models import User
from app.core.permissions import Role, Permission


def test_register_login_refresh_logout_flow(client):
    # 1) Register
    r = client.post(
        "/auth/register",
        json={"email": "t1@example.com", "password": "Aa123456!", "username": "t1"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["email"] == "t1@example.com"

    # 2) Login
    r = client.post(
        "/auth/login",
        json={"email": "t1@example.com", "password": "Aa123456!"},
    )
    assert r.status_code == 200
    tokens = r.json()
    assert "access_token" in tokens and "refresh_token" in tokens

    access = tokens["access_token"]
    refresh = tokens["refresh_token"]

    # 3) Me
    r = client.get("/auth/me", headers={"Authorization": f"Bearer {access}"})
    assert r.status_code == 200
    assert r.json()["email"] == "t1@example.com"

    # 4) Refresh
    r = client.post("/auth/refresh", json={"refresh_token": refresh})
    assert r.status_code == 200
    assert "access_token" in r.json()

    # 5) Logout
    r = client.post("/auth/logout", json={"refresh_token": refresh})
    assert r.status_code == 200
    assert r.json()["ok"] is True

    # 6) Refresh after logout must fail
    r = client.post("/auth/refresh", json={"refresh_token": refresh})
    assert r.status_code == 401


def _create_user(db, email: str, role: str, permissions: int, username: str | None = None) -> User:
    user = User(
        email=email,
        username=username or email.split("@")[0],
        password_hash=hash_password("AdminPass123!"),
        role=role,
        permissions=permissions,
        is_active=True,
        is_banned=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_admin_can_list_users(client, db):
    # Seed admin and a regular user
    admin = _create_user(
        db,
        "admin@example.com",
        role=Role.ADMIN,
        permissions=Permission.MANAGE_USERS,
        username="admin",
    )
    _ = _create_user(
        db,
        "user1@example.com",
        role=Role.REGISTERED,
        permissions=0,
        username="user1",
    )

    token = create_access_token(admin.id)
    r = client.get(
        "/admin/users",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    users = r.json()
    assert any(u["email"] == "user1@example.com" for u in users)


def test_admin_list_users_allows_local_seed_email_domains(client, db):
    admin = _create_user(
        db,
        "admin-seed@example.com",
        role=Role.ADMIN,
        permissions=Permission.MANAGE_USERS,
        username="adminseed",
    )
    _ = _create_user(
        db,
        "seed_admin@awadhi.local",
        role=Role.REGISTERED,
        permissions=0,
        username="seedlocal",
    )

    token = create_access_token(admin.id)
    r = client.get(
        "/admin/users",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    users = r.json()
    assert any(u["email"] == "seed_admin@awadhi.local" for u in users)


def test_non_admin_cannot_access_admin_users(client, db):
    user = _create_user(
        db,
        "nonadmin@example.com",  # CHANGED: unique email
        role=Role.REGISTERED,
        permissions=0,
        username="nonadminuser",  # CHANGED: unique username
    )
    token = create_access_token(user.id)
    r = client.get(
        "/admin/users",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 403


def test_admin_can_update_user_role_and_permissions(client, db):
    admin = _create_user(
        db,
        "admin2@example.com",
        role=Role.ADMIN,
        permissions=Permission.MANAGE_USERS,
        username="admin2",
    )
    target = _create_user(
        db,
        "mod@example.com",
        role=Role.REGISTERED,
        permissions=0,
        username="mod",
    )

    token = create_access_token(admin.id)
    r = client.patch(
        f"/admin/users/{target.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"role": Role.MODERATOR, "permissions": Permission.MODERATE_SUBMISSIONS},
    )
    assert r.status_code == 200
    updated = r.json()
    assert updated["role"] == Role.MODERATOR
    assert updated["permissions"] == Permission.MODERATE_SUBMISSIONS


def test_admin_cannot_set_invalid_role(client, db):
    admin = _create_user(
        db,
        "admin3@example.com",
        role=Role.ADMIN,
        permissions=Permission.MANAGE_USERS,
        username="admin3",
    )
    target = _create_user(
        db,
        "target-invalid-role@example.com",
        role=Role.REGISTERED,
        permissions=0,
        username="targetinvalidrole",
    )

    token = create_access_token(admin.id)
    r = client.patch(
        f"/admin/users/{target.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"role": "contributor"},
    )
    assert r.status_code == 400
    assert "Invalid role" in r.json()["detail"]


def test_public_user_profile(client, db):
    user = _create_user(
        db,
        "public@example.com",
        role=Role.REGISTERED,
        permissions=0,
        username="publicuser",
    )
    r = client.get(f"/users/{user.username}")
    assert r.status_code == 200
    body = r.json()
    assert body["id"] == user.id
    assert body["username"] == "publicuser"
    assert body["role"] == Role.REGISTERED


def test_forgot_password_returns_generic_success(client):
    r = client.post("/auth/forgot-password", json={"email": "does-not-exist@example.com"})
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert "If an account exists" in body["message"]


def test_reset_password_with_valid_token_updates_password(client, db):
    user = User(
        email="reset-ok@example.com",
        username="resetok",
        password_hash=hash_password("OldPass123!"),
        role=Role.REGISTERED,
        is_active=True,
        is_banned=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_password_reset_token(user.id)
    r = client.post(
        "/auth/reset-password",
        json={"token": token, "new_password": "NewPass123!"},
    )
    assert r.status_code == 200
    assert r.json()["ok"] is True

    db.refresh(user)
    assert user.password_hash is not None
    assert verify_password("NewPass123!", user.password_hash)

    login_old = client.post("/auth/login", json={"email": user.email, "password": "OldPass123!"})
    assert login_old.status_code == 401

    login_new = client.post("/auth/login", json={"email": user.email, "password": "NewPass123!"})
    assert login_new.status_code == 200


def test_reset_password_rejects_invalid_token(client):
    r = client.post(
        "/auth/reset-password",
        json={"token": "invalid-token", "new_password": "SomePass123!"},
    )
    assert r.status_code == 400
