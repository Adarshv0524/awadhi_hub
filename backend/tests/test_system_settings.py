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


def test_settings_import_preview_and_atomic_apply(client, db):
    admin = create_admin_user(db)
    token = create_access_token(admin.id)
    headers = {"Authorization": f"Bearer {token}"}

    seed_payload = {
        "schema_version": 1,
        "settings": [
            {
                "key": "rate_limits",
                "value": {
                    "login": {"limit": 5, "window_seconds": 3600},
                    "search": {"limit": 120, "window_seconds": 60},
                    "submission_create": {"limit": 20, "window_seconds": 86400},
                },
            }
        ],
        "dry_run": False,
        "confirmation_text": "APPLY CRITICAL SETTINGS",
    }
    seed_res = client.post("/admin/system_settings/import", json=seed_payload, headers=headers)
    assert seed_res.status_code == 200

    # Dry-run preview with one invalid value should surface errors without changing DB
    preview_payload = {
        "schema_version": 1,
        "settings": [
            {
                "key": "rate_limits",
                "value": {
                    "login": {"limit": "bad", "window_seconds": 3600},
                    "search": {"limit": 120, "window_seconds": 60},
                    "submission_create": {"limit": 20, "window_seconds": 86400},
                },
            }
        ],
        "dry_run": True,
    }
    preview_res = client.post("/admin/system_settings/import", json=preview_payload, headers=headers)
    assert preview_res.status_code == 200
    preview_data = preview_res.json()
    assert preview_data["summary"]["invalid"] == 1
    assert preview_data["applied"] is False

    # Apply with invalid payload should fail and keep existing setting unchanged
    apply_invalid = dict(preview_payload)
    apply_invalid["dry_run"] = False
    apply_invalid["confirmation_text"] = "APPLY CRITICAL SETTINGS"
    apply_invalid_res = client.post("/admin/system_settings/import", json=apply_invalid, headers=headers)
    assert apply_invalid_res.status_code == 400

    after_fail = client.get("/admin/system_settings/rate_limits", headers=headers)
    assert after_fail.status_code == 200
    assert after_fail.json()["value"]["login"]["limit"] == 5


def test_settings_import_requires_confirmation_for_critical_keys(client, db):
    admin = create_admin_user(db)
    token = create_access_token(admin.id)
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "schema_version": 1,
        "settings": [
            {
                "key": "prometheus_enabled",
                "value": True,
            }
        ],
        "dry_run": False,
    }
    res = client.post("/admin/system_settings/import", json=payload, headers=headers)
    assert res.status_code == 400

    ok_payload = dict(payload)
    ok_payload["confirmation_text"] = "APPLY CRITICAL SETTINGS"
    ok_res = client.post("/admin/system_settings/import", json=ok_payload, headers=headers)
    assert ok_res.status_code == 200
    assert ok_res.json()["applied"] is True
