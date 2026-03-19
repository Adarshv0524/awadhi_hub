V2 plan (how to support poems / full-works / richer submissions without breaking current backend)

Goals: support single-document works, richer content types (poem/text/poem collection), and allow submission forms to let users pick Author → Work → Chapter.

Backend additions (recommended, to do in v2):

Add classical_works.work_type more robustly (poem, anthology, epic, single_text) — already present in your model plan; ensure it’s set.

Add work_has_chapters: boolean or infer from work_chapters count to determine frontend behavior.

Add endpoint: GET /content/by-work/{author_slug}/{work_slug} which returns either:

single document (if the work is single-doc), or

list of items grouped by chapter (if multi-chapter).
This is optional; until then, the frontend uses /search?author&work.

Submission API: support author_slug, work_slug, chapter_slug on POST /submissions (already planned). Add helper endpoints for autosuggest:

GET /authors?query=...

GET /authors/{slug}/works?query=...

GET /authors/{slug}/works/{work}/chapters?query=...
-> Frontend can use these to populate dependent dropdowns (Author → Works → Chapters).

Add canonical hierarchy_path creation helper to normalize paths (for SEO).

DB / Migration strategy (Alembic):

Create migrations that add work_type, is_single_document flags, plus indexes on (author_slug, work_slug).

Migrate existing works: detect works with 0 chapters -> mark as is_single_document = true if search shows items for the work.

Frontend features for v2

Submission UI with dependent selects:

Type: dropdown content_type (doha/dictionary/idiom/article)

If classical: pick Author (autocomplete) → fetch works → pick Work → fetch chapters → pick Chapter (or “No chapter / single work”)

UI should show preview of where submission will appear (path).

Allow contributors to create new work/chapter proposals (admin/moderator review flow).

7) Issues we should defer (for later versions)

Full-text indexing tuning (MySQL MATCH/FTS) — leave as is for now.

Rewriting existing canonical URLs to slugs (you already use IDs — we keep ID immutability).

Complex recommendation improvements (cross-type silos vs cross-type recommendations) — currently backend provides cross-type results; if you want strict same-type silos, adjust recommendation service later.

Bulk migrations of legacy content (we’ll plan with Alembic + migration script).

Server-side redirects for old URL formats — can add later if needed.