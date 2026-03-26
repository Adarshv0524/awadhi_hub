from app.db.models import User, Submission
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

    r_trends = client.get("/admin/analytics/contributor-trends", headers=headers)
    assert r_trends.status_code == 200
    trends = r_trends.json()
    assert isinstance(trends, dict)
    assert "dates" in trends
    assert "series" in trends

    r_perf = client.get("/admin/analytics/content-performance", headers=headers)
    assert r_perf.status_code == 200
    assert isinstance(r_perf.json(), list)
