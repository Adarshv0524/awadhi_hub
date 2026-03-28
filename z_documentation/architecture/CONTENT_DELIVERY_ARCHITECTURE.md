# System Architecture & Content Delivery

**Document Purpose**: Deep technical architecture, data flows, and design decisions  
**Audience**: Architects, senior engineers, system designers  
**Last Updated**: March 26, 2026  

---

## Section 1: Hierarchical Content Model

### The Three-Layer Taxonomy

```
┌──────────────────────────────────────────────────────┐
│ ClassicalAuthor (Tulsidas, Krittibas, etc.)          │
│ - slug: unique, URL-friendly identifier              │
│ - name: human-readable name in script/Roman          │
│ - language: awadhi, hindi, etc.                      │
└──────────────────────────────────────────────────────┘
              ↓ (1:N via author_id FK)
┌──────────────────────────────────────────────────────┐
│ ClassicalWork (Ramcharitmanas, Chandayan, etc.)      │
│ - author_id: FK to ClassicalAuthor (non-nullable)    │
│ - slug: unique within author (composite unique key)  │
│ - work_type: poetry, prose, narrative, etc.          │
│ - original_script: devanagari, kaithi, etc.          │
└──────────────────────────────────────────────────────┘
              ↓ (1:N via work_id FK)
┌──────────────────────────────────────────────────────┐
│ WorkChapter (Ayodhya Kand, Manas Kand, etc.)         │
│ - work_id: FK to ClassicalWork (non-nullable)        │
│ - slug: unique within work (composite unique key)    │
│ - number: chapter ordering (1, 2, 3, ...)           │
└──────────────────────────────────────────────────────┘
              ↓ (0:N optional references)
┌──────────────────────────────────────────────────────┐
│ Content Nodes (DohaEntry, Dictionary, Idiom, etc.)   │
│ - author_id, work_id, chapter_id (optional FKs)      │
│ - number_in_chapter: ordering within chapter         │
│ - hierarchy_path: denormalized for URL routing       │
└──────────────────────────────────────────────────────┘
```

### Design Rationale

**Why Three-Layer?**
1. **Referential Integrity**: FK constraints prevent orphaned works/chapters
2. **Efficient Traversal**: Author → Works → Chapters requires minimal queries
3. **Unique Slug Composition**: (author_id, slug) and (work_id, slug) enable semantic URLs
4. **URL Routing**: Slugs enable `/tulsidas/ramcharitmanas/ayodhya-kand` URLs without ID leakage

**Why Optional Content FK?**
1. **Flexibility**: Content can exist standalone or within hierarchy
2. **Content Reuse**: Dictionary entries can span multiple works
3. **Extensibility**: New content types don't require schema redesign

---

## Section 2: Content Linking via Cross-References

### The Polymorphic Pattern

Rather than separate tables per chapter, all canonical content shares:

```python
# Common to DohaEntry, DictionaryEntry, IdiomEntry, ArticleEntry
author_id: Optional[int] = FK("classical_authors.id")
work_id: Optional[int] = FK("classical_works.id")
chapter_id: Optional[int] = FK("work_chapters.id")
number_in_chapter: Optional[int]  # ordering within chapter
hierarchy_path: Optional[str]     # e.g., "author-slug/work-slug/chapter-slug/number"
```

### Examples

**Example 1: Doha in Ramcharitmanas, Ayodhya Kand**
```
DohaEntry {
  id: 100,
  main_text: "श्रीरामचन्द्र कृपालु भजु मन",
  author_id: 1,   // FK to Tulsidas
  work_id: 1,     // FK to Ramcharitmanas
  chapter_id: 1,  // FK to Ayodhya Kand
  number_in_chapter: 23,
  hierarchy_path: "tulsidas/ramcharitmanas/ayodhya-kand/23"
}
```

**Example 2: Standalone Dictionary Entry**
```
DictionaryEntry {
  id: 200,
  lemma_devanagari: "दोहा",
  author_id: null,    // Not linked to hierarchy
  work_id: null,
  chapter_id: null,
  number_in_chapter: null
}
```

**Example 3: Dictionary Entry in Chapter Context**
```
DictionaryEntry {
  id: 201,
  lemma_devanagari: "राम",
  author_id: 1,       // Tulsidas
  work_id: 1,         // Ramcharitmanas
  chapter_id: 1,      // Ayodhya Kand
  number_in_chapter: 5  // 5th definition in this chapter
}
```

### Benefits

| Benefit | How |
|---------|-----|
| **Query Flexibility** | `WHERE chapter_id = 1` returns all content types |
| **Content Reuse** | Dictionary entry appears in multiple chapters without duplication |
| **Extensibility** | Add new content type without modifying hierarchy tables |
| **Polymorphic Display** | Chapter page can render Doha + Dictionary + Idiom + Article |
| **Engagement Unification** | Single EngagementKPI table using (content_type, content_id) |

---

## Section 3: Linked-List Sequencing (Verse Navigation)

### Problem Statement

Users reading verse-by-verse (e.g., Hanuman Chalisa) should navigate adjacent verses without returning to chapter page.

**Desired Experience**:
```
Current: Verse 2 - "Ram dut atulit bal"
← Previous: Verse 1 - "Jai Hanuman gyan gun sagar"
Next → Verse 3 - "Mahavir vikram bichram dharam"
```

### Solution: Implicit Linked-List via (chapter_id, number_in_chapter)

No explicit next/prev pointers. Instead, **query adjacent entries by ordering**.

#### Algorithm: `get_doha_navigation(db, doha_id)`

```python
def get_doha_navigation(db: Session, doha_id: int) -> DohaNavigationOut:
    """
    Return prev/current/next doha cards within same chapter.
    
    Deterministic ordering (no random shuffling):
    1. Primary: number_in_chapter (sequential verses)
    2. Secondary: created_at (fallback if unnumbered)
    3. Tertiary: id (final tiebreaker)
    """
    # Step 1: Fetch current doha
    current = (db.query(DohaEntry)
        .filter(
            DohaEntry.id == doha_id,
            DohaEntry.is_deleted == False,
            DohaEntry.status == "active"
        )
        .first()
    )
    if not current:
        raise HTTPException(404, "Doha not found")

    # Step 2: If current is in a chapter, find previous/next
    if current.chapter_id is not None:
        if current.number_in_chapter is not None:
            # Numbered entries: find largest/smallest number_in_chapter
            previous = (db.query(DohaEntry)
                .filter(
                    DohaEntry.chapter_id == current.chapter_id,
                    DohaEntry.number_in_chapter < current.number_in_chapter,
                    DohaEntry.is_deleted == False,
                    DohaEntry.status == "active"
                )
                .order_by(
                    DohaEntry.number_in_chapter.desc(),  # Largest first
                    DohaEntry.created_at.desc(),
                    DohaEntry.id.desc()
                )
                .first()
            )
            
            next_item = (db.query(DohaEntry)
                .filter(
                    DohaEntry.chapter_id == current.chapter_id,
                    DohaEntry.number_in_chapter > current.number_in_chapter,
                    DohaEntry.is_deleted == False,
                    DohaEntry.status == "active"
                )
                .order_by(
                    DohaEntry.number_in_chapter.asc(),  # Smallest first
                    DohaEntry.created_at.asc(),
                    DohaEntry.id.asc()
                )
                .first()
            )
        else:
            # Unnumbered entries: use created_at fallback
            previous = (db.query(DohaEntry)
                .filter(
                    DohaEntry.chapter_id == current.chapter_id,
                    DohaEntry.created_at < current.created_at,
                    DohaEntry.is_deleted == False,
                    DohaEntry.status == "active"
                )
                .order_by(DohaEntry.created_at.desc(), DohaEntry.id.desc())
                .first()
            )
            
            next_item = (db.query(DohaEntry)
                .filter(
                    DohaEntry.chapter_id == current.chapter_id,
                    DohaEntry.created_at > current.created_at,
                    DohaEntry.is_deleted == False,
                    DohaEntry.status == "active"
                )
                .order_by(DohaEntry.created_at.asc(), DohaEntry.id.asc())
                .first()
            )

    return DohaNavigationOut(
        previous=_to_navcard(previous) if previous else None,
        current=_to_navcard(current),
        next=_to_navcard(next_item) if next_item else None
    )
```

#### Handling Edge Cases

**Case 1: Gapped Numbering**
```
Chapter has verses: [1, 3, 5, 10, ...]
Current: verse 5

Query: WHERE number_in_chapter < 5 ORDER BY DESC LIMIT 1
Result: verse 3 (correct! skips gap at 2, 4)
```

**Case 2: At Boundary (First Verse)**
```
Current: verse 1
Query: WHERE number_in_chapter < 1 ...
Result: NULL → previous = None
        (Previous button disabled)
```

**Case 3: No number_in_chapter**
```
current.number_in_chapter = None
Fallback to created_at comparison
(Works for unordered/user-contributed content)
```

**Case 4: Deleted Previous Entry**
```
Verse 1 → 2 → 3 [deleted] → 4
Current: verse 4
Query: WHERE number_in_chapter < 4 AND is_deleted = False
Result: verse 2 (correct! skips deleted entry)
```

#### Database Index

**File**: `backend/alembic/versions/0015_add_doha_chapter_sequence_index.py`

```python
op.create_index(
    'ix_doha_chapter_number',
    'doha_entries',
    ['chapter_id', 'number_in_chapter']
)
```

**Impact**: O(log n) lookup instead of O(n) full table scan.

---

## Section 4: Engagement Tracking Architecture

### Unified EngagementKPI Table

```python
class EngagementKPI(Base):
    __tablename__ = "engagement_kpis"
    id: int
    content_type: str              # "doha", "dictionary", "idiom", "article"
    content_id: int                # PK of respective content table
    views_count: int
    search_hits_count: int
    likes_count: int
    shares_count: int
    bookmarks_count: int
    weight_score: float            # Computed metric
    
    __table_args__ = (
        UniqueConstraint(
            "content_type", "content_id",
            name="uq_engagement_content"
        ),
    )
```

### Why Unified?

1. **Single schema change** for all content types
2. **Efficient querying**: `WHERE content_type IN ('doha', 'dictionary')`
3. **Consistent metrics** across content types
4. **Extensible**: Add new content type without schema migration

### Weight Score Algorithm

```python
weight_score = 0.6 * log(views + 1) + 0.3 * log(search_hits + 1) + 0.1 * log(likes + 1)
```

**Rationale**:
- Views (60%) = primary discoverability signal
- Search hits (30%) = secondary relevance signal
- Likes (10%) = user preference signal (noisy)
- Logarithmic scaling = prevents single viral entry from dominating

**Example**:
```
views=1000, search_hits=300, likes=50
weight = 0.6 * log(1001) + 0.3 * log(301) + 0.1 * log(51)
       = 0.6 * 6.91 + 0.3 * 5.71 + 0.1 * 3.93
       = 4.146 + 1.713 + 0.393
       = 6.252  ← popularity rank
```

### Engagement Querying Pattern

```python
# Query with engagement metadata
result = (db.query(
    DohaEntry,
    EngagementKPI.views_count,
    EngagementKPI.likes_count,
    EngagementKPI.weight_score
)
.outerjoin(
    EngagementKPI,
    and_(
        EngagementKPI.content_type == "doha",
        EngagementKPI.content_id == DohaEntry.id
    )
)
.filter(DohaEntry.chapter_id == 1))
```

---

## Section 5: Migration & Schema Evolution

### Critical Migrations

| # | Name | Changes | Status |
|---|------|---------|--------|
| 0001 | Auth Tables | users, tokens, oauth | ✅ |
| 0003 | Hierarchy | authors, works, chapters | ✅ |
| 0006 | Doha Entries | canonical content | ✅ |
| 0008 | Engagement | unified KPI tracking | ✅ |
| **0014** | **Schema Drift Fix** | **Critical alignment** | **✅** |
| 0015 | Chapter Sequence Index | Navigation optimization | ✅ |

### Migration 0014: Schema Drift Resolution

**Problem**:
- Model: `submissions.external_references`
- Migration 0004: Created `submissions.references` ❌
- Runtime: `Unknown column 'external_references'` → 500 error

**Solution**:
```python
# Rename references → external_references
op.alter_column('submissions', 'references', new_column_name='external_references')

# Rename key → setting_key
op.alter_column('system_settings', 'key', new_column_name='setting_key')

# Widen version_num for long Alembic IDs
op.alter_column('alembic_version', 'version_num',
    existing_type=VARCHAR(32),
    type_=VARCHAR(255)
)
```

**Prevention**:
1. Add CI schema contract validation
2. Run migrations on clean test DB before merging
3. Compare ORM metadata vs DB schema

---

## Section 6: API Query Patterns

### Pattern 1: Fetch Chapter Content with Metadata

```python
@router.get("/by-path/{author_slug}/{work_slug}/{chapter_slug}/dohas")
def list_chapter_dohas_by_path(...):
    # Resolve hierarchy
    author = get_by_slug(ClassicalAuthor, author_slug)
    work = get_by_slug(ClassicalWork, work_slug, author_id=author.id)
    chapter = get_by_slug(WorkChapter, chapter_slug, work_id=work.id)
    
    # Query content
    dohas = (db.query(DohaEntry)
        .filter(
            DohaEntry.chapter_id == chapter.id,
            DohaEntry.status == "active",
            DohaEntry.is_deleted == False
        )
        .order_by(DohaEntry.number_in_chapter.asc())
        .all()
    )
    
    return ChapterDohasOut(
        chapter_id=chapter.id,
        total=len(dohas),
        items=dohas
    )
```

### Pattern 2: Fetch Content with Engagement

```python
def _doha_query_with_engagement(db):
    return (db.query(
        DohaEntry,
        EngagementKPI.views_count,
        EngagementKPI.likes_count,
        EngagementKPI.shares_count,
        EngagementKPI.bookmarks_count
    )
    .outerjoin(
        EngagementKPI,
        and_(
            EngagementKPI.content_type == "doha",
            EngagementKPI.content_id == DohaEntry.id
        )
    ))
```

### Pattern 3: Sequence Navigation

```python
# Previous verse (largest number_in_chapter < current)
previous = (db.query(DohaEntry)
    .filter(
        DohaEntry.chapter_id == current.chapter_id,
        DohaEntry.number_in_chapter < current.number_in_chapter,
        DohaEntry.is_deleted == False,
        DohaEntry.status == "active"
    )
    .order_by(DohaEntry.number_in_chapter.desc())
    .first()
)
```

---

## Conclusion

This architecture achieves:
- ✅ Strict referential integrity
- ✅ Polymorphic content within chapters
- ✅ Deterministic sequencing
- ✅ Scalable engagement tracking
- ✅ Extensible for new content types
- ✅ Production-ready with migration guardrails

See **Issues.md** for current gaps and roadmap.
