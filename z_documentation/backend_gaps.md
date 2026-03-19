# Backend Specification Gaps & Requirements
**Project:** Awadhi New  
**Date:** December 30, 2025  
**Purpose:** Technical specification for Backend Team to resolve frontend integration issues  
**Status:** 🔴 **CRITICAL - Frontend blocked on 13 backend endpoints**

---

## 🎯 Executive Summary

The frontend is currently operating in **defensive mode** due to missing/incomplete backend response data. This document specifies the exact JSON schema changes required to achieve full frontend-backend synchronization.

### Impact Overview
- **13 endpoints** require schema updates
- **4 new endpoints** needed for dashboard features
- **Estimated frontend completion**: 95% blocked by backend gaps

---

## 📋 MODULE 1: Content API (`/content/doha`)

### Endpoint: `GET /content/doha/{id}`

#### Current JSON Output
```json
{
  "id": 33,
  "main_text": "जो सुख होइ जोग सो, सो सुख पावत आज",
  "meaning": "Whatever happiness is destined, that is received today",
  "text_devanagari": "जो सुख होइ जोग सो, सो सुख पावत आज",
  "text_romanized": "Jo sukh hoi jog so, so sukh paavat aaj",
  "hierarchy_path": "/tulsidas/ramcharitmanas/ayodhyakand",
  "author_id": 5,
  "work_id": 12,
  "chapter_id": 89,
  "number_in_chapter": 15,
  "status": "active",
  "visibility": "public",
  "version": 2,
  "is_canonical": true,
  "confidence_level": 95
}
```

#### Required JSON Output
```json
{
  "id": 33,
  "main_text": "जो सुख होइ जोग सो, सो सुख पावत आज",
  "meaning": "Whatever happiness is destined, that is received today",
  "text_devanagari": "जो सुख होइ जोग सो, सो सुख पावत आज",
  "text_romanized": "Jo sukh hoi jog so, so sukh paavat aaj",
  "hierarchy_path": "/tulsidas/ramcharitmanas/ayodhyakand",
  
  // ✅ ADD: Resolved names from JOINs
  "author_id": 5,
  "author_name": "Tulsidas",
  "work_id": 12,
  "work_name": "Ramcharitmanas",
  "chapter_id": 89,
  "chapter_name": "Ayodhyakand",
  
  "number_in_chapter": 15,
  "status": "active",
  "visibility": "public",
  "version": 2,
  "is_canonical": true,
  "confidence_level": 95,
  
  // ✅ ADD: Timestamps from DohaEntry model
  "created_at": "2024-11-15T10:30:00Z",
  "updated_at": "2024-12-01T14:22:00Z",
  
  // ✅ ADD: Engagement metrics from EngagementKPI relationship
  "likes_count": 42,
  "views_count": 1523,
  "shares_count": 8,
  "bookmarks_count": 17,
  
  // ✅ ADD: Verification/trust data
  "source_reference": "Gita Press Edition, Page 145",
  "verified_by": 3,
  "verified_at": "2024-11-20T09:15:00Z",
  "created_by": 7
}
```

#### Business Justification
| Field | Reason | Impact |
|-------|--------|--------|
| `author_name`, `work_name`, `chapter_name` | **SEO**: Structured data requires names, not IDs | ❌ Google Rich Results broken |
| `created_at`, `updated_at` | **SEO**: `article:published_time` and `article:modified_time` meta tags | ❌ Search engines cannot determine content freshness |
| `likes_count`, `views_count`, `shares_count`, `bookmarks_count` | **UX**: InteractionBar shows engagement metrics | ❌ Always displays 0, misleading users |
| `source_reference`, `verified_by`, `verified_at`, `created_by` | **Trust Signals**: TrustSignals component builds credibility | ❌ Component renders empty |

#### SQL Implementation Hints
```python
# In backend/app/api/v1/content.py
from sqlalchemy.orm import joinedload

doha = db.query(DohaEntry).options(
    joinedload(DohaEntry.author),
    joinedload(DohaEntry.work),
    joinedload(DohaEntry.chapter),
    joinedload(DohaEntry.engagement_kpi)
).filter(DohaEntry.id == doha_id).first()

# Then map to response:
result = DohaOut(
    **doha.__dict__,
    author_name=doha.author.name if doha.author else None,
    work_name=doha.work.name if doha.work else None,
    chapter_name=doha.chapter.name if doha.chapter else None,
    likes_count=doha.engagement_kpi.likes_count if doha.engagement_kpi else 0,
    views_count=doha.engagement_kpi.views_count if doha.engagement_kpi else 0,
    shares_count=doha.engagement_kpi.shares_count if doha.engagement_kpi else 0,
    bookmarks_count=doha.engagement_kpi.bookmarks_count if doha.engagement_kpi else 0
)
```

#### Pydantic Schema Update Required
```python
# backend/app/api/v1/content.py
from datetime import datetime

class DohaOut(BaseModel):
    # Existing fields
    id: int
    hierarchy_path: Optional[str]
    author_id: Optional[int]
    work_id: Optional[int]
    chapter_id: Optional[int]
    number_in_chapter: Optional[int]
    main_text: str
    meaning: Optional[str]
    text_devanagari: Optional[str]
    text_romanized: Optional[str]
    status: str
    visibility: str
    version: int
    is_canonical: bool
    confidence_level: Optional[int]
    
    # ✅ NEW FIELDS
    author_name: Optional[str] = None
    work_name: Optional[str] = None
    chapter_name: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    likes_count: int = 0
    views_count: int = 0
    shares_count: int = 0
    bookmarks_count: int = 0
    source_reference: Optional[str] = None
    verified_by: Optional[int] = None
    verified_at: Optional[datetime] = None
    created_by: Optional[int] = None

    class Config:
        orm_mode = True
```

---

## 📋 MODULE 2: Dictionary API (`/dictionary`)

### Endpoint: `GET /dictionary/{id}`

#### Current JSON Output
```json
{
  "id": 15,
  "lemma_devanagari": "अवधी",
  "lemma_roman": "Awadhi",
  "meaning": "A language spoken in Awadh region",
  "usage_example": "अवधी बोली मीठी है",
  "status": "active",
  "visibility": "public",
  "version": 1,
  "is_canonical": true
}
```

#### Required JSON Output
```json
{
  "id": 15,
  "lemma_devanagari": "अवधी",
  "lemma_roman": "Awadhi",
  "meaning": "A language spoken in Awadh region",
  "usage_example": "अवधी बोली मीठी है",
  "status": "active",
  "visibility": "public",
  "version": 1,
  "is_canonical": true,
  
  // ✅ ADD: Timestamps
  "created_at": "2024-10-05T12:00:00Z",
  "updated_at": "2024-10-05T12:00:00Z",
  
  // ✅ ADD: Engagement metrics
  "likes_count": 23,
  "views_count": 456,
  "shares_count": 3,
  "bookmarks_count": 12,
  
  // ✅ ADD: Trust data
  "source_reference": "Hindi-Awadhi Dictionary, Ram Naresh Tripathi",
  "verified_by": 2,
  "verified_at": "2024-10-06T08:30:00Z",
  "created_by": 5
}
```

#### Business Justification
Same as Doha module - SEO structured data, engagement UI, trust signals.

---

## 📋 MODULE 3: Idioms API (`/idioms`)

### Endpoint: `GET /idioms/{id}`

#### Current JSON Output
```json
{
  "id": 8,
  "text": "हाथी के दांत खाने के और दिखाने के और",
  "meaning": "Hypocrisy; saying one thing and doing another",
  "usage_example": "उसके वादे सिर्फ हाथी के दांत हैं",
  "status": "active",
  "visibility": "public",
  "version": 1
}
```

#### Required JSON Output
```json
{
  "id": 8,
  "text": "हाथी के दांत खाने के और दिखाने के और",
  "meaning": "Hypocrisy; saying one thing and doing another",
  "usage_example": "उसके वादे सिर्फ हाथी के दांत हैं",
  "status": "active",
  "visibility": "public",
  "version": 1,
  
  // ✅ ADD: Timestamps
  "created_at": "2024-09-20T14:15:00Z",
  "updated_at": "2024-09-20T14:15:00Z",
  
  // ✅ ADD: Engagement metrics
  "likes_count": 15,
  "views_count": 234,
  "shares_count": 5,
  "bookmarks_count": 8
}
```

---

## 📋 MODULE 4: Articles API (`/articles`)

### Endpoint: `GET /articles/{id}`

#### Current JSON Output
```json
{
  "id": 5,
  "title": "History of Awadhi Literature",
  "excerpt": "An overview of Awadhi literary tradition",
  "content": "<p>Full article content...</p>",
  "author_id": 3,
  "status": "published",
  "visibility": "public"
}
```

#### Required JSON Output
```json
{
  "id": 5,
  "title": "History of Awadhi Literature",
  "excerpt": "An overview of Awadhi literary tradition",
  "content": "<p>Full article content...</p>",
  "author_id": 3,
  "author_name": "Dr. Rajesh Kumar",  // ✅ ADD
  "status": "published",
  "visibility": "public",
  
  // ✅ ADD: Timestamps
  "created_at": "2024-08-10T09:00:00Z",
  "updated_at": "2024-11-15T16:45:00Z",
  
  // ✅ ADD: Engagement metrics
  "likes_count": 67,
  "views_count": 3421,
  "shares_count": 23,
  "bookmarks_count": 45,
  
  // ✅ ADD: SEO fields
  "meta_description": "Explore the rich history of Awadhi literature...",
  "tags": ["literature", "history", "awadhi"]
}
```

---

## 📋 MODULE 5: Interactions API (NEW ENDPOINTS NEEDED)

### 🆕 Endpoint: `GET /interactions/users/{user_id}/likes`

#### Required JSON Output
```json
{
  "count": 42,
  "results": [
    {
      "content_type": "doha",
      "content_id": 123,
      "created_at": "2024-12-20T10:30:00Z"
    },
    {
      "content_type": "dictionary",
      "content_id": 45,
      "created_at": "2024-12-18T14:20:00Z"
    }
  ]
}
```

#### Business Justification
**Required for:** Dashboard "My Likes" tab  
**Current State:** ❌ Endpoint does not exist  
**Frontend State:** UI implemented but shows empty/dummy data

#### Implementation Notes
```python
# backend/app/api/v1/interactions.py

@router.get("/users/{user_id}/likes")
def api_list_user_likes(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200)
):
    # Owner-only or admin check
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not allowed")
    
    # Query UserInteraction table
    likes = db.query(UserInteraction).filter(
        UserInteraction.user_id == user_id,
        UserInteraction.interaction_type == 'like'
    ).order_by(UserInteraction.created_at.desc()).offset(offset).limit(limit).all()
    
    results = [
        {
            "content_type": like.content_type,
            "content_id": like.content_id,
            "created_at": like.created_at
        }
        for like in likes
    ]
    
    return {"count": len(results), "results": results}
```

---

## 📋 MODULE 6: Users API (NEW ENDPOINTS NEEDED)

### 🆕 Endpoint: `GET /users/{username}/stats`

#### Required JSON Output
```json
{
  "public_submissions": 42,
  "approved_count": 38,
  "likes_received": 156,
  "bookmarks_received": 89,
  "total_views": 4523,
  "member_since": "2024-03-15T08:00:00Z"
}
```

#### Business Justification
**Required for:** Public user profile page (`/users/:username`)  
**Current State:** ❌ Endpoint does not exist  
**Frontend State:** Shows static placeholder text

#### Implementation Notes
```python
# backend/app/api/v1/users.py

class UserPublicStatsOut(BaseModel):
    public_submissions: int
    approved_count: int
    likes_received: int
    bookmarks_received: int
    total_views: int
    member_since: datetime

@router.get("/{username}/stats", response_model=UserPublicStatsOut)
def get_user_stats(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Count approved public submissions
    public_submissions = db.query(Submission).filter(
        Submission.contributor_id == user.id,
        Submission.status == 'approved',
        Submission.visibility == 'public',
        Submission.is_deleted == False
    ).count()
    
    # Count all approved
    approved_count = db.query(Submission).filter(
        Submission.contributor_id == user.id,
        Submission.status == 'approved',
        Submission.is_deleted == False
    ).count()
    
    # Aggregate likes received (complex - need to join with content tables)
    # This is a simplified version - actual implementation needs content_type routing
    total_likes = 0
    total_bookmarks = 0
    total_views = 0
    
    # For each approved submission, get its engagement data
    # TODO: Implement proper aggregation query
    
    return {
        "public_submissions": public_submissions,
        "approved_count": approved_count,
        "likes_received": total_likes,
        "bookmarks_received": total_bookmarks,
        "total_views": total_views,
        "member_since": user.created_at
    }
```

---

## 📋 MODULE 7: Submissions API (SCHEMA UPDATE)

### Endpoint: `PUT /submissions/{id}`

#### Current Request Schema
```python
class SubmissionUpdateIn(BaseModel):
    main_text: Optional[str] = None
    meaning: Optional[str] = None
    external_references: Optional[Dict[str, Any]] = None
    visibility: Optional[str] = None
    submit_for_review: Optional[bool] = None
    expected_version: int
```

#### Required Request Schema
```python
class SubmissionUpdateIn(BaseModel):
    # Existing content fields
    main_text: Optional[str] = None
    meaning: Optional[str] = None
    external_references: Optional[Dict[str, Any]] = None
    visibility: Optional[str] = None
    submit_for_review: Optional[bool] = None
    
    # ✅ NEW: Metadata fields (moderator-only)
    author_slug: Optional[str] = None
    work_slug: Optional[str] = None
    chapter_slug: Optional[str] = None
    number_in_chapter: Optional[int] = None
    is_classical: Optional[bool] = None
    
    expected_version: int
```

#### Business Justification
**Required for:** Moderator inline editing workflow  
**Current State:** ❌ Returns 422 validation error when moderators try to fix metadata  
**Impact:** Moderators must reject submissions for minor metadata errors instead of fixing them

#### Permission Logic Required
```python
@router.put("/{submission_id}")
def update_submission(
    submission_id: int,
    data: SubmissionUpdateIn,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    submission = db.query(Submission).filter(...).first()
    
    is_owner = current_user.id == submission.contributor_id
    is_moderator = current_user.role in ['moderator', 'admin']
    
    # Contributors can only edit content
    if is_owner and not is_moderator:
        if any([data.author_slug, data.work_slug, data.chapter_slug, 
                data.number_in_chapter, data.is_classical]):
            raise HTTPException(403, "Contributors cannot edit metadata")
    
    # Moderators can only edit metadata, not content
    if is_moderator and not is_owner:
        if data.main_text or data.meaning:
            raise HTTPException(403, "Moderators cannot edit content of others' submissions")
    
    # Apply updates...
```

---

## 📋 MODULE 8: Authentication API (FRONTEND INTEGRATION)

### Endpoint: `GET /auth/oauth/google/callback`

#### Current State
✅ **Backend IMPLEMENTED** (exists at `backend/app/api/v1/auth.py` line 128)

#### Frontend Gap
❌ **No frontend integration**
- No "Sign in with Google" button on login page
- No callback handler page at `frontend/src/pages/auth/oauth/google/callback.astro`

#### Required Frontend Implementation
1. Add Google OAuth button to login.astro
2. Create callback handler page to receive OAuth response
3. Store tokens and redirect to dashboard

**Note:** This is a FRONTEND task, backend is ready.

---

## 📋 MODULE 9: Search API (OPTIMIZATION)

### Endpoint: `GET /search/global`

#### Current Behavior
Returns results but no metadata about result counts per content type.

#### Suggested Enhancement
```json
{
  "total_count": 45,
  "counts_by_type": {
    "doha": 23,
    "dictionary": 12,
    "idioms": 7,
    "articles": 3
  },
  "results": [
    {
      "content_type": "doha",
      "content_id": 33,
      "title": "जो सुख होइ जोग सो...",
      "excerpt": "Whatever happiness...",
      "score": 0.95
    }
  ]
}
```

#### Business Justification
Frontend can display "23 Dohas, 12 Dictionary Entries, 7 Idioms, 3 Articles" for better UX.

---

## 🎯 Priority Matrix

| Priority | Module | Endpoint | Change Type | Frontend Blocked? |
|----------|--------|----------|-------------|-------------------|
| 🔴 **P0** | Content | GET /content/doha/{id} | Schema expansion | ✅ YES - InteractionBar broken |
| 🔴 **P0** | Content | GET /dictionary/{id} | Schema expansion | ✅ YES - Same issue |
| 🔴 **P0** | Content | GET /idioms/{id} | Schema expansion | ✅ YES - Same issue |
| 🔴 **P0** | Content | GET /articles/{id} | Schema expansion | ✅ YES - Same issue |
| 🟠 **P1** | Interactions | GET /users/{id}/likes | New endpoint | ✅ YES - Dashboard empty |
| 🟠 **P1** | Users | GET /users/{username}/stats | New endpoint | ✅ YES - Profile incomplete |
| 🟡 **P2** | Submissions | PUT /submissions/{id} | Schema expansion | ⚠️ PARTIAL - Workaround exists |
| 🟢 **P3** | Search | GET /search/global | Enhancement | ❌ NO - Nice to have |

---

## 📊 Implementation Effort Estimates

| Task | Backend Hours | Testing Hours | Total |
|------|:-------------:|:-------------:|:-----:|
| Content API schema expansion (4 endpoints) | 4 | 2 | 6 |
| Engagement KPI joins (4 endpoints) | 3 | 1 | 4 |
| Author/Work/Chapter name resolution | 2 | 1 | 3 |
| User likes endpoint | 2 | 1 | 3 |
| User stats endpoint | 4 | 2 | 6 |
| Submission metadata update | 3 | 2 | 5 |
| **TOTAL** | **18 hours** | **9 hours** | **27 hours** |

**Estimated completion:** 3-4 days of focused backend development

---

## 📝 SQL Query Templates

### Template 1: Join EngagementKPI
```python
content = db.query(ContentModel).options(
    joinedload(ContentModel.engagement_kpi)
).filter(...).first()

likes_count = content.engagement_kpi.likes_count if content.engagement_kpi else 0
```

### Template 2: Join Author/Work/Chapter
```python
doha = db.query(DohaEntry).options(
    joinedload(DohaEntry.author),
    joinedload(DohaEntry.work),
    joinedload(DohaEntry.chapter)
).filter(...).first()

author_name = doha.author.name if doha.author else None
```

### Template 3: Aggregate User Stats
```sql
-- Get total likes received by a user
SELECT SUM(ek.likes_count) as total_likes
FROM engagement_kpi ek
JOIN doha_entries de ON ek.content_id = de.id AND ek.content_type = 'doha'
JOIN submissions s ON s.content_id = de.id AND s.content_type = 'doha'
WHERE s.contributor_id = :user_id AND s.status = 'approved'

UNION ALL

-- Repeat for dictionary, idioms, articles...
```

---

## ✅ Acceptance Criteria

For each endpoint listed above, the backend change is COMPLETE when:

1. ✅ Response JSON matches "Required JSON Output" specification
2. ✅ All NULL fields have proper Optional[Type] annotations
3. ✅ JOINs are optimized (use `joinedload`, not N+1 queries)
4. ✅ OpenAPI/Swagger docs updated automatically
5. ✅ Unit tests pass for new fields
6. ✅ No breaking changes to existing clients

---

## 🚀 Rollout Strategy

### Phase 1: Content API (P0 - Week 1)
- Update DohaOut, DictionaryDetailOut, IdiomOut, ArticleDetailOut schemas
- Add engagement_kpi joins
- Add author/work/chapter name resolution
- Deploy and verify frontend InteractionBar displays real counts

### Phase 2: New Endpoints (P1 - Week 2)
- Implement GET /interactions/users/{id}/likes
- Implement GET /users/{username}/stats
- Deploy and verify dashboard "My Likes" tab functional

### Phase 3: Submissions Update (P2 - Week 3)
- Expand SubmissionUpdateIn schema
- Add permission logic for metadata editing
- Deploy and verify moderators can inline-edit metadata

### Phase 4: Optimizations (P3 - Week 4)
- Search enhancements
- Performance tuning
- Monitoring and observability

---

**Last Updated:** December 30, 2025  
**Next Review:** After Phase 1 completion  
**Contact:** Frontend Lead (for clarifications)
