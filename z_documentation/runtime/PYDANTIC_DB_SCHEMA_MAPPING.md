# Pydantic to Database Schema Mapping

Generated from current code and live DB metadata.

## Database Tables

### alembic_version
Columns (1): version_num

### article_entries
Columns (15): author_id, body, contributor_id, created_at, excerpt, id, source_submission_id, tags, title, title_devanagari, title_roman, title_roman_norm, updated_at, version, visibility

### audit_logs
Columns (9): action, actor_user_id, after, audit_before, audit_metadata, created_at, id, resource_id, resource_type

### classical_authors
Columns (9): created_at, id, is_deleted, language, long_bio, name, short_bio, slug, updated_at

### classical_works
Columns (10): author_id, created_at, description, id, is_deleted, original_script, slug, title, updated_at, work_type

### content_versions
Columns (11): content_id, content_type, created_at, created_by, id, main_text, meaning, notes, text_devanagari, text_romanized, version_number

### dictionary_entries
Columns (18): author_id, chapter_id, contributor_id, created_at, examples, id, language, lemma_devanagari, lemma_roman, lemma_roman_norm, number_in_chapter, pronunciation, senses, source_submission_id, updated_at, version, visibility, work_id

### doha_entries
Columns (24): author_id, chapter_id, confidence_level, created_at, created_by, hierarchy_path, id, is_canonical, is_deleted, main_text, meaning, number_in_chapter, source_reference, source_submission_id, status, text_devanagari, text_romanized, updated_at, variant_group_id, verified_at, verified_by, version, visibility, work_id

### engagement_kpis
Columns (10): bookmarks_count, content_id, content_type, id, likes_count, search_hits_count, shares_count, updated_at, views_count, weight_score

### idiom_entries
Columns (17): author_id, chapter_id, contributor_id, created_at, examples, id, meaning, number_in_chapter, region, source_submission_id, text_devanagari, text_roman, text_roman_norm, updated_at, version, visibility, work_id

### moderation_guidelines
Columns (7): created_at, description, id, is_active, title, url, version

### moderation_logs
Columns (9): action, created_at, from_status, guideline_version, id, moderator_id, note, submission_id, to_status

### oauth_accounts
Columns (6): created_at, id, provider, provider_user_id, raw_profile, user_id

### rate_limit_counters
Columns (9): action_key, count, created_at, granularity, id, ip_address, time_bucket_start, updated_at, user_id

### refresh_tokens
Columns (5): created_at, expires_at, id, token, user_id

### reports
Columns (10): content_id, content_type, created_at, id, note, reason, report_metadata, status, updated_at, user_id

### share_logs
Columns (6): content_id, content_type, created_at, id, share_metadata, user_id

### submissions
Columns (20): assigned_moderator_id, author_slug, chapter_slug, content_type, contributor_id, created_at, external_references, id, is_classical, is_deleted, main_text, meaning, number_in_chapter, priority, references, status, updated_at, version, visibility, work_slug

### system_settings
Columns (4): created_at, setting_key, updated_at, value

### user_interactions
Columns (9): content_id, content_type, created_at, id, interaction_metadata, interaction_type, is_active, updated_at, user_id

### users
Columns (12): created_at, email, id, is_active, is_banned, last_login, password_hash, permission_scopes, permissions, role, updated_at, username

### work_chapters
Columns (8): created_at, id, is_deleted, number, slug, title, updated_at, work_id

## Pydantic Schemas

### SettingIn
Source: app/api/v1/admin_settings.py
Fields: value
Primary tables: system_settings
Field mapping:
- value -> system_settings.value

### SettingOut
Source: app/api/v1/admin_settings.py
Fields: key, value
Primary tables: system_settings
Field mapping:
- key -> system_settings.setting_key
- value -> system_settings.value

### UserCreateAdminIn
Source: app/api/v1/admin_users.py
Fields: email, username, password, role, permissions, permission_scopes, is_active, is_banned
Primary tables: users
Field mapping:
- email -> users.email
- username -> users.username
- password -> (derived/validated/non-column)
- role -> users.role
- permissions -> users.permissions
- permission_scopes -> users.permission_scopes
- is_active -> users.is_active
- is_banned -> users.is_banned

### UserOut
Source: app/api/v1/admin_users.py
Fields: id, email, username, role, permissions, is_active, is_banned
Primary tables: users
Field mapping:
- id -> users.id
- email -> users.email
- username -> users.username
- role -> users.role
- permissions -> users.permissions
- is_active -> users.is_active
- is_banned -> users.is_banned

### UserUpdateAdminIn
Source: app/api/v1/admin_users.py
Fields: role, permissions, permission_scopes, is_active, is_banned
Primary tables: users
Field mapping:
- role -> users.role
- permissions -> users.permissions
- permission_scopes -> users.permission_scopes
- is_active -> users.is_active
- is_banned -> users.is_banned

### DemandItem
Source: app/api/v1/analytics.py
Fields: count, percent
Primary tables: engagement_kpis
Field mapping:
- count -> (derived/validated/non-column)
- percent -> (derived/validated/non-column)

### GrowthSeries
Source: app/api/v1/analytics.py
Fields: dates, series
Primary tables: users, doha_entries, dictionary_entries, idiom_entries, article_entries
Field mapping:
- dates -> (derived/validated/non-column)
- series -> (derived/validated/non-column)

### TopContentItem
Source: app/api/v1/analytics.py
Fields: content_type, content_id, title_or_text, score, views, likes, search_hits
Primary tables: engagement_kpis
Field mapping:
- content_type -> engagement_kpis.content_type
- content_id -> engagement_kpis.content_id
- title_or_text -> (derived/validated/non-column)
- score -> (derived/validated/non-column)
- views -> (derived/validated/non-column)
- likes -> (derived/validated/non-column)
- search_hits -> (derived/validated/non-column)

### ArticleDetailOut
Source: app/api/v1/article.py
Fields: id, title, title_devanagari, title_roman, title_roman_norm, body, excerpt, author_id, tags, contributor_id, source_submission_id, visibility, version, created_at, updated_at
Primary tables: article_entries
Field mapping:
- id -> article_entries.id
- title -> article_entries.title
- title_devanagari -> article_entries.title_devanagari
- title_roman -> article_entries.title_roman
- title_roman_norm -> article_entries.title_roman_norm
- body -> article_entries.body
- excerpt -> article_entries.excerpt
- author_id -> article_entries.author_id
- tags -> article_entries.tags
- contributor_id -> article_entries.contributor_id
- source_submission_id -> article_entries.source_submission_id
- visibility -> article_entries.visibility
- version -> article_entries.version
- created_at -> article_entries.created_at
- updated_at -> article_entries.updated_at

### ArticleListOut
Source: app/api/v1/article.py
Fields: id, title, title_devanagari, title_roman, excerpt, tags, version, created_at
Primary tables: article_entries
Field mapping:
- id -> article_entries.id
- title -> article_entries.title
- title_devanagari -> article_entries.title_devanagari
- title_roman -> article_entries.title_roman
- excerpt -> article_entries.excerpt
- tags -> article_entries.tags
- version -> article_entries.version
- created_at -> article_entries.created_at

### ArticleStatsOut
Source: app/api/v1/article.py
Fields: total_articles, by_tag, recent_count
Primary tables: article_entries
Field mapping:
- total_articles -> (derived/validated/non-column)
- by_tag -> (derived/validated/non-column)
- recent_count -> (derived/validated/non-column)

### LoginIn
Source: app/api/v1/auth.py
Fields: email, password
Primary tables: users, refresh_tokens
Field mapping:
- email -> users.email
- password -> (derived/validated/non-column)

### LogoutIn
Source: app/api/v1/auth.py
Fields: refresh_token
Primary tables: refresh_tokens
Field mapping:
- refresh_token -> (derived/validated/non-column)

### RefreshIn
Source: app/api/v1/auth.py
Fields: refresh_token
Primary tables: refresh_tokens
Field mapping:
- refresh_token -> (derived/validated/non-column)

### RegisterIn
Source: app/api/v1/auth.py
Fields: email, password, username
Primary tables: users
Field mapping:
- email -> users.email
- password -> (derived/validated/non-column)
- username -> users.username

### ContentVersionOut
Source: app/api/v1/content.py
Fields: id, content_type, content_id, version_number, main_text, meaning, text_devanagari, text_romanized, created_by
Primary tables: content_versions
Field mapping:
- id -> content_versions.id
- content_type -> content_versions.content_type
- content_id -> content_versions.content_id
- version_number -> content_versions.version_number
- main_text -> content_versions.main_text
- meaning -> content_versions.meaning
- text_devanagari -> content_versions.text_devanagari
- text_romanized -> content_versions.text_romanized
- created_by -> content_versions.created_by

### DohaOut
Source: app/api/v1/content.py
Fields: id, hierarchy_path, author_id, work_id, chapter_id, number_in_chapter, main_text, meaning, text_devanagari, text_romanized, status, visibility, version, is_canonical, confidence_level
Primary tables: doha_entries
Field mapping:
- id -> doha_entries.id
- hierarchy_path -> doha_entries.hierarchy_path
- author_id -> doha_entries.author_id
- work_id -> doha_entries.work_id
- chapter_id -> doha_entries.chapter_id
- number_in_chapter -> doha_entries.number_in_chapter
- main_text -> doha_entries.main_text
- meaning -> doha_entries.meaning
- text_devanagari -> doha_entries.text_devanagari
- text_romanized -> doha_entries.text_romanized
- status -> doha_entries.status
- visibility -> doha_entries.visibility
- version -> doha_entries.version
- is_canonical -> doha_entries.is_canonical
- confidence_level -> doha_entries.confidence_level

### DictionaryOut
Source: app/api/v1/dictionary.py
Fields: id, lemma_devanagari, lemma_roman, language, version
Primary tables: dictionary_entries
Field mapping:
- id -> dictionary_entries.id
- lemma_devanagari -> dictionary_entries.lemma_devanagari
- lemma_roman -> dictionary_entries.lemma_roman
- language -> dictionary_entries.language
- version -> dictionary_entries.version

### AuthorCreateIn
Source: app/api/v1/hierarchy_admin.py
Fields: slug, name, short_bio, long_bio, language
Primary tables: classical_authors
Field mapping:
- slug -> classical_authors.slug
- name -> classical_authors.name
- short_bio -> classical_authors.short_bio
- long_bio -> classical_authors.long_bio
- language -> classical_authors.language

### AuthorUpdateIn
Source: app/api/v1/hierarchy_admin.py
Fields: name, short_bio, long_bio, language, is_deleted
Primary tables: classical_authors
Field mapping:
- name -> classical_authors.name
- short_bio -> classical_authors.short_bio
- long_bio -> classical_authors.long_bio
- language -> classical_authors.language
- is_deleted -> classical_authors.is_deleted

### ChapterCreateIn
Source: app/api/v1/hierarchy_admin.py
Fields: slug, title, number
Primary tables: work_chapters
Field mapping:
- slug -> work_chapters.slug
- title -> work_chapters.title
- number -> work_chapters.number

### ChapterUpdateIn
Source: app/api/v1/hierarchy_admin.py
Fields: title, number, is_deleted
Primary tables: work_chapters
Field mapping:
- title -> work_chapters.title
- number -> work_chapters.number
- is_deleted -> work_chapters.is_deleted

### WorkCreateIn
Source: app/api/v1/hierarchy_admin.py
Fields: slug, title, description, work_type, original_script
Primary tables: classical_works
Field mapping:
- slug -> classical_works.slug
- title -> classical_works.title
- description -> classical_works.description
- work_type -> classical_works.work_type
- original_script -> classical_works.original_script

### WorkUpdateIn
Source: app/api/v1/hierarchy_admin.py
Fields: title, description, work_type, original_script, is_deleted
Primary tables: classical_works
Field mapping:
- title -> classical_works.title
- description -> classical_works.description
- work_type -> classical_works.work_type
- original_script -> classical_works.original_script
- is_deleted -> classical_works.is_deleted

### AuthorDetailOut
Source: app/api/v1/hierarchy_public.py
Fields: id, slug, name, short_bio, long_bio, language
Primary tables: classical_authors
Field mapping:
- id -> classical_authors.id
- slug -> classical_authors.slug
- name -> classical_authors.name
- short_bio -> classical_authors.short_bio
- long_bio -> classical_authors.long_bio
- language -> classical_authors.language

### AuthorListOut
Source: app/api/v1/hierarchy_public.py
Fields: id, slug, name, short_bio, language
Primary tables: classical_authors
Field mapping:
- id -> classical_authors.id
- slug -> classical_authors.slug
- name -> classical_authors.name
- short_bio -> classical_authors.short_bio
- language -> classical_authors.language

### ChapterOut
Source: app/api/v1/hierarchy_public.py
Fields: id, slug, title, number
Primary tables: work_chapters
Field mapping:
- id -> work_chapters.id
- slug -> work_chapters.slug
- title -> work_chapters.title
- number -> work_chapters.number

### WorkOut
Source: app/api/v1/hierarchy_public.py
Fields: id, slug, title, description, work_type
Primary tables: classical_works
Field mapping:
- id -> classical_works.id
- slug -> classical_works.slug
- title -> classical_works.title
- description -> classical_works.description
- work_type -> classical_works.work_type

### IdiomOut
Source: app/api/v1/idiom.py
Fields: id, text_devanagari, text_roman, meaning, version
Primary tables: idiom_entries
Field mapping:
- id -> idiom_entries.id
- text_devanagari -> idiom_entries.text_devanagari
- text_roman -> idiom_entries.text_roman
- meaning -> idiom_entries.meaning
- version -> idiom_entries.version

### ReportIn
Source: app/api/v1/interactions.py
Fields: content_type, content_id, reason, note, metadata
Primary tables: reports
Field mapping:
- content_type -> reports.content_type
- content_id -> reports.content_id
- reason -> reports.reason
- note -> reports.note
- metadata -> reports.report_metadata

### ShareIn
Source: app/api/v1/interactions.py
Fields: content_type, content_id, metadata
Primary tables: share_logs, engagement_kpis
Field mapping:
- content_type -> share_logs.content_type
- content_id -> share_logs.content_id
- metadata -> share_logs.share_metadata

### ToggleIn
Source: app/api/v1/interactions.py
Fields: content_type, content_id, interaction, metadata
Primary tables: user_interactions, engagement_kpis
Field mapping:
- content_type -> user_interactions.content_type
- content_id -> user_interactions.content_id
- interaction -> user_interactions.interaction_type
- metadata -> (derived/validated/non-column)

### BatchApproveIn
Source: app/api/v1/moderation.py
Fields: submission_ids
Primary tables: submissions
Field mapping:
- submission_ids -> (derived/validated/non-column)

### BatchApproveOut
Source: app/api/v1/moderation.py
Fields: batch_id, created, skipped, errors
Primary tables: submissions, doha_entries, dictionary_entries, idiom_entries, article_entries
Field mapping:
- batch_id -> (derived/validated/non-column)
- created -> (derived/validated/non-column)
- skipped -> (derived/validated/non-column)
- errors -> (derived/validated/non-column)

### ModerationActionIn
Source: app/api/v1/moderation.py
Fields: note, guideline_version
Primary tables: moderation_logs
Field mapping:
- note -> moderation_logs.note
- guideline_version -> moderation_logs.guideline_version

### ModerationBatchIn
Source: app/api/v1/moderation.py
Fields: action, submission_ids, note, guideline_version
Primary tables: submissions, moderation_logs
Field mapping:
- action -> moderation_logs.action
- submission_ids -> (derived/validated/non-column)
- note -> moderation_logs.note
- guideline_version -> moderation_logs.guideline_version

### ModerationSubmissionOut
Source: app/api/v1/moderation.py
Fields: id, content_type, main_text, meaning, status, is_classical, author_slug, work_slug, chapter_slug, number_in_chapter, contributor_id, assigned_moderator_id, priority, version
Primary tables: submissions
Field mapping:
- id -> submissions.id
- content_type -> submissions.content_type
- main_text -> submissions.main_text
- meaning -> submissions.meaning
- status -> submissions.status
- is_classical -> submissions.is_classical
- author_slug -> submissions.author_slug
- work_slug -> submissions.work_slug
- chapter_slug -> submissions.chapter_slug
- number_in_chapter -> submissions.number_in_chapter
- contributor_id -> submissions.contributor_id
- assigned_moderator_id -> submissions.assigned_moderator_id
- priority -> submissions.priority
- version -> submissions.version

### SearchItem
Source: app/api/v1/search.py
Fields: id, hierarchy_path, main_text, meaning, relevance_score
Primary tables: doha_entries, engagement_kpis
Field mapping:
- id -> doha_entries.id
- hierarchy_path -> doha_entries.hierarchy_path
- main_text -> doha_entries.main_text
- meaning -> doha_entries.meaning
- relevance_score -> (derived/validated/non-column)

### SearchOut
Source: app/api/v1/search.py
Fields: total, results
Primary tables: doha_entries, engagement_kpis
Field mapping:
- total -> (derived/validated/non-column)
- results -> (derived/validated/non-column)

### SubmissionCreateIn
Source: app/api/v1/submissions.py
Fields: content_type, main_text, meaning, is_classical, author_slug, work_slug, chapter_slug, number_in_chapter, external_references, visibility, submit_for_review
Primary tables: submissions
Field mapping:
- content_type -> submissions.content_type
- main_text -> submissions.main_text
- meaning -> submissions.meaning
- is_classical -> submissions.is_classical
- author_slug -> submissions.author_slug
- work_slug -> submissions.work_slug
- chapter_slug -> submissions.chapter_slug
- number_in_chapter -> submissions.number_in_chapter
- external_references -> submissions.external_references
- visibility -> submissions.visibility
- submit_for_review -> (derived/validated/non-column)

### SubmissionOut
Source: app/api/v1/submissions.py
Fields: id, content_type, main_text, meaning, is_classical, author_slug, work_slug, chapter_slug, number_in_chapter, external_references, status, visibility, version, contributor_id, priority
Primary tables: submissions
Field mapping:
- id -> submissions.id
- content_type -> submissions.content_type
- main_text -> submissions.main_text
- meaning -> submissions.meaning
- is_classical -> submissions.is_classical
- author_slug -> submissions.author_slug
- work_slug -> submissions.work_slug
- chapter_slug -> submissions.chapter_slug
- number_in_chapter -> submissions.number_in_chapter
- external_references -> submissions.external_references
- status -> submissions.status
- visibility -> submissions.visibility
- version -> submissions.version
- contributor_id -> submissions.contributor_id
- priority -> submissions.priority

### SubmissionUpdateIn
Source: app/api/v1/submissions.py
Fields: main_text, meaning, external_references, visibility, submit_for_review, expected_version
Primary tables: submissions
Field mapping:
- main_text -> submissions.main_text
- meaning -> submissions.meaning
- external_references -> submissions.external_references
- visibility -> submissions.visibility
- submit_for_review -> (derived/validated/non-column)
- expected_version -> (derived/validated/non-column)

### PublicUserOut
Source: app/api/v1/users.py
Fields: id, username, role
Primary tables: users
Field mapping:
- id -> users.id
- username -> users.username
- role -> users.role

### RateLimitAction
Source: app/services/system_settings.py
Fields: limit, window_seconds
Primary tables: system_settings
Field mapping:
- limit -> (derived/validated/non-column)
- window_seconds -> (derived/validated/non-column)

### RateLimitsModel
Source: app/services/system_settings.py
Fields: login, search, submission_create
Primary tables: system_settings
Field mapping:
- login -> (derived/validated/non-column)
- search -> (derived/validated/non-column)
- submission_create -> (derived/validated/non-column)

## Notes

- Some schemas (analytics/search wrappers) represent computed responses rather than direct table rows.
- Mapping is based on field names, explicit special cases, and endpoint/service usage patterns.