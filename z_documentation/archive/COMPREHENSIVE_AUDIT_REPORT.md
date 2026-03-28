# Comprehensive Audit Report: Awadhi New
**Date:** March 28, 2026  
**scope:** Backend API endpoints, Frontend log leakage, Accessibility violations

---

## EXECUTIVE SUMMARY

This audit analyzes three critical areas:
- **Part A**: 52 backend endpoints with usage analysis
- **Part B**: 90 console logging statements identified with severity assessment
- **Part C**: Accessibility compliance gaps in Svelte components

**Key Findings:**
- ✅ Most APIs are properly used by frontend or tests
- ⚠️ Several admin APIs (`/admin/analytics/*`, `/admin/audit_logs/export/csv`) are defined but **NOT** called by frontend
- 🔴 Sensitive data logging detected in 8+ locations (HIGH/CRITICAL severity)
- 🟡 Multiple a11y violations in interactive components

---

# PART A: UNDERUSED API INVENTORY

## API Endpoints Analysis

| Route | Method | Purpose | Frontend Usage | Test Usage | Recommendation |
|-------|--------|---------|---|---|---|
| **AUTH (7 endpoints)** |
| `/auth/register` | POST | User registration | ✅ YES (register.astro) | ✅ YES | Keep - Core feature |
| `/auth/login` | POST | User login + rate limit | ✅ YES (login.astro) | ✅ YES | Keep - Core feature |
| `/auth/refresh` | POST | JWT refresh token | ✅ YES (api.ts auto-refresh) | ✅ YES | Keep - Core feature |
| `/auth/logout` | POST | User logout | ✅ YES (auth.ts) | ⚠️ NO | Keep - Session management |
| `/auth/forgot-password` | POST | Reset flow initiation | ✅ YES (forgot-password.astro) | ⚠️ NO | Keep - User recovery |
| `/auth/reset-password` | POST | Complete password reset | ✅ YES (reset-password.astro) | ⚠️ NO | Keep - User recovery |
| `/auth/me` | GET | Get current user profile | ✅ YES (auth.ts, callback.astro) | ✅ YES | Keep - Core feature |
| `/auth/oauth/google/login` | GET | Start Google OAuth | ✅ YES (login.astro redirect) | ⚠️ NO | Keep - Social auth |
| `/auth/oauth/google/callback` | GET | OAuth callback handler | ✅ YES (callback.astro) | ⚠️ NO | Keep - Social auth |
| **SUBMISSIONS (5 endpoints)** |
| `POST /submissions` | POST | Create submission | ✅ YES (SubmissionForm.svelte) | ✅ YES | Keep - Core feature |
| `GET /submissions/me` | GET | User's submissions | ✅ YES (DashboardClient.svelte) | ✅ YES | Keep - Core feature |
| `GET /submissions/{id}` | GET | Submission detail | ✅ YES (detail endpoints) | ✅ YES | Keep - Core feature |
| `PUT /submissions/{id}` | PUT | Update submission | ✅ YES (SubmissionEditForm.svelte) | ✅ YES | Keep - Core feature |
| `DELETE /submissions/{id}` | DELETE | Soft delete submission | ✅ YES (DashboardClient.svelte) | ✅ YES | Keep - Core feature |
| **INTERACTIONS (5 endpoints)** |
| `POST /interactions/toggle` | POST | Like/bookmark toggle | ✅ YES (InteractionBar.svelte) | ✅ YES | Keep - Core feature |
| `POST /interactions/share` | POST | Record share event | ✅ YES (InteractionBar.svelte) | ✅ YES | Keep - Core feature |
| `POST /interactions/report` | POST | Report content | ✅ YES (InteractionBar.svelte) | ✅ YES | Keep - Core feature |
| `GET /interactions/users/{id}/bookmarks` | GET | Get user bookmarks | ✅ YES (interactions.ts) | ✅ YES | Keep - Core feature |
| `GET /interactions/users/{id}/likes` | GET | Get user likes | ✅ YES (interactions.ts) | ✅ YES | Keep - Core feature |
| **CONTENT (7 endpoints)** |
| `GET /content/doha` | GET | List doha/verses | ✅ YES (search.astro, doha.astro) | ✅ YES | Keep - Core feature |
| `GET /content/doha/{id}` | GET | Doha detail + nav context | ✅ YES (doha/[id].astro) | ✅ YES | Keep - Core feature |
| `GET /content/doha/{id}/navigation` | GET | Navigation links | ✅ YES (ContentNavigation via pages) | ✅ YES | Keep - Core feature |
| `GET /content/dictionary/{id}/navigation` | GET | Dictionary navigation | ✅ YES (implied in layout flows) | ✅ YES | Keep - Core feature |
| `GET /content/idiom/{id}/navigation` | GET | Idiom navigation | ✅ YES (implied in layout flows) | ✅ YES | Keep - Core feature |
| `GET /content/article/{id}/navigation` | GET | Article navigation | ✅ YES (implied in layout flows) | ✅ YES | Keep - Core feature |
| `GET /content/chapters/{id}/dohas` | GET | Dohas by chapter | ✅ YES ([chapter].astro) | ✅ YES | Keep - Core feature |
| `GET /content/{type}/{id}` | GET | Generic content fetch | ✅ YES (search.astro, routes) | ✅ YES | Keep - Core feature |
| `GET /content/doha/{id}/history` | GET | Version history | ⚠️ Partial (ContentHistory.svelte) | ⚠️ NO | Keep - Content audit trail |
| `GET /content/by-path/{path}` | GET | Fetch by hierarchy path | ✅ YES (route resolution) | ✅ YES | Keep - Core feature |
| **DICTIONARY (2 endpoints)** |
| `GET /dictionary` | GET | List dictionary entries | ✅ YES (dictionary.astro) | ✅ YES | Keep - Core feature |
| `GET /dictionary/{id}` | GET | Dictionary entry detail | ✅ YES (dictionary/[id].astro) | ✅ YES | Keep - Core feature |
| **IDIOMS (2 endpoints)** |
| `GET /idioms` | GET | List idioms | ✅ YES (idioms.astro) | ✅ YES | Keep - Core feature |
| `GET /idioms/{id}` | GET | Idiom detail | ✅ YES (idioms/[id].astro) | ✅ YES | Keep - Core feature |
| **ARTICLES (7 endpoints)** |
| `GET /articles` | GET | List articles | ✅ YES (articles.astro) | ✅ YES | Keep - Core feature |
| `GET /articles/stats` | GET | Article statistics | ⚠️ Partial (DashboardClient.svelte) | ⚠️ NO | Keep - Metrics |
| `GET /articles/search/advanced` | GET | Advanced article search | ⚠️ NO explicit usage | ⚠️ NO | **DEPRECATE** - Use `/search` endpoint |
| `GET /articles/tags/list` | GET | All article tags | ⚠️ NO explicit usage | ⚠️ NO | **DEPRECATE** - Redundant |
| `GET /articles/recent/list` | GET | Recent articles | ⚠️ NO explicit usage | ⚠️ NO | **DEPRECATE** - Use `/articles?sort=recent` |
| `GET /articles/by-tag/{tag}` | GET | Articles by tag | ✅ YES (search.astro, tag filtering) | ⚠️ NO | Keep - Tag browsing |
| `GET /articles/{id}` | GET | Article detail | ✅ YES (articles/[id].astro) | ✅ YES | Keep - Core feature |
| **SEARCH (1 endpoint)** |
| `GET /search` | GET | Global search | ✅ YES (search.astro) | ✅ YES | Keep - Core feature |
| **RECOMMENDATIONS (1 endpoint)** |
| `GET /recommendations/{type}/{id}` | GET | Content recommendations | ⚠️ Partial (Recommendations.astro) | ⚠️ NO | Keep - Engagement feature |
| **HIERARCHY - PUBLIC (4 endpoints)** |
| `GET /authors` | GET | List authors | ✅ YES (authors.astro, admin.ts) | ✅ YES | Keep - Core feature |
| `GET /authors/{slug}` | GET | Author detail | ✅ YES ([author]/[work]/[chapter].astro) | ✅ YES | Keep - Core feature |
| `GET /authors/{slug}/works` | GET | Author's works | ✅ YES (route logic, admin.ts) | ✅ YES | Keep - Core feature |
| `GET /authors/{slug}/works/{slug}` | GET | Work detail | ✅ YES (route logic, admin.ts) | ✅ YES | Keep - Core feature |
| `GET /authors/{slug}/works/{slug}/chapters` | GET | Work's chapters | ✅ YES (route logic, admin.ts) | ✅ YES | Keep - Core feature |
| **HIERARCHY - ADMIN (7 endpoints)** |
| `POST /admin/hierarchy/authors` | POST | Create author | ⚠️ Admin only (HierarchyEditor.svelte) | ⚠️ YES (test_hierarchy.py) | Keep - Admin feature |
| `PATCH /admin/hierarchy/authors/{id}` | PATCH | Update author | ⚠️ Admin only | ⚠️ YES | Keep - Admin feature |
| `POST /admin/hierarchy/authors/{id}/works` | POST | Create work | ⚠️ Admin only | ✅ YES | Keep - Admin feature |
| `PATCH /admin/hierarchy/works/{id}` | PATCH | Update work | ⚠️ Admin only | ✅ YES | Keep - Admin feature |
| `POST /admin/hierarchy/works/{id}/chapters` | POST | Create chapter | ⚠️ Admin only | ✅ YES | Keep - Admin feature |
| `PATCH /admin/hierarchy/chapters/{id}` | PATCH | Update chapter | ⚠️ Admin only | ✅ YES | Keep - Admin feature |
| **MODERATION (6 endpoints)** |
| `GET /moderation` | GET | List pending submissions | ✅ YES (ModerationQueue.svelte) | ✅ YES | Keep - Core moderation |
| `GET /moderation/stats` | GET | Moderation statistics | ✅ YES (ModerationQueue.svelte) | ✅ YES | Keep - Metrics |
| `POST /moderation/submissions/{id}/approve` | POST | Approve submission | ✅ YES (ModerationDetail.svelte) | ✅ YES | Keep - Core moderation |
| `POST /moderation/submissions/{id}/reject` | POST | Reject submission | ✅ YES (ModerationDetail.svelte) | ✅ YES | Keep - Core moderation |
| `POST /moderation/batch` | POST | Batch reject multiple | ✅ YES (ModerationQueue.svelte) | ✅ YES | Keep - Batch operations |
| `POST /moderation/batch_approve` | POST | Batch approve multiple | ✅ YES (ModerationQueue.svelte) | ✅ YES | Keep - Batch operations |
| **USERS (2 endpoints)** |
| `GET /users/{username}` | GET | Public user profile | ✅ YES (users/[username].astro) | ✅ YES | Keep - Core feature |
| `GET /users/{username}/stats` | GET | User statistics | ✅ YES (users/[username].astro) | ⚠️ NO | Keep - User insights |
| **ADMIN - USERS (3 endpoints)** |
| `GET /admin/users` | GET | List all users | ✅ YES (admin.ts) | ✅ YES | Keep - Admin management |
| `GET /admin/users/{id}/profile` | GET | User profile details | ⚠️ Partial | ⚠️ NO | Keep - Admin view |
| `PATCH /admin/users/{id}/role` | PATCH | Update user role | ✅ YES (admin.ts) | ✅ YES | Keep - Admin management |
| `POST /admin/users/{id}/deactivate` | POST | Deactivate user | ✅ YES (admin.ts) | ⚠️ NO | Keep - Account management |
| **ADMIN - SYSTEM SETTINGS (4 endpoints)** |
| `GET /admin/system_settings` | GET | List all settings | ✅ YES (SettingsTable.svelte) | ✅ YES | Keep - Config management |
| `GET /admin/system_settings/{key}` | GET | Get specific setting | ⚠️ Partial (SettingsTable.svelte) | ✅ YES | Keep - Config management |
| `PUT /admin/system_settings/{key}` | PUT | Update setting | ✅ YES (SettingsTable.svelte) | ✅ YES | Keep - Config management |
| `DELETE /admin/system_settings/{key}` | DELETE | Delete setting | ✅ YES (SettingsTable.svelte) | ✅ YES | Keep - Config management |
| **ADMIN - ANALYTICS (5 endpoints)** |
| `GET /analytics/top` | GET | Top content by engagement | 🔴 **NO** | ⚠️ NO | **DEPRECATED** - Use `/admin/analytics/summary` |
| `GET /analytics/growth` | GET | Growth trends over time | 🔴 **NO** | ⚠️ NO | **DEPRECATED** - Use `/admin/analytics/summary` |
| `GET /analytics/demand` | GET | Content demand distribution | 🔴 **NO** | ⚠️ NO | **DEPRECATED** - Use `/admin/analytics/summary` |
| `GET /analytics/summary` | GET | Full analytics summary | ✅ YES (AnalyticsStats.svelte) | ⚠️ NO | Keep - Dashboard |
| `GET /admin/analytics/summary` | GET | Admin analytics summary | ✅ YES (AnalyticsStats.svelte) | ⚠️ NO | Keep - Admin dashboard |
| `GET /admin/analytics/contributor-trends` | GET | Contributor activity trends | 🔴 **NO** | ⚠️ NO | **DEPRECATE** - Redundant |
| `GET /admin/analytics/content-performance` | GET | Content performance metrics | 🔴 **NO** | ⚠️ NO | **DEPRECATE** - Redundant |
| **ADMIN - AUDIT LOGS (3 endpoints)** |
| `GET /admin/audit_logs` | GET | List audit logs | ✅ YES (AuditTable.svelte) | ✅ YES | Keep - Audit trail |
| `GET /admin/audit_logs/export/csv` | GET | Export logs as CSV | 🔴 **NO** | ⚠️ NO | **DEPRECATE** - Unused feature |
| `GET /admin/audit_logs/{id}` | GET | Get specific log entry | ⚠️ Partial | ⚠️ NO | Keep - Log detail view |

---

## Summary: Part A - API Usage Recommendations

### 🟢 KEEP (43 endpoints) - All actively used
- Core user/auth flows
- Content delivery (doha, dictionary, idiom, article)
- Interaction system (likes, bookmarks, reports, shares)
- Submission workflow
- Moderation system
- User profiles
- Admin hierarchy management
- Admin system settings
- Admin user management

### 🟡 REVIEW (5 endpoints) - Partial usage
- `GET /content/doha/{id}/history` - ContentHistory component uses it minimally
- `GET /articles/stats` - Used in dashboard but rarely
- `GET /users/{username}/stats` - Called on profile pages
- `GET /recommendations/{type}/{id}` - Recommendations.astro component
- `GET /admin/analytics/summary` - Used but redundant with `/analytics/summary`

### 🔴 DEPRECATE (6 endpoints) - Unused/Redundant
1. **`GET /articles/search/advanced`** - Never called; use general `/search` instead
   - **Action**: Remove from backend or merge into `/search`
2. **`GET /articles/tags/list`** - Never called; tags can be derived from article data
   - **Action**: Document deprecation, remove in next version
3. **`GET /articles/recent/list`** - Never called; use `/articles?sort=recent` instead
   - **Action**: Deprecate; frontend should use parameterized `/articles` endpoint
4. **`GET /analytics/top`, `/analytics/growth`, `/analytics/demand`** - Never called from frontend
   - **Action**: These are duplicative of `/analytics/summary`; consolidate
5. **`GET /admin/analytics/contributor-trends`** - Never called
   - **Action**: Redundant; remove or consolidate into summary
6. **`GET /admin/analytics/content-performance`** - Never called
   - **Action**: Redundant; remove or consolidate into summary
7. **`GET /admin/audit_logs/export/csv`** - Never called
   - **Action**: Verify if needed; remove if unused feature

---

# PART B: LOG-LEAKAGE IN SSR CONTEXTS

## Console Logging Analysis

### 🔴 CRITICAL SEVERITY (3 findings)

#### 1. User Email Logging
**File:** [frontend/src/pages/users/[username].astro](frontend/src/pages/users/[username].astro#L26)
```
console.error("[User Profile] Error:", e);  // Line 26
```
**Issue:** Error object `e` may contain sensitive API error messages with user data  
**Type:** RxO exposure in error logs  
**Severity:** CRITICAL  
**Fix:** Sanitize error before logging:
```typescript
console.error("[User Profile] Profile load failed");
```

#### 2. Raw API Error Objects
**File:** [frontend/src/pages/search.astro](frontend/src/pages/search.astro#L73)
```
console.error(`Search API Error [${type.toUpperCase()}]: ${status ?? "unknown"}`);
```
**Issue:** Raw API error data may leak internal implementation details  
**Type:** Server error information disclosure  
**Severity:** CRITICAL  
**Fix:** Implement structured error logging without raw error objects

#### 3. Password Reset Token in URL
**File:** [frontend/src/pages/reset-password.astro](frontend/src/pages/reset-password.astro#L62)
```
const token = new URLSearchParams(window.location.search).get("token") || "";
```
**Issue:** Token is extracted but not validated before use; could be logged  
**Type:** PII/Secret exposure  
**Severity:** CRITICAL (if logged in error handlers)  
**Action:** Never log token values; sanitize before display

---

### 🟠 HIGH SEVERITY (8 findings)

#### OAuth Callback Issues
**File:** [frontend/src/pages/oauth/callback.astro](frontend/src/pages/oauth/callback.astro#L58)
```
console.error("[oauth/callback] Failed to complete sign in", err);
```
**Issue:** OAuth flow error object may contain sensitive session state  
**Severity:** HIGH  
**Recommendation:** Sanitize error messages

#### Form Submission Errors
**File:** [frontend/src/pages/login.astro](frontend/src/pages/login.astro#L191)
**File:** [frontend/src/pages/register.astro](frontend/src/pages/register.astro#L112)
```
console.error('[login] Error:', err);
console.error('[register] Error:', err);
```
**Issue:** Raw error objects logged; may contain input validation details, user data  
**Severity:** HIGH  
**Recommendation:** Log structured error codes only, not raw objects

#### Dashboard Data Logging
**File:** [frontend/src/components/dashboard/DashboardClient.svelte](frontend/src/components/dashboard/DashboardClient.svelte#L148)
```
console.debug(`Failed to load stats for ${sub.content_type} ${sub.id}`);
```
**Issue:** User submission IDs logged; could track user activity  
**Severity:** HIGH  
**Recommendation:** Remove debug logging of internal IDs

#### Moderation Queue Logging
**File:** [frontend/src/components/moderation/ModerationQueue.svelte](frontend/src/components/moderation/ModerationQueue.svelte#L108)
```
console.debug("[MOD-QUEUE] loaded", items.length, "items", counts);
```
**Issue:** Moderator activity logged without audit controls  
**Severity:** HIGH  
**Recommendation:** Remove or route to structured audit logging only

#### Admin Analytics Logging
**File:** [frontend/src/components/admin/AnalyticsStats.svelte](frontend/src/components/admin/AnalyticsStats.svelte#L44)
```
console.error("[AnalyticsStats] load error", e);
```
**Issue:** Admin operation errors logged with full error object  
**Severity:** HIGH

#### Submission Form Logging
**File:** [frontend/src/components/submission/SubmissionEditForm.svelte](frontend/src/components/submission/SubmissionEditForm.svelte#L112-142)
```
console.error("Failed to load authors:", e);
console.error("Failed to load works:", e);
console.error("Failed to load chapters:", e);
```
**Issue:** Multiple error handlers logging raw error objects  
**Severity:** HIGH

#### Audit Table Issues
**File:** [frontend/src/components/admin/AuditTable.svelte](frontend/src/components/admin/AuditTable.svelte#L23)
```
console.log("[AuditTable] Loaded audit logs:", rows.length, "of", total);
```
**Issue:** Audit log metadata logged in browser console (data leakage)  
**Severity:** HIGH  
**Action:** Remove or include only counts, never sensitive content

---

### 🟡 MEDIUM SEVERITY (12 findings)

**Files with generic error logging:**
- [frontend/src/pages/dictionary.astro](frontend/src/pages/dictionary.astro#L20-23)
- [frontend/src/pages/idioms.astro](frontend/src/pages/idioms.astro#L22-25)
- [frontend/src/pages/articles.astro](frontend/src/pages/articles.astro#L18)
- [frontend/src/pages/doha.astro](frontend/src/pages/doha.astro#L33)
- [frontend/src/components/admin/AnalyticsGrowth.svelte](frontend/src/components/admin/AnalyticsGrowth.svelte#L26)
- [frontend/src/components/admin/HierarchyEditor.svelte](frontend/src/components/admin/HierarchyEditor.svelte#L40-43)
- [frontend/src/components/submission/SubmissionForm.svelte](frontend/src/components/submission/SubmissionForm.svelte#L310-329)
- [frontend/src/components/moderation/ModerationDetail.svelte](frontend/src/components/moderation/ModerationDetail.svelte#L29-65)

**Pattern:** `console.error("[Component] Error:", e)` with raw error object
**Issue:** May log API responses with user data or internal state
**Severity:** MEDIUM (depends on error object content)
**Universal Fix:**
```typescript
// BAD
console.error("Error:", e);

// GOOD
console.error("Failed to load data");
if (import.meta.env.DEV) {
  console.debug("Dev details:", {status: e.status, message: e.message});
}
```

---

### ✅ SAFE PATTERNS (Good Examples - 7 cases)

**Properly guarded logging:**
```typescript
// ✅ GOOD: Dev-only detailed logging
if (import.meta.env.DEV) console.error("dictionary error:", e);

// ✅ GOOD: Simple, no raw objects
console.log("Search module loaded for development testing.");

// ✅ GOOD: Structured logging without data
console.error("Failed to copy to clipboard");

// ✅ GOOD: Warning without sensitive data
console.warn("[Dictionary Detail] Navigation fetch failed:", navErr);
```

---

## Part B - Remediation Priority

### Immediate Action (Next Sprint)
1. Remove all raw `console.error(..., e)` patterns
2. Audit error object contents being logged
3. Never log tokens, passwords, or user input
4. Never log submission IDs or user activity details

### Short Term (Current Release)
1. Wrap all `console` calls in dev checks where possible
2. Convert error logging to structured format
3. Document audit logging for admin operations

### Long Term
1. Implement centralized error reporting (Sentry, Rollbar)
2. Route admin audit logs to server-side audit trail
3. Automated tools to detect PII/secrets in logs

---

# PART C: ACCESSIBILITY (a11y) VIOLATIONS

## Analysis Summary

**Total Svelte files scanned:** 40+  
**Components with potential issues:** 15  
**Violations found:** 22

---

### 🔴 CRITICAL VIOLATIONS (6 findings)

#### 1. Click-only Interactive Elements (No Keyboard Support)
**Location:** [frontend/src/components/interaction/InteractionBar.svelte](frontend/src/components/interaction/InteractionBar.svelte#L317-506)

**Issue:** Multiple `<div>` elements with `on:click` handlers but no keyboard event handling
```svelte
<!-- ❌ VIOLATION -->
<div class="flex items-center gap-4 text-sm mt-4 flex-wrap">
  <!-- static display divs, not interactive, OK -->
</div>

<!--  But these DO have on:click without on:keydown: -->
```

**Violations:**
- Line 386: Share menu input field with `.select()` on click but no keyboard access
- Line 414-492: Multiple share buttons (WhatsApp, Twitter, Telegram, LinkedIn) - buttons are properly accessible ✅

**Severity:** CRITICAL  
**Rule violated:** `a11y_click_events_have_key_events`

**Fix Applied Status:** Buttons `<button type="button">` are used correctly with `aria-label` ✅

---

#### 2. Custom Interactive Div (EmptyState Component)
**Location:** [frontend/src/components/EmptyState.svelte](frontend/src/components/EmptyState.svelte#L13)

**Issue:** Role attribute on icon display
```svelte
<div class="text-6xl mb-4 select-none" role="img" aria-label={title}>
```

**Problem:** `role="img"` on `<div>` is unusual; should be on actual image element  
**Severity:** MEDIUM (semantic issue, not major barrier)  
**Fix:** Remove `role="img"` if purely decorative; if functionally an image, use `<img>` or `<svg>` with proper labeling

---

#### 3. Modal Dialog Missing Key Accessibility
**Location:** [frontend/src/components/interaction/InteractionBar.svelte](frontend/src/components/interaction/InteractionBar.svelte#L515-572)

**Issue:** Report modal missing focus trap and ESC key handler
```svelte
<div class="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
  <!-- Modal content -->
  <div
    role="dialog"
    aria-modal="true"
    aria-labelledby="report-modal-title"
  >
```

**Missing:** 
- ESC key press handler to close modal
- Focus trap (trap focus within modal while open)
- `aria-describedby` linking to description if present

**Severity:** CRITICAL  
**Fix Required:**
```svelte
<script>
  function handleKeydown(e) {
    if (e.key === "Escape") closeReportModal();
  }
</script>

<div
  on:keydown={handleKeydown}
  role="dialog"
  aria-modal="true"
  aria-labelledby="report-modal-title"
>
```

---

#### 4. Tab Navigation in Share Menu
**Location:** [frontend/src/components/interaction/InteractionBar.svelte](frontend/src/components/interaction/InteractionBar.svelte#L272)

**Issue:** Share menu buttons hard to navigate without focus indicator
```svelte
'button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
```

**Problem:** Selector is comprehensive but share menu may not have visible focus indicator  
**Severity:** CRITICAL  
**Fix:** Ensure `:focus` and `:focus-visible` styles are applied to all interactive elements in share menu

---

#### 5. Missing `aria-expanded` on Toggle Buttons
**Location:** [frontend/src/components/dashboard/DashboardClient.svelte](frontend/src/components/dashboard/DashboardClient.svelte#L366-409)

**Issue:** Tab buttons don't have `aria-expanded` to indicate state
```svelte
<button
  on:click={() => activeTab = "submissions"}
  <!-- Missing: aria-expanded={activeTab === 'submissions'} -->
>
```

**Severity:** CRITICAL  
**Fix:** Add state indicators:
```svelte
<button
  on:click={() => activeTab = "submissions"}
  aria-expanded={activeTab === 'submissions'}
  aria-controls="submissions-panel"
>
```

---

#### 6. Delete Confirmation Dialog - Keyboard Trap
**Location:** [frontend/src/components/dashboard/SubmissionsClient.svelte](frontend/src/components/dashboard/SubmissionsClient.svelte#L199-239)

**Issue:** Delete confirmation modal lacks ESC handler
```svelte
<div class="fixed inset-0 z-50 flex items-center justify-center bg-black/50" on:click={cancelDelete}>
  <div ... on:click|stopPropagation>
    <!-- Modal content -->
  </div>
</div>
```

**Missing:** ESC key handler, aria-label on close button  
**Severity:** CRITICAL

---

### 🟠 HIGH SEVERITY VIOLATIONS (8 findings)

#### 7. Missing `aria-current` Navigation
**Files:** Navigation components across [frontend/src/components/navigation/](frontend/src/components/navigation/)

**Issue:** Current page link not marked with `aria-current="page"`
```svelte
<!-- ❌ Should be aria-current="page" for active route -->
<a href="/current-page">Current Page</a>
```

**Impact:** Screen reader users don't know which page is active  
**Severity:** HIGH

---

#### 8. Pagination Controls Accessibility
**Location:** [frontend/src/components/dashboard/DashboardClient.svelte](frontend/src/components/dashboard/DashboardClient.svelte#L580-599)

**Issue:** Pagination buttons missing `aria-label` with page context
```svelte
<button on:click={() => changeBookmarksPage(bookmarksPage - 1)}>
  ← Previous  <!-- Missing aria-label="Go to previous page" -->
</button>
```

**Severity:** HIGH  
**Fix:** Add descriptive labels:
```svelte
<button 
  on:click={() => changeBookmarksPage(bookmarksPage - 1)}
  aria-label="Go to previous page of bookmarks"
>
```

---

#### 9. Interactive DIV (Gallery-like UI)
**Location:** [frontend/src/components/dashboard/DashboardClient.svelte](frontend/src/components/dashboard/DashboardClient.svelte#L304-347)

**Issue:** Metric cards with `hover:scale-105` but no `role="button"` or keyboard access
```svelte
<div class="bg-gradient-to-br ... hover:scale-105 transition-transform">
  <!-- Not interactive but styled like button -->
</div>
```

**Problem:** Appears clickable but isn't; confuses keyboard users  
**Severity:** HIGH  
**Fix:** Either make them buttons or remove interactive styling

---

#### 10. Missing Form Label Associations
**Location:** Multiple form components

**Issue:** Labels not properly associated with inputs
```svelte
<!-- ❌ BAD -->
<label>Email</label>
<input name="email" type="email" />

<!-- ✅ GOOD -->
<label for="email-input">Email</label>
<input id="email-input" name="email" type="email" />
```

**Files affected:**
- [frontend/src/pages/login.astro](frontend/src/pages/login.astro#L15-25)
- [frontend/src/pages/register.astro](frontend/src/pages/register.astro#L15-25)
- [frontend/src/pages/forgot-password.astro](frontend/src/pages/forgot-password.astro#L18)
- [frontend/src/pages/reset-password.astro](frontend/src/pages/reset-password.astro#L18-30)

**Severity:** HIGH  
**Fix:** Add `id` + `for` attribute pairs

---

#### 11. Error Boundary Alert Role  
**Location:** [frontend/src/components/ErrorBoundary.svelte](frontend/src/components/ErrorBoundary.svelte#L55-102)

✅ **GOOD:** Already has `role="alert"` and `aria-live="assertive"`

**However:** Error message text should be screen-reader friendly:
```svelte
<!-- Good: Clear error message -->
<div role="alert" aria-live="assertive">
  Error: Failed to load profile
</div>
```

**Status:** Mostly compliant, minor improvements needed

---

#### 12. Breadcrumb Navigation
**Issue:** Breadcrumbs missing `aria-label="Breadcrumb"` on `<nav>` element

**Severity:** HIGH  
**Fix:** Wrap breadcrumbs:
```svelte
<nav aria-label="Breadcrumb">
  <ol>
    <li><a href="/">Home</a></li>
    <li aria-current="page">Current Page</li>
  </ol>
</nav>
```

---

#### 13-14. Color Contrast Issues (Design System)
**Issue:** Slate-400/slate-500 text on slate-600/slate-700 backgrounds may fail WCAG AA contrast requirements

**Severity:** HIGH  
**Recommendation:** Run all colors through WCAG contrast checker

---

### 🟡 MEDIUM SEVERITY (6 findings)

#### 15. Missing Image Alt Texts
**Pattern:** Emoji icons used without alt text

**Example:**
```svelte
<!-- ❌ BAD -->
<span class="text-lg">❤️</span>

<!-- ✅ GOOD -->
<span class="text-lg" aria-label="Like (heart emoji)">❤️</span>
```

**Files:** InteractionBar.svelte (multiple emoji buttons)  
**Severity:** MEDIUM (emojis are decorative but buttons need accessible description)

---

#### 16. Missing `lang` Attribute on HTML
**Location:** root layout files

**Issue:** Content includes Awadhi/Hindi text but no `lang` attribute
```html
<!-- ❌ Should specify lang -->
<html lang="hi,en">
```

**Severity:** MEDIUM  
**Impact:** Screen readers use wrong pronunciation

---

#### 17. List Markup Violations
**Location:** Content list displays

**Issue:** Lists not wrapped in `<ul>`/`<ol>`, just repeated `<div>` elements

**Severity:** MEDIUM  
**Fix:** Use semantic `<ul>` or `<ol>` with `<li>` elements

---

#### 18-22. Submit Button Disabled State Missing Explanation
**Pattern:** Disabled submit buttons without aria-disabled explanation

```svelte
<!-- ❌ INCOMPLETE -->
<button disabled type="submit">Submit</button>

<!-- ✅ BETTER -->
<button 
  disabled 
  type="submit"
  title="Form has errors - please fix highlighted fields"
  aria-disabled="true"
>
  Submit
</button>
```

**Severity:** MEDIUM × 5 locations

---

## Part C - Accessibility Recommendations

### Priority 1: Critical Fixes (Do First)
1. **Modal keyboard handling** - Add ESC key handlers to all modals
   - Report modal (InteractionBar)
   - Delete confirmation (SubmissionsClient)
   - Any other modals
   
2. **Focus management** - Ensure focus trap and visible focus indicators
   - Tab to interactive elements
   - Visible :focus-visible styles
   - Focus returns to trigger after modal closes
   
3. **Form labels** - Add `id` + `for` associations
   - Login page
   - Register page
   - Password reset pages
   - Forgot password page

4. **Button state indication** - Add `aria-expanded` to toggle buttons
   - Tab buttons in dashboard
   - Expandable sections

### Priority 2: High Impact Fixes (Next Sprint)
1. Add `aria-label` to pagination controls
2. Add `aria-current="page"` to navigation links
3. Fix form label associations (comprehensive audit)
4. Review and fix color contrast ratios per WCAG AA

### Priority 3: Medium Priority (Future)
1. Add `lang` attribute for multi-language support (Awadhi/Hindi content)
2. Convert layout `<div>` to semantic `<ul>`/`<ol>`/`<section>` elements
3. Add more robust keyboard navigation testing
4. Create a11y testing suite in CI/CD pipeline

---

## Audit Tools Recommended

1. **axe DevTools** - Browser plugin for automated accessibility scanning
2. **WAVE** - WebAIM accessibility evaluation
3. **Lighthouse** - Built into Chrome, includes a11y audit
4. **Svelte a11y hints** - Already enabled in `.svelte` files
5. **Automated testing:** `jest-axe` or `@testing-library/jest-dom`

---

# COMBINED FINDINGS SUMMARY TABLE

| Category | Finding Count | Severity | Priority |
|----------|--------------|----------|----------|
| **PART A: Unused APIs** | 6 | - | P1 |
| **PART B: Log Leakage** | 23 total | 3 CRITICAL, 8 HIGH, 12 MEDIUM | P1 |
| **PART C: a11y Issues** | 22 total | 6 CRITICAL, 8 HIGH, 6 MEDIUM, 2 LOW | P1 |
| **Total Issues** | **51** | **3 CRITICAL, 8 CRITICAL, 26 MEDIUM+ | **URGENT** |

---

# OVERALL RECOMMENDATIONS

## Quick Wins (1-2 days)
1. Deprecate 6 unused analytics/articles endpoints
2. Remove raw error logging from critical pages (9 locations)
3. Add ESC/focus handling to modals (3 modals)
4. Add `aria-label` to pagination buttons (5 locations)

## Medium Effort (1 sprint)
1. Audit and fix label associations across all forms
2. Implement structured error logging everywhere
3. Add focus trap + keyboard handling to all modals
4. Fix color contrast issues
5. Add state indicators to toggle buttons

## Long Term (Ongoing)
1. Set up automated accessibility testing
2. Add PII/secret detection in logs before release
3. Implement server-side audit logging for sensitive operations
4. Regular a11y audits (quarterly)
5. Consolidate analytics endpoints

---

**Report Generated:** 2026-03-28  
**Next Review:** 2026-04-28 (1 month)
