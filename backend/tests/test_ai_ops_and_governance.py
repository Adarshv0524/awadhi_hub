from app.auth.hash import hash_password
from app.auth.jwt import create_access_token
from app.db.models import AuditLog, AdminTelemetryEvent, Submission, User
from app.services.admin_telemetry_service import AdminTelemetryEventData, persist_admin_telemetry_event


def _create_user(db, email: str, role: str) -> User:
    user = User(
        email=email,
        username=email.split("@")[0],
        password_hash=hash_password("Pass123!"),
        role=role,
        is_active=True,
        is_banned=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_ai_risk_score_and_moderation_triage(client, db):
    admin = _create_user(db, "ai_admin@example.com", "admin")
    moderator = _create_user(db, "ai_moderator@example.com", "moderator")

    db.add(
        AuditLog(
            actor_user_id=admin.id,
            action="setting:update",
            resource_type="system_setting",
            resource_id=1,
            audit_before={"value": 10},
            after={"value": 50},
            audit_metadata={"ip_address": "127.0.0.1"},
        )
    )
    db.commit()

    persist_admin_telemetry_event(
        db,
        AdminTelemetryEventData(
            actor_user_id=admin.id,
            actor_role="admin",
            session_id="sess-ai-1",
            request_id="req-ai-1",
            module="settings",
            action="update",
            resource_type="system_setting",
            resource_id="1",
            before_state_hash="a",
            after_state_hash="b",
            result="failure",
            error_code="server",
            latency_ms=22,
            client_meta={"ip": "127.0.0.1"},
        ),
    )

    db.add(
        Submission(
            content_type="doha",
            main_text="This is a pending moderation sample text with enough context for AI triage scoring.",
            meaning="Sample meaning",
            is_classical=False,
            status="pending_review",
            visibility="private",
            version=1,
            contributor_id=admin.id,
            priority=2,
        )
    )
    db.commit()

    admin_headers = {"Authorization": f"Bearer {create_access_token(admin.id)}"}
    mod_headers = {"Authorization": f"Bearer {create_access_token(moderator.id)}"}

    risk = client.post(
        "/api/v1/ai/settings-risk-score",
        headers={**admin_headers, "Content-Type": "application/json"},
        json={"setting_key": "rate_limits", "old_value": 10, "new_value": 40},
    )
    assert risk.status_code == 200
    risk_body = risk.json()
    assert "risk_score" in risk_body
    assert 0 <= risk_body["risk_score"] <= 1
    assert isinstance(risk_body.get("rationale"), list)

    triage = client.get("/api/v1/ai/moderation-triage?limit=10", headers=mod_headers)
    assert triage.status_code == 200
    rows = triage.json()
    assert len(rows) >= 1
    assert "confidence" in rows[0]
    assert "rationale_snippets" in rows[0]
    assert "recommendation_id" in rows[0]


def test_3d_analytics_and_governance_exports(client, db):
    admin = _create_user(db, "export_admin@example.com", "admin")
    moderator = _create_user(db, "export_mod@example.com", "moderator")

    persist_admin_telemetry_event(
        db,
        AdminTelemetryEventData(
            actor_user_id=moderator.id,
            actor_role="moderator",
            session_id="sess-gov-1",
            request_id="req-gov-1",
            module="moderation",
            action="approve",
            resource_type="/moderation/submissions",
            resource_id="42",
            before_state_hash="x",
            after_state_hash="y",
            result="success",
            latency_ms=88,
            client_meta={"user_agent": "secret-agent", "safe": "ok"},
        ),
    )
    db.add(
        AuditLog(
            actor_user_id=moderator.id,
            action="moderation:approve",
            resource_type="submission",
            resource_id=42,
            audit_before={"email": "pii@example.com", "old": "a"},
            after={"new": "b"},
            audit_metadata={"ip_address": "127.0.0.1"},
        )
    )
    db.commit()

    admin_headers = {"Authorization": f"Bearer {create_access_token(admin.id)}"}
    mod_headers = {"Authorization": f"Bearer {create_access_token(moderator.id)}"}

    graph = client.get("/admin/analytics/v2/3d/actor-resource-graph", headers=admin_headers)
    assert graph.status_code == 200
    assert "nodes" in graph.json()
    assert "links" in graph.json()

    surface = client.get("/admin/analytics/v2/3d/latency-error-surface", headers=admin_headers)
    assert surface.status_code == 200
    assert isinstance(surface.json(), list)

    export_audit = client.get("/api/v1/governance/export/audit", headers=mod_headers)
    assert export_audit.status_code == 200
    audit_rows = export_audit.json()["results"]
    assert len(audit_rows) >= 1
    assert audit_rows[0]["actor_user_id"] is None
    assert audit_rows[0]["before"].get("email") == "[REDACTED]"

    export_telemetry = client.get("/api/v1/governance/export/telemetry", headers=mod_headers)
    assert export_telemetry.status_code == 200
    telemetry_rows = export_telemetry.json()["results"]
    assert len(telemetry_rows) >= 1
    assert telemetry_rows[0]["actor_user_id"] is None
    assert telemetry_rows[0]["client_meta"].get("user_agent") == "[REDACTED]"

    retention = client.post("/api/v1/governance/retention/run", headers=admin_headers)
    assert retention.status_code == 200
    assert "admin_telemetry_deleted" in retention.json()
