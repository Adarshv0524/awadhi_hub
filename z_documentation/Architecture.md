# Architecture: Technical Deep Dive

**Document Scope**: Hierarchical content model, database schema, content delivery orchestration, and sequencing logic  
**Audience**: Backend engineers, system designers, future maintainers  
**Last Updated**: March 26, 2026  

---

## Part 0: Authentication Architecture

### 0.1 Active Authentication Modes

The system supports two active authentication modes:

- Email/password via `POST /auth/login`
- Google OAuth 2.0 via `/auth/oauth/google/login` and `/auth/oauth/google/callback`

Both flows issue the same JWT access and refresh tokens and converge on the same frontend session storage behavior.

### 0.2 Google OAuth Runtime Flow

1. Frontend login initiates Google OAuth with `client_id`, `redirect_uri`, `response_type=code`, `scope=openid email profile`, and a state token.
2. Google redirects to backend callback: `/auth/oauth/google/callback`.
3. Backend validates state, exchanges code for Google tokens, resolves or creates the user, then issues platform JWT tokens.
4. Backend redirects to frontend `/oauth/callback` with JWT tokens in URL fragment.
5. Frontend callback stores tokens and completes redirect to the requested app path.

### 0.3 Configuration Notes

- Frontend public config uses `PUBLIC_GOOGLE_CLIENT_ID` for OAuth URL composition.
- OAuth callback target must match backend expectations and Google Console allowed redirect URIs.
- No OAuth client secret is stored in frontend code or public environment variables.

---

## Part 1: Hierarchical Content Architecture

### 1.1 The Three-Layer Hierarchy Model

The system employs a **strict hierarchical model** for classical literary works:

```
ClassicalAuthor (primary key: id, unique: slug)
    ↓ (1:N relationship via author_id)
  ClassicalWork (primary key: id, unique: (author_id, slug))
    ↓ (1:N relationship via work_id)
    WorkChapter (primary key: id, unique: (work_id, slug))
```

**Why this structure?**
- Enforces referential integrity (no orphaned works/chapters)
- Enables slug-based URL routing (e.g., `/tulsidas/ramcharitmanas/ayodhya-kand`)
- Supports efficient hierarchy traversal with minimal queries

#### ClassicalAuthor Table

```python
class ClassicalAuthor(Base):
    __tablename__ = "classical_authors"
    id = Column(Integer, primary_key=True)
    slug = Column(String(150), unique=True, index=True)  # tulsidas, krittibas
    name = Column(String(255))                           # तुलसीदास
    short_bio = Column(Text)
    long_bio = Column(Text)
    language = Column(String(50))                        # awadhi, hindi
    is_deleted = Column(Boolean, default=False)
    created_at, updated_at = Column(DateTime)...
```

#### ClassicalWork Table

```python
class ClassicalWork(Base):
    __tablename__ = "classical_works"
    id = Column(Integer, primary_key=True)
    author_id = Column(Integer, ForeignKey("classical_authors.id"))
    slug = Column(String(150), index=True)     # ramcharitmanas, chandayan
    title = Column(String(255))                # रामचरितमानस
    description = Column(Text)
    work_type = Column(String(50))             # poetry, prose, narrative
    original_script = Column(String(50))       # devanagari, kaithi
    is_deleted = Column(Boolean, default=False)
    created_at, updated_at = Column(DateTime)...
    
    __table_args__ = (
        UniqueConstraint("author_id", "slug"),  # (tulsidas, ramcharitmanas) unique
    )
```

#### WorkChapter Table

```python
class WorkChapter(Base):
    __tablename__ = "work_chapters"
    id = Column(Integer, primary_key=True)
    work_id = Column(Integer, ForeignKey("classical_works.id"))
    slug = Column(String(150), index=True)     # ayodhya-kand, manas-kand
    title = Column(String(255))                # अयोध्या काण्ड
    number = Column(Integer)                   # 1, 2, 3, ... (chapter order)
    is_deleted = Column(Boolean, default=False)
    created_at, updated_at = Column(DateTime)...
    
    __table_args__ = (
        UniqueConstraint("work_id", "slug"),    # (ramcharitmanas, ayodhya-kand) unique
        UniqueConstraint("work_id", "number"),  # enforce strict ordering
    )
```

---

### 1.2 Content Node Linking via Cross-References

Classical literature often contains **multiple content types within a single chapter**: verses (Doha/Chaupai), word definitions, idioms, annotations. Rather than creating separate tables per chapter and forcing one-to-one relationships, the system uses **cross-reference fields** to enable **polymorphic content** within a hierarchy.

#### The Cross-Reference Pattern

All canonical content tables include:

```python
# Common to DohaEntry, DictionaryEntry, IdiomEntry, ArticleEntry
author_id = Column(Integer, ForeignKey("classical_authors.id"), nullable=True)
work_id = Column(Integer, ForeignKey("classical_works.id"), nullable=True)
chapter_id = Column(Integer, ForeignKey("work_chapters.id"), nullable=True)
number_in_chapter = Column(Integer, nullable=True)
hierarchy_path = Column(String(512), nullable=True)  # denormalized for URL routing
```

**Why cross-reference instead of specialized tables?**

1. **Flexibility**: The same Doha can exist in multiple chapters (variants)
2. **Query Efficiency**: Single WHERE clause filters by hierarchy (author/work/chapter)
3. **Content Reuse**: Dictionary entries shared across works, indexed by chapter
4. **Extensibility**: New content types added without schema migration for hierarchy

**Example**: In Ramcharitmanas, Ayodhya Kand, the Doha "Ram dut atulit bal..." can be:
- Accessed as `/doha/{doha_id}` (standalone)
- Browsed as part of `/authors/tulsidas/works/ramcharitmanas/chapters/ayodhya-kand`
- Found via `/search?author=tulsidas&work=ramcharitmanas&chapter=ayodhya-kand`

---

### 1.3 The Canonical Content Tables

#### DohaEntry (Verses)

```python
class DohaEntry(Base):
    __tablename__ = "doha_entries"
    id = Column(Integer, primary_key=True)
    # Hierarchy cross-references
    hierarchy_path = Column(String(512), index=True)  # tulsidas/ramcharitmanas/ayodhya-kand/23
    author_id = Column(Integer, index=True)
    work_id = Column(Integer, index=True)
    chapter_id = Column(Integer, index=True)          # FK to work_chapters
    number_in_chapter = Column(Integer)               # 23 (ordering within chapter)
    # Content
    main_text = Column(Text)                          # श्रीरामचन्द्र कृपालु भजु मन
    meaning = Column(Text)                            # English/Hindi commentary
    text_devanagari = Column(Text)
    text_romanized = Column(Text)                     # For search normalization
    # Metadata
    status = Column(String(20), default="active")     # draft, active, archived
    visibility = Column(String(20), default="public") # public, private, restricted
    version = Column(Integer, default=1)
    is_canonical = Column(Boolean, default=True)
    source_submission_id = Column(Integer, unique=True) # backlink to user submission
    created_by, verified_by = Column(Integer)...
    is_deleted = Column(Boolean, default=False)
```

**Key Design Decisions**:
- `number_in_chapter` enables v1 of deterministic sequencing (see Section 2.1)
- `hierarchy_path` is denormalized for fast URL resolution (no 3-way join needed)
- `status` + `is_deleted` provide soft-delete semantics + state machine
- `source_submission_id` maintains audit trail back to user submission

#### DictionaryEntry, IdiomEntry, ArticleEntry

Similar structure, with content-specific fields:

```python
# DictionaryEntry
lemma_devanagari = Column(String(512), index=True)
lemma_roman = Column(String(512), index=True)
lemma_roman_norm = Column(String(512), index=True)  # normalized for search
senses = Column(JSON)  # [{sense: str, example: str}, ...]

# IdiomEntry
text_devanagari = Column(Text, index=True)
text_roman = Column(Text)
meaning = Column(Text)
examples = Column(JSON)
region = Column(String(64))

# ArticleEntry
title = Column(String(512), index=True)
title_devanagari = Column(String(512))
body = Column(Text)
excerpt = Column(Text)
tags = Column(JSON)
```

All support hierarchy linking: `author_id`, `work_id`, `chapter_id`, `number_in_chapter`.

---

## Part 2: Linked-List Sequencing Logic

### 2.1 Verse Navigation: Prev/Current/Next

**Problem**: Users reading "Ram dut atulit bal..." want to press "Next" to jump directly to "Mahavir vikram bichram dharam..." rather than scrolling or navigating back to the chapter page.

**Solution**: Linked-list-style sequencing without explicit prev/next pointers. Instead, **query adjacent entries by (chapter_id, number_in_chapter)**.

#### Implementation: `get_doha_navigation()`

Location: `backend/app/services/content_service.py`

```python
def get_doha_navigation(db: Session, doha_id: int) -> DohaNavigationOut:
    """
    Return prev/current/next doha cards within the same chapter.
    
    Ordering strategy (deterministic, non-shuffling):
    1. Primary: number_in_chapter (handles gapped sequences)
    2. Secondary: created_at (fallback for unordered entries)
    3. Tertiary: id (final tiebreaker)
    """
    # Get current doha
    current = db.query(DohaEntry).filter(
        DohaEntry.id == doha_id,
        DohaEntry.is_deleted == False,
        DohaEntry.status == "active",
    ).first()
    
    if not current:
        raise HTTPException(404, "Doha not found")

    # Find previous: largest number_in_chapter < current.number_in_chapter
    if current.number_in_chapter is not None:
        previous = (db.query(DohaEntry)
            .filter(
                DohaEntry.chapter_id == current.chapter_id,
                DohaEntry.number_in_chapter < current.number_in_chapter,
                DohaEntry.is_deleted == False,
                DohaEntry.status == "active",
            )
            .order_by(
                DohaEntry.number_in_chapter.desc(),  # largest first
                DohaEntry.created_at.desc(),
                DohaEntry.id.desc()
            )
            .first()
        )
    
    # Find next: smallest number_in_chapter > current.number_in_chapter
    if current.number_in_chapter is not None:
        next_item = (db.query(DohaEntry)
            .filter(
                DohaEntry.chapter_id == current.chapter_id,
                DohaEntry.number_in_chapter > current.number_in_chapter,
                DohaEntry.is_deleted == False,
                DohaEntry.status == "active",
            )
            .order_by(
                DohaEntry.number_in_chapter.asc(),   # smallest first
                DohaEntry.created_at.asc(),
                DohaEntry.id.asc()
            )
            .first()
        )
    else:
        # Fallback: use created_at for unordered entries
        previous = (db.query(DohaEntry)
            .filter(
                DohaEntry.chapter_id == current.chapter_id,
                DohaEntry.created_at < current.created_at,
                DohaEntry.is_deleted == False,
                DohaEntry.status == "active",
            )
            .order_by(DohaEntry.created_at.desc(), DohaEntry.id.desc())
            .first()
        )
        next_item = (db.query(DohaEntry)
            .filter(
                DohaEntry.chapter_id == current.chapter_id,
                DohaEntry.created_at > current.created_at,
                DohaEntry.is_deleted == False,
                DohaEntry.status == "active",
            )
            .order_by(DohaEntry.created_at.asc(), DohaEntry.id.asc())
            .first()
        )
    
    return DohaNavigationOut(
        previous=_to_card(previous) if previous else None,
        current=_to_card(current),
        next=_to_card(next_item) if next_item else None,
    )
```

#### Response Schema

```python
class DohaNavCard(BaseModel):
    id: int
    number_in_chapter: Optional[int]
    title: Optional[str] = None
    short_text: str  # first 100 chars of main_text

class DohaNavigationOut(BaseModel):
    previous: Optional[DohaNavCard] = None
    current: DohaNavCard
    next: Optional[DohaNavCard] = None
```

#### Endpoint

```python
@router.get("/doha/{doha_id}/navigation", response_model=DohaNavigationOut)
def get_doha_navigation_endpoint(doha_id: int, db: Session = Depends(get_db)):
    """Return prev/current/next doha cards based on chapter sequence."""
    return get_doha_navigation(db, doha_id)
```

#### Frontend Integration

File: `frontend/src/pages/doha/[id].astro`

```astro
let navigation = null;

try {
  navigation = await api(`/content/doha/${id}/navigation`);
} catch (navErr) {
  console.warn("[Doha] Navigation fetch failed:", navErr);
}
```

Then rendered via:

```astro
<NavigationControls 
  previousId={navigation?.previous?.id}
  nextId={navigation?.next?.id}
  previousText={navigation?.previous?.short_text}
  nextText={navigation?.next?.short_text}
/>
```

#### Handling Edge Cases

1. **No Previous/Next**: Buttons disabled, visually grayed out (CSS class `opacity-50`)
2. **Gapped Numbering**: If chapter has verses [1, 3, 5, 10], queries find nearest ordered neighbor
3. **Unordered Content**: Fallback to created_at ensures deterministic sequencing even without number_in_chapter
4. **Deleted/Inactive**: Filter excludes is_deleted=True, status != "active"

#### Performance Considerations

- Index on `(chapter_id, number_in_chapter)` added in migration 0015
- Two-query pattern (one per direction) is acceptable for <100 items per chapter
- For very large chapters (1000+ verses), consider pagination-based navigation

---

### 2.2 Chapter Content Listing

#### Current Implementation

File: `backend/app/api/v1/content.py`

```python
@router.get("/by-path/{author_slug}/{work_slug}/{chapter_slug}/dohas", 
            response_model=ChapterDohasOut)
def list_chapter_dohas_by_path(
    author_slug: str,
    work_slug: str,
    chapter_slug: str,
    db: Session = Depends(get_db),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
):
    """
    GET /content/by-path/tulsidas/ramcharitmanas/ayodhya-kand/dohas?offset=0&limit=50
    
    Returns paginated list of dohas in chapter, sorted by number_in_chapter.
    """
    # Resolve hierarchy
    author = db.query(ClassicalAuthor).filter(
        ClassicalAuthor.slug == author_slug,
        ClassicalAuthor.is_deleted == False
    ).first()
    if not author:
        raise HTTPException(404, "Author not found")
    
    work = db.query(ClassicalWork).filter(
        ClassicalWork.author_id == author.id,
        ClassicalWork.slug == work_slug,
        ClassicalWork.is_deleted == False
    ).first()
    if not work:
        raise HTTPException(404, "Work not found")
    
    chapter = db.query(WorkChapter).filter(
        WorkChapter.work_id == work.id,
        WorkChapter.slug == chapter_slug,
        WorkChapter.is_deleted == False
    ).first()
    if not chapter:
        raise HTTPException(404, "Chapter not found")
    
    # Query dohas
    q = db.query(DohaEntry).filter(
        DohaEntry.chapter_id == chapter.id,
        DohaEntry.is_deleted == False,
        DohaEntry.status == "active",
    )
    total = q.count()
    items = (q
        .order_by(DohaEntry.number_in_chapter.asc(), DohaEntry.id.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    
    return ChapterDohasOut(
        chapter_id=chapter.id,
        chapter_slug=chapter.slug,
        total=total,
        offset=offset,
        limit=limit,
        items=[_serialize_chapter_doha(i) for i in items],
    )
```

#### Response Schema

```python
class ChapterDohaItem(BaseModel):
    id: int
    hierarchy_path: Optional[str]
    chapter_id: Optional[int]
    number_in_chapter: Optional[int]
    main_text: str
    meaning: Optional[str]
    text_devanagari: Optional[str]
    text_romanized: Optional[str]

class ChapterDohasOut(BaseModel):
    chapter_id: int
    chapter_slug: Optional[str]
    total: int
    offset: int
    limit: int
    items: List[ChapterDohaItem]
```

#### Chapter Page Sequence Presentation

The chapter page now displays sequence metadata per card to improve orientation while reading long chapters.

```text
Verse {index + 1} of {chapterItems.length}
```

Implementation notes:
- End-user numbering is explicitly 1-based.
- Sequence badges are styled through `.sequence-badge` in chapter-specific CSS.
- Label text is adaptable (`Verse` by default, `Stanza` for poem-like contexts).

---

## Part 3: Polymorphic Content Rendering

### 3.1 Engagement Tracking Across Content Types

The **EngagementKPI** table is designed to be **content-type agnostic**:

```python
class EngagementKPI(Base):
    __tablename__ = "engagement_kpis"
    id = Column(Integer, primary_key=True)
    content_type = Column(String(50), index=True)  # "doha", "dictionary", "idiom", "article"
    content_id = Column(Integer, index=True)       # FK to respective table
    views_count = Column(Integer, default=0)
    search_hits_count = Column(Integer, default=0)
    likes_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    bookmarks_count = Column(Integer, default=0)
    weight_score = Column(Float, default=0.0)
    
    __table_args__ = (
        UniqueConstraint("content_type", "content_id"),  # Enforce 1:1
    )
```

#### Weight Score Algorithm

```python
weight_score = 0.6 * log(views + 1) + 0.3 * log(search_hits + 1) + 0.1 * log(likes + 1)
```

**Rationale**:
- Views are the primary signal (0.6 weight)
- Search hits indicate discoverability (0.3)
- Likes add user preference signal (0.1)
- Logarithmic scaling prevents single viral entry from dominating

#### Querying Engagement for Multiple Content Types

```python
# Efficient query for chapter dohas with engagement
def _doha_query_with_metadata(db: Session):
    return (
        db.query(
            DohaEntry,
            ClassicalAuthor.name.label("author_name"),
            ClassicalWork.title.label("work_name"),
            WorkChapter.title.label("chapter_name"),
            EngagementKPI.views_count.label("views_count"),
            EngagementKPI.likes_count.label("likes_count"),
            EngagementKPI.shares_count.label("shares_count"),
            EngagementKPI.bookmarks_count.label("bookmarks_count"),
            EngagementKPI.search_hits_count.label("search_hits_count"),
            EngagementKPI.weight_score.label("weight_score"),
        )
        .outerjoin(ClassicalAuthor, ClassicalAuthor.id == DohaEntry.author_id)
        .outerjoin(ClassicalWork, ClassicalWork.id == DohaEntry.work_id)
        .outerjoin(WorkChapter, WorkChapter.id == DohaEntry.chapter_id)
        .outerjoin(
            EngagementKPI,
            and_(
                EngagementKPI.content_type == "doha",
                EngagementKPI.content_id == DohaEntry.id,
            ),
        )
    )
```

All content-node API payloads (`doha`, `dictionary`, `idiom`, and `article`) include these engagement fields in response schemas and serialization output with safe defaults:

```text
views_count, likes_count, shares_count, bookmarks_count, search_hits_count, weight_score
```

Default handling contract:
- Integer metrics default to `0`
- `weight_score` defaults to `0.0`

---

## Part 4: Schematic Improvements & Data Integrity

### 4.1 Migration History & Schema Evolution

| # | Migration | Key Changes |
|---|-----------|------------|
| 0001 | Create Auth Tables | users, refresh_tokens, oauth_accounts |
| 0002 | User Role Index | Added role-based indexing |
| 0003 | Hierarchy Tables | classical_authors, classical_works, work_chapters |
| 0004 | Submissions | submissions table with status machine |
| 0005 | Moderation | moderation_logs, moderation_guidelines |
| 0006 | Doha Entries | doha_entries, content_versions |
| 0007 | Fulltext Index | MySQL FULLTEXT on doha main_text |
| 0008 | Engagement | engagement_kpis, user_interactions, share_logs, reports |
| 0009 | Rate Limiting | rate_limit_counters with atomic upsert |
| 0010 | System Settings | system_settings key-value store |
| 0011 | Audit Logging | audit_logs for all user actions |
| 0012 | Content Types | dictionary_entries, idiom_entries, article_entries |
| 0013 | Interactions v2 | Enhanced user_interactions with metadata |
| **0014** | **Schema Drift Fix** | **Reconciled model/migration drift (CRITICAL)** |
| 0015 | Indexes | Added composite index on (chapter_id, number_in_chapter) |

### 4.2 Critical Schema Drift Resolution (Migration 0014)

**Problem**: Model and migration drift caused runtime 500 errors:
- Model expects `submissions.external_references`, but migration created `references`
- Model expects `system_settings.setting_key`, but migration created `key`
- `alembic_version.version_num` VARCHAR(32) was too short for long revision IDs

**Resolution** (Migration 0014):
```python
# Step 1: Rename submissions.references -> external_references
op.alter_column('submissions', 'references', new_column_name='external_references')

# Step 2: Rename system_settings.key -> setting_key
op.alter_column('system_settings', 'key', new_column_name='setting_key')

# Step 3: Widen alembic_version.version_num
op.alter_column('alembic_version', 'version_num', 
                existing_type=VARCHAR(32),
                type_=VARCHAR(255))
```

**Lesson Learned**: Schema drift prevention requires:
1. **Pre-migration Testing**: Run migrations against clean DB in CI
2. **Schema Contract Validation**: Compare ORM metadata vs migration output
3. **Regression Marking**: Document drift in migration docstrings

---

## Part 5: Authorization & Moderation

### 5.1 Role-Based Access Control

```python
class User(Base):
    role = Column(String(50), default="registered")     # registered, moderator, admin
    permissions = Column(Integer, default=0)             # Bitfield for fine-grained perms
    permission_scopes = Column(JSON)                     # e.g., {"moderate": ["doha"], "admin": ["hierarchy"]}
```

#### Role Hierarchy

| Role | Can Do |
|------|--------|
| **registered** | Submit content, like/bookmark, view public content |
| **moderator** | Review submissions, approve/reject, comment |
| **admin** | Manage hierarchy, manage users, bulk operations |

---

## Part 6: Integration Points & Future Extensibility

### 6.1 Adding a New Content Type (e.g., Chaupai)

1. **Create new table** (MODEL)
   ```python
   class ChauPaiEntry(Base):
       __tablename__ = "chaupai_entries"
       # ... standard fields + hierarchy linking
   ```

2. **Add migration** (ALEMBIC)
   ```bash
   alembic revision --autogenerate -m "add_chaupai_entries"
   ```

3. **Create API endpoints** (REST)
   ```python
   @router.get("/content/chaupai", response_model=List[ChauPaiOut])
   def list_chaupais(...): ...
   
   @router.get("/content/chaupai/{id}/navigation", response_model=ChauPaiNavigationOut)
   def get_chaupai_navigation(...): ...
   ```

4. **Create frontend page** (ASTRO)
   ```astro
   // /chaupai/[id].astro
   import NavigationControls from "../components/content/NavigationControls.svelte";
   ```

5. **Extend EngagementKPI** (optional, already supports via content_type)

### 6.2 Universal NavigationControls Component

`NavigationControls.svelte` is a universal frontend component intended for all content detail pages (`doha`, `dictionary`, `idiom`, `article`).

Current behavior:
- Fully active for Doha pages where navigation payloads are available.
- Conditionally mounted on Dictionary/Idiom/Article pages, but remains dormant until navigation payloads are returned by API.

Dependency:
- Full non-Doha activation depends on [LOGICAL-003] (navigation API coverage for Dictionary/Idiom/Article).

Component contract:
- Supports `previousId`/`nextId` and optional `previousHref`/`nextHref` for type-agnostic routing.
- Parent pages should render only when previous/next navigation targets are present.

---

## Conclusion

This architecture achieves:
- ✅ **Strict hierarchical integrity** via FK constraints
- ✅ **Polymorphic content** via cross-reference fields
- ✅ **Efficient sequencing** via (chapter_id, number_in_chapter) queries
- ✅ **Unified engagement** via normalized EngagementKPI table
- ✅ **Audit trails** via moderation_logs and content_versions
- ✅ **Deterministic ordering** via fallback chains
- ✅ **Schema safety** via migrations + testing

**Next Steps**: See Issues.md for current gaps and remediation roadmap.
