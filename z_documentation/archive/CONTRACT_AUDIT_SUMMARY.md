# Contract Audit Summary - Quick Reference

**Audit Date:** March 28, 2026  
**Report Generated:** 2026-03-28T00:00:00Z  
**Backend Schema Version:** SubmissionCreateIn (app/api/v1/submissions.py)  
**Frontend Form Version:** SubmissionForm.svelte (frontend/src/components/submission/SubmissionForm.svelte)

---

## ⚡ Quick Status

| Content Type | Status | Issue Count | Severity |
|---|---|---|---|
| 🟢 **doha** | PASS | 0 | - |
| 🔴 **dictionary** | FAIL | 2 | CRITICAL + HIGH |
| 🟢 **idiom** | PASS | 0 | - |
| 🔴 **article** | FAIL | 1 | CRITICAL |

**Overall Result**: 🔴 **NEEDS FIXES** (2 critical issues found)

---

## 🎯 Critical Issues (Must Fix Immediately)

### 1️⃣ Dictionary: lemma_devanagari Placement Error
- **What's wrong**: Frontend sends `lemma_devanagari` as top-level field
- **Where it should be**: Inside `external_references` dict
- **Why it matters**: Backend schema error OR data loss
- **File to fix**: `frontend/src/components/submission/SubmissionForm.svelte` line 208
- **Fix type**: Move fields from payload root to payload.external_references

### 2️⃣ Article: title Placement Error  
- **What's wrong**: Frontend sends `title` as top-level field
- **Where it should be**: Inside `external_references` dict
- **Why it matters**: Title is lost, canonical articles created with wrong metadata
- **File to fix**: `frontend/src/components/submission/SubmissionForm.svelte` line 220
- **Fix type**: Move title from payload root to payload.external_references

---

## ⚠️ High Priority Issues (Must Fix Soon)

### 3️⃣ Dictionary: Missing senses Form Input
- **What's wrong**: Frontend has no UI to collect definitions/senses
- **Why it matters**: DictionaryPayload requires senses array; empty array creates incomplete entries
- **File to fix**: `frontend/src/components/submission/SubmissionForm.svelte` dictionary section
- **Fix type**: Add form input for definitions

---

## ℹ️ Low Priority Issues (Nice to Fix)

### 4️⃣ time_spent_seconds Field Ignored
- **What's wrong**: Frontend sends this but backend schema doesn't accept it
- **Why it matters**: Analytics capability unused
- **File to fix**: `backend/app/api/v1/submissions.py` (add field)
- **Impact**: Very low - affects only analytics

### 5️⃣ Idiom: usage_example Top-Level (Minor)
- **What's wrong**: Frontend sends usage_example as top-level field
- **Why it doesn't break**: Data is also in external_references.examples (working copy)
- **Fix type**: Optional cleanup (remove from top-level)
- **Impact**: None - functional but adds noise

---

## 📊 Detailed Findings by Content Type

### DOHA ✅ PASS
```
✅ All fields in correct locations
✅ main_text: correct
✅ meaning: correct
✅ Metadata: correct
⚠️ time_spent_seconds sent but ignored (LOW impact)

Status: Ready to use
```

### DICTIONARY ❌ FAIL
```
❌ lemma_devanagari: TOP-LEVEL (must move to external_references)
❌ lemma_roman: TOP-LEVEL (must move to external_references)
⚠️ senses: NO FORM INPUT (must add form)
✅ main_text: correct
✅ meaning: correct
✅ Metadata: correct

Status: BROKEN - Submissions will fail or lose data
```

### IDIOM ✅ PASS
```
✅ main_text: correct
✅ meaning: correct
✅ text_devanagari: correct (in external_references)
✅ text_roman: correct (MANDATORY field present)
✅ examples: correct
⚠️ usage_example: top-level + in external_references (minor redundancy)

Status: Ready to use (per MED-003 design)
```

### ARTICLE ❌ FAIL
```
❌ title: TOP-LEVEL (must move to external_references)
❌ body: NOT in external_references for moderation lookup
✅ main_text: correct (used as body)
✅ meaning: correct (used as excerpt)
✅ excerpt: correct
✅ Metadata: correct

Status: BROKEN - Title lost, canonical entries corrupted
```

---

## 🔧 How to Fix

### Step 1: Update buildPayload Function (SubmissionForm.svelte line 202)

```typescript
// Dictionary: Current BROKEN code
if (content_type === "dictionary") {
    payload.lemma_devanagari = lemma_devanagari || null;    // ❌
    payload.lemma_roman = lemma_roman || null;              // ❌
    payload.main_text = lemma_devanagari || lemma_roman || null;
    payload.meaning = meaning || null;
}

// Dictionary: FIXED code
if (content_type === "dictionary") {
    payload.main_text = lemma_devanagari || lemma_roman || null;
    payload.meaning = meaning || null;
    payload.external_references = {
        ...(Object.keys(parsedExternalReferences).length ? parsedExternalReferences : {}),
        lemma_devanagari: lemma_devanagari || null,
        lemma_roman: lemma_roman || null,
        senses: []  // TODO: populate from form after adding senses input
    };
}

// Article: Current BROKEN code
else if (content_type === "article") {
    payload.title = title || null;                          // ❌
    payload.main_text = content || null;
    payload.meaning = excerpt || null;
}

// Article: FIXED code
else if (content_type === "article") {
    payload.main_text = content || null;
    payload.meaning = excerpt || null;
    payload.external_references = {
        ...(Object.keys(parsedExternalReferences).length ? parsedExternalReferences : {}),
        title: title || null,
        body: content || null,
        excerpt: excerpt || null,
        tags: []
    };
}
```

### Step 2: Add Dictionary Senses Form Input

```svelte
{#if content_type === "dictionary"}
    <!-- Existing fields -->
    <input bind:value={lemma_devanagari} />
    <input bind:value={lemma_roman} />
    
    <!-- NEW: Add senses input -->
    <div class="field">
        <label>Definitions / Senses (at least one required)</label>
        {#each senses as sense, idx}
            <input bind:value={sense.definition} placeholder="Definition" required />
            {#if senses.length > 1}
                <button on:click={() => removeSense(idx)}>Remove</button>
            {/if}
        {/each}
        <button on:click={addSense}>+ Add Definition</button>
    </div>
    
    <textarea bind:value={meaning} />
{/if}
```

Add to script:
```typescript
let senses: {definition: string, pos?: string}[] = [{definition: ""}];
function addSense() { senses = [...senses, {definition: ""}]; }
function removeSense(idx: number) { senses = senses.filter((_, i) => i !== idx); }
```

---

## ✅ Verification Checklist

After fixes are applied:

- [ ] **Dictionary submission**: 
  - [ ] Form submit → 200 OK (no 400 error)
  - [ ] Data stored in DB with external_references.lemma_devanagari
  - [ ] Moderator approve → canonical entry created
  - [ ] Canonical entry has correct lemma and definitions

- [ ] **Article submission**:
  - [ ] Form submit → 200 OK (no 400 error)
  - [ ] Data stored with external_references.title
  - [ ] Moderator approve → canonical entry created
  - [ ] Canonical entry has correct title (not body)

- [ ] **Idiom submission** (ensure no regression):
  - [ ] Form submit → 200 OK
  - [ ] Moderator approve → canonical entry created
  - [ ] All fields correct

- [ ] **Doha submission** (ensure no regression):
  - [ ] Form submit → 200 OK
  - [ ] Moderator approve → canonical entry created
  - [ ] All fields correct

---

## 📁 Generated Documentation

### Detailed Analysis
- **contract_audit_report.json** - Complete field-by-field comparison in JSON format
  - Use this for programmatic validation
  - Shows all field types, validators, and frontend/backend mappings
  - Lists expected vs actual values for each content type

### Implementation Guide
- **CONTRACT_AUDIT_DETAILED_GUIDE.md** - Step-by-step fixing guide
  - Root cause explanations
  - Code snippets for each issue
  - Testing scenarios
  - Before/after comparisons

### Visual Comparison
- **CONTRACT_AUDIT_VISUAL_COMPARISON.md** - Data flow diagrams
  - Shows how data flows for each content type
  - Highlights where things go wrong
  - Includes visual representation of correct vs broken flows

### This File
- **CONTRACT_AUDIT_SUMMARY.md** - Quick reference (you are here)
  - High-level overview
  - Issue categorization
  - Quick fix checklist

---

## 🎬 Impact Timeline

### Without Fixes
- ❌ Dictionary submissions blocked or lose data
- ❌ Article submissions blocked or create corrupted entries
- ❌ Moderation fails silently or creates bad canonical entries
- 🔄 Users frustrated, feature non-functional for 2 content types

### With Fixes
- ✅ All submission types work correctly
- ✅ Moderation approvals succeed
- ✅ Canonical entries have correct metadata
- ✅ Feature fully functional

**Fix Effort**: 1-2 hours
**Testing Effort**: 30 minutes
**Total Time**: ~2 hours

---

## 📞 Questions?

Refer to:
1. `contract_audit_report.json` - For specific field details
2. `CONTRACT_AUDIT_DETAILED_GUIDE.md` - For implementation steps
3. `CONTRACT_AUDIT_VISUAL_COMPARISON.md` - For workflow diagrams
