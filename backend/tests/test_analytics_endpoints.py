from app.db.models import User, Submission
from app.services.admin_telemetry_service import AdminTelemetryEventData, persist_admin_telemetry_event
from app.auth.hash import hash_password
from app.auth.jwt import create_access_token


def _create_admin(db, email: str = "analytics_admin@example.com"):
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


def test_analytics_summary_endpoint_exists(client, db):
    admin = _create_admin(db, "analytics_admin_summary@example.com")
    token = create_access_token(admin.id)
    headers = {"Authorization": f"Bearer {token}"}

    pending = Submission(
        content_type="doha",
        main_text="pending submission",
        meaning="pending meaning",
        is_classical=False,
        status="pending_review",
        visibility="public",
        version=1,
        contributor_id=admin.id,
    )
    approved = Submission(
        content_type="doha",
        main_text="approved submission",
        meaning="approved meaning",
        is_classical=False,
        status="approved",
        visibility="public",
        version=1,
        contributor_id=admin.id,
    )
    db.add_all([pending, approved])
    db.commit()

    r = client.get("/analytics/summary", headers=headers)
    assert r.status_code == 200
    body = r.json()
    assert "today_approved" in body
    assert "pending_review" in body
    assert "total_approved" in body
    assert body["pending_review"] >= 1
    assert body["total_approved"] >= 1


def test_admin_analytics_alias_endpoints_exist(client, db):
    admin = _create_admin(db, "analytics_admin_alias@example.com")
    token = create_access_token(admin.id)
    headers = {"Authorization": f"Bearer {token}"}

    r_summary = client.get("/admin/analytics/summary", headers=headers)
    assert r_summary.status_code == 200

    r_summary_v2 = client.get("/admin/analytics/v2/summary", headers=headers)
    assert r_summary_v2.status_code == 200

    r_growth_v2 = client.get("/admin/analytics/v2/growth", headers=headers)
    assert r_growth_v2.status_code == 200
    growth_v2 = r_growth_v2.json()
    assert isinstance(growth_v2, dict)
    assert "dates" in growth_v2
    assert "series" in growth_v2

    r_top_v2 = client.get("/admin/analytics/v2/top", headers=headers)
    assert r_top_v2.status_code == 200
    assert isinstance(r_top_v2.json(), list)

    r_demand_v2 = client.get("/admin/analytics/v2/demand", headers=headers)
    assert r_demand_v2.status_code == 200
    assert isinstance(r_demand_v2.json(), dict)

    persist_admin_telemetry_event(
        db,
        AdminTelemetryEventData(
            request_id="req-analytics-1",
            actor_user_id=admin.id,
            actor_role="admin",
            session_id="sess-analytics-1",
            module="moderation",
            action="approve",
            resource_type="moderation/submissions",
            resource_id="42",
            before_state_hash="before",
            after_state_hash="after",
            result="success",
            latency_ms=110.0,
            client_meta={"path": "/moderation/42"},
        ),
    )
    persist_admin_telemetry_event(
        db,
        AdminTelemetryEventData(
            request_id="req-analytics-2",
            actor_user_id=admin.id,
            actor_role="moderator",
            session_id="sess-analytics-2",
            module="users",
            action="view",
            resource_type="/admin/users",
            resource_id="1",
            before_state_hash="",
            after_state_hash="",
            result="failure",
            error_code="permission",
            latency_ms=15.0,
            client_meta={"path": "/admin/users"},
        ),
    )

    r_throughput = client.get("/admin/analytics/v2/action-throughput", headers=headers)
    assert r_throughput.status_code == 200
    assert isinstance(r_throughput.json(), list)

    r_cycle = client.get("/admin/analytics/v2/moderation-cycle-time", headers=headers)
    assert r_cycle.status_code == 200
    assert "p95_ms" in r_cycle.json()

    r_denials = client.get("/admin/analytics/v2/rbac-denials", headers=headers)
    assert r_denials.status_code == 200
    assert isinstance(r_denials.json(), list)

    r_events = client.get("/admin/analytics/v2/events?module=users", headers=headers)
    assert r_events.status_code == 200
    assert isinstance(r_events.json(), list)

    # Deprecated analytics endpoints must be removed from backend contract.
    for removed_path in [
        "/analytics/top",
        "/analytics/growth",
        "/analytics/demand",
        "/admin/analytics/contributor-trends",
        "/admin/analytics/content-performance",
    ]:
        removed = client.get(removed_path, headers=headers)
        assert removed.status_code == 404
