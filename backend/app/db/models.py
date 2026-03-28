# app/db/models.py
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    JSON,
    Text,
    func,
    UniqueConstraint,
    ForeignKey,
    Float,
    Index
)
from sqlalchemy.orm import declarative_base, relationship, foreign
Base = declarative_base()
# ============================================
#           Module 1: User Management
# ============================================
class User(Base):
    """User account table for authentication and authorization."""
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)
    role = Column(String(50), default="registered", nullable=False)
    permissions = Column(Integer, default=0, nullable=False)
    permission_scopes = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_banned = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)

class RefreshToken(Base):
    """JWT refresh tokens for session management."""
    __tablename__ = "refresh_tokens"
    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(String(512), unique=True, nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
class OAuthAccount(Base):
    """OAuth provider accounts linked to users (Google, etc.)."""
    __tablename__ = "oauth_accounts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    provider = Column(String(50), nullable=False)
    provider_user_id = Column(String(255), nullable=False)
    user_id = Column(Integer, nullable=False, index=True)
    raw_profile = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    __table_args__ = (
        UniqueConstraint("provider", "provider_user_id", name="uq_provider_user"),
    )
# ============================================
#       Module 3: Classical Hierarchy
# ============================================
class ClassicalAuthor(Base):
    """Classical authors (poets, writers) for literary works."""
    __tablename__ = "classical_authors"
    id = Column(Integer, primary_key=True, autoincrement=True)
    slug = Column(String(150), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False)
    short_bio = Column(Text, nullable=True)
    long_bio = Column(Text, nullable=True)
    language = Column(String(50), nullable=True)
    is_deleted = Column(Boolean, nullable=False, server_default="0")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    works = relationship("ClassicalWork", back_populates="author")
class ClassicalWork(Base):
    """Classical literary works (books, poetry collections)."""
    __tablename__ = "classical_works"
    id = Column(Integer, primary_key=True, autoincrement=True)
    author_id = Column(Integer, ForeignKey("classical_authors.id"), nullable=False, index=True)
    slug = Column(String(150), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    work_type = Column(String(50), nullable=True)
    original_script = Column(String(50), nullable=True)
    is_deleted = Column(Boolean, nullable=False, server_default="0")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    author = relationship("ClassicalAuthor", back_populates="works")
    chapters = relationship("WorkChapter", back_populates="work")
    __table_args__ = (
        UniqueConstraint("author_id", "slug", name="uq_works_author_slug"),
    )
class WorkChapter(Base):
    """Chapters within classical works."""
    __tablename__ = "work_chapters"
    id = Column(Integer, primary_key=True, autoincrement=True)
    work_id = Column(Integer, ForeignKey("classical_works.id"), nullable=False, index=True)
    slug = Column(String(150), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    number = Column(Integer, nullable=False)
    is_deleted = Column(Boolean, nullable=False, server_default="0")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    work = relationship("ClassicalWork", back_populates="chapters")
    __table_args__ = (
        UniqueConstraint("work_id", "slug", name="uq_chapters_work_slug"),
        UniqueConstraint("work_id", "number", name="uq_chapters_work_number"),
    )
# ============================================
#       Module 4: Submission & Moderation
# ============================================
class Submission(Base):
    """User-submitted content awaiting moderation."""
    __tablename__ = "submissions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    content_type = Column(String(50), nullable=False)  # "doha", "dictionary", "idiom", "article"
    main_text = Column(Text, nullable=False)
    meaning = Column(Text, nullable=True)
    is_classical = Column(Boolean, nullable=False, server_default="0")
    author_slug = Column(String(150), nullable=True)
    work_slug = Column(String(150), nullable=True)
    chapter_slug = Column(String(150), nullable=True)
    number_in_chapter = Column(Integer, nullable=True)
    external_references = Column(JSON, nullable=True)
    status = Column(String(20), nullable=False, server_default="draft")
    visibility = Column(String(20), nullable=False, server_default="private")
    version = Column(Integer, nullable=False, server_default="1")
    contributor_id = Column(Integer, nullable=False, index=True)
    assigned_moderator_id = Column(Integer, nullable=True, index=True)
    priority = Column(Integer, nullable=False, server_default="0")
    is_deleted = Column(Boolean, nullable=False, server_default="0")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
class ModerationGuideline(Base):
    """Versioned moderation guidelines for content approval."""
    __tablename__ = "moderation_guidelines"
    id = Column(Integer, primary_key=True, autoincrement=True)
    version = Column(String(50), nullable=False, unique=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    url = Column(String(500), nullable=True)
    is_active = Column(Boolean, nullable=False, server_default="0")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
class ModerationLog(Base):
    """Audit log for moderation actions."""
    __tablename__ = "moderation_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    submission_id = Column(Integer, nullable=False, index=True)
    moderator_id = Column(Integer, nullable=False, index=True)
    action = Column(String(50), nullable=False)
    from_status = Column(String(20), nullable=True)
    to_status = Column(String(20), nullable=True)
    guideline_version = Column(String(50), nullable=True)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
# ============================================
#       Module 6: Canonical Content
# ============================================
class DohaEntry(Base):
    """Canonical doha (couplet) entries."""
    __tablename__ = "doha_entries"
    id = Column(Integer, primary_key=True, autoincrement=True)
    hierarchy_path = Column(String(512), nullable=True, index=True)
    author_id = Column(Integer, nullable=True, index=True)
    work_id = Column(Integer, nullable=True, index=True)
    chapter_id = Column(Integer, nullable=True, index=True)
    number_in_chapter = Column(Integer, nullable=True)
    main_text = Column(Text, nullable=False)
    meaning = Column(Text, nullable=True)
    text_devanagari = Column(Text, nullable=True)
    text_romanized = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, server_default="active")
    visibility = Column(String(20), nullable=False, server_default="public")
    version = Column(Integer, nullable=False, server_default="1")
    is_canonical = Column(Boolean, nullable=False, server_default="1")
    variant_group_id = Column(Integer, nullable=True)
    confidence_level = Column(Integer, nullable=True)
    source_reference = Column(JSON, nullable=True)
    source_submission_id = Column(Integer, nullable=True, unique=True)
    created_by = Column(Integer, nullable=True)
    verified_by = Column(Integer, nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    is_deleted = Column(Boolean, nullable=False, server_default="0")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    engagement_kpi = relationship(
        "EngagementKPI",
        primaryjoin="and_(EngagementKPI.content_type=='doha', foreign(EngagementKPI.content_id)==DohaEntry.id)",
        uselist=False,
        viewonly=True,
    )


class PoetryNode(Base):
    """Canonical chapter-sequenced poetry nodes across mixed poetry types."""

    __tablename__ = "poetry_nodes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    author_id = Column(Integer, ForeignKey("classical_authors.id"), nullable=False)
    work_id = Column(Integer, ForeignKey("classical_works.id"), nullable=False)
    chapter_id = Column(Integer, ForeignKey("work_chapters.id"), nullable=False)

    poetry_type = Column(String(50), nullable=False)
    sequence_no = Column(Integer, nullable=False)

    main_text = Column(Text, nullable=False)
    text_devanagari = Column(Text, nullable=True)
    text_romanized = Column(Text, nullable=True)
    meaning = Column(Text, nullable=True)

    prosody_metadata = Column(JSON, nullable=True)
    status = Column(String(20), nullable=False, server_default="active")
    visibility = Column(String(20), nullable=False, server_default="public")

    source_submission_id = Column(Integer, ForeignKey("submissions.id"), nullable=True, unique=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    verified_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)

    version = Column(Integer, nullable=False, server_default="1")
    is_deleted = Column(Boolean, nullable=False, server_default="0")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("chapter_id", "sequence_no", name="uq_poetry_nodes_chapter_sequence"),
        Index("ix_poetry_nodes_chapter_sequence", "chapter_id", "sequence_no"),
        Index("ix_poetry_nodes_work_chapter", "work_id", "chapter_id"),
        Index("ix_poetry_nodes_poetry_type", "poetry_type"),
    )

    author = relationship("ClassicalAuthor")
    work = relationship("ClassicalWork")
    chapter = relationship("WorkChapter")


class PoetryTypeRegistry(Base):
    """Optional registry for supported poetry types and renderer metadata."""

    __tablename__ = "poetry_type_registry"

    id = Column(Integer, primary_key=True, autoincrement=True)
    poetry_type = Column(String(50), nullable=False, unique=True)
    display_name = Column(String(120), nullable=False)
    family = Column(String(60), nullable=True)
    validation_schema = Column(JSON, nullable=True)
    default_renderer = Column(String(120), nullable=True)
    is_user_defined = Column(Boolean, nullable=False, server_default="0")
    is_active = Column(Boolean, nullable=False, server_default="1")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

class ContentVersion(Base):
    """Version history for canonical content."""
    __tablename__ = "content_versions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    content_type = Column(String(50), nullable=False)
    content_id = Column(Integer, nullable=False)
    version_number = Column(Integer, nullable=False)
    main_text = Column(Text, nullable=True)
    meaning = Column(Text, nullable=True)
    text_devanagari = Column(Text, nullable=True)
    text_romanized = Column(Text, nullable=True)
    created_by = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    notes = Column(Text, nullable=True)
class DictionaryEntry(Base):
    """Canonical dictionary entries (words/lemmas with definitions)."""
    __tablename__ = "dictionary_entries"
    id = Column(Integer, primary_key=True, autoincrement=True)
    lemma_devanagari = Column(String(512), nullable=False, index=True)
    lemma_roman = Column(String(512), nullable=True, index=True)
    lemma_roman_norm = Column(String(512), nullable=True, index=True)
    language = Column(String(16), nullable=False, server_default="hi")
    senses = Column(JSON, nullable=False)
    pronunciation = Column(String(255), nullable=True)
    examples = Column(JSON, nullable=True)
    contributor_id = Column(Integer, nullable=True, index=True)
    author_id = Column(Integer, nullable=True, index=True)
    work_id = Column(Integer, nullable=True, index=True)
    chapter_id = Column(Integer, nullable=True, index=True)
    number_in_chapter = Column(Integer, nullable=True)
    source_submission_id = Column(Integer, nullable=True, unique=True)
    visibility = Column(String(20), nullable=False, server_default="public")
    version = Column(Integer, nullable=False, server_default="1")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    __table_args__ = (
        Index("ix_dictionary_lemma_devanagari", "lemma_devanagari"),
        Index("ix_dictionary_lemma_roman", "lemma_roman"),
        Index("ix_dictionary_lemma_roman_norm", "lemma_roman_norm"),
    )
class IdiomEntry(Base):
    """Canonical idiom/phrase entries."""
    __tablename__ = "idiom_entries"
    id = Column(Integer, primary_key=True, autoincrement=True)
    text_devanagari = Column(Text, nullable=False, index=True)
    text_roman = Column(Text, nullable=True)
    text_roman_norm = Column(String(512), nullable=True, index=True)
    meaning = Column(Text, nullable=True)
    examples = Column(JSON, nullable=True)
    region = Column(String(64), nullable=True)
    contributor_id = Column(Integer, nullable=True, index=True)
    author_id = Column(Integer, nullable=True, index=True)
    work_id = Column(Integer, nullable=True, index=True)
    chapter_id = Column(Integer, nullable=True, index=True)
    number_in_chapter = Column(Integer, nullable=True)
    source_submission_id = Column(Integer, nullable=True, unique=True)
    visibility = Column(String(20), nullable=False, server_default="public")
    version = Column(Integer, nullable=False, server_default="1")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    __table_args__ = (
        Index("ix_idiom_text_roman_norm", "text_roman_norm"),
    )
class ArticleEntry(Base):
    """Canonical article/essay entries."""
    __tablename__ = "article_entries"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(512), nullable=False, index=True)
    title_devanagari = Column(String(512), nullable=True)
    title_roman = Column(String(512), nullable=True)
    title_roman_norm = Column(String(512), nullable=True, index=True)
    body = Column(Text, nullable=False)
    excerpt = Column(Text, nullable=True)
    author_id = Column(Integer, nullable=True, index=True)  # References User (contributor)
    tags = Column(JSON, nullable=True)
    contributor_id = Column(Integer, nullable=True, index=True)
    source_submission_id = Column(Integer, nullable=True, unique=True)
    visibility = Column(String(20), nullable=False, server_default="public")
    version = Column(Integer, nullable=False, server_default="1")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    __table_args__ = (
        Index("ix_article_title_roman_norm", "title_roman_norm"),
    )
# ============================================
#       Module 8: Engagement Tracking
# ============================================
class EngagementKPI(Base):
    """Engagement metrics for content (views, likes, shares, bookmarks)."""
    __tablename__ = "engagement_kpis"
    id = Column(Integer, primary_key=True, autoincrement=True)
    content_type = Column(String(50), nullable=False, index=True)
    content_id = Column(Integer, nullable=False, index=True)
    views_count = Column(Integer, nullable=False, default=0)
    search_hits_count = Column(Integer, nullable=False, default=0)
    likes_count = Column(Integer, nullable=False, default=0)
    shares_count = Column(Integer, nullable=False, default=0)
    bookmarks_count = Column(Integer, nullable=False, default=0)  # NEW
    weight_score = Column(Float, nullable=False, default=0.0)
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    __table_args__ = (
        UniqueConstraint("content_type", "content_id", name="uq_engagement_content"),
    )

class UserInteraction(Base):
    """User interactions (likes/bookmarks) with content."""
    __tablename__ = "user_interactions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    content_type = Column(String(50), nullable=False, index=True)  # e.g., "doha","dictionary","article","idiom"
    content_id = Column(Integer, nullable=False, index=True)
    interaction_type = Column(String(50), nullable=False)  # 'like' | 'bookmark'
    is_active = Column(Boolean, nullable=False, server_default="1")  # toggle on/off (soft delete)
    interaction_metadata = Column(JSON, nullable=True)  # ip_address, user_agent, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    __table_args__ = (
        UniqueConstraint("user_id", "content_type", "content_id", "interaction_type", name="uq_user_interaction"),
        Index("ix_user_interaction_user_content", "user_id", "content_type", "content_id"),
    )

class ShareLog(Base):
    """Append-only log of content shares."""
    __tablename__ = "share_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    content_type = Column(String(50), nullable=False, index=True)
    content_id = Column(Integer, nullable=False, index=True)
    share_metadata = Column(JSON, nullable=True)  # e.g., { "channel": "whatsapp", "referrer": "...", "ip_address": "..."}
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    __table_args__ = (
        Index("ix_share_logs_content", "content_type", "content_id"),
    )


class ReputationLevel(Base):
    """Level definitions for contributor reputation progression."""

    __tablename__ = "reputation_levels"

    id = Column(Integer, primary_key=True, autoincrement=True)
    slug = Column(String(64), nullable=False, unique=True, index=True)
    name = Column(String(120), nullable=False)
    min_points = Column(Integer, nullable=False, server_default="0")
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class BadgeDefinition(Base):
    """Badge catalog and unlock criteria metadata."""

    __tablename__ = "badge_definitions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    slug = Column(String(64), nullable=False, unique=True, index=True)
    name = Column(String(120), nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String(120), nullable=True)
    criteria = Column(JSON, nullable=True)
    is_active = Column(Boolean, nullable=False, server_default="1")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class UserReputation(Base):
    """Aggregate user reputation counters and current level."""

    __tablename__ = "user_reputation"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    points = Column(Integer, nullable=False, server_default="0")
    approved_submissions = Column(Integer, nullable=False, server_default="0")
    likes_received = Column(Integer, nullable=False, server_default="0")
    current_level_id = Column(Integer, ForeignKey("reputation_levels.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User")
    current_level = relationship("ReputationLevel")


class UserBadge(Base):
    """User-to-badge mapping for earned achievements."""

    __tablename__ = "user_badges"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    badge_definition_id = Column(Integer, ForeignKey("badge_definitions.id"), nullable=False, index=True)
    earned_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    badge_metadata = Column(JSON, nullable=True)

    user = relationship("User")
    badge = relationship("BadgeDefinition")

    __table_args__ = (
        UniqueConstraint("user_id", "badge_definition_id", name="uq_user_badges_user_badge"),
    )

class Report(Base):
    """User reports/flags for content."""
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    content_type = Column(String(50), nullable=False, index=True)
    content_id = Column(Integer, nullable=False, index=True)
    reason = Column(String(64), nullable=False)  # spam | abuse | copyright | other
    note = Column(Text, nullable=True)
    report_metadata = Column(JSON, nullable=True)  # ip, ua, request_id...
    status = Column(String(20), nullable=False, server_default="open")  # open/resolved/rejected
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    __table_args__ = (
        Index("ix_reports_content", "content_type", "content_id"),
    )

# ============================================
#       Module 9: Rate Limiting
# ============================================
class RateLimitCounter(Base):
    """Rate limiting counters for API endpoints."""
    __tablename__ = "rate_limit_counters"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=True, index=True)
    ip_address = Column(String(45), nullable=True)
    action_key = Column(String(128), nullable=False)
    time_bucket_start = Column(DateTime(timezone=True), nullable=False)
    count = Column(Integer, nullable=False, server_default="0")
    granularity = Column(Integer, nullable=False, server_default="60")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    __table_args__ = (
        UniqueConstraint("user_id", "ip_address", "action_key", "time_bucket_start", name="uq_rate_limit_bucket"),
        Index("ix_rl_action_bucket", "action_key", "time_bucket_start"),
    )
# ============================================
#       Module 10: System Settings
# ============================================
class SystemSetting(Base):
    """System-wide configuration settings."""
    __tablename__ = "system_settings"
    setting_key = Column(String(255), primary_key=True, nullable=False)
    value = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
# ============================================
#       Module 11: Audit Logging
# ============================================
class AuditLog(Base):
    """System-wide audit log for all user actions."""
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    actor_user_id = Column(Integer, nullable=True, index=True)
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(50), nullable=True, index=True)
    resource_id = Column(Integer, nullable=True, index=True)
    audit_before = Column("before", JSON, nullable=True)
    after = Column(JSON, nullable=True)
    audit_metadata = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    __table_args__ = (
        Index("ix_audit_created_at", "created_at"),
        Index("ix_audit_resourcetype_id", "resource_type", "resource_id"),
    )