import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.db.models import (
    ClassicalAuthor,
    ClassicalWork,
    DohaEntry,
    WorkChapter,
    DictionaryEntry,
    IdiomEntry,
    ArticleEntry,
)
from app.main import app


@pytest.fixture
def navigation_seed_data(db):
    suffix = uuid.uuid4().hex[:8]
    source_seed = uuid.uuid4().int % 1_000_000_000

    author = ClassicalAuthor(
        slug=f"nav-author-{suffix}",
        name="Navigation Author",
        language="awadhi",
    )
    db.add(author)
    db.commit()
    db.refresh(author)

    work = ClassicalWork(
        author_id=author.id,
        slug=f"nav-work-{suffix}",
        title="Navigation Work",
        work_type="poetry",
    )
    db.add(work)
    db.commit()
    db.refresh(work)

    sequential_chapter = WorkChapter(
        work_id=work.id,
        slug=f"nav-chapter-seq-{suffix}",
        title="Sequential Chapter",
        number=1,
    )
    gapped_chapter = WorkChapter(
        work_id=work.id,
        slug=f"nav-chapter-gap-{suffix}",
        title="Gapped Chapter",
        number=2,
    )
    db.add_all([sequential_chapter, gapped_chapter])
    db.commit()
    db.refresh(sequential_chapter)
    db.refresh(gapped_chapter)

    sequential_ids = {}
    for idx, num in enumerate([1, 2, 3, 4, 5], start=1):
        entry = DohaEntry(
            hierarchy_path=f"nav-author-{suffix}/nav-work-{suffix}/nav-chapter-seq-{suffix}/{num}",
            author_id=author.id,
            work_id=work.id,
            chapter_id=sequential_chapter.id,
            number_in_chapter=num,
            main_text=f"Sequential doha {num}",
            status="active",
            visibility="public",
            version=1,
            is_canonical=True,
            source_submission_id=source_seed + idx,
        )
        db.add(entry)
        db.flush()
        sequential_ids[num] = entry.id

    gapped_ids = {}
    for idx, num in enumerate([1, 2, 5], start=101):
        entry = DohaEntry(
            hierarchy_path=f"nav-author-{suffix}/nav-work-{suffix}/nav-chapter-gap-{suffix}/{num}",
            author_id=author.id,
            work_id=work.id,
            chapter_id=gapped_chapter.id,
            number_in_chapter=num,
            main_text=f"Gapped doha {num}",
            status="active",
            visibility="public",
            version=1,
            is_canonical=True,
            source_submission_id=source_seed + idx,
        )
        db.add(entry)
        db.flush()
        gapped_ids[num] = entry.id

    # This doha has number_in_chapter=3 in a different chapter and must not leak into navigation.
    other_chapter_entry = DohaEntry(
        hierarchy_path=f"nav-author-{suffix}/nav-work-{suffix}/nav-chapter-seq-{suffix}/99",
        author_id=author.id,
        work_id=work.id,
        chapter_id=gapped_chapter.id,
        number_in_chapter=99,
        main_text="Other chapter doha",
        status="active",
        visibility="public",
        version=1,
        is_canonical=True,
        source_submission_id=source_seed + 999,
    )
    db.add(other_chapter_entry)
    db.commit()

    return {
        "sequential": sequential_ids,
        "gapped": gapped_ids,
    }


async def _navigation_request(doha_id: int):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        return await ac.get(f"/content/doha/{doha_id}/navigation")


async def _typed_navigation_request(content_type: str, entry_id: int):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        return await ac.get(f"/content/{content_type}/{entry_id}/navigation")


@pytest.mark.asyncio
async def test_navigation_middle_node_has_previous_and_next(navigation_seed_data):
    middle_id = navigation_seed_data["sequential"][3]

    response = await _navigation_request(middle_id)
    assert response.status_code == 200

    payload = response.json()
    assert payload["current"]["id"] == middle_id
    assert payload["previous"]["id"] == navigation_seed_data["sequential"][2]
    assert payload["next"]["id"] == navigation_seed_data["sequential"][4]


@pytest.mark.asyncio
async def test_navigation_beginning_returns_null_previous(navigation_seed_data):
    first_id = navigation_seed_data["sequential"][1]

    response = await _navigation_request(first_id)
    assert response.status_code == 200

    payload = response.json()
    assert payload["previous"] is None
    assert payload["current"]["id"] == first_id
    assert payload["next"]["id"] == navigation_seed_data["sequential"][2]


@pytest.mark.asyncio
async def test_navigation_end_returns_null_next(navigation_seed_data):
    last_id = navigation_seed_data["sequential"][5]

    response = await _navigation_request(last_id)
    assert response.status_code == 200

    payload = response.json()
    assert payload["previous"]["id"] == navigation_seed_data["sequential"][4]
    assert payload["current"]["id"] == last_id
    assert payload["next"] is None


@pytest.mark.asyncio
async def test_navigation_sequence_gap_uses_ordered_neighbors(navigation_seed_data):
    second_in_gapped = navigation_seed_data["gapped"][2]

    response = await _navigation_request(second_in_gapped)
    assert response.status_code == 200

    payload = response.json()
    assert payload["previous"]["id"] == navigation_seed_data["gapped"][1]
    assert payload["next"]["id"] == navigation_seed_data["gapped"][5]


@pytest.mark.asyncio
async def test_navigation_nonexistent_doha_returns_404():
    response = await _navigation_request(999999999)
    assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "content_type,model,create_payload",
    [
        (
            "dictionary",
            DictionaryEntry,
            lambda chapter_id, n, sid: {
                "lemma_devanagari": f"शब्द {n}",
                "lemma_roman": f"shabd-{n}",
                "lemma_roman_norm": f"shabd-{n}",
                "language": "hi",
                "senses": [{"definition": f"sense {n}"}],
                "chapter_id": chapter_id,
                "number_in_chapter": n,
                "source_submission_id": sid,
                "visibility": "public",
                "version": 1,
            },
        ),
        (
            "idiom",
            IdiomEntry,
            lambda chapter_id, n, sid: {
                "text_devanagari": f"मुहावरा {n}",
                "text_roman": f"muhavra-{n}",
                "text_roman_norm": f"muhavra-{n}",
                "meaning": f"meaning {n}",
                "chapter_id": chapter_id,
                "number_in_chapter": n,
                "source_submission_id": sid,
                "visibility": "public",
                "version": 1,
            },
        ),
    ],
)
async def test_navigation_non_doha_content_types_within_chapter(db, content_type, model, create_payload):
    suffix = uuid.uuid4().hex[:8]
    seed = uuid.uuid4().int % 1_000_000_000

    author = ClassicalAuthor(slug=f"nav-typed-author-{suffix}", name="Nav Typed", language="awadhi")
    db.add(author)
    db.commit()
    db.refresh(author)

    work = ClassicalWork(
        author_id=author.id,
        slug=f"nav-typed-work-{suffix}",
        title="Nav Typed Work",
        work_type="poetry",
    )
    db.add(work)
    db.commit()
    db.refresh(work)

    chapter = WorkChapter(
        work_id=work.id,
        slug=f"ayodhya-kand-{suffix}",
        title="Ayodhya Kand",
        number=1,
    )
    db.add(chapter)
    db.commit()
    db.refresh(chapter)

    created_ids = {}
    for idx, num in enumerate([1, 2, 3], start=1):
        row = model(**create_payload(chapter.id, num, seed + idx))
        db.add(row)
        db.flush()
        created_ids[num] = row.id
    db.commit()

    response = await _typed_navigation_request(content_type, created_ids[2])
    assert response.status_code == 200
    payload = response.json()

    assert payload["previous"]["id"] == created_ids[1]
    assert payload["current"]["id"] == created_ids[2]
    assert payload["next"]["id"] == created_ids[3]


@pytest.mark.asyncio
async def test_navigation_article_returns_404_when_not_chapter_linked(db):
    entry = ArticleEntry(
        title="Standalone article",
        body="Article body",
        source_submission_id=int(uuid.uuid4().int % 1_000_000_000),
        visibility="public",
        version=1,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)

    response = await _typed_navigation_request("article", entry.id)
    assert response.status_code == 404
