import uuid

from app.auth.hash import hash_password
from app.core.permissions import Role
from app.db.models import (
    User,
    Submission,
    DohaEntry,
    ArticleEntry,
    UserInteraction,
)


def create_user(db, email: str, username: str, role: str = Role.REGISTERED) -> User:
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


def test_public_user_stats_aggregates_only_approved_public_content(client, db):
    suffix = uuid.uuid4().hex[:8]
    contributor = create_user(db, f"stats-contrib-{suffix}@example.com", f"stats-contrib-{suffix}")
    reactor = create_user(db, f"stats-reactor-{suffix}@example.com", f"stats-reactor-{suffix}")

    s_public_doha = Submission(
        content_type="doha",
        main_text="public approved doha",
        status="approved",
        visibility="public",
        contributor_id=contributor.id,
        version=1,
        priority=0,
        is_deleted=False,
    )
    s_public_article = Submission(
        content_type="article",
        main_text="public approved article",
        status="approved",
        visibility="public",
        contributor_id=contributor.id,
        version=1,
        priority=0,
        is_deleted=False,
    )
    s_private_approved = Submission(
        content_type="doha",
        main_text="private approved doha",
        status="approved",
        visibility="private",
        contributor_id=contributor.id,
        version=1,
        priority=0,
        is_deleted=False,
    )
    s_public_no_engagement = Submission(
        content_type="doha",
        main_text="public approved doha no engagement",
        status="approved",
        visibility="public",
        contributor_id=contributor.id,
        version=1,
        priority=0,
        is_deleted=False,
    )
    s_pending = Submission(
        content_type="doha",
        main_text="pending doha",
        status="pending_review",
        visibility="public",
        contributor_id=contributor.id,
        version=1,
        priority=0,
        is_deleted=False,
    )
    s_rejected = Submission(
        content_type="doha",
        main_text="rejected doha",
        status="rejected",
        visibility="public",
        contributor_id=contributor.id,
        version=1,
        priority=0,
        is_deleted=False,
    )
    db.add_all([
        s_public_doha,
        s_public_article,
        s_private_approved,
        s_public_no_engagement,
        s_pending,
        s_rejected,
    ])
    db.commit()
    db.refresh(s_public_doha)
    db.refresh(s_public_article)
    db.refresh(s_private_approved)
    db.refresh(s_public_no_engagement)

    doha_public = DohaEntry(
        main_text="canonical public doha",
        status="active",
        visibility="public",
        version=1,
        is_canonical=True,
        source_submission_id=s_public_doha.id,
    )
    doha_private = DohaEntry(
        main_text="canonical private doha",
        status="active",
        visibility="private",
        version=1,
        is_canonical=True,
        source_submission_id=s_private_approved.id,
    )
    doha_inactive = DohaEntry(
        main_text="canonical inactive-liked doha",
        status="active",
        visibility="public",
        version=1,
        is_canonical=True,
        source_submission_id=s_public_no_engagement.id,
    )
    article_public = ArticleEntry(
        title="canonical public article",
        body="body",
        visibility="public",
        version=1,
        source_submission_id=s_public_article.id,
    )
    db.add_all([doha_public, doha_private, doha_inactive, article_public])
    db.commit()
    db.refresh(doha_public)
    db.refresh(doha_private)
    db.refresh(doha_inactive)
    db.refresh(article_public)

    like_public_doha = UserInteraction(
        user_id=reactor.id,
        content_type="doha",
        content_id=doha_public.id,
        interaction_type="like",
        is_active=True,
    )
    bookmark_public_doha = UserInteraction(
        user_id=reactor.id,
        content_type="doha",
        content_id=doha_public.id,
        interaction_type="bookmark",
        is_active=True,
    )
    like_public_article = UserInteraction(
        user_id=reactor.id,
        content_type="article",
        content_id=article_public.id,
        interaction_type="like",
        is_active=True,
    )
    bookmark_public_article = UserInteraction(
        user_id=reactor.id,
        content_type="article",
        content_id=article_public.id,
        interaction_type="bookmark",
        is_active=True,
    )
    like_private_doha = UserInteraction(
        user_id=reactor.id,
        content_type="doha",
        content_id=doha_private.id,
        interaction_type="like",
        is_active=True,
    )
    inactive_like_public = UserInteraction(
        user_id=reactor.id,
        content_type="doha",
        content_id=doha_inactive.id,
        interaction_type="like",
        is_active=False,
    )
    db.add_all(
        [
            like_public_doha,
            bookmark_public_doha,
            like_public_article,
            bookmark_public_article,
            like_private_doha,
            inactive_like_public,
        ]
    )
    db.commit()

    r = client.get(f"/users/{contributor.username}/stats")
    assert r.status_code == 200
    body = r.json()

    assert body["public_submissions"] == 3
    assert body["approved_count"] == 3
    assert body["likes_received"] == 2
    assert body["bookmarks_received"] == 2


def test_public_user_stats_user_not_found(client):
    r = client.get("/users/not-a-real-user/stats")
    assert r.status_code == 404
