# Issues Log: Categorized by Type

**Document Purpose**: GitHub-style issue tracking for bugs, feature gaps, and architectural improvements  
**Last Audit**: March 26, 2026  
**Format**: Severity + Type + Reproducible Status + Mitigation Status  

---

## Legend

### Severity Levels
- **CRITICAL**: Blocks core functionality; causes 500 errors or data loss
- **HIGH**: Impacts user experience or feature completeness; 400/403/404 responses
- **MEDIUM**: Workaround exists; affects polish or non-critical features
- **LOW**: Nice-to-have optimizations; accepts minor inefficiency

### Issue Types
1. **WIRING** – Backend-Frontend contract mismatch (missing data, schema gaps)
2. **STYLING** – UI/UX presentation (visual feedback, layout, responsive issues)
3. **DATA STRUCTURE** – Schema/model alignment, drift, or design debt
4. **OPTIMIZATION** – Query performance, caching, N+1, unnecessary round-trips
5. **LOGICAL FLOW** – Feature completeness, workflow gaps, missing endpoints

### Resolution Status
- 🔴 **NOT STARTED**
- 🟡 **IN PROGRESS**
- 🟢 **RESOLVED** (✅ included in migration or code)

---

## 1. WIRING ISSUES (Backend-Frontend Contract)

## 2. STYLING ISSUES (UI/UX Presentation)

### [STYLING-003] Navigation Controls Not Shown for Non-Hierarchical Content

**Severity**: LOW  
**Impact**: Users of Dictionary/Idiom/Article cannot sequence-navigate  
**Status**: 🟡 BLOCKED BY [LOGICAL-003]  

#### Problem

NavigationControls component only shown for Doha:

```astro
{doha && (
  <NavigationControls
    previousId={navigation?.previous?.id}
    nextId={navigation?.next?.id}
  />
)}
```

Dictionary, Idiom, and Article pages have no sequence navigation.

#### Resolution

Blocked by [LOGICAL-003]: Navigation API not yet implemented for other content types.

---

## 3. DATA STRUCTURE ISSUES (Schema Alignment & Design)

---

## 4. OPTIMIZATION ISSUES (Query & Performance)

### [OPTIMIZATION-001] Chapter Page Uses Fallback Search Instead of Direct Endpoint

**Severity**: MEDIUM  
**Impact**: Extra API round-trip; potential ordering inconsistency  
**Status**: 🔴 NOT STARTED  

#### Problem

File: `frontend/src/pages/[author]/[work]/[chapter].astro`

```javascript
const chapterDohasBase = `/content/by-path/${encodedPath}/dohas`;

// First fetch succeeds (path-based)
async function fetchAllChapterDohas() {
  let offset = 0;
  const merged = [];
  
  while (true) {
    // Makes TWO API calls per page
    const res = await api(`${chapterDohasBase}?offset=${offset}&limit=${pageSize}`);
    // ...then fallback to search if needed
    if (!res.items) {
      const fallback = await api(`/search?author=...&work=...&chapter=...`);
    }
  }
}
```

#### Current Endpoints

- ✅ `/content/by-path/{author_slug}/{work_slug}/{chapter_slug}/dohas` – works fine
- ✅ `/content/chapters/{chapter_id}/dohas` – by ID instead of by slug
- ❌ No slug-based chapter ID lookup to avoid triple-join

#### Why Fallback Exists

Fallback is defensive: if hierarchy lookup fails, search provides a recovery path. But this is unnecessary if dedicated endpoint is always available.

#### Fix (Optional, Low Priority)

Frontend could prefer `/content/chapters/{id}/dohas` if chapter page pre-resolves to ID:

```astro
// Resolve ID once
const chapterId = await resolveChapterIdFromSlug(author, work, chapter);
// Then use efficient ID-based endpoint
const data = await api(`/content/chapters/${chapterId}/dohas`);
```

Or backend could add a faster endpoint:

```python
@router.get("/by-path-bulk/{author_slug}/{work_slug}/{chapter_slug}/dohas", 
            response_model=ChapterDohasOut)
def list_chapter_dohas_bulk_by_path(...):
    """Optimized: cache hierarchy resolution."""
    # Could cache author/work/chapter lookups if hit frequently
```

#### Effort
- Minimal; would not measurably improve performance unless chapter pages scale to 1000+ DAU

#### Priority
**LOW** – Current implementation is acceptable.

---

### [OPTIMIZATION-002] Navigation Requires Separate API Call

**Severity**: LOW  
**Impact**: Two API calls to load doha page (one for content, one for nav)  
**Status**: 🔴 Not started (acceptable for now)  

#### Problem

File: `frontend/src/pages/doha/[id].astro`

```astro
doha = await api(`/content/doha/${id}`);
navigation = await api(`/content/doha/${id}/navigation`);  // Second call
```

#### Alternative (Eager Loading)

Backend could include navigation in `/content/doha/{id}` response:

```python
class DohaOutWithNav(BaseModel):
    # ... all DohaOut fields ...
    navigation: Optional[DohaNavigationOut] = None
```

With query:

```python
# Fetch all 3 dohas in one query with UNION
prev_next = get_doha_navigation(db, doha_id)
doha_response = DohaOutWithNav(
    **doha_dict,
    navigation=prev_next
)
```

#### Tradeoff

- **Pro**: Saves 1 API call; better lighthouse score
- **Con**: Larger response payload; `/content/doha` list endpoint would bloat

#### Current Choice

Current two-call pattern is acceptable:
- Separation of concerns (content vs navigation)
- Each call is < 50ms
- Cacheable separately

#### Priority
**LOW** – Optimization, not requirement.

---

## 5. LOGICAL FLOW ISSUES (Feature Completeness)

### [LOGICAL-001] Moderator Inline Edit Cannot Update Hierarchy Metadata

**Severity**: HIGH  
**Impact**: Moderators must reject submissions to correct hierarchy metadata; creates unnecessary rejection loops  
**Status**: 🔴 NOT STARTED  

#### Problem

SubmissionUpdateIn schema prevents metadata field updates:

```python
# backend/app/api/v1/submissions.py
class SubmissionUpdateIn(BaseModel):
    main_text: Optional[str]
    meaning: Optional[str]
    # ❌ MISSING: author_slug, work_slug, chapter_slug, number_in_chapter, is_classical
```

Moderator workflow:
1. Submission arrives with wrong chapter_slug
2. Moderator reviews, sees error but CANNOT fix inline
3. Moderator clicks "Reject" to send feedback
4. User resubmits with correct chapter_slug
5. Loop repeats

#### Expected Workflow

1. Submission arrives with wrong metadata
2. Moderator corrects inline: chapter_slug from "wrong-kand" to "ayodhya-kand"
3. Moderator clicks "Approve"
4. Canonical entry created with corrected hierarchy

#### Fix

**Backend** (`backend/app/api/v1/submissions.py`):

```python
class SubmissionUpdateIn(BaseModel):
    main_text: Optional[str] = None
    meaning: Optional[str] = None
    # ✅ NEW: Allow moderator to correct hierarchy metadata
    author_slug: Optional[str] = None
    work_slug: Optional[str] = None
    chapter_slug: Optional[str] = None
    number_in_chapter: Optional[int] = None
    is_classical: Optional[bool] = None

@router.put("/submissions/{submission_id}")
def update_submission(submission_id: int, payload: SubmissionUpdateIn, 
                     current_user: User = Depends(require_auth)):
    """Moderator ONLY can update hierarchy metadata."""
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    
    # Moderator role check
    if current_user.role not in ["moderator", "admin"]:
        # Non-moderators can only update their own draft submissions
        if submission.contributor_id != current_user.id or submission.status != "draft":
            raise HTTPException(403, "Cannot edit this submission")
    
    # Moderators can update metadata + content
    if current_user.role in ["moderator", "admin"] and payload.author_slug:
        # Validate hierarchy references
        author = db.query(ClassicalAuthor).filter(
            ClassicalAuthor.slug == payload.author_slug
        ).first()
        if not author:
            raise HTTPException(400, "Invalid author_slug")
        # ... validate work, chapter similarly
        
        # Re-run classical validation after metadata update
        is_valid, errors, reason = classical_submission_validation.validate(
            db, submission.main_text, payload
        )
        if not is_valid:
            raise HTTPException(400, f"Validation failed: {reason}")
    
    # Update submission
    if payload.main_text:
        submission.main_text = payload.main_text
    if payload.meaning:
        submission.meaning = payload.meaning
    if current_user.role in ["moderator", "admin"]:
        if payload.author_slug:
            submission.author_slug = payload.author_slug
        if payload.work_slug:
            submission.work_slug = payload.work_slug
        if payload.chapter_slug:
            submission.chapter_slug = payload.chapter_slug
        if payload.number_in_chapter is not None:
            submission.number_in_chapter = payload.number_in_chapter
        if payload.is_classical is not None:
            submission.is_classical = payload.is_classical
    
    submission.updated_at = func.now()
    db.commit()
    return SubmissionDetailOut.from_orm(submission)
```

#### Effort
- Backend: 3 hours (schema, validation, auth checks)
- Frontend: 1 hour (expose fields in moderation UI)
- Testing: 2 hours

#### Priority
**HIGH** – Blocks moderation workflow efficiency.

---

### [LOGICAL-002] Missing Likes Endpoint for User Dashboard

**Severity**: HIGH  
**Impact**: Dashboard likes tab is placeholder; breaks feature parity with bookmarks  
**Status**: 🔴 NOT STARTED  

#### Problem

Backend has bookmarks endpoint but no likes endpoint:

```python
# ✅ Exists
@router.get("/interactions/users/{user_id}/bookmarks")
def get_user_bookmarks(user_id: int, ...):
    pass

# ❌ Missing
@router.get("/interactions/users/{user_id}/likes")
def get_user_likes(user_id: int, ...):
    # Should return paginated user's liked content
    pass
```

Frontend has placeholder:

```svelte
<!-- frontend/src/components/dashboard/DashboardClient.svelte -->
{#if tab === 'likes'}
  <p>TODO: Implement likes endpoint</p>  <!-- ❌ -->
{:else if tab === 'bookmarks'}
  <!-- Works fine -->
{/if}
```

#### Database Support

Data exists in `user_interactions`:

```
user_id: 42
content_type: "doha"
content_id: 123
interaction_type: "like"  # ← exists and is active
```

#### Fix

**Backend** (`backend/app/api/v1/interactions.py`):

```python
class UserLikeOut(BaseModel):
    id: int
    content_id: int
    content_type: str
    content_title: str
    content_snippet: str
    created_at: datetime

@router.get("/interactions/users/{user_id}/likes", response_model=List[UserLikeOut])
def get_user_likes(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_auth),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    """Return user's liked content (only owner or admin can view)."""
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(403, "Cannot access other user's likes")
    
    # Query likes
    likes = (
        db.query(
            UserInteraction,
            DohaEntry.main_text,  # content preview
            # ... handle other content types
        )
        .filter(
            UserInteraction.user_id == user_id,
            UserInteraction.interaction_type == "like",
            UserInteraction.is_active == True,
        )
        .outerjoin(DohaEntry, ...)
        .order_by(UserInteraction.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    
    return [
        UserLikeOut(
            id=ui.UserInteraction.id,
            content_id=ui.UserInteraction.content_id,
            content_type=ui.UserInteraction.content_type,
            content_title=...,  # extract from joined table
            content_snippet=...,
            created_at=ui.UserInteraction.created_at,
        )
        for ui in likes
    ]
```

#### Effort
- Backend: 2 hours
- Frontend: 0.5 hour (render list)
- Testing: 1 hour

#### Priority
**HIGH** – Feature parity with bookmarks.

---

### [LOGICAL-003] Content Navigation API Only Implemented for Doha

**Severity**: MEDIUM  
**Impact**: Dictionary/Idiom/Article pages cannot sequence-navigate  
**Status**: 🔴 NOT STARTED  

#### Problem

Verse navigation exists:

```python
@router.get("/content/doha/{doha_id}/navigation")  # ✅ Works
```

But no equivalent for other content types:

```python
# ❌ Missing
@router.get("/content/dictionary/{id}/navigation")
@router.get("/content/idiom/{id}/navigation")
@router.get("/content/article/{id}/navigation")
```

#### Why It Matters

Dictionary entries within a chapter should support next/prev navigation, just like verses. E.g., Ramcharitmanas Ayodhya Kand contains both verses and definitions, and both should be sequenceable.

#### Fix

**Backend** (`backend/app/services/content_service.py`):

```python
def get_content_navigation(db: Session, content_type: str, content_id: int):
    """Generic navigation for any content type with hierarchy linking."""
    
    # Get current content
    if content_type == "doha":
        current = db.query(DohaEntry).filter(DohaEntry.id == content_id).first()
    elif content_type == "dictionary":
        current = db.query(DictionaryEntry).filter(DictionaryEntry.id == content_id).first()
    elif content_type == "idiom":
        current = db.query(IdiomEntry).filter(IdiomEntry.id == content_id).first()
    elif content_type == "article":
        current = db.query(ArticleEntry).filter(ArticleEntry.id == content_id).first()
    else:
        raise HTTPException(400, f"Unknown content_type: {content_type}")
    
    if not current or current.chapter_id is None:
        raise HTTPException(404, "Content not found or not hierarchical")
    
    # Generic prev/next logic (same as doha)
    if current.number_in_chapter is not None:
        previous = db.query(
            _get_model_class(content_type)  # dynamic model selection
        ).filter(
            _get_model_class(content_type).chapter_id == current.chapter_id,
            _get_model_class(content_type).number_in_chapter < current.number_in_chapter,
            _get_model_class(content_type).is_deleted == False,
            _get_model_class(content_type).status == "active",
        ).order_by(
            _get_model_class(content_type).number_in_chapter.desc(),
            _get_model_class(content_type).created_at.desc(),
            _get_model_class(content_type).id.desc(),
        ).first()
        
        next_item = db.query(
            _get_model_class(content_type)
        ).filter(
            _get_model_class(content_type).chapter_id == current.chapter_id,
            _get_model_class(content_type).number_in_chapter > current.number_in_chapter,
            _get_model_class(content_type).is_deleted == False,
            _get_model_class(content_type).status == "active",
        ).order_by(
            _get_model_class(content_type).number_in_chapter.asc(),
            _get_model_class(content_type).created_at.asc(),
            _get_model_class(content_type).id.asc(),
        ).first()
    # ... fallback for unordered content
    
    return ContentNavigationOut(previous=..., current=..., next=...)
```

**API Endpoints** (`backend/app/api/v1/content.py`):

```python
@router.get("/dictionary/{entry_id}/navigation", response_model=ContentNavigationOut)
@router.get("/idiom/{entry_id}/navigation", response_model=ContentNavigationOut)
@router.get("/article/{entry_id}/navigation", response_model=ContentNavigationOut)
def get_content_navigation(content_type: str, entry_id: int, ...):
    """Generic navigation endpoint for all content types."""
    return get_content_navigation(db, content_type, entry_id)
```

#### Effort
- Backend: 4 hours (generic function + endpoints for 3 types)
- Frontend: 1 hour (import navigation on dict/idiom/article pages)
- Testing: 2 hours

#### Priority
**MEDIUM** – Nice-to-have; doha sequencing is priority.

---

### [LOGICAL-004] Missing Public User Stats Endpoint

**Severity**: HIGH  
**Impact**: Public profiles cannot show real contribution stats; blocks profile page feature  
**Status**: 🔴 NOT STARTED  

#### Problem

Backend has user profile endpoint:

```python
@router.get("/users/{username}")  # ✅ Basic profile
```

But no stats endpoint:

```python
@router.get("/users/{username}/stats")  # ❌ Missing
```

Spec documented but unimplemented (see `z_documentation/BACKEND_TODO_user_stats.md`).

#### Frontend Impact

File: `frontend/src/pages/users/[username].astro`

```astro
<div class="user-stats">
  <p>Contributions: {stats?.contributions_count ?? 0}</p>
  <p>Likes Received: {stats?.likes_received ?? 0}</p>
  <!-- All zeros because endpoint missing -->
</div>
```

#### Fix

**Backend** (`backend/app/api/v1/users.py`):

```python
class UserStatsOut(BaseModel):
    username: str
    contributions_count: int              # approved submissions
    likes_received: int                   # sum of likes on user's approved content
    most_liked_content_id: Optional[int]  # top piece by engagement
    most_liked_content_type: Optional[str]
    average_engagement_score: float       # mean weight_score across user's submissions
    joined_date: datetime

@router.get("/users/{username}/stats", response_model=UserStatsOut)
def get_user_stats(username: str, db: Session = Depends(get_db)):
    """Public stats for user profile."""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(404, "User not found")
    
    # Count approved submissions (across all content types)
    contribution_count = (
        db.query(func.count(Submission.id))
        .filter(
            Submission.contributor_id == user.id,
            Submission.status == "approved",
            Submission.is_deleted == False,
        )
        .scalar()
    )
    
    # Likes received on user's content
    likes_received = (
        db.query(func.sum(EngagementKPI.likes_count))
        .join(
            Submission,
            and_(
                Submission.contributor_id == user.id,
                # This join is tricky; requires mapping submissions to canonical entries
            )
        )
        .scalar() or 0
    )
    
    # Average weight_score across user's entries
    avg_score = (
        db.query(func.avg(EngagementKPI.weight_score))
        .join(Submission, ...)
        .scalar() or 0.0
    )
    
    return UserStatsOut(
        username=user.username,
        contributions_count=contribution_count,
        likes_received=likes_received,
        average_engagement_score=avg_score,
        joined_date=user.created_at,
    )
```

#### Effort
- Backend: 3 hours (complex joins, null handling)
- Frontend: 0.5 hour (display stats)
- Testing: 1.5 hours

#### Priority
**HIGH** – Required for public profile page.

---

## Summary Table

| Issue ID | Severity | Type | Status | Effort |
|----------|----------|------|--------|--------|
| STYLING-003 | LOW | Styling | 🟡 | Blocked by LOGICAL-003 |
| OPTIMIZATION-001 | MEDIUM | Optimization | 🔴 | 0.5h |
| OPTIMIZATION-002 | LOW | Optimization | 🔴 | N/A |
| LOGICAL-001 | HIGH | Logical | 🔴 | 6h |
| LOGICAL-002 | HIGH | Logical | 🔴 | 3.5h |
| LOGICAL-003 | MEDIUM | Logical | 🔴 | 7h |
| LOGICAL-004 | HIGH | Logical | 🔴 | 4.5h |

### Critical Path (Highest Priority)

1. **LOGICAL-001** (6h) – Moderator metadata editing
2. **LOGICAL-002** (3.5h) – Likes endpoint
3. **LOGICAL-004** (4.5h) – User stats endpoint

**Estimated Total**: ~10 hours (≈1.25 dev days)

---

## References

- `README.md` – Quick introduction and current status
- `Architecture.md` – System design and content delivery logic
- `BACKEND_TODO_user_stats.md` – Original user stats spec
- `BACKEND_ISSUE_moderator_inline_editing_metadata.md` – Moderation workflow details
- `IMPLEMENTATION_GAPS.md` – Historical gap documentation
