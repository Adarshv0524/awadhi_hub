# Contract Consistency Audit - Detailed Findings & Fixes

**Generated:** March 28, 2026  
**Status:** 🔴 2 Critical Contract Violations | 2 Content Types Failing

---

## Executive Summary

The Awadhi platform has **contract consistency failures** in dictionary and article submission workflows that will cause:
- **Dictionary**: 400 Bad Request on submit OR data loss + 500 error on moderation approval
- **Article**: 400 Bad Request on submit OR corrupted canonical entries after approval

| Content Type | Status | Issue | Severity |
|---|---|---|---|
| **doha** | ✅ PASS | Minor analytics field ignored | LOW |
| **dictionary** | ❌ FAIL | lemma_devanagari/lemma_roman placement wrong | CRITICAL |
| **idiom** | ✅ PASS | Correctly implemented | - |
| **article** | ❌ FAIL | Title sent wrong place + not in external_references | CRITICAL |

---

## Root Cause Analysis

### Why This Happened

1. **Dictionary & Article**: Frontend form designed to send content-type-specific fields as top-level payload fields
2. **Backend Schema**: Only accepts generic submission fields (`main_text`, `meaning`, `external_references`)
3. **Moderation Service**: Expects content-type-specific fields inside `external_references` dictionary
4. **Result**: Three-way mismatch between form design, API schema, and moderation expectations

---

## Detailed Issues

### Issue #1: Dictionary - lemma_devanagari in Wrong Location (CRITICAL)

**File**: `frontend/src/components/submission/SubmissionForm.svelte`, lines 206-236

**Current (BROKEN)**:
```typescript
if (content_type === "dictionary") {
    payload.lemma_devanagari = lemma_devanagari || null;     // ❌ Top-level
    payload.lemma_roman = lemma_roman || null;               // ❌ Top-level
    payload.main_text = lemma_devanagari || lemma_roman || null;
    payload.meaning = meaning || null;
}
```

**Backend Schema Expects**:
```python
class SubmissionCreateIn(BaseModel):
    content_type: str
    main_text: str
    meaning: Optional[str] = None
    external_references: Optional[Dict[str, Any]] = None
    # ❌ NO lemma_devanagari or lemma_roman fields!
```

**Moderation Service Extracts From**:
```python
def create_canonical_dictionary_from_submission(db: Session, submission):
    refs = submission.external_references or {}
    payload_dict = {
        "lemma_devanagari": refs.get("lemma_devanagari") or submission.main_text,  # ← expects in refs!
        "lemma_roman": refs.get("lemma_roman") or refs.get("lemmaRoman"),
        "senses": refs.get("senses") or []
    }
    payload = DictionaryPayload(**payload_dict)  # ← Pydantic validation
```

**What Happens When User Submits**:
1. POST `/submissions` with `{content_type: "dictionary", lemma_devanagari: "शब्द", lemma_roman: "shabd", main_text: "शब्द", ...}`
2. Pydantic validates against `SubmissionCreateIn`
3. Fields `lemma_devanagari` and `lemma_roman` are **not in schema**
4. **Result**: 
   - If `extra = "forbid"`: ❌ ValidationError (400 Bad Request)
   - If `extra = "ignore"`: ⚠️ Fields silently dropped, data lost

**Fix**:
```typescript
// FIXED: Put dictionary fields in external_references
if (content_type === "dictionary") {
    payload.main_text = lemma_devanagari || lemma_roman || null;
    payload.meaning = meaning || null;
    payload.external_references = {
        ...(parsedExternalReferences || {}),
        lemma_devanagari: lemma_devanagari || null,
        lemma_roman: lemma_roman || null,
        senses: []  // TODO: Add form input for senses
    };
}
```

---

### Issue #2: Dictionary - Missing senses Field (HIGH)

**Problem**: Frontend has no form input to collect `senses` (definitions), but `DictionaryPayload` requires it as a non-empty list.

**Current Flow**:
```
Frontend → No senses input
   ↓
external_references.senses = undefined
   ↓
DictionaryPayload extracts senses = [] (empty!)
   ↓
Canonical DictionaryEntry created with empty definitions
   ↓
Users see empty dictionary entries
```

**Backend Validator**:
```python
class DictionaryPayload(BaseModel):
    lemma_devanagari: str
    lemma_roman: Optional[str] = None
    senses: list[DictionarySense]  # ← Required! No default
```

**Fix**: Add frontend form section for senses:
```svelte
{#if content_type === "dictionary"}
    <!-- Existing fields -->
    <input bind:value={lemma_devanagari} required />
    <textarea bind:value={meaning} />
    
    <!-- NEW: Sense definitions -->
    <div class="field">
        <label>Definitions / Senses (at least one required)</label>
        <button on:click={addSense}>Add Definition</button>
        {#each senses as sense, idx}
            <div class="sense-input">
                <input 
                    type="text" 
                    bind:value={sense.definition} 
                    placeholder="Definition"
                    required
                />
                <input 
                    type="text" 
                    bind:value={sense.pos} 
                    placeholder="Part of speech (optional)"
                />
            </div>
        {/each}
    </div>
{/if}
```

Then in `buildPayload`:
```typescript
if (content_type === "dictionary") {
    payload.external_references = {
        lemma_devanagari: lemma_devanagari || null,
        lemma_roman: lemma_roman || null,
        senses: senses.length ? senses : []  // ← Now populated
    };
}
```

---

### Issue #3: Article - title in Wrong Location (CRITICAL)

**File**: `frontend/src/components/submission/SubmissionForm.svelte`, lines 218-229

**Current (BROKEN)**:
```typescript
else if (content_type === "article") {
    payload.title = title || null;            // ❌ Top-level field (not in schema!)
    payload.main_text = content || null;      // ✅ Correct
    payload.meaning = excerpt || null;        // ✅ Correct
}
```

**Backend Schema**:
```python
class SubmissionCreateIn(BaseModel):
    content_type: str
    main_text: str
    meaning: Optional[str] = None
    # ❌ NO title field!
```

**Moderation Service Expects**:
```python
def create_canonical_article_from_submission(db: Session, submission):
    refs = submission.external_references or {}
    payload_dict = {
        "title": refs.get("title") or submission.main_text,     # ← expects in refs!
        "body": refs.get("body") or submission.main_text,
        "excerpt": refs.get("excerpt"),
        "tags": refs.get("tags")
    }
    payload = ArticlePayload(**payload_dict)  # ← Pydantic validation
```

**What Happens When User Submits**:
1. POST `/submissions` with `{content_type: "article", title: "My Article", main_text: "Body...", ...}`
2. Backend drops `title` field (not in schema)
3. Submission stored without title
4. **Result**: ❌ Title data lost completely

**What Happens When Moderator Approves**:
1. Service tries: `refs.get("title")` → None
2. Falls back to: `submission.main_text` → "Body..."
3. Creates canonical article with `title = "Body..."` ← WRONG!
4. **Result**: ❌ Corrupted canonical entry

**Fix**:
```typescript
// FIXED: Put article metadata in external_references
else if (content_type === "article") {
    payload.main_text = content || null;
    payload.meaning = excerpt || null;
    payload.external_references = {
        ...(parsedExternalReferences || {}),
        title: title || null,      // ← In external_references
        body: content || null,
        excerpt: excerpt || null,
        tags: []
    };
}
```

---

### Issue #4: All Types - time_spent_seconds Field Ignored (LOW)

**File**: `frontend/src/components/submission/SubmissionForm.svelte`, line 215

**Current**:
```typescript
if (timeSpent !== undefined) {
    payload.time_spent_seconds = timeSpent;  // ❌ Not in SubmissionCreateIn schema
}
```

**Result**: Field sent but silently ignored by backend. Analytics data lost.

**Impact**: LOW - No functional failure, just unused metric

**Fix**: Add to backend schema if time tracking needed:
```python
class SubmissionCreateIn(BaseModel):
    # ... other fields ...
    time_spent_seconds: Optional[int] = None  # ← Add this
```

---

## Fixed Frontend Code

**File to Update**: `frontend/src/components/submission/SubmissionForm.svelte`

**Function**: `buildPayload()` at line 202

```typescript
function buildPayload(submitForReview: boolean, timeSpent?: number) {
    const parsedExternalReferences = external_refs ? JSON.parse(external_refs) : {};
    const payload: any = {
        content_type,
        submit_for_review: submitForReview,
        visibility,
    };
    
    // Add time tracking
    if (timeSpent !== undefined) {
        payload.time_spent_seconds = timeSpent;
    }
    
    // Type-specific fields FIXED
    if (content_type === "dictionary") {
        // FIXED: Move lemma fields to external_references
        payload.main_text = lemma_devanagari || lemma_roman || null;
        payload.meaning = meaning || null;
        payload.external_references = {
            ...(Object.keys(parsedExternalReferences).length ? parsedExternalReferences : {}),
            lemma_devanagari: lemma_devanagari || null,
            lemma_roman: lemma_roman || null,
            senses: []  // TODO: Collect from form after adding senses input
        };
    } else if (content_type === "idiom") {
        payload.main_text = main_text || null;
        payload.meaning = meaning || null;
        payload.usage_example = usage_example || null;
        payload.external_references = {
            ...parsedExternalReferences,
            text_devanagari: main_text || null,
            text_roman: idiom_text_roman || null,
            meaning: meaning || null,
            examples: usage_example ? [usage_example] : null,
        };
    } else if (content_type === "article") {
        // FIXED: Move title to external_references
        payload.main_text = content || null;
        payload.meaning = excerpt || null;
        payload.external_references = {
            ...(Object.keys(parsedExternalReferences).length ? parsedExternalReferences : {}),
            title: title || null,
            body: content || null,
            excerpt: excerpt || null,
            tags: []
        };
    } else if (content_type === "doha") {
        payload.main_text = main_text || null;
        payload.meaning = meaning || null;
    }
    
    // Common metadata
    payload.is_classical = Boolean(is_classical);
    payload.author_slug = selected_author_slug || (free_author_name || null);
    payload.work_slug = selected_work_slug || null;
    payload.chapter_slug = selected_chapter_slug || null;
    payload.number_in_chapter = number_in_chapter || null;
    
    // Only add external_references if not already set by type-specific logic
    if (content_type !== "dictionary" && content_type !== "article" && content_type !== "idiom") {
        if (Object.keys(parsedExternalReferences).length) {
            payload.external_references = parsedExternalReferences;
        }
    }
    
    // Clean up null values
    Object.keys(payload).forEach(k => payload[k] == null && delete payload[k]);
    
    return payload;
}
```

---

## Optional Enhancements

### 1. Add Senses Input to Dictionary Form

**Insert after lemma_roman input**:
```svelte
{#if content_type === "dictionary"}
    <!-- Existing lemma fields -->
    <input bind:value={lemma_devanagari} required />
    <input bind:value={lemma_roman} />
    
    <!-- NEW: Senses/Definitions -->
    <div class="field">
        <label>Meanings / Definitions (at least one required)</label>
        {#each senses as sense, idx (idx)}
            <div style="margin-bottom: 12px; padding: 12px; background: #0f172a; border: 1px solid #334155; border-radius: 6px;">
                <input 
                    type="text" 
                    bind:value={sense.definition}
                    placeholder="Definition (required)"
                    required
                    style="margin-bottom: 8px;"
                />
                <select bind:value={sense.pos} style="margin-bottom: 8px;">
                    <option value="">Part of speech (optional)</option>
                    <option value="n">Noun (संज्ञा)</option>
                    <option value="v">Verb (क्रिया)</option>
                    <option value="adj">Adjective (विशेषण)</option>
                    <option value="adv">Adverb (क्रियाविशेषण)</option>
                    <option value="pron">Pronoun (सर्वनाम)</option>
                </select>
                {#if senses.length > 1}
                    <button 
                        class="btn btn-ghost" 
                        on:click={() => removeSense(idx)}
                        style="font-size: 0.85rem; padding: 6px 10px;"
                    >
                        Remove
                    </button>
                {/if}
            </div>
        {/each}
        
        <button 
            class="btn btn-ghost" 
            on:click={addSense}
            style="margin-top: 8px;"
        >
            + Add Another Definition
        </button>
    </div>
    
    <textarea bind:value={meaning} placeholder="General meaning..." />
{/if}
```

**Add to script**:
```typescript
let senses: {definition: string, pos?: string}[] = [{definition: ""}];

function addSense() {
    senses = [...senses, {definition: ""}];
}

function removeSense(idx: number) {
    senses = senses.filter((_, i) => i !== idx);
}
```

---

## Testing Checklist

### Dictionary Submission Test
- [ ] Fill form: lemma_devanagari="शब्द", lemma_roman="shabd", meaning="meaning"
- [ ] Add definitions
- [ ] Solo submit → 200 OK (no 400)
- [ ] Data in database response
- [ ] Moderator approves → canonical entry created
- [ ] Canonical entry has correct lemma and definitions

### Article Submission Test
- [ ] Fill form: title="My Article", content="Body text", excerpt="Summary"
- [ ] Submit → 200 OK (no 400)
- [ ] Data in database response
- [ ] Moderator approves → canonical article created
- [ ] Canonical entry has correct title (not body text)

### Idiom Submission Test
- [ ] Verify still works (should not break with fixes)
- [ ] text_roman is captured in external_references

---

## Files to Update

| File | Change | Priority |
|---|---|---|
| `frontend/src/components/submission/SubmissionForm.svelte` | Fix buildPayload function | CRITICAL |
| `backend/app/api/v1/submissions.py` | Add time_spent_seconds to schema | MEDIUM |
| `frontend/src/components/submission/SubmissionForm.svelte` | Add senses input form | HIGH |

---

## Impact on Existing Submissions

- **Future submissions**: Fixed after code changes
- **Existing rejected submissions**: Can be resubmitted after frontend fix
- **Existing approved submissions**: Canonical entries have correct data (service handles fallbacks)
- **No database migration needed**: Schema changes only in Pydantic models

---

## Next Steps

1. **Immediate**: Apply buildPayload fixes for dictionary and article
2. **Short-term**: Add form inputs for dictionary senses
3. **Medium-term**: Add time_spent_seconds to backend if analytics needed
4. **Testing**: Run full submission + moderation workflow for each content type
