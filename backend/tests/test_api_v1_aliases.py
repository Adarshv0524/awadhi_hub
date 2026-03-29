from app.auth.hash import hash_password
from app.auth.jwt import create_access_token
from app.core.permissions import Permission, Role
from app.db.models import User


def _create_admin(db):
    admin = User(
        email="aliasadmin@example.com",
        username="aliasadmin",
        password_hash=hash_password("Admin123!"),
        role=Role.ADMIN,
        permissions=Permission.MANAGE_USERS,
        is_active=True,
        is_banned=False,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


def test_api_v1_public_aliases_exist(client):
    # Authors list alias
    r = client.get("/api/v1/authors")
    assert r.status_code == 200

    # Content list alias
    r = client.get("/api/v1/content/doha")
    assert r.status_code == 200

    # Search alias
    r = client.get("/api/v1/search", params={"q": "test"})
    assert r.status_code == 200


def test_api_v1_auth_alias_requires_login(client):
    r = client.get("/api/v1/auth/me")
    assert r.status_code == 401


def test_api_v1_admin_alias_requires_admin(client, db):
    admin = _create_admin(db)
    token = create_access_token(admin.id)
    headers = {"Authorization": f"Bearer {token}"}

    r = client.get("/api/v1/admin/system_settings", headers=headers)
    assert r.status_code == 200
    assert isinstance(r.json(), list)
