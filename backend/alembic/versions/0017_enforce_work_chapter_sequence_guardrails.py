"""enforce contiguous chapter numbering guardrails

Revision ID: 0017_enforce_work_chapter_sequence_guardrails
Revises: 0016_poetry_nodes_foundation
Create Date: 2026-03-28 00:00:00.000000
"""

from alembic import op


revision = "0017_enforce_work_chapter_sequence_guardrails"
down_revision = "0016_poetry_nodes_foundation"
branch_labels = None
depends_on = None


def _create_sqlite_triggers() -> None:
    op.execute(
        """
        CREATE TRIGGER IF NOT EXISTS trg_work_chapters_contiguous_insert
        BEFORE INSERT ON work_chapters
        FOR EACH ROW
        WHEN NEW.is_deleted = 0
        BEGIN
            SELECT RAISE(ABORT, 'Chapter number must be contiguous and append-only')
            WHERE NEW.number <> (
                SELECT COALESCE(MAX(number), 0) + 1
                FROM work_chapters
                WHERE work_id = NEW.work_id AND is_deleted = 0
            );
        END
        """
    )
    op.execute(
        """
        CREATE TRIGGER IF NOT EXISTS trg_work_chapters_no_renumber
        BEFORE UPDATE OF number, work_id ON work_chapters
        FOR EACH ROW
        WHEN OLD.is_deleted = 0 AND NEW.is_deleted = 0
        BEGIN
            SELECT RAISE(ABORT, 'Renumbering or moving active chapters is not allowed');
        END
        """
    )


def _create_mysql_triggers() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_work_chapters_contiguous_insert")
    op.execute(
        """
        CREATE TRIGGER trg_work_chapters_contiguous_insert
        BEFORE INSERT ON work_chapters
        FOR EACH ROW
        BEGIN
            DECLARE expected_num INT;
            IF NEW.is_deleted = 0 THEN
                SELECT COALESCE(MAX(number), 0) + 1
                INTO expected_num
                FROM work_chapters
                WHERE work_id = NEW.work_id AND is_deleted = 0;
                IF NEW.number <> expected_num THEN
                    SIGNAL SQLSTATE '45000'
                    SET MESSAGE_TEXT = 'Chapter number must be contiguous and append-only';
                END IF;
            END IF;
        END
        """
    )

    op.execute("DROP TRIGGER IF EXISTS trg_work_chapters_no_renumber")
    op.execute(
        """
        CREATE TRIGGER trg_work_chapters_no_renumber
        BEFORE UPDATE ON work_chapters
        FOR EACH ROW
        BEGIN
            IF OLD.is_deleted = 0 AND NEW.is_deleted = 0 THEN
                IF NEW.number <> OLD.number OR NEW.work_id <> OLD.work_id THEN
                    SIGNAL SQLSTATE '45000'
                    SET MESSAGE_TEXT = 'Renumbering or moving active chapters is not allowed';
                END IF;
            END IF;
        END
        """
    )


def upgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name

    if dialect == "sqlite":
        _create_sqlite_triggers()
        return

    if dialect == "mysql":
        _create_mysql_triggers()


def downgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name

    if dialect == "sqlite":
        op.execute("DROP TRIGGER IF EXISTS trg_work_chapters_contiguous_insert")
        op.execute("DROP TRIGGER IF EXISTS trg_work_chapters_no_renumber")
        return

    if dialect == "mysql":
        op.execute("DROP TRIGGER IF EXISTS trg_work_chapters_contiguous_insert")
        op.execute("DROP TRIGGER IF EXISTS trg_work_chapters_no_renumber")
