# tests/test_batch_moderation_atomic.py
import uuid
from app.db.models import Submission, User, DohaEntry
from app.auth.hash import hash_password
from app.auth.jwt import create_access_token

def create_admin(db, username_suffix=""):
    """Create admin with unique username"""
    username = f"batadm{username_suffix}"
    admin = User(
        email=f"{username}@ex.com",
        username=username,
        password_hash=hash_password("P@ss123"),
        role="admin"
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin

def create_doha_submission(db, user_id, content="test doha", submit_for_review=True):
    sub = Submission(
        content_type="doha",
        main_text=content,
        meaning="meaning",
        is_classical=False,
        external_references=None,
        status="pending_review" if submit_for_review else "draft",
        visibility="public",
        version=1,
        contributor_id=user_id,
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub

def test_batch_approve_success(client, db):
    admin = create_admin(db, "_success")
    s1 = create_doha_submission(db, admin.id)
    s2 = create_doha_submission(db, admin.id)
    token = create_access_token(admin.id)
    headers = {"Authorization": f"Bearer {token}"}
    
    # FIX: Correct endpoint path (no /admin prefix)
    r = client.post(
        "/moderation/batch_approve",
        json={"submission_ids": [s1.id, s2.id]},
        headers=headers
    )
    assert r.status_code == 200, r.text
    j = r.json()
    assert "batch_id" in j
    assert len(j["created"]) == 2
    
    # Verify canonical entries exist
    c1 = db.query(DohaEntry).filter(DohaEntry.source_submission_id == s1.id).first()
    c2 = db.query(DohaEntry).filter(DohaEntry.source_submission_id == s2.id).first()
    assert c1 is not None and c2 is not None

def test_batch_approve_atomic_failure(db, client):
    admin = create_admin(db, "_atomic")  # FIX: Unique username
    
    # Create one valid and one invalid submission (invalid status)
    s1 = create_doha_submission(db, admin.id, submit_for_review=True)
    s2 = create_doha_submission(db, admin.id, submit_for_review=False)  # draft - invalid
    
    token = create_access_token(admin.id)
    headers = {"Authorization": f"Bearer {token}"}
    
    # FIX: Correct endpoint path
    r = client.post(
        "/moderation/batch_approve",
        json={"submission_ids": [s1.id, s2.id]},
        headers=headers
    )
    assert r.status_code == 400
    
    # Ensure no canonical was created for s1 (atomic rollback)
    c1 = db.query(DohaEntry).filter(DohaEntry.source_submission_id == s1.id).first()
    assert c1 is None
