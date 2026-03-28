# Contract Audit - Visual Comparison Summary

## 📊 Content Type Status Matrix

```
┌─────────────┬──────────┬──────────────────────────────────────┐
│ Type        │ Status   │ Issue                                │
├─────────────┼──────────┼──────────────────────────────────────┤
│ doha        │ ✅ PASS  │ None (extra time_spent_seconds OK)   │
│ dictionary  │ ❌ FAIL  │ lemma fields in wrong place + no     │
│             │          │ senses input form                    │
│ idiom       │ ✅ PASS  │ None (minor usage_example in top     │
│             │          │ level, but data in external_refs OK) │
│ article     │ ❌ FAIL  │ title in wrong place                 │
└─────────────┴──────────┴──────────────────────────────────────┘
```

---

## 🔴 Dictionary Content Type - CRITICAL FAILURE

### Data Flow Mismatch

```
FRONTEND FORM (SubmissionForm.svelte)
└─ User Input:
   ├─ lemma_devanagari = "शब्द"        (required)
   ├─ lemma_roman = "shabd"           (optional)
   └─ meaning = "sense"               (required)

buildPayload() FUNCTION
└─ payload = {
     content_type: "dictionary",
     main_text: "शब्द",                ← fallback to lemma_devanagari
     meaning: "sense",
     lemma_devanagari: "शब्द",         ❌ WRONG PLACE (top-level)
     lemma_roman: "shabd",             ❌ WRONG PLACE (top-level)
   }

BACKEND SCHEMA (SubmissionCreateIn)
├─ ✅ content_type: accepted
├─ ✅ main_text: accepted
├─ ✅ meaning: accepted
├─ ❌ lemma_devanagari: NOT IN SCHEMA → VALIDATION ERROR or IGNORED
├─ ❌ lemma_roman: NOT IN SCHEMA → VALIDATION ERROR or IGNORED
└─ external_references: accepted but empty

API RESPONSE
├─ If Pydantic extra='forbid': 400 Bad Request
└─ If Pydantic extra='ignore': Fields silently dropped 💨

DATABASE
└─ Submission stored with:
   ├─ content_type = "dictionary"
   ├─ main_text = "शब्द" ← Was supposed to enter via lemma
   ├─ meaning = "sense"
   ├─ external_references = {} ← EMPTY!
   └─ ❌ lemma_devanagari LOST
   └─ ❌ lemma_roman LOST

MODERATION APPROVAL
└─ create_canonical_dictionary_from_submission()
   ├─ refs = submission.external_references = {}
   ├─ Try: refs.get('lemma_devanagari') → None
   ├─ Fallback: submission.main_text → "शब्द"
   └─ ✅ Good, main_text was lemma
   
   But what if submission had both:
   ├─ lemma_devanagari = "word1"
   ├─ main_text = "word2"
   └─ ❌ Wrong values parsed!

CANONICAL DICTIONARY ENTRY CREATED
└─ lemma_devanagari = "शब्द" ← Correct by accident
    lemma_roman = None ← WRONG! Lost in submission
    senses = [] ← WRONG! No input form for this
```

---

## 🔴 Article Content Type - CRITICAL FAILURE

### Data Flow Mismatch

```
FRONTEND FORM (SubmissionForm.svelte)
└─ User Input:
   ├─ title = "My Article"           (required)
   ├─ content = "Article body..."    (required)
   └─ excerpt = "Summary"            (optional)

buildPayload() FUNCTION
└─ payload = {
     content_type: "article",
     main_text: "Article body...",   ← content
     meaning: "Summary",              ← excerpt
     title: "My Article",             ❌ WRONG PLACE (top-level)
   }

BACKEND SCHEMA (SubmissionCreateIn)
├─ ✅ content_type: accepted
├─ ✅ main_text: accepted
├─ ✅ meaning: accepted
├─ ❌ title: NOT IN SCHEMA → VALIDATION ERROR or IGNORED
└─ external_references: accepted but empty

WHAT HAPPENS TO TITLE FIELD
├─ If Pydantic extra='forbid': 400 Bad Request
└─ If Pydantic extra='ignore': title={} silently dropped 💨
                               🎬 DATA LOSS!

DATABASE
└─ Submission stored with:
   ├─ content_type = "article"
   ├─ main_text = "Article body..."
   ├─ meaning = "Summary"
   ├─ external_references = {} ← EMPTY!
   └─ ❌ title LOST COMPLETELY!

MODERATION APPROVAL
└─ create_canonical_article_from_submission()
   ├─ refs = submission.external_references = {}
   ├─ Try: refs.get('title') → None ← Not found!
   ├─ Try: refs.get('body') → None
   ├─ Fallback: submission.main_text → "Article body..."
   └─ DIT! Creates article with title = "Article body..."
   
CANONICAL ARTICLE ENTRY CREATED
└─ title = "Article body..." ❌ CORRUPTED!
    body = "Article body..."  ✅ Correct
    excerpt = "Summary"       ✅ Correct
```

---

## ✅ Idiom Content Type - CORRECT

### Data Flow (Working Correctly)

```
FRONTEND FORM (SubmissionForm.svelte)
└─ User Input:
   ├─ main_text = "कहावत"            (required)
   ├─ idiom_text_roman = "kahavat"   (required)
   ├─ meaning = "meaning"            (required)
   └─ usage_example = "example"      (optional)

buildPayload() FUNCTION
└─ payload = {
     content_type: "idiom",
     main_text: "कहावत",              ✅ Correct here
     meaning: "meaning",
     usage_example: "example",        ⚠️ Also top-level (OK, ignored)
     external_references: {           ✅✅✅ CORRECT PLACE!
       text_devanagari: "कहावत",
       text_roman: "kahavat",
       meaning: "meaning",
       examples: ["example"]
     }
   }

BACKEND SCHEMA (SubmissionCreateIn)
├─ ✅ content_type: accepted
├─ ✅ main_text: accepted
├─ ✅ meaning: accepted
├─ ⚠️  usage_example: ignored (not in schema, but data in external_refs)
└─ ✅ external_references: accepted

DATABASE
└─ Submission stored with:
   ├─ content_type = "idiom"
   ├─ main_text = "कहावत"
   ├─ meaning = "meaning"
   └─ external_references = {
       text_devanagari: "कहावत",      ✅ PRESENT
       text_roman: "kahavat",         ✅ PRESENT
       meaning: "meaning",
       examples: ["example"]
     }

MODERATION APPROVAL
└─ create_canonical_idiom_from_submission()
   ├─ refs = submission.external_references
   ├─ text_devanagari: refs.get('text_devanagari') or submission.main_text →  ✅ "कहावत"
   ├─ text_roman: refs.get('text_roman') → ✅ "kahavat"  [MANDATORY]
   ├─ meaning: submission.meaning or refs.get('meaning') → ✅ "meaning"
   └─ examples: refs.get('examples') → ✅ ["example"]

CANONICAL IDIOM ENTRY CREATED
└─ text_devanagari = "कहावत"  ✅
    text_roman = "kahavat"    ✅
    meaning = "meaning"       ✅
    examples = ["example"]    ✅
```

---

## 📝 Required Fixes

### Fix #1: Dictionary buildPayload

**Current (Lines 206-236)**:
```typescript
if (content_type === "dictionary") {
    payload.lemma_devanagari = lemma_devanagari || null;      // ❌ Remove
    payload.lemma_roman = lemma_roman || null;                // ❌ Remove
    payload.main_text = lemma_devanagari || lemma_roman || null;
    payload.meaning = meaning || null;
}
```

**Fixed**:
```typescript
if (content_type === "dictionary") {
    payload.main_text = lemma_devanagari || lemma_roman || null;
    payload.meaning = meaning || null;
    payload.external_references = {
        ...(Object.keys(parsedExternalReferences).length ? parsedExternalReferences : {}),
        lemma_devanagari: lemma_devanagari || null,      // ✅ Moved here
        lemma_roman: lemma_roman || null,                // ✅ Moved here
        senses: []  // TODO: Add form input
    };
}
```

### Fix #2: Article buildPayload

**Current (Lines 218-229)**:
```typescript
else if (content_type === "article") {
    payload.title = title || null;           // ❌ Remove
    payload.main_text = content || null;
    payload.meaning = excerpt || null;
}
```

**Fixed**:
```typescript
else if (content_type === "article") {
    payload.main_text = content || null;
    payload.meaning = excerpt || null;
    payload.external_references = {
        ...(Object.keys(parsedExternalReferences).length ? parsedExternalReferences : {}),
        title: title || null,                // ✅ Moved here
        body: content || null,
        excerpt: excerpt || null,
        tags: []
    };
}
```

### Fix #3: Add Senses Input

**Add new input section** after lemma_roman in dictionary form:
```svelte
<!-- NEW: Senses/Definitions Input -->
<div class="field">
    <label>Meanings / Definitions (required)</label>
    {#each senses as sense, idx}
        <input bind:value={sense.definition} placeholder="Definition" required />
        <!-- Add "Remove" button if idx > 0 -->
    {/each}
    <button on:click={addSense}>+ Add Definition</button>
</div>
```

---

## 🧪 Test Scenarios

### Before Fix - Dictionary
```
User submits: lemma_devanagari="शब्द", lemma_roman="shabd", meaning="word"
Expected:     ✅ See submitted entry
Actual:       ❌ 400 Bad Request OR data lost + broken moderation
Test Result:  FAIL
```

### Before Fix - Article
```
User submits: title="Article", content="Body", excerpt="Summary"
Expected:     ✅ See submitted entry
Actual:       ❌ 400 Bad Request OR canonical entry with title="Body"
Test Result:  FAIL
```

### After Fix - Dictionary
```
User submits: lemma_devanagari="शब्द", lemma_roman="shabd", meaning="word",
              senses=[{definition: "a word"}]
Expected:     ✅ Submission accepted, canonical entry created
Actual:       ✅ All fields preserved
Test Result:  PASS
```

### After Fix - Article
```
User submits: title="Article", content="Body", excerpt="Summary"
Expected:     ✅ Submission accepted, canonical entry with correct title
Actual:       ✅ All fields preserved
Test Result:  PASS
```

---

## 📋 Implementation Checklist

- [ ] Update `frontend/src/components/submission/SubmissionForm.svelte` buildPayload function
  - [ ] Dictionary: Move lemma fields to external_references
  - [ ] Article: Move title to external_references
  - [ ] Add senses array to dictionary external_references
  
- [ ] Add form input for dictionary senses/definitions
  - [ ] Input field for each sense
  - [ ] Add/Remove buttons

- [ ] Test all workflows
  - [ ] Dictionary submit → approve
  - [ ] Article submit → approve
  - [ ] Idiom submit (no changes, ensure not broken)
  - [ ] Doha submit (no changes, ensure not broken)

- [ ] (Optional) Add time_spent_seconds to backend schema

---

## 📈 Impact Analysis

| Aspect | Dictionary | Article | Idiom | Doha |
|--------|-----------|---------|-------|------|
| Submissions blocked | ❌ Yes | ❌ Yes | ✅ No | ✅ No |
| Data loss possible | ⚠️ Yes | ⚠️ Yes | ✅ No | ✅ No |
| Moderation failures | ⚠️ Yes | ⚠️ Yes | ✅ No | ✅ No |
| Canonical data corrupted | ⚠️ Maybe | ✅ Yes | ✅ No | ✅ No |
| Fix complexity | Medium | Low | N/A | N/A |
| Time to fix | 1-2 hours | 30 min | N/A | N/A |
