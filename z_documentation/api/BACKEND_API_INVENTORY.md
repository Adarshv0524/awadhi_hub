# Backend API Endpoint Inventory
**Date:** December 30, 2025  
**Total Endpoints:** 66

---

## 1. Authentication Module (`/auth`)
| Method | Endpoint | Auth Required | Response Model | Purpose |
|--------|----------|---------------|----------------|---------|
| POST | `/auth/register` | No | TokenPair | User registration |
| POST | `/auth/login` | No | TokenPair | User login with email/password |
| POST | `/auth/refresh` | Refresh token | TokenPair | Refresh access token |
| POST | `/auth/logout` | Yes | None | Invalidate refresh token |
| GET | `/auth/me` | Yes | UserOut | Get current user profile |
| GET | `/auth/oauth/google/callback` | No | TokenPair | Google OAuth callback |

---

## 2. Content Module (`/content`)
| Method | Endpoint | Auth Required | Response Model | Purpose |
|--------|----------|---------------|----------------|---------|
| GET | `/content/doha` | No | List[DohaOut] | List doha entries (public) |
| GET | `/content/doha/{doha_id}` | No | DohaOut | Get single doha entry |
| GET | `/content/doha/{doha_id}/history` | No | List[ContentVersionOut] | Get doha version history |
| GET | `/content/by-path/{hierarchy_path}` | No | DohaOut | Get doha by hierarchy path |

---

## 3. Dictionary Module (`/dictionary`)
| Method | Endpoint | Auth Required | Response Model | Purpose |
|--------|----------|---------------|----------------|---------|
| GET | `/dictionary` | No | List[DictionaryOut] | List dictionary entries |
| GET | `/dictionary/{entry_id}` | No | DictionaryDetailOut | Get single dictionary entry |

---

## 4. Idiom Module (`/idioms`)
| Method | Endpoint | Auth Required | Response Model | Purpose |
|--------|----------|---------------|----------------|---------|
| GET | `/idioms` | No | List[IdiomOut] | List idiom entries |
| GET | `/idioms/{idiom_id}` | No | IdiomOut | Get single idiom entry |

---

## 5. Article Module (`/articles`)
| Method | Endpoint | Auth Required | Response Model | Purpose |
|--------|----------|---------------|----------------|---------|
| GET | `/articles` | No | List[ArticleListOut] | List articles with search/filter |
| GET | `/articles/stats` | No | ArticleStatsOut | Get article statistics |
| GET | `/articles/search/advanced` | No | Dict | Advanced search with filters |
| GET | `/articles/{article_id}` | No | ArticleDetailOut | Get single article |
| GET | `/articles/by-tag/{tag}` | No | List | Get articles by tag |
| GET | `/articles/recent/list` | No | List | Get recent articles |
| GET | `/articles/tags/list` | No | Dict | Get all article tags |

---

## 6. Submissions Module (`/submissions`)
| Method | Endpoint | Auth Required | Response Model | Purpose |
|--------|----------|---------------|----------------|---------|
| POST | `/submissions` | Yes | SubmissionOut | Create new submission |
| GET | `/submissions/me` | Yes | List[SubmissionOut] | Get user's submissions |
| GET | `/submissions/{submission_id}` | Yes | SubmissionOut | Get single submission |
| PUT | `/submissions/{submission_id}` | Yes | SubmissionOut | Update submission |
| DELETE | `/submissions/{submission_id}` | Yes | None | Delete submission |

---

## 7. Moderation Module (`/moderation`)
| Method | Endpoint | Auth Required | Response Model | Purpose |
|--------|----------|---------------|----------------|---------|
| GET | `/moderation/queue` | Moderator+ | List[SubmissionOut] | Get moderation queue |
| GET | `/moderation/queue/{id}` | Moderator+ | SubmissionOut | Get submission details |
| POST | `/moderation/queue/{id}/approve` | Moderator+ | Dict | Approve submission |
| POST | `/moderation/queue/{id}/reject` | Moderator+ | Dict | Reject submission |
| POST | `/moderation/batch` | Moderator+ | Dict | Batch moderation actions |
| POST | `/moderation/batch_approve` | Moderator+ | BatchApproveOut | Batch approve submissions |

---

## 8. Interactions Module (`/interactions`)
| Method | Endpoint | Auth Required | Response Model | Purpose |
|--------|----------|---------------|----------------|---------|
| POST | `/interactions/toggle` | Yes | Dict | Toggle like/bookmark |
| POST | `/interactions/share` | Yes | Dict | Track share action |
| POST | `/interactions/report` | Yes | Dict | Report content |
| GET | `/interactions/users/{user_id}/bookmarks` | No | PaginatedResponse | Get user bookmarks |

---

## 9. Hierarchy Public Module (`/authors`)
| Method | Endpoint | Auth Required | Response Model | Purpose |
|--------|----------|---------------|----------------|---------|
| GET | `/authors` | No | List[AuthorListOut] | List all authors |
| GET | `/authors/{author_slug}` | No | AuthorDetailOut | Get author details |
| GET | `/authors/{author_slug}/works` | No | List[WorkOut] | Get author's works |
| GET | `/authors/{author_slug}/works/{work_slug}` | No | WorkDetailOut | Get work details |
| GET | `/authors/{author_slug}/works/{work_slug}/chapters` | No | List[ChapterOut] | Get work chapters |

---

## 10. Hierarchy Admin Module (`/admin/hierarchy`)
| Method | Endpoint | Auth Required | Response Model | Purpose |
|--------|----------|---------------|----------------|---------|
| POST | `/admin/hierarchy/authors` | Admin | Dict | Create author |
| PATCH | `/admin/hierarchy/authors/{author_id}` | Admin | Dict | Update author |
| POST | `/admin/hierarchy/authors/{author_id}/works` | Admin | Dict | Create work |
| PATCH | `/admin/hierarchy/works/{work_id}` | Admin | Dict | Update work |
| POST | `/admin/hierarchy/works/{work_id}/chapters` | Admin | Dict | Create chapter |
| PATCH | `/admin/hierarchy/chapters/{chapter_id}` | Admin | Dict | Update chapter |

---

## 11. Admin Users Module (`/admin/users`)
| Method | Endpoint | Auth Required | Response Model | Purpose |
|--------|----------|---------------|----------------|---------|
| GET | `/admin/users` | Admin | List[AdminUserOut] | List all users |
| GET | `/admin/users/{user_id}` | Admin | AdminUserOut | Get user details |
| POST | `/admin/users` | Admin | AdminUserOut | Create user |
| PATCH | `/admin/users/{user_id}` | Admin | AdminUserOut | Update user |

---

## 12. Admin Settings Module (`/admin/settings`)
| Method | Endpoint | Auth Required | Response Model | Purpose |
|--------|----------|---------------|----------------|---------|
| GET | `/admin/settings` | Admin | List[SettingOut] | Get all settings |
| GET | `/admin/settings/{key}` | Admin | SettingOut | Get single setting |
| PUT | `/admin/settings/{key}` | Admin | SettingOut | Update setting |
| DELETE | `/admin/settings/{key}` | Admin | None | Delete setting |

---

## 13. Admin Audit Module (`/admin/audit`)
| Method | Endpoint | Auth Required | Response Model | Purpose |
|--------|----------|---------------|----------------|---------|
| GET | `/admin/audit` | Admin | PaginatedResponse | Get audit logs |
| GET | `/admin/audit/export/csv` | Admin | CSV file | Export audit logs |
| GET | `/admin/audit/{id}` | Admin | AuditLogOut | Get single audit log |

---

## 14. Analytics Module (`/analytics`)
| Method | Endpoint | Auth Required | Response Model | Purpose |
|--------|----------|---------------|----------------|---------|
| GET | `/analytics/top` | No | List[TopContentItem] | Get top content by engagement |
| GET | `/analytics/growth` | No | GrowthSeries | Get content growth over time |
| GET | `/analytics/demand` | No | Dict[str, DemandItem] | Get content demand metrics |

---

## 15. Other Modules
| Method | Endpoint | Auth Required | Response Model | Purpose |
|--------|----------|---------------|----------------|---------|
| GET | `/recommendations/{content_type}/{content_id}` | No | List | Get content recommendations |
| GET | `/search/search` | No | SearchResults | Global search |
| GET | `/users/{username}` | No | PublicUserOut | Get public user profile |

---

## Response Models Summary

### Core Data Models
- **DohaOut**: id, main_text, meaning, text_devanagari, text_romanized, hierarchy_path, author_name, work_name, chapter_name, version, created_at, updated_at, engagement counts
- **DictionaryOut**: id, text, meaning, text_devanagari, text_roman, part_of_speech, version
- **IdiomOut**: id, text, meaning, text_devanagari, text_roman, usage_example, version
- **ArticleListOut**: id, title, title_devanagari, title_roman, excerpt, tags, version, created_at
- **ArticleDetailOut**: Extends ArticleListOut + body, author_id, contributor_id

### User Models
- **UserOut**: id, username, email, role, created_at
- **PublicUserOut**: id, username, role, created_at (no email)
- **AdminUserOut**: Extends UserOut + is_active, is_banned, last_login

### Submission Models
- **SubmissionOut**: id, content_type, main_text, meaning, status, visibility, version, contributor_id, created_at, updated_at

### Pagination
- **PaginatedResponse**: count, results[]

---

## Query Parameters Summary

### Common Filters
- `q`: Search query
- `offset`: Pagination offset
- `limit`: Items per page
- `visibility`: public/private filter
- `status`: draft/pending/approved/rejected

### Content-Specific
- `tag`: Filter by tag (articles)
- `content_type`: doha/dictionary/idiom/article
- `start_date`/`end_date`: Time range filters
- `sort_by`: Sorting criteria

---

**Next Step:** Begin iterative audit of each endpoint's frontend integration.
