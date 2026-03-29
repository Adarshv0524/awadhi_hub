from __future__ import annotations

from pathlib import Path


FRONTEND_ADMIN_WRAPPER = (
    Path(__file__).resolve().parents[2] / "frontend" / "src" / "lib" / "admin.ts"
)


def test_create_chapter_wrapper_uses_number_field_not_order_num() -> None:
    source = FRONTEND_ADMIN_WRAPPER.read_text(encoding="utf-8")

    # Signature contract: createChapter input payload uses `number`.
    assert "createChapter(workId: number, data: { slug: string; title: string; number: number })" in source

    # Body contract: wrapper must not serialize legacy `order_num`.
    assert "order_num" not in source
