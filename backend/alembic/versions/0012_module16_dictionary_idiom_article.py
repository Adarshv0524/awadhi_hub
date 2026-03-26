"""create dictionary, idiom, article tables

Revision ID: 0012_module16_dictionary_idiom_article
Revises: 0011_audit_logs
Create Date: 2025-12-12 00:00:00.000002
"""
from alembic import op
import sqlalchemy as sa

revision = "0012_module16_dictionary_idiom_article"
down_revision = "0011_audit_logs"
branch_labels = None
depends_on = None

def upgrade():
    # dictionary_entries
    op.create_table(
        "dictionary_entries",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("lemma_devanagari", sa.String(512), nullable=False),
        sa.Column("lemma_roman", sa.String(512), nullable=True),
        sa.Column("lemma_roman_norm", sa.String(512), nullable=True),
        sa.Column("language", sa.String(16), nullable=False, server_default="hi"),
        sa.Column("senses", sa.JSON(), nullable=False),
        sa.Column("pronunciation", sa.String(255), nullable=True),
        sa.Column("examples", sa.JSON(), nullable=True),
        sa.Column("contributor_id", sa.Integer(), nullable=True),
        sa.Column("author_id", sa.Integer(), nullable=True),
        sa.Column("work_id", sa.Integer(), nullable=True),
        sa.Column("chapter_id", sa.Integer(), nullable=True),
        sa.Column("number_in_chapter", sa.Integer(), nullable=True),
        sa.Column("source_submission_id", sa.Integer(), nullable=True, unique=True),
        sa.Column("visibility", sa.String(20), nullable=False, server_default="public"),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_dictionary_lemma_devanagari", "dictionary_entries", ["lemma_devanagari"])
    op.create_index("ix_dictionary_lemma_roman", "dictionary_entries", ["lemma_roman"])
    op.create_index("ix_dictionary_lemma_roman_norm", "dictionary_entries", ["lemma_roman_norm"])
    # MySQL FULLTEXT index
    try:
        op.create_index("ft_dictionary_lemma_fulltext", "dictionary_entries", ["lemma_devanagari", "lemma_roman"], mysql_prefix="FULLTEXT")
    except Exception:
        pass

    # idiom_entries
    op.create_table(
        "idiom_entries",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("text_devanagari", sa.Text(), nullable=False),
        sa.Column("text_roman", sa.Text(), nullable=True),
        sa.Column("text_roman_norm", sa.String(512), nullable=True),
        sa.Column("meaning", sa.Text(), nullable=True),
        sa.Column("examples", sa.JSON(), nullable=True),
        sa.Column("region", sa.String(64), nullable=True),
        sa.Column("contributor_id", sa.Integer(), nullable=True),
        sa.Column("author_id", sa.Integer(), nullable=True),
        sa.Column("work_id", sa.Integer(), nullable=True),
        sa.Column("chapter_id", sa.Integer(), nullable=True),
        sa.Column("number_in_chapter", sa.Integer(), nullable=True),
        sa.Column("source_submission_id", sa.Integer(), nullable=True, unique=True),
        sa.Column("visibility", sa.String(20), nullable=False, server_default="public"),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_idiom_text_roman_norm", "idiom_entries", ["text_roman_norm"])
    try:
        op.create_index("ft_idiom_text_fulltext", "idiom_entries", ["text_devanagari", "text_roman"], mysql_prefix="FULLTEXT")
    except Exception:
        pass

    # article_entries
    op.create_table(
        "article_entries",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("title", sa.String(512), nullable=False),
        sa.Column("title_devanagari", sa.String(512), nullable=True),
        sa.Column("title_roman", sa.String(512), nullable=True),
        sa.Column("title_roman_norm", sa.String(512), nullable=True),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("excerpt", sa.Text(), nullable=True),
        sa.Column("author_id", sa.Integer(), nullable=True),
        sa.Column("tags", sa.JSON(), nullable=True),
        sa.Column("contributor_id", sa.Integer(), nullable=True),
        sa.Column("source_submission_id", sa.Integer(), nullable=True, unique=True),
        sa.Column("visibility", sa.String(20), nullable=False, server_default="public"),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_article_title_roman_norm", "article_entries", ["title_roman_norm"])
    try:
        op.create_index("ft_article_title_body", "article_entries", ["title", "body"], mysql_prefix="FULLTEXT")
    except Exception:
        pass


def downgrade():
    op.drop_index("ft_article_title_body", table_name="article_entries")
    op.drop_index("ix_article_title_roman_norm", table_name="article_entries")
    op.drop_table("article_entries")

    op.drop_index("ft_idiom_text_fulltext", table_name="idiom_entries")
    op.drop_index("ix_idiom_text_roman_norm", table_name="idiom_entries")
    op.drop_table("idiom_entries")

    op.drop_index("ft_dictionary_lemma_fulltext", table_name="dictionary_entries")
    op.drop_index("ix_dictionary_lemma_roman_norm", table_name="dictionary_entries")
    op.drop_index("ix_dictionary_lemma_roman", table_name="dictionary_entries")
    op.drop_index("ix_dictionary_lemma_devanagari", table_name="dictionary_entries")
    op.drop_table("dictionary_entries")
