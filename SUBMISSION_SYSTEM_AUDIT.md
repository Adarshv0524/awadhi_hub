# Submission/Contribution System Audit
**Date**: March 29, 2026  
**Scope**: Complete analysis of backend Pydantic models, database schemas, and frontend submission form

---

## Executive Summary

The Awadhi submission system supports **5 main content types** (4 legacy + poetry variants):
1. **Poetry** (dynamic types: doha, chaupai, jhulana, other_poetry)
2. **Dictionary** - Word entries with definitions
3. **Idiom** - Idioms and proverbs  
4. **Article** - Long-form articles

The system uses a **two-tier architecture**:
- **Submissions table** (user contributions awaiting moderation)
- **Canonical tables** (DohaEntry, DictionaryEntry, IdiomEntry, ArticleEntry - moderation-approved content)

---

## 1. All Supported Content Types

### Poetry Types (Dynamic, stored in PoetryType table)
- `doha` - Classical couplets
- `chaupai` - 4-line verse form
- `jhulana` - Swing form
- `other_poetry` - User-defined poetry

### Legacy Types (Fixed)
- `dictionary` - Word/lemma entries
- `idiom` - Idioms and proverbs
- `article` - Long-form articles

---

## 2. Detailed Field Mapping by Content Type

### 2.1 POETRY (All Poetry Types: doha, chaupai, jhulana, other_poetry)

#### Backend Database Model: `Submission` table
| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| `id` | Integer | ✅ | Auto-increment | Primary key |
| `content_type` | String(50) | ✅ | — | Poetry type (e.g., "doha") |
| `main_text` | Text | ✅ | — | Poetry in Devanagari script |
| `meaning` | Text | ❌ | NULL | Translation/explanation |
| `is_classical` | Boolean | ✅ | False | Whether it's historical content |
| `author_slug` | String(150) | ❌ | NULL | Classical author reference |
| `work_slug` | String(150) | ❌ | NULL | Classical work reference |
| `chapter_slug` | String(150) | ❌ | NULL | Chapter within work |
| `number_in_chapter` | Integer | ❌ | NULL | Sequence number |
| `external_references` | JSON | ❌ | NULL | Additional metadata (poetry_type stored here) |
| `status` | String(20) | ✅ | "draft" | draft, pending, approved, rejected |
| `visibility` | String(20) | ✅ | "private" | private, public |
| `version` | Integer | ✅ | 1 | Optimistic concurrency control |
| `contributor_id` | Integer | ✅ | — | User who submitted |
| `assigned_moderator_id` | Integer | ❌ | NULL | Moderator assignment |
| `priority` | Integer | ✅ | 0 | Review priority |

#### Backend Pydantic Schema: `SubmissionCreateIn` + `SubmissionOut`
```python
class SubmissionCreateIn:
    content_type: str  # e.g., "doha"
    main_text: str     # Required
    meaning: Optional[str]
    is_classical: bool = False
    author_slug: Optional[str]
    work_slug: Optional[str]
    chapter_slug: Optional[str]
    number_in_chapter: Optional[int]
    external_references: Optional[Dict[str, Any]]  # Stores poetry_type
    visibility: Optional[str] = "private"
    submit_for_review: bool = False
```

#### Canonical Database Model: `PoetryNode` table (via poetry_nodes)
| Field | Type | Notes |
|-------|------|-------|
| Poetry node ID, hierarchy path, text, metadata, engagement KPIs | — | Managed by poetry service |

#### Frontend Form Fields (SubmissionForm.svelte)
- **Required**: 
  - `main_text` - Poetry text (Devanagari)
  
- **Optional**:
  - `meaning` - Translation/explanation
  - `is_classical` - Checkbox for classical content
  - `selected_author_slug` - Select dropdown or free text
  - `free_author_name` - Free-text author name
  - `selected_work_slug` - Depends on author selection
  - `selected_chapter_slug` - Depends on work selection
  - `number_in_chapter` - Sequence number
  - `external_refs` - JSON for advanced references
  - `visibility` - private/public

---

### 2.2 DICTIONARY

#### Backend Database Model: `Submission` table + `DictionaryEntry` canonical
| Field (Submission) | Type | Required | Notes |
|-------|------|----------|-------|
| `main_text` | Text | ✅ | Stores lemma_devanagari or lemma_roman |
| `meaning` | Text | ✅ | First sense definition |
| `external_references` | JSON | ✅ | Stores: lemma_devanagari, lemma_roman, senses array, pronunciation |

#### DictionaryEntry Canonical Model
| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `lemma_devanagari` | String(512) | ✅ | Word in Devanagari |
| `lemma_roman` | String(512) | ❌ | Word in Roman script |
| `lemma_roman_norm` | String(512) | ❌ | Normalized Roman |
| `language` | String(16) | ✅ | Default: "hi" (Hindi/Awadhi) |
| `senses` | JSON | ✅ | Array of sense objects |
| `pronunciation` | String(255) | ❌ | Phonetic info |
| `examples` | JSON | ❌ | Usage examples |
| `author_id` | Integer | ❌ | Classical author reference |
| `work_id` | Integer | ❌ | Classical work reference |
| `chapter_id` | Integer | ❌ | Chapter reference |
| `number_in_chapter` | Integer | ❌ | Sequence number |
| `visibility` | String(20) | ✅ | public/private |

#### Pydantic Schema: `SubmissionCreateIn`
```python
# Payload structure for dictionary submission:
{
    "content_type": "dictionary",
    "main_text": "शब्द",  # From lemma_devanagari
    "meaning": "meaning of first sense",
    "external_references": {
        "lemma_devanagari": "शब्द",
        "lemma_roman": "shabd",
        "senses": [
            {
                "definition": "Definition text",
                "pos": "noun",  # part of speech
                "examples": ["Example 1", "Example 2"]
            }
        ]
    },
    "visibility": "private",
    "is_classical": false
}
```

#### Frontend Form Fields
- **Required**:
  - `lemma_devanagari` - Word in Devanagari
  - `dictionarySenses` (array):
    - `definition` - Required for each sense
    
- **Optional**:
  - `lemma_roman` - Roman transliteration
  - `dictionarySenses.pos` - Part of speech
  - `dictionarySenses.example` - Usage example
  - Classical hierarchy fields (author, work, chapter)
  - `external_refs` - Advanced JSON references
  - `visibility`

**Form Feature**: Multi-sense support - users can add/remove multiple senses

---

### 2.3 IDIOM

#### Backend Database Model: `Submission` table + `IdiomEntry` canonical
| Field (Submission) | Type | Required | Notes |
|-------|------|----------|-------|
| `main_text` | Text | ✅ | Devanagari text |
| `meaning` | Text | ✅ | Meaning/explanation |
| `external_references` | JSON | ✅ | Stores: text_devanagari, text_roman, meaning, examples |

#### IdiomEntry Canonical Model
| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `text_devanagari` | Text | ✅ | Idiom in Devanagari |
| `text_roman` | Text | ❌ | Roman transliteration |
| `text_roman_norm` | String(512) | ❌ | Normalized |
| `meaning` | Text | ❌ | Explanation |
| `examples` | JSON | ❌ | Array of example sentences |
| `region` | String(64) | ❌ | Geographic region (e.g., "Avadh") |
| `author_id` | Integer | ❌ | If from classical work |
| `work_id` | Integer | ❌ | If from classical work |
| `chapter_id` | Integer | ❌ | Chapter reference |
| `number_in_chapter` | Integer | ❌ | Sequence |
| `visibility` | String(20) | ✅ | public/private |

#### Pydantic Schema: `SubmissionCreateIn`
```python
{
    "content_type": "idiom",
    "main_text": "idiom in devanagari",
    "meaning": "what it means",
    "external_references": {
        "text_devanagari": "idiom text",
        "text_roman": "romanized form",
        "meaning": "explanation",
        "examples": ["Example sentence 1", "Example 2"]
    },
    "visibility": "private",
    "is_classical": false
}
```

#### Frontend Form Fields
- **Required**:
  - `main_text` - Idiom/proverb in Devanagari
  - `idiom_text_roman` - Romanized text
  - `meaning` - Explanation
  
- **Optional**:
  - `usage_example` - Example usage (stored as first item in examples)
  - Classical hierarchy (author, work, chapter)
  - `external_refs` - Advanced JSON
  - `visibility`

---

### 2.4 ARTICLE

#### Backend Database Model: `Submission` table + `ArticleEntry` canonical
| Field (Submission) | Type | Required | Notes |
|-------|------|----------|-------|
| `main_text` | Text | ✅ | Article body/content |
| `meaning` | Text | ✅ | Excerpt/summary |
| `external_references` | JSON | ✅ | Stores: title, body, excerpt, tags |

#### ArticleEntry Canonical Model
| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `title` | String(512) | ✅ | Article title |
| `title_devanagari` | String(512) | ❌ | Title in Devanagari |
| `title_roman` | String(512) | ❌ | Title in Roman |
| `title_roman_norm` | String(512) | ❌ | Normalized title |
| `body` | Text | ✅ | Article content |
| `excerpt` | Text | ❌ | Summary |
| `tags` | JSON | ❌ | Topic tags |
| `author_id` | Integer | ✅ | Contributor (User ID) |
| `visibility` | String(20) | ✅ | public/private |
| `version` | Integer | ✅ | Versioning |

#### Pydantic Schema: `SubmissionCreateIn`
```python
{
    "content_type": "article",
    "main_text": "article body content",
    "meaning": "excerpt or summary",
    "external_references": {
        "title": "Article Title",
        "body": "full article content",
        "excerpt": "summary text",
        "tags": ["tag1", "tag2"]  # Optional
    },
    "visibility": "private",
    "is_classical": false
}
```

#### Frontend Form Fields
- **Required**:
  - `title` - Article title
  - `content` - Article body (mapped to main_text)
  
- **Optional**:
  - `excerpt` - Summary (mapped to meaning)
  - Classical hierarchy fields (rarely used for articles)
  - `external_refs` - Advanced JSON
  - `visibility`

---

## 3. Frontend Form Structure Analysis

### 3.1 Form Sections (SubmissionForm.svelte)

#### Section 1: Content Type Selector
- **Purpose**: Select submission type
- **Field**: `content_type` (required)
- **Options**: 
  - Dynamic poetry types (from API)
  - dictionary, idiom, article (hardcoded)
- **Behavior**: Clears type-specific fields when switching types

#### Section 2: Type-Specific Content Fields
Renders different UI based on `content_type`:

**For Poetry Types**:
- `main_text` (textarea) - Devanagari text ✅ Required
- `meaning` (textarea) - Translation ❌ Optional

**For Dictionary**:
- `lemma_devanagari` (input) ✅ Required
- `lemma_roman` (input) ❌ Optional
- `dictionarySenses` (dynamic array of objects):
  - `definition` (textarea) ✅ Required
  - `pos` (input) ❌ Optional
  - `example` (input) ❌ Optional
  - Add/remove buttons for multiple senses

**For Idiom**:
- `main_text` (input) ✅ Required
- `idiom_text_roman` (input) ✅ Required
- `meaning` (textarea) ✅ Required
- `usage_example` (textarea) ❌ Optional

**For Article**:
- `title` (input) ✅ Required
- `excerpt` (textarea) ❌ Optional
- `content` (large textarea) ✅ Required

#### Section 3: Metadata (Optional Classical Hierarchy)
- **Purpose**: Link submissions to classical hierarchy
- **Fields**:
  - `is_classical` (checkbox)
  - `selected_author_slug` (dropdown from API)
  - `free_author_name` (free text input)
  - `selected_work_slug` (conditional dropdown)
  - `selected_chapter_slug` (conditional dropdown)
  - `number_in_chapter` (number input)
  - `external_refs` (textarea with JSON format)
  - `visibility` (dropdown: private/public)

**Validation Logic**:
- If `is_classical` = true, expects author_slug, work_slug, chapter_slug, number_in_chapter
- Works with free-text author name OR selected author slug

#### Section 4: Action Buttons
- "Submit for Review" - Sets `submit_for_review: true`
- "Save as Draft" - Sets `submit_for_review: false`
- Shows username of logged-in user

### 3.2 Supporting Features

**Auto-save & Draft Recovery**:
- LocalStorage cache with key `awadhi_submission_draft`
- Auto-saves after 1 second of inactivity
- Restores on page load
- Shows "Saving...", "Saved at HH:MM" indicators
- Unsaved changes warning

**Validation**:
- Client-side validation via `validateSubmissionPayload` utility
- Tracks form changes to warn on page navigation
- Required field indicators with red asterisks

**Form State Tracking**:
- Tracks time spent on form (`formStartTime`)
- Sends `time_spent_seconds` to API
- Initial state snapshot for change detection

---

## 4. Payload Transformation Logic

The form builds different payloads based on content type. Key mappings:

### Dictionary Payload
```javascript
{
  content_type: "dictionary",
  main_text: lemma_devanagari || lemma_roman,
  meaning: normalizedSenses[0]?.definition || meaning,
  external_references: {
    lemma_devanagari,
    lemma_roman,
    senses: normalizedSenses  // Filtered array
  },
  visibility,
  is_classical,
  author_slug,
  submit_for_review
}
```

### Idiom Payload
```javascript
{
  content_type: "idiom",
  main_text: main_text,
  meaning: meaning,
  external_references: {
    text_devanagari: main_text,
    text_roman: idiom_text_roman,
    meaning: meaning,
    examples: usage_example ? [usage_example] : null
  },
  visibility,
  is_classical,
  author_slug,
  submit_for_review
}
```

### Article Payload
```javascript
{
  content_type: "article",
  main_text: content,
  meaning: excerpt,
  external_references: {
    title: title,
    body: content,
    excerpt: excerpt
  },
  visibility,
  is_classical,
  author_slug,
  submit_for_review
}
```

### Poetry Payload
```javascript
{
  content_type: poetry_type,  // "doha", "chaupai", etc.
  main_text: main_text,
  meaning: meaning,
  external_references: {
    poetry_type: content_type,
    // + parsed external_refs
  },
  is_classical,
  author_slug,
  work_slug,
  chapter_slug,
  number_in_chapter,
  visibility,
  submit_for_review
}
```

---

## 5. Issues & Problem Areas

### 🔴 **CRITICAL ISSUES**

#### 1. **Payload Mapping Inconsistencies**
- **Problem**: The form stores user input in multiple field names but API expects specific names
- **Example**: 
  - Dictionary form uses `lemma_devanagari` but API's `main_text` field
  - Article form uses `title` locally but stores in `external_references.title`
  - This creates a lossy/reconstructive transformation
- **Impact**: Awkward data flow, potential data loss on round-trips

#### 2. **Dual Author Reference System**
- **Problem**: `selected_author_slug` (dropdown) vs `free_author_name` (free text)
- **Logic**: Uses `author_slug = selected_author_slug || (free_author_name || null)`
- **Issue**: Only one can be submitted - no way to indicate both
- **Form Bug**: Free-text author name field appears AFTER dropdown, confusing UX

#### 3. **External References are Semi-Structured**
- **Problem**: JSON field `external_references` stores crucial data:
  - For dictionary: senses, definitions, POS
  - For idiom: romanization, examples
  - For article: title, body
- **Issue**: Data is both in `main_text`/`meaning` AND `external_references`
- **Risk**: Duplication, sync issues, unclear source of truth

### 🟡 **MODERATE ISSUES**

#### 4. **Conditional Rendering Logic is Fragile**
- **Problem**: Form shows/hides fields based on `isPoetryType` flag
- `isPoetryType` = !LEGACY_TYPES.includes(content_type)]
- **Issue**: If new poetry types added to frontend but backend doesn't recognize them, form breaks
- **Missing Types**: No explicit list of valid poetry types in form

#### 5. **Classical Hierarchy Validation is Backend-Only**
- **Problem**: Form requires you to select author/work/chapter, but doesn't validate they exist
- **Issue**: Users can submit with invalid hierarchies; API returns 400
- **Better**: Fetch and pre-validate hierarchy options as user selects

#### 6. **Sense Array Type for Dictionary**
- **Problem**: Form hardcodes `{ definition: "", pos: "", example: "" }` structure
- **Backend expects**: `senses` array with specific schema (definition is required, others structured)
- **Mismatch**: No validation that at least one sense has a definition

#### 7. **Idiom Requires Both Main Text AND Roman**
- **Problem**: Form marks both `main_text` and `idiom_text_roman` as required
- **Question**: What if contributor only knows one form?
- **Better**: Make at least one required, prefer Devanagari

#### 8. **Usage Example is Single String**
- **Problem**: Form stores `usage_example` as single string
- **Schema expects**: `examples` array (plural)
- **Result**: Only the first example is captured

### 🟠 **MINOR ISSUES**

#### 9. **Form Validation Utility is Not Inspected**
- `validateSubmissionPayload()` imported from `../../lib/submissionValidation`
- **Cannot assess**: Validation rules, error messages, edge cases
- **Recommendation**: Review separately

#### 10. **Article: body vs. excerpt mapping unclear**
- Form has `content` (large textarea) and `excerpt` (small textarea)
- Mapping: `main_text = content`, `meaning = excerpt`
- **Confusion**: "meaning" is misleading for articles

#### 11. **Visibility Default Always "private"**
- **Issue**: Form always defaults to private, no smart defaults based on content type
- **Better**: Public submissions should be default for approved content types

#### 12. **No Content-Type Specific Help Text**
- Each content type needs different guidance
- Form shows generic text, no validation rules per type
- Example: Dictionary should explain senses structure

---

## 6. Recommended Field Organization for Form Redesign

### **Proposed New Structure**

```
┌─────────────────────────────────────────┐
│  SUBMISSION FORM - Clean Architecture  │
├─────────────────────────────────────────┤

1. HEADER
   - Progress indicator (if multi-step)
   - Auto-save status

2. CONTENT TYPE SELECTOR
   - Radio or visual card selector
   - Show context-specific help

3. UNIFIED CONTENT SECTION
   [Based on content_type]
   
   For POETRY:
   ├─ Poetry Text (Required)
   ├─ Meaning/Translation (Optional)
   └─ [Classical Hierarchy Section]
   
   For DICTIONARY:
   ├─ Word (Devanagari) (Required)
   ├─ Word (Roman) (Optional)
   ├─ Pronunciation (New: Optional)
   ├─ Senses Editor (Required: ≥1)
   │  ├─ Sense Definition (Required)
   │  ├─ Part of Speech (Optional dropdown)
   │  ├─ Examples (Optional: multiple)
   │  └─ [Add/Remove Sense buttons]
   └─ [Classical Hierarchy Section]
   
   For IDIOM:
   ├─ Idiom Text (Devanagari) (Required)
   ├─ Idiom Text (Roman) (Required, or at least one)
   ├─ Meaning (Required)
   ├─ Region/Context (New: Optional)
   ├─ Examples (New: Multiple entries)
   └─ [Classical Hierarchy Section]
   
   For ARTICLE:
   ├─ Title (Required)
   ├─ Article Content (Required)
   ├─ Excerpt/Summary (Optional)
   ├─ Tags (New: Optional)
   └─ [Classical Metadata minimal]

4. CLASSICAL HIERARCHY (Collapsible)
   ├─ Is Classical? (Checkbox)
   ├─ Author (Dropdown OR Free Text)
   ├─ Work (Conditional Dropdown)
   ├─ Chapter (Conditional Dropdown)
   └─ Position in Chapter (Number)

5. VISIBILITY & SUBMISSION
   ├─ Visibility (Radio: Private/Public)
   ├─ [Submit for Review Button]
   └─ [Save as Draft Button]

6. METADATA (Collapsible/Hidden)
   ├─ External References (JSON, Advanced)
   └─ Time Tracking (Hidden)
```

### **Field Organization by Content Type**

#### **Dictionary Entry Form**
| Section | Field | Type | Required | UI Component |
|---------|-------|------|----------|--------------|
| **Word** | Devanagari | Text | ✅ | Input |
| | Roman | Text | ❌ | Input |
| | Pronunciation | Text | ❌ | Input (NEW) |
| **Senses** | [Array Editor] | — | — | Dynamic form builder |
| | | Definition | ✅ | Textarea |
| | | POS | ❌ | Select (noun, verb, etc.) |
| | | Examples | ❌ | Multi-input |
| **Add Sense** | + Button | — | — | |
| **Hierarchy** | Classical (checkbox) | — | ❌ | |
| | Author | Select/Text | ❌ | Hybrid field |

#### **Idiom Entry Form**
| Section | Field | Type | Required | UI Component |
|---------|-------|------|----------|--------------|
| **Text** | Devanagari | Text | ✅ | Input (≥1 required) |
| | Roman | Text | ✅ | Input (≥1 required) |
| **Meaning** | Explanation | Textarea | ✅ | |
| **Usage** | Examples | Text[] | ❌ | Multi-input |
| | Region/Context | Text | ❌ | Input (NEW) |
| **Hierarchy** | Classical (checkbox) | — | ❌ | |
| | Author | Select/Text | ❌ | |

#### **Article Form**
| Section | Field | Type | Required | UI Component |
|---------|-------|------|----------|--------------|
| **Content** | Title | Text | ✅ | Input |
| | Body | Textarea | ✅ | Large editor |
| | Excerpt | Textarea | ❌ | |
| **Organization** | Tags | Text[] | ❌ | Multi-input (NEW) |
| **Visibility** | Public/Private | Radio | ✅ | |

#### **Poetry Form** (All Types)
| Section | Field | Type | Required | UI Component |
|---------|-------|------|----------|--------------|
| **Text** | Devanagari | Textarea | ✅ | |
| | Meaning | Textarea | ❌ | |
| **Hierarchy** | Classical (checkbox) | — | ✅ | Must link to hierarchy |
| | Author | Select/Text | ✅ | |
| | Work | Select | ✅ | |
| | Chapter | Select | ✅ | |
| | Seq Number | Number | ✅ | |

---

## 7. Unused or Confusing Form Fields

### **Unused**
1. ✓ `free_author_name` - Only used if `author_slug` not selected; rarely used
   - **Better**: Manage as single "Author" field with async search + free-text fallback

2. ✓ `number_in_chapter` - Metadata field not meaningful for most submissions
   - **Question**: Is this auto-assigned by moderators? Or user-guessed?

3. ✓ `external_refs` (JSON textarea) - Advanced field, requires users to write JSON
   - **Better**: Replaced with type-specific structured fields

### **Confusing**
1. ❌ `meaning` field name for articles
   - **Should be**: `excerpt` or `summary`
   - **Impact**: Users don't understand what "meaning" means for an article

2. ❌ `main_text` is overloaded
   - Poetry: The poetry itself
   - Dictionary: First lemma form
   - Idiom: The idiom text
   - Article: The full article body
   - **Better**: Use explicit `poetry_text`, `lemma`, `idiom_text`, `body`

3. ❌ Dual author system (dropdown + free text)
   - **Should be**: Single searchable field with fallback to free text

4. ❌ `is_classical` checkbox with optional hierarchy fields
   - **Confusing**: Checkbox label doesn't explain what it unlocks
   - **Better**: "Link to classical work?" with explanatory text

5. ❌ `external_references` JSON field in UI
   - **Should be**: Remove from frontend; let backend handle
   - **If needed**: Type-specific structured editors

---

## 8. Current Form Validation Rules

### Validation implemented in form:
- Required fields marked with red asterisk
- Client-side validation via `validateSubmissionPayload()`
- Type-specific field requirements:
  - **Dictionary**: At least 1 sense with definition
  - **Idiom**: main_text, idiom_text_roman, meaning all required
  - **Article**: title, content required
  - **Poetry**: main_text required

### Backend validation:
- If `is_classical=true`: author_slug, work_slug, chapter_slug, number_in_chapter ALL required
- Classical references must exist in database
- Content type must be recognized
- Token/auth required

---

## 9. Recommendations for Clean UI Redesign

### Priority 1: Critical Fixes

1. **Restructure `main_text` / `meaning` mapping**
   - Use explicit fields for each content type
   - Eliminate dual storage in both top-level and `external_references`
   - ✅ Dictionary: `lemma_devanagari`, `lemma_roman`, `senses` (structured)
   - ✅ Idiom: `idiom_text_devanagari`, `idiom_text_roman`, `meaning`
   - ✅ Article: `title`, `body`, `excerpt`
   - ✅ Poetry: `poetry_text`, `translation/meaning`

2. **Fix author reference system**
   - Single "Author" field: Dropdown (searchable) with free-text fallback
   - Label: "Link to classical author (optional)" 
   - Help text: "If from a known author/work, link it for better discoverability"

3. **Simplify external_references**
   - Remove JSON textarea from UI (move to backend/admin tools)
   - Keep structured editors for each type
   - Reserved for non-standard metadata

### Priority 2: UX Improvements

4. **Better hierarchy linking**
   - Pre-populate chapter options with counts
   - Show "Position in chapter" ONLY if chapter selected
   - Add hierarchy browser/visualizer

5. **Dictionary sense builder UX**
   - Show example of well-formed sense
   - Dropdown for POS (noun, verb, adjective, adverb, etc.)
   - Inline example editor (no separate input field)
   - Validation: Highlight if definition is empty

6. **Content-type specific help**
   - Add collapsible "?" sections with examples
   - Show required vs. optional fields clearly
   - Provide do's and don'ts for each type

7. **Better form state management**
   - Save drafts to backend (not just localStorage)
   - Show draft recovery on load
   - Version control for iterative editing

### Priority 3: New Features

8. **Support multiple examples**
   - Idiom: Allow 2-3 example sentences
   - Dictionary: Allow multiple POS (noun, verb)
   - Article: Auto-generate excerpt from body

9. **Rich text editor**
   - For Article body (markdown or minor HTML)
   - For Meaning/Translation fields

10. **Input validation feedback**
    - Real-time validation as user types
    - Suggestions (e.g., auto-complete for author names)
    - Error messages closer to problematic fields

---

## 10. Summary Table: All Fields by Type

| Field | Poetry | Dictionary | Idiom | Article | Required | UI Type |
|-------|--------|-----------|-------|---------|----------|----------|
| content_type | ✅ | ✅ | ✅ | ✅ | ✅ | Select |
| **MAIN CONTENT** | | | | | | |
| main_text (poetry) | ✅ | — | — | — | ✅ | Textarea |
| lemma_devanagari | — | ✅ | — | — | ✅ | Input |
| lemma_roman | — | ❌ | — | — | ❌ | Input |
| text_devanagari (idiom) | — | — | ✅ | — | ✅ | Input |
| text_roman (idiom) | — | — | ✅ | — | ✅ | Input |
| title (article) | — | — | — | ✅ | ✅ | Input |
| body (article) | — | — | — | ✅ | ✅ | Textarea |
| **MEANING** | | | | | | |
| meaning (poetry/idiom) | ❌ | — | ✅ | — | ❌/✅ | Textarea |
| senses (dict) | — | ✅ | — | — | ✅ | Array |
| definition | — | ✅ | — | — | ✅ | Textarea |
| pos | — | ❌ | — | — | ❌ | Input |
| example (dict) | — | ❌ | — | — | ❌ | Input |
| usage_example | — | — | ❌ | — | ❌ | Textarea |
| excerpt (article) | — | — | — | ❌ | ❌ | Textarea |
| **METADATA** | | | | | | |
| is_classical | ❌ | ❌ | ❌ | ❌ | ❌ | Checkbox |
| author_slug | ❌ | ❌ | ❌ | ❌ | ❌ | Select |
| work_slug | ❌ | ❌ | ❌ | ❌ | ❌ | Select |
| chapter_slug | ❌ | ❌ | ❌ | ❌ | ❌ | Select |
| number_in_chapter | ❌ | ❌ | ❌ | ❌ | ❌ | Number |
| external_references | ❌ | ✅ | ✅ | ✅ | ❌ | JSON |
| visibility | ❌ | ❌ | ❌ | ❌ | ❌ | Select |
| submit_for_review | ✅ | ✅ | ✅ | ✅ | ❌ | Action |

---

## 11. API Validation Flow

```
Frontend Form Submission
    ↓
validateSubmissionPayload() [Client-side validation]
    ↓
buildPayload() [Transform to API schema]
    ↓
POST /submissions
    ↓
Backend: SubmissionCreateIn validation (Pydantic)
    ↓
Classical hierarchy validation (if is_classical=true)
    ↓
Content type validation (doha, dictionary, idiom, article, or poetry_type)
    ↓
Save to Submission table
    ↓
Response: SubmissionOut [with id, status, version]
```

---

## 12. Conclusion

The system is **functional but architecturally messy**. The main problems:

1. **Data is stored in multiple places** (main_text + external_references)
2. **Field names don't match semantic meaning** (main_text, meaning are overloaded)
3. **Author reference system is awkward** (dropdown + free text split)
4. **Payload transformation is lossy** (round-trip reconstruction loses structure)

**For a redesign, prioritize**:
1. Explicit, semantic field names per content type
2. Single source of truth for critical data
3. Unified author field
4. Type-specific structured editors (no JSON in UI)
5. Better UX for dictionary senses and article metadata
