# tests/test_system_settings.py

from app.auth.jwt import create_access_token
from app.auth.hash import hash_password
from app.db.models import User
from app.core.permissions import Role, Permission


def create_admin_user(db):
    admin = User(
        email="settingsadmin@example.com",
        username="settingsadmin",
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


def test_admin_can_create_update_delete_setting(client, db):
    admin = create_admin_user(db)
    token = create_access_token(admin.id)
    headers = {"Authorization": f"Bearer {token}"}

    # Create setting with ALL required fields
    rate_limits_value = {
        "login": {"limit": 5, "window_seconds": 3600},
        "search": {"limit": 120, "window_seconds": 60},
        "submission_create": {"limit": 20, "window_seconds": 86400}
    }
    
    r = client.put(
        "/admin/system_settings/rate_limits",
        json={"value": rate_limits_value},
        headers=headers
    )

    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")

    assert r.status_code == 200
    data = r.json()
    assert data["key"] == "rate_limits"
    assert data["value"]["login"]["limit"] == 5

    # Update setting
    updated_value = {
        "login": {"limit": 8, "window_seconds": 3600},
        "search": {"limit": 120, "window_seconds": 60},
        "submission_create": {"limit": 20, "window_seconds": 86400}
    }
    
    r = client.put(
        "/admin/system_settings/rate_limits",
        json={"value": updated_value},
        headers=headers
    )
    assert r.status_code == 200
    data = r.json()
    assert data["value"]["login"]["limit"] == 8

    # Get setting
    r = client.get("/admin/system_settings/rate_limits", headers=headers)
    assert r.status_code == 200
    assert r.json()["value"]["login"]["limit"] == 8

    # Delete setting
    r = client.delete("/admin/system_settings/rate_limits", headers=headers)
    assert r.status_code == 204


def test_non_admin_cannot_modify_settings(client, db):
    user = User(
        email="normalsettingsuser@example.com",
        username="normalsettingsuser",
        password_hash=hash_password("Pass123!"),
        role=Role.REGISTERED,
        permissions=0,
        is_active=True,
        is_banned=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    token = create_access_token(user.id)
    headers = {"Authorization": f"Bearer {token}"}

    r = client.put(
        "/admin/system_settings/test_key",
        json={"value": "test"},
        headers=headers
    )
    assert r.status_code == 403
