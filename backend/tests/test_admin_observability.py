from app.auth.hash import hash_password
from app.auth.jwt import create_access_token
from app.db.models import AdminTelemetryEvent, User


def _create_admin(db, email: str = "observability_admin@example.com") -> User:
    admin = User(
        email=email,
        username=email.split("@")[0],
        password_hash=hash_password("Pass123!"),
        role="admin",
        is_active=True,
        is_banned=False,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


def test_admin_event_ingestion_and_slo_summary(client, db):
    admin = _create_admin(db)
    token = create_access_token(admin.id)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    payload = {
        "session_id": "sess-001",
        "request_id": "req-test-001",
        "module": "users",
        "action": "update",
        "resource_type": "users",
        "resource_id": "4",
        "before_state_hash": "abc-before",
        "after_state_hash": "abc-after",
        "result": "failure",
        "error_code": "server",
        "latency_ms": 242.5,
        "client_meta": {"component": "UsersTable"},
    }

    r_ingest = client.post("/api/v1/telemetry/admin-events", headers=headers, json=payload)
    assert r_ingest.status_code == 202
    assert r_ingest.json().get("accepted") is True

    stored = db.query(AdminTelemetryEvent).filter(AdminTelemetryEvent.request_id == "req-test-001").first()
    assert stored is not None
    assert stored.actor_user_id == admin.id
    assert stored.actor_role == "admin"
    assert stored.error_code == "server"
    assert stored.module == "users"
    assert stored.action == "update"

    r_slo = client.get("/api/v1/telemetry/admin-observability/slo?window_minutes=120", headers=headers)
    assert r_slo.status_code == 200
    body = r_slo.json()
    assert body["total_events"] >= 1
    assert body["failed_events"] >= 1
    assert body["error_rate"] > 0
    assert body["action_success_rate"] < 100
    assert "p95" in body["latency_ms"]

    r_complete = client.get("/api/v1/telemetry/admin-observability/completeness?window_minutes=120", headers=headers)
    assert r_complete.status_code == 200
    complete_body = r_complete.json()
    assert complete_body["events"] >= 1
    assert complete_body["completeness_percent"] >= 95.0
    assert complete_body["meets_target"] is True


def test_admin_request_middleware_captures_request_id_and_latency(client, db):
    admin = _create_admin(db, "observability_admin_mw@example.com")
    token = create_access_token(admin.id)
    request_id = "req-middleware-abc"
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Request-ID": request_id,
    }

    r = client.get("/admin/users?limit=1", headers=headers)
    assert r.status_code == 200
    assert r.headers.get("X-Request-ID") == request_id

    logged = (
        db.query(AdminTelemetryEvent)
        .filter(
            AdminTelemetryEvent.request_id == request_id,
        )
        .order_by(AdminTelemetryEvent.id.desc())
        .first()
    )
    assert logged is not None
    assert logged.resource_type == "users"
    assert logged.action == "view"
    assert logged.actor_role == "admin"
    assert logged.result == "success"
    assert logged.latency_ms is not None
