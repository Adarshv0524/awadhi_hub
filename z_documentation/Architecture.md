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

### 2.1 Chapter Content Navigation: Prev/Current/Next

**Problem**: Users reading chapter-linked content need deterministic next/previous traversal without returning to chapter listings.

**Solution**: Linked-list-style sequencing without explicit prev/next pointers. The backend uses a generic navigation service that queries adjacent entries by **(chapter_id, number_in_chapter)** with ordered fallbacks.

#### Implementation: `get_content_navigation()`

Location: `backend/app/services/content_service.py`

```python
def get_content_navigation(db: Session, content_type: str, content_id: int) -> ContentNavigationOut:
    """
    Return prev/current/next cards within the same chapter for a supported content type.
    
    Ordering strategy (deterministic, non-shuffling):
    1. Primary: number_in_chapter (handles gapped sequences)
    2. Secondary: created_at (fallback for unordered entries)
    3. Tertiary: id (final tiebreaker)
    """
    # Resolve current model by content_type and load active record
    model_class = _get_model_class(content_type)
    current = _apply_active_content_filters(
        db.query(model_class),
        model_class,
    ).filter(model_class.id == content_id).first()
    
    if not current:
        raise HTTPException(404, "Content not found")

    # Find previous: largest number_in_chapter < current.number_in_chapter
    if current.number_in_chapter is not None:
        previous = (_apply_active_content_filters(db.query(model_class), model_class)
            .filter(
                model_class.chapter_id == current.chapter_id,
                model_class.number_in_chapter < current.number_in_chapter,
            )
            .order_by(
                model_class.number_in_chapter.desc(),
                model_class.created_at.desc(),
                model_class.id.desc(),
            )
            .first()
        )
    
    # Find next: smallest number_in_chapter > current.number_in_chapter
    if current.number_in_chapter is not None:
        next_item = (_apply_active_content_filters(db.query(model_class), model_class)
            .filter(
                model_class.chapter_id == current.chapter_id,
                model_class.number_in_chapter > current.number_in_chapter,
            )
            .order_by(
                model_class.number_in_chapter.asc(),
                model_class.created_at.asc(),
                model_class.id.asc(),
            )
            .first()
        )
    else:
        # Fallback: use created_at for unordered entries
        previous = (_apply_active_content_filters(db.query(model_class), model_class)
            .filter(
                model_class.chapter_id == current.chapter_id,
                model_class.created_at < current.created_at,
            )
            .order_by(model_class.created_at.desc(), model_class.id.desc())
            .first()
        )
        next_item = (_apply_active_content_filters(db.query(model_class), model_class)
            .filter(
                model_class.chapter_id == current.chapter_id,
                model_class.created_at > current.created_at,
            )
            .order_by(model_class.created_at.asc(), model_class.id.asc())
            .first()
        )
    
    return ContentNavigationOut(
        previous=_to_card(previous) if previous else None,
        current=_to_card(current),
        next=_to_card(next_item) if next_item else None,
    )
```

#### Response Schema

```python
class ContentNavCard(BaseModel):
    id: int
    number_in_chapter: Optional[int]
    content_type: Optional[str] = None
    title: Optional[str] = None
    short_text: str

class ContentNavigationOut(BaseModel):
    previous: Optional[ContentNavCard] = None
    current: ContentNavCard
    next: Optional[ContentNavCard] = None
```

#### Endpoint

```python
@router.get("/doha/{doha_id}/navigation", response_model=ContentNavigationOut)
def get_doha_navigation_endpoint(doha_id: int, db: Session = Depends(get_db)):
    return get_content_navigation(db, content_type="doha", content_id=doha_id)

@router.get("/dictionary/{entry_id}/navigation", response_model=ContentNavigationOut)
def get_dictionary_navigation_endpoint(entry_id: int, db: Session = Depends(get_db)):
    return get_content_navigation(db, content_type="dictionary", content_id=entry_id)

@router.get("/idiom/{entry_id}/navigation", response_model=ContentNavigationOut)
def get_idiom_navigation_endpoint(entry_id: int, db: Session = Depends(get_db)):
    return get_content_navigation(db, content_type="idiom", content_id=entry_id)

@router.get("/article/{entry_id}/navigation", response_model=ContentNavigationOut)
def get_article_navigation_endpoint(entry_id: int, db: Session = Depends(get_db)):
    return get_content_navigation(db, content_type="article", content_id=entry_id)
```

#### Frontend Integration

Files:
- `frontend/src/pages/doha/[id].astro`
- `frontend/src/pages/dictionary/[id].astro`
- `frontend/src/pages/idioms/[id].astro`
- `frontend/src/pages/articles/[id].astro`

```astro
let navigation = null;

try {
    navigation = await api(`/content/dictionary/${id}/navigation`);
} catch (navErr) {
    console.warn("[Detail] Navigation fetch failed:", navErr);
}
```

Then rendered via:

```astro
<NavigationControls 
  previousId={navigation?.previous?.id}
  nextId={navigation?.next?.id}
    previousContentType={navigation?.previous?.content_type}
    nextContentType={navigation?.next?.content_type}
    previousKind="Definition"
    nextKind="Definition"
  previousText={navigation?.previous?.short_text}
  nextText={navigation?.next?.short_text}
/>
```

#### Handling Edge Cases

1. **No Previous/Next**: Buttons disabled, visually grayed out (CSS class `opacity-50`)
2. **Gapped Numbering**: If chapter has sparse numbering [1, 3, 5, 10], queries find nearest ordered neighbor
3. **Unordered Content**: Fallback to created_at ensures deterministic sequencing even without number_in_chapter
4. **Deleted/Inactive**: Filter excludes is_deleted=True, status != "active"

#### Performance Considerations

- Index on `(chapter_id, number_in_chapter)` added in migration 0015
- Two-query pattern (one per direction) is acceptable for <100 items per chapter
- For very large chapters (1000+ entries), consider pagination-based navigation

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

### 3.2 Interaction System API Parity (Likes + Bookmarks)

Both likes and bookmarks now have bi-directional API support for create/read/delete semantics.

Implemented endpoints:
- `POST /interactions/toggle`:
    - Create: toggling a missing interaction creates an active row.
    - Delete: toggling an active interaction marks it inactive (`is_active = false`) and removes it from list views.
- `GET /interactions/users/{user_id}/bookmarks`:
    - Paginated user bookmark retrieval with content previews.
- `GET /interactions/users/{user_id}/likes`:
    - Paginated user like retrieval with content previews.

Access control:
- Retrieval endpoints are owner-or-admin only.

Dashboard parity:
- User dashboard renders both Bookmarks and Likes tabs from dedicated APIs with pagination (`offset`/`limit`) and active-only filtering.

Integrity guarantee:
- Un-liking content sets `is_active = false` and it no longer appears in dashboard likes lists.

### 3.3 User & Social System: Public Stats Aggregation

Public profile analytics are exposed through:

- `GET /users/{username}/stats`

Response contract (`UserStatsOut`):

```python
class UserStatsOut(BaseModel):
     username: str
     contributions_count: int
     likes_received: int
     most_liked_content_id: Optional[int]
     average_engagement_score: float
     joined_date: datetime
```

Aggregation rules:

1. `contributions_count`:
    - Count `submissions` where `contributor_id` matches the user, `status == "approved"`, and `is_deleted == False`.
2. `likes_received`:
    - Build a polymorphic union of canonical content rows (`doha`, `dictionary`, `idiom`, `article`) linked through `source_submission_id` to this contributor's approved/public submissions.
    - Left join `engagement_kpis` on `(content_type, content_id)` and compute `SUM(likes_count)`.
3. `average_engagement_score`:
    - On the same KPI join, compute `AVG(weight_score)` and default to `0.0` if empty.
4. `most_liked_content_id`:
    - Order joined rows by `likes_count DESC`, then `content_id ASC`; return the top `content_id`, else `null`.

Privacy contract:

- Endpoint is public (no auth required) for profile visibility.
- No private identity fields are returned (email, password hash, tokens, moderation data).
- Draft/rejected/deleted submissions are excluded from contribution counts.
- KPI rollups for public profiles are computed from approved/public canonical contributions.

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

### 4.3 Database Integrity Guardrail (CI Enforced)

The repository now includes a schema contract guardrail that blocks merges when ORM metadata and migration-produced schema diverge.

Implementation:
- `backend/scripts/schema_contract_check.py`
- CI step: `Schema Contract Check` in `.github/workflows/test.yml`

Contract scope:
1. Build expected schema from `app.db.models.Base.metadata`
2. Apply `alembic upgrade head` to a temporary SQLite database
3. Inspect physical schema with SQLAlchemy inspector
4. Compare table/column presence, normalized type affinity, and nullability
5. Fail with a detailed diff and non-zero exit status on mismatch

### 4.4 Lessons Learned from DATA-001

Historical schema drift caused runtime faults when model and migration column names diverged (`references` vs `external_references`, `key` vs `setting_key`).

Permanent safeguards now in place:
1. **Pre-migration Testing**: Migration smoke checks against a clean database
2. **Schema Contract Validation**: CI-enforced metadata-vs-migration comparison
3. **Regression Documentation**: Drift incidents archived in architecture/changelog context

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

### 5.2 Moderator Inline Metadata Editing (LOGICAL-001 Resolved)

The submission update flow now supports moderator/admin inline correction of hierarchy metadata without forcing contributor rejection loops.

Implemented in `backend/app/api/v1/submissions.py`:
- `SubmissionUpdateIn` includes `author_slug`, `work_slug`, `chapter_slug`, `number_in_chapter`, and `is_classical`.
- Metadata writes are role-gated: only moderator/admin can edit hierarchy fields.
- Contributor edits remain limited to allowed statuses (`draft`, `rejected`) and non-metadata fields.
- Hierarchy references are revalidated against `ClassicalAuthor`, `ClassicalWork`, and `WorkChapter` before commit.
- Update endpoint returns detailed payload (`SubmissionDetailOut`) including timestamps for moderation UI refresh.

Verified behavior:
- Moderator can update `number_in_chapter`/slugs for pending submissions.
- Regular users receive 403 when attempting hierarchy metadata edits.
- Regular text-only edits continue to work for eligible contributor-owned submissions.

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
    import NavigationControls from "../components/navigation/NavigationControls.svelte";
   ```

5. **Extend EngagementKPI** (optional, already supports via content_type)

### 6.2 Universal NavigationControls Component

`NavigationControls.svelte` is a universal frontend component intended for all content detail pages (`doha`, `dictionary`, `idiom`, `article`).

Frontend Component Library classification:
- **Global Content Component**: `frontend/src/components/navigation/NavigationControls.svelte`
- Purpose: Consistent previous/next navigation UX across all chapter-linked content detail routes.
- UX contract: Type-aware route resolution plus contextual labels such as "Next Definition" and "Next Article".

Current behavior:
- Active for all content detail pages that can resolve chapter-linked navigation payloads.
- For content records without hierarchy linkage (for example article rows without `chapter_id`), navigation endpoints intentionally return not found and UI should keep controls hidden.

Component contract:
- Supports `previousId`/`nextId` and optional `previousHref`/`nextHref` for type-agnostic routing.
- Parent pages should render only when previous/next navigation targets are present.

### 6.3 Future Scalability & Optimizations

This section archives low-priority optimization ideas that are currently not justified by observed latency.

#### [OPTIMIZATION-001] Chapter Page Fallbacks

Archived assessment:
- Current chapter route `frontend/src/pages/[author]/[work]/[chapter].astro` already uses `GET /content/by-path/{author}/{work}/{chapter}/dohas`.
- Chapter fetch path is stable in runtime checks and remains under 100ms in local profiling.
- The previously proposed `GET /content/by-path-bulk/{author}/{work}/{chapter}` endpoint would duplicate existing behavior without measurable gain at current load.

Measured baseline (local, 5 runs):
- `GET /content/by-path/tulsidas/ramcharitmanas/baal-kaand/dohas?offset=0&limit=100`: ~5-6ms median

Decision:
- **Archive for Future**.
- Reconsider only when chapter traffic or chapter size trends make hierarchy resolution a confirmed bottleneck.

#### [OPTIMIZATION-002] Eager Loading Navigation

Archived assessment:
- Current Doha detail page uses two calls:
    1. `GET /content/doha/{id}`
    2. `GET /content/doha/{id}/navigation`
- This separation keeps list payloads lean and avoids adding navigation objects to non-detail responses.
- A detail-only schema (`DohaDetailOut` extends `DohaOut` with optional `navigation`) remains the preferred future design if/when a single-round-trip path is needed.

Measured baseline (local, 5 runs):
- `GET /content/doha/4`: ~3-4ms median
- `GET /content/doha/4/navigation`: ~4-6ms median

Decision:
- **Archive for Future**.
- Implement only when end-to-end page metrics show navigation call overhead is material in production latency budgets.

Operational note:
- If implemented later, use `DohaDetailOut` only on detail endpoints so `GET /content/doha` list/search payloads remain compact.

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
