# Implementation Gaps Report
**Project:** Awadhi New  
**Date:** December 30, 2025  
**Status:** Issues documented in markdown files vs actual code  
**Purpose:** Track persistent issues requiring implementation

---

## 🔴 BACKEND GAPS (High Priority)

### 1. Engagement Data Not Returned in Content APIs
**Documented In:** `CONTENT_MODULE_AUDIT_REPORT.md`, `FRONTEND_BACKEND_SYNC_REPORT.md`  
**Status:** ❌ **STILL BROKEN**

#### Issue
Backend tracks engagement metrics (`likes_count`, `views_count`, `shares_count`, `bookmarks_count`) in the `EngagementKPI` table but NEVER returns this data in content response schemas.

#### Affected Files
- `backend/app/api/v1/content.py` - DohaOut schema (lines 14-32)
- `backend/app/api/v1/dictionary.py` - DictionaryDetailOut schema
- `backend/app/api/v1/idiom.py` - IdiomOut schema
- `backend/app/api/v1/article.py` - ArticleDetailOut schema

#### Current State
```python
# backend/app/api/v1/content.py
class DohaOut(BaseModel):
    id: int
    main_text: str
    meaning: Optional[str]
    # ... other fields ...
    # ❌ MISSING: likes_count, views_count, shares_count, bookmarks_count
```

#### Required Fix
```python
class DohaOut(BaseModel):
    # ... existing fields ...
    likes_count: int = 0
    views_count: int = 0
    shares_count: int = 0
    bookmarks_count: int = 0

# In GET endpoints, add:
doha = db.query(DohaEntry).options(
    joinedload(DohaEntry.engagement_kpi)
).filter(DohaEntry.id == doha_id).first()

# Then populate in response:
result = {
    **doha.__dict__,
    "likes_count": doha.engagement_kpi.likes_count if doha.engagement_kpi else 0,
    "views_count": doha.engagement_kpi.views_count if doha.engagement_kpi else 0,
    # etc.
}
```

#### Impact
- Frontend `InteractionBar` component ALWAYS shows 0 for all metrics
- SEO rich snippets missing engagement signals
- Users cannot see content popularity

---

### 2. Timestamps Missing from Response Schemas
**Documented In:** `CONTENT_MODULE_AUDIT_REPORT.md`, `FRONTEND_BACKEND_SYNC_REPORT.md`, `z_documentation/architecture/SYSTEM_ARCHITECTURE_BLUEPRINT.md`  
**Status:** ❌ **STILL BROKEN**

#### Issue
Database models have `created_at` and `updated_at` fields, but Pydantic response schemas exclude them.

#### Affected Files
- `backend/app/api/v1/content.py` - DohaOut (no timestamps)
- `backend/app/api/v1/dictionary.py` - DictionaryDetailOut (no timestamps)
- `backend/app/api/v1/idiom.py` - IdiomOut (no timestamps)
- `backend/app/api/v1/article.py` - ArticleDetailOut (no timestamps)

#### Current State
Frontend components expect timestamps but receive nothing:
```astro
<!-- frontend/src/pages/doha/[id].astro line 84 -->
<ModerationInfo 
  createdAt={doha.created_at}  <!-- ❌ undefined -->
  updatedAt={doha.updated_at}  <!-- ❌ undefined -->
/>
```

#### Required Fix
```python
from datetime import datetime

class DohaOut(BaseModel):
    # ... existing fields ...
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
```

#### Impact
- Frontend cannot show "Last updated" timestamps
- SEO metadata missing `dateModified` field
- Content freshness indicators broken

---

### 3. Author/Work/Chapter Names Not Resolved
**Documented In:** `CONTENT_MODULE_AUDIT_REPORT.md`, `FRONTEND_BACKEND_SYNC_REPORT.md`  
**Status:** ❌ **STILL BROKEN**

#### Issue
Backend sends only IDs (`author_id`, `work_id`, `chapter_id`) but not names. Frontend needs to make additional API calls or display IDs directly.

#### Current State
```python
# backend/app/api/v1/content.py
class DohaOut(BaseModel):
    author_id: Optional[int]  # ✅ SENT
    work_id: Optional[int]    # ✅ SENT
    chapter_id: Optional[int] # ✅ SENT
    # ❌ MISSING: author_name, work_name, chapter_name
```

Frontend receives IDs but displays nothing:
```astro
<!-- frontend/src/pages/doha/[id].astro -->
<StructuredData 
  data={{
    author: doha.author_name,  <!-- ❌ undefined -->
    work: doha.work_name       <!-- ❌ undefined -->
  }}
/>
```

#### Required Fix
```python
# Add JOINs to content queries
doha = db.query(DohaEntry).options(
    joinedload(DohaEntry.author),
    joinedload(DohaEntry.work),
    joinedload(DohaEntry.chapter)
).filter(...).first()

# Expand schema
class DohaOut(BaseModel):
    # ... existing fields ...
    author_name: Optional[str]
    work_name: Optional[str]
    chapter_name: Optional[str]
```

#### Impact
- Structured data incomplete (bad SEO)
- Cannot display "By Tulsidas from Ramcharitmanas"
- Users see IDs instead of readable names

---

### 4. User Likes Endpoint Missing
**Documented In:** `BACKEND_TODO_user_likes.md`  
**Status:** ❌ **NOT IMPLEMENTED**

#### Issue
Dashboard "My Likes" tab requires `GET /interactions/users/{userId}/likes` endpoint that doesn't exist.

#### Current State
```python
# backend/app/api/v1/interactions.py - Only has:
- POST /interactions/toggle
- POST /interactions/share
- POST /interactions/report
- GET /interactions/users/{user_id}/bookmarks  # ✅ EXISTS

# ❌ MISSING: GET /interactions/users/{user_id}/likes
```

#### Required Implementation
```python
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
    
    # Query UserInteraction table for 'like' interactions
    likes = db.query(UserInteraction).filter(
        UserInteraction.user_id == user_id,
        UserInteraction.interaction_type == 'like'
    ).offset(offset).limit(limit).all()
    
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

#### Impact
- Dashboard "My Likes" tab shows empty/dummy data
- Users cannot review content they've liked

---

### 5. User Public Statistics Endpoint Missing
**Documented In:** `BACKEND_TODO_user_stats.md`  
**Status:** ❌ **NOT IMPLEMENTED**

#### Issue
Public user profile page (`/users/:username`) needs statistics about user contributions.

#### Current State
```python
# backend/app/api/v1/users.py - Only returns:
class PublicUserOut(BaseModel):
    id: int
    username: Optional[str]
    role: str
    # ❌ MISSING: Statistics fields
```

#### Required Implementation
```python
@router.get("/{username}/stats")
def get_user_stats(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Count approved public submissions
    public_submissions = db.query(Submission).filter(
        Submission.contributor_id == user.id,
        Submission.status == 'approved',
        Submission.visibility == 'public'
    ).count()
    
    # Count all approved submissions
    approved_count = db.query(Submission).filter(
        Submission.contributor_id == user.id,
        Submission.status == 'approved'
    ).count()
    
    # Calculate likes received (complex query needed)
    # ... aggregate from EngagementKPI joined with content tables
    
    return {
        "public_submissions": public_submissions,
        "approved_count": approved_count,
        "likes_received": 0,  # TODO: implement
        "bookmarks_received": 0  # TODO: implement
    }
```

#### Impact
- User profiles show no contribution statistics
- Cannot gamify/recognize active contributors

---

### 6. Submission Metadata Fields Not Updateable
**Documented In:** `BACKEND_ISSUE_moderator_inline_editing_metadata.md`  
**Status:** ❌ **STILL BROKEN**

#### Issue
Moderators cannot edit metadata fields (`author_slug`, `work_slug`, `chapter_slug`, `number_in_chapter`, `is_classical`) via `PUT /submissions/{id}`.

#### Current State
```python
# backend/app/api/v1/submissions.py lines 34-42
class SubmissionUpdateIn(BaseModel):
    main_text: Optional[str] = None
    meaning: Optional[str] = None
    external_references: Optional[Dict[str, Any]] = None
    visibility: Optional[str] = None
    submit_for_review: Optional[bool] = None
    expected_version: int
    # ❌ MISSING: author_slug, work_slug, chapter_slug, number_in_chapter, is_classical
```

#### Required Fix
```python
class SubmissionUpdateIn(BaseModel):
    # Existing fields
    main_text: Optional[str] = None
    meaning: Optional[str] = None
    external_references: Optional[Dict[str, Any]] = None
    visibility: Optional[str] = None
    submit_for_review: Optional[bool] = None
    
    # ✅ ADD: Metadata fields (moderator-only)
    author_slug: Optional[str] = None
    work_slug: Optional[str] = None
    chapter_slug: Optional[str] = None
    number_in_chapter: Optional[int] = None
    is_classical: Optional[bool] = None
    
    expected_version: int

# In PUT handler, add permission check:
@router.put("/{submission_id}")
def update_submission(
    submission_id: int,
    data: SubmissionUpdateIn,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    submission = db.query(Submission).filter(...).first()
    
    # Only owner can update content
    if current_user.id != submission.contributor_id:
        # But moderators can update metadata
        if current_user.role not in ['moderator', 'admin']:
            raise HTTPException(403, "Not allowed")
        
        # Moderators can ONLY update metadata, not content
        if data.main_text or data.meaning:
            raise HTTPException(403, "Moderators cannot edit content")
    
    # Apply updates...
```

#### Impact
- Moderators cannot fix incorrect author/work assignments
- Must reject submissions for minor metadata errors
- Slows moderation workflow

---

### 7. OAuth Callback Handler Exists But No Frontend Integration
**Documented In:** `z_documentation/audit/01_AUTH_MODULE_AUDIT.md`  
**Status:** ⚠️ **BACKEND READY, FRONTEND MISSING**

#### Issue
Backend has `GET /auth/oauth/google/callback` endpoint but frontend has no "Sign in with Google" button or callback page.

#### Backend State
```python
# backend/app/api/v1/auth.py line 128
@router.get("/oauth/google/callback")
def oauth_google_callback(...):
    # ✅ IMPLEMENTED
```

#### Frontend State
```astro
<!-- frontend/src/pages/login.astro lines 54-60 -->
<!-- TODO: Implement Google OAuth -->
<!-- <div class="mt-4">
  <button type="button" ...>
    Sign in with Google
  </button>
</div> -->
```

**Frontend missing:**
- `frontend/src/pages/auth/oauth/google/callback.astro` handler page
- Google OAuth button in login/register pages

#### Impact
- Users cannot use Google Sign-In
- Backend OAuth infrastructure unused

---

## 🟡 FRONTEND GAPS (Medium Priority)

### 8. Loading Skeletons Missing on Content Pages
**Documented In:** `FRONTEND_BACKEND_SYNC_REPORT.md`  
**Status:** ✅ **IMPLEMENTED** (December 30, 2025)

#### Solution
Created `ContentSkeleton.svelte` component with 3 variants (detail, list, card).

**Usage:**
```svelte
<Recommendations client:load>
  <ContentSkeleton variant="card" count={3} slot="fallback" />
</Recommendations>
```

**See:** `FRONTEND_REMEDIATION_LOG.md` for full implementation details.

---

### 9. Empty State Components Missing
**Documented In:** `FRONTEND_BACKEND_SYNC_REPORT.md`  
**Status:** ✅ **IMPLEMENTED** (December 30, 2025)

#### Solution
Created `EmptyState.svelte` component, applied to doha list page.

**Example:**
```svelte
<EmptyState 
  icon="📜"
  title="No dohas available yet"
  actionText="Submit a Doha"
  actionHref="/submit"
/>
```

**Applied To:**
- ✅ `pages/doha.astro`
- ⏳ TODO: Search results, dashboard tabs

---

### 10. Hierarchy Path Not Parsed
**Documented In:** `FRONTEND_BACKEND_SYNC_REPORT.md`, `SYSTEM_ARCHITECTURE_BLUEPRINT.md`  
**Status:** ✅ **IMPLEMENTED** (December 30, 2025)

#### Solution
Created `lib/hierarchyParser.ts` utility and `Breadcrumbs.svelte` component.

**Functions:**
- `parseHierarchyPath()` - Converts to array of objects
- `formatHierarchyPath()` - Returns "Tulsidas → Ramcharitmanas"
- `truncateHierarchyPath()` - Handles long paths

**Applied To:**
- ✅ `pages/doha/[id].astro`
- ⏳ TODO: dictionary, idioms, articles pages

**Example Output:**
```
Before: /tulsidas/ramcharitmanas/ayodhyakand
After:  Tulsidas → Ramcharitmanas → Ayodhyakand
```

---

### 11. Permissions and Permission Scopes Unused
**Documented In:** `z_documentation/audit/01_AUTH_MODULE_AUDIT.md`, `FRONTEND_BACKEND_SYNC_REPORT.md`  
**Status:** ❌ **DATA RECEIVED BUT IGNORED**

#### Issue
Backend sends `permissions` (bitmask) and `permission_scopes` (JSON object) from `/auth/me` but frontend never uses them.

#### Current State
```typescript
// Backend sends:
{
  id: 1,
  email: "user@example.com",
  role: "contributor",
  permissions: 31,  // ❌ Frontend ignores this
  permission_scopes: {  // ❌ Frontend ignores this
    "can_edit_own": true,
    "can_moderate": false
  }
}

// Frontend only uses:
user.role  // ✅ USED for basic role checks
```

#### Required Fix
Create permission helper:
```typescript
// frontend/src/lib/permissions.ts
export function hasPermission(user: any, permission: string): boolean {
  if (!user?.permission_scopes) return false;
  return user.permission_scopes[permission] === true;
}

// Usage in components:
{#if hasPermission($user, 'can_moderate')}
  <button>Moderate</button>
{/if}
```

#### Impact
- Granular permissions unavailable
- Must rely on coarse role checks
- Backend permission system underutilized

---

### 12. No Client-Side Form Validation
**Documented In:** `FRONTEND_BACKEND_SYNC_REPORT.md`  
**Status:** ⚠️ **PARTIAL - Only HTML5 validation**

#### Issue
Forms rely solely on backend validation, causing unnecessary API calls for obvious errors.

#### Current State
```astro
<!-- frontend/src/pages/login.astro -->
<input type="email" name="email" required />  <!-- ✅ HTML5 only -->
<input type="password" name="password" required />  <!-- ✅ HTML5 only -->
```

#### Required Enhancement
Add client-side validation before API call:
```javascript
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const passwordMinLength = 6;

if (!emailRegex.test(email)) {
  errorEl.textContent = "Invalid email format";
  return;
}

if (password.length < passwordMinLength) {
  errorEl.textContent = "Password must be at least 6 characters";
  return;
}
```

#### Impact
- Unnecessary API calls for invalid data
- Slower feedback to users
- Higher backend load

---

### 13. No "Remember Me" Feature
**Documented In:** `z_documentation/audit/01_AUTH_MODULE_AUDIT.md`  
**Status:** ❌ **NOT IMPLEMENTED**

#### Issue
Login form has no "Remember Me" checkbox despite backend supporting long-lived refresh tokens.

#### Required Implementation
```astro
<!-- frontend/src/pages/login.astro -->
<div class="flex items-center">
  <input 
    type="checkbox" 
    id="remember" 
    name="remember" 
    class="mr-2"
  />
  <label for="remember" class="text-sm">Keep me signed in</label>
</div>
```

Backend could extend refresh token TTL for "remember me" users.

#### Impact
- Users must re-login frequently
- Poor UX for returning users

---

## 🟢 LOW PRIORITY / NICE-TO-HAVE

### 14. Search Autocomplete Not Implemented
**Documented In:** `FRONTEND_BACKEND_SYNC_REPORT.md`  
**Status:** ❌ **NOT IMPLEMENTED**

Search box has no suggestions/autocomplete despite backend full-text search capability.

---

### 15. Keyboard Shortcuts in Moderation Queue
**Documented In:** `FRONTEND_BACKEND_SYNC_REPORT.md`  
**Status:** ❌ **NOT IMPLEMENTED**

Moderators cannot use keyboard shortcuts (e.g., A for approve, R for reject) for faster workflow.

---

### 16. Dark Mode Toggle
**Status:** ❌ **NOT IMPLEMENTED**

Application hardcoded to dark theme, no user preference toggle.

---

### 17. Analytics Export to CSV
**Documented In:** `FRONTEND_BACKEND_SYNC_REPORT.md`  
**Status:** ❌ **NOT IMPLEMENTED**

Admin analytics dashboard shows charts but no CSV export functionality.

---

## Summary Statistics

| Category | Total Issues | Implemented | Partially Done | Not Started |
|----------|:------------:|:-----------:|:--------------:|:-----------:|
| **Backend Critical** | 7 | 1 (OAuth) | 0 | 6 |
| **Frontend Critical** | 6 | 4 (Token Refresh, Loading States, Empty States, Hierarchy Parser) | 2 (Form validation, Permissions) | 0 |
| **Low Priority** | 4 | 0 | 0 | 4 |
| **TOTAL** | **17** | **5 (29%)** | **2 (12%)** | **10 (59%)** |

---

## ✅ RECENTLY COMPLETED (December 30, 2025)

### Frontend Defensive Architecture
1. ✅ **ContentSkeleton Component** - Loading states for SSR pages
2. ✅ **EmptyState Component** - Professional UI for 0 results
3. ✅ **Hierarchy Parser** - Converts "/tulsidas/..." → "Tulsidas → Ramcharitmanas"
4. ✅ **Breadcrumbs Component** - Navigation from hierarchy_path
5. ✅ **Doha Pages Defensive Rendering** - Safe engagement data, author fallbacks, text truncation

**See:** `FRONTEND_REMEDIATION_LOG.md` for complete details

---

## Implementation Priority Order

### Week 1 (Critical)
1. ✅ **DONE:** Token refresh interceptor (implemented in api.ts)
2. ✅ **DONE:** Login/Register loading states (fixed Dec 30)
3. **Backend:** Add engagement data to content response schemas
4. **Backend:** Add timestamps to all content response schemas
5. **Frontend:** Create loading skeleton component

### Week 2 (High Priority)
6. **Backend:** Resolve author/work/chapter names in content responses
7. **Backend:** Implement `GET /interactions/users/{userId}/likes`
8. **Backend:** Implement `GET /users/{username}/stats`
9. **Frontend:** Create empty state component
10. **Frontend:** Implement hierarchy path parser

### Week 3 (Medium Priority)
11. **Backend:** Expand SubmissionUpdateIn to support metadata editing
12. **Frontend:** Implement Google OAuth flow
13. **Frontend:** Add client-side form validation
14. **Frontend:** Implement permission helpers

### Week 4 (Polish)
15. Search autocomplete
16. Keyboard shortcuts in moderation
17. Dark mode toggle
18. Analytics CSV export

---

**Last Updated:** December 30, 2025  
**Next Review:** After critical backend schema changes implemented
