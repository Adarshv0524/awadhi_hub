# API Reference & Inventory

**Document Purpose**: Complete endpoint documentation, schemas, and integration examples  
**Last Updated**: March 26, 2026  
**Version**: 1.0.0  

---

## Authentication Endpoints

### POST /auth/register

Register a new user account.

**Request**
```json
{
  "email": "user@example.com",
  "username": "username_optional",
  "password": "securepassword"
}
```

**Response (201)**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username_optional",
  "role": "registered",
  "created_at": "2026-03-26T10:30:00Z"
}
```

---

### POST /auth/login

Authenticate with email and password.

**Request**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response (200)**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

---

### POST /auth/refresh

Refresh expired access token.

**Request (Header)**
```
Authorization: Bearer {refresh_token}
```

**Response (200)**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

---

### POST /auth/logout

Invalidate current session.

**Response (200)**
```json
{
  "message": "Logged out successfully"
}
```

---

### POST /auth/me

Get current authenticated user.

**Request (Header)**
```
Authorization: Bearer {access_token}
```

**Response (200)**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "role": "registered",
  "permission_scopes": {}
}
```

---

### POST /auth/oauth/google/callback

Handle Google OAuth callback.

**Request (Query)**
```
?code=authorization_code&state=state_value
```

**Response (200)**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

---

## Hierarchy Endpoints (Public)

### GET /hierarchy/authors

List all classical authors.

**Query Parameters**
- `offset`: int (default 0)
- `limit`: int (default 50, max 200)

**Response (200)**
```json
{
  "total": 42,
  "offset": 0,
  "limit": 50,
  "items": [
    {
      "id": 1,
      "slug": "tulsidas",
      "name": "तुलसीदास",
      "short_bio": "16th century poet",
      "language": "awadhi",
      "created_at": "2026-01-01T00:00:00Z"
    }
  ]
}
```

---

### GET /hierarchy/authors/{author_slug}/works

List works by a specific author.

**Response (200)**
```json
{
  "total": 5,
  "items": [
    {
      "id": 1,
      "slug": "ramcharitmanas",
      "title": "रामचरितमानस",
      "work_type": "poetry",
      "description": "Epic poem by Tulsidas"
    }
  ]
}
```

---

### GET /hierarchy/authors/{author_slug}/works/{work_slug}/chapters

List chapters for a specific work.

**Response (200)**
```json
{
  "total": 7,
  "items": [
    {
      "id": 1,
      "slug": "ayodhya-kand",
      "title": "अयोध्या काण्ड",
      "number": 1
    }
  ]
}
```

---

## Content Endpoints (Public)

### GET /content/doha

List all doha entries.

**Query Parameters**
- `offset`: int (default 0, min 0)
- `limit`: int (default 50, min 1, max 200)
- `visibility`: string (optional: "public", "private")

**Response (200)**
```json
[
  {
    "id": 1,
    "main_text": "श्रीरामचन्द्र कृपालु भजु मन",
    "meaning": "Worship kind-hearted Shri Ramchandra",
    "text_devanagari": "श्रीरामचन्द्र कृपालु भजु मन",
    "text_romanized": "Shriramchandra Krripalu Bhaju Man",
    "hierarchy_path": "tulsidas/ramcharitmanas/ayodhya-kand/1",
    "number_in_chapter": 1,
    "author_name": "तुलसीदास",
    "work_name": "रामचरितमानस",
    "chapter_name": "अयोध्या काण्ड",
    "created_at": "2026-01-01T00:00:00Z",
    "updated_at": "2026-01-01T00:00:00Z",
    "likes_count": 42,
    "views_count": 1203,
    "shares_count": 15,
    "bookmarks_count": 28
  }
]
```

---

### GET /content/doha/{doha_id}

Get a single doha entry with full details.

**Response (200)**
```json
{
  "id": 1,
  "main_text": "श्रीरामचन्द्र कृपालु भजु मन",
  "meaning": "Worship kind-hearted Shri Ramchandra",
  "text_devanagari": "श्रीरामचन्द्र कृपालु भजु मन",
  "text_romanized": "Shriramchandra Krripalu Bhaju Man",
  "hierarchy_path": "tulsidas/ramcharitmanas/ayodhya-kand/1",
  "number_in_chapter": 1,
  "author_name": "तुलसीदास",
  "work_name": "रामचरितमानस",
  "chapter_name": "अयोध्या काण्ड",
  "created_at": "2026-01-01T00:00:00Z",
  "updated_at": "2026-01-01T00:00:00Z",
  "likes_count": 42,
  "views_count": 1203,
  "shares_count": 15,
  "bookmarks_count": 28,
  "status": "active",
  "visibility": "public",
  "version": 1,
  "is_canonical": true
}
```

---

### GET /content/doha/{doha_id}/navigation

Get previous, current, and next doha cards within the same chapter.

**Response (200)**
```json
{
  "previous": {
    "id": 23,
    "number_in_chapter": 23,
    "short_text": "Ram dut atulit bal"
  },
  "current": {
    "id": 24,
    "number_in_chapter": 24,
    "short_text": "Mahavir vikram bichram dharam"
  },
  "next": {
    "id": 25,
    "number_in_chapter": 25,
    "short_text": "Jai Hanuman gyan gun sagar"
  }
}
```

**Response (200 - At Boundary)**
```json
{
  "previous": null,
  "current": {
    "id": 1,
    "number_in_chapter": 1,
    "short_text": "First verse"
  },
  "next": {
    "id": 2,
    "number_in_chapter": 2,
    "short_text": "Second verse"
  }
}
```

---

### GET /content/by-path/{author_slug}/{work_slug}/{chapter_slug}/dohas

Get all dohas for a specific chapter.

**Query Parameters**
- `offset`: int (default 0)
- `limit`: int (default 100, max 200)

**Response (200)**
```json
{
  "chapter_id": 1,
  "chapter_slug": "ayodhya-kand",
  "total": 287,
  "offset": 0,
  "limit": 100,
  "items": [
    {
      "id": 1,
      "hierarchy_path": "tulsidas/ramcharitmanas/ayodhya-kand/1",
      "chapter_id": 1,
      "number_in_chapter": 1,
      "main_text": "..."
    }
  ]
}
```

---

### GET /content/chapters/{chapter_id}/dohas

Get dohas by chapter ID (preferred over by-path).

**Response (200)**
```json
{
  "chapter_id": 1,
  "chapter_slug": "ayodhya-kand",
  "total": 287,
  "offset": 0,
  "limit": 100,
  "items": [...]
}
```

---

### GET /content/doha/{doha_id}/history

Get version history of a doha entry.

**Response (200)**
```json
[
  {
    "id": 1,
    "content_type": "doha",
    "content_id": 1,
    "version_number": 1,
    "main_text": "Original text",
    "created_by": 5,
    "created_at": "2026-01-01T00:00:00Z",
    "notes": "Initial creation"
  }
]
```

---

## Search Endpoints

### GET /search

Full-text search across all content types.

**Query Parameters**
- `q`: string (required, search query)
- `content_type`: string (optional: "doha", "dictionary", "idiom", "article")
- `author`: string (optional, author slug)
- `work`: string (optional, work slug)
- `chapter`: string (optional, chapter slug)
- `offset`: int (default 0)
- `limit`: int (default 50, max 200)

**Response (200)**
```json
{
  "total": 125,
  "offset": 0,
  "limit": 50,
  "query": "ram dut",
  "items": [
    {
      "id": 1,
      "content_type": "doha",
      "main_text": "Ram dut atulit bal",
      "meaning": "...",
      "author_name": "तुलसीदास",
      "score": 0.95
    }
  ]
}
```

---

## Interactions Endpoints (Authenticated)

### GET /interactions/users/{user_id}/bookmarks

Get user's bookmarked content.

**Query Parameters**
- `offset`: int (default 0)
- `limit`: int (default 50, max 200)

**Response (200)**
```json
[
  {
    "id": 1,
    "content_id": 10,
    "content_type": "doha",
    "content_title": "Ram dut atulit...",
    "content_snippet": "Ram dut atulit bal...",
    "created_at": "2026-03-20T10:00:00Z"
  }
]
```

---

### POST /interactions/bookmarks

Add content to user's bookmarks.

**Request**
```json
{
  "content_type": "doha",
  "content_id": 10
}
```

**Response (201)**
```json
{
  "id": 1,
  "user_id": 42,
  "content_type": "doha",
  "content_id": 10,
  "interaction_type": "bookmark"
}
```

---

### DELETE /interactions/bookmarks/{bookmark_id}

Remove bookmark.

**Response (204)**
```
(No content)
```

---

### GET /interactions/users/{user_id}/likes

**⚠️ MISSING ENDPOINT** – See Issues.md for details.

---

### POST /interactions/likes

Like content.

**Request**
```json
{
  "content_type": "doha",
  "content_id": 10
}
```

**Response (201)**
```json
{
  "id": 1,
  "user_id": 42,
  "content_type": "doha",
  "content_id": 10,
  "interaction_type": "like"
}
```

---

### DELETE /interactions/likes/{like_id}

Unlike content.

**Response (204)**
```
(No content)
```

---

## Submissions Endpoints (Authenticated)

### POST /submissions

Submit new content for moderation.

**Request**
```json
{
  "content_type": "doha",
  "main_text": "नया दोहा",
  "meaning": "New verse",
  "is_classical": true,
  "author_slug": "tulsidas",
  "work_slug": "ramcharitmanas",
  "chapter_slug": "ayodhya-kand",
  "number_in_chapter": 288
}
```

**Response (201)**
```json
{
  "id": 1,
  "content_type": "doha",
  "main_text": "नया दोहा",
  "status": "draft",
  "contributor_id": 42,
  "created_at": "2026-03-26T10:00:00Z"
}
```

---

### GET /submissions/{submission_id}

Get submission details.

**Response (200)**
```json
{
  "id": 1,
  "content_type": "doha",
  "main_text": "नया दोहा",
  "status": "pending_review",
  "contributor_id": 42,
  "assigned_moderator_id": 5,
  "created_at": "2026-03-26T10:00:00Z"
}
```

---

### PUT /submissions/{submission_id}

Update submission (moderator can edit metadata).

**Request (Moderator)**
```json
{
  "main_text": "Corrected text",
  "meaning": "Corrected meaning",
  "chapter_slug": "corrected-chapter"
}
```

**Response (200)**
```json
{
  "id": 1,
  "main_text": "Corrected text",
  "chapter_slug": "corrected-chapter",
  "updated_at": "2026-03-26T11:00:00Z"
}
```

---

### POST /submissions/{submission_id}/approve

Approve submission (moderator).

**Response (200)**
```json
{
  "submission_id": 1,
  "status": "approved",
  "canonical_entry_id": 100,
  "message": "Submission approved and canonical entry created"
}
```

---

### POST /submissions/{submission_id}/reject

Reject submission (moderator).

**Request**
```json
{
  "reason": "Invalid hierarchy reference",
  "note": "Author slug 'unknown-author' does not exist"
}
```

**Response (200)**
```json
{
  "submission_id": 1,
  "status": "rejected",
  "reason": "Invalid hierarchy reference"
}
```

---

### POST /submissions/batch-approve

Batch approve multiple submissions (atomic).

**Request**
```json
{
  "submission_ids": [1, 2, 3, 4, 5]
}
```

**Response (200)**
```json
{
  "approved_count": 5,
  "failed_count": 0,
  "approved_ids": [1, 2, 3, 4, 5],
  "created_entries": 5
}
```

---

## Users Endpoints

### GET /users/{username}

Get public user profile.

**Response (200)**
```json
{
  "id": 1,
  "username": "user123",
  "email": "user@example.com",
  "role": "registered",
  "created_at": "2026-01-15T00:00:00Z"
}
```

---

### GET /users/{username}/stats

**⚠️ MISSING ENDPOINT** – See Issues.md for details.

Expected response:
```json
{
  "username": "user123",
  "contributions_count": 12,
  "likes_received": 145,
  "average_engagement_score": 0.65,
  "joined_date": "2026-01-15T00:00:00Z"
}
```

---

## Rate Limiting

All endpoints are subject to rate limiting:

| Action | Limit | Window |
|--------|-------|--------|
| Search | 60 requests | 60 seconds |
| API calls (general) | 100 requests | 60 seconds |
| Login attempts | 5 requests | 1 hour |
| Submission creation | 10 requests | 1 hour |

**Rate Limit Headers**
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1648300800
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid chapter_slug: chapter-not-found"
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
  "detail": "Not authorized to perform this action"
}
```

### 404 Not Found
```json
{
  "detail": "Doha not found"
}
```

### 429 Too Many Requests
```json
{
  "detail": "Rate limit exceeded"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Pagination

All list endpoints follow standard pagination:

```json
{
  "total": 1000,
  "offset": 0,
  "limit": 50,
  "items": [...]
}
```

- `total`: Total number of available items
- `offset`: Starting position of returned items
- `limit`: Maximum items per page
- `items`: Array of results

---

## Schema Definitions

### DohaOut
```typescript
{
  id: number
  main_text: string
  meaning?: string
  text_devanagari?: string
  text_romanized?: string
  hierarchy_path?: string
  number_in_chapter?: number
  author_name?: string
  work_name?: string
  chapter_name?: string
  created_at?: datetime
  updated_at?: datetime
  likes_count?: number
  views_count?: number
  shares_count?: number
  bookmarks_count?: number
  status: string
  visibility: string
  version: number
  is_canonical: boolean
}
```

### SubmissionUpdateIn
```typescript
{
  main_text?: string
  meaning?: string
  author_slug?: string        // Moderator only
  work_slug?: string          // Moderator only
  chapter_slug?: string       // Moderator only
  number_in_chapter?: number  // Moderator only
  is_classical?: boolean      // Moderator only
}
```

---

See **Issues.md** for missing endpoints and planned improvements.
