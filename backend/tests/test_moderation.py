# tests/test_moderation.py

from app.db.models import User, ClassicalAuthor, ClassicalWork, WorkChapter, Submission, ModerationLog
from app.auth.hash import hash_password
from app.auth.jwt import create_access_token
from app.core.permissions import Role


def create_user(db, email: str, role: str, username: str) -> User:
    u = User(
        email=email,
        username=username,
        password_hash=hash_password("Pass123!"),
        role=role,
        permissions=0,
        is_active=True,
        is_banned=False,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


def create_hierarchy(db):
    # 1. Check or Create Author
    author = db.query(ClassicalAuthor).filter_by(slug="tulsidas").first()
    if not author:
        author = ClassicalAuthor(slug="tulsidas", name="Goswami Tulsidas", language="awadhi")
        db.add(author)
        db.commit()
        db.refresh(author)

    # 2. Check or Create Work
    work = db.query(ClassicalWork).filter_by(slug="ramcharitmanas").first()
    if not work:
        work = ClassicalWork(author_id=author.id, slug="ramcharitmanas", title="Ramcharitmanas", work_type="epic")
        db.add(work)
        db.commit()
        db.refresh(work)

    # 3. Check or Create Chapter
    chapter = db.query(WorkChapter).filter_by(slug="ayodhya-kand").first()
    if not chapter:
        chapter = WorkChapter(work_id=work.id, slug="ayodhya-kand", title="अयोध्या काण्ड", number=2)
        db.add(chapter)
        db.commit()
        db.refresh(chapter)

    return author, work, chapter


def create_pending_submission(db, contributor_id: int, is_classical: bool = False) -> Submission:
    sub = Submission(
        content_type="doha",
        main_text="pending doha",
        meaning="meaning",
        is_classical=is_classical,
        author_slug="tulsidas" if is_classical else None,
        work_slug="ramcharitmanas" if is_classical else None,
        chapter_slug="ayodhya-kand" if is_classical else None,
        number_in_chapter=23 if is_classical else None,
        status="pending_review",
        visibility="private",
        version=1,
        contributor_id=contributor_id,
        priority=0,
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub


def test_non_moderator_cannot_access_queue(client, db):
    user = create_user(db, "u1@example.com", Role.REGISTERED, "u1")
    token = create_access_token(user.id)

    r = client.get(
        "/moderation/submissions",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 403


def test_list_and_approve_submission(client, db):
    create_hierarchy(db)
    contributor = create_user(db, "c1@example.com", Role.REGISTERED, "contrib")
    moderator = create_user(db, "m1@example.com", Role.MODERATOR, "mod1")

    # create pending submission
    sub = create_pending_submission(db, contributor_id=contributor.id, is_classical=True)

    mod_token = create_access_token(moderator.id)

    # queue listing
    r = client.get(
        "/moderation/submissions",
        headers={"Authorization": f"Bearer {mod_token}"},
    )
    assert r.status_code == 200
    items = r.json()
    assert any(i["id"] == sub.id for i in items)

    # approve
    r = client.post(
        f"/moderation/submissions/{sub.id}/approve",
        headers={"Authorization": f"Bearer {mod_token}"},
        json={
            "note": "Looks good",
            "guideline_version": "v1",
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "approved"
    assert body["assigned_moderator_id"] == moderator.id

    # ensure moderation log exists
    logs = db.query(ModerationLog).filter(ModerationLog.submission_id == sub.id).all()
    assert len(logs) == 1
    assert logs[0].action == "approve"
    assert logs[0].from_status == "pending_review"
    assert logs[0].to_status == "approved"


def test_reject_allows_later_edit_by_contributor(client, db):
    contributor = create_user(db, "c2@example.com", Role.REGISTERED, "contrib2")
    moderator = create_user(db, "m2@example.com", Role.MODERATOR, "mod2")
    sub = create_pending_submission(db, contributor_id=contributor.id, is_classical=False)

    mod_token = create_access_token(moderator.id)

    # reject
    r = client.post(
        f"/moderation/submissions/{sub.id}/reject",
        headers={"Authorization": f"Bearer {mod_token}"},
        json={"note": "Not accurate"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "rejected"

    # contributor can now edit because 'rejected' is allowed in ALLOWED_STATUSES_FOR_USER_EDIT
    contrib_token = create_access_token(contributor.id)
    r = client.put(
        f"/submissions/{sub.id}",
        headers={"Authorization": f"Bearer {contrib_token}"},
        json={
            "main_text": "fixed text",
            "expected_version": body["version"],
        },
    )
    assert r.status_code == 200
    assert r.json()["main_text"] == "fixed text"


def test_batch_approve(client, db):
    contributor = create_user(db, "c3@example.com", Role.REGISTERED, "contrib3")
    moderator = create_user(db, "m3@example.com", Role.MODERATOR, "mod3")

    s1 = create_pending_submission(db, contributor_id=contributor.id)
    s2 = create_pending_submission(db, contributor_id=contributor.id)

    mod_token = create_access_token(moderator.id)

    r = client.post(
        "/moderation/batch",
        headers={"Authorization": f"Bearer {mod_token}"},
        json={
            "action": "approve",
            "submission_ids": [s1.id, s2.id],
            "note": "Batch OK",
            "guideline_version": "v1",
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["count"] == 2

    # verify statuses
    # FIX: Retrieve fresh objects or refresh the existing ones
    s1_db = db.query(Submission).get(s1.id)
    s2_db = db.query(Submission).get(s2.id)
    
    # Refresh to ensure we see the changes made by the API request
    db.refresh(s1_db)
    db.refresh(s2_db)

    assert s1_db.status == "approved"
    assert s2_db.status == "approved"
    

def test_batch_fails_if_missing_submission(client, db):
    contributor = create_user(db, "c4@example.com", Role.REGISTERED, "contrib4")
    moderator = create_user(db, "m4@example.com", Role.MODERATOR, "mod4")

    s1 = create_pending_submission(db, contributor_id=contributor.id)
    mod_token = create_access_token(moderator.id)

    # attempt to approve s1 and a non-existent id
    r = client.post(
        "/moderation/batch",
        headers={"Authorization": f"Bearer {mod_token}"},
        json={
            "action": "approve",
            "submission_ids": [s1.id, 9999],
            "note": "should fail",
        },
    )
    assert r.status_code == 400
    assert "not found" in r.json()["detail"]

    # s1 should still be pending_review
    s1_db = db.query(Submission).get(s1.id)
    assert s1_db.status == "pending_review"
