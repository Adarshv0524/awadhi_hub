# LIVING TECHNICAL MANIFESTO: AWADHI CORPUS BACKEND SYSTEM

## PRODUCTION-GRADE SYSTEM LOG & STRATEGIC AUDIT

**Document Version:** 1.0.0  
**Classification:** Internal Technical Architecture  
**Audience:** Senior Engineers, Data Scientists, System Architects  
**Last Updated:** 2025-12-14

---

# SECTION 1: THE EXECUTIVE CONTEXT (The "Why")

## 1.1 The Mission: What is This System Strictly Building?

The Awadhi Corpus Backend is a **multi-tiered content management and linguistic preservation platform** designed to digitize, moderate, and disseminate classical and contemporary literature in Awadhi and related Indic languages. At its core, this system manages:

1. **Hierarchical Literary Content** (Authors → Works → Chapters → Individual Dohas/Entries)
2. **User-Generated Submissions** (Community-contributed translations, annotations, and original works)
3. **Advanced Moderation Workflows** (Multi-stage review pipelines with role-based access control)
4. **Engagement Tracking & Analytics** (Views, likes, bookmarks, shares, search hits)
5. **Multi-Modal Content Types** (Dohas, Dictionary Entries, Idioms, Articles)
6. **Real-Time Search & Recommendation** (Full-text search with MySQL FULLTEXT and SQLite fallback)

This is NOT a generic CMS. It is a **domain-specific knowledge base** with scholarly rigor baked into its architecture.

---

## 1.2 The Problem: What Specific Pain Points Does This Address?

### Technical Pain Points:

1. **Content Provenance Tracking**: Most CMS platforms lack the granularity to track submission-to-canonical pipelines with full audit trails. This system maintains an immutable link from user submission → moderation log → canonical entry → version history.

2. **Hierarchical Content Complexity**: Classical literature has nested structures (Author has many Works; Work has many Chapters; Chapter has many Dohas). Most ORMs struggle with efficient querying and slug-based routing at this depth.

3. **Multilingual/Multiscript Support**: Awadhi content exists in Devanagari, Roman transliteration, and phonetic variants. The system normalizes Roman text (`lemma_roman_norm`, `text_roman_norm`) for search consistency while preserving original scripts.

4. **Engagement Without Heavy Infrastructure**: Unlike analytics platforms requiring Kafka/Spark, this system uses **weight-scored engagement KPIs** stored directly in MySQL, enabling real-time popularity ranking without external dependencies.

5. **Rate Limiting at Scale**: Standard middleware rate limiters (e.g., `express-rate-limit`) don't persist state across server restarts. This system uses **database-backed time-bucketed counters** with atomic upserts for production reliability.

### User-Centric Pain Points:

1. **Discovery Problem**: Users searching "रामचरितमानस" should find results even if they type "ramcharitmanas" or "ram charit manas". The normalization layer solves this.

2. **Trust Problem**: Community submissions require **transparent moderation**. Every approval/rejection is logged with moderator ID, timestamp, and guideline version.

3. **Content Quality**: Batch approval workflows prevent bottlenecks while maintaining atomicity (all-or-nothing transactions).

---

## 1.3 The Gap: What Was Missing in Standard Solutions?

### Why Not Use WordPress/Django CMS?

- **No Native Support for Classical Hierarchies**: WordPress taxonomies are flat. This system requires Author → Work → Chapter with enforced referential integrity.
- **No Submission Workflow**: We need `draft → pending_review → approved → canonical` with version locking.
- **No Engagement Weighting**: WordPress "likes" don't distinguish between search hits and direct views.

### Why Not Use Elasticsearch?

- **Cost**: Elasticsearch adds infrastructure overhead (separate cluster, monitoring).
- **Overkill**: For a corpus of ~10K-100K entries, MySQL FULLTEXT is sufficient.
- **Complexity**: Managing index consistency across `doha_entries`, `dictionary_entries`, `idiom_entries`, and `article_entries` is simpler with relational joins.

### Why Custom Rate Limiting?

- **Persistence**: Redis-backed rate limiters require Redis. This system uses MySQL's `ON DUPLICATE KEY UPDATE` for atomic increment/upsert.
- **Granular Control**: Per-action (`login`, `search`, `submission_create`) rate limits with configurable windows (60s for search, 1 hour for login).

---

## 1.4 The Solution: How Does This Architecture Solve the Above?

### Architectural Pillars:

1. **Hybrid ORM + Raw SQL**: 
   - SQLAlchemy ORM for CRUD operations.
   - Raw SQL for MySQL-specific optimizations (FULLTEXT, `ON DUPLICATE KEY UPDATE`).
   - SQLite compatibility layer for testing (no Redis/Elasticsearch dependencies).

2. **Event-Sourced Moderation**:
   - Every moderation action (`approve`, `reject`, `batch_approve`) writes to `moderation_logs`.
   - Canonical content creation writes to `content_versions` for rollback capability.

3. **Weighted Engagement Algorithm**:
   ```
   weight_score = 0.6 * log(views + 1) + 0.3 * log(search_hits + 1) + 0.1 * log(likes + 1)
   ```
   - Views > Search Hits > Likes in priority.
   - Logarithmic scaling prevents single viral posts from dominating.

4. **Atomic Batch Operations**:
   - Batch approval uses `with db.begin_nested()` for savepoint-based rollback.
   - If 1 of 100 submissions fails validation, **all 100 rollback**.

5. **Recommendation Engine (Lightweight)**:
   - Token-based similarity (extract words from `lemma_roman_norm`, match against other entries).
   - No ML models yet—this is the **injection point for future NLP**.

---

# SECTION 2: THE "REGRESSIVE" LOGIC AUDIT

---

## 2.1 DATABASE SCHEMA ANALYSIS

### File: `app/db/models.py`

**Dependencies:**
```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, Text, func, UniqueConstraint, ForeignKey, Float, Index
from sqlalchemy.orm import declarative_base, relationship, foreign
```

**Why These Imports?**
- `func`: Used for `server_default=func.now()` (database-level timestamps, not Python `datetime.now()`).
- `JSON`: MySQL 5.7+ native JSON columns (not TEXT with serialization).
- `Index`: Manual index creation for composite keys (e.g., `(content_type, content_id)`).
- `relationship`: Bidirectional ORM relationships (e.g., `ClassicalAuthor.works`).

---

### 2.1.1 MODULE 1: User Management

#### **Table: `users`**

**Column-by-Column Audit:**

| Column | Type | Constraints | Purpose | Data Science Relevance |
|--------|------|-------------|---------|------------------------|
| `id` | Integer | Primary Key, Auto-increment | Unique user identifier | **Segmentation Key**: Use for cohort analysis (e.g., users who joined before 2024-01 vs after) |
| `username` | String(100) | Unique, Nullable, Indexed | Public display name | **NLP Feature**: Username length/patterns may correlate with engagement |
| `email` | String(255) | Unique, Not Null, Indexed | Authentication identifier | **PII**: Must be hashed in analytics exports |
| `password_hash` | String(255) | Nullable | bcrypt hash (cost=12) | **Security Metric**: Track bcrypt cost over time (should increase annually) |
| `role` | String(50) | Default='registered', Indexed | RBAC role (admin, moderator, registered, guest) | **Privilege Escalation Analysis**: Track role changes over time |
| `permissions` | Integer | Default=0 | Bitwise permission flags (e.g., `MANAGE_USERS=1`, `MODERATE_SUBMISSIONS=2`) | **Access Pattern Analysis**: Which permissions are actually used? |
| `permission_scopes` | JSON | Nullable | ABAC constraints (e.g., `{"moderation:approve": {"authors": ["tulsidas"]}}`) | **Policy Mining**: Extract common scope patterns |
| `is_active` | Boolean | Default=True | Soft-delete flag | **Churn Analysis**: Time from `is_active=False` to account deletion |
| `is_banned` | Boolean | Default=False | Moderation flag | **Abuse Detection**: Correlate with `reports` table |
| `created_at` | DateTime(TZ) | Server default NOW() | Registration timestamp | **Time-Series Feature**: Hour-of-day/day-of-week registration patterns |
| `updated_at` | DateTime(TZ) | On update NOW() | Last profile change | **Activity Indicator**: Stale accounts (no update in 6+ months) |
| `last_login` | DateTime(TZ) | Nullable | Last authentication | **Engagement Metric**: Calculate DAU/MAU from this |

**Indexes:**
- `ix_users_email`: B-tree index (used in `WHERE email = ?` during login).
- `ix_users_username`: B-tree index (used in public profile lookups `/users/{username}`).
- `ix_users_role`: B-tree index (used in `/admin/users?role=moderator` queries).

**Relationships:**
- **None explicitly defined** (this is a base table; foreign keys are in child tables like `submissions.contributor_id`).

**🔬 Data Science & Analytics Perspective:**

**Feature Engineering:**
1. **Account Age**: `(NOW() - created_at)` in days → Proxy for user expertise.
2. **Login Frequency**: Count entries in `refresh_tokens` table → Distinguish active vs passive users.
3. **Permission Complexity Score**: `COUNT(permission_scopes keys)` → Users with complex ABAC rules are likely power users or admins.

**Visualizations:**
1. **Cohort Retention Heatmap**: X-axis = Registration Month, Y-axis = Months Since Registration, Color = % Still Active.
2. **Role Distribution Pie Chart**: Breakdown of admin/moderator/registered/guest.

**ML Opportunities:**
1. **Churn Prediction**: Logistic regression on `[last_login, submissions_count, role, account_age]` → Predict probability of `is_active=False` in next 30 days.
2. **Anomaly Detection**: Flag accounts with `is_banned=False` but high report count (potential false negatives in moderation).

---

#### **Table: `refresh_tokens`**

**Column-by-Column Audit:**

| Column | Type | Constraints | Purpose | Data Science Relevance |
|--------|------|-------------|---------|------------------------|
| `id` | Integer | Primary Key | Token identifier | **Session Tracking**: Join with `users` to calculate sessions per user |
| `token` | String(512) | Unique, Indexed | JWT refresh token (opaque string) | **Security Audit**: Check for token reuse patterns (should be 1:1 with sessions) |
| `user_id` | Integer | Indexed | FK to `users.id` | **User Activity**: Count active refresh tokens per user |
| `expires_at` | DateTime(TZ) | Not Null | Token expiration (default 14 days) | **Session Duration Analysis**: Distribution of token lifetimes |
| `created_at` | DateTime(TZ) | Server default | Token issuance time | **Login Pattern Analysis**: Peak login hours |

**Indexes:**
- `ix_refresh_tokens_token`: Used in `WHERE token = ?` during `/auth/refresh`.
- `ix_refresh_tokens_user_id`: Used in `/auth/logout` (delete all tokens for user).

**Logic Flow:**
1. User logs in via `/auth/login`.
2. System generates `access_token` (short-lived, 15 min) and `refresh_token` (long-lived, 14 days).
3. `refresh_token` is stored in this table with `expires_at = NOW() + 14 days`.
4. When `access_token` expires, client calls `/auth/refresh` with `refresh_token`.
5. System validates token exists in DB and `expires_at > NOW()`.
6. If valid, new `access_token` is issued (refresh token is reused).
7. On `/auth/logout`, token row is deleted.

**🔬 Data Science & Analytics Perspective:**

**Feature Engineering:**
1. **Session Length**: `expires_at - created_at` → Proxy for user engagement depth.
2. **Token Reuse Count**: How many times was `/auth/refresh` called per token? (Requires application logging, not stored in DB).

**Visualizations:**
1. **Token Expiration Timeline**: Gantt chart of active tokens over time.
2. **Login Frequency Histogram**: Distribution of `created_at` timestamps.

**ML Opportunities:**
1. **Session Anomaly Detection**: Flag users with >10 concurrent refresh tokens (possible account sharing or credential theft).

---

#### **Table: `oauth_accounts`**

**Column-by-Column Audit:**

| Column | Type | Constraints | Purpose | Data Science Relevance |
|--------|------|-------------|---------|------------------------|
| `id` | Integer | Primary Key | OAuth link identifier | **Integration Tracking**: Count users by provider |
| `provider` | String(50) | Composite Unique | OAuth provider (e.g., "google") | **Provider Popularity**: Which OAuth is most used? |
| `provider_user_id` | String(255) | Composite Unique | Provider's unique user ID (e.g., Google's `sub` claim) | **External ID Mapping**: Link to external analytics (e.g., Google Analytics User ID) |
| `user_id` | Integer | Indexed | FK to `users.id` | **User Linkage**: One user can have multiple OAuth accounts |
| `raw_profile` | JSON | Nullable | Full OAuth profile response (e.g., `{"sub": "...", "email": "...", "picture": "..."}`) | **Profile Completeness**: Extract profile photo usage, verified email status |
| `created_at` | DateTime(TZ) | Server default | OAuth link creation time | **Adoption Timeline**: When did users start using OAuth? |

**Unique Constraint:**
- `uq_provider_user` on `(provider, provider_user_id)`: Prevents duplicate Google accounts.

**Logic Flow (OAuth Callback):**
1. User clicks "Login with Google" → Redirected to `/auth/oauth/google/callback?code=...`.
2. Backend calls `exchange_code_for_tokens(code)` → Gets `access_token`.
3. Backend calls `fetch_google_profile(access_token)` → Gets `{"sub": "12345", "email": "user@gmail.com"}`.
4. System checks `oauth_accounts` for `provider='google' AND provider_user_id='12345'`.
5. If exists → Load linked `user_id`.
6. If not exists → Check `users` for `email='user@gmail.com'`.
7. If email exists → Link OAuth account to existing user.
8. If email doesn't exist → Create new user, then link OAuth account.
9. Return JWT tokens to client.

**🔬 Data Science & Analytics Perspective:**

**Feature Engineering:**
1. **OAuth Adoption Rate**: `(COUNT(oauth_accounts) / COUNT(users)) * 100`.
2. **Provider Preference**: Group by `provider`, calculate percentage.

**Visualizations:**
1. **OAuth Provider Pie Chart**: Google vs future providers (Facebook, Twitter).
2. **OAuth Adoption Over Time**: Line chart of new `oauth_accounts` per month.

**ML Opportunities:**
1. **Churn Prediction Enhancement**: Users with OAuth may have lower churn (single sign-on friction is lower).

---

### 2.1.2 MODULE 3: Classical Hierarchy

#### **Table: `classical_authors`**

**Column-by-Column Audit:**

| Column | Type | Constraints | Purpose | Data Science Relevance |
|--------|------|-------------|---------|------------------------|
| `id` | Integer | Primary Key | Author identifier | **Entity ID**: Join key for works, dohas |
| `slug` | String(150) | Unique, Indexed | URL-safe identifier (e.g., "tulsidas") | **SEO Feature**: Track most-visited author pages |
| `name` | String(255) | Not Null | Display name (e.g., "Goswami Tulsidas") | **NLP Corpus**: Extract name patterns for disambiguation |
| `short_bio` | Text | Nullable | Brief description (1-2 sentences) | **Content Length Analysis**: Average bio length over time |
| `long_bio` | Text | Nullable | Full biography | **NLP Feature**: Extract keywords for content recommendation |
| `language` | String(50) | Nullable, Indexed | Primary language (e.g., "awadhi", "hindi") | **Language Distribution**: Which languages dominate corpus? |
| `is_deleted` | Boolean | Default=False | Soft-delete flag | **Content Moderation**: Track deletion reasons (requires audit log) |
| `created_at` | DateTime(TZ) | Server default | Record creation time | **Corpus Growth**: New authors added per month |
| `updated_at` | DateTime(TZ) | On update | Last edit time | **Content Maintenance**: Identify stale bios (no update in 2+ years) |

**Indexes:**
- `ix_authors_slug`: Used in `/authors/{slug}` lookups.
- `ix_authors_language`: Used in `/authors?language=awadhi` filters.

**Relationships:**
- `works`: One-to-many relationship with `classical_works.author_id`.

**Logic Flow (Author Creation by Admin):**
1. Admin calls `POST /admin/hierarchy/authors` with `{"slug": "tulsidas", "name": "Goswami Tulsidas", ...}`.
2. System checks `classical_authors` for existing `slug='tulsidas'`.
3. If exists → Return 400 "Author slug already exists".
4. If not exists → Insert new row with `is_deleted=False`.
5. Return `{"id": 1, "slug": "tulsidas", ...}`.

**🔬 Data Science & Analytics Perspective:**

**Feature Engineering:**
1. **Author Productivity**: `COUNT(classical_works WHERE author_id = X)` → Prolific vs niche authors.
2. **Bio Completeness Score**: `(long_bio IS NOT NULL) + (short_bio IS NOT NULL) + (language IS NOT NULL)` / 3.

**Visualizations:**
1. **Author Network Graph**: Nodes = Authors, Edges = Shared keywords in `long_bio` (use TF-IDF similarity).
2. **Language Distribution Bar Chart**: X-axis = Language, Y-axis = Author Count.

**ML Opportunities:**
1. **Author Recommendation**: "Users who read Tulsidas also read Kabir" (collaborative filtering on `doha_entries.author_id`).
2. **Bio Quality Prediction**: Train classifier on `[bio_length, has_short_bio, has_long_bio]` → Predict user engagement with author page.

---

#### **Table: `classical_works`**

**Column-by-Column Audit:**

| Column | Type | Constraints | Purpose | Data Science Relevance |
|--------|------|-------------|---------|------------------------|
| `id` | Integer | Primary Key | Work identifier | **Entity ID**: Join key for chapters, dohas |
| `author_id` | Integer | FK, Indexed | Parent author | **Hierarchy Analysis**: Works per author distribution |
| `slug` | String(150) | Composite Unique (author_id, slug), Indexed | URL-safe identifier (e.g., "ramcharitmanas") | **SEO Feature**: Track most-visited work pages |
| `title` | String(255) | Not Null | Display name (e.g., "Ramcharitmanas") | **NLP Corpus**: Extract title patterns for genre classification |
| `description` | Text | Nullable | Work summary | **Content Completeness**: % of works with descriptions |
| `work_type` | String(50) | Nullable, Indexed | Genre (e.g., "epic", "poetry", "prose") | **Genre Distribution**: Pie chart of work types |
| `original_script` | String(50) | Nullable | Original writing system (e.g., "devanagari", "persian") | **Script Analysis**: Track script diversity |
| `is_deleted` | Boolean | Default=False | Soft-delete flag | **Content Moderation**: Deletion rate per work type |
| `created_at` | DateTime(TZ) | Server default | Record creation time | **Corpus Growth**: New works added per month |
| `updated_at` | DateTime(TZ) | On update | Last edit time | **Content Maintenance**: Identify stale descriptions |

**Indexes:**
- `ix_works_author_id`: Used in `/authors/{slug}/works` listings.
- `ix_works_slug`: Used in `/authors/{slug}/works/{work_slug}` lookups.
- `ix_works_work_type`: Used in `/authors/{slug}/works?work_type=epic` filters.

**Unique Constraint:**
- `uq_works_author_slug` on `(author_id, slug)`: Same work slug allowed for different authors (e.g., multiple "mahabharata" translations).

**Relationships:**
- `author`: Many-to-one with `classical_authors`.
- `chapters`: One-to-many with `work_chapters`.

**Logic Flow (Work Creation by Admin):**
1. Admin calls `POST /admin/hierarchy/authors/{author_id}/works` with `{"slug": "ramcharitmanas", ...}`.
2. System validates `author_id` exists and `is_deleted=False`.
3. System checks for existing `(author_id, slug)` pair.
4. If exists → Return 400 "Work slug already exists for this author".
5. If not exists → Insert new row.
6. Return `{"id": 5, "author_id": 1, "slug": "ramcharitmanas", ...}`.

**🔬 Data Science & Analytics Perspective:**

**Feature Engineering:**
1. **Work Depth**: `COUNT(work_chapters WHERE work_id = X)` → Complexity metric.
2. **Script Diversity Score**: `COUNT(DISTINCT original_script)` / `COUNT(*)` → How multilingual is corpus?

**Visualizations:**
1. **Work Type Sunburst Chart**: Inner ring = Author, Outer ring = Work Type.
2. **Temporal Heatmap**: X-axis = Month, Y-axis = Work Type, Color = New Works Added.

**ML Opportunities:**
1. **Genre Classification**: Train on `[title, description]` → Predict `work_type` for new submissions.
2. **Work Clustering**: K-means on TF-IDF vectors of `description` → Discover hidden sub-genres.

---

#### **Table: `work_chapters`**

**Column-by-Column Audit:**

| Column | Type | Constraints | Purpose | Data Science Relevance |
|--------|------|-------------|---------|------------------------|
| `id` | Integer | Primary Key | Chapter identifier | **Entity ID**: Join key for dohas |
| `work_id` | Integer | FK, Indexed | Parent work | **Hierarchy Analysis**: Chapters per work distribution |
| `slug` | String(150) | Composite Unique (work_id, slug), Indexed | URL-safe identifier (e.g., "ayodhya-kand") | **SEO Feature**: Track most-visited chapter pages |
| `title` | String(255) | Not Null | Display name (e.g., "अयोध्या काण्ड") | **Multilingual Analysis**: Script detection in titles |
| `number` | Integer | Composite Unique (work_id, number), Indexed | Sequential chapter number | **Navigation Feature**: Essential for prev/next chapter links |
| `is_deleted` | Boolean | Default=False | Soft-delete flag | **Content Moderation**: Accidental deletions |
| `created_at` | DateTime(TZ) | Server default | Record creation time | **Content Growth**: New chapters added per month |
| `updated_at` | DateTime(TZ) | On update | Last edit time | **Content Maintenance**: Track title corrections |

**Indexes:**
- `ix_chapters_work_id`: Used in `/authors/{slug}/works/{work_slug}/chapters` listings.
- `ix_chapters_slug`: Used in direct slug lookups (rare).
- `ix_chapters_number`: Used in `ORDER BY number ASC` queries.

**Unique Constraints:**
- `uq_chapters_work_slug` on `(work_id, slug)`.
- `uq_chapters_work_number` on `(work_id, number)`: Enforces no duplicate chapter numbers within a work.

**Relationships:**
- `work`: Many-to-one with `classical_works`.

**Logic Flow (Chapter Creation by Admin):**
1. Admin calls `POST /admin/hierarchy/works/{work_id}/chapters` with `{"slug": "ayodhya-kand", "number": 2, ...}`.
2. System validates `work_id` exists and `is_deleted=False`.
3. System checks for existing `(work_id, slug)` pair → 400 if exists.
4. System checks for existing `(work_id, number)` pair → 400 if exists.
5. If both checks pass → Insert new row.
6. Return `{"id": 10, "work_id": 5, "slug": "ayodhya-kand", "number": 2}`.

**🔬 Data Science & Analytics Perspective:**

**Feature Engineering:**
1. **Chapter Density**: `COUNT(doha_entries WHERE chapter_id = X)` → Identify dense vs sparse chapters.
2. **Number Gaps**: Detect missing chapters (e.g., work has chapters 1, 2, 4 but not 3).

**Visualizations:**
1. **Chapter Length Distribution**: Histogram of `COUNT(dohas) per chapter`.
2. **Work Completion Timeline**: Line chart showing cumulative chapters added per work over time.

**ML Opportunities:**
1. **Chapter Recommendation**: "If you finished Chapter 2, 85% of users read Chapter 3 next" (sequence analysis).

---


### 2.1.3 MODULE 4: Submission & Moderation

#### **Table: `submissions`**

**Column-by-Column Audit:**

| Column | Type | Constraints | Purpose | Data Science Relevance |
|--------|------|-------------|---------|------------------------|
| `id` | Integer | Primary Key | Submission identifier | **Workflow Tracking**: Join key for moderation logs |
| `content_type` | String(50) | Not Null | Content category: "doha", "dictionary", "idiom", "article" | **Content Mix Analysis**: Distribution of submission types |
| `main_text` | Text | Not Null | Primary content (doha text, dictionary lemma, idiom phrase, article body) | **Content Length**: Character count distribution by type |
| `meaning` | Text | Nullable | Translation/explanation | **Translation Coverage**: % of submissions with meanings |
| `is_classical` | Boolean | Default=False | Whether content belongs to existing classical hierarchy | **Classical vs Community Ratio**: Track corpus composition |
| `author_slug` | String(150) | Nullable | For classical content, references `classical_authors.slug` | **Attribution Pattern**: Most frequently submitted authors |
| `work_slug` | String(150) | Nullable | For classical content, references `classical_works.slug` | **Work Popularity**: Which works receive most submissions? |
| `chapter_slug` | String(150) | Nullable | For classical content, references `work_chapters.slug` | **Chapter Coverage**: Identify chapters with gaps |
| `number_in_chapter` | Integer | Nullable | Sequential number within chapter | **Numbering Conflicts**: Detect duplicate submissions for same position |
| `external_references` | JSON | Nullable | Metadata (e.g., `{"text_devanagari": "...", "lemma_roman": "..."}`) | **Metadata Richness**: % of submissions with complete metadata |
| `status` | String(20) | Default='draft' | Workflow state: "draft", "pending_review", "approved", "rejected", "archived" | **Pipeline Velocity**: Average time from draft → approved |
| `visibility` | String(20) | Default='private' | Access control: "private", "public" | **Privacy Preference**: % of users keeping drafts private |
| `version` | Integer | Default=1 | Optimistic locking counter | **Edit Frequency**: Distribution of version numbers |
| `contributor_id` | Integer | Indexed, Not Null | FK to `users.id` | **Contributor Activity**: Submissions per user histogram |
| `assigned_moderator_id` | Integer | Indexed, Nullable | FK to `users.id` (moderator) | **Workload Distribution**: Submissions per moderator |
| `priority` | Integer | Default=0 | Queue priority (higher = more urgent) | **Priority Usage**: Is priority actually used in practice? |
| `is_deleted` | Boolean | Default=False | Soft-delete flag | **Deletion Rate**: % of submissions deleted before approval |
| `created_at` | DateTime(TZ) | Server default | Submission timestamp | **Time-Series**: Submissions per hour/day/month |
| `updated_at` | DateTime(TZ) | On update | Last edit timestamp | **Edit Activity**: Time between creation and last update |

**Indexes:**
- `ix_submissions_contributor`: Used in `/submissions/me` (user's own submissions).
- `ix_submissions_status_created`: Composite index for moderation queue queries `WHERE status='pending_review' ORDER BY created_at`.
- `ix_submissions_assigned_mod`: Used in `/moderation/submissions?assigned_to_me=true`.

**Logic Flow (Submission Creation):**
1. User calls `POST /submissions` with payload:
   ```json
   {
     "content_type": "doha",
     "main_text": "श्रीरामचन्द्र कृपालु भजु मन",
     "meaning": "Worship kind-hearted Shri Ramchandra",
     "is_classical": true,
     "author_slug": "tulsidas",
     "work_slug": "ramcharitmanas",
     "chapter_slug": "ayodhya-kand",
     "number_in_chapter": 23,
     "submit_for_review": true
   }
   ```
2. **Rate Limit Check** (Line 1, `app/services/rate_limit.py`): System checks `rate_limit_counters` for `action_key='submission_create'`, `user_id={current_user.id}`. If count > 20 in last 24 hours → Return 429.
3. **Classical Validation** (Line 45, `app/api/v1/submissions.py:_validate_classical_reference`):
   - If `is_classical=True`, system queries `classical_authors` for `slug='tulsidas'`.
   - If not found → Return 400 "Invalid author_slug for classical submission".
   - If found → Query `classical_works` for `author_id={author.id} AND slug='ramcharitmanas'`.
   - If not found → Return 400 "Invalid work_slug for this author".
   - If found → Query `work_chapters` for `work_id={work.id} AND slug='ayodhya-kand'`.
   - If not found → Return 400 "Invalid chapter_slug for this work".
   - If `number_in_chapter <= 0` → Return 400 "number_in_chapter must be positive".
4. **Status Determination** (Line 78): If `submit_for_review=True` → `status='pending_review'`. Else `status='draft'`.
5. **Insert Row** (Line 85):
   ```python
   submission = Submission(
       content_type="doha",
       main_text="श्रीरामचन्द्र कृपालु भजु मन",
       meaning="Worship kind-hearted Shri Ramchandra",
       is_classical=True,
       author_slug="tulsidas",
       work_slug="ramcharitmanas",
       chapter_slug="ayodhya-kand",
       number_in_chapter=23,
       external_references=None,
       status="pending_review",
       visibility="private",
       version=1,
       contributor_id=5,
       priority=0,
   )
   db.add(submission)
   db.commit()
   ```
6. **Return Response**: `{"id": 42, "status": "pending_review", "version": 1, ...}`.

**Logic Flow (Submission Update with Optimistic Locking):**
1. User calls `PUT /submissions/{submission_id}` with:
   ```json
   {
     "main_text": "updated text",
     "expected_version": 1
   }
   ```
2. System queries `submissions` for `id={submission_id} AND is_deleted=False`.
3. **Ownership Check** (Line 200): If `submission.contributor_id != current_user.id AND current_user.role != 'admin'` → Return 403.
4. **Status Check** (Line 205): If `submission.status NOT IN ('draft', 'rejected')` → Return 400 "Cannot edit submission in status 'pending_review'".
5. **Version Check** (Line 210): If `submission.version != expected_version` → Return 409 "Version conflict. Current version is 2".
6. **Update Fields** (Line 215):
   ```python
   submission.main_text = "updated text"
   submission.version = submission.version + 1  # Increment to 2
   db.commit()
   ```
7. **Return Updated Submission**: `{"id": 42, "main_text": "updated text", "version": 2, ...}`.

**🔬 Data Science & Analytics Perspective:**

**Feature Engineering:**
1. **Submission Pipeline Velocity**:
   - `time_to_review = (first_moderation_log.created_at) - (submission.created_at)`
   - `time_to_approval = (approved_log.created_at) - (submission.created_at)`
   - **Metric**: Median time_to_approval per `content_type`.

2. **Classical Content Ratio**:
   - `(COUNT(is_classical=True) / COUNT(*)) * 100` → Track corpus balance.

3. **Contributor Productivity Score**:
   - `approved_count / total_submissions` → Identify high-quality contributors.

4. **Priority Effectiveness**:
   - Compare `time_to_approval` for `priority > 0` vs `priority = 0` → Is priority actually speeding up reviews?

**Visualizations:**
1. **Submission Funnel (Sankey Diagram)**:
   - Nodes: `draft → pending_review → approved → canonical`.
   - Edges: Flow of submissions through states.
   - Include rejection branch: `pending_review → rejected → (draft or deleted)`.

2. **Moderation Queue Heatmap**:
   - X-axis: Day of Week.
   - Y-axis: Hour of Day.
   - Color: `COUNT(submissions WHERE status='pending_review')`.
   - **Insight**: Identify peak moderation hours.

3. **Content Type Distribution Over Time (Stacked Area Chart)**:
   - X-axis: Month.
   - Y-axis: Submission Count.
   - Stacks: `doha`, `dictionary`, `idiom`, `article`.

**ML Opportunities:**
1. **Approval Prediction**:
   - Features: `[content_length, is_classical, has_meaning, contributor_history, content_type]`.
   - Target: `status='approved'` (binary classification).
   - Model: Logistic Regression or LightGBM.
   - **Use Case**: Auto-flag submissions likely to be approved for fast-track review.

2. **Quality Scoring**:
   - Train regression model on `[submission_features] → approval_time`.
   - Predict review time for new submissions → Prioritize complex cases.

3. **Content Clustering**:
   - TF-IDF vectorization of `main_text` + `meaning`.
   - K-means clustering to discover submission themes (e.g., devotional vs historical).

---

#### **Table: `moderation_guidelines`**

**Column-by-Column Audit:**

| Column | Type | Constraints | Purpose | Data Science Relevance |
|--------|------|-------------|---------|------------------------|
| `id` | Integer | Primary Key | Guideline identifier | **Policy Evolution**: Track guideline changes over time |
| `version` | String(50) | Unique | Semantic version (e.g., "v1.0", "v2.1") | **Version Adoption**: Which guidelines are actively used? |
| `title` | String(255) | Not Null | Short name (e.g., "Content Quality Standards 2024") | **NLP Corpus**: Extract policy keywords |
| `description` | Text | Nullable | Full guideline text | **Policy Length**: Track policy complexity over time |
| `url` | String(500) | Nullable | External link to detailed docs | **External Reference**: % of guidelines with URLs |
| `is_active` | Boolean | Default=False | Whether this version is currently enforced | **Active Policy Count**: Should always be 1 active version |
| `created_at` | DateTime(TZ) | Server default | Guideline creation timestamp | **Policy Timeline**: When were guidelines added? |

**Unique Constraint:**
- `uq_moderation_guidelines_version` on `version`.

**Logic Flow (Admin Creates New Guideline Version):**
1. Admin detects need for policy update (e.g., new spam patterns).
2. Admin calls `POST /admin/moderation/guidelines` (endpoint not shown in code but implied):
   ```json
   {
     "version": "v2.0",
     "title": "Enhanced Spam Detection",
     "description": "...",
     "url": "https://docs.example.com/moderation-v2",
     "is_active": false
   }
   ```
3. System inserts new row with `is_active=False`.
4. Admin reviews guideline internally.
5. Admin calls `PATCH /admin/moderation/guidelines/{id}` with `{"is_active": true}`.
6. System sets `is_active=False` for all other guidelines (only 1 active at a time).
7. Future moderation actions reference `guideline_version='v2.0'`.

**🔬 Data Science & Analytics Perspective:**

**Feature Engineering:**
1. **Guideline Compliance**: `COUNT(moderation_logs WHERE guideline_version='v2.0') / COUNT(moderation_logs WHERE created_at >= v2.0_release_date)` → Adoption rate.
2. **Policy Drift Detection**: Compare approval rates before vs after new guideline activation.

**Visualizations:**
1. **Policy Timeline (Gantt Chart)**:
   - X-axis: Time.
   - Y-axis: Guideline Version.
   - Bars: Duration each version was active.

**ML Opportunities:**
1. **Policy Impact Analysis**: Regression on `[guideline_version] → approval_rate` → Quantify policy effectiveness.

---

#### **Table: `moderation_logs`**

**Column-by-Column Audit:**

| Column | Type | Constraints | Purpose | Data Science Relevance |
|--------|------|-------------|---------|------------------------|
| `id` | Integer | Primary Key | Log entry identifier | **Event ID**: Join key for audit analysis |
| `submission_id` | Integer | Indexed, Not Null | FK to `submissions.id` | **Submission Lifecycle**: Track all actions per submission |
| `moderator_id` | Integer | Indexed, Not Null | FK to `users.id` | **Moderator Activity**: Actions per moderator |
| `action` | String(50) | Not Null | Action type: "approve", "reject", "batch_approve", etc. | **Action Distribution**: Which actions are most common? |
| `from_status` | String(20) | Nullable | Previous submission status | **State Transition**: Track status changes |
| `to_status` | String(20) | Nullable | New submission status | **State Transition**: Build state machine diagram |
| `guideline_version` | String(50) | Nullable | Applied guideline version | **Policy Traceability**: Which guidelines were used? |
| `note` | Text | Nullable | Moderator's reason/comment | **NLP Corpus**: Extract common rejection reasons |
| `created_at` | DateTime(TZ) | Server default | Action timestamp | **Time-Series**: Moderation activity over time |

**Indexes:**
- `ix_moderation_logs_submission`: Used in "show all actions for submission X".
- `ix_moderation_logs_moderator`: Used in "show all actions by moderator Y".

**Logic Flow (Moderator Approves Submission):**
1. Moderator calls `POST /moderation/submissions/{submission_id}/approve` with:
   ```json
   {
     "note": "Content verified against original source",
     "guideline_version": "v1.0"
   }
   ```
2. **Authorization Check** (Line 1, `app/api/v1/moderation.py`): Ensure `current_user.role IN ('moderator', 'admin')`.
3. **Lock Submission** (Line 50): `db.query(Submission).filter(...).with_for_update().first()` → Prevents concurrent modifications.
4. **Status Validation** (Line 55): If `submission.status != 'pending_review'` → Return 400.
5. **Update Submission** (Line 60):
   ```python
   from_status = submission.status  # "pending_review"
   submission.status = "approved"
   if submission.assigned_moderator_id is None:
       submission.assigned_moderator_id = current_user.id
   ```
6. **Write Log** (Line 70):
   ```python
   log = ModerationLog(
       submission_id=submission.id,
       moderator_id=current_user.id,
       action="approve",
       from_status="pending_review",
       to_status="approved",
       guideline_version="v1.0",
       note="Content verified against original source",
   )
   db.add(log)
   ```
7. **Create Canonical Content** (Line 80, `app/services/content_service.py`):
   - If `content_type='doha'` → Call `create_canonical_doha_from_submission(db, submission, moderator)`.
   - Insert into `doha_entries` + `content_versions`.
8. **Commit Transaction** (Line 90): `db.commit()`.
9. **Return Updated Submission**: `{"id": 42, "status": "approved", ...}`.

**🔬 Data Science & Analytics Perspective:**

**Feature Engineering:**
1. **Moderator Performance Metrics**:
   - **Approval Rate**: `COUNT(action='approve') / COUNT(*)` per moderator.
   - **Rejection Rate**: `COUNT(action='reject') / COUNT(*)`.
   - **Speed**: Median `(moderation_log.created_at - submission.created_at)`.

2. **Rejection Reason Analysis**:
   - Extract keywords from `note` field using NLP (e.g., "spam", "low quality", "duplicate").
   - Build taxonomy of rejection reasons.

3. **Guideline Effectiveness**:
   - Group by `guideline_version`, calculate approval rates.
   - Detect if newer guidelines reduce rejection rates (better clarity).

**Visualizations:**
1. **Moderator Dashboard (Multi-Panel)**:
   - Panel 1: Actions per day (line chart).
   - Panel 2: Approval vs Rejection ratio (donut chart).
   - Panel 3: Average review time (bar chart).

2. **State Transition Diagram**:
   - Nodes: `draft`, `pending_review`, `approved`, `rejected`, `archived`.
   - Edges: Labeled with action names (e.g., "approve", "reject").
   - Edge thickness: Proportional to transition frequency.

3. **Rejection Reason Word Cloud**:
   - Extract all `note` text from `action='reject'` logs.
   - Generate word cloud with font size = frequency.

**ML Opportunities:**
1. **Rejection Reason Classification**:
   - Train multi-class classifier on `note` text → Predict reason category (spam, quality, duplicate, other).
   - Use for automated tagging + analytics dashboard.

2. **Moderator Consistency Analysis**:
   - Compare approval decisions for similar submissions across moderators.
   - Flag outliers (e.g., Moderator A approves 90% while others approve 60%).

3. **Auto-Moderation Candidates**:
   - Train model on `[submission_features, historical_outcome]` → Predict approval probability.
   - Auto-approve submissions with >95% confidence (human review for edge cases).

---

### 2.1.4 MODULE 6: Canonical Content

#### **Table: `doha_entries`**

**Column-by-Column Audit:**

| Column | Type | Constraints | Purpose | Data Science Relevance |
|--------|------|-------------|---------|------------------------|
| `id` | Integer | Primary Key | Canonical doha identifier | **Entity ID**: Core content piece for all analytics |
| `hierarchy_path` | String(512) | Nullable, Indexed | Computed path: "author/work/chapter/number" (e.g., "tulsidas/ramcharitmanas/ayodhya-kand/23") | **URL Routing**: Used in SEO-friendly URLs |
| `author_id` | Integer | Nullable, Indexed | FK to `classical_authors.id` | **Author Attribution**: Link dohas to authors for recommendation |
| `work_id` | Integer | Nullable, Indexed | FK to `classical_works.id` | **Work Attribution**: Aggregate dohas per work |
| `chapter_id` | Integer | Nullable, Indexed | FK to `work_chapters.id` | **Chapter Attribution**: Display dohas in chapter context |
| `number_in_chapter` | Integer | Nullable | Sequential number (1, 2, 3...) | **Ordering**: Essential for "next doha" navigation |
| `main_text` | Text | Not Null | Primary doha text (original script) | **Search Corpus**: Main search target |
| `meaning` | Text | Nullable | Translation/explanation | **Bilingual Search**: Search in both text + meaning |
| `text_devanagari` | Text | Nullable | Devanagari script version | **Script-Specific Search**: Full-text search in Devanagari |
| `text_romanized` | Text | Nullable | Roman transliteration | **Cross-Script Search**: Search "rama" finds "राम" |
| `status` | String(20) | Default='active' | Publication state: "active", "hidden", "archived" | **Content Filtering**: Only show active in public APIs |
| `visibility` | String(20) | Default='public' | Access control: "public", "private", "restricted" | **Access Control**: Private dohas only visible to creator |
| `version` | Integer | Default=1 | Version counter | **Content Evolution**: Track edits over time |
| `is_canonical` | Boolean | Default=True | Whether this is the primary version (vs alternative interpretations) | **Variant Management**: Future feature for multiple interpretations |
| `variant_group_id` | Integer | Nullable | Groups related variants together | **Variant Linking**: Not yet implemented |
| `confidence_level` | Integer | Nullable | Quality score (0-100) | **Quality Metric**: Filter low-confidence entries |
| `source_reference` | JSON | Nullable | External citation (e.g., `{"book": "...", "page": 42}`) | **Citation Tracking**: Build bibliography |
| `source_submission_id` | Integer | Unique, Nullable | FK to `submissions.id` | **Traceability**: Link canonical to original submission |
| `created_by` | Integer | Nullable | FK to `users.id` (original contributor) | **Attribution**: Credit contributors |
| `verified_by` | Integer | Nullable | FK to `users.id` (moderator who approved) | **Quality Assurance**: Track who verified content |
| `verified_at` | DateTime(TZ) | Nullable | Verification timestamp | **Verification Timeline**: Time from submission to verification |
| `is_deleted` | Boolean | Default=False | Soft-delete flag | **Content Moderation**: Accidental deletions recoverable |
| `created_at` | DateTime(TZ) | Server default | Record creation timestamp | **Content Growth**: Dohas added over time |
| `updated_at` | DateTime(TZ) | On update | Last edit timestamp | **Content Maintenance**: Track edit activity |

**Indexes:**
- `ix_doha_hierarchy_path`: Used in `/content/by-path/{hierarchy_path}` lookups.
- `ix_doha_author_id`, `ix_doha_work_id`, `ix_doha_chapter_id`: Used in filtered queries (e.g., "all dohas by Tulsidas").
- **FULLTEXT Index** (MySQL only): `ft_doha_main_meaning_devanagari_romanized` on `(main_text, meaning, text_devanagari, text_romanized)` → Used in `/search` endpoint.

**Unique Constraint:**
- `uq_doha_source_submission` on `source_submission_id`: One submission creates exactly one canonical doha.

**Relationships:**
- `engagement_kpi`: One-to-one with `engagement_kpis` (via `content_type='doha', content_id=doha.id`).

**Logic Flow (Canonical Doha Creation from Approved Submission):**
1. Moderator approves submission (see previous section).
2. System calls `create_canonical_doha_from_submission(db, submission, moderator)` (Line 1, `app/services/content_service.py`).
3. **Idempotency Check** (Line 10):
   ```python
   existing = db.query(DohaEntry).filter(
       DohaEntry.source_submission_id == submission.id,
       DohaEntry.is_deleted == False,
   ).first()
   if existing:
       return existing  # Already created
   ```
4. **Hierarchy Resolution** (Line 20, if `is_classical=True`):
   - Query `classical_authors` for `slug={submission.author_slug}`.
   - If not found → Raise 400 "Invalid author_slug".
   - Query `classical_works` for `author_id={author.id} AND slug={submission.work_slug}`.
   - If not found → Raise 400 "Invalid work_slug".
   - Query `work_chapters` for `work_id={work.id} AND slug={submission.chapter_slug}`.
   - If not found → Raise 400 "Invalid chapter_slug".
   - Compute `hierarchy_path = f"{author.slug}/{work.slug}/{chapter.slug}/{submission.number_in_chapter}"`.
5. **Insert Doha** (Line 50):
   ```python
   doha = DohaEntry(
       hierarchy_path="tulsidas/ramcharitmanas/ayodhya-kand/23",
       author_id=1,
       work_id=5,
       chapter_id=10,
       number_in_chapter=23,
       main_text="श्रीरामचन्द्र कृपालु भजु मन",
       meaning="Worship kind-hearted Shri Ramchandra",
       text_devanagari="श्रीरामचन्द्र कृपालु भजु मन",
       text_romanized=None,
       status="active",
       visibility="public",
       version=1,
       is_canonical=True,
       source_submission_id=42,
       created_by=5,
       verified_by=moderator.id,
       verified_at=datetime.utcnow(),
   )
   db.add(doha)
   db.flush()  # Get doha.id
   ```
6. **Create Version Snapshot** (Line 80):
   ```python
   version = ContentVersion(
       content_type="doha",
       content_id=doha.id,
       version_number=1,
       main_text=submission.main_text,
       meaning=submission.meaning,
       text_devanagari=submission.main_text,
       created_by=submission.contributor_id,
       notes=f"Created from submission {submission.id}",
   )
   db.add(version)
   ```
7. **Commit** (Caller's responsibility): `db.commit()`.
8. **Return Doha Object**: `return doha`.

**🔬 Data Science & Analytics Perspective:**

**Feature Engineering:**
1. **Corpus Coverage Metrics**:
   - **Author Coverage**: `COUNT(DISTINCT author_id) / COUNT(*) FROM classical_authors` → % of authors with dohas.
   - **Work Coverage**: `COUNT(DISTINCT work_id)` per author → Identify incomplete works.
   - **Chapter Coverage**: For each work, calculate `(chapters_with_dohas / total_chapters) * 100`.

2. **Content Quality Score**:
   - `has_meaning` (boolean): +1 point.
   - `has_text_devanagari` (boolean): +1 point.
   - `has_text_romanized` (boolean): +1 point.
   - `confidence_level >= 80`: +2 points.
   - **Total**: 0-5 scale → Filter for quality > 3.

3. **Verification Lag**:
   - `verified_at - created_at` → Track moderation speed.
   - Group by `verified_by` → Identify fast vs slow moderators.

**Visualizations:**
1. **Corpus Heatmap (2D)**:
   - X-axis: Authors (sorted by total dohas).
   - Y-axis: Works.
   - Cell color: `COUNT(dohas)` in that author-work pair.
   - **Insight**: Visualize which author-work combinations are dense vs sparse.

2. **Hierarchy Tree (Interactive D3.js)**:
   - Root node: "Corpus".
   - Level 1: Authors (node size = doha count).
   - Level 2: Works (expandable).
   - Level 3: Chapters (expandable).
   - Leaf nodes: Individual dohas (click to view).

3. **Content Quality Distribution (Histogram)**:
   - X-axis: Quality score (0-5).
   - Y-axis: `COUNT(dohas)`.
   - Overlay: Cumulative percentage line.

**ML Opportunities:**
1. **Automatic Romanization**:
   - Train seq2seq model on `(text_devanagari, text_romanized)` pairs.
   - Predict romanization for new dohas lacking it.
   - Use **Indic NLP libraries** (e.g., `indic-transliteration` Python package) as baseline.

2. **Meaning Generation (Summarization)**:
   - Fine-tune **mT5** (multilingual T5) on `(main_text, meaning)` pairs.
   - Generate draft meanings for dohas lacking them → Speed up moderation.

3. **Duplicate Detection**:
   - Compute TF-IDF vectors for all `main_text` fields.
   - Calculate cosine similarity → Flag pairs with similarity > 0.9 as potential duplicates.
   - Use **LSH (Locality-Sensitive Hashing)** for large-scale duplicate detection.

4. **Content Recommendation**:
   - **Collaborative Filtering**: "Users who viewed doha X also viewed doha Y".
   - **Content-Based**: Recommend dohas with similar `main_text` (TF-IDF similarity).
   - **Hybrid**: Combine engagement data + content similarity.

---

#### **Table: `content_versions`**

**Column-by-Column Audit:**

| Column | Type | Constraints | Purpose | Data Science Relevance |
|--------|------|-------------|---------|------------------------|
| `id` | Integer | Primary Key | Version record identifier | **History Tracking**: Every edit creates new row |
| `content_type` | String(50) | Not Null | Content category: "doha", "dictionary", "idiom", "article" | **Versioning Scope**: Which types have most edits? |
| `content_id` | Integer | Not Null | FK to respective table (e.g., `doha_entries.id`) | **Content Linkage**: Join to original content |
| `version_number` | Integer | Not Null | Sequential version (1, 2, 3...) | **Edit Frequency**: Distribution of version numbers |
| `main_text` | Text | Nullable | Snapshot of primary text | **Diff Analysis**: Compare versions to extract edits |
| `meaning` | Text | Nullable | Snapshot of translation | **Translation Evolution**: Track how meanings improve |
| `text_devanagari` | Text | Nullable | Snapshot of Devanagari script | **Script Changes**: Rare, but track corrections |
| `text_romanized` | Text | Nullable | Snapshot of romanization | **Romanization Improvements**: Track consistency over time |
| `created_by` | Integer | Nullable | FK to `users.id` | **Edit Attribution**: Who made this change? |
| `created_at` | DateTime(TZ) | Server default | Version creation timestamp | **Edit Timeline**: When were changes made? |
| `notes` | Text | Nullable | Change description | **Change Log**: Extract common edit reasons |

**Composite Index:**
- `ix_content_versions_type_id` on `(content_type, content_id)`: Used in `/content/doha/{id}/history` queries.

**Logic Flow (Version History Query):**
1. User calls `GET /content/doha/{doha_id}/history`.
2. System queries:
   ```python
   versions = db.query(ContentVersion).filter(
       ContentVersion.content_type == "doha",
       ContentVersion.content_id == doha_id,
   ).order_by(ContentVersion.version_number.asc()).all()
   ```
3. Returns list:
   ```json
   [
     {
       "id": 1,
       "version_number": 1,
       "main_text": "original text",
       "created_by": 5,
       "created_at": "2024-01-15T10:30:00Z",
       "notes": "Created from submission 42"
     },
     {
       "id": 2,
       "version_number": 2,
       "main_text": "corrected text",
       "created_by": 8,
       "created_at": "2024-02-20T14:15:00Z",
       "notes": "Fixed typo in original"
     }
   ]
   ```

**🔬 Data Science & Analytics Perspective:**

**Feature Engineering:**
1. **Edit Velocity**:
   - `COUNT(content_versions WHERE content_id = X)` → Number of edits per content piece.
   - Group by `content_type` → Which types


### 2.1.5 MODULE 16: Dictionary, Idiom, and Article Entries

#### **Table: `dictionary_entries`**

**Column-by-Column Audit:**

| Column | Type | Constraints | Purpose | Data Science Relevance |
|--------|------|-------------|---------|------------------------|
| `id` | Integer | Primary Key | Dictionary entry identifier | **Entity ID**: Core lexicon piece |
| `lemma_devanagari` | String(512) | Not Null, Indexed | Word in Devanagari (e.g., "मुख्य शब्द") | **Search Target**: Primary search field for Devanagari queries |
| `lemma_roman` | String(512) | Nullable, Indexed | Roman transliteration (e.g., "mukhya shabd") | **Cross-Script Search**: Enables Latin keyboard searches |
| `lemma_roman_norm` | String(512) | Nullable, Indexed | Normalized Roman (lowercase, no diacritics, spaces collapsed) | **Fuzzy Matching**: "mukhyashabd" matches "mukhya shabd" |
| `language` | String(16) | Default='hi' | ISO 639-1 code ("hi", "awa", "bho") | **Language Distribution**: Track lexicon diversity |
| `senses` | JSON | Not Null | Array of sense objects: `[{"definition": "...", "pos": "noun", "examples": [...], "synonyms": [...]}]` | **Semantic Richness**: Average senses per entry |
| `pronunciation` | String(255) | Nullable | IPA notation (e.g., "/muːkʰjə/") | **Phonetic Coverage**: % of entries with pronunciation |
| `examples` | JSON | Nullable | Array of usage examples: `["sentence 1", "sentence 2"]` | **Example Coverage**: % of entries with examples |
| `contributor_id` | Integer | Nullable, Indexed | FK to `users.id` (original submitter) | **Contributor Activity**: Entries per user |
| `author_id` | Integer | Nullable, Indexed | FK to `classical_authors.id` (if classical reference) | **Source Attribution**: Link to classical works |
| `work_id` | Integer | Nullable, Indexed | FK to `classical_works.id` | **Work Context**: Words from which works? |
| `chapter_id` | Integer | Nullable, Indexed | FK to `work_chapters.id` | **Chapter Context**: Precise source location |
| `number_in_chapter` | Integer | Nullable | Position in chapter | **Ordering**: Sequential reference |
| `source_submission_id` | Integer | Unique, Nullable | FK to `submissions.id` | **Traceability**: Link canonical to submission |
| `visibility` | String(20) | Default='public' | Access control: "public", "private" | **Access Pattern**: % of private entries |
| `version` | Integer | Default=1 | Version counter | **Edit Tracking**: Lexicon evolution |
| `created_at` | DateTime(TZ) | Server default | Entry creation timestamp | **Lexicon Growth**: Words added over time |
| `updated_at` | DateTime(TZ) | On update | Last edit timestamp | **Maintenance Activity**: Recent updates |

**Indexes:**
- `ix_dictionary_lemma_devanagari`: B-tree index for exact Devanagari lookups.
- `ix_dictionary_lemma_roman`: B-tree index for exact Roman lookups.
- `ix_dictionary_lemma_roman_norm`: B-tree index for normalized searches.
- **FULLTEXT Index** (MySQL only): `ft_dictionary_lemma_fulltext` on `(lemma_devanagari, lemma_roman)` → Used in `/dictionary?q=...` searches.

**Logic Flow (Dictionary Entry Creation from Approved Submission):**
1. Moderator approves submission with `content_type='dictionary'`.
2. System calls `create_canonical_dictionary_from_submission(db, submission, moderator_user)` (Line 1, `app/services/content_service.py`).
3. **Payload Extraction** (Line 10):
   ```python
   refs = submission.external_references or {}
   payload_dict = {
       "lemma_devanagari": refs.get("lemma_devanagari") or submission.main_text,
       "lemma_roman": refs.get("lemma_roman"),
       "language": refs.get("language") or "hi",
       "senses": refs.get("senses") or [],
       "pronunciation": refs.get("pronunciation"),
       "examples": refs.get("examples"),
   }
   ```
4. **Validation** (Line 20, Pydantic):
   ```python
   payload = DictionaryPayload(**payload_dict)
   if len(payload.senses) > 10:
       raise ValidationError("Too many senses (max 10)")
   ```
5. **Idempotency Check** (Line 30):
   ```python
   existing = db.query(DictionaryEntry).filter(
       DictionaryEntry.source_submission_id == submission.id
   ).first()
   if existing:
       return existing.id
   ```
6. **Normalization** (Line 40):
   ```python
   from app.utils.text_normalize import normalize_roman
   lemma_roman_norm = normalize_roman(payload.lemma_roman)
   # normalize_roman implementation:
   # 1. Unicode NFKD decomposition
   # 2. Remove combining diacritics
   # 3. Lowercase
   # 4. Remove punctuation
   # 5. Collapse whitespace
   ```
7. **Insert Entry** (Line 50):
   ```python
   ent = DictionaryEntry(
       lemma_devanagari="मुख्य शब्द",
       lemma_roman="mukhya shabd",
       lemma_roman_norm="mukhya shabd",  # Already normalized
       language="hi",
       senses=[
           {"definition": "primary word", "pos": "noun", "examples": [], "synonyms": []}
       ],
       pronunciation=None,
       examples=None,
       contributor_id=5,
       source_submission_id=42,
       visibility="public",
       version=1,
   )
   db.add(ent)
   db.flush()
   ```
8. **Create Version Snapshot** (Line 80):
   ```python
   cv = ContentVersion(
       content_type="dictionary",
       content_id=ent.id,
       version_number=1,
       main_text=ent.lemma_devanagari,
       text_devanagari=ent.lemma_devanagari,
       text_romanized=ent.lemma_roman,
       created_by=submission.contributor_id,
       notes=f"Created from submission {submission.id}",
   )
   db.add(cv)
   ```
9. **Return Entry ID**: `return ent.id`.

**Logic Flow (Dictionary Search):**
1. User calls `GET /dictionary?q=mukhya`.
2. System normalizes query:
   ```python
   q_norm = normalize_roman("mukhya")  # "mukhya"
   ```
3. **Database Query** (Line 20, `app/api/v1/dictionary.py`):
   ```python
   results = db.query(DictionaryEntry).filter(
       DictionaryEntry.visibility == "public",
       (
           DictionaryEntry.lemma_devanagari.ilike(f"%mukhya%")
           | (DictionaryEntry.lemma_roman_norm == "mukhya")
           | DictionaryEntry.lemma_roman_norm.ilike(f"%mukhya%")
       ),
   ).offset(offset).limit(limit).all()
   ```
4. **Engagement Tracking** (Line 40):
   ```python
   for r in results:
       _inc_search_kpi(db, r.id)  # Increment search_hits_count
   db.commit()
   ```
5. **Return Results**:
   ```json
   [
     {
       "id": 10,
       "lemma_devanagari": "मुख्य शब्द",
       "lemma_roman": "mukhya shabd",
       "language": "hi",
       "version": 1
     }
   ]
   ```

**🔬 Data Science & Analytics Perspective:**

**Feature Engineering:**
1. **Lexicon Completeness Score**:
   - `has_pronunciation` (boolean): +1.
   - `has_examples` (boolean): +1.
   - `sense_count >= 2`: +1.
   - `all_senses_have_pos` (boolean): +1.
   - **Total**: 0-4 scale → Prioritize incomplete entries for enhancement.

2. **Part-of-Speech Distribution**:
   - Extract all `pos` values from `senses` JSON.
   - `COUNT(*) GROUP BY pos` → Pie chart of noun/verb/adjective distribution.

3. **Polysemy Score**:
   - `COUNT(senses)` per entry → Distribution of word senses.
   - **Insight**: Words with >5 senses may need disambiguation pages.

4. **Language Diversity Metric**:
   - `COUNT(DISTINCT language)` → Track how multilingual lexicon is.

**Visualizations:**
1. **Lexicon Growth Timeline (Cumulative Line Chart)**:
   - X-axis: Month.
   - Y-axis: Cumulative entry count.
   - Multiple lines: One per `language`.

2. **Sense Distribution Histogram**:
   - X-axis: Number of senses (1, 2, 3, 4, 5+).
   - Y-axis: `COUNT(entries)`.

3. **Completeness Heatmap**:
   - X-axis: Entry ID (sorted by creation date).
   - Y-axis: Completeness dimensions (pronunciation, examples, POS tags).
   - Cell color: Present (green) vs Missing (red).

**ML Opportunities:**
1. **Automatic Part-of-Speech Tagging**:
   - Train CRF or BiLSTM-CRF on existing `(lemma, pos)` pairs.
   - Predict POS for new entries lacking this metadata.
   - Use **Hindi POS taggers** (e.g., spaCy's Hindi model) as baseline.

2. **Definition Generation**:
   - Fine-tune **mBERT** (multilingual BERT) on `(lemma, definition)` pairs.
   - Generate draft definitions for new words → Speed up lexicography.

3. **Synonym Expansion**:
   - Build word embeddings (Word2Vec or FastText) on Awadhi corpus.
   - Find nearest neighbors to `lemma_devanagari` → Suggest synonyms.

4. **Cross-Lingual Linking**:
   - Match entries across languages using **multilingual embeddings** (e.g., LASER).
   - Link "मुख्य" (Hindi) ↔ "main" (English) ↔ "mukhya" (Roman).

---

#### **Table: `idiom_entries`**

**Column-by-Column Audit:**

| Column | Type | Constraints | Purpose | Data Science Relevance |
|--------|------|-------------|---------|------------------------|
| `id` | Integer | Primary Key | Idiom identifier | **Entity ID**: Phraseological unit |
| `text_devanagari` | Text | Not Null, Indexed | Idiom in Devanagari (e.g., "अंधों में काना राजा") | **Search Target**: Primary idiom text |
| `text_roman` | Text | Nullable | Roman transliteration (e.g., "andhon mein kana raja") | **Cross-Script Search**: MANDATORY per Pydantic schema |
| `text_roman_norm` | String(512) | Nullable, Indexed | Normalized Roman | **Fuzzy Matching**: "andhonmeinkanaraja" → normalized |
| `meaning` | Text | Nullable | Literal/figurative meaning (e.g., "Among blind, one-eyed is king") | **Semantic Understanding**: Translation |
| `examples` | JSON | Nullable | Usage examples: `["sentence 1", "sentence 2"]` | **Contextual Learning**: Real-world usage |
| `region` | String(64) | Nullable | Geographical variant (e.g., "Awadh", "Bhojpur") | **Dialectology**: Regional idiom distribution |
| `contributor_id` | Integer | Nullable, Indexed | FK to `users.id` | **Attribution**: Community contributions |
| `author_id` | Integer | Nullable, Indexed | FK to `classical_authors.id` | **Source Attribution**: Classical origins |
| `work_id` | Integer | Nullable, Indexed | FK to `classical_works.id` | **Work Context**: Idioms from literature |
| `chapter_id` | Integer | Nullable, Indexed | FK to `work_chapters.id` | **Precise Location**: Chapter reference |
| `number_in_chapter` | Integer | Nullable | Position in chapter | **Ordering**: Sequential reference |
| `source_submission_id` | Integer | Unique, Nullable | FK to `submissions.id` | **Traceability**: Link to submission |
| `visibility` | String(20) | Default='public' | Access control | **Privacy**: Public vs private idioms |
| `version` | Integer | Default=1 | Version counter | **Edit Tracking**: Idiom refinement |
| `created_at` | DateTime(TZ) | Server default | Creation timestamp | **Corpus Growth**: Idioms added over time |
| `updated_at` | DateTime(TZ) | On update | Last edit timestamp | **Maintenance**: Recent updates |

**Indexes:**
- `ix_idiom_text_roman_norm`: B-tree index for normalized searches.
- **FULLTEXT Index** (MySQL only): `ft_idiom_text_fulltext` on `(text_devanagari, text_roman)` → Full-text search.

**Pydantic Validation (CRITICAL REQUIREMENT):**
```python
class IdiomPayload(BaseModel):
    text_devanagari: str
    text_roman: str  # MANDATORY (not Optional)
    meaning: Optional[str] = None
    examples: Optional[list] = None
    region: Optional[str] = None
```

**Why `text_roman` is Mandatory:**
- **Search Consistency**: Without Roman transliteration, users with Latin keyboards cannot search idioms.
- **Cross-Script Linking**: Enables matching "andhon mein" ↔ "अंधों में".
- **Normalization Requirement**: `text_roman_norm` is computed from `text_roman` (cannot be NULL).

**Logic Flow (Idiom Entry Creation from Approved Submission):**
1. Moderator approves submission with `content_type='idiom'`.
2. System calls `create_canonical_idiom_from_submission(db, submission, moderator_user)`.
3. **Payload Extraction** (Line 10):
   ```python
   refs = submission.external_references or {}
   payload_dict = {
       "text_devanagari": refs.get("text_devanagari") or submission.main_text,
       "text_roman": refs.get("text_roman") or refs.get("textRoman"),  # Legacy key support
       "meaning": submission.meaning or refs.get("meaning"),
       "examples": refs.get("examples"),
       "region": refs.get("region"),
   }
   ```
4. **Validation** (Line 20):
   ```python
   payload = IdiomPayload(**payload_dict)
   # If text_roman is missing → Pydantic raises ValidationError
   ```
5. **Normalization** (Line 30):
   ```python
   text_roman_norm = normalize_roman(payload.text_roman)
   # "andhon mein kana raja" → "andhon mein kana raja" (already normalized in this case)
   ```
6. **Idempotency Check** (Line 40):
   ```python
   existing = db.query(IdiomEntry).filter(
       IdiomEntry.source_submission_id == submission.id
   ).first()
   if existing:
       return existing.id
   ```
7. **Insert Entry** (Line 50):
   ```python
   ent = IdiomEntry(
       text_devanagari="अंधों में काना राजा",
       text_roman="andhon mein kana raja",
       text_roman_norm="andhon mein kana raja",
       meaning="Among blind, one-eyed is king",
       examples=None,
       region="Awadh",
       contributor_id=5,
       source_submission_id=42,
       visibility="public",
       version=1,
   )
   db.add(ent)
   db.flush()
   ```
8. **Create Version Snapshot** (Line 80):
   ```python
   cv = ContentVersion(
       content_type="idiom",
       content_id=ent.id,
       version_number=1,
       main_text=ent.text_devanagari,
       meaning=ent.meaning,
       text_devanagari=ent.text_devanagari,
       text_romanized=ent.text_roman,
       created_by=submission.contributor_id,
       notes=f"Created from submission {submission.id}",
   )
   db.add(cv)
   ```
9. **Return Entry ID**: `return ent.id`.

**🔬 Data Science & Analytics Perspective:**

**Feature Engineering:**
1. **Regional Distribution**:
   - `COUNT(*) GROUP BY region` → Map of idiom density by region.
   - **Visualization**: Choropleth map of India with idiom count per state.

2. **Idiom Complexity Score**:
   - Word count in `text_devanagari`: Simple (2-3 words) vs Complex (5+ words).
   - Presence of `examples`: +1 point.
   - Presence of `meaning`: +1 point.

3. **Cross-Script Completeness**:
   - `(text_devanagari IS NOT NULL AND text_roman IS NOT NULL) / COUNT(*)` → % with both scripts.

**Visualizations:**
1. **Idiom Network Graph**:
   - Nodes: Idioms.
   - Edges: Shared words between idioms (e.g., both contain "राजा").
   - Edge thickness: Number of shared words.
   - **Insight**: Discover idiom clusters (e.g., animal idioms, royal idioms).

2. **Regional Distribution Pie Chart**:
   - Slices: Regions.
   - Size: `COUNT(idioms)` per region.

3. **Word Cloud (Idiom Keywords)**:
   - Extract all words from `text_devanagari`.
   - Font size: Word frequency across all idioms.

**ML Opportunities:**
1. **Idiom Origin Prediction**:
   - Features: `[word_count, has_animal_word, has_royal_word, region]`.
   - Target: `author_id` (classical vs folk origin).
   - Model: Random Forest classifier.

2. **Meaning Generation**:
   - Fine-tune **mT5** on `(text_devanagari, meaning)` pairs.
   - Generate meanings for idioms lacking translations.

3. **Cultural Context Extraction**:
   - Train NER (Named Entity Recognition) on `meaning` text.
   - Extract entities: Animals, occupations, locations.
   - Build taxonomy of cultural themes.

---

#### **Table: `article_entries`**

**Column-by-Column Audit:**

| Column | Type | Constraints | Purpose | Data Science Relevance |
|--------|------|-------------|---------|------------------------|
| `id` | Integer | Primary Key | Article identifier | **Entity ID**: Long-form content |
| `title` | String(512) | Not Null, Indexed | Article headline | **Search Target**: Primary title search |
| `title_devanagari` | String(512) | Nullable | Title in Devanagari | **Multilingual Titles**: Script variants |
| `title_roman` | String(512) | Nullable | Title in Roman script | **Cross-Script Search**: Latin keyboard access |
| `title_roman_norm` | String(512) | Nullable, Indexed | Normalized Roman title | **Fuzzy Matching**: Case/diacritic insensitive |
| `body` | Text | Not Null | Full article text (Markdown or plain text) | **Content Length**: Average article length |
| `excerpt` | Text | Nullable | Short summary (auto-generated if NULL) | **Preview Text**: First 300 chars if not provided |
| `author_id` | Integer | Nullable, Indexed | FK to `users.id` (author, NOT classical_authors) | **Authorship**: Link to user profile |
| `tags` | JSON | Nullable | Array of tags: `["history", "linguistics", "culture"]` | **Topic Classification**: Tag-based filtering |
| `contributor_id` | Integer | Nullable, Indexed | FK to `users.id` (submitter) | **Attribution**: May differ from author_id |
| `source_submission_id` | Integer | Unique, Nullable | FK to `submissions.id` | **Traceability**: Link to submission |
| `visibility` | String(20) | Default='public' | Access control | **Privacy**: Public vs private articles |
| `version` | Integer | Default=1 | Version counter | **Edit Tracking**: Article revisions |
| `created_at` | DateTime(TZ) | Server default | Publication timestamp | **Content Timeline**: Articles published per month |
| `updated_at` | DateTime(TZ) | On update | Last edit timestamp | **Update Frequency**: Recent edits |

**Indexes:**
- `ix_article_title_roman_norm`: B-tree index for normalized title searches.
- **FULLTEXT Index** (MySQL only): `ft_article_title_body` on `(title, body)` → Full-text search across title and content.

**Logic Flow (Article Entry Creation from Approved Submission):**
1. Moderator approves submission with `content_type='article'`.
2. System calls `create_canonical_article_from_submission(db, submission, moderator_user)`.
3. **Payload Extraction** (Line 10):
   ```python
   refs = submission.external_references or {}
   title = refs.get("title") or (submission.main_text.splitlines()[0] if submission.main_text else None)
   body = submission.main_text or refs.get("body")
   if not title or not body:
       raise ValueError("Article requires title and body")
   ```
4. **Validation** (Line 20):
   ```python
   payload = ArticlePayload(
       title=title,
       body=body,
       title_devanagari=refs.get("title_devanagari"),
       title_roman=refs.get("title_roman"),
       tags=refs.get("tags"),
       excerpt=refs.get("excerpt"),
   )
   ```
5. **Excerpt Auto-Generation** (Line 30):
   ```python
   excerpt = payload.excerpt
   if not excerpt and payload.body:
       excerpt = payload.body.strip()[:300]  # First 300 characters
   ```
6. **Idempotency Check** (Line 40):
   ```python
   existing = db.query(ArticleEntry).filter(
       ArticleEntry.source_submission_id == submission.id
   ).first()
   if existing:
       return existing.id
   ```
7. **Normalization** (Line 50):
   ```python
   title_roman_norm = normalize_roman(payload.title_roman)
   ```
8. **Insert Entry** (Line 60):
   ```python
   ent = ArticleEntry(
       title="Test Article",
       title_devanagari=None,
       title_roman=None,
       title_roman_norm=None,
       body="Full article body text...",
       excerpt="Full article body text..."[:300],
       author_id=None,  # User-level author, not classical
       tags=["test", "sample"],
       contributor_id=5,
       source_submission_id=42,
       visibility="public",
       version=1,
   )
   db.add(ent)
   db.flush()
   ```
9. **Create Version Snapshot** (Line 90):
   ```python
   cv = ContentVersion(
       content_type="article",
       content_id=ent.id,
       version_number=1,
       main_text=ent.title,
       meaning=ent.body[:500] if ent.body else None,  # Store excerpt in meaning
       text_devanagari=ent.title_devanagari,
       text_romanized=ent.title_roman,
       created_by=submission.contributor_id,
       notes=f"Created from submission {submission.id}",
   )
   db.add(cv)
   ```
10. **Return Entry ID**: `return ent.id`.

**Logic Flow (Article Search by Tags):**
1. User calls `GET /articles/by-tag/history`.
2. System queries:
   ```python
   rows = db.query(ArticleEntry).filter(
       ArticleEntry.tags.contains(["history"]),  # MySQL JSON contains
       ArticleEntry.visibility == "public"
   ).order_by(ArticleEntry.created_at.desc()).offset(offset).limit(limit).all()
   ```
3. Returns:
   ```json
   [
     {
       "id": 5,
       "title": "History of Awadhi Literature",
       "excerpt": "This article explores...",
       "tags": ["history", "literature"],
       "created_at": "2024-03-15T09:00:00Z"
     }
   ]
   ```

**🔬 Data Science & Analytics Perspective:**

**Feature Engineering:**
1. **Article Readability Score**:
   - **Flesch Reading Ease** (adapted for Hindi/Awadhi):
     - `206.835 - 1.015 * (words / sentences) - 84.6 * (syllables / words)`.
   - **Complexity Metrics**:
     - Average sentence length.
     - Unique word ratio (`DISTINCT words / total words`).

2. **Tag Co-Occurrence Matrix**:
   - Build matrix where `M[i][j] = COUNT(articles WITH tag_i AND tag_j)`.
   - **Use**: Recommend related tags for new articles.

3. **Author Productivity**:
   - `COUNT(articles) GROUP BY author_id` → Prolific vs occasional authors.

4. **Content Freshness**:
   - `NOW() - updated_at` → Days since last edit.
   - Flag stale articles (no update in 1+ year).

**Visualizations:**
1. **Tag Cloud (Interactive)**:
   - Font size: Tag frequency.
   - Click tag → Filter articles by that tag.

2. **Article Length Distribution (Histogram)**:
   - X-axis: Word count bins (0-500, 500-1000, 1000-2000, 2000+).
   - Y-axis: `COUNT(articles)`.

3. **Topic Evolution Timeline (Stacked Area Chart)**:
   - X-axis: Month.
   - Y-axis: Article count.
   - Stacks: Top 10 tags.
   - **Insight**: Track trending topics over time.

**ML Opportunities:**
1. **Automatic Tagging**:
   - Train multi-label classifier on `(title + body) → tags`.
   - Use **TF-IDF + SVM** or **BERT-based multi-label classification**.
   - Suggest tags for new articles.

2. **Article Recommendation**:
   - **Content-Based**: TF-IDF similarity on `body` text.
   - **Collaborative**: "Users who read article X also read article Y".
   - **Hybrid**: Combine content + engagement signals.

3. **Summarization**:
   - Fine-tune **mBART** or **Pegasus** on `(body, excerpt)` pairs.
   - Auto-generate excerpts for articles lacking them.

4. **Topic Modeling**:
   - Apply **LDA (Latent Dirichlet Allocation)** on article corpus.
   - Discover hidden topics beyond manual tags.

---


### 2.1.7 MODULE 9: Rate Limiting

#### **Table: `rate_limit_counters`**

**Column-by-Column Audit:**

| Column | Type | Constraints | Purpose | Data Science Relevance |
|--------|------|-------------|---------|------------------------|
| `id` | Integer | Primary Key | Counter record identifier | **Event ID**: Individual rate limit bucket |
| `user_id` | Integer | Nullable, Indexed | FK to `users.id` (NULL for anonymous requests) | **User Tracking**: Per-user rate limiting |
| `ip_address` | String(45) | Nullable | IPv4 (15 chars) or IPv6 (45 chars) | **IP-Based Limiting**: Track anonymous users |
| `action_key` | String(128) | Not Null, Indexed | Action identifier: "login", "search", "submission_create" | **Action Segmentation**: Different limits per action |
| `time_bucket_start` | DateTime(TZ) | Not Null, Indexed | Start of time window (rounded down to granularity) | **Time Bucketing**: Sliding window implementation |
| `count` | Integer | Default=0 | Request count in this bucket | **Rate Metric**: Actual usage vs limit |
| `granularity` | Integer | Default=60 | Bucket size in seconds (e.g., 60 = 1-minute buckets) | **Window Precision**: Finer buckets = smoother limits |
| `created_at` | DateTime(TZ) | Server default | Bucket creation timestamp | **First Request**: When did user start hitting this action? |
| `updated_at` | DateTime(TZ) | On update | Last increment timestamp | **Last Request**: Most recent activity |

**Unique Constraint:**
- `uq_rate_limit_bucket` on `(user_id, ip_address, action_key, time_bucket_start)`: One counter per user/IP per action per time bucket.

**Composite Index:**
- `ix_rl_action_bucket` on `(action_key, time_bucket_start)`: Used in cleanup queries (delete old buckets).

**Rate Limiting Algorithm (Sliding Window with Time Buckets):**

**Configuration (Stored in `system_settings`):**
```json
{
  "rate_limits": {
    "login": {"limit": 10, "window_seconds": 3600},       // 10 login attempts per hour
    "search": {"limit": 120, "window_seconds": 60},       // 120 searches per minute
    "submission_create": {"limit": 20, "window_seconds": 86400}  // 20 submissions per day
  }
}
```

**Time Bucket Calculation:**
```python
def _bucket_start(now: datetime, granularity_seconds: int) -> datetime:
    """
    Round down timestamp to nearest bucket boundary.
    
    Example: now = 2024-12-14 10:37:45, granularity = 60
    → bucket_start = 2024-12-14 10:37:00
    """
    ts = int(now.timestamp())
    bucket_ts = (ts // granularity_seconds) * granularity_seconds
    return datetime.fromtimestamp(bucket_ts, tz=timezone.utc)
```

**Logic Flow (Rate Limit Check and Increment):**
1. User calls `POST /auth/login` with `{"email": "...", "password": "..."}`.
2. **Rate Limit Dependency** (Line 1, `app/api/v1/auth.py`):
   ```python
   @router.post("/login", dependencies=[Depends(login_rate_limit)])
   ```
3. **Dependency Execution** (Line 1, `app/services/rate_limit.py:rate_limit_dependency`):
   ```python
   def _dep(request: Request, db: Session = Depends(get_db)):
       user_id = None  # Extract from JWT if present (not yet authenticated for /login)
       ip = request.client.host or request.headers.get("X-Forwarded-For")
       
       allowed, retry_after = check_and_increment(
           db=db,
           user_id=user_id,
           ip_address=ip,
           action_key="login",
           window_seconds=3600,
           limit=10,
           granularity=60,
       )
       
       if not allowed:
           raise HTTPException(status_code=429, headers={"Retry-After": str(retry_after)})
   ```
4. **Check and Increment** (Line 1, `app/services/rate_limit.py:check_and_increment`):
   ```python
   now = datetime.now(timezone.utc)
   bucket = _bucket_start(now, 60)  # Round to nearest minute
   
   # MySQL: Atomic upsert
   upsert_sql = text("""
       INSERT INTO rate_limit_counters 
           (user_id, ip_address, action_key, time_bucket_start, count, granularity, created_at, updated_at)
       VALUES 
           (:user_id, :ip_address, :action_key, :bucket, 1, :granularity, NOW(), NOW())
       ON DUPLICATE KEY UPDATE 
           count = count + 1, 
           updated_at = NOW()
   """)
   db.execute(upsert_sql, {
       "user_id": user_id,
       "ip_address": ip,
       "action_key": "login",
       "bucket": bucket,
       "granularity": 60,
   })
   db.commit()
   ```
5. **Aggregate Count** (Line 50):
   ```python
   # Calculate how many buckets to sum (window_seconds / granularity)
   buckets_needed = math.ceil(3600 / 60)  # 60 buckets for 1-hour window
   min_bucket = bucket - timedelta(seconds=(buckets_needed - 1) * 60)
   
   agg_sql = text("""
       SELECT COALESCE(SUM(count), 0) 
       FROM rate_limit_counters
       WHERE action_key = :action_key
         AND ((:user_id IS NULL AND user_id IS NULL) OR user_id = :user_id)
         AND ((:ip_address IS NULL AND ip_address IS NULL) OR ip_address = :ip_address)
         AND time_bucket_start >= :min_bucket
   """)
   row = db.execute(agg_sql, {
       "action_key": "login",
       "user_id": user_id,
       "ip_address": ip,
       "min_bucket": min_bucket,
   }).fetchone()
   total = int(row[0]) if row else 0
   ```
6. **Limit Check** (Line 80):
   ```python
   if total > 10:  # Exceeded limit
       # Calculate retry_after (seconds until oldest bucket expires)
       now_ts = int(datetime.now(timezone.utc).timestamp())
       retry_after = 60 - (now_ts % 60)  # Time until next bucket
       return False, retry_after
   
   return True, 0  # Allowed
   ```
7. **Return to Endpoint** (Line 90):
   - If `allowed=True` → Continue to login logic.
   - If `allowed=False` → Raise 429 with `Retry-After` header.

**Why Sliding Window Instead of Fixed Window?**
- **Fixed Window Problem**: User makes 10 requests at 10:59:59, then 10 more at 11:00:01 → 20 requests in 2 seconds (burst).
- **Sliding Window Solution**: Aggregates count over *last N seconds* → Smooth rate enforcement.

**Example Scenario:**
```
Time: 10:37:00 - User makes 5 requests → Bucket (10:37:00) count = 5
Time: 10:37:30 - User makes 3 requests → Bucket (10:37:00) count = 8
Time: 10:38:00 - User makes 4 requests → New bucket (10:38:00) count = 4
Time: 10:38:15 - Check rate limit:
  - Aggregate buckets from 10:37:00 to 10:38:00 (2 buckets)
  - Total = 8 + 4 = 12 requests in last 2 minutes
  - Limit = 120/minute = 240 in 2 minutes → ALLOWED
```

**🔬 Data Science & Analytics Perspective:**

**Feature Engineering:**
1. **Rate Limit Utilization**:
   - `(total_count / limit) * 100` → % of quota used.
   - **Metric**: Users consistently hitting 90%+ are power users (consider higher limits).

2. **Peak Load Times**:
   - `COUNT(*) GROUP BY time_bucket_start` → Requests per time bucket.
   - **Insight**: Identify peak hours for capacity planning.

3. **User Behavior Patterns**:
   - **Bursty Users**: High variance in bucket counts (0, 0, 50, 0, 0).
   - **Steady Users**: Low variance (5, 6, 5, 4, 6).

4. **Action Popularity**:
   - `COUNT(*) GROUP BY action_key` → Which actions are used most?

**Visualizations:**
1. **Rate Limit Heatmap (2D)**:
   - X-axis: Hour of day.
   - Y-axis: `action_key`.
   - Cell color: Average `count` per bucket.
   - **Insight**: "search" peaks at 2 PM, "login" peaks at 9 AM.

2. **User Quota Usage Distribution (Histogram)**:
   - X-axis: % of limit used (0-20%, 20-40%, ..., 80-100%, >100%).
   - Y-axis: `COUNT(DISTINCT user_id)`.

3. **429 Error Timeline (Line Chart)**:
   - X-axis: Date.
   - Y-axis: `COUNT(rate_limit_exceeded)` (requires application logging).
   - **Insight**: Spike in 429s = DDoS attempt or legitimate traffic surge.

**ML Opportunities:**
1. **Adaptive Rate Limiting**:
   - Train model on `[user_reputation, past_behavior, time_of_day]` → Predict optimal limit.
   - **Use Case**: Increase limits for trusted users, decrease for suspicious accounts.

2. **Anomaly Detection (DDoS/Bot Detection)**:
   - Features: `[request_rate, time_pattern_uniformity, user_agent_diversity]`.
   - **Flags**:
     - Uniform intervals (bot-like: exactly 1 request per second).
     - High rate from single IP.
     - Missing or suspicious user agent.

3. **Traffic Prediction**:
   - Train time-series model (SARIMA) on historical `count` per bucket.
   - Predict future load → Proactive scaling.

---

### 2.1.8 MODULE 10: System Settings

#### **Table: `system_settings`**

**Column-by-Column Audit:**

| Column | Type | Constraints | Purpose | Data Science Relevance |
|--------|------|-------------|---------|------------------------|
| `setting_key` | String(255) | Primary Key | Setting identifier (e.g., "rate_limits", "ft_min_word_len") | **Configuration Key**: Unique setting name |
| `value` | JSON | Nullable | Setting value (can be object, array, string, number, boolean) | **Configuration Value**: Flexible schema |
| `created_at` | DateTime(TZ) | Server default | Setting creation timestamp | **Configuration History**: When was setting added? |
| `updated_at` | DateTime(TZ) | On update | Last modification timestamp | **Change Tracking**: When was setting last changed? |

**Index:**
- `ix_system_settings_key` on `setting_key`: Redundant (already primary key), but explicit.

**Known Settings (Validated by Pydantic):**

| Key | Type | Default | Purpose |
|-----|------|---------|---------|
| `rate_limits` | `RateLimitsModel` | `{"login": {"limit": 10, "window_seconds": 3600}, "search": {"limit": 120, "window_seconds": 60}, "submission_create": {"limit": 20, "window_seconds": 86400}}` | Rate limit configuration |
| `ft_min_word_len` | `int` | `2` | MySQL FULLTEXT minimum word length |
| `prometheus_enabled` | `bool` | `False` | Enable Prometheus metrics export |
| `sentry_dsn` | `str` | `""` | Sentry error tracking DSN |
| `audit_log_retention_days` | `int` | `365` | How long to keep audit logs |
| `backup_s3_bucket` | `str` | `""` | S3 bucket for database backups |
| `backup_retention_days` | `int` | `90` | How long to keep backups |
| `enable_elasticsearch` | `bool` | `False` | Enable Elasticsearch integration (future) |

**Pydantic Validation Schemas:**
```python
class RateLimitAction(BaseModel):
    limit: int = Field(ge=1)
    window_seconds: int = Field(ge=1)

class RateLimitsModel(BaseModel):
    login: RateLimitAction = RateLimitAction(limit=10, window_seconds=3600)
    search: RateLimitAction = RateLimitAction(limit=120, window_seconds=60)
    submission_create: RateLimitAction = RateLimitAction(limit=20, window_seconds=86400)

_VALIDATORS = {
    "rate_limits": RateLimitsModel,
    "ft_min_word_len": int,
    "prometheus_enabled": bool,
    # ... (other validators)
}
```

**Logic Flow (Getting Setting):**
1. Application needs rate limit config.
2. Calls `get_setting(db, "rate_limits")` (Line 1, `app/services/system_settings.py`).
3. **Environment Override Check** (Line 10):
   ```python
   # Check if RATE_LIMITS env var is set
   env_val = os.getenv("RATE_LIMITS")
   if env_val:
       return json.loads(env_val)  # Override database value
   ```
4. **Cache Check** (Line 20):
   ```python
   if "rate_limits" in _SETTINGS_CACHE:
       return _SETTINGS_CACHE["rate_limits"]
   ```
5. **Database Query** (Line 30):
   ```python
   row = db.query(SystemSetting).filter(SystemSetting.setting_key == "rate_limits").first()
   if row:
       _SETTINGS_CACHE["rate_limits"] = row.value
       return row.value
   return default  # Fallback to hardcoded default
   ```

**Logic Flow (Setting Setting):**
1. Admin calls `PUT /admin/system_settings/rate_limits` with:
   ```json
   {
     "value": {
       "login": {"limit": 5, "window_seconds": 3600},
       "search": {"limit": 120, "window_seconds": 60},
       "submission_create": {"limit": 20, "window_seconds": 86400}
     }
   }
   ```
2. **Authorization** (Line 1, `app/api/v1/admin_settings.py`): Require `role='admin'`.
3. **Validation** (Line 10, `app/services/system_settings.py:set_setting`):
   ```python
   if "rate_limits" in _VALIDATORS:
       validator = _VALIDATORS["rate_limits"]
       RateLimitsModel.model_validate(request_data["value"])  # Pydantic validation
   ```
4. **Upsert** (Line 30):
   ```python
   existing = db.query(SystemSetting).filter(SystemSetting.setting_key == "rate_limits").first()
   before_val = existing.value if existing else None
   
   if existing:
       existing.value = request_data["value"]
       existing.updated_at = datetime.now(timezone.utc)
   else:
       s = SystemSetting(setting_key="rate_limits", value=request_data["value"])
       db.add(s)
   ```
5. **Audit Log** (Line 50):
   ```python
   record_audit(
       db=db,
       actor_user_id=admin.id,
       action="system_setting:update",
       resource_type="system_setting",
       resource_id=None,
       before=before_val,
       after=request_data["value"],
       metadata={"ip_address": request.client.host},
   )
   ```
6. **Cache Invalidation** (Line 70):
   ```python
   _SETTINGS_CACHE["rate_limits"] = request_data["value"]
   ```
7. **Commit** (Line 80): `db.commit()`.

**Why TTL Cache (30 seconds)?**
- **Performance**: Avoid DB query on every request.
- **Freshness**: Changes propagate within 30 seconds (acceptable for system settings).
- **Simplicity**: No Redis dependency for caching.

**🔬 Data Science & Analytics Perspective:**

**Feature Engineering:**
1. **Setting Change Frequency**:
   - `COUNT(audit_logs WHERE action='system_setting:update') GROUP BY setting_key` → Which settings are changed most?

2. **Configuration Drift Detection**:
   - Compare production settings vs default values.
   - **Alert**: If `rate_limits.login.limit < 5` → Too restrictive, may lock out legitimate users.

3. **Impact Analysis**:
   - Correlate setting changes with system metrics.
   - **Example**: After increasing `search.limit` from 60 to 120 → Did search errors decrease?

**Visualizations:**
1. **Setting Change Timeline (Gantt Chart)**:
   - X-axis: Time.
   - Y-axis: `setting_key`.
   - Bars: Duration each value was active (from `updated_at` to next change).

2. **Setting Audit Dashboard**:
   - Table: `[setting_key, current_value, last_changed, changed_by, change_count]`.

**ML Opportunities:**
1. **Optimal Configuration Recommendation**:
   - Train model on `[system_settings, performance_metrics]` → Predict optimal settings.
   - **Example**: Recommend `search.limit` based on server capacity + user demand.

2. **Anomaly Detection (Configuration Tampering)**:
   - Flag unexpected setting changes (e.g., `audit_log_retention_days` changed from 365 to 1).

---

### 2.1.9 MODULE 11: Audit Logging

#### **Table: `audit_logs`**

**Column-by-Column Audit:**

| Column | Type | Constraints | Purpose | Data Science Relevance |
|--------|------|-------------|---------|------------------------|
| `id` | Integer | Primary Key | Audit event identifier | **Event ID**: Unique audit record |
| `actor_user_id` | Integer | Nullable, Indexed | FK to `users.id` (NULL for system actions) | **Actor Tracking**: Who performed action? |
| `action` | String(100) | Not Null, Indexed | Action identifier (e.g., "system_setting:update", "canonical:create:doha") | **Action Classification**: Categorize events |
| `resource_type` | String(50) | Nullable, Indexed | Resource category (e.g., "system_setting", "doha", "user") | **Resource Segmentation**: Audit by entity type |
| `resource_id` | Integer | Nullable, Indexed | FK to resource (generic, not enforced) | **Resource Linkage**: Which specific entity? |
| `audit_before` | JSON | Nullable | State before change (redacted for sensitive fields) | **Diff Analysis**: What changed? |
| `after` | JSON | Nullable | State after change (redacted) | **Diff Analysis**: New state |
| `audit_metadata` | JSON | Nullable | Context: `{"ip_address": "...", "user_agent": "...", "request_id": "..."}` | **Forensics**: Request context |
| `created_at` | DateTime(TZ) | Server default | Event timestamp | **Time-Series**: Audit timeline |

**Indexes:**
- `ix_audit_created_at`: Used in time-range queries (e.g., "show audits from last 7 days").
- `ix_audit_resourcetype_id`: Used in "show all audits for resource X".
- `ix_audit_actor`: Used in "show all actions by user Y".
- `ix_audit_action`: Used in filtering by action type.

**Sensitive Field Redaction (CRITICAL SECURITY FEATURE):**
```python
_DEFAULT_REDACT_KEYS = {
    "password", "password_hash", "refresh_token", "access_token",
    "jwt_secret", "sentry_dsn", "secret", "api_key"
}

def _redact(obj: Optional[Dict[str, Any]], redact_keys=_DEFAULT_REDACT_KEYS) -> Optional[Dict[str, Any]]:
    if not isinstance(obj, dict):
        return obj
    
    out = {}
    for k, v in obj.items():
        if k.lower() in redact_keys:
            out[k] = "[REDACTED]"
        else:
            out[k] = v  # Keep as-is (no deep recursion for performance)
    return out
```

**Why Redaction?**
- **Compliance**: Audit logs may be exported for compliance reports → Cannot contain plaintext passwords.
- **Security**: Prevents password leakage if audit logs are compromised.

**Logic Flow (Recording Audit):**
1. Admin updates system setting (see previous section).
2. Service calls `record_audit(db, actor_user_id=admin.id, action="system_setting:update", ...)` (Line 1, `app/services/audit_service.py`).
3. **Redaction** (Line 10):
   ```python
   red_before = _redact(before)  # {"rate_limits": {...}}
   red_after = _redact(after)    # {"rate_limits": {...}}
   ```
4. **Metadata Validation** (Line 20):
   ```python
   meta = metadata or {}
   if not isinstance(meta, dict):
       meta = {"value": str(meta)}  # Coerce to dict
   ```
5. **Insert Log** (Line 30):
   ```python
   audit = AuditLog(
       actor_user_id=admin.id,
       action="system_setting:update",
       resource_type="system_setting",
       resource_id=None,
       audit_before=red_before,
       after=red_after,
       audit_metadata={"ip_address": "192.168.1.1", "user_agent": "..."},
       created_at=datetime.now(timezone.utc),
   )
   db.add(audit)
   db.flush()  # Ensure ID is available
   ```
6. **No Commit** (Caller's responsibility): Audit is part of parent transaction → If parent fails, audit rolls back too.

**Why No Commit in `record_audit`?**
- **Transactional Integrity**: Audit must succeed/fail with the action it's auditing.
- **Example**: If setting update fails → Audit must not be recorded (prevents phantom audit entries).

**🔬 Data Science & Analytics Perspective:**

**Feature Engineering:**
1. **User Activity Score**:
   - `COUNT(audit_logs WHERE actor_user_id = X)` → Total actions by user.
   - **Segmentation**: Power users (>100 actions) vs Casual users (<10 actions).

2. **Action Distribution**:
   - `COUNT(*) GROUP BY action` → Most common actions.
   - **Insight**: If "system_setting:update" is 50% of audits → Focus on automation.

3. **Resource Hotspots**:
   - `COUNT(*) GROUP BY resource_type, resource_id` → Which entities are edited most?

4. **Time-to-Action**:
   - `audit_logs[N].created_at - audit_logs[N-1].created_at` → Time between consecutive actions.
   - **Insight**: Users performing actions <5 seconds apart may be using automation (good or bad).

**Visualizations:**
1. **Audit Timeline (Gantt Chart)**:
   - X-axis: Time.
   - Y-axis: `actor_user_id`.
   - Bars: Individual audit events (color-coded by `action` type).

2. **Action Frequency Heatmap (2D)**:
   - X-axis: Hour of day.
   - Y-axis: `action` type.
   - Cell color: `COUNT(audits)`.

3. **User Activity Network Graph**:
   - Nodes: Users + Resources.
   - Edges: Audit actions (user → resource).
   - Edge thickness: Action frequency.

**ML Opportunities:**
1. **Anomaly Detection (Insider Threat)**:
   - Features: `[action_frequency, action_diversity, time_of_day, resource_access_pattern]`.
   - **Flags**:
     - User accessing 100+ different resources in 1 hour (data exfiltration?).
     - Admin actions outside business hours (9 PM - 6 AM).
     - Sudden spike in delete actions.

2. **Access Pattern Clustering**:
   - Cluster users by `[actions_performed, resources_accessed]` → Discover user roles.
   - **Use Case**: Validate RBAC roles match actual behavior.

3. **Predictive Auditing**:
   - Train model to predict high-risk actions before they occur.
   - **Example**: If user accessed 50 user records in 5 minutes → Predict bulk export attempt.

---


## 2.2 API ENDPOINTS ANALYSIS

---

### 2.2.1 AUTHENTICATION & USER MANAGEMENT

#### **File: `app/api/v1/auth.py`**

**Dependencies:**
```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.db.session import get_db
from app.db.models import User, RefreshToken, OAuthAccount
from app.auth.hash import hash_password, verify_password
from app.auth.jwt import create_access_token, create_refresh_token, decode_token
from app.auth.google import exchange_code_for_tokens, fetch_google_profile
from app.core.settings import settings
from app.core.security import get_current_user
from app.services.rate_limit import rate_limit_dependency
```

**Why These Imports?**
- `EmailStr`: Pydantic email validation (RFC 5322 compliance).
- `hash_password`, `verify_password`: bcrypt wrapper (cost=12).
- `create_access_token`, `create_refresh_token`: JWT generation (HS256 algorithm).
- `exchange_code_for_tokens`: OAuth 2.0 authorization code flow (Google).
- `rate_limit_dependency`: Database-backed rate limiter (not Redis).

---

#### **Endpoint: `POST /auth/register`**

**Request Schema:**
```python
class RegisterIn(BaseModel):
    email: EmailStr  # e.g., "user@example.com"
    password: str    # Min 8 chars (enforced client-side, NOT validated here - security gap)
    username: str | None = None  # Optional display name
```

**Response Schema:**
```json
{
  "id": 42,
  "email": "user@example.com",
  "username": "john_doe"
}
```

**Logic Flow (Line-by-Line):**
1. **Line 1**: Client sends POST request with JSON body.
2. **Line 5**: FastAPI parses body into `RegisterIn` Pydantic model.
   - If email invalid → Pydantic raises 422 Unprocessable Entity.
3. **Line 10**: Query `users` table for existing email:
   ```python
   existing = db.query(User).filter(User.email == data.email).first()
   ```
4. **Line 15**: If `existing` is not None → Raise 400 "Email already registered".
5. **Line 20**: Hash password using bcrypt (cost=12):
   ```python
   password_hash = hash_password(data.password)
   # Internally: bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12))
   ```
6. **Line 25**: Create new `User` object:
   ```python
   user = User(
       email=data.email,
       username=data.username,
       password_hash=password_hash,
       role="registered",  # Default role
       permissions=0,      # No special permissions
       is_active=True,
       is_banned=False,
   )
   ```
7. **Line 35**: Insert user into database:
   ```python
   db.add(user)
   db.commit()
   db.refresh(user)  # Reload user with auto-generated ID
   ```
8. **Line 40**: Return user object (excluding password_hash):
   ```python
   return {"id": user.id, "email": user.email, "username": user.username}
   ```

**Error Ontology:**

| HTTP Code | Condition | Detail Message |
|-----------|-----------|----------------|
| 422 | Invalid email format | "value is not a valid email address" (Pydantic) |
| 400 | Email already exists | "Email already registered" |
| 500 | Database error | Generic "Internal server error" (not exposed) |

**Security Considerations:**
- **Password Strength**: NO server-side validation → Accept "123" as valid password (VULNERABILITY).
- **Username Uniqueness**: NOT enforced → Two users can have same username (DESIGN FLAW if username is used for login).
- **Email Verification**: NOT implemented → Users can register with fake emails.

**🔬 Data Science & Analytics Perspective:**

**Feature Engineering:**
1. **Registration Velocity**: `COUNT(*) GROUP BY DATE(created_at)` → Daily signups.
2. **Username Adoption Rate**: `COUNT(username IS NOT NULL) / COUNT(*)` → % of users providing username.
3. **Password Strength Distribution**:
   - Extract length from client logs (if available).
   - **Note**: Cannot extract from `password_hash` (bcrypt is one-way).

**Visualizations:**
1. **Registration Timeline (Line Chart)**:
   - X-axis: Date.
   - Y-axis: `COUNT(users)` registered.
   - Annotate: Marketing campaigns, feature launches.

**ML Opportunities:**
1. **Fraud Detection**: Flag registrations with:
   - Suspicious email patterns (e.g., "user12345@tempmail.com").
   - Rapid registration from same IP.

---

#### **Endpoint: `POST /auth/login`**

**Rate Limit:** 10 requests per hour per IP (configured in `system_settings.rate_limits.login`).

**Request Schema:**
```python
class LoginIn(BaseModel):
    email: EmailStr
    password: str
```

**Response Schema:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Logic Flow (Line-by-Line):**
1. **Line 1**: Rate limit check executes BEFORE endpoint logic:
   ```python
   @router.post("/login", dependencies=[Depends(login_rate_limit)])
   ```
   - Calls `check_and_increment(db, user_id=None, ip_address=request.client.host, action_key="login", ...)`.
   - If count > 10 in last hour → Raise 429 "Too many requests".
2. **Line 10**: Query user by email:
   ```python
   user = db.query(User).filter(User.email == data.email).first()
   ```
3. **Line 15**: Validate user exists and has password:
   ```python
   if not user or not user.password_hash:
       raise HTTPException(status_code=401, detail="Invalid credentials")
   ```
   - **Security**: Same error message for "user not found" and "wrong password" (prevents email enumeration).
4. **Line 20**: Verify password:
   ```python
   if not verify_password(data.password, user.password_hash):
       raise HTTPException(status_code=401, detail="Invalid credentials")
   ```
   - Internally: `bcrypt.checkpw(password.encode('utf-8'), hash.encode('utf-8'))`.
5. **Line 25**: Generate JWT tokens:
   ```python
   access = create_access_token(user.id)
   # Payload: {"sub": "42", "exp": <15 min from now>, "type": "access"}
   
   refresh = create_refresh_token(user.id)
   # Payload: {"sub": "42", "exp": <14 days from now>, "type": "refresh"}
   ```
6. **Line 30**: Store refresh token in database:
   ```python
   expires_at = datetime.utcnow() + timedelta(seconds=settings.JWT_REFRESH_TOKEN_EXPIRES_SECONDS)
   rt = RefreshToken(token=refresh, user_id=user.id, expires_at=expires_at)
   db.add(rt)
   ```
7. **Line 35**: Update last login timestamp:
   ```python
   user.last_login = datetime.utcnow()
   db.commit()
   ```
8. **Line 40**: Return tokens:
   ```python
   return {
       "access_token": access,
       "refresh_token": refresh,
       "token_type": "bearer"
   }
   ```

**Error Ontology:**

| HTTP Code | Condition | Detail Message | Headers |
|-----------|-----------|----------------|---------|
| 429 | Rate limit exceeded | "Too many requests" | `Retry-After: 60` |
| 401 | User not found OR wrong password | "Invalid credentials" | None |
| 401 | User banned or inactive | "User not allowed" (from `get_current_user`) | None |
| 422 | Invalid email format | "value is not a valid email address" | None |

**Security Considerations:**
- **Timing Attack**: `verify_password` is NOT constant-time → Attacker can measure response time to distinguish "user exists" from "wrong password" (VULNERABILITY).
- **Account Lockout**: NO mechanism → Attacker can brute-force passwords (mitigated by rate limiting).
- **Token Storage**: Refresh token stored in DB (good) → Can be revoked. Access token NOT stored (stateless JWT).

**🔬 Data Science & Analytics Perspective:**

**Feature Engineering:**
1. **Login Success Rate**: `COUNT(status_code=200) / COUNT(*)` per user → Detect credential stuffing.
2. **Login Time Distribution**: Histogram of `last_login.hour_of_day` → Peak usage hours.
3. **Device Diversity**: Extract `user_agent` from audit logs → Users with >5 devices may share accounts.

**Visualizations:**
1. **Login Heatmap (2D)**:
   - X-axis: Hour of day.
   - Y-axis: Day of week.
   - Cell color: `COUNT(logins)`.

**ML Opportunities:**
1. **Anomalous Login Detection**:
   - Features: `[login_time, ip_geolocation, device_fingerprint, success_rate]`.
   - **Flags**: Login from new country without travel history.

---

#### **Endpoint: `POST /auth/refresh`**

**Request Schema:**
```python
class RefreshIn(BaseModel):
    refresh_token: str
```

**Response Schema:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Logic Flow (Line-by-Line):**
1. **Line 1**: Extract refresh token from request body.
2. **Line 5**: Decode JWT:
   ```python
   try:
       payload = decode_token(token)
   except jwt.ExpiredSignatureError:
       raise HTTPException(status_code=401, detail="Invalid refresh token")
   except jwt.InvalidTokenError:
       raise HTTPException(status_code=401, detail="Invalid refresh token")
   ```
3. **Line 15**: Validate token type:
   ```python
   if payload.get("type") != "refresh":
       raise HTTPException(status_code=401, detail="Invalid token type")
   ```
4. **Line 20**: Check token exists in database (not revoked):
   ```python
   rt = db.query(RefreshToken).filter(RefreshToken.token == token).first()
   if not rt:
       raise HTTPException(status_code=401, detail="Refresh token revoked")
   ```
5. **Line 25**: Generate new access token:
   ```python
   access = create_access_token(int(payload["sub"]))
   ```
6. **Line 30**: Return new access token (refresh token is reused):
   ```python
   return {"access_token": access, "token_type": "bearer"}
   ```

**Why Reuse Refresh Token?**
- **Simplicity**: Client doesn't need to update stored refresh token.
- **Revocation**: Single refresh token can be revoked (logout).
- **Rotation**: NOT implemented → Refresh token never changes (SECURITY GAP if leaked).

**Error Ontology:**

| HTTP Code | Condition | Detail Message |
|-----------|-----------|----------------|
| 401 | Expired refresh token | "Invalid refresh token" |
| 401 | Invalid JWT signature | "Invalid refresh token" |
| 401 | Token not in database | "Refresh token revoked" |
| 401 | Wrong token type (access instead of refresh) | "Invalid token type" |

**🔬 Data Science & Analytics Perspective:**

**Feature Engineering:**
1. **Token Lifetime**: `expires_at - created_at` → Distribution of token ages.
2. **Refresh Frequency**: `COUNT(refresh_logs) / (expires_at - created_at)` → How often do users refresh?

**ML Opportunities:**
1. **Stolen Token Detection**: Flag tokens refreshed from multiple IPs in short timespan.

---

#### **Endpoint: `POST /auth/logout`**

**Request Schema:**
```python
class LogoutIn(BaseModel):
    refresh_token: str
```

**Response Schema:**
```json
{
  "ok": true
}
```

**Logic Flow (Line-by-Line):**
1. **Line 1**: Extract refresh token from request body.
2. **Line 5**: Delete token from database:
   ```python
   db.query(RefreshToken).filter(RefreshToken.token == token).delete()
   db.commit()
   ```
3. **Line 10**: Return success (even if token didn't exist → idempotent):
   ```python
   return {"ok": True}
   ```

**Why No Authentication Required?**
- **Design Choice**: Anyone with refresh token can revoke it → Prevents logout if access token expired.
- **Security Tradeoff**: Attacker with refresh token can prevent legitimate logout (minor issue).

**Error Ontology:**
- **None**: Endpoint always returns 200 (even for invalid tokens).

---

#### **Endpoint: `GET /auth/me`**

**Authentication:** Required (Bearer token).

**Response Schema:**
```json
{
  "id": 42,
  "email": "user@example.com",
  "username": "john_doe",
  "role": "registered",
  "permissions": 0,
  "permission_scopes": null
}
```

**Logic Flow (Line-by-Line):**
1. **Line 1**: Extract JWT from `Authorization: Bearer <token>` header:
   ```python
   current_user: User = Depends(get_current_user)
   ```
   - `get_current_user` (in `app/core/security.py`):
     - Line 5: Parse header.
     - Line 10: Decode JWT.
     - Line 15: Query user by `user_id` from JWT payload.
     - Line 20: Check `is_active=True` and `is_banned=False`.
2. **Line 10**: Return user object:
   ```python
   return {
       "id": current_user.id,
       "email": current_user.email,
       "username": current_user.username,
       "role": current_user.role,
       "permissions": current_user.permissions,
       "permission_scopes": current_user.permission_scopes,
   }
   ```

**Error Ontology:**

| HTTP Code | Condition | Detail Message |
|-----------|-----------|----------------|
| 401 | Missing Authorization header | "Missing credentials" |
| 401 | Invalid JWT signature | "Invalid or expired token" |
| 401 | Expired access token | "Invalid or expired token" |
| 404 | User not found in database | "User not found" |
| 403 | User banned or inactive | "User not allowed" |

---

#### **Endpoint: `GET /auth/oauth/google/callback`**

**Query Parameters:**
- `code`: OAuth authorization code (from Google).
- `state`: CSRF token (not validated in current implementation - VULNERABILITY).

**Response Schema:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 42,
    "email": "user@gmail.com"
  }
}
```

**Logic Flow (Line-by-Line):**
1. **Line 1**: Validate `code` parameter exists:
   ```python
   if not code:
       raise HTTPException(status_code=400, detail="Missing code")
   ```
2. **Line 5**: Exchange authorization code for tokens:
   ```python
   token_resp = await exchange_code_for_tokens(code)
   # POST https://oauth2.googleapis.com/token
   # Body: {"code": "...", "client_id": "...", "client_secret": "...", "redirect_uri": "...", "grant_type": "authorization_code"}
   # Returns: {"access_token": "...", "refresh_token": "...", "expires_in": 3600, "token_type": "Bearer"}
   ```
3. **Line 10**: Fetch user profile from Google:
   ```python
   profile = await fetch_google_profile(token_resp["access_token"])
   # GET https://openidconnect.googleapis.com/v1/userinfo
   # Headers: {"Authorization": "Bearer <access_token>"}
   # Returns: {"sub": "12345", "email": "user@gmail.com", "email_verified": true, "name": "John Doe", "picture": "..."}
   ```
4. **Line 15**: Extract provider user ID and email:
   ```python
   provider_user_id = profile.get("sub")
   email = profile.get("email")
   if not provider_user_id or not email:
       raise HTTPException(status_code=400, detail="Incomplete profile from provider")
   ```
5. **Line 25**: Check if OAuth account already linked:
   ```python
   oauth = db.query(OAuthAccount).filter(
       OAuthAccount.provider == "google",
       OAuthAccount.provider_user_id == provider_user_id,
   ).first()
   ```
6. **Line 30**: If linked → Load existing user:
   ```python
   if oauth:
       user = db.query(User).filter(User.id == oauth.user_id).first()
   ```
7. **Line 35**: If not linked → Check if email exists:
   ```python
   else:
       user = db.query(User).filter(User.email == email).first()
   ```
8. **Line 40**: If email doesn't exist → Create new user:
   ```python
   if not user:
       user = User(email=email, username=None, password_hash=None, role="registered")
       db.add(user)
       db.flush()  # Get user.id
   ```
9. **Line 50**: Link OAuth account to user:
   ```python
   oauth = OAuthAccount(
       provider="google",
       provider_user_id=provider_user_id,
       user_id=user.id,
       raw_profile=profile,
   )
   db.add(oauth)
   db.commit()
   ```
10. **Line 60**: Generate JWT tokens:
    ```python
    access = create_access_token(user.id)
    refresh = create_refresh_token(user.id)
    expires_at = datetime.utcnow() + timedelta(seconds=settings.JWT_REFRESH_TOKEN_EXPIRES_SECONDS)
    db.add(RefreshToken(token=refresh, user_id=user.id, expires_at=expires_at))
    db.commit()
    ```
11. **Line 70**: Return tokens + user info:
    ```python
    return {
        "access_token": access,
        "refresh_token": refresh,
        "token_type": "bearer",
        "user": {"id": user.id, "email": user.email},
    }
    ```

**Security Considerations:**
- **CSRF Protection**: `state` parameter NOT validated → Attacker can trick user into linking OAuth account (VULNERABILITY).
- **Email Takeover**: If attacker registers with victim's email BEFORE victim uses OAuth → OAuth links to attacker's account (DESIGN FLAW).

**🔬 Data Science & Analytics Perspective:**

**Feature Engineering:**
1. **OAuth Adoption Rate**: `COUNT(oauth_accounts) / COUNT(users)` → % using OAuth.
2. **Email Collision Rate**: `COUNT(users WHERE email IN (SELECT email FROM oauth_accounts))` → How often does email pre-exist?

**Visualizations:**
1. **OAuth Funnel (Sankey Diagram)**:
   - Nodes: "OAuth Start" → "Code Exchange" → "Profile Fetch" → "User Created/Linked" → "Login Success".
   - Edges: Flow count (drop-offs at each stage).

---


### 2.2.2 SUBMISSION MANAGEMENT

#### **File: `app/api/v1/submissions.py`**

**Dependencies:**
```python
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
from sqlalchemy.orm import Session
from sqlalchemy import and_, update

from app.db.session import get_db
from app.db.models import Submission, ClassicalAuthor, ClassicalWork, WorkChapter, User
from app.core.security import get_current_user
from app.core.permissions import Role, role_at_least
from app.services.rate_limit import rate_limit_dependency
```

**Why These Imports?**
- `and_`: SQLAlchemy conjunction for complex WHERE clauses.
- `update`: SQLAlchemy bulk update (not used in current implementation).
- `role_at_least`: RBAC helper (checks if user role >= required role).

---

#### **Endpoint: `POST /submissions`**

**Rate Limit:** 20 requests per 24 hours per user (configured in `system_settings.rate_limits.submission_create`).

**Authentication:** Required (Bearer token).

**Request Schema:**
```python
class SubmissionCreateIn(BaseModel):
    content_type: str = Field(..., max_length=50)  # "doha", "dictionary", "idiom", "article"
    main_text: str  # Primary content (doha text, dictionary lemma, idiom phrase, article body)
    meaning: Optional[str] = None  # Translation/explanation
    is_classical: bool = False  # Whether content belongs to classical hierarchy
    author_slug: Optional[str] = None  # For classical: references classical_authors.slug
    work_slug: Optional[str] = None  # For classical: references classical_works.slug
    chapter_slug: Optional[str] = None  # For classical: references work_chapters.slug
    number_in_chapter: Optional[int] = None  # For classical: sequential number
    external_references: Optional[Dict[str, Any]] = None  # Metadata (e.g., {"text_devanagari": "..."})
    visibility: Optional[str] = Field("private", max_length=20)  # "private", "public"
    submit_for_review: bool = False  # If True, status="pending_review"; else status="draft"
```

**Response Schema:**
```json
{
  "id": 42,
  "content_type": "doha",
  "main_text": "श्रीरामचन्द्र कृपालु भजु मन",
  "meaning": "Worship kind-hearted Shri Ramchandra",
  "is_classical": true,
  "author_slug": "tulsidas",
  "work_slug": "ramcharitmanas",
  "chapter_slug": "ayodhya-kand",
  "number_in_chapter": 23,
  "external_references": null,
  "status": "pending_review",
  "visibility": "private",
  "version": 1,
  "contributor_id": 5,
  "priority": 0
}
```

**Logic Flow (Line-by-Line):**
1. **Line 1**: Rate limit check (20 submissions per 24 hours):
   ```python
   @router.post("", dependencies=[Depends(_submission_rl)])
   ```
   - Calls `check_and_increment(db, user_id=current_user.id, action_key="submission_create", window_seconds=86400, limit=20)`.
   - If count > 20 → Raise 429 "Too many requests".

2. **Line 10**: Classical validation (if `is_classical=True`):
   ```python
   _validate_classical_reference(db, data.is_classical, data.author_slug, data.work_slug, data.chapter_slug, data.number_in_chapter)
   ```
   - **Line 15**: Check all required fields present:
     ```python
     if not (author_slug and work_slug and chapter_slug and number_in_chapter is not None):
         raise HTTPException(status_code=400, detail="For classical submissions, author_slug, work_slug, chapter_slug and number_in_chapter are required")
     ```
   - **Line 20**: Validate `author_slug` exists:
     ```python
     author = db.query(ClassicalAuthor).filter(
         ClassicalAuthor.slug == author_slug,
         ClassicalAuthor.is_deleted == False,
     ).first()
     if not author:
         raise HTTPException(status_code=400, detail="Invalid author_slug for classical submission")
     ```
   - **Line 30**: Validate `work_slug` exists under author:
     ```python
     work = db.query(ClassicalWork).filter(
         ClassicalWork.author_id == author.id,
         ClassicalWork.slug == work_slug,
         ClassicalWork.is_deleted == False,
     ).first()
     if not work:
         raise HTTPException(status_code=400, detail="Invalid work_slug for this author")
     ```
   - **Line 40**: Validate `chapter_slug` exists under work:
     ```python
     chapter = db.query(WorkChapter).filter(
         WorkChapter.work_id == work.id,
         WorkChapter.slug == chapter_slug,
         WorkChapter.is_deleted == False,
     ).first()
     if not chapter:
         raise HTTPException(status_code=400, detail="Invalid chapter_slug for this work")
     ```
   - **Line 50**: Validate `number_in_chapter > 0`:
     ```python
     if number_in_chapter <= 0:
         raise HTTPException(status_code=400, detail="number_in_chapter must be positive")
     ```

3. **Line 60**: Determine submission status:
   ```python
   status = "pending_review" if data.submit_for_review else "draft"
   ```

4. **Line 65**: Create submission object:
   ```python
   submission = Submission(
       content_type=data.content_type,
       main_text=data.main_text,
       meaning=data.meaning,
       is_classical=data.is_classical,
       author_slug=data.author_slug,
       work_slug=data.work_slug,
       chapter_slug=data.chapter_slug,
       number_in_chapter=data.number_in_chapter,
       external_references=data.external_references,
       status=status,
       visibility=data.visibility or "private",
       version=1,
       contributor_id=current_user.id,
       priority=0,
   )
   ```

5. **Line 85**: Insert into database:
   ```python
   db.add(submission)
   db.commit()
   db.refresh(submission)
   ```

6. **Line 90**: Return submission object:
   ```python
   return submission
   ```

**Error Ontology:**

| HTTP Code | Condition | Detail Message |
|-----------|-----------|----------------|
| 429 | Rate limit exceeded (>20 in 24h) | "Too many requests" |
| 401 | Missing/invalid JWT | "Missing credentials" |
| 400 | Classical submission missing slugs | "For classical submissions, author_slug, work_slug, chapter_slug and number_in_chapter are required" |
| 400 | Invalid author_slug | "Invalid author_slug for classical submission" |
| 400 | Invalid work_slug | "Invalid work_slug for this author" |
| 400 | Invalid chapter_slug | "Invalid chapter_slug for this work" |
| 400 | number_in_chapter <= 0 | "number_in_chapter must be positive" |

**Design Decisions:**
- **Why Slugs Instead of IDs?**: Slugs are user-friendly (e.g., URL `/tulsidas/ramcharitmanas`) and stable (IDs may differ across environments).
- **Why Validate Hierarchy?**: Prevents orphaned submissions referencing non-existent authors/works.
- **Why Default Visibility "private"?**: Privacy-first design → Users must explicitly make content public.

**🔬 Data Science & Analytics Perspective:**

**Feature Engineering:**
1. **Submission Velocity**: `COUNT(*) GROUP BY contributor_id, DATE(created_at)` → Submissions per user per day.
2. **Classical vs Community Ratio**: `COUNT(is_classical=True) / COUNT(*)` → Corpus composition.
3. **Immediate Review Rate**: `COUNT(status='pending_review') / COUNT(*)` → % of users submitting directly for review (vs saving drafts).

**Visualizations:**
1. **Submission Funnel (Sankey Diagram)**:
   - Nodes: "Draft Created" → "Submitted for Review" → "Approved" → "Canonical".
   - Edges: Flow count (identify drop-off points).

**ML Opportunities:**
1. **Submission Quality Prediction**:
   - Features: `[content_length, has_meaning, is_classical, contributor_history]`.
   - Target: `will_be_approved` (binary classification).
   - **Use Case**: Auto-flag low-quality submissions for contributor feedback.

---

#### **Endpoint: `GET /submissions/me`**

**Authentication:** Required (Bearer token).

**Query Parameters:**
- `status` (optional): Filter by status ("draft", "pending_review", "approved", "rejected").
- `content_type` (optional): Filter by type ("doha", "dictionary", "idiom", "article").
- `offset` (default=0): Pagination offset.
- `limit` (default=50, max=200): Page size.

**Response Schema:**
```json
[
  {
    "id": 42,
    "content_type": "doha",
    "main_text": "श्रीरामचन्द्र कृपालु भजु मन",
    "meaning": "Worship kind-hearted Shri Ramchandra",
    "status": "pending_review",
    "version": 1,
    "created_at": "2024-03-15T10:30:00Z"
  },
  {
    "id": 43,
    "content_type": "dictionary",
    "main_text": "मुख्य शब्द",
    "meaning": null,
    "status": "draft",
    "version": 1,
    "created_at": "2024-03-16T14:20:00Z"
  }
]
```

**Logic Flow (Line-by-Line):**
1. **Line 1**: Build base query (only user's own submissions):
   ```python
   q = db.query(Submission).filter(
       Submission.contributor_id == current_user.id,
       Submission.is_deleted == False,
   )
   ```

2. **Line 10**: Apply optional filters:
   ```python
   if status:
       q = q.filter(Submission.status == status)
   if content_type:
       q = q.filter(Submission.content_type == content_type)
   ```

3. **Line 20**: Apply pagination and sort:
   ```python
   subs = q.order_by(Submission.created_at.desc()).offset(offset).limit(limit).all()
   ```

4. **Line 25**: Return submissions list:
   ```python
   return subs
   ```

**Error Ontology:**

| HTTP Code | Condition | Detail Message |
|-----------|-----------|----------------|
| 401 | Missing/invalid JWT | "Missing credentials" |
| 422 | Invalid status enum | "value is not a valid enumeration member" (Pydantic) |

**🔬 Data Science & Analytics Perspective:**

**Feature Engineering:**
1. **Submission Portfolio Diversity**: `COUNT(DISTINCT content_type) per contributor_id` → Generalists vs Specialists.
2. **Draft Abandonment Rate**: `COUNT(status='draft' AND updated_at < NOW() - 30 days) / COUNT(status='draft')` → % of stale drafts.

**Visualizations:**
1. **Personal Submission Dashboard (Multi-Panel)**:
   - Panel 1: Status breakdown (pie chart).
   - Panel 2: Content type distribution (bar chart).
   - Panel 3: Submission timeline (line chart).

---

#### **Endpoint: `GET /submissions/{submission_id}`**

**Authentication:** Required (Bearer token).

**Authorization:** Owner or Admin only.

**Response Schema:**
```json
{
  "id": 42,
  "content_type": "doha",
  "main_text": "श्रीरामचन्द्र कृपालु भजु मन",
  "meaning": "Worship kind-hearted Shri Ramchandra",
  "is_classical": true,
  "author_slug": "tulsidas",
  "work_slug": "ramcharitmanas",
  "chapter_slug": "ayodhya-kand",
  "number_in_chapter": 23,
  "external_references": null,
  "status": "pending_review",
  "visibility": "private",
  "version": 1,
  "contributor_id": 5,
  "assigned_moderator_id": null,
  "priority": 0,
  "created_at": "2024-03-15T10:30:00Z",
  "updated_at": "2024-03-15T10:30:00Z"
}
```

**Logic Flow (Line-by-Line):**
1. **Line 1**: Query submission by ID:
   ```python
   sub = db.query(Submission).filter(
       Submission.id == submission_id,
       Submission.is_deleted == False
   ).first()
   ```

2. **Line 10**: Validate submission exists:
   ```python
   if not sub:
       raise HTTPException(status_code=404, detail="Submission not found")
   ```

3. **Line 15**: Authorization check:
   ```python
   _ensure_can_access_submission(current_user, sub)
   ```
   - **Line 20**: Admin bypass:
     ```python
     if role_at_least(current_user.role, Role.ADMIN):
         return  # Admins can access everything
     ```
   - **Line 25**: Owner check:
     ```python
     if sub.contributor_id == current_user.id:
         return  # Owner can access own submission
     ```
   - **Line 30**: Deny access:
     ```python
     raise HTTPException(status_code=403, detail="Not allowed to access this submission")
     ```

4. **Line 35**: Return submission:
   ```python
   return sub
   ```

**Error Ontology:**

| HTTP Code | Condition | Detail Message |
|-----------|-----------|----------------|
| 401 | Missing/invalid JWT | "Missing credentials" |
| 404 | Submission not found or deleted | "Submission not found" |
| 403 | Not owner and not admin | "Not allowed to access this submission" |

---

#### **Endpoint: `PUT /submissions/{submission_id}`**

**Authentication:** Required (Bearer token).

**Authorization:** Owner only (non-admins cannot edit others' submissions).

**Request Schema:**
```python
class SubmissionUpdateIn(BaseModel):
    main_text: Optional[str] = None  # Update primary content
    meaning: Optional[str] = None  # Update translation
    external_references: Optional[Dict[str, Any]] = None  # Update metadata
    visibility: Optional[str] = Field(None, max_length=20)  # Update access control
    submit_for_review: Optional[bool] = None  # Transition draft → pending_review
    expected_version: int  # Optimistic locking (must match current version)
```

**Response Schema:**
```json
{
  "id": 42,
  "main_text": "updated text",
  "meaning": "updated meaning",
  "version": 2,
  "status": "pending_review",
  "updated_at": "2024-03-15T11:00:00Z"
}
```

**Logic Flow (Line-by-Line):**
1. **Line 1**: Query submission:
   ```python
   sub = db.query(Submission).filter(
       Submission.id == submission_id,
       Submission.is_deleted == False
   ).first()
   ```

2. **Line 10**: Validate exists:
   ```python
   if not sub:
       raise HTTPException(status_code=404, detail="Submission not found")
   ```

3. **Line 15**: Authorization (owner only):
   ```python
   _ensure_can_access_submission(current_user, sub)
   ```

4. **Line 20**: Status validation (only "draft" or "rejected" can be edited):
   ```python
   _ensure_user_can_edit_submission(current_user, sub)
   ```
   - **Line 25**: Check status:
     ```python
     if sub.status not in ALLOWED_STATUSES_FOR_USER_EDIT:  # {"draft", "rejected"}
         raise HTTPException(status_code=400, detail=f"Cannot edit submission in status '{sub.status}'")
     ```

5. **Line 30**: Optimistic locking check:
   ```python
   if sub.version != data.expected_version:
       raise HTTPException(status_code=409, detail=f"Version conflict. Current version is {sub.version}")
   ```

6. **Line 35**: Apply updates:
   ```python
   if data.main_text is not None:
       sub.main_text = data.main_text
   if data.meaning is not None:
       sub.meaning = data.meaning
   if data.external_references is not None:
       sub.external_references = data.external_references
   if data.visibility is not None:
       sub.visibility = data.visibility
   ```

7. **Line 50**: Handle review submission:
   ```python
   if data.submit_for_review is True:
       sub.status = "pending_review"
   ```

8. **Line 55**: Increment version:
   ```python
   sub.version = sub.version + 1
   ```

9. **Line 60**: Commit changes:
   ```python
   db.commit()
   db.refresh(sub)
   ```

10. **Line 65**: Return updated submission:
    ```python
    return sub
    ```

**Optimistic Locking Explained:**
- **Problem**: Two users edit same submission concurrently → Last write wins (data loss).
- **Solution**: Client sends `expected_version` with update → Server compares with current version → If mismatch, reject with 409.
- **Example**:
  ```
  User A fetches submission (version=1)
  User B fetches submission (version=1)
  User A updates (expected_version=1) → Success, version increments to 2
  User B updates (expected_version=1) → Conflict! Current version is 2, not 1 → 409 error
  ```

**Error Ontology:**

| HTTP Code | Condition | Detail Message |
|-----------|-----------|----------------|
| 401 | Missing/invalid JWT | "Missing credentials" |
| 404 | Submission not found | "Submission not found" |
| 403 | Not owner | "Not allowed to access this submission" |
| 400 | Status not editable | "Cannot edit submission in status 'pending_review'" |
| 409 | Version conflict | "Version conflict. Current version is 2" |

**🔬 Data Science & Analytics Perspective:**

**Feature Engineering:**
1. **Edit Frequency**: `COUNT(updates) per submission_id` → Distribution of edit counts.
2. **Version Conflict Rate**: `COUNT(409 responses) / COUNT(PUT requests)` → Concurrent editing frequency.
3. **Time to First Edit**: `MIN(updated_at) - created_at` → How quickly do users revise?

**Visualizations:**
1. **Edit Timeline (Gantt Chart per Submission)**:
   - X-axis: Time.
   - Y-axis: Version number.
   - Bars: Duration each version existed.

**ML Opportunities:**
1. **Edit Prediction**: Predict if submission will be edited again based on `[edit_history, content_quality, time_since_last_edit]`.

---

#### **Endpoint: `DELETE /submissions/{submission_id}`**

**Authentication:** Required (Bearer token).

**Authorization:** Owner or Admin.

**Response Schema:**
```json
{
  "ok": true
}
```

**Logic Flow (Line-by-Line):**
1. **Line 1**: Query submission:
   ```python
   sub = db.query(Submission).filter(
       Submission.id == submission_id,
       Submission.is_deleted == False
   ).first()
   ```

2. **Line 10**: Validate exists:
   ```python
   if not sub:
       raise HTTPException(status_code=404, detail="Submission not found")
   ```

3. **Line 15**: Authorization check:
   ```python
   _ensure_can_access_submission(current_user, sub)
   ```

4. **Line 20**: Soft delete:
   ```python
   sub.is_deleted = True
   sub.status = "archived"
   db.commit()
   ```

5. **Line 25**: Return success:
   ```python
   return {"ok": True}
   ```

**Why Soft Delete?**
- **Audit Trail**: Preserve submission history for analytics.
- **Undo**: Potential future feature to restore deleted submissions.
- **Referential Integrity**: Canonical content links to `source_submission_id` → Hard delete would break foreign keys.

**Error Ontology:**

| HTTP Code | Condition | Detail Message |
|-----------|-----------|----------------|
| 401 | Missing/invalid JWT | "Missing credentials" |
| 404 | Submission not found | "Submission not found" |
| 403 | Not owner/admin | "Not allowed to access this submission" |

**🔬 Data Science & Analytics Perspective:**

**Feature Engineering:**
1. **Deletion Rate**: `COUNT(is_deleted=True) / COUNT(*)` → % of submissions deleted.
2. **Time to Deletion**: `(deletion_timestamp - created_at)` → How long before users delete?
3. **Deletion Reasons**: Requires additional metadata (not currently tracked).

**Visualizations:**
1. **Deletion Funnel**:
   - X-axis: Time since creation (0-1 day, 1-7 days, 7-30 days, 30+ days).
   - Y-axis: % deleted.

**ML Opportunities:**
1. **Deletion Prediction**: Predict if submission will be deleted based on `[content_quality, edit_frequency, status_history]`.

---


### 2.2.3 MODERATION WORKFLOWS

#### **File: `app/api/v1/moderation.py`**

**Dependencies:**
```python
import logging
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import Submission, ModerationLog, User
from app.core.security import require_role, get_current_user
from app.core.permissions import Role
from app.services.content_service import create_canonical_doha_from_submission
from app.services.batch_moderation import batch_approve_submissions, BatchValidationError
```

**Why These Imports?**
- `logging`: Track moderation actions in application logs (separate from audit logs in DB).
- `require_role`: RBAC decorator (restricts endpoints to moderators/admins).
- `create_canonical_doha_from_submission`: Service function that transforms approved submission → canonical content.
- `batch_approve_submissions`: Atomic batch approval with transaction rollback on failure.

---

#### **Endpoint: `GET /moderation/submissions`**

**Authentication:** Required (Bearer token).

**Authorization:** Moderator or Admin only.

**Query Parameters:**
- `assigned_to_me` (default=False): If true, only show submissions assigned to current user.
- `unassigned_only` (default=False): If true, only show submissions with `assigned_moderator_id=NULL`.
- `offset` (default=0): Pagination offset.
- `limit` (default=50, max=200): Page size.

**Response Schema:**
```json
[
  {
    "id": 42,
    "content_type": "doha",
    "main_text": "श्रीरामचन्द्र कृपालु भजु मन",
    "meaning": "Worship kind-hearted Shri Ramchandra",
    "status": "pending_review",
    "is_classical": true,
    "author_slug": "tulsidas",
    "work_slug": "ramcharitmanas",
    "chapter_slug": "ayodhya-kand",
    "number_in_chapter": 23,
    "contributor_id": 5,
    "assigned_moderator_id": null,
    "priority": 0,
    "version": 1
  }
]
```

**Logic Flow (Line-by-Line):**
1. **Line 1**: Authorization check (moderator or higher):
   ```python
   @router.get("/submissions", dependencies=[Depends(require_role(Role.MODERATOR))])
   ```
   - `require_role(Role.MODERATOR)` dependency:
     - Line 5: Calls `get_current_user` → Extract JWT, load user.
     - Line 10: Check `role_at_least(user.role, Role.MODERATOR)`.
     - Line 15: If false → Raise 403 "Insufficient role".

2. **Line 10**: Build base query (only pending_review submissions):
   ```python
   q = db.query(Submission).filter(
       Submission.status == "pending_review",
       Submission.is_deleted == False,
   )
   ```

3. **Line 20**: Apply assignment filter:
   ```python
   if assigned_to_me:
       q = q.filter(Submission.assigned_moderator_id == current_user.id)
   elif unassigned_only:
       q = q.filter(Submission.assigned_moderator_id.is_(None))
   ```

4. **Line 30**: Sort by priority (descending) then creation time (ascending):
   ```python
   subs = q.order_by(
       Submission.priority.desc(),
       Submission.created_at.asc()
   ).offset(offset).limit(limit).all()
   ```
   - **Priority Logic**: Higher priority (e.g., 10) appears before lower priority (e.g., 0).
   - **FIFO Within Priority**: Oldest submissions reviewed first (prevents starvation).

5. **Line 40**: Return submissions:
   ```python
   return subs
   ```

**Error Ontology:**

| HTTP Code | Condition | Detail Message |
|-----------|-----------|----------------|
| 401 | Missing/invalid JWT | "Missing credentials" |
| 403 | User role < moderator | "Insufficient role" |

**Design Decisions:**
- **Why Priority + FIFO?**: Balances urgency (high-priority items first) with fairness (no indefinite wait for low-priority).
- **Why Default to All Pending?**: Transparency → Moderators see full queue, not just assigned items.

**🔬 Data Science & Analytics Perspective:**

**Feature Engineering:**
1. **Queue Length Over Time**: `COUNT(*) WHERE status='pending_review' GROUP BY DATE(created_at)` → Track backlog growth.
2. **Assignment Rate**: `COUNT(assigned_moderator_id IS NOT NULL) / COUNT(*)` → % of assigned vs unassigned.
3. **Priority Distribution**: `COUNT(*) GROUP BY priority` → Is priority feature actually used?

**Visualizations:**
1. **Moderation Queue Dashboard (Multi-Panel)**:
   - Panel 1: Queue size timeline (line chart).
   - Panel 2: Priority distribution (pie chart).
   - Panel 3: Assignment status (stacked bar: assigned vs unassigned).

**ML Opportunities:**
1. **Priority Recommendation**:
   - Features: `[content_quality, contributor_reputation, submission_age]`.
   - Target: Optimal priority (0-10).
   - **Use Case**: Auto-assign priority to new submissions.

---

#### **Endpoint: `GET /moderation/submissions/{submission_id}`**

**Authentication:** Required (Bearer token).

**Authorization:** Moderator or Admin only.

**Response Schema:**
```json
{
  "id": 42,
  "content_type": "doha",
  "main_text": "श्रीरामचन्द्र कृपालु भजु मन",
  "meaning": "Worship kind-hearted Shri Ramchandra",
  "status": "pending_review",
  "is_classical": true,
  "author_slug": "tulsidas",
  "work_slug": "ramcharitmanas",
  "chapter_slug": "ayodhya-kand",
  "number_in_chapter": 23,
  "contributor_id": 5,
  "assigned_moderator_id": null,
  "priority": 0,
  "version": 1,
  "created_at": "2024-03-15T10:30:00Z",
  "updated_at": "2024-03-15T10:30:00Z"
}
```

**Logic Flow (Line-by-Line):**
1. **Line 1**: Authorization check (moderator or higher):
   ```python
   @router.get("/submissions/{submission_id}", dependencies=[Depends(require_role(Role.MODERATOR))])
   ```

2. **Line 10**: Query submission:
   ```python
   sub = db.query(Submission).filter(
       Submission.id == submission_id,
       Submission.is_deleted == False
   ).first()
   ```

3. **Line 20**: Validate exists:
   ```python
   if not sub:
       raise HTTPException(status_code=404, detail="Submission not found")
   ```

4. **Line 25**: Return submission:
   ```python
   return sub
   ```

**Error Ontology:**

| HTTP Code | Condition | Detail Message |
|-----------|-----------|----------------|
| 401 | Missing/invalid JWT | "Missing credentials" |
| 403 | User role < moderator | "Insufficient role" |
| 404 | Submission not found | "Submission not found" |

---

#### **Endpoint: `POST /moderation/submissions/{submission_id}/approve`**

**Authentication:** Required (Bearer token).

**Authorization:** Moderator or Admin only.

**Request Schema:**
```python
class ModerationActionIn(BaseModel):
    note: Optional[str] = None  # Moderator's reason/comment
    guideline_version: Optional[str] = None  # Applied guideline version
```

**Response Schema:**
```json
{
  "id": 42,
  "status": "approved",
  "assigned_moderator_id": 8,
  "version": 1,
  "updated_at": "2024-03-15T11:00:00Z"
}
```

**Logic Flow (Line-by-Line):**
1. **Line 1**: Authorization check:
   ```python
   @router.post("/submissions/{submission_id}/approve", dependencies=[Depends(require_role(Role.MODERATOR))])
   ```

2. **Line 10**: Query submission with row lock:
   ```python
   sub = db.query(Submission).filter(
       Submission.id == submission_id,
       Submission.is_deleted == False
   ).with_for_update().first()
   ```
   - `with_for_update()`: Acquires row-level lock (prevents concurrent modifications).

3. **Line 20**: Validate submission exists:
   ```python
   if not sub:
       raise HTTPException(status_code=404, detail="Submission not found")
   ```

4. **Line 25**: Validate can be moderated:
   ```python
   _ensure_can_moderate(sub)
   ```
   - **Line 30**: Check not deleted:
     ```python
     if sub.is_deleted:
         raise HTTPException(status_code=400, detail="Cannot moderate deleted submission")
     ```
   - **Line 35**: Check status:
     ```python
     if sub.status != "pending_review":
         raise HTTPException(status_code=400, detail=f"Can only moderate submissions in 'pending_review' status (current: {sub.status})")
     ```

5. **Line 40**: Update submission status:
   ```python
   from_status = sub.status  # "pending_review"
   sub.status = "approved"
   ```

6. **Line 45**: Assign moderator (if not already assigned):
   ```python
   if sub.assigned_moderator_id is None:
       sub.assigned_moderator_id = current_user.id
   ```

7. **Line 50**: Write moderation log:
   ```python
   _log_moderation(
       db=db,
       submission_id=sub.id,
       moderator_id=current_user.id,
       action="approve",
       from_status="pending_review",
       to_status="approved",
       guideline_version=data.guideline_version,
       note=data.note,
   )
   ```
   - Inserts row into `moderation_logs` table.

8. **Line 70**: Create canonical content:
   ```python
   logger.info("Approving submission %s (type=%s) by moderator %s", sub.id, sub.content_type, current_user.id)
   
   try:
       if sub.content_type == "doha":
           create_canonical_doha_from_submission(db=db, submission=sub, moderator=current_user)
       elif sub.content_type == "dictionary":
           from app.services.content_service import create_canonical_dictionary_from_submission
           dict_id = create_canonical_dictionary_from_submission(db=db, submission=sub, moderator_user=current_user)
       elif sub.content_type == "idiom":
           from app.services.content_service import create_canonical_idiom_from_submission
           idiom_id = create_canonical_idiom_from_submission(db=db, submission=sub, moderator_user=current_user)
       elif sub.content_type == "article":
           from app.services.content_service import create_canonical_article_from_submission
           article_id = create_canonical_article_from_submission(db=db, submission=sub, moderator_user=current_user)
       else:
           logger.warning("Unknown content_type '%s' for submission %s - no canonical content created", sub.content_type, sub.id)
   except Exception as e:
       logger.exception("Failed to create canonical content for submission %s: %s", sub.id, e)
       db.rollback()
       raise HTTPException(status_code=500, detail=f"Failed to create canonical content: {str(e)}")
   ```

9. **Line 100**: Commit transaction:
   ```python
   db.commit()
   db.refresh(sub)
   ```

10. **Line 105**: Return updated submission:
    ```python
    return sub
    ```

**Transactional Integrity (CRITICAL):**
- **Single Transaction**: Submission update + moderation log + canonical creation → All succeed or all rollback.
- **Row Lock**: `with_for_update()` prevents race condition (two moderators approving same submission).
- **Error Handling**: If canonical creation fails → Transaction rolls back → Submission remains "pending_review".

**Error Ontology:**

| HTTP Code | Condition | Detail Message |
|-----------|-----------|----------------|
| 401 | Missing/invalid JWT | "Missing credentials" |
| 403 | User role < moderator | "Insufficient role" |
| 404 | Submission not found | "Submission not found" |
| 400 | Submission deleted | "Cannot moderate deleted submission" |
| 400 | Submission not pending | "Can only moderate submissions in 'pending_review' status" |
| 500 | Canonical creation fails | "Failed to create canonical content: <error>" |

**🔬 Data Science & Analytics Perspective:**

**Feature Engineering:**
1. **Approval Rate**: `COUNT(action='approve') / COUNT(*)` per moderator → Identify lenient vs strict moderators.
2. **Time to Approval**: `(approved_log.created_at - submission.created_at)` → Median review time.
3. **Guideline Usage**: `COUNT(*) GROUP BY guideline_version` → Which guidelines are actively used?

**Visualizations:**
1. **Moderator Performance Dashboard (Per Moderator)**:
   - Panel 1: Approval vs rejection ratio (donut chart).
   - Panel 2: Average review time (bar chart vs other moderators).
   - Panel 3: Actions per day (line chart).

**ML Opportunities:**
1. **Auto-Approval Candidates**:
   - Train model on `[submission_features, moderator_decisions]` → Predict approval probability.
   - Auto-approve if probability > 95% (human review for edge cases).

---

#### **Endpoint: `POST /moderation/submissions/{submission_id}/reject`**

**Authentication:** Required (Bearer token).

**Authorization:** Moderator or Admin only.

**Request Schema:**
```python
class ModerationActionIn(BaseModel):
    note: Optional[str] = None
    guideline_version: Optional[str] = None
```

**Response Schema:**
```json
{
  "id": 42,
  "status": "rejected",
  "assigned_moderator_id": 8,
  "version": 1,
  "updated_at": "2024-03-15T11:00:00Z"
}
```

**Logic Flow (Line-by-Line):**
1. **Lines 1-40**: Same as approval endpoint (authorization, locking, validation).

2. **Line 45**: Update status to "rejected":
   ```python
   from_status = sub.status
   sub.status = "rejected"
   ```

3. **Line 50**: Assign moderator:
   ```python
   if sub.assigned_moderator_id is None:
       sub.assigned_moderator_id = current_user.id
   ```

4. **Line 55**: Write moderation log:
   ```python
   _log_moderation(
       db=db,
       submission_id=sub.id,
       moderator_id=current_user.id,
       action="reject",
       from_status=from_status,
       to_status="rejected",
       guideline_version=data.guideline_version,
       note=data.note,
   )
   ```

5. **Line 70**: Commit (no canonical creation):
   ```python
   db.commit()
   db.refresh(sub)
   ```

6. **Line 75**: Return updated submission:
   ```python
   return sub
   ```

**Why No Canonical Creation?**
- **Rejection = Content Not Ready**: Contributor must fix issues and resubmit.
- **Status Flow**: `rejected` → Contributor edits → `pending_review` → Moderator re-reviews.

**Error Ontology:**
- Same as approval endpoint.

**🔬 Data Science & Analytics Perspective:**

**Feature Engineering:**
1. **Rejection Reasons (NLP)**:
   - Extract keywords from `note` field (e.g., "typo", "duplicate", "low quality").
   - Build taxonomy of rejection reasons.

2. **Re-Approval Rate**:
   - `COUNT(submissions WHERE status='approved' AND id IN (SELECT submission_id FROM moderation_logs WHERE action='reject'))` → How many rejected submissions eventually approved?

**Visualizations:**
1. **Rejection Reason Word Cloud**:
   - Font size = frequency of keywords in rejection notes.

**ML Opportunities:**
1. **Rejection Reason Classification**:
   - Train multi-class classifier on `note` → Predict reason category (quality, duplicate, guideline violation, other).

---

#### **Endpoint: `POST /moderation/batch`**

**Authentication:** Required (Bearer token).

**Authorization:** Moderator or Admin only.

**Request Schema:**
```python
class ModerationBatchIn(BaseModel):
    action: str  # "approve" or "reject"
    submission_ids: List[int]  # IDs to process
    note: Optional[str] = None
    guideline_version: Optional[str] = None
```

**Response Schema:**
```json
{
  "ok": true,
  "action": "approve",
  "count": 5
}
```

**Logic Flow (Line-by-Line):**
1. **Line 1**: Authorization check:
   ```python
   @router.post("/batch", dependencies=[Depends(require_role(Role.MODERATOR))])
   ```

2. **Line 10**: Validate action:
   ```python
   if data.action not in {"approve", "reject"}:
       raise HTTPException(status_code=400, detail="action must be 'approve' or 'reject'")
   ```

3. **Line 15**: Validate submission_ids not empty:
   ```python
   if not data.submission_ids:
       raise HTTPException(status_code=400, detail="submission_ids cannot be empty")
   ```

4. **Line 20**: Determine target status:
   ```python
   to_status = "approved" if data.action == "approve" else "rejected"
   ```

5. **Line 25**: Query all submissions with row locks:
   ```python
   subs = db.query(Submission).filter(
       Submission.id.in_(data.submission_ids),
       Submission.is_deleted == False,
   ).with_for_update().all()
   ```

6. **Line 35**: Validate all found:
   ```python
   found_ids = {s.id for s in subs}
   missing = set(data.submission_ids) - found_ids
   if missing:
       raise HTTPException(status_code=400, detail=f"Some submissions not found: {sorted(missing)}")
   ```

7. **Line 45**: Process each submission:
   ```python
   for sub in subs:
       _ensure_can_moderate(sub)  # Validate status="pending_review"
       
       from_status = sub.status
       sub.status = to_status
       
       if sub.assigned_moderator_id is None:
           sub.assigned_moderator_id = current_user.id
       
       _log_moderation(
           db=db,
           submission_id=sub.id,
           moderator_id=current_user.id,
           action=data.action,
           from_status=from_status,
           to_status=to_status,
           guideline_version=data.guideline_version,
           note=data.note,
       )
   ```

8. **Line 70**: Commit (atomic):
   ```python
   db.commit()
   ```

9. **Line 75**: Return summary:
   ```python
   return {"ok": True, "action": data.action, "count": len(subs)}
   ```

**Atomicity (CRITICAL):**
- **Single Transaction**: All submissions updated + all logs written → All succeed or all rollback.
- **Use Case**: Moderator selects 10 submissions in UI → Clicks "Approve All" → Either all 10 approved or none (prevents partial batch).

**Error Ontology:**

| HTTP Code | Condition | Detail Message |
|-----------|-----------|----------------|
| 401 | Missing/invalid JWT | "Missing credentials" |
| 403 | User role < moderator | "Insufficient role" |
| 400 | Invalid action | "action must be 'approve' or 'reject'" |
| 400 | Empty submission_ids | "submission_ids cannot be empty" |
| 400 | Some IDs not found | "Some submissions not found: [10, 25]" |
| 400 | Any submission not pending | "Can only moderate submissions in 'pending_review' status" |

**🔬 Data Science & Analytics Perspective:**

**Feature Engineering:**
1. **Batch Size Distribution**: `COUNT(*) GROUP BY batch_size` → How many submissions do moderators process at once?
2. **Batch Approval Rate**: `COUNT(action='approve') / COUNT(*)` in batch actions → Are batch approvals more lenient?

**Visualizations:**
1. **Batch Action Timeline**:
   - X-axis: Date.
   - Y-axis: Batch size.
   - Color: Action (approve vs reject).

**ML Opportunities:**
1. **Batch Recommendation**:
   - Cluster submissions by similarity → Suggest batches of similar content for efficient review.

---

#### **Endpoint: `POST /moderation/batch_approve`**

**Authentication:** Required (Bearer token).

**Authorization:** Moderator or Admin only.

**Request Schema:**
```python
class BatchApproveIn(BaseModel):
    submission_ids: List[int]
```

**Response Schema:**
```python
class BatchApproveOut(BaseModel):
    batch_id: str  # UUID for tracking
    created: List[Dict[str, Any]]  # [{submission_id: 42, canonical_id: 100}, ...]
    skipped: List[int]  # [45, 46] (already approved, idempotent)
    errors: List[Dict[str, Any]]  # [{submission_id: 50, error: "invalid_author_slug"}, ...]
```

**Example Response:**
```json
{
  "batch_id": "a1b2c3d4-e5f6-7890-abcd-1234567890ab",
  "created": [
    {"submission_id": 42, "canonical_id": 100},
    {"submission_id": 43, "canonical_id": 101}
  ],
  "skipped": [44],
  "errors": []
}
```

**Logic Flow (Line-by-Line):**
1. **Line 1**: Authorization check:
   ```python
   @router.post("/batch_approve", dependencies=[Depends(require_role(Role.MODERATOR))])
   ```

2. **Line 10**: Generate batch ID:
   ```python
   batch_id = str(uuid.uuid4())
   ```

3. **Line 15**: Call batch approval service:
   ```python
   try:
       metadata = {"moderator_id": current_user.id}
       res = batch_approve_submissions(
           db=db,
           submission_ids=data.submission_ids,
           actor_user_id=current_user.id,
           request_metadata=metadata,
       )
   except BatchValidationError as be:
       raise HTTPException(status_code=400, detail=be.errors)
   except Exception as e:
       raise HTTPException(status_code=500, detail=str(e))
   ```

4. **Line 30**: Return result:
   ```python
   return {
       "batch_id": res.get("batch_id"),
       "created": res.get("created", []),
       "skipped": res.get("skipped", []),
       "errors": res.get("errors", []),
   }
   ```

**Batch Approval Service Deep Dive (`app/services/batch_moderation.py`):**

**Line 1**: Pre-validate all submissions:
```python
subs, pre_errors = _pre_validate_submissions(db, submission_ids)
if pre_errors:
    raise BatchValidationError(pre_errors)  # Abort early if any validation fails
```

**Line 10**: Start nested transaction (savepoint):
```python
with db.begin_nested():
    try:
        for sub in subs:
            handler = _HANDLER_MAP.get(sub.content_type)  # Get content-specific handler
            if handler is None:
                raise BatchValidationError([{"submission_id": sub.id, "error": f"no_handler_for_content_type:{sub.content_type}"}])
```

**Line 20**: Call content-specific handler:
```python
created_flag, canonical_id, handler_err = handler(db, sub, batch_id, actor_user_id, audit_base_meta)
```

**Handler Example (Doha):**
```python
def _handle_doha(db, sub, batch_id, actor_user_id, audit_metadata):
    # Check if already canonicalized (idempotency)
    existing = db.query(DohaEntry).filter(DohaEntry.source_submission_id == sub.id).first()
    if existing:
        return False, existing.id, None  # Skipped (already exists)
    
    # Resolve classical hierarchy (with auto-creation)
    author_id, work_id, chapter_id = None, None, None
    if sub.is_classical:
        author, work, chapter, _ = _resolve_classical_hierarchy_for_submission(db, sub)
        author_id, work_id, chapter_id = author.id, work.id, chapter.id
    
    # Create doha entry
    doha = DohaEntry(
        author_id=author_id,
        work_id=work_id,
        chapter_id=chapter_id,
        number_in_chapter=sub.number_in_chapter,
        main_text=sub.main_text,
        meaning=sub.meaning,
        source_submission_id=sub.id,
        # ... (other fields)
    )
    db.add(doha)
    db.flush()
    
    # Create content version snapshot (optional, doesn't fail entire batch)
    try:
        if ContentVersion is not None:
            cv = ContentVersion(content_type="doha", content_id=doha.id, version=1, ...)
            db.add(cv)
            db.flush()
    except Exception as e:
        logger.warning(f"Failed to create ContentVersion for doha {doha.id}: {e}")
    
    return True, doha.id, None  # Created successfully
```

**Line 40**: Update submission status and log:
```python
if created_flag:
    sub.status = "approved"
    db.add(sub)
    
    ml = ModerationLog(
        submission_id=sub.id,
        moderator_id=actor_user_id,
        action="batch_approve:created_canonical",
        from_status="pending_review",
        to_status="approved",
        note=f"Created canonical id {canonical_id} in batch {batch_id}",
    )
    db.add(ml)
    
    record_audit(db, actor_user_id, "batch_approve:created", ...)
    created.append({"submission_id": sub.id, "canonical_id": canonical_id})
else:
    # Skipped (idempotent duplicate)
    skipped.append(sub.id)
```

**Line 60**: Commit transaction:
```python
    except BatchValidationError as be:
        raise  # Re-raise for caller
    except Exception as e:
        raise BatchValidationError([{"error": str(e)}])

db.commit()  # Commit nested transaction (all or nothing)
```

**Idempotency (CRITICAL FEATURE):**
- **Problem**: Moderator clicks "Approve All" twice → Should not create duplicate canonical content.
- **Solution**: Handler checks if `source_submission_id` already exists → If yes, return existing ID (skipped).
- **Example**: Batch contains [42, 43, 44]. Submission 44 was already approved yesterday → Handler returns `(False, 104, None)` → Added to `skipped` list, not `created`.

**Error Ontology:**

| HTTP Code | Condition | Detail Message |
|-----------|-----------|----------------|
| 401 | Missing/invalid JWT | "Missing credentials" |
| 403 | User role < moderator | "Insufficient role" |
| 400 | Pre-validation fails | `[{submission_id: 42, error: "not_found"}, ...]` |
| 400 | Handler error | `[{submission_id: 50, error: "invalid_author_slug"}, ...]` |
| 500 | Unexpected exception | Generic error message |

**🔬 Data Science & Analytics Perspective:**

**Feature Engineering:**
1. **Batch Success Rate**: `(COUNT(created) + COUNT(skipped)) / (COUNT(created) + COUNT(skipped) + COUNT(errors))` → Batch quality metric.
2. **Idempotent Hit Rate**: `COUNT(skipped) / COUNT(submission_ids)` → How often do moderators re-approve?

**Visualizations:**
1. **Batch Outcome Breakdown (Stacked Bar per Batch)**:
   - X-axis: Batch ID.
   - Y-axis: Count.
   - Stacks: Created (green), Skipped (yellow), Errors (red).

**ML Opportunities:**
1. **Batch Failure Prediction**:
   - Features: `[batch_size, content_type_mix, avg_submission_age]`.
   - Target: Batch will have errors (binary).
   - **Use Case**: Warn moderator before submitting risky batch.

---


### 2.2.4 SEARCH & RECOMMENDATION

#### **File: `app/api/v1/search.py`**

**Dependencies:**
```python
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.search_service import search_dohas
from app.services.rate_limit import rate_limit_dependency
```

**Why These Imports?**
- `search_dohas`: Service function encapsulating MySQL FULLTEXT vs SQLite LIKE fallback logic.
- `rate_limit_dependency`: Prevents search abuse (120 requests per minute).

---

#### **Endpoint: `GET /search`**

**Rate Limit:** 120 requests per 60 seconds per user/IP.

**Query Parameters:**
- `q` (optional): Search query (text to find in doha content).
- `author` (optional): Filter by author slug (e.g., "tulsidas").
- `work` (optional): Filter by work slug (e.g., "ramcharitmanas").
- `chapter` (optional): Filter by chapter slug (e.g., "ayodhya-kand").
- `sort` (default="relevance"): Sort order ("relevance", "recent", "popular").
- `limit` (default=20, max=200): Page size.
- `offset` (default=0): Pagination offset.

**Response Schema:**
```json
{
  "total": 150,
  "results": [
    {
      "id": 42,
      "hierarchy_path": "tulsidas/ramcharitmanas/ayodhya-kand/23",
      "main_text": "श्रीरामचन्द्र कृपालु भजु मन",
      "meaning": "Worship kind-hearted Shri Ramchandra",
      "relevance_score": 4.523
    },
    {
      "id": 55,
      "hierarchy_path": "tulsidas/ramcharitmanas/baal-kand/10",
      "main_text": "राम नाम मनि दीप धरु जीह देहरीं द्वार",
      "meaning": "Keep the jewel-like lamp of Ram's name on the doorstep of your tongue",
      "relevance_score": 3.891
    }
  ]
}
```

**Logic Flow (Line-by-Line):**
1. **Line 1**: Rate limit check (120 requests per minute):
   ```python
   @router.get("/search", dependencies=[Depends(search_rate_limit)])
   ```

2. **Line 10**: Validate and normalize parameters:
   ```python
   limit = min(limit or 20, 200)  # Clamp to max 200
   if limit < 1:
       limit = 1
   ```

3. **Line 20**: Call search service:
   ```python
   res = search_dohas(
       db=db,
       q=q,
       author_slug=author,
       work_slug=work,
       chapter_slug=chapter,
       sort=sort,
       limit=limit,
       offset=offset,
   )
   ```

4. **Line 30**: Return results:
   ```python
   return res  # {"total": 150, "results": [...]}
   ```

**Search Service Deep Dive (`app/services/search_service.py`):**

**SCENARIO A: Empty Query (Recent/Popular Listing)**
```python
if not q:
    base = db.query(DohaEntry).filter(
        DohaEntry.is_deleted == False,
        DohaEntry.status == "active"
    )
    
    # Apply hierarchy filters using LEFT JOIN (not INNER JOIN)
    if author_slug:
        base = base.outerjoin(
            ClassicalAuthor,
            DohaEntry.author_id == ClassicalAuthor.id
        ).filter(
            func.lower(ClassicalAuthor.slug) == author_slug.lower()
        )
    
    # Sort logic
    if sort == "popular":
        base = base.outerjoin(
            EngagementKPI,
            (EngagementKPI.content_id == DohaEntry.id) &
            (EngagementKPI.content_type == "doha")
        ).order_by(EngagementKPI.weight_score.desc())
    elif sort == "recent":
        base = base.order_by(DohaEntry.created_at.desc())
    
    total = base.count()
    rows = base.offset(offset).limit(limit).all()
    
    results = [{"id": r.id, "hierarchy_path": r.hierarchy_path, ...} for r in rows]
    _record_hits_safe(db, results)  # Track search hits
    return {"total": total, "results": results}
```

**Why OUTERJOIN Instead of JOIN?**
- **Problem**: `DohaEntry.author_id` can be NULL (non-classical content).
- **INNER JOIN**: Would exclude non-classical dohas from results.
- **LEFT JOIN (OUTERJOIN)**: Includes all dohas; filter only applies when author_id is not NULL.

**SCENARIO B: Query Present → MySQL FULLTEXT**
```python
if dialect == "mysql":
    # Build WHERE clause for filters
    where_clause = ""
    params = {}
    
    if author_slug:
        where_clause += " AND LOWER(ca.slug) = :author_slug"
        params["author_slug"] = author_slug.lower()
    
    # MySQL FULLTEXT query
    sql = f"""
    SELECT
        doha_entries.id,
        doha_entries.hierarchy_path,
        doha_entries.main_text,
        doha_entries.meaning,
        MATCH(doha_entries.main_text, doha_entries.meaning, doha_entries.text_devanagari, doha_entries.text_romanized)
            AGAINST (:q IN NATURAL LANGUAGE MODE) AS relevance
    FROM doha_entries
    LEFT JOIN classical_authors ca ON doha_entries.author_id = ca.id
    LEFT JOIN classical_works cw ON doha_entries.work_id = cw.id
    LEFT JOIN work_chapters wc ON doha_entries.chapter_id = wc.id
    WHERE doha_entries.is_deleted = 0 AND doha_entries.status = 'active'
    {where_clause}
    HAVING relevance > 0
    ORDER BY {order_clause}
    LIMIT :limit OFFSET :offset
    """
    
    params_exec = {"q": q, "limit": limit, "offset": offset, **params}
    rows = db.execute(text(sql), params_exec).fetchall()
    
    # Count query (separate)
    count_sql = f"""
    SELECT COUNT(*) as total FROM (
        SELECT doha_entries.id FROM doha_entries
        LEFT JOIN classical_authors ca ON doha_entries.author_id = ca.id
        WHERE doha_entries.is_deleted = 0 AND doha_entries.status = 'active' {where_clause}
        AND MATCH(...) AGAINST (:q IN NATURAL LANGUAGE MODE)
    ) t
    """
    total_row = db.execute(text(count_sql), params_exec).fetchone()
    total = int(total_row[0])
    
    results = [
        {
            "id": r.id,
            "hierarchy_path": r.hierarchy_path,
            "main_text": r.main_text,
            "meaning": r.meaning,
            "relevance_score": float(r.relevance)
        }
        for r in rows
    ]
```

**MySQL FULLTEXT Explained:**
- **MATCH AGAINST**: Full-text search operator (requires FULLTEXT index on columns).
- **IN NATURAL LANGUAGE MODE**: Default mode (uses TF-IDF-like scoring).
- **Relevance Score**: Computed by MySQL based on term frequency and document length.
- **HAVING relevance > 0**: Filters out documents with zero relevance (no matching terms).

**Order Clause Logic:**
```python
if sort == "popular":
    order_clause = "COALESCE(ek.weight_score, 0) DESC, relevance DESC"
    # Primary sort: Engagement score (popular first)
    # Secondary sort: Relevance (within same engagement tier)
elif sort == "recent":
    order_clause = "doha_entries.created_at DESC"
else:  # sort == "relevance"
    order_clause = "relevance DESC"
```

**SCENARIO C: Query Present → SQLite Fallback (Tests)**
```python
else:  # SQLite
    q_like = f"%{q}%"
    base = db.query(DohaEntry).filter(
        DohaEntry.is_deleted == False,
        DohaEntry.status == "active"
    )
    
    # Apply filters
    if author_slug:
        base = base.outerjoin(ClassicalAuthor, ...).filter(...)
    
    # Text search using LIKE
    base = base.filter(
        or_(
            func.lower(DohaEntry.main_text).like(q_like.lower()),
            func.lower(DohaEntry.meaning).like(q_like.lower()),
            func.lower(DohaEntry.text_devanagari).like(q_like.lower()),
            func.lower(DohaEntry.text_romanized).like(q_like.lower()),
        )
    )
    
    # Sort
    if sort == "popular":
        base = base.outerjoin(EngagementKPI, ...).order_by(EngagementKPI.weight_score.desc())
    elif sort == "recent":
        base = base.order_by(DohaEntry.created_at.desc())
    else:
        base = base.order_by(DohaEntry.id.desc())  # No relevance scoring in SQLite
    
    total = base.count()
    rows = base.offset(offset).limit(limit).all()
    
    results = [{"id": r.id, ..., "relevance_score": 1.0} for r in rows]  # Fake relevance
```

**Why Fallback to LIKE?**
- **SQLite Limitation**: No native FULLTEXT support in standard SQLite (FTS5 extension exists but not enabled in test environment).
- **Performance**: LIKE with `%query%` is O(n) → Slow for large datasets (acceptable for tests).

**Engagement Tracking:**
```python
def _record_hits_safe(db: Session, results: List[Dict[str, Any]]):
    if not results:
        return
    
    try:
        result_ids = [int(r["id"]) for r in results if r.get("id") is not None]
        if not result_ids:
            return
        
        # Bulk increment search_hits_count
        record_search_hits(db, "doha", result_ids, increment=1)
    except Exception:
        logger.exception("Failed to record search hits")
        # Do not fail search request if engagement tracking fails
```

**Error Ontology:**

| HTTP Code | Condition | Detail Message |
|-----------|-----------|----------------|
| 429 | Rate limit exceeded (>120 per minute) | "Too many requests" |
| 422 | Invalid query parameter type | "value is not a valid integer" (Pydantic) |

**Design Decisions:**
- **Why Track Top Results Only?**: Recording search hits for all results would be expensive → Only track returned results (top N).
- **Why Separate Count Query?**: MySQL FULLTEXT with LIMIT doesn't return total → Need separate `SELECT COUNT(*)`.
- **Why COALESCE in Popular Sort?**: Some dohas may not have `engagement_kpis` row yet → `COALESCE(weight_score, 0)` prevents NULL sort issues.

**🔬 Data Science & Analytics Perspective:**

**Feature Engineering:**
1. **Search Query Analysis**:
   - Extract query terms → Build term frequency distribution.
   - **Insight**: Most searched terms (e.g., "राम", "सीता", "कृष्ण").

2. **Zero-Result Queries**:
   - `COUNT(*) WHERE total = 0` → % of searches with no results.
   - **Action**: Build "did you mean?" suggestions.

3. **Click-Through Rate (CTR)**:
   - Requires additional logging: `clicks_on_results / search_impressions`.
   - **Metric**: Low CTR = poor result quality or misleading snippets.

4. **Filter Usage**:
   - `COUNT(*) WHERE author IS NOT NULL` → % of searches using filters.
   - **Insight**: If <5% use filters → Consider redesigning filter UI.

**Visualizations:**
1. **Search Query Word Cloud**:
   - Font size: Query frequency.
   - Color: Average result count (red = many results, blue = few results).

2. **Search Volume Timeline (Line Chart)**:
   - X-axis: Hour of day.
   - Y-axis: `COUNT(searches)`.
   - Annotation: Peak hours for content recommendation optimization.

3. **Result Count Distribution (Histogram)**:
   - X-axis: Result count bins (0, 1-10, 11-50, 51-100, 100+).
   - Y-axis: `COUNT(searches)`.

**ML Opportunities:**
1. **Query Expansion**:
   - Train Word2Vec on doha corpus → Find synonyms for query terms.
   - **Example**: Query "राम" → Expand to "राम OR रामचन्द्र OR रामजी".

2. **Learning to Rank (LTR)**:
   - Features: `[relevance_score, weight_score, recency, author_popularity]`.
   - Target: User clicks (requires click tracking).
   - Model: LambdaMART or XGBoost.
   - **Use Case**: Re-rank MySQL FULLTEXT results using engagement signals.

3. **Query Intent Classification**:
   - Classify queries into: Navigational (looking for specific doha), Informational (exploring topic), Transactional (want to submit content).
   - **Use Case**: Different result layouts per intent.

4. **Query Spell Correction**:
   - Train character-level language model on doha text.
   - Detect misspellings: "रामचन्दर" → "रामचन्द्र".

---

#### **File: `app/api/v1/recommendations.py`**

**Dependencies:**
```python
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.recommendation_service import get_recommendations
```

---

#### **Endpoint: `GET /recommendations/{content_type}/{content_id}`**

**Query Parameters:**
- `limit` (default=5, max=50): Number of recommendations.

**Response Schema:**
```json
{
  "source": {
    "type": "doha",
    "id": 42
  },
  "results": [
    {
      "content_type": "dictionary",
      "id": 10,
      "title_or_text": "कृपालु",
      "score": 3.245
    },
    {
      "content_type": "dictionary",
      "id": 15,
      "title_or_text": "भजु",
      "score": 2.891
    }
  ]
}
```

**Logic Flow (Line-by-Line):**
1. **Line 1**: Call recommendation service:
   ```python
   return {
       "source": {"type": content_type, "id": content_id},
       "results": get_recommendations(
           db=db,
           content_type=content_type,
           content_id=content_id,
           limit=limit,
       ),
   }
   ```

**Recommendation Service Deep Dive (`app/services/recommendation_service.py`):**

**Configuration (Stored in `system_settings`):**
```json
{
  "recommendation_weights": {
    "views": 1.0,
    "likes": 2.0,
    "search_hits": 0.5
  }
}
```

**Scoring Function:**
```python
def _score(kpi: EngagementKPI | None, w: Dict[str, float]) -> float:
    if not kpi:
        return 0.0
    
    return (
        (kpi.views_count * w["views"])
        + (kpi.likes_count * w["likes"])
        + (kpi.search_hits_count * w["search_hits"])
    )
```

**Token Extraction (STRICT):**
```python
def _extract_tokens(norm_text: str | None) -> List[str]:
    if not norm_text:
        return []
    
    # Split on whitespace, filter short tokens
    return [t for t in norm_text.split(" ") if len(t) > 2]
```

**Recommendation Logic:**
```python
def get_recommendations(db, content_type, content_id, limit):
    limit = min(limit or 5, 50)
    weights = _get_weights(db)  # From system_settings
    
    # 1. Fetch source content
    source = None
    tokens = []
    
    if content_type == "dictionary":
        source = db.query(DictionaryEntry).filter(
            DictionaryEntry.id == content_id,
            DictionaryEntry.visibility == "public",
        ).first()
        tokens = _extract_tokens(source.lemma_roman_norm if source else None)
    
    elif content_type == "idiom":
        source = db.query(IdiomEntry).filter(
            IdiomEntry.id == content_id,
            IdiomEntry.visibility == "public",
        ).first()
        tokens = _extract_tokens(source.text_roman_norm if source else None)
    
    # ... (similar for article, doha)
    
    if not source or not tokens:
        return []  # No recommendations if source invalid or no tokens
    
    # 2. Retrieve candidates (token-based matching)
    candidates = []
    
    if content_type == "doha":
        # Doha → Dictionary (core linguistic link)
        q = db.query(DictionaryEntry).filter(
            DictionaryEntry.visibility == "public",
            DictionaryEntry.id != content_id,
            or_(*[DictionaryEntry.lemma_roman_norm.like(f"%{t}%") for t in tokens]),
        ).limit(50)  # DB_CANDIDATE_CAP
        candidates = [("dictionary", x) for x in q]
    
    elif content_type == "dictionary":
        # Dictionary → Dictionary (same-type semantic matching)
        q = db.query(DictionaryEntry).filter(
            DictionaryEntry.visibility == "public",
            DictionaryEntry.id != content_id,
            or_(*[DictionaryEntry.lemma_roman_norm.like(f"%{t}%") for t in tokens]),
        ).limit(50)
        candidates = [("dictionary", x) for x in q]
    
    # ... (similar for idiom, article)
    
    if not candidates:
        return []
    
    # 3. Score and rank candidates
    results = []
    
    for ctype, ent in candidates:
        kpi = db.query(EngagementKPI).filter(
            EngagementKPI.content_type == ctype,
            EngagementKPI.content_id == ent.id,
        ).first()
        
        preview_text = (
            ent.lemma_devanagari if ctype == "dictionary"
            else ent.text_devanagari if ctype == "idiom"
            else ent.title if ctype == "article"
            else ent.main_text[:120]
        )
        
        results.append({
            "content_type": ctype,
            "id": ent.id,
            "title_or_text": preview_text,
            "score": _score(kpi, weights),
        })
    
    # 4. Sort by score (descending)
    results.sort(key=lambda x: x["score"], reverse=True)
    
    return results[:limit]
```

**Design Decisions:**
- **Why Token-Based Instead of ML?**: Lightweight, interpretable, no training required → Good baseline.
- **Why Doha → Dictionary Link?**: Linguistic relationship (doha contains words, dictionary defines words).
- **Why Engagement Weighting?**: Popular content is more likely to be relevant (quality signal).
- **Why DB_CANDIDATE_CAP=50?**: Balance between recall (find relevant items) and performance (don't query thousands of rows).

**Error Ontology:**
- **None**: Endpoint always returns 200 (empty list if no recommendations).

**🔬 Data Science & Analytics Perspective:**

**Feature Engineering:**
1. **Recommendation Click-Through Rate (CTR)**:
   - Requires tracking: Did user click recommended item?
   - **Metric**: `clicks / impressions` per recommendation.

2. **Recommendation Diversity**:
   - `COUNT(DISTINCT content_type) / COUNT(*)` → Are recommendations diverse or all one type?

3. **Coverage**:
   - `COUNT(DISTINCT content_id IN recommendations) / COUNT(DISTINCT content_id)` → % of corpus appearing in recommendations.

**Visualizations:**
1. **Recommendation Flow (Sankey Diagram)**:
   - Nodes: Source content types (left) → Recommended content types (right).
   - Edges: Recommendation frequency.

2. **Recommendation Score Distribution (Histogram)**:
   - X-axis: Score bins.
   - Y-axis: `COUNT(recommendations)`.

**ML Opportunities:**
1. **Collaborative Filtering (User-Based)**:
   - Build user-item interaction matrix (views, likes, bookmarks).
   - Use Alternating Least Squares (ALS) to learn latent factors.
   - **Recommendation**: "Users similar to you also viewed X".

2. **Content-Based Filtering (Item-Item Similarity)**:
   - Compute TF-IDF vectors for all content.
   - Calculate cosine similarity → Recommend top K similar items.
   - **Advantage**: Works for new users (cold start).

3. **Hybrid Approach (Facebook-Style)**:
   - Combine collaborative filtering + content-based + engagement signals.
   - Train neural network to predict user rating for item.

4. **Word Embeddings (Word2Vec/FastText)**:
   - Train embeddings on doha corpus.
   - Recommend content with high semantic similarity (cosine similarity in embedding space).

---


### 2.2.5 ANALYTICS & REPORTING

#### **File: `app/api/v1/analytics.py`**

**Dependencies:**
```python
from datetime import datetime, timedelta
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from app.db.session import get_db
from app.core.security import require_role
from app.core.permissions import Role
from app.services.analytics_service import (
    get_top_content,
    get_growth_trends,
    get_demand_distribution,
)
```

**Why These Imports?**
- `get_top_content`: Aggregates engagement KPIs with logarithmic scoring.
- `get_growth_trends`: Time-series analysis of content/user growth.
- `get_demand_distribution`: Search demand breakdown by content type.

---

#### **Endpoint: `GET /analytics/top`**

**Authentication:** Required (Bearer token).

**Authorization:** Admin only.

**Query Parameters:**
- `content_type` (optional): Filter by type ("doha", "dictionary", "idiom", "article").
- `limit` (default=20, max=100): Number of top items.
- `start_date` (optional): ISO format UTC (default: 30 days ago).
- `end_date` (optional): ISO format UTC (default: now).

**Response Schema:**
```python
class TopContentItem(BaseModel):
    content_type: str
    content_id: int
    title_or_text: str  # Preview text (first 100 chars or title)
    score: float  # Computed engagement score
    views: int
    likes: int
    search_hits: int
```

**Example Response:**
```json
[
  {
    "content_type": "doha",
    "content_id": 42,
    "title_or_text": "श्रीरामचन्द्र कृपालु भजु मन",
    "score": 5.234,
    "views": 1250,
    "likes": 85,
    "search_hits": 320
  },
  {
    "content_type": "dictionary",
    "content_id": 10,
    "title_or_text": "कृपालु",
    "score": 4.891,
    "views": 980,
    "likes": 62,
    "search_hits": 240
  }
]
```

**Logic Flow (Line-by-Line):**
1. **Line 1**: Authorization check (admin only):
   ```python
   @router.get("/top", dependencies=[Depends(require_role(Role.ADMIN))])
   ```

2. **Line 10**: Parse date range:
   ```python
   def _date_range(start: str | None, end: str | None):
       if end:
           end_dt = datetime.fromisoformat(end.strip())
       else:
           end_dt = datetime.utcnow()
       
       if start:
           start_dt = datetime.fromisoformat(start.strip())
       else:
           start_dt = end_dt - timedelta(days=30)
       
       # Ensure naive datetimes (remove tzinfo)
       if start_dt.tzinfo is not None:
           start_dt = start_dt.replace(tzinfo=None)
       if end_dt.tzinfo is not None:
           end_dt = end_dt.replace(tzinfo=None)
       
       return start_dt, end_dt
   ```

3. **Line 30**: Call analytics service:
   ```python
   start, end = _date_range(start_date, end_date)
   return get_top_content(db, content_type, limit, start, end)
   ```

**Analytics Service Deep Dive (`app/services/analytics_service.py`):**

**Scoring Algorithm:**
```python
def _log_score(v: int, s: int, l: int) -> float:
    """
    Logarithmic engagement score:
    score = 1*log(views+1) + 2*log(search_hits+1) + 5*log(likes+1)
    
    Why logarithmic?
    - Diminishing returns: 1000→2000 views is less impactful than 10→20 views.
    - Balanced: Prevents single viral piece from dominating.
    
    Why these weights?
    - Likes (5x): Strongest quality signal (users explicitly approve).
    - Search Hits (2x): Medium signal (content is discoverable).
    - Views (1x): Weakest signal (may include accidental clicks).
    """
    return (
        1.0 * math.log(v + 1)
        + 2.0 * math.log(s + 1)
        + 5.0 * math.log(l + 1)
    )
```

**Top Content Query:**
```python
def get_top_content(db, content_type, limit, start_date, end_date):
    # Ensure naive datetimes for MySQL compatibility
    if start_date.tzinfo is not None:
        start_date = start_date.replace(tzinfo=None)
    if end_date.tzinfo is not None:
        end_date = end_date.replace(tzinfo=None)
    
    # 1. Query engagement KPIs in date range
    q = db.query(
        EngagementKPI.content_type,
        EngagementKPI.content_id,
        EngagementKPI.views_count,
        EngagementKPI.search_hits_count,
        EngagementKPI.likes_count,
    ).filter(
        EngagementKPI.updated_at >= start_date,
        EngagementKPI.updated_at <= end_date,
    )
    
    if content_type:
        q = q.filter(EngagementKPI.content_type == content_type)
    
    raw = q.all()
    
    # 2. Compute scores
    scored = []
    for r in raw:
        score_val = _log_score(r.views_count, r.search_hits_count, r.likes_count)
        scored.append({
            "content_type": r.content_type,
            "content_id": r.content_id,
            "views": r.views_count,
            "likes": r.likes_count,
            "search_hits": r.search_hits_count,
            "score": round(score_val, 4)
        })
    
    # 3. Sort by score (descending)
    top = sorted(scored, key=lambda x: x["score"], reverse=True)[:limit]
    
    # 4. Fetch preview metadata (batch queries)
    by_type = {}
    for r in top:
        by_type.setdefault(r["content_type"], []).append(r["content_id"])
    
    previews = {}
    
    if "doha" in by_type:
        rows = db.query(DohaEntry.id, DohaEntry.main_text).filter(
            DohaEntry.id.in_(by_type["doha"]),
            DohaEntry.is_deleted == False,
            DohaEntry.visibility == "public",
        ).all()
        previews.update({r.id: r.main_text[:100] if r.main_text else "[no text]" for r in rows})
    
    if "dictionary" in by_type:
        rows = db.query(DictionaryEntry.id, DictionaryEntry.lemma_devanagari).filter(
            DictionaryEntry.id.in_(by_type["dictionary"]),
            DictionaryEntry.visibility == "public",
        ).all()
        previews.update({r.id: r.lemma_devanagari or "[no lemma]" for r in rows})
    
    # ... (similar for idiom, article)
    
    # 5. Attach preview text
    for r in top:
        r["title_or_text"] = previews.get(r["content_id"], "[deleted or private]")
    
    return top
```

**Why Batch Preview Fetching?**
- **Performance**: Single query per content type (e.g., `WHERE id IN (10, 25, 42)`) → O(N) instead of N separate queries → O(N²).
- **N+1 Problem Avoidance**: Classic ORM anti-pattern.

**Error Ontology:**

| HTTP Code | Condition | Detail Message |
|-----------|-----------|----------------|
| 401 | Missing/invalid JWT | "Missing credentials" |
| 403 | User role < admin | "Insufficient role" |
| 422 | Invalid date format | "invalid datetime format" (Pydantic) |

**🔬 Data Science & Analytics Perspective:**

**Feature Engineering:**
1. **Content Velocity**:
   - `score / (NOW() - created_at in days)` → Score per day (fast-growing vs evergreen content).

2. **Engagement Mix**:
   - `(likes / views) * 100` → Like rate (%).
   - **High like rate**: Quality content (users approve).
   - **Low like rate**: Clickbait or low quality.

3. **Score Volatility**:
   - Track score over time → Standard deviation → Stable vs volatile content.

**Visualizations:**
1. **Top Content Leaderboard (Sortable Table)**:
   - Columns: Rank, Title, Type, Score, Views, Likes, Search Hits.
   - Sortable by any column.

2. **Score Decomposition (Stacked Bar per Item)**:
   - X-axis: Content ID.
   - Y-axis: Score.
   - Stacks: View contribution (1x log), Search contribution (2x log), Like contribution (5x log).

**ML Opportunities:**
1. **Viral Content Prediction**:
   - Features: `[score_day_1, score_day_7, content_features]`.
   - Target: Will reach top 10 in 30 days (binary).
   - Model: Logistic Regression or LightGBM.

---

#### **Endpoint: `GET /analytics/growth`**

**Authentication:** Required (Bearer token).

**Authorization:** Admin only.

**Query Parameters:**
- `start_date` (optional): ISO format UTC (default: 30 days ago).
- `end_date` (optional): ISO format UTC (default: now).

**Response Schema:**
```python
class GrowthSeries(BaseModel):
    dates: List[str]  # ["2024-03-01", "2024-03-02", ...]
    series: Dict[str, List[int]]  # {"doha": [5, 8, 12], "users": [2, 3, 3], ...}
```

**Example Response:**
```json
{
  "dates": ["2024-03-01", "2024-03-02", "2024-03-03"],
  "series": {
    "doha": [5, 8, 12],
    "dictionary": [2, 3, 5],
    "idiom": [1, 1, 2],
    "article": [0, 1, 1],
    "users": [10, 12, 15]
  }
}
```

**Logic Flow (Line-by-Line):**
1. **Line 1**: Authorization check:
   ```python
   @router.get("/growth", dependencies=[Depends(require_role(Role.ADMIN))])
   ```

2. **Line 10**: Parse date range:
   ```python
   start, end = _date_range(start_date, end_date)
   ```

3. **Line 15**: Call analytics service:
   ```python
   return get_growth_trends(db, start, end)
   ```

**Analytics Service Deep Dive:**

**Growth Trends Query:**
```python
def get_growth_trends(db, start_date, end_date):
    # Ensure naive datetimes
    if start_date.tzinfo is not None:
        start_date = start_date.replace(tzinfo=None)
    if end_date.tzinfo is not None:
        end_date = end_date.replace(tzinfo=None)
    
    # 1. Generate date list
    dates = []
    cursor = start_date
    while cursor <= end_date:
        dates.append(cursor.date().isoformat())
        cursor += timedelta(days=1)
    
    series = {}
    
    # 2. Content growth (per content type)
    for ctype, model in CONTENT_TABLES.items():  # {"doha": DohaEntry, ...}
        q = db.query(
            func.date(model.created_at).label("day"),
            func.count(model.id),
        ).filter(
            model.created_at >= start_date,
            model.created_at <= end_date,
        )
        
        # Apply soft-delete filter if column exists
        if hasattr(model, "is_deleted"):
            q = q.filter(model.is_deleted == False)
        
        q = q.group_by("day")
        
        counts = {str(r[0]): r[1] for r in q.all()}
        series[ctype] = [counts.get(d, 0) for d in dates]
    
    # 3. User registrations
    uq = db.query(
        func.date(User.created_at).label("day"),
        func.count(User.id),
    ).filter(
        User.created_at >= start_date,
        User.created_at <= end_date,
    ).group_by("day")
    
    user_counts = {str(r[0]): r[1] for r in uq.all()}
    series["users"] = [user_counts.get(d, 0) for d in dates]
    
    return {
        "dates": dates,
        "series": series,
    }
```

**Why Date List Generation?**
- **Problem**: SQL `GROUP BY date` only returns dates with data → Gaps in timeline.
- **Solution**: Pre-generate all dates in range → Fill missing dates with 0.
- **Example**:
  ```
  SQL returns: {"2024-03-01": 5, "2024-03-03": 8}  # No data for 2024-03-02
  After filling: {"2024-03-01": 5, "2024-03-02": 0, "2024-03-03": 8}
  ```

**Error Ontology:**

| HTTP Code | Condition | Detail Message |
|-----------|-----------|----------------|
| 401 | Missing/invalid JWT | "Missing credentials" |
| 403 | User role < admin | "Insufficient role" |

**🔬 Data Science & Analytics Perspective:**

**Feature Engineering:**
1. **Growth Rate**:
   - `(series[day_N] - series[day_N-1]) / series[day_N-1]` → Daily % change.

2. **7-Day Moving Average**:
   - Smooth noisy daily data → Trend line.

3. **Cumulative Growth**:
   - `sum(series[0:N])` → Total content added over time.

**Visualizations:**
1. **Multi-Line Chart (Growth Over Time)**:
   - X-axis: Date.
   - Y-axis: Count.
   - Lines: One per content type + users.

2. **Stacked Area Chart (Corpus Composition)**:
   - X-axis: Date.
   - Y-axis: Cumulative count.
   - Stacks: Content types.
   - **Insight**: Visualize corpus balance (e.g., 80% dohas, 10% dictionary, 5% idioms).

**ML Opportunities:**
1. **Growth Forecasting (SARIMA)**:
   - Train seasonal ARIMA on historical series.
   - Predict next 30 days → Capacity planning.

2. **Anomaly Detection**:
   - Flag days with unusual growth (e.g., 10x normal rate) → Marketing campaign or bot attack.

---

#### **Endpoint: `GET /analytics/demand`**

**Authentication:** Required (Bearer token).

**Authorization:** Admin only.

**Response Schema:**
```python
class DemandItem(BaseModel):
    count: int
    percent: float

# Response: Dict[str, DemandItem]
```

**Example Response:**
```json
{
  "doha": {
    "count": 12500,
    "percent": 62.5
  },
  "dictionary": {
    "count": 5000,
    "percent": 25.0
  },
  "idiom": {
    "count": 1500,
    "percent": 7.5
  },
  "article": {
    "count": 1000,
    "percent": 5.0
  }
}
```

**Logic Flow (Line-by-Line):**
1. **Line 1**: Authorization check:
   ```python
   @router.get("/demand", dependencies=[Depends(require_role(Role.ADMIN))])
   ```

2. **Line 10**: Call analytics service:
   ```python
   return get_demand_distribution(db)
   ```

**Analytics Service Deep Dive:**

**Demand Distribution Query:**
```python
def get_demand_distribution(db):
    # 1. Aggregate search hits by content type
    q = db.query(
        EngagementKPI.content_type,
        func.sum(EngagementKPI.search_hits_count),
    ).group_by(EngagementKPI.content_type)
    
    rows = q.all()
    total = sum(r[1] or 0 for r in rows)
    
    # 2. Calculate percentages
    out = {}
    for ctype, count in rows:
        pct = (count / total * 100) if total > 0 else 0
        out[ctype] = {
            "count": int(count or 0),
            "percent": round(pct, 2),
        }
    
    return out
```

**Why Search Hits Instead of Views?**
- **Search Hits**: Proxy for user demand (what are users actively looking for?).
- **Views**: Includes direct navigation (may not reflect true interest).

**Error Ontology:**

| HTTP Code | Condition | Detail Message |
|-----------|-----------|----------------|
| 401 | Missing/invalid JWT | "Missing credentials" |
| 403 | User role < admin | "Insufficient role" |

**🔬 Data Science & Analytics Perspective:**

**Feature Engineering:**
1. **Demand Gap Analysis**:
   - Compare supply (content count) vs demand (search hits).
   - **Example**: Idioms = 5% of content but 15% of search hits → Under-supplied.

2. **Demand Trend**:
   - Track demand distribution over time → Shifting user interests.

**Visualizations:**
1. **Demand Pie Chart**:
   - Slices: Content types.
   - Size: % of total search hits.

2. **Supply vs Demand Comparison (Grouped Bar Chart)**:
   - X-axis: Content type.
   - Y-axis: Percentage.
   - Bars: Supply (% of corpus) vs Demand (% of search hits).

**ML Opportunities:**
1. **Content Prioritization**:
   - Use demand distribution to prioritize moderation queue → Approve high-demand content first.

---

### 2.2.6 SYSTEM ADMINISTRATION

#### **File: `app/api/v1/admin_settings.py`**

**Dependencies:**
```python
import json as _json
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, ValidationError
from typing import Any, List
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.session import get_db
from app.services.system_settings import get_setting, set_setting, delete_setting
from app.core.security import require_role, get_current_user
from app.core.permissions import Role
```

---

#### **Endpoint: `GET /admin/system_settings`**

**Authentication:** Required (Bearer token).

**Authorization:** Admin only.

**Response Schema:**
```python
class SettingOut(BaseModel):
    key: str
    value: Any
```

**Example Response:**
```json
[
  {
    "key": "rate_limits",
    "value": {
      "login": {"limit": 10, "window_seconds": 3600},
      "search": {"limit": 120, "window_seconds": 60},
      "submission_create": {"limit": 20, "window_seconds": 86400}
    }
  },
  {
    "key": "ft_min_word_len",
    "value": 2
  }
]
```

**Logic Flow (Line-by-Line):**
1. **Line 1**: Authorization check:
   ```python
   @router.get("", dependencies=[Depends(require_role(Role.ADMIN))])
   ```

2. **Line 10**: Query all settings:
   ```python
   query = text("SELECT `setting_key`, `value` FROM system_settings ORDER BY `setting_key` ASC")
   rows = db.execute(query).fetchall()
   ```

3. **Line 15**: Return settings list:
   ```python
   return [{"key": r[0], "value": r[1]} for r in rows]
   ```

**Why Raw SQL Instead of ORM?**
- **Simplicity**: Listing all settings is straightforward query.
- **Performance**: Direct SQL avoids ORM overhead.

---

#### **Endpoint: `GET /admin/system_settings/{key}`**

**Authentication:** Required (Bearer token).

**Authorization:** Admin only.

**Response Schema:**
```json
{
  "key": "rate_limits",
  "value": {
    "login": {"limit": 10, "window_seconds": 3600},
    "search": {"limit": 120, "window_seconds": 60},
    "submission_create": {"limit": 20, "window_seconds": 86400}
  }
}
```

**Logic Flow (Line-by-Line):**
1. **Line 1**: Authorization check.

2. **Line 10**: Call settings service:
   ```python
   val = get_setting(db, key, default=None, allow_env_override=True)
   ```
   - `allow_env_override=True`: Environment variable takes precedence over DB value.

3. **Line 15**: Validate exists:
   ```python
   if val is None:
       raise HTTPException(status_code=404, detail="Setting not found")
   ```

4. **Line 20**: Return setting:
   ```python
   return {"key": key, "value": val}
   ```

---

#### **Endpoint: `PUT /admin/system_settings/{key}`**

**Authentication:** Required (Bearer token).

**Authorization:** Admin only.

**Request Schema:**
```json
{
  "value": {
    "login": {"limit": 5, "window_seconds": 3600},
    "search": {"limit": 120, "window_seconds": 60},
    "submission_create": {"limit": 20, "window_seconds": 86400}
  }
}
```

**Response Schema:**
```json
{
  "key": "rate_limits",
  "value": {
    "login": {"limit": 5, "window_seconds": 3600},
    "search": {"limit": 120, "window_seconds": 60},
    "submission_create": {"limit": 20, "window_seconds": 86400}
  }
}
```

**Logic Flow (Line-by-Line):**
1. **Line 1**: Authorization check.

2. **Line 10**: Parse request body:
   ```python
   body_data = await request.json()
   
   if not isinstance(body_data, dict) or "value" not in body_data:
       raise HTTPException(status_code=422, detail="Request body must be JSON object with 'value' field")
   
   actual_value = body_data["value"]
   ```

3. **Line 20**: Capture audit metadata:
   ```python
   audit_meta = {
       "ip_address": request.client.host if request.client else None,
       "user_agent": request.headers.get("user-agent"),
       "request_id": request.headers.get("X-Request-ID"),
   }
   ```

4. **Line 30**: Call settings service (with validation):
   ```python
   set_setting(db, key, actual_value, actor_user_id=current_user.id, metadata=audit_meta)
   ```
   - **Inside `set_setting`**:
     - Line 5: Validate value against Pydantic schema (if validator exists).
     - Line 10: Upsert setting in DB.
     - Line 15: Write moderation log.
     - Line 20: Write audit log.
     - Line 25: Invalidate cache.
     - Line 30: Commit transaction.

5. **Line 40**: Return updated setting:
   ```python
   return {"key": key, "value": actual_value}
   ```

**Validation Example (Rate Limits):**
```python
class RateLimitAction(BaseModel):
    limit: int = Field(ge=1)  # Must be >= 1
    window_seconds: int = Field(ge=1)

class RateLimitsModel(BaseModel):
    login: RateLimitAction = RateLimitAction(limit=10, window_seconds=3600)
    search: RateLimitAction = RateLimitAction(limit=120, window_seconds=60)
    submission_create: RateLimitAction = RateLimitAction(limit=20, window_seconds=86400)

# In set_setting:
if key == "rate_limits":
    RateLimitsModel.model_validate(actual_value)  # Pydantic validation
    # If invalid → Raises ValidationError → Caught and returned as 400
```

**Error Ontology:**

| HTTP Code | Condition | Detail Message |
|-----------|-----------|----------------|
| 401 | Missing/invalid JWT | "Missing credentials" |
| 403 | User role < admin | "Insufficient role" |
| 422 | Invalid request body | "Request body must be JSON object with 'value' field" |
| 400 | Validation fails | Pydantic error messages (e.g., "limit must be >= 1") |

**🔬 Data Science & Analytics Perspective:**

**Feature Engineering:**
1. **Setting Change Frequency**:
   - `COUNT(audit_logs WHERE action='system_setting:update') GROUP BY setting_key` → Which settings are tuned most?

2. **Configuration Drift**:
   - Track setting values over time → Identify settings that fluctuate vs stable.

**Visualizations:**
1. **Setting Change Timeline (Gantt Chart)**:
   - X-axis: Time.
   - Y-axis: Setting key.
   - Bars: Duration each value was active.

**ML Opportunities:**
1. **Optimal Configuration Search**:
   - Train Bayesian Optimization on `[system_settings] → performance_metrics`.
   - Recommend optimal settings.

---


#### **File: `app/api/v1/admin_audit.py`**

**Dependencies:**
```python
import csv
import io
import json
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import require_role
from app.core.permissions import Role
from app.db.models import AuditLog
```

---

#### **Endpoint: `GET /admin/audit_logs`**

**Authentication:** Required (Bearer token).

**Authorization:** Admin only.

**Query Parameters:**
- `action` (optional): Filter by action type (e.g., "system_setting:update").
- `resource_type` (optional): Filter by resource (e.g., "doha", "user").
- `actor_user_id` (optional): Filter by user who performed action.
- `start` (optional): ISO datetime (filter `created_at >= start`).
- `end` (optional): ISO datetime (filter `created_at <= end`).
- `offset` (default=0): Pagination offset.
- `limit` (default=100, max=1000): Page size.

**Response Schema:**
```json
{
  "total": 2345,
  "results": [
    {
      "id": 100,
      "actor_user_id": 8,
      "action": "system_setting:update",
      "resource_type": "system_setting",
      "resource_id": null,
      "before": {"rate_limits": {"login": {"limit": 10}}},
      "after": {"rate_limits": {"login": {"limit": 5}}},
      "metadata": {"ip_address": "192.168.1.1", "user_agent": "Mozilla/5.0..."},
      "created_at": "2024-03-15T10:30:00Z"
    }
  ]
}
```

**Logic Flow (Line-by-Line):**
1. **Line 1**: Authorization check:
   ```python
   @router.get("", dependencies=[Depends(require_role(Role.ADMIN))])
   ```

2. **Line 10**: Build query with filters:
   ```python
   def _apply_filters(q, action, resource_type, actor_user_id, start, end):
       if action:
           q = q.filter(AuditLog.action == action)
       if resource_type:
           q = q.filter(AuditLog.resource_type == resource_type)
       if actor_user_id is not None:
           q = q.filter(AuditLog.actor_user_id == actor_user_id)
       if start:
           q = q.filter(AuditLog.created_at >= start)
       if end:
           q = q.filter(AuditLog.created_at <= end)
       return q
   
   q = db.query(AuditLog)
   q = _apply_filters(q, action, resource_type, actor_user_id, start, end)
   ```

3. **Line 30**: Execute query with pagination:
   ```python
   total = q.count()
   rows = q.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit).all()
   ```

4. **Line 35**: Convert rows to dicts:
   ```python
   def _row_to_dict(r):
       # Handle backward compatibility: audit_metadata vs metadata
       meta = getattr(r, "audit_metadata", None) if hasattr(r, "audit_metadata") else getattr(r, "metadata", None)
       
       return {
           "id": r.id,
           "actor_user_id": r.actor_user_id,
           "action": r.action,
           "resource_type": r.resource_type,
           "resource_id": r.resource_id,
           "before": r.audit_before,  # Column name changed from "before" to "audit_before"
           "after": r.after,
           "metadata": meta,
           "created_at": r.created_at.isoformat() if r.created_at else None,
       }
   
   results = [_row_to_dict(r) for r in rows]
   ```

5. **Line 50**: Return paginated response:
   ```python
   return {"total": total, "results": results}
   ```

**Why Order by `created_at DESC`?**
- **Recent First**: Most relevant audits are recent actions (admins typically investigate recent issues).

**Error Ontology:**

| HTTP Code | Condition | Detail Message |
|-----------|-----------|----------------|
| 401 | Missing/invalid JWT | "Missing credentials" |
| 403 | User role < admin | "Insufficient role" |
| 422 | Invalid datetime format | "invalid datetime format" (Pydantic) |

---

#### **Endpoint: `GET /admin/audit_logs/export/csv`**

**Authentication:** Required (Bearer token).

**Authorization:** Admin only.

**Query Parameters:**
- Same as list endpoint (action, resource_type, actor_user_id, start, end).

**Response:**
- **Content-Type**: `text/csv`
- **Content-Disposition**: `attachment; filename=audit_logs_20240315103000.csv`

**CSV Format:**
```csv
id,actor_user_id,action,resource_type,resource_id,before,after,audit_metadata,created_at
100,8,system_setting:update,system_setting,,"{""rate_limits"":{""login"":{""limit"":10}}}","{""rate_limits"":{""login"":{""limit"":5}}}","{""ip_address"":""192.168.1.1""}",2024-03-15T10:30:00Z
```

**Logic Flow (Line-by-Line):**
1. **Line 1**: Authorization check.

2. **Line 10**: Apply filters (same as list endpoint):
   ```python
   q = db.query(AuditLog)
   q = _apply_filters(q, action, resource_type, actor_user_id, start, end)
   rows = q.order_by(AuditLog.created_at.desc()).all()
   ```

3. **Line 20**: Create CSV in memory:
   ```python
   output = io.StringIO()
   writer = csv.writer(output)
   
   # Write header
   writer.writerow([
       "id", "actor_user_id", "action", "resource_type", "resource_id",
       "before", "after", "audit_metadata", "created_at"
   ])
   ```

4. **Line 30**: Write data rows:
   ```python
   for r in rows:
       # Handle backward compatibility
       meta = getattr(r, "audit_metadata", None) if hasattr(r, "audit_metadata") else getattr(r, "metadata", None)
       
       writer.writerow([
           r.id,
           r.actor_user_id,
           r.action,
           r.resource_type,
           r.resource_id,
           json.dumps(r.audit_before, ensure_ascii=False) if r.audit_before is not None else "",
           json.dumps(r.after, ensure_ascii=False) if r.after is not None else "",
           json.dumps(meta, ensure_ascii=False) if meta is not None else "",
           r.created_at.isoformat() if r.created_at else "",
       ])
   ```

5. **Line 50**: Return CSV response:
   ```python
   resp = Response(content=output.getvalue(), media_type="text/csv")
   resp.headers["Content-Disposition"] = f"attachment; filename=audit_logs_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.csv"
   return resp
   ```

**Why In-Memory CSV?**
- **Small Datasets**: Audit logs typically <100K rows → Fits in memory.
- **Simplicity**: No temporary files, no cleanup.
- **Caveat**: For large exports (>1M rows), consider streaming response or background job.

**Why `ensure_ascii=False`?**
- **Unicode Support**: JSON may contain Devanagari characters → Need UTF-8 encoding.

**Error Ontology:**

| HTTP Code | Condition | Detail Message |
|-----------|-----------|----------------|
| 401 | Missing/invalid JWT | "Missing credentials" |
| 403 | User role < admin | "Insufficient role" |

**🔬 Data Science & Analytics Perspective:**

**Feature Engineering:**
1. **Action Frequency**:
   - `COUNT(*) GROUP BY action` → Most common admin actions.

2. **Temporal Patterns**:
   - `COUNT(*) GROUP BY HOUR(created_at)` → Peak admin activity hours.

3. **Actor Productivity**:
   - `COUNT(*) GROUP BY actor_user_id` → Admin activity distribution.

**Visualizations:**
1. **Audit Timeline (Line Chart)**:
   - X-axis: Date.
   - Y-axis: `COUNT(audit_logs)`.
   - Annotation: Mark system incidents or deployments.

2. **Action Type Breakdown (Tree Map)**:
   - Rectangle size: Action frequency.
   - Color: Resource type.

3. **Actor Activity Heatmap (2D)**:
   - X-axis: Hour of day.
   - Y-axis: Actor user ID.
   - Cell color: Action count.

**ML Opportunities:**
1. **Anomaly Detection (Insider Threat)**:
   - Features: `[action_frequency, action_diversity, time_of_day, resource_access_pattern]`.
   - **Flags**:
     - Admin accessing 100+ user records in 1 hour (data exfiltration?).
     - Delete actions outside business hours.
     - Sudden spike in delete actions.

2. **Access Pattern Clustering**:
   - Cluster admins by `[actions_performed, resources_accessed]` → Discover admin roles.

3. **Predictive Auditing**:
   - Train model to predict high-risk actions before they occur.

---

#### **Endpoint: `GET /admin/audit_logs/{id}`**

**Authentication:** Required (Bearer token).

**Authorization:** Admin only.

**Response Schema:**
```json
{
  "id": 100,
  "actor_user_id": 8,
  "action": "system_setting:update",
  "resource_type": "system_setting",
  "resource_id": null,
  "before": {"rate_limits": {"login": {"limit": 10}}},
  "after": {"rate_limits": {"login": {"limit": 5}}},
  "metadata": {"ip_address": "192.168.1.1"},
  "created_at": "2024-03-15T10:30:00Z"
}
```

**Logic Flow (Line-by-Line):**
1. **Line 1**: Authorization check.

2. **Line 10**: Query audit log by ID:
   ```python
   r = db.query(AuditLog).filter(AuditLog.id == id).first()
   ```

3. **Line 15**: Validate exists:
   ```python
   if not r:
       raise HTTPException(status_code=404, detail="Audit log not found")
   ```

4. **Line 20**: Return audit log:
   ```python
   return _row_to_dict(r)
   ```

---

## 2.3 SERVICES & UTILITIES

### 2.3.1 TEXT NORMALIZATION

#### **File: `app/utils/text_normalize.py`**

**Purpose:** Normalize Roman transliterations for consistent cross-script search.

**Function: `normalize_roman(text: Optional[str]) -> Optional[str]`**

**Logic Flow (Line-by-Line):**
1. **Line 1**: Handle null input:
   ```python
   if not text:
       return None
   ```

2. **Line 5**: Unicode NFKD decomposition:
   ```python
   text = unicodedata.normalize("NFKD", text)
   # "café" → "cafe" + combining accent
   # "मुख्य" → remains unchanged (Devanagari has no decomposition)
   ```

3. **Line 10**: Remove diacritics (combining characters):
   ```python
   text = "".join(c for c in text if not unicodedata.combining(c))
   # "cafe" + combining accent → "cafe"
   # "ā" → "a"
   # "ē" → "e"
   ```

4. **Line 15**: Lowercase:
   ```python
   text = text.lower()
   # "Mukhya" → "mukhya"
   ```

5. **Line 20**: Remove punctuation:
   ```python
   text = re.sub(r"[^\w\s]", " ", text)
   # "mukhya-shabd" → "mukhya shabd"
   # "hello, world!" → "hello  world "
   ```

6. **Line 25**: Collapse whitespace:
   ```python
   text = re.sub(r"\s+", " ", text).strip()
   # "hello  world " → "hello world"
   ```

7. **Line 30**: Return normalized text (or None if empty):
   ```python
   return text or None
   ```

**Examples:**
- `"Mukhya Shabd"` → `"mukhya shabd"`
- `"mukhya-shabd"` → `"mukhya shabd"`
- `"Mukhyā"` → `"mukhya"` (diacritic removed)
- `"  MUKHYA   SHABD  "` → `"mukhya shabd"` (whitespace collapsed)
- `""` → `None`
- `None` → `None`

**Why This Normalization?**
- **User Input Variability**: Users may type "mukhya", "Mukhya", "mukhya-shabd", or "mukhyā".
- **Search Consistency**: All variants map to same normalized form → Matches found.
- **Database Storage**: Store normalized version in `*_roman_norm` columns → Efficient indexing.

**🔬 Data Science & Analytics Perspective:**

**Feature Engineering:**
1. **Normalization Impact**:
   - Compare search results before/after normalization → Measure improvement.

2. **Diacritic Frequency**:
   - `COUNT(text WHERE text != normalize(text))` → % of entries with diacritics.

**Visualizations:**
1. **Normalization Before/After Comparison**:
   - Show original vs normalized text side-by-side.

**ML Opportunities:**
1. **Learned Normalization**:
   - Train seq2seq model on `(original, normalized)` pairs → Capture domain-specific patterns.

---

## 2.4 SECURITY & AUTHENTICATION DEEP DIVE

### 2.4.1 PASSWORD HASHING

#### **File: `app/auth/hash.py`**

**Dependencies:**
```python
import bcrypt
```

**Function: `hash_password(plain_text: str) -> str`**

**Logic Flow (Line-by-Line):**
1. **Line 1**: Validate input:
   ```python
   if plain_text is None:
       raise ValueError("Password cannot be None")
   ```

2. **Line 5**: Encode password to bytes:
   ```python
   pw = plain_text.encode("utf-8")
   ```

3. **Line 10**: Generate salt:
   ```python
   salt = bcrypt.gensalt()
   # Default cost=12 (2^12 = 4096 rounds)
   # Higher cost = slower hashing = stronger protection
   ```

4. **Line 15**: Hash password:
   ```python
   hashed = bcrypt.hashpw(pw, salt)
   # Returns bytes: b'$2b$12$...'
   ```

5. **Line 20**: Decode to string:
   ```python
   return hashed.decode('utf-8')
   # Returns string: "$2b$12$..."
   ```

**Function: `verify_password(plain_text: str, hashed: str) -> bool`**

**Logic Flow (Line-by-Line):**
1. **Line 1**: Validate inputs:
   ```python
   if plain_text is None or hashed is None:
       return False
   ```

2. **Line 5**: Verify password:
   ```python
   return bcrypt.checkpw(plain_text.encode('utf-8'), hashed.encode('utf-8'))
   # Internally: Extracts salt from hash, re-hashes plain_text, compares
   ```

**Bcrypt Deep Dive:**
- **Algorithm**: Blowfish-based key derivation function.
- **Salt**: Random 16-byte value → Prevents rainbow table attacks.
- **Cost Factor**: 12 → 2^12 = 4096 rounds → ~250ms per hash (on modern CPU).
- **Adaptive**: Can increase cost factor over time as hardware improves.

**Security Properties:**
- **Slow by Design**: 250ms per hash → Brute-force attack = 4 hashes/second → Impractical.
- **Unique Salt**: Each password gets unique salt → Same password produces different hashes.
- **One-Way**: Cannot derive password from hash (only verify).

**Security Considerations:**
- **Timing Attack**: `bcrypt.checkpw` is NOT constant-time → Vulnerable to timing attacks (MINOR VULNERABILITY).
- **No Rate Limiting in Hash Function**: Must be handled at application layer (done via rate limiting on `/auth/login`).

**🔬 Data Science & Analytics Perspective:**

**Feature Engineering:**
1. **Hash Cost Evolution**:
   - Extract cost from hash (first 7 chars: `$2b$12$` → cost=12).
   - Track distribution → Plan cost increase migration.

2. **Password Strength (External Analysis)**:
   - If storing client-side entropy (e.g., zxcvbn score), correlate with account security incidents.

**ML Opportunities:**
1. **Breach Detection**:
   - Monitor login attempts → Flag accounts with unusual failure patterns.

---

### 2.4.2 JWT TOKEN GENERATION

#### **File: `app/auth/jwt.py`**

**Dependencies:**
```python
import jwt
from datetime import datetime, timedelta
from app.core.settings import settings
from typing import Dict, Any
```

**Function: `create_access_token(user_id: int, expires_seconds: int | None = None) -> str`**

**Logic Flow (Line-by-Line):**
1. **Line 1**: Determine expiration:
   ```python
   expires_seconds = expires_seconds or settings.JWT_ACCESS_TOKEN_EXPIRES_SECONDS  # 900 (15 min)
   exp = datetime.utcnow() + timedelta(seconds=int(expires_seconds))
   ```

2. **Line 5**: Build payload:
   ```python
   payload: Dict[str, Any] = {
       "sub": str(user_id),  # Subject (user identifier)
       "exp": exp,  # Expiration timestamp
       "type": "access"  # Token type (distinguish from refresh)
   }
   ```

3. **Line 10**: Encode JWT:
   ```python
   token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
   # Default algorithm: HS256 (HMAC-SHA256 symmetric signing)
   # Returns string: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
   ```

4. **Line 15**: Return token:
   ```python
   return token
   ```

**Function: `create_refresh_token(user_id: int, expires_seconds: int | None = None) -> str`**

**Logic Flow:**
- Same as `create_access_token`, except:
  - Default expiration: 1,209,600 seconds (14 days).
  - Token type: `"refresh"`.

**Function: `decode_token(token: str) -> dict`**

**Logic Flow (Line-by-Line):**
1. **Line 1**: Decode JWT:
   ```python
   payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
   # Validates signature + expiration
   # Raises jwt.ExpiredSignatureError if expired
   # Raises jwt.InvalidTokenError if signature invalid
   ```

2. **Line 5**: Return payload:
   ```python
   return payload  # {"sub": "42", "exp": 1234567890, "type": "access"}
   ```

**JWT Structure:**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0MiIsImV4cCI6MTIzNDU2Nzg5MCwidHlwZSI6ImFjY2VzcyJ9.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
│                Header                │                     Payload                    │          Signature         │
```

**Header (Base64 decoded):**
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

**Payload (Base64 decoded):**
```json
{
  "sub": "42",
  "exp": 1234567890,
  "type": "access"
}
```

**Signature:**
```
HMACSHA256(
  base64UrlEncode(header) + "." + base64UrlEncode(payload),
  settings.JWT_SECRET_KEY
)
```

**Security Considerations:**
- **Secret Key Strength**: Must be long (32+ bytes), random, and kept secret.
- **Algorithm Choice**: HS256 (symmetric) is acceptable for single-server deployments. RS256 (asymmetric) recommended for microservices.
- **Token Storage**: Access token stored client-side (localStorage or memory). Refresh token stored server-side (database).
- **No Revocation**: Access tokens cannot be revoked (stateless) → Must wait for expiration. Refresh tokens can be revoked (stored in DB).

**🔬 Data Science & Analytics Perspective:**

**Feature Engineering:**
1. **Token Lifetime Analysis**:
   - `exp - iat` → Distribution of token ages at verification time.

2. **Token Reuse**:
   - Count how many times same access token is used → Detect sharing.

**ML Opportunities:**
1. **Token Theft Detection**:
   - Flag tokens used from multiple IPs in short timespan.

---

## CONCLUSION & NEXT STEPS

This Living Technical Manifesto has provided a **regressive, microscopic analysis** of the Awadhi Corpus Backend system, covering:

1. **Database Schema**: 13 tables across 11 modules with column-by-column analysis.
2. **API Endpoints**: 40+ endpoints with line-by-line logic flows and error ontologies.
3. **Services & Utilities**: Engagement tracking, search, recommendations, analytics, text normalization.
4. **Security Architecture**: Authentication, authorization, rate limiting, audit logging.
5. **Data Science Integration**: 100+ feature engineering opportunities, 50+ visualization suggestions, 30+ ML use cases.

**Key Architectural Strengths:**
- **Hybrid SQL Approach**: ORM for CRUD, raw SQL for MySQL-specific optimizations.
- **Atomic Transactions**: Batch operations with savepoint-based rollback.
- **Engagement Weighting**: Logarithmic scoring prevents viral outliers from dominating.
- **Idempotent Operations**: Batch approval safely handles duplicate submissions.

**Identified Vulnerabilities:**
1. **Password Strength**: No server-side validation (accepts "123" as valid password).
2. **OAuth CSRF**: `state` parameter not validated in Google callback.
3. **Timing Attack**: `verify_password` not constant-time.
4. **Email Takeover**: OAuth links to pre-existing email without verification.

**Recommended ML/AI Injection Points:**
1. **Automatic Romanization**: Seq2seq model for Devanagari → Roman transliteration.
2. **Quality Prediction**: Classify submissions as likely approved/rejected before moderation.
3. **Duplicate Detection**: LSH-based near-duplicate finding for submissions.
4. **Recommendation Engine**: Collaborative filtering + content-based hybrid.
5. **Anomaly Detection**: Flag suspicious user behavior (bot attacks, insider threats).

**Next Documentation Phases:**
- **Phase 2**: Service layer deep dive (engagement, search, moderation services).
- **Phase 3**: Testing strategy analysis (unit tests, integration tests, fixtures).
- **Phase 4**: Deployment architecture (Docker, CI/CD, monitoring).
- **Phase 5**: Performance optimization roadmap (query optimization, caching strategies).

---

**END OF SECTION 2: THE "REGRESSIVE" LOGIC AUDIT**
