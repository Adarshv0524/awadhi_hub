import uuid

from app.auth.hash import hash_password
from app.core.permissions import Role
from app.db.models import (
    User,
    Submission,
    DohaEntry,
    DictionaryEntry,
    ArticleEntry,
    EngagementKPI,
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
    s_public_dictionary = Submission(
        content_type="dictionary",
        main_text="public approved dictionary",
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
        s_public_dictionary,
        s_private_approved,
        s_public_no_engagement,
        s_pending,
        s_rejected,
    ])
    db.commit()
    db.refresh(s_public_doha)
    db.refresh(s_public_article)
    db.refresh(s_public_dictionary)
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
    dictionary_public = DictionaryEntry(
        lemma_devanagari="लोक",
        lemma_roman="lok",
        language="hi",
        senses=[{"sense": "people"}],
        visibility="public",
        version=1,
        source_submission_id=s_public_dictionary.id,
    )
    db.add_all([doha_public, doha_private, doha_inactive, article_public, dictionary_public])
    db.commit()
    db.refresh(doha_public)
    db.refresh(doha_private)
    db.refresh(doha_inactive)
    db.refresh(article_public)
    db.refresh(dictionary_public)

    kpi_public_doha = EngagementKPI(
        content_type="doha",
        content_id=doha_public.id,
        likes_count=3,
        bookmarks_count=1,
        weight_score=12.0,
    )
    kpi_public_article = EngagementKPI(
        content_type="article",
        content_id=article_public.id,
        likes_count=5,
        bookmarks_count=2,
        weight_score=18.0,
    )
    kpi_public_dictionary = EngagementKPI(
        content_type="dictionary",
        content_id=dictionary_public.id,
        likes_count=7,
        bookmarks_count=1,
        weight_score=30.0,
    )
    # Private submission canonical content should not influence public stats.
    kpi_private_doha = EngagementKPI(
        content_type="doha",
        content_id=doha_private.id,
        likes_count=100,
        weight_score=99.0,
    )
    db.add_all([kpi_public_doha, kpi_public_article, kpi_public_dictionary, kpi_private_doha])
    db.commit()

    r = client.get(f"/users/{contributor.username}/stats")
    assert r.status_code == 200
    body = r.json()

    assert body["username"] == contributor.username
    assert body["contributions_count"] == 4
    assert body["likes_received"] == 15
    assert body["most_liked_content_id"] == dictionary_public.id
    assert body["average_engagement_score"] == 20.0
    assert body["joined_date"]


def test_public_user_stats_user_not_found(client):
    r = client.get("/users/not-a-real-user/stats")
    assert r.status_code == 404


def test_public_user_stats_excludes_deleted_submissions(client, db):
    suffix = uuid.uuid4().hex[:8]
    contributor = create_user(db, f"stats-del-{suffix}@example.com", f"stats-del-{suffix}")

    deleted_submission = Submission(
        content_type="article",
        main_text="deleted approved article",
        status="approved",
        visibility="public",
        contributor_id=contributor.id,
        version=1,
        priority=0,
        is_deleted=True,
    )
    db.add(deleted_submission)
    db.commit()
    db.refresh(deleted_submission)

    article = ArticleEntry(
        title="deleted submission article",
        body="body",
        visibility="public",
        version=1,
        source_submission_id=deleted_submission.id,
    )
    db.add(article)
    db.commit()
    db.refresh(article)

    db.add(
        EngagementKPI(
            content_type="article",
            content_id=article.id,
            likes_count=11,
            weight_score=25.0,
        )
    )
    db.commit()

    r = client.get(f"/users/{contributor.username}/stats")
    assert r.status_code == 200
    body = r.json()

    assert body["contributions_count"] == 0
    assert body["likes_received"] == 0
    assert body["average_engagement_score"] == 0.0
    assert body["most_liked_content_id"] is None
