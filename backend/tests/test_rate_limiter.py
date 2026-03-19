# tests/test_rate_limiter.py
import uuid
import time
from app.db.models import User, RateLimitCounter, SystemSetting
from app.auth.hash import hash_password


def test_login_rate_limit_blocks_after_limit(client, db):
    """Test that rate limiting blocks after configured limit"""
    # SETUP: Ensure table exists
    engine = db.get_bind()
    RateLimitCounter.__table__.create(bind=engine, checkfirst=True)
    
    # CRITICAL: Set rate limit to 10 for this test
    rate_limit_config = {
        "login": {"limit": 10, "window_seconds": 3600},
        "search": {"limit": 120, "window_seconds": 60},
        "submission_create": {"limit": 20, "window_seconds": 86400}
    }
    
    # Check if setting exists, update or create
    existing_setting = db.query(SystemSetting).filter(SystemSetting.setting_key == "rate_limits").first()
    if existing_setting:
        existing_setting.value = rate_limit_config
    else:
        db.add(SystemSetting(setting_key="rate_limits", value=rate_limit_config))
    db.commit()
    
    # ISOLATE: Clear all rate limit counters
    db.query(RateLimitCounter).delete()
    db.commit()
    
    # Create unique user
    email = f"rl-{uuid.uuid4().hex[:6]}@example.com"
    pwd = "Aa123456!"
    user = User(
        email=email,
        username=email.split("@")[0],
        password_hash=hash_password(pwd),
        role="registered"
    )
    db.add(user)
    db.commit()

    # Perform 10 FAILED login attempts (matches our configured limit)
    for i in range(10):
        r = client.post("/auth/login", json={"email": email, "password": "WrongPassword"})
        time.sleep(0.1)
        print(f"Attempt {i+1}: status={r.status_code}")
        assert r.status_code == 401, f"expected 401 on attempt {i+1}, got {r.status_code}"

    # Verify counter state
    db.expire_all()
    count_records = db.query(RateLimitCounter).count()
    print(f"\n=== RATE LIMIT RECORDS: {count_records}")
    for record in db.query(RateLimitCounter).all():
        print(f"  action={record.action_key}, count={record.count}")

    # 11th attempt should be blocked with 429
    r = client.post("/auth/login", json={"email": email, "password": "WrongPassword"})
    print(f"Attempt 11: status={r.status_code}")
    assert r.status_code == 429, f"Expected 429 Too Many Requests, got {r.status_code}: {r.text}"
    assert "Retry-After" in r.headers


def test_search_endpoint_still_works_under_limit(client):
    """Test that search works normally under rate limit"""
    r = client.get("/search", params={"q": "test"})
    assert r.status_code == 200


def test_submission_create_with_auth_and_rate_limit(client, db):
    """Test submission creation with authentication and rate limiting"""
    from app.auth.jwt import create_access_token
    
    # Ensure table exists
    engine = db.get_bind()
    RateLimitCounter.__table__.create(bind=engine, checkfirst=True)
    
    # Create unique user
    email = f"sub-{uuid.uuid4().hex[:6]}@example.com"
    pwd = "Aa123456!"
    user = User(
        email=email,
        username=email.split("@")[0],
        password_hash=hash_password(pwd),
        role="registered"
    )
    db.add(user)
    db.commit()
    token = create_access_token(user.id)

    headers = {"Authorization": f"Bearer {token}"}
    r = client.post(
        "/submissions",
        json={"content_type": "doha", "main_text": "test", "meaning": "x"},
        headers=headers
    )
    assert r.status_code in (200, 201)
