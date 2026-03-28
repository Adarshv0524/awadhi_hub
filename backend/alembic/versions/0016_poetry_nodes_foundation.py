"""create poetry nodes foundation and backfill doha

Revision ID: 0016_poetry_nodes_foundation
Revises: 0015_add_doha_chapter_sequence_index
Create Date: 2026-03-28 00:00:00.000000
"""

from collections import defaultdict

from alembic import op
import sqlalchemy as sa


revision = "0016_poetry_nodes_foundation"
down_revision = "0015_add_doha_chapter_sequence_index"
branch_labels = None
depends_on = None


def _canonical_doha_rows(bind, doha_entries):
    stmt = (
        sa.select(doha_entries)
        .where(doha_entries.c.is_canonical == sa.true())
        .where(doha_entries.c.is_deleted == sa.false())
    )
    return bind.execute(stmt).mappings().all()


def _build_poetry_backfill_rows(doha_rows):
    chapter_buckets = defaultdict(list)
    for row in doha_rows:
        chapter_buckets[row["chapter_id"]].append(row)

    payload = []
    skipped = 0

    for chapter_id, rows in chapter_buckets.items():
        if chapter_id is None:
            skipped += len(rows)
            continue

        sorted_rows = sorted(
            rows,
            key=lambda r: (
                r["number_in_chapter"] if (r["number_in_chapter"] is not None and r["number_in_chapter"] > 0) else 10**9,
                r["id"],
            ),
        )

        for sequence_no, row in enumerate(sorted_rows, start=1):
            if row["author_id"] is None or row["work_id"] is None:
                skipped += 1
                continue

            payload.append(
                {
                    "author_id": row["author_id"],
                    "work_id": row["work_id"],
                    "chapter_id": row["chapter_id"],
                    "poetry_type": "doha",
                    "sequence_no": sequence_no,
                    "main_text": row["main_text"],
                    "text_devanagari": row["text_devanagari"],
                    "text_romanized": row["text_romanized"],
                    "meaning": row["meaning"],
                    "prosody_metadata": None,
                    "status": row["status"] or "active",
                    "visibility": row["visibility"] or "public",
                    "source_submission_id": row["source_submission_id"],
                    "created_by": row["created_by"],
                    "verified_by": row["verified_by"],
                    "verified_at": row["verified_at"],
                    "version": row["version"] or 1,
                    "is_deleted": row["is_deleted"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                }
            )

    return payload, skipped


def data_upgrades():
    bind = op.get_bind()
    meta = sa.MetaData()

    doha_entries = sa.Table("doha_entries", meta, autoload_with=bind)
    poetry_nodes = sa.Table("poetry_nodes", meta, autoload_with=bind)
    poetry_type_registry = sa.Table("poetry_type_registry", meta, autoload_with=bind)

    doha_rows = _canonical_doha_rows(bind, doha_entries)
    payload, skipped = _build_poetry_backfill_rows(doha_rows)

    if skipped:
        raise RuntimeError(
            f"Cannot complete poetry_nodes backfill: skipped {skipped} canonical doha rows due to missing hierarchy fields."
        )

    if payload:
        bind.execute(sa.insert(poetry_nodes), payload)

    inserted_count = bind.execute(
        sa.select(sa.func.count()).select_from(poetry_nodes).where(poetry_nodes.c.poetry_type == "doha")
    ).scalar_one()
    expected_count = len(doha_rows)
    if inserted_count != expected_count:
        raise RuntimeError(
            f"Poetry backfill count mismatch: expected {expected_count}, inserted {inserted_count}."
        )

    bind.execute(
        sa.insert(poetry_type_registry),
        [
            {"poetry_type": "doha", "display_name": "Doha", "family": "classical", "is_user_defined": False, "is_active": True},
            {"poetry_type": "chaupai", "display_name": "Chaupai", "family": "classical", "is_user_defined": False, "is_active": True},
            {"poetry_type": "jhulana", "display_name": "Jhulana", "family": "classical", "is_user_defined": False, "is_active": True},
            {"poetry_type": "sorath", "display_name": "Sorath", "family": "classical", "is_user_defined": False, "is_active": True},
            {"poetry_type": "savaiya", "display_name": "Savaiya", "family": "classical", "is_user_defined": False, "is_active": True},
            {"poetry_type": "ghanakshari", "display_name": "Ghanakshari", "family": "classical", "is_user_defined": False, "is_active": True},
            {"poetry_type": "chappay", "display_name": "Chappay", "family": "classical", "is_user_defined": False, "is_active": True},
            {"poetry_type": "other_poetry", "display_name": "Other Poetry", "family": "user_defined", "is_user_defined": True, "is_active": True},
        ],
    )


def upgrade():
    op.create_table(
        "poetry_nodes",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("author_id", sa.Integer(), sa.ForeignKey("classical_authors.id"), nullable=False),
        sa.Column("work_id", sa.Integer(), sa.ForeignKey("classical_works.id"), nullable=False),
        sa.Column("chapter_id", sa.Integer(), sa.ForeignKey("work_chapters.id"), nullable=False),
        sa.Column("poetry_type", sa.String(length=50), nullable=False),
        sa.Column("sequence_no", sa.Integer(), nullable=False),
        sa.Column("main_text", sa.Text(), nullable=False),
        sa.Column("text_devanagari", sa.Text(), nullable=True),
        sa.Column("text_romanized", sa.Text(), nullable=True),
        sa.Column("meaning", sa.Text(), nullable=True),
        sa.Column("prosody_metadata", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
        sa.Column("visibility", sa.String(length=20), nullable=False, server_default="public"),
        sa.Column("source_submission_id", sa.Integer(), sa.ForeignKey("submissions.id"), nullable=True),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("verified_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("chapter_id", "sequence_no", name="uq_poetry_nodes_chapter_sequence"),
        sa.UniqueConstraint("source_submission_id", name="uq_poetry_nodes_source_submission"),
    )
    op.create_index("ix_poetry_nodes_chapter_sequence", "poetry_nodes", ["chapter_id", "sequence_no"])
    op.create_index("ix_poetry_nodes_work_chapter", "poetry_nodes", ["work_id", "chapter_id"])
    op.create_index("ix_poetry_nodes_poetry_type", "poetry_nodes", ["poetry_type"])

    op.create_table(
        "poetry_type_registry",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("poetry_type", sa.String(length=50), nullable=False, unique=True),
        sa.Column("display_name", sa.String(length=120), nullable=False),
        sa.Column("family", sa.String(length=60), nullable=True),
        sa.Column("validation_schema", sa.JSON(), nullable=True),
        sa.Column("default_renderer", sa.String(length=120), nullable=True),
        sa.Column("is_user_defined", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    data_upgrades()


def downgrade():
    op.drop_table("poetry_type_registry")

    op.drop_index("ix_poetry_nodes_poetry_type", table_name="poetry_nodes")
    op.drop_index("ix_poetry_nodes_work_chapter", table_name="poetry_nodes")
    op.drop_index("ix_poetry_nodes_chapter_sequence", table_name="poetry_nodes")
    op.drop_table("poetry_nodes")
