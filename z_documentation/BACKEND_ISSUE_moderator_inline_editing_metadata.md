## Issue: Moderator Inline Editing - Limited to Basic Fields Only

**Problem:** The backend `PUT /submissions/{id}` endpoint currently only supports updating basic content fields (`main_text`, `meaning`, `external_references`, `visibility`) through the `SubmissionUpdateIn` schema. Metadata fields like `author_slug`, `work_slug`, `chapter_slug`, `number_in_chapter`, and `is_classical` cannot be updated, causing 422 validation errors when moderators attempt comprehensive inline edits.

**Impact:** Moderators can only fix typos/content but cannot correct structural metadata (wrong author attribution, incorrect chapter placement, classical status) without rejecting and requesting contributor resubmission.

**Required Changes:**
1. Expand `SubmissionUpdateIn` schema in `submissions.py` to include optional metadata fields
2. Update PUT handler to apply these fields to the submission model
3. Add permission checks to ensure only moderators/admins can edit metadata (contributors should remain restricted to content-only)

**Complexity:** Moderate - Requires schema extension, database field updates, and permission logic. No MySQL schema changes needed (fields already exist in Submission table).
