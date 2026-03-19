# alembic/versions/0007_doha_fulltext_index.py
"""add fulltext index on doha_entries for search

Revision ID: 0007_doha_fulltext_index
Revises: 0006_doha_content
Create Date: 2025-12-11 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0007_doha_fulltext_index"
down_revision = "0006_doha_content"
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    dialect_name = conn.engine.dialect.name

    # Only create FULLTEXT index if MySQL (other DBs will ignore or need different syntax).
    if dialect_name == "mysql":
        # ensure columns exist then create fulltext index
        op.create_index(
            "ft_doha_main_meaning_devanagari_romanized",
            "doha_entries",
            ["main_text", "meaning", "text_devanagari", "text_romanized"],
            mysql_prefix="FULLTEXT",
        )
    else:
        # For non-MySQL DBs, just add a normal index on main_text (helpful for LIKE)
        try:
            op.create_index("ix_doha_main_text", "doha_entries", ["main_text"])
        except Exception:
            # if index exists or unsupported, ignore quietly
            pass


def downgrade():
    conn = op.get_bind()
    dialect_name = conn.engine.dialect.name

    if dialect_name == "mysql":
        op.drop_index("ft_doha_main_meaning_devanagari_romanized", table_name="doha_entries")
    else:
        try:
            op.drop_index("ix_doha_main_text", table_name="doha_entries")
        except Exception:
            pass
