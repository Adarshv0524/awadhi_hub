from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import inspect, text

from app.auth.hash import hash_password
from app.db.models import (
    Base,
    User,
    RefreshToken,
    OAuthAccount,
    ClassicalAuthor,
    ClassicalWork,
    WorkChapter,
    Submission,
    ModerationGuideline,
    ModerationLog,
    DohaEntry,
    ContentVersion,
    DictionaryEntry,
    IdiomEntry,
    ArticleEntry,
    EngagementKPI,
    UserInteraction,
    ShareLog,
    Report,
    RateLimitCounter,
    SystemSetting,
    AuditLog,
)
from app.db.session import SessionLocal, engine


def _table_columns(table_name: str) -> set[str]:
    insp = inspect(engine)
    if table_name not in insp.get_table_names():
        return set()
    return {c["name"] for c in insp.get_columns(table_name)}


def reconcile_schema() -> None:
    with engine.begin() as conn:
        # Ensure submissions has external_references expected by ORM + Pydantic.
        sub_cols = _table_columns("submissions")
        if "submissions" in inspect(engine).get_table_names() and "external_references" not in sub_cols:
            conn.execute(text("ALTER TABLE submissions ADD COLUMN external_references JSON NULL"))
            if "references" in sub_cols:
                conn.execute(
                    text("UPDATE submissions SET external_references = `references` WHERE external_references IS NULL")
                )

        # Ensure system_settings PK column name matches ORM (setting_key).
        ss_cols = _table_columns("system_settings")
        if "system_settings" in inspect(engine).get_table_names() and "setting_key" not in ss_cols and "key" in ss_cols:
            conn.execute(text("ALTER TABLE system_settings CHANGE COLUMN `key` setting_key VARCHAR(255) NOT NULL"))

        # Ensure alembic revision IDs do not overflow on future upgrades.
        av_cols = _table_columns("alembic_version")
        if "version_num" in av_cols:
            conn.execute(text("ALTER TABLE alembic_version MODIFY COLUMN version_num VARCHAR(255) NOT NULL"))

        # Ensure audit_logs column names match ORM model.
        audit_cols = _table_columns("audit_logs")
        if "audit_logs" in inspect(engine).get_table_names():
            if "audit_before" not in audit_cols and "before" in audit_cols:
                conn.execute(text("ALTER TABLE audit_logs CHANGE COLUMN `before` audit_before JSON NULL"))
            if "audit_metadata" not in audit_cols and "metadata" in audit_cols:
                conn.execute(text("ALTER TABLE audit_logs CHANGE COLUMN `metadata` audit_metadata JSON NULL"))

    Base.metadata.create_all(bind=engine)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def get_or_create_user(db, *, email: str, username: str | None, role: str, permissions: int = 0, scopes: Any = None):
    obj = db.query(User).filter(User.email == email).first()
    if obj:
        return obj
    obj = User(
        email=email,
        username=username,
        password_hash=hash_password("Seed@12345"),
        role=role,
        permissions=permissions,
        permission_scopes=scopes,
        is_active=True,
        is_banned=False,
    )
    db.add(obj)
    db.flush()
    return obj


def get_or_create_author(db, slug: str, name: str, short_bio: str, language: str):
    obj = db.query(ClassicalAuthor).filter(ClassicalAuthor.slug == slug).first()
    if obj:
        return obj
    obj = ClassicalAuthor(slug=slug, name=name, short_bio=short_bio, language=language, is_deleted=False)
    db.add(obj)
    db.flush()
    return obj


def get_or_create_work(db, author_id: int, slug: str, title: str, work_type: str):
    obj = (
        db.query(ClassicalWork)
        .filter(ClassicalWork.author_id == author_id, ClassicalWork.slug == slug)
        .first()
    )
    if obj:
        return obj
    obj = ClassicalWork(author_id=author_id, slug=slug, title=title, work_type=work_type, is_deleted=False)
    db.add(obj)
    db.flush()
    return obj


def get_or_create_chapter(db, work_id: int, slug: str, title: str, number: int):
    obj = db.query(WorkChapter).filter(WorkChapter.work_id == work_id, WorkChapter.slug == slug).first()
    if obj:
        return obj
    obj = WorkChapter(work_id=work_id, slug=slug, title=title, number=number, is_deleted=False)
    db.add(obj)
    db.flush()
    return obj


def get_or_create_submission(db, **kwargs):
    key_text = kwargs["main_text"]
    obj = db.query(Submission).filter(Submission.main_text == key_text).first()
    if obj:
        return obj
    obj = Submission(**kwargs)
    db.add(obj)
    db.flush()
    return obj


def seed_data() -> dict[str, int]:
    db = SessionLocal()
    try:
        now = _now()

        # Users
        admin = get_or_create_user(
            db,
            email="seed_admin@awadhi.local",
            username="seed_admin",
            role="admin",
            permissions=65535,
            scopes={"all": True},
        )
        moderator = get_or_create_user(
            db,
            email="seed_moderator@awadhi.local",
            username="seed_moderator",
            role="moderator",
            permissions=1024,
            scopes={"moderation": ["approve", "reject"]},
        )
        contributor1 = get_or_create_user(
            db,
            email="seed_contrib1@awadhi.local",
            username="seed_contrib1",
            role="contributor",
            permissions=256,
        )
        contributor2 = get_or_create_user(
            db,
            email="seed_contrib2@awadhi.local",
            username="seed_contrib2",
            role="contributor",
            permissions=256,
        )
        reader = get_or_create_user(
            db,
            email="seed_reader@awadhi.local",
            username="seed_reader",
            role="registered",
            permissions=0,
        )

        # OAuth + refresh tokens
        if not db.query(OAuthAccount).filter(OAuthAccount.provider == "google", OAuthAccount.provider_user_id == "seed_google_sub_001").first():
            db.add(
                OAuthAccount(
                    provider="google",
                    provider_user_id="seed_google_sub_001",
                    user_id=reader.id,
                    raw_profile={"email": reader.email, "name": "Seed Reader"},
                )
            )
        if not db.query(RefreshToken).filter(RefreshToken.token == "seed_refresh_token_admin").first():
            db.add(
                RefreshToken(
                    token="seed_refresh_token_admin",
                    user_id=admin.id,
                    expires_at=now + timedelta(days=10),
                )
            )
        if not db.query(RefreshToken).filter(RefreshToken.token == "seed_refresh_token_mod").first():
            db.add(
                RefreshToken(
                    token="seed_refresh_token_mod",
                    user_id=moderator.id,
                    expires_at=now + timedelta(days=10),
                )
            )

        # Classical hierarchy
        tulsi = get_or_create_author(db, "tulsidas", "Goswami Tulsidas", "Bhakti poet", "Awadhi")
        malik = get_or_create_author(db, "malik-muhammad-jayasi", "Malik Muhammad Jayasi", "Sufi poet", "Awadhi")

        ramcharit = get_or_create_work(db, tulsi.id, "ramcharitmanas", "Ramcharitmanas", "epic")
        vinay = get_or_create_work(db, tulsi.id, "vinay-patrika", "Vinay Patrika", "poetry")
        padmavat = get_or_create_work(db, malik.id, "padmavat", "Padmavat", "epic")

        ch1 = get_or_create_chapter(db, ramcharit.id, "baal-kaand", "Baal Kaand", 1)
        ch2 = get_or_create_chapter(db, ramcharit.id, "ayodhya-kaand", "Ayodhya Kaand", 2)
        ch3 = get_or_create_chapter(db, vinay.id, "prarthana", "Prarthana", 1)
        ch4 = get_or_create_chapter(db, vinay.id, "stuti", "Stuti", 2)
        ch5 = get_or_create_chapter(db, padmavat.id, "khand-1", "Khand 1", 1)
        ch6 = get_or_create_chapter(db, padmavat.id, "khand-2", "Khand 2", 2)

        # Guidelines
        if not db.query(ModerationGuideline).filter(ModerationGuideline.version == "v1.0").first():
            db.add(
                ModerationGuideline(
                    version="v1.0",
                    title="Core Moderation Rules",
                    description="Approve factual and culturally relevant content.",
                    url="https://example.local/moderation/v1",
                    is_active=True,
                )
            )
        if not db.query(ModerationGuideline).filter(ModerationGuideline.version == "v1.1").first():
            db.add(
                ModerationGuideline(
                    version="v1.1",
                    title="Community Style Guide",
                    description="Consistent transliteration and respectful language.",
                    url="https://example.local/moderation/v1.1",
                    is_active=False,
                )
            )

        # Submissions
        sub_specs = [
            {
                "content_type": "doha",
                "main_text": "seed_doha_1: राम नाम बिनु जीवन सूना",
                "meaning": "Without remembrance of Rama, life feels empty.",
                "is_classical": True,
                "author_slug": "tulsidas",
                "work_slug": "ramcharitmanas",
                "chapter_slug": "baal-kaand",
                "number_in_chapter": 1,
                "external_references": {"source": "manuscript-a", "folio": "12a"},
                "status": "approved",
                "visibility": "public",
                "version": 1,
                "contributor_id": contributor1.id,
                "assigned_moderator_id": moderator.id,
                "priority": 5,
                "is_deleted": False,
            },
            {
                "content_type": "doha",
                "main_text": "seed_doha_2: करम बिनु नाहीं फल मिलई",
                "meaning": "No fruit is attained without action.",
                "is_classical": True,
                "author_slug": "tulsidas",
                "work_slug": "ramcharitmanas",
                "chapter_slug": "ayodhya-kaand",
                "number_in_chapter": 2,
                "external_references": {"source": "printed-edition", "page": 45},
                "status": "pending_review",
                "visibility": "private",
                "version": 1,
                "contributor_id": contributor2.id,
                "assigned_moderator_id": moderator.id,
                "priority": 4,
                "is_deleted": False,
            },
            {
                "content_type": "dictionary",
                "main_text": "seed_dict_1_payload",
                "meaning": "Entry payload for 'अनुग्रह'.",
                "is_classical": False,
                "status": "approved",
                "visibility": "public",
                "version": 1,
                "contributor_id": contributor1.id,
                "assigned_moderator_id": moderator.id,
                "priority": 3,
                "is_deleted": False,
                "external_references": {"lemma": "अनुग्रह"},
            },
            {
                "content_type": "idiom",
                "main_text": "seed_idiom_1_payload",
                "meaning": "Idiom payload for 'नयनन मा बसि गइल'.",
                "is_classical": False,
                "status": "approved",
                "visibility": "public",
                "version": 1,
                "contributor_id": contributor2.id,
                "assigned_moderator_id": moderator.id,
                "priority": 2,
                "is_deleted": False,
                "external_references": {"idiom": "नयनन मा बसि गइल"},
            },
            {
                "content_type": "article",
                "main_text": "seed_article_1_payload",
                "meaning": "Article payload on Awadhi oral traditions.",
                "is_classical": False,
                "status": "approved",
                "visibility": "public",
                "version": 1,
                "contributor_id": contributor1.id,
                "assigned_moderator_id": moderator.id,
                "priority": 2,
                "is_deleted": False,
                "external_references": {"topic": "oral traditions"},
            },
            {
                "content_type": "doha",
                "main_text": "seed_doha_3: परहित सरिस धरम नहिं भाई",
                "meaning": "There is no dharma like working for others.",
                "is_classical": True,
                "author_slug": "tulsidas",
                "work_slug": "vinay-patrika",
                "chapter_slug": "prarthana",
                "number_in_chapter": 3,
                "external_references": {"source": "oral-recitation"},
                "status": "approved",
                "visibility": "public",
                "version": 1,
                "contributor_id": contributor1.id,
                "assigned_moderator_id": moderator.id,
                "priority": 5,
                "is_deleted": False,
            },
            {
                "content_type": "doha",
                "main_text": "seed_doha_4: प्रेम पियाला जो पिए",
                "meaning": "One who drinks the cup of love is transformed.",
                "is_classical": True,
                "author_slug": "malik-muhammad-jayasi",
                "work_slug": "padmavat",
                "chapter_slug": "khand-1",
                "number_in_chapter": 4,
                "external_references": {"source": "archive-copy"},
                "status": "rejected",
                "visibility": "private",
                "version": 2,
                "contributor_id": contributor2.id,
                "assigned_moderator_id": moderator.id,
                "priority": 1,
                "is_deleted": False,
            },
            {
                "content_type": "article",
                "main_text": "seed_article_2_payload",
                "meaning": "Article payload on proverbs and ecology.",
                "is_classical": False,
                "status": "draft",
                "visibility": "private",
                "version": 1,
                "contributor_id": contributor2.id,
                "assigned_moderator_id": None,
                "priority": 1,
                "is_deleted": False,
                "external_references": {"topic": "ecology"},
            },
        ]
        submissions = [get_or_create_submission(db, **s) for s in sub_specs]

        # Canonical doha entries from approved doha submissions
        doha_specs = [
            ("tulsidas/ramcharitmanas/baal-kaand/1", ch1, submissions[0], contributor1.id),
            ("tulsidas/vinay-patrika/prarthana/3", ch3, submissions[5], contributor1.id),
            ("jayasi/padmavat/khand-1/1", ch5, submissions[6], contributor2.id),
        ]
        for path, ch, src_sub, creator_id in doha_specs:
            existing = db.query(DohaEntry).filter(DohaEntry.source_submission_id == src_sub.id).first()
            if existing:
                continue
            db.add(
                DohaEntry(
                    hierarchy_path=path,
                    author_id=ch.work.author_id,
                    work_id=ch.work_id,
                    chapter_id=ch.id,
                    number_in_chapter=ch.number,
                    main_text=src_sub.main_text,
                    meaning=src_sub.meaning,
                    text_devanagari=src_sub.main_text,
                    text_romanized=src_sub.main_text,
                    status="active",
                    visibility="public",
                    version=1,
                    is_canonical=True,
                    confidence_level=85,
                    source_reference=src_sub.external_references,
                    source_submission_id=src_sub.id,
                    created_by=creator_id,
                    verified_by=moderator.id,
                    verified_at=now,
                    is_deleted=False,
                )
            )

        db.flush()

        # Canonical dictionary entries
        dict_specs = [
            ("अनुग्रह", "anugrah", "anugrah", submissions[2].id),
            ("अभिराम", "abhiram", "abhiram", None),
            ("उदासीन", "udasin", "udasin", None),
            ("सहज", "sahaj", "sahaj", None),
        ]
        for idx, (lemma_dev, lemma_rom, lemma_norm, src_sub_id) in enumerate(dict_specs, start=1):
            existing = db.query(DictionaryEntry).filter(DictionaryEntry.lemma_devanagari == lemma_dev).first()
            if existing:
                continue
            db.add(
                DictionaryEntry(
                    lemma_devanagari=lemma_dev,
                    lemma_roman=lemma_rom,
                    lemma_roman_norm=lemma_norm,
                    language="hi",
                    senses=[{"gloss": f"Meaning {idx}", "pos": "adj"}],
                    pronunciation=lemma_rom,
                    examples=[{"text": f"{lemma_dev} शब्द का लोक प्रयोग"}],
                    contributor_id=contributor1.id,
                    author_id=tulsi.id,
                    work_id=ramcharit.id,
                    chapter_id=ch1.id,
                    number_in_chapter=idx,
                    source_submission_id=src_sub_id,
                    visibility="public",
                    version=1,
                )
            )

        # Canonical idiom entries
        idiom_specs = [
            ("नयनन मा बसि गइल", "nayanan ma basi gail", submissions[3].id),
            ("धूरि उड़ाइ देब", "dhuri udai deb", None),
            ("मनवा हरसाइ गवा", "manwa harsai gawa", None),
            ("घामे पसीना छुटा", "ghame pasina chhuta", None),
        ]
        for idx, (dev, rom, src_sub_id) in enumerate(idiom_specs, start=1):
            existing = db.query(IdiomEntry).filter(IdiomEntry.text_devanagari == dev).first()
            if existing:
                continue
            db.add(
                IdiomEntry(
                    text_devanagari=dev,
                    text_roman=rom,
                    text_roman_norm=rom,
                    meaning=f"Seed idiom meaning {idx}",
                    examples=[{"text": f"उदाहरण {idx}"}],
                    region="Awadh",
                    contributor_id=contributor2.id,
                    author_id=malik.id,
                    work_id=padmavat.id,
                    chapter_id=ch5.id,
                    number_in_chapter=idx,
                    source_submission_id=src_sub_id,
                    visibility="public",
                    version=1,
                )
            )

        # Canonical article entries
        article_specs = [
            ("Awadhi Oral Traditions", "awadhi-oral-traditions", submissions[4].id),
            ("Village Proverbs and Ecology", "village-proverbs-ecology", None),
            ("Performance Poetry in Awadh", "performance-poetry-awadh", None),
            ("Folk Memory and Language", "folk-memory-language", None),
        ]
        for i, (title, title_norm, src_sub_id) in enumerate(article_specs, start=1):
            existing = db.query(ArticleEntry).filter(ArticleEntry.title == title).first()
            if existing:
                continue
            db.add(
                ArticleEntry(
                    title=title,
                    title_devanagari=title,
                    title_roman=title_norm,
                    title_roman_norm=title_norm,
                    body=f"Seed article body {i}: discusses Awadhi heritage and usage.",
                    excerpt=f"Seed excerpt {i}",
                    author_id=contributor1.id,
                    tags=["awadhi", "culture", "literature"] if i % 2 else ["awadhi", "linguistics"],
                    contributor_id=contributor1.id,
                    source_submission_id=src_sub_id,
                    visibility="public",
                    version=1,
                )
            )

        db.flush()

        # Content versions
        for doha in db.query(DohaEntry).limit(3).all():
            for ver in (1, 2):
                exists = (
                    db.query(ContentVersion)
                    .filter(
                        ContentVersion.content_type == "doha",
                        ContentVersion.content_id == doha.id,
                        ContentVersion.version_number == ver,
                    )
                    .first()
                )
                if exists:
                    continue
                db.add(
                    ContentVersion(
                        content_type="doha",
                        content_id=doha.id,
                        version_number=ver,
                        main_text=doha.main_text,
                        meaning=doha.meaning,
                        text_devanagari=doha.text_devanagari,
                        text_romanized=doha.text_romanized,
                        created_by=moderator.id,
                        notes=f"Seed version {ver}",
                    )
                )

        # Moderation logs
        for sub in submissions[:5]:
            exists = (
                db.query(ModerationLog)
                .filter(
                    ModerationLog.submission_id == sub.id,
                    ModerationLog.action == "seed_review",
                )
                .first()
            )
            if exists:
                continue
            db.add(
                ModerationLog(
                    submission_id=sub.id,
                    moderator_id=moderator.id,
                    action="seed_review",
                    from_status="pending_review" if sub.status != "draft" else "draft",
                    to_status=sub.status,
                    guideline_version="v1.0",
                    note="Seed moderation trail",
                )
            )

        # Engagement KPIs for canonical content
        def ensure_kpi(content_type: str, content_id: int, base: int):
            row = (
                db.query(EngagementKPI)
                .filter(EngagementKPI.content_type == content_type, EngagementKPI.content_id == content_id)
                .first()
            )
            if row:
                return
            db.add(
                EngagementKPI(
                    content_type=content_type,
                    content_id=content_id,
                    views_count=base * 10,
                    search_hits_count=base * 4,
                    likes_count=base * 3,
                    shares_count=base * 2,
                    bookmarks_count=base,
                    weight_score=float(base) * 1.5,
                )
            )

        for i, d in enumerate(db.query(DohaEntry).limit(3).all(), start=1):
            ensure_kpi("doha", d.id, i)
        for i, d in enumerate(db.query(DictionaryEntry).limit(3).all(), start=1):
            ensure_kpi("dictionary", d.id, i + 1)
        for i, d in enumerate(db.query(IdiomEntry).limit(3).all(), start=1):
            ensure_kpi("idiom", d.id, i + 2)
        for i, d in enumerate(db.query(ArticleEntry).limit(3).all(), start=1):
            ensure_kpi("article", d.id, i + 3)

        db.flush()

        # Interactions, shares, reports
        first_doha = db.query(DohaEntry).first()
        first_article = db.query(ArticleEntry).first()
        first_dict = db.query(DictionaryEntry).first()
        first_idiom = db.query(IdiomEntry).first()

        interaction_specs = [
            (reader.id, "doha", first_doha.id if first_doha else 1, "like"),
            (reader.id, "doha", first_doha.id if first_doha else 1, "bookmark"),
            (contributor1.id, "article", first_article.id if first_article else 1, "like"),
            (contributor1.id, "dictionary", first_dict.id if first_dict else 1, "bookmark"),
            (contributor2.id, "idiom", first_idiom.id if first_idiom else 1, "like"),
            (contributor2.id, "article", first_article.id if first_article else 1, "bookmark"),
        ]
        for uid, ctype, cid, itype in interaction_specs:
            row = (
                db.query(UserInteraction)
                .filter(
                    UserInteraction.user_id == uid,
                    UserInteraction.content_type == ctype,
                    UserInteraction.content_id == cid,
                    UserInteraction.interaction_type == itype,
                )
                .first()
            )
            if row:
                continue
            db.add(
                UserInteraction(
                    user_id=uid,
                    content_type=ctype,
                    content_id=cid,
                    interaction_type=itype,
                    is_active=True,
                    interaction_metadata={"seed": True},
                )
            )

        share_specs = [
            (reader.id, "doha", first_doha.id if first_doha else 1, "whatsapp"),
            (reader.id, "article", first_article.id if first_article else 1, "telegram"),
            (contributor1.id, "dictionary", first_dict.id if first_dict else 1, "facebook"),
            (contributor2.id, "idiom", first_idiom.id if first_idiom else 1, "x"),
        ]
        for uid, ctype, cid, channel in share_specs:
            exists = (
                db.query(ShareLog)
                .filter(ShareLog.user_id == uid, ShareLog.content_type == ctype, ShareLog.content_id == cid)
                .first()
            )
            if exists:
                continue
            db.add(
                ShareLog(
                    user_id=uid,
                    content_type=ctype,
                    content_id=cid,
                    share_metadata={"channel": channel, "seed": True},
                )
            )

        report_specs = [
            (reader.id, "doha", first_doha.id if first_doha else 1, "other", "Needs source annotation"),
            (contributor1.id, "article", first_article.id if first_article else 1, "copyright", "Check publication rights"),
            (contributor2.id, "dictionary", first_dict.id if first_dict else 1, "spam", "Duplicated entry"),
            (reader.id, "idiom", first_idiom.id if first_idiom else 1, "abuse", "Contains rude variation"),
        ]
        for uid, ctype, cid, reason, note in report_specs:
            exists = (
                db.query(Report)
                .filter(Report.user_id == uid, Report.content_type == ctype, Report.content_id == cid, Report.reason == reason)
                .first()
            )
            if exists:
                continue
            db.add(
                Report(
                    user_id=uid,
                    content_type=ctype,
                    content_id=cid,
                    reason=reason,
                    note=note,
                    report_metadata={"seed": True},
                    status="open",
                )
            )

        # System settings
        settings_specs = {
            "rate_limits": {
                "login": {"limit": 100, "window_seconds": 3600},
                "search": {"limit": 300, "window_seconds": 60},
                "submission_create": {"limit": 50, "window_seconds": 86400},
            },
            "recommendation_weights": {"likes": 3, "shares": 2, "views": 1, "search_hits": 2},
            "ft_min_word_len": 3,
            "prometheus_enabled": False,
            "backup_retention_days": 30,
        }
        for key, value in settings_specs.items():
            row = db.query(SystemSetting).filter(SystemSetting.setting_key == key).first()
            if row:
                row.value = value
            else:
                db.add(SystemSetting(setting_key=key, value=value))

        # Audit logs
        audit_specs = [
            (admin.id, "seed:create_users", "users", admin.id),
            (admin.id, "seed:create_hierarchy", "classical_authors", tulsi.id),
            (moderator.id, "seed:moderate", "submissions", submissions[0].id),
            (contributor1.id, "seed:create_article", "article_entries", 1),
            (reader.id, "seed:report_content", "reports", 1),
        ]
        for actor, action, rtype, rid in audit_specs:
            exists = db.query(AuditLog).filter(AuditLog.action == action, AuditLog.resource_type == rtype, AuditLog.resource_id == rid).first()
            if exists:
                continue
            db.add(
                AuditLog(
                    actor_user_id=actor,
                    action=action,
                    resource_type=rtype,
                    resource_id=rid,
                    audit_before=None,
                    after={"seed": True},
                    audit_metadata={"source": "bootstrap_schema_and_seed"},
                )
            )

        # Rate limit counters
        rl_specs = [
            (reader.id, None, "login", 2, 60),
            (None, "127.0.0.1", "search", 15, 60),
            (contributor1.id, None, "submission_create", 1, 3600),
        ]
        bucket = now.replace(minute=0, second=0, microsecond=0)
        for uid, ip, action_key, count, granularity in rl_specs:
            row = (
                db.query(RateLimitCounter)
                .filter(
                    RateLimitCounter.user_id == uid,
                    RateLimitCounter.ip_address == ip,
                    RateLimitCounter.action_key == action_key,
                    RateLimitCounter.time_bucket_start == bucket,
                )
                .first()
            )
            if row:
                row.count = count
                continue
            db.add(
                RateLimitCounter(
                    user_id=uid,
                    ip_address=ip,
                    action_key=action_key,
                    time_bucket_start=bucket,
                    count=count,
                    granularity=granularity,
                )
            )

        db.commit()

        # Summary counts
        models = {
            "users": User,
            "refresh_tokens": RefreshToken,
            "oauth_accounts": OAuthAccount,
            "classical_authors": ClassicalAuthor,
            "classical_works": ClassicalWork,
            "work_chapters": WorkChapter,
            "submissions": Submission,
            "moderation_guidelines": ModerationGuideline,
            "moderation_logs": ModerationLog,
            "doha_entries": DohaEntry,
            "content_versions": ContentVersion,
            "dictionary_entries": DictionaryEntry,
            "idiom_entries": IdiomEntry,
            "article_entries": ArticleEntry,
            "engagement_kpis": EngagementKPI,
            "user_interactions": UserInteraction,
            "share_logs": ShareLog,
            "reports": Report,
            "rate_limit_counters": RateLimitCounter,
            "system_settings": SystemSetting,
            "audit_logs": AuditLog,
        }
        return {name: db.query(model).count() for name, model in models.items()}
    finally:
        db.close()


def main() -> None:
    reconcile_schema()
    counts = seed_data()
    total = sum(counts.values())
    print("Schema reconciled and tables ensured.")
    print("Row counts by table:")
    for table, count in counts.items():
        print(f"- {table}: {count}")
    print(f"Total rows across seeded tables: {total}")


if __name__ == "__main__":
    main()
