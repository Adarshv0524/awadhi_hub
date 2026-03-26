"""
E2E (End-to-End) tests for the Awadhi Hub Author → Work → Chapter → Doha → Navigation flow.

These tests verify that users can navigate through the classical hierarchy
and access verse navigation without errors.

Core Happy Path Journey:
1. Retrieve dohas from chapter endpoint
2. Call Navigation API for first doha - verify next matches second doha
3. Call Navigation API for middle doha - verify prev/next work
4. Call Navigation API for last doha - verify no next
5. Test with gapped sequences (e.g., verses 1,2,5) - PRIMARY FIX VERIFICATION

Requirements (from ISSUE-009):
- Slug normalization: All slugs (author, work, chapter) are normalized
- Strict ordering: If number_in_chapter is missing/duplicated, fallback to created_at or id
- Navigation must handle gapped sequences correctly (core bug fix)
"""

import uuid
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.db.models import ClassicalAuthor, ClassicalWork, WorkChapter, DohaEntry
from app.main import app
from app.utils.slug_normalizer import normalize_slug


async def _make_request(path: str):
    """Helper to make async requests to the test app."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        return await ac.get(path)


@pytest.fixture
def e2e_hierarchy(db: Session):
    """
    Create a test hierarchy for the E2E journey.
    
    Structure:
    - Author: "Tulsidas-{uuid}" (slug: "tulsidas-{uuid}")
      - Work: "Ramayana-{uuid}" (slug: "ramayana-{uuid}")
        - Chapter: "chapter-1-{uuid}"
          - Doha 1 (number_in_chapter: 1)
          - Doha 2 (number_in_chapter: 2)
          - Doha 3 (number_in_chapter: 3)
    """
    # Use unique suffix for each test instance
    suffix = uuid.uuid4().hex[:8]
    
    # Create author
    author = ClassicalAuthor(
        slug=f"tulsidas-{suffix}",
        name=f"Tulsidas {suffix}",
        short_bio="Great poet",
        is_deleted=False,
    )
    db.add(author)
    db.flush()

    # Create work
    work = ClassicalWork(
        author_id=author.id,
        slug=f"ramayana-{suffix}",
        title=f"Ramayana {suffix}",
        description="Epic poem",
        work_type="poetry",
        is_deleted=False,
    )
    db.add(work)
    db.flush()

    # Create chapter
    chapter = WorkChapter(
        work_id=work.id,
        slug=f"chapter-1-{suffix}",
        title=f"Chapter 1 {suffix}",
        number=1,
        is_deleted=False,
    )
    db.add(chapter)
    db.flush()

    # Create dohas with explicit numbering (sequential to ensure navigation works)
    doha1 = DohaEntry(
        chapter_id=chapter.id,
        number_in_chapter=1,
        main_text="Doha One",
        meaning="First verse",
        status="active",
        is_deleted=False,
        created_at=datetime.now(timezone.utc),
    )
    doha2 = DohaEntry(
        chapter_id=chapter.id,
        number_in_chapter=2,
        main_text="Doha Two",
        meaning="Second verse",
        status="active",
        is_deleted=False,
        created_at=datetime.now(timezone.utc),
    )
    doha3 = DohaEntry(
        chapter_id=chapter.id,
        number_in_chapter=3,
        main_text="Doha Three",
        meaning="Third verse",
        status="active",
        is_deleted=False,
        created_at=datetime.now(timezone.utc),
    )
    db.add_all([doha1, doha2, doha3])
    db.commit()

    return {
        "author": author,
        "work": work,
        "chapter": chapter,
        "dohas": [doha1, doha2, doha3],
    }


@pytest.mark.asyncio
async def test_e2e_retrieve_dohas_from_chapter(e2e_hierarchy):
    """
    STEP 1: Retrieve dohas from chapter.
    
    AP: GET /content/chapters/{chapter_id}/dohas should return paginated list.
    """
    chapter = e2e_hierarchy["chapter"]
    dohas = e2e_hierarchy["dohas"]
    
    response = await _make_request(f"/content/chapters/{chapter.id}/dohas?offset=0&limit=10")
    assert response.status_code == 200
    data = response.json()
    
    items = data.get("items", [])
    assert len(items) >= 1, "Chapter should have at least one doha"
    
    first_doha = items[0]
    assert first_doha["id"] == dohas[0].id
    assert first_doha["number_in_chapter"] == 1
    assert first_doha["main_text"] == "Doha One"


@pytest.mark.asyncio
async def test_e2e_navigation_first_doha_has_next(e2e_hierarchy):
    """
    STEP 2: Navigation for first doha confirms NEXT points to second doha.
    
    ✅ Core E2E verification: first doha → next doha link works.
    """
    dohas = e2e_hierarchy["dohas"]
    first_doha_id = dohas[0].id
    second_doha_id = dohas[1].id
    
    response = await _make_request(f"/content/doha/{first_doha_id}/navigation")
    assert response.status_code == 200
    nav_data = response.json()
    
    # Verify structure
    assert "previous" in nav_data
    assert "current" in nav_data
    assert "next" in nav_data
    
    # First doha should have no previous
    assert nav_data["previous"] is None, "First doha should have no previous verse"
    
    # First doha should have correct current
    assert nav_data["current"]["id"] == first_doha_id
    assert nav_data["current"]["number_in_chapter"] == 1
    
    # **KEY ASSERTION**: First doha's next must be second doha
    assert nav_data["next"] is not None, "First doha should have a next verse"
    assert nav_data["next"]["id"] == second_doha_id, f"Next ID should match second doha (expected {second_doha_id}, got {nav_data['next']['id']})"
    assert nav_data["next"]["number_in_chapter"] == 2


@pytest.mark.asyncio
async def test_e2e_navigation_middle_doha_has_both(e2e_hierarchy):
    """
    STEP 3: Navigation for middle doha returns both previous and next.
    """
    dohas = e2e_hierarchy["dohas"]
    second_doha_id = dohas[1].id
    first_doha_id = dohas[0].id
    third_doha_id = dohas[2].id
    
    response = await _make_request(f"/content/doha/{second_doha_id}/navigation")
    assert response.status_code == 200
    nav_data = response.json()
    
    assert nav_data["previous"] is not None, "Middle doha should have previous"
    assert nav_data["previous"]["id"] == first_doha_id
    
    assert nav_data["current"]["id"] == second_doha_id
    assert nav_data["current"]["number_in_chapter"] == 2
    
    assert nav_data["next"] is not None, "Middle doha should have next"
    assert nav_data["next"]["id"] == third_doha_id


@pytest.mark.asyncio
async def test_e2e_navigation_last_doha_no_next(e2e_hierarchy):
    """
    STEP 4: Navigation for last doha has previous but no next.
    """
    dohas = e2e_hierarchy["dohas"]
    third_doha_id = dohas[2].id
    second_doha_id = dohas[1].id
    
    response = await _make_request(f"/content/doha/{third_doha_id}/navigation")
    assert response.status_code == 200
    nav_data = response.json()
    
    assert nav_data["previous"] is not None, "Last doha should have previous"
    assert nav_data["previous"]["id"] == second_doha_id
    
    assert nav_data["current"]["id"] == third_doha_id
    assert nav_data["current"]["number_in_chapter"] == 3
    
    assert nav_data["next"] is None, "Last doha should have no next verse"


@pytest.mark.asyncio
async def test_e2e_navigation_gapped_sequence_fix(db: Session):
    """
    PRIMARY REGRESSION TEST: Navigation handles GAPPED sequences correctly.
    
    This tests the core fix from ISSUE-008:
    If a chapter has verses with number_in_chapter = [1, 2, 5],
    then next of verse 2 should be verse 5 (NOT None).
    
    ✅ This is the definitive verification that the gapped sequence bug is fixed.
    """
    # Create minimal hierarchy
    author = ClassicalAuthor(
        slug="test-author",
        name="Test Author",
        is_deleted=False,
    )
    db.add(author)
    db.flush()

    work = ClassicalWork(
        author_id=author.id,
        slug="test-work",
        title="Test Work",
        work_type="poetry",
        is_deleted=False,
    )
    db.add(work)
    db.flush()

    chapter = WorkChapter(
        work_id=work.id,
        slug="gapped-chapter",
        title="Gapped Chapter",
        number=1,
        is_deleted=False,
    )
    db.add(chapter)
    db.flush()

    # Create dohas with GAPPED number_in_chapter: [1, 2, 5]
    doha1 = DohaEntry(
        chapter_id=chapter.id,
        number_in_chapter=1,
        main_text="Verse One",
        meaning="First",
        status="active",
        is_deleted=False,
    )
    doha2 = DohaEntry(
        chapter_id=chapter.id,
        number_in_chapter=2,
        main_text="Verse Two",
        meaning="Second",
        status="active",
        is_deleted=False,
    )
    # GAPPED: verses 3, 4 are missing
    doha5 = DohaEntry(
        chapter_id=chapter.id,
        number_in_chapter=5,
        main_text="Verse Five",
        meaning="Fifth",
        status="active",
        is_deleted=False,
    )
    db.add_all([doha1, doha2, doha5])
    db.commit()

    # TEST: Navigation for verse 2 (middle of gapped sequence)
    # Before fix: nav.next would return None (looked for number_in_chapter == 2 + 1)
    # After fix: nav.next should return verse 5 (finds nearest ordered neighbor)
    
    response = await _make_request(f"/content/doha/{doha2.id}/navigation")
    assert response.status_code == 200
    nav_data = response.json()
    
    # Verify previous is correct
    assert nav_data["previous"] is not None, "Verse 2 should have previous (verse 1)"
    assert nav_data["previous"]["id"] == doha1.id
    assert nav_data["previous"]["number_in_chapter"] == 1
    
    # Verify current is correct
    assert nav_data["current"]["id"] == doha2.id
    assert nav_data["current"]["number_in_chapter"] == 2
    
    # **PRIMARY ASSERTION**: Next must be verse 5 (the FIX)
    assert nav_data["next"] is not None, "Verse 2 should have next (verse 5), even though gapped"
    assert nav_data["next"]["id"] == doha5.id, f"Next should be verse 5, got verse {nav_data['next']['number_in_chapter']}"
    assert nav_data["next"]["number_in_chapter"] == 5
