# tests/test_audit_logs.py
import json
from app.db.models import User
from app.auth.hash import hash_password
from app.auth.jwt import create_access_token
from app.services.audit_service import record_audit

def test_record_audit_service_and_api(client, db):
    # create admin
    admin = User(email="audadmin@example.com", username="audadmin", password_hash=hash_password("Pass123!"), role="admin")
    db.add(admin); db.commit(); db.refresh(admin)
    token = create_access_token(admin.id)
    headers = {"Authorization": f"Bearer {token}"}

    # Use service to record audit directly (simulate action)
    before = {"rate_limits": {"login": {"limit": 5}}}
    after = {"rate_limits": {"login": {"limit": 8}}}
    meta = {"ip_address": "127.0.0.1", "user_agent": "pytest", "request_id": "r1"}
    audit = record_audit(db=db, actor_user_id=admin.id, action="test:change", resource_type="system_setting", resource_id=None, before=before, after=after, metadata=meta)
    # commit so API reads it
    db.commit()

    # admin can list
    r = client.get("/admin/audit_logs", headers=headers)
    assert r.status_code == 200
    j = r.json()
    assert j["total"] >= 1

    # get single
    r = client.get(f"/admin/audit_logs/{audit.id}", headers=headers)
    assert r.status_code == 200
    assert r.json()["action"] == "test:change"

def test_non_admin_cannot_access_audit(client, db):
    # create non-admin
    from app.db.models import User
    u = User(email="u2@example.com", username="u2", password_hash=hash_password("Pass123!"), role="registered")
    db.add(u); db.commit(); db.refresh(u)
    token = create_access_token(u.id)
    headers = {"Authorization": f"Bearer {token}"}
    r = client.get("/admin/audit_logs", headers=headers)
    assert r.status_code == 403
