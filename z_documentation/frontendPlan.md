# **PART 1: THE "ZERO-AMBIGUITY" TECHNICAL AUDIT**

***

## **1.1 DATABASE SCHEMA DOCUMENTATION**

### **Module 1: User Management & Authentication**

#### **Table: `users`**
- **Columns:**
  - `id` (Integer, PK, Auto-increment)
  - `username` (String, Unique, Nullable, Indexed)
  - `email` (String, Unique, NOT NULL, Indexed)
  - `password_hash` (String, Nullable)
  - `role` (String, Default: 'registered', NOT NULL, Indexed)
  - `permissions` (Integer, Default: 0)
  - `permission_scopes` (JSON, Nullable)
  - `is_active` (Boolean, Default: TRUE)
  - `is_banned` (Boolean, Default: FALSE)
  - `created_at` (DateTime with TZ, Server Default: CURRENT_TIMESTAMP)
  - `updated_at` (DateTime with TZ, Auto-update)
  - `last_login` (DateTime with TZ, Nullable)
- **Indexes:** `ix_users_email`, `ix_users_username`, `ix_users_role`
- **Use Cases:** User registration, authentication, role-based access control

#### **Table: `refresh_tokens`**
- **Columns:**
  - `id` (Integer, PK, Auto-increment)
  - `token` (String, Unique, NOT NULL, Indexed)
  - `user_id` (Integer, FK → users.id, Indexed)
  - `expires_at` (DateTime with TZ, NOT NULL)
  - `created_at` (DateTime with TZ, Server Default)
- **Indexes:** `ix_refresh_tokens_token`, `ix_refresh_tokens_user_id`
- **Use Cases:** JWT refresh token storage, token validation

#### **Table: `oauth_accounts`**
- **Columns:**
  - `id` (Integer, PK, Auto-increment)
  - `provider` (String, NOT NULL)
  - `provider_user_id` (String, NOT NULL)
  - `user_id` (Integer, FK → users.id, NOT NULL)
  - `raw_profile` (JSON, Nullable)
  - `created_at` (DateTime with TZ, Server Default)
- **Unique Constraint:** `uq_provider_user` (provider, provider_user_id)
- **Indexes:** `ix_oauth_provider_user`
- **Use Cases:** Google OAuth integration, social login

***

### **Module 2: Classical Literature Hierarchy**

#### **Table: `classical_authors`**
- **Columns:**
  - `id` (Integer, PK, Auto-increment)
  - `slug` (String, Unique, NOT NULL, Indexed)
  - `name` (String, NOT NULL)
  - `short_bio` (Text, Nullable)
  - `long_bio` (Text, Nullable)
  - `language` (String, Nullable, Indexed)
  - `is_deleted` (Boolean, Default: FALSE)
  - `created_at`, `updated_at` (DateTime with TZ)
- **Indexes:** `ix_authors_slug`, `ix_authors_language`
- **Use Cases:** Author listings, author detail pages, filtering by language

#### **Table: `classical_works`**
- **Columns:**
  - `id` (Integer, PK, Auto-increment)
  - `author_id` (Integer, FK → classical_authors.id, NOT NULL, Indexed)
  - `slug` (String, NOT NULL)
  - `title` (String, NOT NULL)
  - `description` (Text, Nullable)
  - `work_type` (String, Nullable, Indexed)
  - `original_script` (String, Nullable)
  - `is_deleted` (Boolean, Default: FALSE)
  - `created_at`, `updated_at` (DateTime with TZ)
- **Unique Constraint:** `uq_works_author_slug` (author_id, slug)
- **Indexes:** `ix_works_author_id`, `ix_works_slug`, `ix_works_work_type`
- **Use Cases:** Work listings under authors, work type filtering

#### **Table: `work_chapters`**
- **Columns:**
  - `id` (Integer, PK, Auto-increment)
  - `work_id` (Integer, FK → classical_works.id, NOT NULL, Indexed)
  - `slug` (String, NOT NULL, Indexed)
  - `title` (String, NOT NULL)
  - `number` (Integer, NOT NULL, Indexed)
  - `is_deleted` (Boolean, Default: FALSE)
  - `created_at`, `updated_at` (DateTime with TZ)
- **Unique Constraints:** `uq_chapters_work_slug`, `uq_chapters_work_number`
- **Indexes:** `ix_chapters_work_id`, `ix_chapters_slug`, `ix_chapters_number`
- **Use Cases:** Chapter navigation within works, sequential chapter browsing

***

### **Module 3: Content Submission & Moderation**

#### **Table: `submissions`**
- **Columns:**
  - `id` (Integer, PK, Auto-increment)
  - `content_type` (String, NOT NULL) — Enum: 'doha', 'dictionary', 'idiom', 'article'
  - `main_text` (Text, NOT NULL)
  - `meaning` (Text, Nullable)
  - `is_classical` (Boolean, Default: FALSE)
  - `author_slug`, `work_slug`, `chapter_slug` (String, Nullable)
  - `number_in_chapter` (Integer, Nullable)
  - `references` (JSON, Nullable)
  - `status` (String, Default: 'draft') — Enum: draft, pending_review, approved, rejected
  - `visibility` (String, Default: 'private') — Enum: private, public
  - `version` (Integer, Default: 1)
  - `contributor_id` (Integer, FK → users.id, NOT NULL, Indexed)
  - `assigned_moderator_id` (Integer, FK → users.id, Nullable, Indexed)
  - `priority` (Integer, Default: 0)
  - `is_deleted` (Boolean, Default: FALSE)
  - `created_at`, `updated_at` (DateTime with TZ)
- **Indexes:** `ix_submissions_contributor`, `ix_submissions_status_created`, `ix_submissions_assigned_mod`
- **Use Cases:** User content submission, moderation queue management

#### **Table: `moderation_guidelines`**
- **Columns:**
  - `id` (Integer, PK, Auto-increment)
  - `version` (String, Unique, NOT NULL)
  - `title` (String, NOT NULL)
  - `description` (Text, Nullable)
  - `url` (String, Nullable)
  - `is_active` (Boolean, Default: FALSE)
  - `created_at` (DateTime with TZ)

#### **Table: `moderation_logs`**
- **Columns:**
  - `id` (Integer, PK, Auto-increment)
  - `submission_id` (Integer, NOT NULL, Indexed)
  - `moderator_id` (Integer, NOT NULL, Indexed)
  - `action` (String, NOT NULL)
  - `from_status`, `to_status` (String, Nullable)
  - `guideline_version` (String, Nullable)
  - `note` (Text, Nullable)
  - `created_at` (DateTime with TZ)
- **Indexes:** `ix_moderation_logs_submission`, `ix_moderation_logs_moderator`

***

### **Module 4: Canonical Content — Dohas**

#### **Table: `doha_entries`**
- **Columns:**
  - `id` (Integer, PK, Auto-increment)
  - `hierarchy_path` (String, Nullable, Indexed)
  - `author_id`, `work_id`, `chapter_id` (Integer, Nullable, Indexed)
  - `number_in_chapter` (Integer, Nullable)
  - `main_text` (Text, NOT NULL)
  - `meaning` (Text, Nullable)
  - `text_devanagari` (Text, Nullable)
  - `text_romanized` (Text, Nullable)
  - `status` (String, Default: 'active')
  - `visibility` (String, Default: 'public')
  - `version` (Integer, Default: 1)
  - `is_canonical` (Boolean, Default: TRUE)
  - `variant_group_id` (Integer, Nullable)
  - `confidence_level` (Integer, Nullable)
  - `source_reference` (JSON, Nullable)
  - `source_submission_id` (Integer, Unique, Nullable)
  - `created_by`, `verified_by` (Integer, Nullable)
  - `verified_at` (DateTime with TZ, Nullable)
  - `is_deleted` (Boolean, Default: FALSE)
  - `created_at`, `updated_at` (DateTime with TZ)
- **Indexes:** `ix_doha_hierarchy_path`, `ix_doha_author_id`, `ix_doha_work_id`, `ix_doha_chapter_id`
- **FULLTEXT Index (MySQL):** `ft_doha_main_meaning_devanagari_romanized` on (main_text, meaning, text_devanagari, text_romanized)
- **Use Cases:** Doha detail pages, search by author/work/chapter, full-text search

#### **Table: `content_versions`**
- **Columns:**
  - `id` (Integer, PK, Auto-increment)
  - `content_type` (String, NOT NULL)
  - `content_id` (Integer, NOT NULL)
  - `version_number` (Integer, NOT NULL)
  - `main_text`, `meaning`, `text_devanagari`, `text_romanized` (Text, Nullable)
  - `created_by` (Integer, Nullable)
  - `created_at` (DateTime with TZ)
  - `notes` (Text, Nullable)
- **Composite Index:** `ix_content_versions_type_id` (content_type, content_id)
- **Use Cases:** Version history tracking, content rollback

***

### **Module 5: Canonical Content — Dictionary, Idioms, Articles**

#### **Table: `dictionary_entries`**
- **Columns:**
  - `id` (Integer, PK, Auto-increment)
  - `lemma_devanagari` (String, NOT NULL, Indexed)
  - `lemma_roman` (String, Nullable, Indexed)
  - `lemma_roman_norm` (String, Nullable, Indexed)
  - `language` (String, Default: 'hi')
  - `senses` (JSON, NOT NULL) — Array of sense objects
  - `pronunciation` (String, Nullable)
  - `examples` (JSON, Nullable)
  - `contributor_id`, `author_id`, `work_id`, `chapter_id` (Integer, Nullable, Indexed)
  - `number_in_chapter` (Integer, Nullable)
  - `source_submission_id` (Integer, Unique, Nullable)
  - `visibility` (String, Default: 'public')
  - `version` (Integer, Default: 1)
  - `created_at`, `updated_at` (DateTime with TZ)
- **FULLTEXT Index (MySQL):** `ft_dictionary_lemma_fulltext` on (lemma_devanagari, lemma_roman)
- **Use Cases:** Dictionary search, word detail pages, alphabetical browsing

#### **Table: `idiom_entries`**
- **Columns:**
  - `id` (Integer, PK, Auto-increment)
  - `text_devanagari` (Text, NOT NULL, Indexed)
  - `text_roman` (Text, Nullable)
  - `text_roman_norm` (String, Nullable, Indexed)
  - `meaning` (Text, Nullable)
  - `examples` (JSON, Nullable)
  - `region` (String, Nullable)
  - `contributor_id`, `author_id`, `work_id`, `chapter_id` (Integer, Nullable, Indexed)
  - `number_in_chapter` (Integer, Nullable)
  - `source_submission_id` (Integer, Unique, Nullable)
  - `visibility` (String, Default: 'public')
  - `version` (Integer, Default: 1)
  - `created_at`, `updated_at` (DateTime with TZ)
- **FULLTEXT Index (MySQL):** `ft_idiom_text_fulltext` on (text_devanagari, text_roman)
- **Use Cases:** Idiom search, idiom detail pages

#### **Table: `article_entries`**
- **Columns:**
  - `id` (Integer, PK, Auto-increment)
  - `title` (String, NOT NULL, Indexed)
  - `title_devanagari`, `title_roman`, `title_roman_norm` (String, Nullable, Indexed on norm)
  - `body` (Text, NOT NULL)
  - `excerpt` (Text, Nullable)
  - `author_id` (Integer, Nullable, Indexed)
  - `tags` (JSON, Nullable) — Array of strings
  - `contributor_id` (Integer, Nullable, Indexed)
  - `source_submission_id` (Integer, Unique, Nullable)
  - `visibility` (String, Default: 'public')
  - `version` (Integer, Default: 1)
  - `created_at`, `updated_at` (DateTime with TZ)
- **FULLTEXT Index (MySQL):** `ft_article_title_body` on (title, body)
- **Use Cases:** Article listing, tag filtering, full-text search

***

### **Module 6: Engagement & Analytics**

#### **Table: `engagement_kpis`**
- **Columns:**
  - `id` (Integer, PK, Auto-increment)
  - `content_type` (String, NOT NULL, Indexed)
  - `content_id` (Integer, NOT NULL, Indexed)
  - `views_count` (Integer, Default: 0)
  - `search_hits_count` (Integer, Default: 0)
  - `likes_count` (Integer, Default: 0)
  - `shares_count` (Integer, Default: 0)
  - `bookmarks_count` (Integer, Default: 0)
  - `weight_score` (Float, Default: 0.0)
  - `updated_at` (DateTime, Auto-update)
- **Unique Constraint:** `uq_engagement_content` (content_type, content_id)
- **Composite Index:** `ix_engagement_content`
- **Use Cases:** Trending content, analytics dashboard, content ranking

#### **Table: `user_interactions`**
- **Columns:**
  - `id` (Integer, PK, Auto-increment)
  - `user_id` (Integer, NOT NULL, Indexed)
  - `content_type` (String, NOT NULL, Indexed)
  - `content_id` (Integer, NOT NULL, Indexed)
  - `interaction_type` (String, NOT NULL) — Enum: 'like', 'bookmark'
  - `is_active` (Boolean, Default: TRUE)
  - `interaction_metadata` (JSON, Nullable)
  - `created_at`, `updated_at` (DateTime with TZ)
- **Unique Constraint:** `uq_user_interaction` (user_id, content_type, content_id, interaction_type)
- **Composite Index:** `ix_user_interaction_user_content`
- **Use Cases:** User bookmarks list, liked content, personalization

#### **Table: `share_logs`**
- **Columns:**
  - `id` (Integer, PK, Auto-increment)
  - `user_id` (Integer, NOT NULL, Indexed)
  - `content_type`, `content_id` (String/Integer, NOT NULL, Indexed)
  - `share_metadata` (JSON, Nullable) — channel, referrer, IP
  - `created_at` (DateTime with TZ)
- **Composite Index:** `ix_share_logs_content`
- **Use Cases:** Share count analytics, viral content tracking

#### **Table: `reports`**
- **Columns:**
  - `id` (Integer, PK, Auto-increment)
  - `user_id` (Integer, NOT NULL, Indexed)
  - `content_type`, `content_id` (String/Integer, NOT NULL, Indexed)
  - `reason` (String, NOT NULL) — Enum: spam, abuse, copyright, other
  - `note` (Text, Nullable)
  - `report_metadata` (JSON, Nullable)
  - `status` (String, Default: 'open') — Enum: open, resolved, rejected
  - `created_at`, `updated_at` (DateTime with TZ)
- **Composite Index:** `ix_reports_content`
- **Use Cases:** Content moderation, flag management

***

### **Module 7: System & Audit**

#### **Table: `system_settings`**
- **Columns:**
  - `key` (String, PK, NOT NULL, Indexed)
  - `value` (JSON, Nullable)
  - `created_at`, `updated_at` (DateTime with TZ)
- **Use Cases:** Feature flags, system configuration, rate limits

#### **Table: `audit_logs`**
- **Columns:**
  - `id` (Integer, PK, Auto-increment)
  - `actor_user_id` (Integer, Nullable, Indexed)
  - `action` (String, NOT NULL, Indexed)
  - `resource_type` (String, Nullable)
  - `resource_id` (Integer, Nullable)
  - `before`, `after` (JSON, Nullable)
  - `metadata` (JSON, Nullable)
  - `created_at` (DateTime with TZ, Indexed)
- **Indexes:** `ix_audit_created_at`, `ix_audit_resourcetype_id`, `ix_audit_actor`, `ix_audit_action`
- **Use Cases:** Compliance, activity tracking, forensics

#### **Table: `rate_limit_counters`**
- **Columns:**
  - `id` (Integer, PK, Auto-increment)
  - `user_id` (Integer, Nullable)
  - `ip_address` (String, Nullable)
  - `action_key` (String, NOT NULL)
  - `time_bucket_start` (DateTime with TZ, NOT NULL)
  - `count` (Integer, Default: 0)
  - `granularity` (Integer, Default: 60)
  - `created_at`, `updated_at` (DateTime with TZ)
- **Unique Constraint:** `uq_rate_limit_bucket`
- **Composite Index:** `ix_rl_action_bucket`

***

## **1.2 API ROUTES DOCUMENTATION**

### **Authentication Routes (Tag: `auth`)**

| **HTTP Method** | **Endpoint** | **Purpose** |
|---|---|---|
| POST | `/auth/register` | Create new user account |
| POST | `/auth/login` | Authenticate user, return access + refresh tokens |
| POST | `/auth/refresh` | Exchange refresh token for new access token |
| POST | `/auth/logout` | Invalidate refresh token |
| GET | `/auth/me` | Get current authenticated user details |
| GET | `/auth/oauth/google/callback` | Handle Google OAuth callback |

**Parameters:**
- `/auth/register`: Body: `RegisterIn` (email, password, username optional)
- `/auth/login`: Body: `LoginIn` (email, password)
- `/auth/refresh`: Body: `RefreshIn` (refresh_token)
- `/auth/logout`: Body: `LogoutIn` (refresh_token)
- `/auth/oauth/google/callback`: Query: `code` (optional string), `state` (optional string)

***

### **Admin User Management (Tag: `admin-users`)**

| **HTTP Method** | **Endpoint** | **Purpose** |
|---|---|---|
| GET | `/admin/users` | List all users (admin only) |
| POST | `/admin/users` | Create user via admin |
| GET | `/admin/users/{user_id}` | Get single user details |
| PATCH | `/admin/users/{user_id}` | Update user (role, permissions, etc.) |

**Parameters:**
- `GET /admin/users`: Query: `offset` (int, min 0, default 0), `limit` (int, min 1, max 200, default 50)
- `POST /admin/users`: Body: `UserCreateAdminIn`
- `GET /admin/users/{user_id}`: Path: `user_id` (integer)
- `PATCH /admin/users/{user_id}`: Path: `user_id` (integer), Body: `UserUpdateAdminIn`

***

### **Public User Profile (Tag: `users`)**

| **HTTP Method** | **Endpoint** | **Purpose** |
|---|---|---|
| GET | `/users/{username}` | Get public user profile by username |

**Parameters:**
- Path: `username` (string)

***

### **Classical Hierarchy — Public Access (Tag: `authors`)**

| **HTTP Method** | **Endpoint** | **Purpose** |
|---|---|---|
| GET | `/authors` | List all authors |
| GET | `/authors/{author_slug}` | Get single author details |
| GET | `/authors/{author_slug}/works` | List works under an author |
| GET | `/authors/{author_slug}/works/{work_slug}` | Get single work details |
| GET | `/authors/{author_slug}/works/{work_slug}/chapters` | List chapters in a work |

**Parameters:**
- `GET /authors`: Query: `q` (optional string, search in name), `language` (optional string), `offset` (int ≥0, default 0), `limit` (int 1-100, default 20)
- `GET /authors/{author_slug}`: Path: `author_slug` (string)
- `GET /authors/{author_slug}/works`: Path: `author_slug`, Query: `work_type` (optional string), `offset` (≥0, default 0), `limit` (1-200, default 50)
- `GET /authors/{author_slug}/works/{work_slug}`: Path: `author_slug`, `work_slug`
- `GET /authors/{author_slug}/works/{work_slug}/chapters`: Path: `author_slug`, `work_slug`, Query: `offset` (≥0, default 0), `limit` (1-500, default 200)

***

### **Admin Hierarchy Management (Tag: `admin-hierarchy`)**

| **HTTP Method** | **Endpoint** | **Purpose** |
|---|---|---|
| POST | `/admin/hierarchy/authors` | Create new author |
| PATCH | `/admin/hierarchy/authors/{author_id}` | Update author |
| POST | `/admin/hierarchy/authors/{author_id}/works` | Create work under author |
| PATCH | `/admin/hierarchy/works/{work_id}` | Update work |
| POST | `/admin/hierarchy/works/{work_id}/chapters` | Create chapter under work |
| PATCH | `/admin/hierarchy/chapters/{chapter_id}` | Update chapter |

**Parameters:**
- `POST /admin/hierarchy/authors`: Body: `AuthorCreateIn` (slug, name, short_bio, long_bio, language)
- `PATCH /admin/hierarchy/authors/{author_id}`: Path: `author_id` (int), Body: `AuthorUpdateIn`
- `POST /admin/hierarchy/authors/{author_id}/works`: Path: `author_id`, Body: `WorkCreateIn` (slug, title, description, work_type, original_script)
- `PATCH /admin/hierarchy/works/{work_id}`: Path: `work_id`, Body: `WorkUpdateIn`
- `POST /admin/hierarchy/works/{work_id}/chapters`: Path: `work_id`, Body: `ChapterCreateIn` (slug, title, number)
- `PATCH /admin/hierarchy/chapters/{chapter_id}`: Path: `chapter_id`, Body: `ChapterUpdateIn`

***

### **User Submissions (Tag: `submissions`)**

| **HTTP Method** | **Endpoint** | **Purpose** |
|---|---|---|
| POST | `/submissions` | Create new content submission |
| GET | `/submissions/me` | List current user's submissions |
| GET | `/submissions/{submission_id}` | Get single submission details |
| PUT | `/submissions/{submission_id}` | Update submission |
| DELETE | `/submissions/{submission_id}` | Soft delete submission |

**Parameters:**
- `POST /submissions`: Body: `SubmissionCreateIn` (content_type, main_text, meaning, is_classical, author_slug, work_slug, chapter_slug, number_in_chapter, references)
- `GET /submissions/me`: Query: `status` (optional string), `content_type` (optional string), `offset` (≥0, default 0), `limit` (1-200, default 50)
- `GET /submissions/{submission_id}`: Path: `submission_id` (int)
- `PUT /submissions/{submission_id}`: Path: `submission_id`, Body: `SubmissionUpdateIn`
- `DELETE /submissions/{submission_id}`: Path: `submission_id`

***

### **Moderation (Tag: `moderation`)**

| **HTTP Method** | **Endpoint** | **Purpose** |
|---|---|---|
| GET | `/moderation/submissions` | List pending submissions (moderation queue) |
| GET | `/moderation/submissions/{submission_id}` | Get submission for moderation |
| POST | `/moderation/submissions/{submission_id}/approve` | Approve submission |
| POST | `/moderation/submissions/{submission_id}/reject` | Reject submission |
| POST | `/moderation/batch` | Batch assign/moderate submissions |
| POST | `/moderation/batch_approve` | Batch approve multiple submissions (Admin only) |

**Parameters:**
- `GET /moderation/submissions`: Query: `assigned_to_me` (boolean, default false), `unassigned_only` (boolean, default false), `offset` (≥0, default 0), `limit` (1-200, default 50)
- `GET /moderation/submissions/{submission_id}`: Path: `submission_id` (int)
- `POST /moderation/submissions/{submission_id}/approve`: Path: `submission_id`, Body: `ModerationActionIn` (note, guideline_version)
- `POST /moderation/submissions/{submission_id}/reject`: Path: `submission_id`, Body: `ModerationActionIn`
- `POST /moderation/batch`: Body: `ModerationBatchIn` (submission_ids, action)
- `POST /moderation/batch_approve`: Body: `BatchApproveIn` (submission_ids array)

***

### **Canonical Content — Doha (Tag: `content`)**

| **HTTP Method** | **Endpoint** | **Purpose** |
|---|---|---|
| GET | `/content/doha` | List doha entries |
| GET | `/content/doha/{doha_id}` | Get single doha |
| GET | `/content/doha/{doha_id}/history` | Get version history of doha |
| GET | `/content/by-path/{hierarchy_path}` | Get doha by hierarchy path (e.g., author/work/chapter/number) |

**Parameters:**
- `GET /content/doha`: Query: `offset` (≥0, default 0), `limit` (1-200, default 50)
- `GET /content/doha/{doha_id}`: Path: `doha_id` (int)
- `GET /content/doha/{doha_id}/history`: Path: `doha_id`
- `GET /content/by-path/{hierarchy_path}`: Path: `hierarchy_path` (string, e.g., `kabir/bijak/chapter-1/1`)

***

### **Dictionary (Tag: `dictionary`)**

| **HTTP Method** | **Endpoint** | **Purpose** |
|---|---|---|
| GET | `/dictionary` | Search dictionary entries |
| GET | `/dictionary/{entry_id}` | Get single dictionary entry with full details |

**Parameters:**
- `GET /dictionary`: Query: `q` (required string, min length 1), `offset` (int, default 0), `limit` (int, default 20)
- `GET /dictionary/{entry_id}`: Path: `entry_id` (int)

**Use Cases:**
- Search by Devanagari or Roman lemma
- Exact match or partial match via normalized Roman
- Increments `search_hits_count` in `engagement_kpis`

***

### **Idioms (Tag: `idioms`)**

| **HTTP Method** | **Endpoint** | **Purpose** |
|---|---|---|
| GET | `/idioms` | Search idiom entries |
| GET | `/idioms/{idiom_id}` | Get single idiom entry |

**Parameters:**
- `GET /idioms`: Query: `q` (required string, min length 1), `offset` (int, default 0), `limit` (int, default 20)
- `GET /idioms/{idiom_id}`: Path: `idiom_id` (int)

**Use Cases:**
- Search by Devanagari or normalized Roman text
- Increments `search_hits_count` on search, `views_count` on detail view

***

### **Articles (Tag: `articles`)**

| **HTTP Method** | **Endpoint** | **Purpose** |
|---|---|---|
| GET | `/articles` | List articles (public visibility) |
| GET | `/articles/stats` | Get article statistics (total count, tag distribution, recent count) |
| GET | `/articles/search/advanced` | Advanced search with multiple filters |
| GET | `/articles/{article_id}` | Get single article details |
| GET | `/articles/by-tag/{tag}` | Get articles by specific tag |
| GET | `/articles/recent/list` | Get recently published articles |
| GET | `/articles/tags/list` | List all unique tags |

**Parameters:**
- `GET /articles`: Query: `q` (optional string, search title/body), `tag` (optional string), `offset` (≥0, default 0), `limit` (1-100, default 25)
- `GET /articles/stats`: No parameters
- `GET /articles/search/advanced`: Query: `title` (optional), `body` (optional), `tag` (optional), `offset` (≥0, default 0), `limit` (1-100, default 25)
- `GET /articles/{article_id}`: Path: `article_id` (int)
- `GET /articles/by-tag/{tag}`: Path: `tag` (string), Query: `offset` (≥0, default 0), `limit` (1-100, default 25)
- `GET /articles/recent/list`: Query: `days` (int 1-365, default 30), `limit` (1-50, default 10)
- `GET /articles/tags/list`: No parameters

***

### **Search (Tag: `search`)**

| **HTTP Method** | **Endpoint** | **Purpose** |
|---|---|---|
| GET | `/search` | Global search across doha content |

**Parameters:**
- Query: `q` (optional string, search query), `author` (optional string, author slug), `work` (optional string, work slug), `chapter` (optional string, chapter slug), `sort` (string, enum: 'relevance'|'recent', default 'relevance'), `limit` (1-200, default 20), `offset` (≥0, default 0)

**Use Cases:**
- Full-text search on doha_entries
- Filter by hierarchy (author, work, chapter)
- Sort by relevance (MySQL MATCH AGAINST) or recent (created_at DESC)

***

### **Analytics (Tag: `analytics`)**

| **HTTP Method** | **Endpoint** | **Purpose** |
|---|---|---|
| GET | `/analytics/top` | Get top performing content by engagement score |
| GET | `/analytics/growth` | Get daily content creation and user registration trends |
| GET | `/analytics/demand` | Get search demand distribution across content types |

**Parameters:**
- `GET /analytics/top`: Query: `content_type` (optional string, enum: doha|dictionary|idiom|article), `limit` (1-100, default 20), `start_date` (optional ISO string, default 30 days ago), `end_date` (optional ISO string, default now)
- `GET /analytics/growth`: Query: `start_date` (optional ISO string), `end_date` (optional ISO string)
- `GET /analytics/demand`: No parameters

**Use Cases:**
- Admin dashboard — trending content widget
- Growth charts — content creation over time
- Demand heatmap — which content types are searched most

***

### **Recommendations (Tag: `recommendations`)**

| **HTTP Method** | **Endpoint** | **Purpose** |
|---|---|---|
| GET | `/recommendations/{content_type}/{content_id}` | Get related content recommendations |

**Parameters:**
- Path: `content_type` (string, enum: doha|dictionary|idiom|article), `content_id` (int)
- Query: `limit` (1-50, default 5)

**Use Cases:**
- "Related Dohas" widget on doha detail page
- "Similar Words" on dictionary page
- Algorithm: Same author/work, similar tags, or high engagement content

***

### **User Interactions (Tag: `interactions`)**

| **HTTP Method** | **Endpoint** | **Purpose** |
|---|---|---|
| POST | `/interactions/toggle` | Toggle like/bookmark for content |
| POST | `/interactions/share` | Record share event |
| POST | `/interactions/report` | Report content |
| GET | `/interactions/users/{user_id}/bookmarks` | List user's bookmarks |

**Parameters:**
- `POST /interactions/toggle`: Body: `ToggleIn` (content_type, content_id, interaction_type: 'like'|'bookmark')
- `POST /interactions/share`: Body: `ShareIn` (content_type, content_id, metadata: JSON with channel info)
- `POST /interactions/report`: Body: `ReportIn` (content_type, content_id, reason, note)
- `GET /interactions/users/{user_id}/bookmarks`: Path: `user_id` (int), Query: `offset` (≥0, default 0), `limit` (1-200, default 50)

**Use Cases:**
- Bookmark button on every content card
- Share button → triggers social share modal, logs event
- Report content → moderator review queue

***

### **Admin Settings (Tag: `admin-system-settings`)**

| **HTTP Method** | **Endpoint** | **Purpose** |
|---|---|---|
| GET | `/admin/system_settings` | List all system settings |
| GET | `/admin/system_settings/{key}` | Get single setting by key |
| PUT | `/admin/system_settings/{key}` | Create or update setting |
| DELETE | `/admin/system_settings/{key}` | Delete setting |

**Parameters:**
- `GET /admin/system_settings`: No parameters
- `GET /admin/system_settings/{key}`: Path: `key` (string)
- `PUT /admin/system_settings/{key}`: Path: `key`, Body: `{"value": <any_json>}`
- `DELETE /admin/system_settings/{key}`: Path: `key`

**Use Cases:**
- Feature flags (e.g., `feature:recommendations_enabled`)
- Rate limits (e.g., `rate_limit:search:per_minute`)
- Banner messages, maintenance mode

***

### **Audit Logs (Tag: `admin-audit`)**

| **HTTP Method** | **Endpoint** | **Purpose** |
|---|---|---|
| GET | `/admin/audit_logs` | List audit logs with filters |
| GET | `/admin/audit_logs/export/csv` | Export audit logs as CSV |
| GET | `/admin/audit_logs/{id}` | Get single audit log entry |

**Parameters:**
- `GET /admin/audit_logs`: Query: `action` (optional string), `resource_type` (optional string), `actor_user_id` (optional int), `start` (optional ISO date), `end` (optional ISO date), `offset` (≥0, default 0), `limit` (1-1000, default 100)
- `GET /admin/audit_logs/export/csv`: Query: Same as above
- `GET /admin/audit_logs/{id}`: Path: `id` (int)

**Use Cases:**
- Compliance dashboard
- User activity tracking
- Forensic analysis after security incident

***

### **Health Check**

| **HTTP Method** | **Endpoint** | **Purpose** |
|---|---|---|
| GET | `/health` | Service health check (returns `{"status": "ok"}`) |

***

## **1.3 KEY VARIABLES & CONFIGURATION SETTINGS**

From `app/core/settings.py` (inferred from context):
- `settings.mysql_url` — MySQL database connection string
- `settings.APP_DEBUG` — Debug mode boolean
- Google OAuth settings: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI`
- JWT secret keys: `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `REFRESH_TOKEN_EXPIRE_DAYS`

***

## **1.4 ENUMERATIONS & CHOICE PARAMETERS**

### **Content Types (Universal)**
- `doha`, `dictionary`, `idiom`, `article`

### **Submission Status**
- `draft`, `pending_review`, `approved`, `rejected`

### **Visibility**
- `private`, `public`

### **User Roles**
- `registered` (default), `contributor`, `moderator`, `admin`

### **Interaction Types**
- `like`, `bookmark`

### **Report Reasons**
- `spam`, `abuse`, `copyright`, `other`

### **Report Status**
- `open`, `resolved`, `rejected`

### **Sort Options (Search)**
- `relevance`, `recent`

### **Analytics Content Type Filter**
- `doha`, `dictionary`, `idiom`, `article`

***
***
---





# **PART 2: THE MASTER ARCHITECTURE & IMPLEMENTATION PLAN**

***

## **2.1 ARCHITECTURE & RENDERING STRATEGY**

### **2.1.1 Hybrid Rendering Decision Matrix**

Your backend contains **tens of thousands of canonical entries** across four content types. The rendering strategy must balance **SEO discoverability** with **build performance** and **server costs**. Here's the exact breakdown:

#### **Static Site Generation (SSG) — Priority Routes**

**When to Use:** Content that is stable, critical for SEO, and doesn't change frequently.

**Routes for SSG:**
1. **Landing Page** (`/`)
   - Fully static HTML
   - Preload featured dohas, trending content widgets
   - Above-the-fold content baked into HTML
   - Metadata: Site-wide OpenGraph, canonical URL

2. **Authors Index** (`/authors`)
   - Static page with alphabetical author list (A-Z navigation)
   - Preload first 100 authors server-side
   - Lazy load remaining authors via client-side fetch on scroll
   - Metadata: "Browse Classical Authors | Awadhi Corpus"

3. **Individual Author Pages** (`/authors/{author_slug}`)
   - **Critical for SEO** — Each author is a landing page
   - Pregenerate during build: Query `classical_authors` table, iterate all `slug` values
   - Metadata: Author name, short_bio as meta description
   - Structured Data: JSON-LD Person schema

4. **Individual Work Pages** (`/authors/{author_slug}/works/{work_slug}`)
   - Static generation for top 500 most-viewed works (query `engagement_kpis` WHERE `content_type='doha'` ORDER BY `weight_score` DESC LIMIT 500)
   - Fallback: Server-Side Render (SSR) for long-tail works
   - Metadata: Work title, author name, description
   - Structured Data: JSON-LD CreativeWork schema

5. **Chapter List Pages** (`/authors/{author_slug}/works/{work_slug}/chapters`)
   - SSG for top 200 works only
   - Metadata: Work title + "Chapters"
   - Canonical URL to avoid duplicate content

6. **Static Content Pages**
   - About Us, Privacy Policy, Terms of Service, Guidelines
   - Contact, FAQ, How to Contribute
   - Fully static, no dynamic data

**Build Strategy for SSG:**
- Use Astro's `getStaticPaths()` to generate paths at build time
- Query FastAPI endpoints during build (e.g., `GET /authors?limit=1000`)
- Store generated paths in a sitemap index
- Incremental Static Regeneration (ISR) — Rebuild changed pages only when data updates (trigger via webhook from FastAPI admin panel)

***

#### **Server-Side Rendering (SSR) — Dynamic Routes**

**When to Use:** Content that is personalized, frequently updated, or has infinite variations.

**Routes for SSR:**

1. **Doha Detail Pages** (`/doha/{doha_id}` or `/doha/by-path/{hierarchy_path}`)
   - **50,000+ dohas** — SSG is impractical for all
   - SSR ensures fresh content for new submissions approved by moderators
   - Fetch from `/content/doha/{doha_id}` or `/content/by-path/{hierarchy_path}`
   - Metadata: `main_text` (first 100 chars) as description, `text_devanagari` in OpenGraph image
   - Structured Data: JSON-LD Article schema with `author`, `datePublished`, `inLanguage`

2. **Dictionary Entry Pages** (`/dictionary/{entry_id}`)
   - SSR for all entries
   - Fetch from `/dictionary/{entry_id}`
   - Metadata: `lemma_devanagari` + `lemma_roman` in title, first sense definition as description
   - Structured Data: JSON-LD DefinedTerm schema

3. **Idiom Entry Pages** (`/idioms/{idiom_id}`)
   - SSR for all entries
   - Metadata: `text_devanagari` in title, `meaning` as description
   - Structured Data: JSON-LD Article schema with `genre: "idiom"`

4. **Article Detail Pages** (`/articles/{article_id}`)
   - SSR for all articles
   - Fetch from `/articles/{article_id}`
   - Metadata: `title`, `excerpt` as description, `tags` as keywords
   - Structured Data: JSON-LD Article schema with `author`, `datePublished`, `keywords`

5. **Search Results Page** (`/search`)
   - SSR (query params: `?q=...&author=...&work=...`)
   - Fetch from `/search?q=...&limit=20&offset=0`
   - Metadata: Dynamic title based on query (e.g., "Search results for 'प्रेम'")
   - No indexing (add `<meta name="robots" content="noindex">` to avoid duplicate content issues)

6. **User Profile Pages** (`/users/{username}`)
   - SSR for public profiles
   - Fetch from `/users/{username}`
   - Metadata: Username, bio (if available)
   - No indexing for privacy (add robots noindex)

7. **Authenticated Pages**
   - User Dashboard (`/dashboard`)
   - My Submissions (`/submissions`)
   - Bookmarks (`/bookmarks`)
   - Admin Panel routes (`/admin/*`)
   - **All Client-Side Rendered (CSR)** with authentication guards

***

#### **Client-Side Rendering (CSR) — Interactive Features**

**When to Use:** Features requiring user authentication, real-time updates, or heavy client-side state.

**Routes for CSR:**
1. **User Dashboard** (`/dashboard`)
   - Svelte component fetches `/auth/me`, `/submissions/me`, `/interactions/users/{user_id}/bookmarks`
   - Displays submission history, bookmarks grid, contribution stats

2. **Admin Panel** (`/admin/*`)
   - Entire admin section is CSR with route guards
   - Moderation queue: `/admin/moderation` (fetches `/moderation/submissions`)
   - User management: `/admin/users` (fetches `/admin/users`)
   - Analytics dashboard: `/admin/analytics` (fetches `/analytics/top`, `/analytics/growth`, `/analytics/demand`)
   - System settings: `/admin/settings` (fetches `/admin/system_settings`)
   - Audit logs: `/admin/audit` (fetches `/admin/audit_logs`)

3. **Submission Form** (`/submit`)
   - Dynamic form with conditional fields based on `content_type` selection
   - Client-side validation before POST to `/submissions`
   - Autocomplete for `author_slug`, `work_slug`, `chapter_slug` (fetches `/authors`, `/authors/{slug}/works`, etc.)

4. **Moderation Interface** (`/admin/moderate/{submission_id}`)
   - Side-by-side view: submission content vs. canonical content (if exists)
   - Approve/Reject buttons → POST to `/moderation/submissions/{submission_id}/approve` or `/reject`
   - Batch approve checkbox selection → POST to `/moderation/batch_approve`

***


## 2. Data Fetching Layer (Astro + Svelte + FastAPI)

### 2.1.1 Never Let UI Talk to DB Concepts

Frontend should **never think in tables**.
It should think in **documents**.

Your API already supports this well.

---

### 2.1.2 Data Fetching Pattern

You will use **three layers**:

#### 1️⃣ Page Loader (Astro frontmatter)

* Fetches canonical document data
* Used for SEO HTML
* Uses FastAPI endpoints directly

#### 2️⃣ Svelte Islands

* Enhance interactivity (tabs, bookmarks, copy, toggle scripts)
* Consume already-fetched data
* Or call APIs for user actions

#### 3️⃣ Client Fetch (Auth-Only)

* Admin analytics
* User interactions
* Search autosuggest

---

### 2.1.3 Mapping Backend Endpoints to Frontend Pages

Examples:

| Frontend Page     | Backend Endpoint            |
| ----------------- | --------------------------- |
| Dictionary Entry  | `GET /dictionary/{id}`      |
| Dictionary Search | `GET /dictionary?q=`        |
| Idiom Entry       | `GET /idioms/{id}`          |
| Article Page      | `GET /articles/{id}`        |
| Author Page       | `GET /authors/{slug}`       |
| Author Works      | `GET /authors/{slug}/works` |

This mapping must be **one-to-one** to avoid abstraction rot.

---


## **2.2 "BRUTAL" SEO STRATEGY**

### **2.2.1 Programmatic SEO — Generating 50,000+ Landing Pages**

**Challenge:** You have **50,000+ dohas**, **10,000+ dictionary entries**, **5,000+ idioms**, and **1,000+ articles**. Building all at once is impractical.

**Solution: Tiered Indexing Strategy**

#### **Tier 1: Priority Content (SSG at Build Time)**
- Top 500 most-viewed dohas (query `engagement_kpis` WHERE `content_type='doha'` ORDER BY `weight_score` DESC)
- All authors (likely < 200 authors)
- Top 500 works
- All dictionary browse pages by letter (26 pages for A-Z)
- Top 100 articles by engagement

**Build Command:**
- Fetch priority IDs from analytics endpoint at build time
- Pass to `getStaticPaths()` in respective page files
- Build time: ~5-10 minutes for 1,000-2,000 pages

#### **Tier 2: On-Demand SSR with CDN Caching**
- All remaining content (45,000+ dohas, etc.)
- First request: SSR generates HTML, caches at CDN (Cloudflare/Vercel Edge)
- Subsequent requests: Served from CDN cache (sub-50ms response time)
- Cache invalidation: Webhook from FastAPI triggers purge when content updates

#### **Tier 3: Dynamic Sitemap Generation**
- Generate sitemap index file pointing to multiple sub-sitemaps:
  - `/sitemap-authors.xml` (all authors)
  - `/sitemap-dohas-1.xml` (dohas 1-10,000)
  - `/sitemap-dohas-2.xml` (dohas 10,001-20,000)
  - `/sitemap-dictionary.xml` (all dictionary entries)
  - `/sitemap-idioms.xml` (all idioms)
  - `/sitemap-articles.xml` (all articles)
- Sub-sitemaps dynamically generated via SSR endpoint
- Fetch content IDs from database at request time
- Cache sitemaps for 24 hours
- Submit sitemap index to Google Search Console

**Sitemap Endpoint Structure:**
- `/api/sitemap/index.xml` → Sitemap index file
- `/api/sitemap/dohas.xml?page=1` → Paginated doha sitemap (10,000 URLs per page)
- Include `<lastmod>` from `updated_at` column for each entry
- Include `<priority>` based on `weight_score` from `engagement_kpis`

***

### **2.2.2 Canonicalization & Duplicate Content Strategy**

**Problem:** Same doha accessible via multiple URLs:
- `/doha/12345`
- `/doha/by-path/kabir/bijak/chapter-1/5`

**Solution:**
- Choose **one canonical URL** per doha (recommend: by-path for better UX)
- On `/doha/{id}` pages, add `<link rel="canonical" href="/doha/by-path/{hierarchy_path}">` in `<head>`
- On `/doha/by-path/{path}` pages, self-referential canonical tag

**Dictionary/Idiom Canonicalization:**
- Dictionary entries: `/dictionary/{id}` as canonical
- Optional: Add slug-based URLs later (`/dictionary/word/{lemma_roman_norm}`) but canonical back to ID-based URL

**Article Canonicalization:**
- `/articles/{id}` as canonical
- Tag pages (`/articles/tag/{tag}`) → `rel="noindex,follow"` to avoid thin content penalty

***

### **2.2.3 Dynamic Metadata Generation**

**Meta Tag Requirements for Each Content Type:**

#### **Doha Detail Page** (`/doha/by-path/{path}`)
```
<title>{main_text_first_50_chars} | {author_name} | Awadhi Corpus</title>
<meta name="description" content="{meaning_first_160_chars}">
<meta name="keywords" content="{author_name}, {work_title}, doha, awadhi poetry">
<link rel="canonical" href="https://awadhicorpus.org/doha/by-path/{hierarchy_path}">

<!-- OpenGraph -->
<meta property="og:type" content="article">
<meta property="og:title" content="{main_text}">
<meta property="og:description" content="{meaning}">
<meta property="og:url" content="https://awadhicorpus.org/doha/by-path/{hierarchy_path}">
<meta property="og:image" content="https://awadhicorpus.org/og-images/doha/{doha_id}.png">
<meta property="article:author" content="{author_name}">
<meta property="article:published_time" content="{created_at_iso}">

<!-- Twitter Card -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{main_text}">
<meta name="twitter:description" content="{meaning}">
<meta name="twitter:image" content="https://awadhicorpus.org/og-images/doha/{doha_id}.png">
```

**OpenGraph Image Generation Strategy:**
- Use serverless function (Vercel OG Image / Cloudflare Workers) to generate dynamic images
- Template: Devanagari text overlaid on cultural background (manuscript texture)
- Endpoint: `/api/og-image/doha/{doha_id}.png`
- Cache indefinitely (content rarely changes)

#### **Dictionary Entry Page** (`/dictionary/{id}`)
```
<title>{lemma_devanagari} ({lemma_roman}) - Meaning, Definition | Awadhi Dictionary</title>
<meta name="description" content="{lemma_devanagari}: {first_sense_definition}">
<meta name="keywords" content="{lemma_roman}, {language}, awadhi dictionary, hindi dictionary">
<link rel="canonical" href="https://awadhicorpus.org/dictionary/{id}">

<!-- Structured Data: DefinedTerm -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "DefinedTerm",
  "name": "{lemma_devanagari}",
  "alternateName": "{lemma_roman}",
  "inDefinedTermSet": "Awadhi Dictionary",
  "description": "{first_sense_definition}",
  "inLanguage": "{language}"
}
</script>
```

#### **Article Page** (`/articles/{id}`)
```
<title>{title} | Awadhi Corpus</title>
<meta name="description" content="{excerpt}">
<meta name="keywords" content="{tags_comma_separated}">
<link rel="canonical" href="https://awadhicorpus.org/articles/{id}">

<!-- Structured Data: Article -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "{title}",
  "description": "{excerpt}",
  "author": {
    "@type": "Person",
    "name": "{author_name}"
  },
  "datePublished": "{created_at_iso}",
  "dateModified": "{updated_at_iso}",
  "keywords": "{tags_comma_separated}",
  "inLanguage": "hi"
}
</script>
```

***

### **2.2.4 Structured Data (JSON-LD) Implementation**

**Schema.org Types Used:**

1. **Website** (on homepage)
   - `@type: "WebSite"`
   - Include `potentialAction: SearchAction` with `/search?q={search_term_string}` as target

2. **Person** (on author pages)
   - `@type: "Person"`
   - `name`, `description` (short_bio)
   - `sameAs` array if author has external links (Wikipedia, etc.)

3. **CreativeWork** (on work pages)
   - `@type: "CreativeWork"`
   - `name` (work title), `author` (Person schema), `inLanguage`

4. **Article** (on doha, idiom, and article pages)
   - `@type: "Article"`
   - `headline`, `author`, `datePublished`, `inLanguage`, `text` (main_text or body)

5. **DefinedTerm** (on dictionary entries)
   - `@type: "DefinedTerm"`
   - `name` (lemma), `inDefinedTermSet`, `description` (first sense)

6. **BreadcrumbList** (on all nested pages)
   - Example for `/doha/by-path/kabir/bijak/chapter-1/5`:
     - Home > Authors > Kabir > Bijak > Chapter 1 > Doha 5

**Implementation:**
- Create Svelte component `<StructuredData data={jsonLdObject} />`
- Component renders `<script type="application/ld+json">{JSON.stringify(data)}</script>`
- Import and use in Astro page layouts

***

### **2.2.5 Performance Optimization for SEO**

Google's Core Web Vitals are ranking factors. Target metrics:
- **Largest Contentful Paint (LCP):** < 2.5s
- **First Input Delay (FID):** < 100ms
- **Cumulative Layout Shift (CLS):** < 0.1

**Strategies:**

1. **Image Optimization:**
   - Use Astro's `<Image>` component for automatic optimization
   - Lazy load images below the fold
   - Generate WebP/AVIF formats with fallback to JPEG
   - For OpenGraph images, generate at build time and store in CDN

2. **Font Loading:**
   - Use `font-display: swap` for Devanagari fonts (e.g., Noto Sans Devanagari)
   - Preload critical font files: `<link rel="preload" href="/fonts/NotoSansDevanagari.woff2" as="font" type="font/woff2" crossorigin>`
   - Subset fonts to include only required glyphs (A-Z, Devanagari range)

3. **CSS Optimization:**
   - Extract critical CSS and inline in `<head>`
   - Defer non-critical CSS with `media="print" onload="this.media='all'"`
   - Use Tailwind CSS with PurgeCSS to remove unused styles

4. **JavaScript Optimization:**
   - Minimize JS bundles (Astro already does this)
   - Use `client:idle` for non-critical Svelte components (e.g., share button)
   - Use `client:visible` for below-fold widgets (e.g., recommendations)

5. **CDN & Caching:**
   - Deploy to Vercel/Netlify with global CDN
   - Cache static assets forever with hashed filenames
   - Cache HTML pages with stale-while-revalidate

6. **Server Response Time:**
   - FastAPI backend behind CDN (Cloudflare Workers or Vercel Edge Functions)
   - Database connection pooling (MySQL connector with max_connections=100)
   - Index optimization on frequently queried columns (already done in migrations)

***

## **2.3 UI/UX & REKHTA-STYLE AESTHETICS**

### **2.3.1 Design Philosophy**

**Inspiration: Rekhta.org**
- Text-heavy layout with ample whitespace
- Emphasis on readability over flashy graphics
- Cultural authenticity (manuscript textures, traditional patterns)
- Bilingual support (Hindi/Urdu/English)

**Your Modernization:**
- Cleaner typography (avoid cluttered sidebars)
- Responsive grid system (mobile-first)
- Dark mode support (reduce eye strain for long reading sessions)
- Accessibility compliance (WCAG 2.1 AA)

***

### **2.3.2 Component Breakdown**

#### **Layout Components**

1. **Header**
   - Logo (left)
   - Search bar (center, autofocus on `/`)
   - User menu (right: Login/Register or Profile dropdown)
   - Navigation menu (Authors, Dictionary, Idioms, Articles, Contribute)
   - Sticky on scroll

2. **Footer**
   - Links: About, Privacy, Terms, Contact, Guidelines
   - Social media icons (Twitter, Facebook, Instagram)
   - Language selector (Hindi/English)
   - Copyright notice

3. **Breadcrumb**
   - Used on all nested pages
   - Structured data integration (BreadcrumbList JSON-LD)

4. **Sidebar (optional, desktop only)**
   - "Popular Authors" widget (top 10 by engagement)
   - "Trending Dohas" widget (top 5 by recent views)
   - "Random Doha" button (fetches random doha from API)

***

#### **Content Components**

1. **DohaCard**
   - Props: `doha` object (id, main_text, meaning, author_name, work_title)
   - Layout: Devanagari text (large font, 24px), meaning below (16px), author/work metadata (12px, muted color)
   - Hover state: Subtle background change, "Read More" button appears
   - Click: Navigate to `/doha/by-path/{hierarchy_path}`

2. **DictionaryCard**
   - Props: `entry` object (id, lemma_devanagari, lemma_roman, first_sense)
   - Layout: Lemma in Devanagari (18px bold), Roman transliteration (14px, muted), definition excerpt (14px)
   - Click: Navigate to `/dictionary/{id}`

3. **IdiomCard**
   - Similar to DohaCard but emphasizes `text_devanagari` and `meaning`

4. **ArticleCard**
   - Props: `article` object (id, title, excerpt, tags, created_at)
   - Layout: Title (20px bold), excerpt (14px, 2 lines max with ellipsis), tags (badges), date (12px, muted)
   - Click: Navigate to `/articles/{id}`

5. **AuthorCard**
   - Props: `author` object (slug, name, short_bio, work_count)
   - Layout: Author name (18px bold), short bio (14px, 3 lines max), work count badge
   - Click: Navigate to `/authors/{slug}`

***

#### **Interactive Components**

1. **SearchBar**
   - Input with autocomplete suggestions (debounced API call to `/search?q=...&limit=5`)
   - Submit: Navigate to `/search?q=...`
   - Keyboard navigation: Arrow keys to select suggestion, Enter to submit

2. **FilterPanel**
   - Used on search/browse pages
   - Filters: Author, Work, Content Type, Language
   - Dropdowns populated from API (e.g., `/authors?limit=1000`)
   - Apply button updates URL query params

3. **PaginationControls**
   - Props: `currentPage`, `totalPages`, `onPageChange`
   - Displays: Previous, 1, 2, 3, ..., Last, Next
   - Updates URL query param `?page=...`

4. **InteractionButtons**
   - Like button (heart icon), Bookmark button (bookmark icon), Share button (share icon)
   - On click: POST to `/interactions/toggle` with content_type, content_id, interaction_type
   - Optimistic UI update: Toggle icon state immediately, revert on API error
   - Toast notification on success/error

5. **ReportModal**
   - Triggered by "Report" link on content pages
   - Form: Reason (dropdown), Note (textarea)
   - Submit: POST to `/interactions/report`
   - Close modal on success, show confirmation toast

***

#### **Admin Components**

1. **ModerationQueueTable**
   - Columns: ID, Content Type, Main Text (truncated), Contributor, Status, Actions
   - Actions: Approve button (green), Reject button (red), View Details link
   - Batch selection: Checkboxes, Bulk Approve button at top

2. **AnalyticsDashboard**
   - Widgets: Total Content Count, Total Users, Top Content (table), Growth Chart (line chart), Demand Chart (pie chart)
   - Fetch data from `/analytics/top`, `/analytics/growth`, `/analytics/demand`
   - Charts rendered with Chart.js or D3.js

3. **UserManagementTable**
   - Columns: ID, Username, Email, Role, Permissions, Actions
   - Actions: Edit (opens modal), Ban/Unban toggle
   - Search bar above table (filter by email/username)

4. **AuditLogViewer**
   - Table: ID, Actor, Action, Resource Type, Resource ID, Created At
   - Expandable rows: Click to view `before` and `after` JSON diffs
   - Export CSV button (triggers `/admin/audit_logs/export/csv`)

***

### **2.3.3 Typography & Whitespace Strategy**

**Fonts:**
- **Devanagari:** Noto Sans Devanagari (Google Fonts)
  - Weights: Regular (400), Medium (500), Bold (700)
  - Use Medium (500) for primary text to improve readability
- **Roman:** Inter or Open Sans
  - Weights: Regular (400), Semibold (600)
- **Monospace (code/logs):** JetBrains Mono

**Font Sizes:**
- H1 (page title): 36px (mobile), 48px (desktop)
- H2 (section heading): 28px (mobile), 36px (desktop)
- H3 (subsection): 22px (mobile), 28px (desktop)
- Body text: 16px (mobile), 18px (desktop)
- Metadata (dates, counts): 14px

**Line Height:**
- Devanagari text: 1.8 (extra spacing for diacritics)
- Roman text: 1.6

**Whitespace:**
- Vertical rhythm: 24px baseline grid
- Section padding: 48px top/bottom (desktop), 32px (mobile)
- Card margins: 16px between cards in grid
- Content max-width: 800px (for readability, centered on large screens)

**Color Palette:**
- Primary: Saffron (#FF9933) — for CTAs, active states
- Secondary: Dark Green (#138808) — for success states, approval buttons
- Background (light mode): Off-white (#FAFAFA)
- Background (dark mode): Dark grey (#1A1A1A)
- Text (light mode): Near-black (#2C2C2C)
- Text (dark mode): Off-white (#E0E0E0)
- Accent: Deep Red (#B71C1C) — for errors, reject buttons

***

## **2.4 THE "DATA SCIENTIST" ADMIN DASHBOARD**

### **2.4.1 Beyond CRUD — Analytics-First Design**

Standard admin panels show tables with Create/Edit/Delete buttons. Your admin panel should visualize **data insights** that help you make editorial decisions.

***

### **2.4.2 Dashboard Widgets**

#### **Widget 1: Content Overview Cards**
- Four cards in a row (desktop) or stacked (mobile)
- Card 1: Total Dohas (fetch count from database or cache)
- Card 2: Total Dictionary Entries
- Card 3: Total Idioms
- Card 4: Total Articles
- Each card shows:
  - Big number (e.g., "12,458")
  - Trend indicator: "+245 this month" (green up arrow) or "-12 this month" (red down arrow)
  - Sparkline chart (tiny line chart showing last 7 days)

**Data Source:** `/analytics/growth?start_date=...&end_date=...`

***

#### **Widget 2: Top Performing Content**
- Table with columns: Rank, Title/Text, Content Type, Views, Engagement Score
- Top 10 entries sorted by `weight_score` DESC
- Clicking a row navigates to content detail page

**Data Source:** `/analytics/top?limit=10`

**Use Case:** Identify which content drives traffic. Promote similar content.

***

#### **Widget 3: Search Gap Analysis**
- **Problem:** Users search for terms not in your database.
- **Solution:** Log failed search queries (where result count = 0).
- **Backend Enhancement Needed:** Add logging to `/search` endpoint when `len(results) == 0`:
  - Insert into new table `search_gaps` (query, timestamp, user_id, ip_address)
- **Widget Display:**
  - Table: Search Query, Frequency, Last Searched
  - Top 20 queries ordered by frequency DESC
  - "Add to Content Queue" button next to each query (creates a submission draft with the query as main_text)

**Data Source:** New endpoint `/admin/analytics/search-gaps?limit=20`

**Use Case:** Prioritize content creation based on user demand.

***

#### **Widget 4: Content Growth Chart**
- Line chart with 5 lines (one per content type: doha, dictionary, idiom, article, users)
- X-axis: Last 30 days
- Y-axis: Cumulative count

**Data Source:** `/analytics/growth?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`

**Use Case:** Visualize growth trajectory. Identify slow weeks (prompt moderators to approve more submissions).

***

#### **Widget 5: Engagement Heatmap**
- Heatmap showing engagement by content type and time of day
- Rows: Content types (doha, dictionary, idiom, article)
- Columns: Hours of day (0-23)
- Cell color intensity: Number of views/interactions in that hour

**Data Source:** New endpoint `/admin/analytics/engagement-heatmap`

**Backend Enhancement:** Query `engagement_kpis` joined with `doha_entries.created_at` (or other content tables), group by HOUR(created_at) and content_type.

**Use Case:** Optimize posting schedule. If dohas get most engagement at 9 AM, schedule moderation approvals for 8:30 AM.

***

#### **Widget 6: Contributor Leaderboard**
- Table: Rank, Username, Submissions (approved count), Accuracy (approved / total)
- Top 10 contributors by approved submission count

**Data Source:** Query `submissions` table:
  - Count WHERE `status='approved'` GROUP BY `contributor_id`
  - Join with `users` table to get username
  - Sort by count DESC

**Use Case:** Gamification. Recognize top contributors with badges. Offer incentives (e.g., "Contributor of the Month").

***

#### **Widget 7: Moderation Queue Stats**
- Three cards:
  - Card 1: Pending Submissions (count WHERE `status='pending_review'`)
  - Card 2: Average Review Time (time between `created_at` and moderation action timestamp)
  - Card 3: Moderator Activity (table: Moderator Name, Reviews This Week)

**Data Source:**
  - `/moderation/submissions?limit=1` (check count in response metadata)
  - Query `moderation_logs` table for average time between submission creation and moderation action

**Use Case:** Ensure moderation queue doesn't grow stale. Alert if average review time > 48 hours.

***

#### **Widget 8: API Latency Monitor**
- Table: Endpoint, P50 Latency, P95 Latency, Error Rate
- Top 10 slowest endpoints

**Backend Enhancement:** Instrument FastAPI with middleware to log request duration and errors. Store in `api_metrics` table or external service (e.g., Prometheus + Grafana).

**Widget Display:** Fetch from `/admin/analytics/api-latency`

**Use Case:** Identify performance bottlenecks. Optimize slow queries.

***

### **2.4.3 Admin Dashboard Layout**

**Top Section:**
- Date range selector (Last 7 days, Last 30 days, Custom range)
- Export buttons: Download CSV (all data), Generate Report (PDF)

**Main Content (scrollable):**
- Content Overview Cards (Widget 1)
- Growth Chart (Widget 4)
- Top Performing Content (Widget 2)
- Search Gap Analysis (Widget 3)
- Engagement Heatmap (Widget 5)
- Contributor Leaderboard (Widget 6)
- Moderation Queue Stats (Widget 7)
- API Latency Monitor (Widget 8)

**Sidebar (optional):**
- Quick links: Moderation Queue, User Management, System Settings, Audit Logs
- Notification bell: Unread reports, pending submissions count

***

## **2.5 AUTHENTICATION & SECURITY**

### **2.5.1 Google OAuth Integration**

**Flow:**
1. User clicks "Login with Google" button
2. Frontend redirects to `/auth/oauth/google/callback?code=...&state=...` (backend handles this)
3. Backend exchanges code for access token, fetches user profile, creates/updates user record
4. Backend generates JWT access + refresh tokens, returns to frontend
5. Frontend stores tokens in `httpOnly` cookie (secure flag in production)

**Frontend Implementation:**
- No OAuth library needed (backend handles everything)
- Just redirect to backend OAuth endpoint on button click

***

### **2.5.2 JWT Token Management**

**Access Token:**
- Lifetime: 15 minutes
- Stored in `httpOnly` cookie or `localStorage` (your choice — cookie is more secure)
- Sent in `Authorization: Bearer {token}` header on every API request

**Refresh Token:**
- Lifetime: 30 days
- Stored in `httpOnly` cookie only (never in `localStorage`)
- Used to obtain new access token when expired

**Token Refresh Strategy:**
- Interceptor in API client detects 401 response
- Automatically calls `/auth/refresh` with refresh token
- Retries original request with new access token
- If refresh fails (401), redirect to login page

***

### **2.5.3 Route Protection in Astro Middleware**

**Middleware File:** `/src/middleware/auth.ts`

**Logic:**
- Check for access token in cookies or `Authorization` header
- If missing, redirect to `/auth/login`
- If present, verify token signature (call `/auth/me` endpoint)
- If valid, proceed to route
- If invalid, redirect to `/auth/login`

**Protected Routes:**
- `/dashboard`, `/submit`, `/bookmarks`, `/admin/*`

**Implementation in Astro:**
- Use middleware to check authentication before rendering protected pages
- For SSR pages, check token server-side
- For CSR pages, check token in Svelte component's `onMount()` hook

***

### **2.5.4 Security Best Practices**

1. **CSRF Protection:**
   - Use SameSite cookies: `SameSite=Strict`
   - Add CSRF token to forms (backend validates)

2. **XSS Prevention:**
   - Sanitize user input before rendering (Astro does this by default for `{variable}` syntax)
   - Use Content Security Policy (CSP) headers: `Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.example.com;`

3. **Rate Limiting:**
   - Backend already has `rate_limit_counters` table
   - Enforce limits: 100 requests/minute per IP for public endpoints, 10 requests/minute for submission endpoint
   - Return 429 Too Many Requests if exceeded

4. **HTTPS Only:**
   - Redirect HTTP to HTTPS in production
   - Set Secure flag on cookies

5. **Input Validation:**
   - Validate all form inputs on frontend (immediate feedback)
   - Re-validate on backend (security)

***

## **2.6 THE "ANTI-FEATURE" SCOPE GUARD**

### **2.6.1 Features to AVOID (For Now)**

1. **Advanced Search Filters**
   - No faceted search (multiple filters combined with AND/OR logic)
   - Stick to simple search with optional author/work filters
   - Reason: Complexity. Advanced filters require complex UI and backend logic.

2. **User Comments/Discussions**
   - No comment section on content pages
   - Reason: Moderation burden. You'll spend more time moderating comments than content.

3. **Social Features**
   - No following users, no activity feed, no direct messages
   - Reason: Scope creep. Focus on content, not social networking.

4. **Recommendations Engine**
   - No machine learning-based recommendations
   - Simple rule-based recommendations only (same author, same work, high engagement)
   - Reason: ML requires training data, infrastructure, maintenance.

5. **Multi-Language UI**
   - No i18n framework (no translating entire UI to Hindi/Urdu)
   - Content can be bilingual (Devanagari + Roman), but UI in English only (for now)
   - Reason: Translation effort is massive. Focus on content first.

6. **Mobile App**
   - No native iOS/Android apps
   - Responsive web app only
   - Reason: App development doubles workload. PWA (Progressive Web App) is sufficient.

7. **Real-Time Features**
   - No WebSocket connections, no live updates
   - Polling is acceptable (e.g., refresh moderation queue every 30 seconds)
   - Reason: Complexity and infrastructure cost.

8. **Custom CMS**
   - No building a custom content editor
   - Use simple forms with markdown support (for articles)
   - Reason: CMS development is a project in itself.

***

### **2.6.2 Features to ADD (Later versions)**

Save these for Phase 2-3 after MVP launch:

1. **Doha Collections**
   - Users can create custom collections (e.g., "Dohas on Love," "Kabir's Best")
   - Like playlists for dohas

2. **Audio Recitations**
   - Upload audio files of dohas being recited
   - Attach to doha entries
   - Requires: Audio player component, file storage (S3), CDN

3. **Translation Variants**
   - Multiple translations of same doha in different languages
   - Requires: Variant management UI, translation submission workflow

4. **API for Developers**
   - Public API with rate limiting
   - Allow third-party apps to access your data
   - Requires: API key management, documentation site

5. **Contributor Dashboard**
   - Separate from admin panel
   - Shows contributor's stats: Total submissions, Approval rate, Badges earned
   - Requires: New endpoint, new UI page

***

