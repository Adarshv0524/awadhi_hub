# Module Audits & Component Analysis

**Document Purpose**: Per-module implementation breakdown and technical details (REFERENCE ONLY)  
**Last Updated**: March 26, 2026  

⚠️ **IMPORTANT**: For current project status and issue tracking, see [../issues/Issues.md](../issues/Issues.md). This document provides technical reference details only and should not be considered the authoritative status source.

---


## Module 1: Authentication & Authorization

**Status**: ✅ **COMPLETE**

### What Works

- ✅ JWT token generation and validation
- ✅ Email/password registration and login
- ✅ OAuth Google integration (backend)
- ✅ Refresh token rotation
- ✅ Role-based access control (registered, moderator, admin)
- ✅ Database-backed rate limiting
- ✅ Session timeout enforcement

### Implementation Details

**File**: `backend/app/api/v1/auth.py`

```python
# JWT generation with expiry
def create_access_token(user_id, role, expires_in=3600):
    payload = {
        "sub": str(user_id),
        "role": role,
        "exp": datetime.utcnow() + timedelta(seconds=expires_in)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

# Rate limiting: 5 login attempts per hour per IP
rate_limit_check(action="login", user_id=None, ip_address=client_ip)
```

### Gaps

- ⚠️ **OAuth frontend trigger missing**: Backend endpoint exists, but login page doesn't show Google button
  - See [WIRING-003] in Issues.md

---

## Module 2: Hierarchy Management

**Status**: ✅ **COMPLETE**

### What Works

- ✅ Authors CRUD (public browse, admin create/update)
- ✅ Works CRUD with FK to author
- ✅ Chapters CRUD with FK to work
- ✅ Unique constraint enforcement: (author_id, work_slug), (work_id, chapter_slug)
- ✅ Soft-delete via is_deleted flag
- ✅ Slug-based URL routing

### Implementation Details

**File**: `backend/app/db/models.py`

```python
class ClassicalAuthor(Base):
    __tablename__ = "classical_authors"
    slug = Column(String(150), unique=True, index=True)
    is_deleted = Column(Boolean, default=False)

class ClassicalWork(Base):
    __table_args__ = (
        UniqueConstraint("author_id", "slug"),  # Composite unique
    )

class WorkChapter(Base):
    __table_args__ = (
        UniqueConstraint("work_id", "slug"),
        UniqueConstraint("work_id", "number"),  # Enforce ordering
    )
```

### Test Coverage

**File**: `backend/tests/test_hierarchy.py`

- ✅ CRUD operations
- ✅ Duplicate slug prevention
- ✅ Cascading deletes via is_deleted
- ✅ Slug URL routing

### Gaps

None. Module fully functional.

---

## Module 3: Canonical Content (Doha)

**Status**: ✅ **MOSTLY COMPLETE** (95%)

### What Works

- ✅ DohaEntry creation with hierarchy linking
- ✅ Prev/next navigation via `get_doha_navigation()`
- ✅ Chapter-ordered listing
- ✅ Version history tracking
- ✅ Full-text search
- ✅ Soft-delete + status machine (draft/active/archived)

### Implementation Details

**File**: `backend/app/db/models.py`

```python
class DohaEntry(Base):
    __tablename__ = "doha_entries"
    hierarchy_path = Column(String(512), index=True)
    author_id = Column(Integer, index=True)
    work_id = Column(Integer, index=True)
    chapter_id = Column(Integer, index=True)
    number_in_chapter = Column(Integer)  # For sequencing
    main_text = Column(Text)
    text_devanagari = Column(Text)
    text_romanized = Column(Text)  # For search normalization
```

**File**: `backend/app/api/v1/content.py`

```python
@router.get("/doha/{doha_id}/navigation")
def get_doha_navigation_endpoint(doha_id: int, ...):
    """Return prev/current/next navigation cards."""
    return get_doha_navigation(db, doha_id)
```

### Test Coverage

**File**: `backend/tests/test_canonical_doha.py`

```python
def test_doha_navigation_returns_prev_current_next(client, db):
    # Create author/work/chapter/dohas
    # Query navigation endpoint
    # Assert prev/current/next populated correctly
```

### Gaps

- ⚠️ **Timestamps missing from response schema** (WIRING-002)
- ✅ Navigation extended to dictionary/idiom/article with universal content endpoints

---

## Module 4: Polymorphic Content (Dictionary, Idiom, Article)

**Status**: ⚠️ **MOSTLY COMPLETE** (85%)

### What Works

- ✅ DictionaryEntry, IdiomEntry, ArticleEntry models
- ✅ Hierarchy cross-reference fields (author_id, work_id, chapter_id)
- ✅ List/get/search endpoints
- ✅ Version history support

### What's Missing

- ⚠️ Frontend polish for universal navigation controls across all non-doha detail pages
- ⚠️ Article navigation availability depends on chapter linkage (`chapter_id`)

### Implementation Details

**File**: `backend/app/db/models.py`

```python
class DictionaryEntry(Base):
    lemma_devanagari = Column(String(512), index=True)
    lemma_roman = Column(String(512), index=True)
    # Hierarchy linking
    author_id = Column(Integer, nullable=True)
    work_id = Column(Integer, nullable=True)
    chapter_id = Column(Integer, nullable=True)
    number_in_chapter = Column(Integer, nullable=True)

class IdiomEntry(Base):
    text_devanagari = Column(Text, index=True)
    # Same hierarchy linking pattern
```

### Test Coverage

- ✅ Basic CRUD tested
- ✅ Hierarchy sequencing tests added for doha/dictionary/idiom navigation endpoints

---

## Module 5: Submission & Moderation

**Status**: ⚠️ **MOSTLY COMPLETE** (85%)

### What Works

- ✅ Submission creation with schema validation
- ✅ Status machine: draft → pending_review → approved/rejected
- ✅ Moderator review/approval
- ✅ Batch approval with atomic transactions
- ✅ Classical hierarchy validation
- ✅ Audit log tracking (ModerationLog)

### Implementation Details

**File**: `backend/app/api/v1/submissions.py`

```python
class SubmissionIn(BaseModel):
    content_type: str
    main_text: str
    meaning: Optional[str]
    is_classical: bool
    author_slug: Optional[str]
    work_slug: Optional[str]
    chapter_slug: Optional[str]
    number_in_chapter: Optional[int]

@router.post("/submissions/{submission_id}/approve")
def approve_submission(submission_id: int, ...):
    # Validate
    # Create canonical entry
    # Log moderation action
    # Update submission status
```

### Test Coverage

- ✅ Classical validation (author/work/chapter slug resolution)
- ✅ Batch approval atomicity
- ✅ Status transitions

### Gaps

- ⚠️ **Cannot edit hierarchy metadata inline** (LOGICAL-001)
  - SubmissionUpdateIn excludes author_slug, work_slug, chapter_slug
  - Moderators must reject and ask user to resubmit
  - See Issues.md for detailed fix

---

## Module 6: Engagement & Analytics

**Status**: ⚠️ **INCOMPLETE** (50%)

### What Works

- ✅ EngagementKPI table with unified schema
- ✅ UserInteraction (likes/bookmarks tracking)
- ✅ ShareLog and Report tables
- ✅ Weight score computation
- ✅ Database constraints (UQ on content_type + content_id)

### What's Missing

- ✅ **Engagement metrics returned in content API responses**
    - Doha/Dictionary/Idiom/Article responses now include engagement counters for frontend rendering.

**File**: `backend/app/api/v1/content.py`

```python
class DohaOut(BaseModel):
    id: int
    main_text: str
    meaning: Optional[str]
    # ❌ MISSING: likes_count, views_count, shares_count, bookmarks_count
```

### Test Coverage

- ✅ EngagementKPI storage
- ⚠️ Response serialization NOT tested

---

## Module 7: Search & Recommendations

**Status**: ✅ **COMPLETE**

### What Works

- ✅ Full-text search across all content types
- ✅ Roman + Devanagari script support
- ✅ Text normalization (lemma_roman_norm, text_roman_norm)
- ✅ Hierarchy filtering (author, work, chapter)
- ✅ MySQL FULLTEXT index + SQLite fallback

### Implementation Details

**File**: `backend/app/services/search_service.py`

```python
def search_content(db, query: str, content_type=None, 
                   author=None, work=None, chapter=None, ...):
    # Normalize query (Roman to Devanagari)
    # Build WHERE clause with hierarchy filters
    # Execute FULLTEXT search or SQLite fallback
    # Return ranked results
```

### Test Coverage

- ✅ Search by query
- ✅ Search by hierarchy filters
- ✅ Roman script matching

---

## Module 8: User Interactions

**Status**: ⚠️ **INCOMPLETE** (70%)

### What Works

- ✅ Bookmarks: create, list, delete
- ✅ Likes: create, list, delete
- ✅ UniqueConstraint enforcement

### Notes

- Likes and bookmarks retrieval now share owner/admin access control and active-only filtering behavior.

**File**: `backend/app/api/v1/interactions.py`

```python
@router.get("/interactions/users/{user_id}/bookmarks")  # ✅ Works
def get_user_bookmarks(user_id: int, ...):
    pass

@router.get("/interactions/users/{user_id}/likes")      # ✅ Works
def get_user_likes(user_id: int, ...):
    return {"total_count": ..., "count": ..., "results": [...]} 
```

---

## Module 9: Users & Profiles

**Status**: ✅ **MOSTLY COMPLETE** (90%)

### What Works

- ✅ User registration + login
- ✅ GET /users/{username} (public profile)
- ✅ GET /users/{username}/stats (public contribution metrics)
- ✅ Created_at tracking

### What's Missing

- ⚠️ Frontend visualization polish for richer stats cards

**File**: `backend/app/api/v1/users.py`

```python
@router.get("/users/{username}")      # ✅ Works
def get_user_profile(username: str, ...):
    return UserOut.from_orm(user)

@router.get("/users/{username}/stats") # ✅ Implemented
def get_user_stats(username: str, ...):
    return UserStatsOut(...)
```

---

## Frontend Components Analysis

### Components Status

| Component | File | Status | Issue |
|-----------|------|--------|-------|
| Hierarchy Browsing | `pages/[author]/[work]/[chapter].astro` | ✅ Works | None |
| Doha Page | `pages/doha/[id].astro` | ⚠️ Partial | WIRING-002 |
| Navigation Controls | `components/content/NavigationControls.svelte` | ✅ Works | Only wired for Doha |
| InteractionBar | `components/interaction/InteractionBar.svelte` | ✅ Working | None |
| Dashboard | `components/dashboard/DashboardClient.svelte` | ⚠️ Partial | WIRING/STYLING backlog |

### Navigation Controls

**File**: `frontend/src/components/content/NavigationControls.svelte`

```svelte
<button on:click={() => handleNavigation(previousId)}>
  ← Previous
</button>
```

- ✅ Implemented and styled
- ✅ Works with Doha pages
- ❌ Not extended to other content types

### InteractionBar

**File**: `frontend/src/components/interaction/InteractionBar.svelte`

```svelte
<script>
    export let content;
    let likes = content?.likes_count ?? 0;
    let views = content?.views_count ?? 0;
</script>
```

- ✅ Receives and displays populated engagement values
- ✅ Uses `?? 0` fallback for null/undefined safety

---

## Summary: Module Status Matrix

| Module | Status | Critical Gaps | Effort to Fix |
|--------|--------|----------------|---------------|
| Auth | ✅ Complete | None | 0h |
| Hierarchy | ✅ Complete | None | 0h |
| Doha Content | ✅ ~95% | WIRING-002 | 2h |
| Other Content | ⚠️ ~85% | STYLING-003 | 1h |
| Submissions | ✅ ~95% | None | 0h |
| Engagement | ✅ ~90% | None | 0h |
| Search | ✅ Complete | None | 0h |
| Interactions | ✅ ~90% | None | 0h |
| Users | ✅ ~90% | None | 0h |
| **TOTAL** | **⚠️ ~82%** | **6 issues** | **~10.5h** |

---

See **Issues.md** for detailed problem statements and fix procedures.
