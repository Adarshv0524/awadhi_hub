# Content Module Audit Report
**Date:** December 30, 2025  
**Scope:** Backend API endpoints and Frontend pages for Doha, Dictionary, Idioms, and Articles

---

## Executive Summary

This audit examines four content modules (Doha, Dictionary, Idioms, Articles) comparing backend API responses with frontend UI implementation. **Major findings:**

1. **Engagement Data NOT Displayed**: Backend tracks `views_count`, `likes_count`, `shares_count`, `bookmarks_count` in `EngagementKPI` table but this data is **NEVER returned** to frontend
2. **Missing Backend Fields**: Response schemas exclude critical fields like timestamps (`created_at`, `updated_at`), verification data, and source references
3. **Incomplete UI States**: Several pages lack proper loading/empty/error states
4. **SEO Gaps**: Metadata incomplete; engagement metrics not used for rich snippets
5. **Unused Frontend References**: Frontend expects fields that backend doesn't provide

---

## 1. DOHA Module (`/content/doha`)

### Backend: `content.py`

**Endpoint:** `GET /content/doha`  
**Response Model:** `DohaOut` (Lines 15-31)

#### Fields SENT by Backend:
```python
- id, hierarchy_path, author_id, work_id, chapter_id, number_in_chapter
- main_text, meaning, text_devanagari, text_romanized
- status, visibility, version, is_canonical, confidence_level
```

#### Fields IGNORED (available in DB but NOT in response schema):
- ❌ `created_at` - Available in model (line 192), **NOT in DohaOut schema**
- ❌ `updated_at` - Available in model (line 193), **NOT in DohaOut schema**
- ❌ `source_reference` - Available in model (line 185), **NOT in DohaOut schema**
- ❌ `source_submission_id` - Available in model (line 186), **NOT in DohaOut schema**
- ❌ `verified_by` - Available in model (line 188), **NOT in DohaOut schema**
- ❌ `verified_at` - Available in model (line 189), **NOT in DohaOut schema**
- ❌ `created_by` - Available in model (line 187), **NOT in DohaOut schema**
- ❌ **ALL ENGAGEMENT DATA** - Never joined or returned:
  - `views_count`, `likes_count`, `shares_count`, `bookmarks_count`, `search_hits_count`

### Frontend: `doha.astro` & `doha/[id].astro`

#### List Page (`doha.astro`, Lines 1-31)
**Issues:**
- ✅ Has error state (line 22)
- ⚠️ **NO loading state** - SSR means no spinner, but could show skeleton
- ❌ **NO empty state** - If `items.length === 0`, shows nothing
- ⚠️ Uses `title ?? main_text ?? Doha ${id}` - but backend never sends `title` field

#### Detail Page (`doha/[id].astro`)
**Issues:**
- ✅ Has error handling (redirects to 404)
- ❌ **NO loading state** (SSR page)
- ✅ Uses `TrustSignals` component but expects fields backend doesn't send:
  - Line 68: `sourceReference={doha.source_reference}` - **NOT in backend response**
  - Line 69: `verifiedBy={doha.verified_by}` - **NOT in backend response**
  - Line 70: `verifiedAt={doha.verified_at}` - **NOT in backend response**
- ✅ Uses `ModerationInfo` component expecting:
  - Line 84: `createdAt={doha.created_at}` - **NOT in backend response**
  - Line 85: `updatedAt={doha.updated_at}` - **NOT in backend response**
- ⚠️ `InteractionBar` component (lines 93-99):
  - Expects: `likes={doha?.likes_count ?? 0}` - **Field doesn't exist in response**
  - Expects: `bookmarks={doha?.bookmarks_count ?? 0}` - **Field doesn't exist**
  - Expects: `shares={doha?.shares_count ?? 0}` - **Field doesn't exist**
  - **Result:** All counts default to 0, even if DB has data

**SEO Issues:**
- ✅ Has StructuredData for CreativeWork (line 27)
- ❌ StructuredData uses `doha.created_at` (line 32) - **field not in response**
- ❌ StructuredData uses `doha.author_name` (line 33) - **field doesn't exist**
- ❌ StructuredData uses `doha.work_name` (line 34) - **field doesn't exist**

---

## 2. DICTIONARY Module (`/dictionary`)

### Backend: `dictionary.py`

**Endpoint:** `GET /dictionary`  
**Response Model:** `DictionaryOut` (Lines 18-25)

#### Fields SENT by Backend:
```python
- id, lemma_devanagari, lemma_roman, language, version
```

**Detail Endpoint:** `GET /dictionary/{entry_id}`  
**Response Model:** `DictionaryDetailOut` (Lines 28-31)
```python
- (inherits DictionaryOut fields)
- senses, pronunciation, examples
```

#### Fields IGNORED (in DB but NOT in response):
- ❌ `lemma_roman_norm` - Used for search (line 99), but not exposed
- ❌ `contributor_id` - DB field, not returned
- ❌ `author_id` - DB field, not returned  
- ❌ `work_id`, `chapter_id`, `number_in_chapter` - DB fields, not returned
- ❌ `source_submission_id` - DB field, not returned
- ❌ `created_at` - **NOT in response schema**
- ❌ `updated_at` - **NOT in response schema**
- ❌ **ALL ENGAGEMENT DATA** - Never joined or returned:
  - Backend TRACKS views via `_inc_view_kpi()` (lines 64-81)
  - Backend TRACKS search hits via `_inc_search_kpi()` (lines 37-59)
  - **But data never returned to frontend**

### Frontend: `dictionary.astro` & `dictionary/[id].astro`

#### List Page (`dictionary.astro`, Lines 1-58)
**Issues:**
- ✅ Has error state (lines 28-32)
- ✅ Has empty state (lines 49-53)
- ❌ **NO loading state**
- ⚠️ Shows "Showing up to 100 entries" but only displays `id`, `lemma_devanagari`, `lemma_roman`
  - Could show `language` field (available in response)

#### Detail Page (`dictionary/[id].astro`)
**Issues:**
- ✅ Has error handling (404 redirect)
- ❌ **NO loading state**
- ✅ Uses `TrustSignals` component but expects unavailable fields:
  - Lines 70-74: `is_canonical`, `confidence_level`, `source_reference`, `verified_by`, `verified_at` - **NONE in backend response**
- ❌ `ModerationInfo` component expects `created_at`, `updated_at` - **NOT in response**
- ⚠️ `InteractionBar` (lines 105-111):
  - `likes={entry?.likes_count ?? 0}` - **Field doesn't exist, always 0**
  - `bookmarks={entry?.bookmarks_count ?? 0}` - **Field doesn't exist**
  - `shares={entry?.shares_count ?? 0}` - **Field doesn't exist**

**SEO Issues:**
- ✅ Has canonical link, meta description
- ✅ Has StructuredData for DefinedTerm
- ❌ Missing engagement signals (view count, rating) for rich snippets

---

## 3. IDIOMS Module (`/idioms`)

### Backend: `idiom.py`

**Endpoint:** `GET /idioms`  
**Response Model:** `IdiomOut` (Lines 18-25)

#### Fields SENT by Backend:
```python
- id, text_devanagari, text_roman, meaning, version
```

#### Fields IGNORED (in DB but NOT returned):
- ❌ `text_roman_norm` - Used for search, not exposed
- ❌ `examples` - DB field (JSONB), **NOT in response schema**
- ❌ `region` - DB field, not returned
- ❌ `contributor_id`, `author_id`, `work_id`, `chapter_id`, `number_in_chapter` - DB fields, not returned
- ❌ `source_submission_id` - DB field, not returned
- ❌ `created_at` - **NOT in response schema**
- ❌ `updated_at` - **NOT in response schema**
- ❌ **ALL ENGAGEMENT DATA** - Never joined or returned:
  - Backend TRACKS views via `_inc_view_kpi()` (lines 54-71)
  - Backend TRACKS search hits via `_inc_search_kpi()` (lines 34-51)
  - **Data never sent to frontend**

### Frontend: `idioms.astro` & `idioms/[id].astro`

#### List Page (`idioms.astro`, Lines 1-64)
**Issues:**
- ✅ Has error state (lines 36-40)
- ✅ Has empty state (lines 57-61)
- ❌ **NO loading state**
- ✅ Displays `text_devanagari`, `text_roman`, `meaning` (all available)

#### Detail Page (`idioms/[id].astro`)
**Issues:**
- ✅ Has error state (line 21)
- ✅ Has error handling (404 redirect)
- ❌ **NO loading state**
- ✅ Uses `TrustSignals` expecting:
  - Lines 83-87: `is_canonical`, `confidence_level`, `source_reference`, `verified_by`, `verified_at` - **NONE in backend response**
- ❌ `ModerationInfo` expects:
  - Lines 119-123: `created_at`, `updated_at` - **NOT in response**
- ❌ Tries to display `idiom.usage` (line 107) - **Field doesn't exist in backend**
- ❌ References `idiom.created_at` in StructuredData (line 53) - **NOT in response**
- ⚠️ `InteractionBar` (lines 134-140):
  - All counts default to 0 (backend doesn't send engagement data)

**SEO Issues:**
- ✅ Has canonical link, meta description
- ✅ Has StructuredData
- ❌ Uses unavailable field `created_at` in schema

---

## 4. ARTICLES Module (`/articles`)

### Backend: `article.py`

**Endpoint:** `GET /articles`  
**Response Model:** `ArticleListOut` (Lines 60-70)

#### Fields SENT by Backend (List):
```python
- id, title, title_devanagari, title_roman, excerpt, tags, version, created_at
```

**Detail Endpoint:** `GET /articles/{article_id}`  
**Response Model:** `ArticleDetailOut` (Lines 72-88)
```python
- id, title, title_devanagari, title_roman, title_roman_norm
- body, excerpt, author_id, tags, contributor_id
- source_submission_id, visibility, version
- created_at, updated_at
```

#### Fields IGNORED (in DB but NOT returned):
- ❌ **ALL ENGAGEMENT DATA** - Never joined or returned:
  - Backend TRACKS views via `_inc_view_kpi()` (lines 42-59)
  - Backend TRACKS search hits via `_inc_search_kpi()` (lines 21-39)
  - `views_count`, `likes_count`, `shares_count`, `bookmarks_count` exist in DB
  - **NOT included in ArticleDetailOut schema**

**Note:** Articles endpoint is better than others - it DOES return `created_at` and `updated_at`!

### Frontend: `articles.astro` & `articles/[id].astro`

#### List Page (`articles.astro`, Lines 1-36)
**Issues:**
- ✅ Has error state (line 20)
- ❌ **NO loading state**
- ❌ **NO empty state** - If `articles.length === 0`, shows nothing
- ⚠️ Expects `summary` field (line 33) - **Backend sends `excerpt`, not `summary`**
  - This is a **naming mismatch** between frontend TypeScript type and backend response

#### Detail Page (`articles/[id].astro`)
**Issues:**
- ✅ Has error handling (404 redirect)
- ❌ **NO loading state**
- ✅ Uses `TrustSignals` expecting:
  - Lines 70-74: `is_canonical`, `confidence_level`, `source_reference`, `verified_by`, `verified_at` - **NOT in ArticleDetailOut**
- ✅ `ModerationInfo` component:
  - Lines 91-96: Uses `created_at`, `updated_at` - **THESE EXIST in backend response!**
  - ✅ **This module is correctly implemented for timestamps**
- ⚠️ `InteractionBar` (lines 101-107):
  - `likes={article?.likes_count ?? 0}` - **Field doesn't exist, always 0**
  - `bookmarks={article?.bookmarks_count ?? 0}` - **Field doesn't exist**
  - `shares={article?.shares_count ?? 0}` - **Field doesn't exist**
- ❌ StructuredData uses `article.author_name` (line 48) - **Backend only sends `author_id`**

**SEO Issues:**
- ✅ Has canonical link, meta description
- ✅ Has StructuredData for Article
- ❌ Missing author name (only ID provided)
- ❌ No engagement metrics in schema

---

## Summary of Critical Issues

### 1. **ENGAGEMENT DATA COMPLETELY MISSING** ❌❌❌

**Problem:** All 4 modules track engagement in DB but NEVER return it to frontend

| Module | Backend Tracks | Sends to Frontend | Result |
|--------|---------------|-------------------|---------|
| Doha | ✅ views, likes, shares, bookmarks | ❌ NO | Always shows 0 |
| Dictionary | ✅ views, likes, shares, bookmarks | ❌ NO | Always shows 0 |
| Idioms | ✅ views, likes, shares, bookmarks | ❌ NO | Always shows 0 |
| Articles | ✅ views, likes, shares, bookmarks | ❌ NO | Always shows 0 |

**Location of Issue:**
- Backend response schemas exclude engagement fields:
  - [content.py](backend/app/api/v1/content.py#L15-L31) - `DohaOut` schema
  - [dictionary.py](backend/app/api/v1/dictionary.py#L18-L31) - `DictionaryOut` schema
  - [idiom.py](backend/app/api/v1/idiom.py#L18-L25) - `IdiomOut` schema
  - [article.py](backend/app/api/v1/article.py#L60-L88) - `ArticleListOut` & `ArticleDetailOut` schemas

**Frontend Expects But Never Gets:**
- [doha/[id].astro](frontend/src/pages/doha/[id].astro#L93-L99) - InteractionBar
- [dictionary/[id].astro](frontend/src/pages/dictionary/[id].astro#L105-L111) - InteractionBar
- [idioms/[id].astro](frontend/src/pages/idioms/[id].astro#L134-L140) - InteractionBar
- [articles/[id].astro](frontend/src/pages/articles/[id].astro#L101-L107) - InteractionBar

---

### 2. **TIMESTAMP DATA MISSING** (except Articles)

| Module | `created_at` in DB | Sent to Frontend | `updated_at` in DB | Sent to Frontend |
|--------|-------------------|------------------|-------------------|------------------|
| Doha | ✅ | ❌ | ✅ | ❌ |
| Dictionary | ✅ | ❌ | ✅ | ❌ |
| Idioms | ✅ | ❌ | ✅ | ❌ |
| Articles | ✅ | ✅ | ✅ | ✅ |

**Frontend Uses But Doesn't Receive:**
- [doha/[id].astro](frontend/src/pages/doha/[id].astro#L84-L85) - ModerationInfo component
- [dictionary/[id].astro](frontend/src/pages/dictionary/[id].astro#L105-L111) - ModerationInfo (not rendered currently)
- [idioms/[id].astro](frontend/src/pages/idioms/[id].astro#L119-L123) - ModerationInfo component

---

### 3. **VERIFICATION/TRUST DATA MISSING**

All detail pages use `TrustSignals` component expecting:
- `is_canonical`
- `confidence_level`
- `source_reference`
- `verified_by`
- `verified_at`

**Status:**

| Module | Fields in DB | Sent to Frontend |
|--------|-------------|------------------|
| Doha | `is_canonical`, `confidence_level` ✅ | `is_canonical`, `confidence_level` ✅ / Others ❌ |
| Dictionary | ❌ None exist | ❌ |
| Idioms | ❌ None exist | ❌ |
| Articles | ❌ None exist | ❌ |

**Note:** Only `DohaEntry` model has these trust fields, but `source_reference`, `verified_by`, `verified_at` are not in response schema.

---

### 4. **MISSING UI STATES**

| Page | Loading State | Empty State | Error State |
|------|--------------|-------------|-------------|
| doha.astro | ❌ | ❌ | ✅ |
| doha/[id].astro | ❌ | N/A | ✅ |
| dictionary.astro | ❌ | ✅ | ✅ |
| dictionary/[id].astro | ❌ | N/A | ✅ |
| idioms.astro | ❌ | ✅ | ✅ |
| idioms/[id].astro | ❌ | N/A | ✅ |
| articles.astro | ❌ | ❌ | ✅ |
| articles/[id].astro | ❌ | N/A | ✅ |

**Note:** Loading states less critical for SSR pages, but empty states are important.

---

### 5. **FIELD NAME MISMATCHES**

| Frontend Reference | Backend Sends | Issue |
|-------------------|---------------|-------|
| `article.summary` | `excerpt` | [articles.astro:33](frontend/src/pages/articles.astro#L33) expects `summary` |
| `doha.title` | (none) | [doha.astro:27](frontend/src/pages/doha.astro#L27) - backend has no `title` field |
| `article.author_name` | `author_id` | [articles/[id].astro:48](frontend/src/pages/articles/[id].astro#L48) - only ID available |
| `doha.author_name` | `author_id` | [doha/[id].astro:33](frontend/src/pages/doha/[id].astro#L33) - only ID available |
| `doha.work_name` | `work_id` | [doha/[id].astro:34](frontend/src/pages/doha/[id].astro#L34) - only ID available |
| `idiom.usage` | (none) | [idioms/[id].astro:107](frontend/src/pages/idioms/[id].astro#L107) - doesn't exist |

---

### 6. **SEO GAPS**

#### Structured Data Issues:
- ❌ `doha/[id].astro` - Uses undefined fields: `created_at`, `author_name`, `work_name`
- ❌ `idioms/[id].astro` - Uses undefined field: `created_at`
- ❌ `articles/[id].astro` - Uses undefined field: `author_name`

#### Missing Rich Snippet Opportunities:
- ❌ No engagement metrics (view counts, ratings) in any structured data
- ❌ No `dateModified` in Doha, Dictionary, Idioms (Articles has it)
- ❌ No author information (only IDs, not names)

---

## Detailed Line-by-Line Issues

### DOHA

#### Backend (`content.py`):
- **Line 15-31:** `DohaOut` schema missing: `created_at`, `updated_at`, `source_reference`, `verified_by`, `verified_at`, `created_by`, engagement fields

#### Frontend (`doha.astro`):
- **Line 7:** TypeScript type has `title?` field that backend never sends
- **Line 22:** Error state ✅
- **Line 26:** No empty state for `items.length === 0` ❌
- **Line 27:** Uses `it.title` (doesn't exist) ❌

#### Frontend (`doha/[id].astro`):
- **Line 27-34:** StructuredData uses `created_at`, `author_name`, `work_name` (none available) ❌
- **Line 68-70:** TrustSignals uses `source_reference`, `verified_by`, `verified_at` (not in response) ❌
- **Line 84-85:** ModerationInfo uses `created_at`, `updated_at` (not in response) ❌
- **Line 93-99:** InteractionBar uses `likes_count`, `bookmarks_count`, `shares_count` (all undefined, default to 0) ❌

---

### DICTIONARY

#### Backend (`dictionary.py`):
- **Line 18-25:** `DictionaryOut` missing: `created_at`, `updated_at`, engagement fields
- **Line 28-31:** `DictionaryDetailOut` missing: same as above

#### Frontend (`dictionary.astro`):
- **Line 28-32:** Error state ✅
- **Line 49-53:** Empty state ✅
- **No loading state** ❌

#### Frontend (`dictionary/[id].astro`):
- **Line 70-74:** TrustSignals uses fields that don't exist in DictionaryEntry model ❌
- **Line 105-111:** InteractionBar uses engagement fields (all undefined) ❌
- **ModerationInfo not rendered** (commented out or missing)

---

### IDIOMS

#### Backend (`idiom.py`):
- **Line 18-25:** `IdiomOut` missing: `examples`, `region`, `created_at`, `updated_at`, engagement fields

#### Frontend (`idioms.astro`):
- **Line 36-40:** Error state ✅
- **Line 57-61:** Empty state ✅
- **No loading state** ❌

#### Frontend (`idioms/[id].astro`):
- **Line 53:** StructuredData uses `created_at` (not in response) ❌
- **Line 83-87:** TrustSignals uses fields that don't exist ❌
- **Line 107:** Tries to render `idiom.usage` (doesn't exist) ❌
- **Line 119-123:** ModerationInfo uses `created_at`, `updated_at` (not in response) ❌
- **Line 134-140:** InteractionBar uses engagement fields (all undefined) ❌

---

### ARTICLES

#### Backend (`article.py`):
- **Line 60-70:** `ArticleListOut` missing: engagement fields, author info
- **Line 72-88:** `ArticleDetailOut` missing: engagement fields, author info
- **Note:** ✅ DOES include `created_at` and `updated_at` (only module that does!)

#### Frontend (`articles.astro`):
- **Line 6:** TypeScript type has `summary?` but backend sends `excerpt` ❌
- **Line 20:** Error state ✅
- **Line 33:** Uses `article.summary` instead of `article.excerpt` ❌
- **No empty state** ❌

#### Frontend (`articles/[id].astro`):
- **Line 48:** StructuredData uses `article.author_name` (only `author_id` available) ❌
- **Line 70-74:** TrustSignals uses fields that don't exist ❌
- **Line 91-96:** ModerationInfo uses `created_at`, `updated_at` ✅ (These exist!) 
- **Line 101-107:** InteractionBar uses engagement fields (all undefined) ❌

---

## Recommendations (NOT IMPLEMENTED - For Reference Only)

### High Priority:
1. **Add engagement data to ALL response schemas** - Join `EngagementKPI` table
2. **Add `created_at`/`updated_at` to Doha, Dictionary, Idioms** - Copy Articles pattern
3. **Fix field name mismatches** - `summary` vs `excerpt`, etc.
4. **Add empty states** to list pages

### Medium Priority:
5. **Add author/work names** - Join User/hierarchy tables instead of just IDs
6. **Fix StructuredData** - Use only available fields or fetch missing data
7. **Add `examples` field to IdiomOut** - It's in DB but not returned

### Low Priority:
8. **Add loading skeletons** for SSR pages (progressive enhancement)
9. **Add trust fields** to Dictionary/Idioms/Articles models (if needed)

---

## Appendix: File Locations

### Backend API Files:
- [content.py](backend/app/api/v1/content.py) - Doha endpoints
- [dictionary.py](backend/app/api/v1/dictionary.py) - Dictionary endpoints
- [idiom.py](backend/app/api/v1/idiom.py) - Idioms endpoints
- [article.py](backend/app/api/v1/article.py) - Articles endpoints
- [interactions.py](backend/app/api/v1/interactions.py) - Like/bookmark/share endpoints
- [models.py](backend/app/db/models.py) - Database models

### Frontend Pages:
- [doha.astro](frontend/src/pages/doha.astro)
- [doha/[id].astro](frontend/src/pages/doha/[id].astro)
- [dictionary.astro](frontend/src/pages/dictionary.astro)
- [dictionary/[id].astro](frontend/src/pages/dictionary/[id].astro)
- [idioms.astro](frontend/src/pages/idioms.astro)
- [idioms/[id].astro](frontend/src/pages/idioms/[id].astro)
- [articles.astro](frontend/src/pages/articles.astro)
- [articles/[id].astro](frontend/src/pages/articles/[id].astro)

### Frontend Components:
- [InteractionBar.svelte](frontend/src/components/interaction/InteractionBar.svelte)
- [TrustSignals.svelte](frontend/src/components/content/TrustSignals.svelte)
- [ModerationInfo.svelte](frontend/src/components/content/ModerationInfo.svelte)

---

**End of Report**
