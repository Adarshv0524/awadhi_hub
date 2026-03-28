# Awadhi Hub 2026: System Architecture
## Deep Technical Reference for Engineers

**Purpose**: Comprehensive technical documentation of system components, data flow, schema, API patterns, and deployment strategy.

**Audience**: Backend developers, architects, DBAs, DevOps  
**Last Updated**: March 28, 2026

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Components](#architecture-components)
3. [Data Layer Design](#data-layer-design)
4. [API Patterns](#api-patterns)
5. [Service Layer](#service-layer)
6. [Deployment Architecture](#deployment-architecture)
7. [Performance Characteristics](#performance-characteristics)
8. [Security & Auth](#security--authentication)

---

## System Overview

### Component Stack

```
┌─────────────────────────────────────────────────────────────┐
│  CLIENT LAYER                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Browsers (Chrome, Firefox, Safari, Mobile)           │   │
│  │ → Astro Server-Side Rendered Static Site             │   │
│  │ → Svelte Dynamic Components (Client-side hydration)  │   │
│  └──────────────────────────────────────────────────────┘   │
└───────────────────────────────┬─────────────────────────────┘
                                │ HTTP REST
┌───────────────────────────────▼─────────────────────────────┐
│  API LAYER                                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ FastAPI Application (python 3.12)                    │   │
│  │ ├─ Route handlers (/api/v1/*)                        │   │
│  │ ├─ Request validation (Pydantic)                     │   │
│  │ ├─ JWT token verification                           │   │
│  │ ├─ CORS middleware                                   │   │
│  │ └─ Error handling (HTTP status codes)                │   │
│  └──────────────────────────────────────────────────────┘   │
└───────────────────────────────┬─────────────────────────────┘
                                │ ORM (SQLAlchemy)
┌───────────────────────────────▼─────────────────────────────┐
│  SERVICE LAYER                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Business Logic Services                              │   │
│  │ ├─ universal_content_service (navigation)            │   │
│  │ ├─ moderation_service (approval workflow)            │   │
│  │ ├─ engagement_service (KPIs & metrics)               │   │
│  │ ├─ hierarchy_service (author/work/chapter trees)     │   │
│  │ ├─ submission_service (user uploads)                 │   │
│  │ ├─ search_service (full-text indexing)               │   │
│  │ └─ auth_service (user & token mgmt)                  │   │
│  └──────────────────────────────────────────────────────┘   │
└───────────────────────────────┬─────────────────────────────┘
                                │ Connection Pooling
┌───────────────────────────────▼─────────────────────────────┐
│  DATA LAYER                                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ MySQL 8.0+ Database                                  │   │
│  │ ├─ Users & Auth (users, refresh_tokens, oauth_*)     │   │
│  │ ├─ Content Hierarchy (authors, works, chapters)      │   │
│  │ ├─ Universal Content (doha, chaupai, idiom, etc.)    │   │
│  │ ├─ Moderation (submissions, moderation_logs)         │   │
│  │ ├─ Engagement (engagement_kpis, user_interactions)   │   │
│  │ ├─ System (system_settings, audit_logs)              │   │
│  │ └─ Indices (full-text, btree, unique constraints)    │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Request Flow Example: User Views a Content Item

```
1. Browser GET /hanuman_bahuk/chapter_1
   ↓
2. Astro SSR renders page, calls backend API
   ↓
3. FastAPI GET /api/v1/content/unified/101/nav?current_number=1
   ↓
4. JWT token verified (middleware)
   ↓
5. universal_content_service.get_chapter_navigation(db, chapter_id=101, number=1)
   ├─ Query UniversalContent (where chapter_id=101, number_in_chapter=1)
   ├─ Enrich with EngagementKPI (views, likes, etc.)
   ├─ Fetch next/prev items (2 more queries)
   └─ Return combined result
   ↓
6. FastAPI serializes Pydantic schema to JSON
   ↓
7. Browser receives JSON, Svelte hydrates components
   ↓
8. User sees rendered content with interactive buttons
```

---

## Architecture Components

### 1. Frontend (Astro + Svelte)

#### Purpose
Deliver fast, SEO-friendly HTML to browsers; hydrate interactive features with Svelte.

#### Structure
```
frontend/
├─ src/
│  ├─ pages/           # Astro routes (SSR → static HTML)
│  │  ├─ index.astro
│  │  ├─ search.astro
│  │  ├─ [author]/[work]/[chapter].astro  # Dynamic routes
│  │  ├─ doha/[id].astro
│  │  ├─ login.astro
│  │  └─ dashboard/
│  ├─ components/       # Svelte interactive components
│  │  ├─ content/ContentDispatcher.svelte  # Dynamic renderer
│  │  ├─ interaction/InteractionBar.svelte  # Like/bookmark UI
│  │  ├─ navigation/NavigationControls.svelte
│  │  ├─ submission/SubmissionForm.svelte
│  │  └─ common/
│  ├─ layouts/         # Astro layouts (HTML structure)
│  │  ├─ BaseLayout.astro  # <head>, canonical URL, meta tags
│  │  └─ DashboardLayout.astro
│  ├─ lib/            # Client-side utilities
│  │  ├─ types.ts     # TypeScript interface definitions
│  │  ├─ api.ts       # Fetch wrappers
│  │  ├─ stores.ts    # Svelte stores (auth, UI state)
│  │  └─ utils.ts
│  └─ styles/         # Shared CSS
│      └─ globals.css
├─ public/            # Static assets (logos, downloads)
├─ astro.config.mjs   # Build config
├─ svelte.config.js   # Svelte preprocessing
└─ tsconfig.json      # TypeScript config
```

#### Key Features
- **Server-Side Rendering**: Every page pre-rendered for SEO
- **Hydration**: Svelte components activate on client
- **Dynamic Routes**: Use Astro `getStaticPaths()` for content pages
- **TypeScript**: Full type safety via types.ts
- **Responsive**: Mobile-first design, dark theme

---

### 2. Backend (FastAPI)

#### Purpose
REST API for data access, business logic, moderation workflows.

#### Project Structure
```
backend/
├─ app/
│  ├─ main.py              # FastAPI app initialization
│  ├─ api/v1/              # REST endpoints
│  │  ├─ content_universal.py   # New unified endpoint
│  │  ├─ hierarchy_public.py     # Author/work/chapter
│  │  ├─ submissions.py
│  │  ├─ moderation.py
│  │  ├─ search.py
│  │  ├─ users.py
│  │  └─ ...20+ more files
│  ├─ services/            # Business logic
│  │  ├─ universal_content_service.py
│  │  ├─ moderation_service.py
│  │  ├─ engagement_service.py
│  │  └─ ...6 more services
│  ├─ schemas/             # Pydantic request/response models
│  │  ├─ content_universal.py
│  │  ├─ submissions.py
│  │  └─ ...10+ more files
│  ├─ db/
│  │  ├─ models.py         # SQLAlchemy ORM models (11 tables)
│  │  ├─ session.py        # Database connection management
│  │  └─ __init__.py
│  ├─ core/
│  │  ├─ security.py       # JWT token & OAuth handling
│  │  └─ permissions.py    # Role-based access control
│  ├─ auth/                # Authentication routes
│  │  ├─ google_oauth.py
│  │  └─ jwt_handler.py
│  └─ utils/               # Utilities (logging, validation, etc.)
├─ alembic/                # Database migrations
│  ├─ env.py
│  ├─ alembic.ini
│  └─ versions/            # Migration files (15+ versions)
├─ tests/                  # Pytest test suite
├─ pyproject.toml          # Poetry dependencies
├─ requirements.txt
└─ Dockerfile
```

#### Key Technologies
- **Framework**: FastAPI (async, auto-docs)
- **ORM**: SQLAlchemy 2.0
- **Database**: MySQL 8.0+
- **Validation**: Pydantic v2
- **Migrations**: Alembic
- **Authentication**: JWT + OAuth2 (Google)
- **Testing**: Pytest + fixtures

---

### 3. Database (MySQL)

#### Schema Overview

**11 Core Tables**:

```
Users & Auth:
├─ users                (id, email, username, role, permissions, ...)
├─ refresh_tokens      (id, token, user_id, expires_at, ...)
└─ oauth_accounts      (id, provider, provider_user_id, user_id, ...)

Content Hierarchy:
├─ classical_authors   (id, slug, name, bio, language, ...)
├─ classical_works     (id, author_id, slug, title, description, ...)
└─ work_chapters       (id, work_id, slug, title, number, ...)

Universal Content (NEW):
└─ universal_content   (id, work_id, chapter_id, content_type, number_in_chapter,
                        main_text, metadata, visibility, ...)

Moderation:
├─ submissions         (id, content_type, main_text, status, contributor_id, ...)
├─ moderation_logs     (id, submission_id, moderator_id, action, from_status, ...)
└─ moderation_guidelines (id, version, title, url, is_active, ...)

Versioning:
└─ content_versions    (id, content_type, content_id, version_number, ...)

Engagement:
├─ engagement_kpis     (id, content_type, content_id, views_count,
                        likes_count, shares_count, bookmarks_count, weight_score, ...)
├─ user_interactions   (id, user_id, content_type, content_id,
                        interaction_type[like|bookmark], is_active, ...)
├─ share_logs          (id, user_id, content_type, content_id, share_metadata, ...)
└─ reports             (id, user_id, content_type, content_id, reason, status, ...)

System:
├─ system_settings     (setting_key, value[JSON], created_at, ...)
├─ audit_logs          (id, actor_user_id, action, resource_type, resource_id, ...)
├─ rate_limit_counters (id, user_id, ip_address, action_key, time_bucket, count, ...)
└─ content_type_definitions (id, content_type, display_name, characteristics, ...)
```

#### Indices Strategy

**High-frequency queries** (see performance section):
- `universal_content(chapter_id, number_in_chapter)` - PRIMARY for nav
- `universal_content(content_type)` - Filter by type
- `engagement_kpis(content_type, content_id)` - KPI lookups
- `user_interactions(user_id, content_type, content_id)` - User's interactions
- `users(email)` - Auth lookups

---

## Data Layer Design

### Content Hierarchy

**Classical Three-Layer Model** (immutable):

```
ClassicalAuthor
  ├─ slug: "tulsidas"
  ├─ name: "ता युलसीदास"
  │
  └─ ClassicalWork
     ├─ slug: "hanuman_bahuk"
     ├─ title: "हनुमान बाहुक"
     │
     └─ WorkChapter (sequence = immutable)
        ├─ slug: "chapter_1"
        ├─ number: 1 (unique within work)
        │
        └─ UniversalContent (polymorphic items in sequence)
           ├─ content_type: "ghanakshari" | "savaiya" | "doha" | "other"
           ├─ number_in_chapter: 1, 2, 3, ...
           └─ main_text, metadata, etc.
```

**Key Invariants**:
- Each chapter has ordered items (1, 2, 3, ...)
- No gaps in numbering (unique constraint on (chapter_id, number_in_chapter))
- Sequence is immutable (renumber via migration)
- Multiple content types in same chapter allowed

### Engagement Polymorphism

**Single table, multiple entities** via content_type discriminator:

```sql
engagement_kpis:
  content_id | content_type | views | likes | shares | ...
  -----------|--------------|-------|-------|--------|-----
  505        | universal_content | 234 | 12  | 3     | ...
```

**Query Example**:
```sql
-- Get likes for any content
SELECT likes_count FROM engagement_kpis
WHERE content_type = 'universal_content'
  AND content_id = 505
```

### Versioning Strategy

**Immutable history with move-forward semantics**:

```
universal_content:
  id: 505
  version: 3              ← Current version number
  main_text: "..."       ← Current text (v3)

content_versions (history):
  id: 100  | content_id: 505 | version: 1 | main_text: "..." | created_by: 10
  id: 101  | content_id: 505 | version: 2 | main_text: "..." | created_by: 11
  id: 102  | content_id: 505 | version: 3 | main_text: "..." | created_by: 12
```

**Usage**: Moderators can roll back to v1 if needed.

---

## API Patterns

### Endpoint Categories

#### 1. Hierarchy Traversal (Public)
```
GET /api/v1/hierarchy/public/{author}/works/{work}/chapters/{chapter}
GET /api/v1/hierarchy/public/{author}/works
GET /api/v1/hierarchy/public/{author}
```

#### 2. Content Navigation (Public)
```
GET /api/v1/content/unified/{chapter_id}/nav?current_number=5
  → Returns: current + next + prev + chapter metadata

GET /api/v1/content/{content_id}
  → Returns: single unified content item with engagement
```

#### 3. Submission & Moderation (Private)
```
POST /api/v1/submissions    (any authenticated user)
GET  /api/v1/submissions/me (see my submissions)
GET  /api/v1/moderation/queue (moderators only)
PATCH /api/v1/moderation/{submission_id}/approve (moderators only)
```

#### 4. Search (Public)
```
GET /api/v1/search?q=...&content_type=doha&offset=0&limit=25
  → Full-text search across all content
```

#### 5. Engagement (Authenticated)
```
POST /api/v1/interactions/like      (required: auth token)
POST /api/v1/interactions/bookmark
GET  /api/v1/users/{user_id}/likes
```

### Request/Response Patterns

#### Standard Response Format
```json
{
  "id": 505,
  "content_type": "chaupai",
  "main_text": "सखे सखे तुम्हरे कुल की बड़ाई...",
  "metadata": {
    "meter": "chaupai",
    "lines": 4,
    "region": "Lucknow"
  },
  "engagement": {
    "views": 234,
    "likes": 12,
    "shares": 3,
    "bookmarks": 5
  },
  "created_at": "2025-12-01T10:30:00Z",
  "verified_by": 42
}
```

#### Error Response Format
```json
{
  "detail": {
    "type": "validation_error",
    "message": "Invalid content_type",
    "issues": [
      {
        "field": "content_type",
        "message": "must be one of: doha, chaupai, ..."
      }
    ]
  },
  "status_code": 400,
  "request_id": "req_abc123"
}
```

#### List Response Format
```json
{
  "data": [...],
  "pagination": {
    "total": 1250,
    "offset": 0,
    "limit": 25,
    "has_next": true
  }
}
```

### Authentication Patterns

**JWT Token** (issued at login, expires in 24h):
```
Authorization: Bearer eyJhbGc...
```

**OAuth2 (Google)**:
```
POST /api/v1/auth/google/callback
  ├─ Exchange code for token
  ├─ Create/link user account
  └─ Return JWT
```

**Refresh Token** (long-lived, in httpOnly cookie):
```
POST /api/v1/auth/refresh
  ├─ Use refresh token
  ├─ Issue new access token
  └─ Return new JWT
```

---

## Service Layer

### Universal Content Service
**File**: `app/services/universal_content_service.py`

**Responsibilities**:
- Fetch next/prev items in chapter (core navigation)
- Enrich content with engagement metrics
- Handle polymorphic queries (any content_type)

**Key Functions**:
```python
get_chapter_navigation(db, chapter_id, current_number)
  → UniversalNavigationOut
  
get_next_content_in_chapter(db, chapter_id, current_number)
  → Optional[UniversalContentOut]
  
get_previous_content_in_chapter(db, chapter_id, current_number)
  → Optional[UniversalContentOut]

enrich_content(db, content: UniversalContent)
  → UniversalContentOut (with KPI + hierarchy info)
```

### Moderation Service
**File**: `app/services/moderation_service.py`

**Responsibilities**:
- Validate submissions against schema
- Route to appropriate creator function
- Create canonical entries
- Log moderation actions

**Key Functions**:
```python
approve_submission_universal(submission_id, db, moderator_id)  
  → UniversalContent
  
reject_submission(submission_id, db, moderator_id, reason)
  → None

flag_for_review(submission_id, db)
  → None
```

### Engagement Service
**File**: `app/services/engagement_service.py`

**Responsibilities**:
- Increment view/like/share/bookmark counts
- Compute weight scores
- Fetch engagement metrics

**Key Functions**:
```python
increment_engagement(db, content_type, content_id, event_type)
  → EngagementKPI
  
get_engagement_summary(db, content_type, content_id)
  → EngagementOut
  
compute_weight_score(kpi: EngagementKPI)
  → float  # Weighted formula: views×0.1 + likes×10 + shares×50 + ...
```

---

## Deployment Architecture

### Environment Setup

```
├─ Development
│  ├─ Backend: uvicorn app.main:app --reload --port 8000
│  ├─ Frontend: npm run dev (Astro dev server)
│  ├─ Database: Local MySQL or Docker container
│  └─ Env: .env.dev (with dummy OAuth keys)
│
├─ Staging
│  ├─ Backend: Gunicorn (4 workers) on port 8000
│  ├─ Frontend: Exported static HTML (npm run build)
│  ├─ Database: AWS RDS MySQL (separate staging DB)
│  ├─ CDN: CloudFront caching static assets
│  └─ Env: .env.staging (with OAuth keys)
│
└─ Production
   ├─ Backend: Gunicorn (12 workers) behind nginx reverse proxy
   ├─ Frontend: Static HTML on S3 + CloudFront CDN
   ├─ Database: AWS RDS MySQL (multi-AZ, automated backups)
   ├─ Cache: Redis for sessions & API caching
   ├─ Search: Elasticsearch for full-text indexing
   └─ Env: .env.prod (with prod OAuth/DB credentials)
```

### Docker Compose (Local Development)

```yaml
version: '3'
services:
  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: awadhi_db
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      DATABASE_URL: mysql://root:root@db:3306/awadhi_db
    command: uvicorn app.main:app --reload --host 0.0.0.0

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
    environment:
      PUBLIC_API_URL: http://localhost:8000

volumes:
  mysql_data:
```

### CI/CD Pipeline

```
Git Push
  ↓
GitHub Actions
  ├─ Unit Tests (backend pytest, frontend Jest)
  ├─ Linting (black, eslint, prettier)
  ├─ Type Checks (mypy, tsc)
  ├─ Integration Tests (Docker Compose)
  └─ Build & Push Docker images to ECR
    ↓
Merge to main → Auto-deploy to staging
    ↓
Manual approval → Deploy to production
```

---

## Performance Characteristics

### Query Performance Targets

| Operation | Target | Notes |
|-----------|--------|-------|
| GET /content/{id} | < 50ms | KPI fetch + hierarchy lookup |
| GET /content/unified/{ch}/nav | < 200ms | 3 content queries + enrichment |
| GET /hierarchy/public/{author} | < 100ms | Works + chapters tree (cached) |
| Search (1000 items) | < 500ms | Full-text with pagination |
| POST /submit | < 1000ms | Validation + DB insert |

### Caching Strategy

```
Browser Cache:
├─ Static HTML pages: 1 hour (set via headers)
├─ Images/CSS: 1 day
└─ API responses: No cache (auth-required)

Server Cache (Redis):
├─ Hierarchy trees: 1 hour (invalidate on new work)
├─ User profiles: 30 min (invalidate on update)
├─ Search index: 5 min (full-text rebuild nightly)
└─ Session tokens: TTL match JWT expiry
```

### Database Optimization

**Most Common Queries**:

```sql
-- Navigation (called 100,000x/day)
SELECT * FROM universal_content
WHERE chapter_id = ?
  AND number_in_chapter > ?
  AND visibility = 'public'
ORDER BY number_in_chapter ASC
LIMIT 1;
-- Index: (chapter_id, number_in_chapter, visibility)

-- User's submitted items (called 1,000x/day)
SELECT * FROM universal_content
WHERE created_by = ?
  AND is_deleted = 0
ORDER BY created_at DESC;
-- Index: (created_by, is_deleted, created_at)

-- Engagement stats (called 50,000x/day)
SELECT * FROM engagement_kpis
WHERE content_type = 'universal_content'
  AND content_id = ?;
-- Index: (content_type, content_id) - UNIQUE

-- Search (called 10,000x/day)
SELECT * FROM universal_content
WHERE MATCH(main_text) AGAINST(? IN BOOLEAN MODE)
  AND visibility = 'public'
LIMIT 50;
-- Index: FULLTEXT (main_text)
```

---

## Security & Authentication

### Authorization Model

**Role-Based Access Control (RBAC)**:

```
┌─ anonymous (unauthenticated)
│  └─ Can: Read public content, search, view profiles
│
├─ registered (authenticated user)
│  └─ Can: + Submit content, like, bookmark, view dashboard
│
├─ contributor (reputation > 10)
│  └─ Can: + Batch submit, see moderation queue
│
├─ moderator
│  └─ Can: + Approve/reject submissions, edit guidelines
│
└─ admin
   └─ Can: + User management, system settings, complete DB access
```

### Authentication Flow

```
1. User login via Google OAuth
   GET https://accounts.google.com/o/oauth2/v2/auth
   ├─ client_id, redirect_uri, scopes (email, profile)
   └─ User approves

2. Google redirects to callback
   GET /api/v1/auth/google/callback?code=...
   ├─ Backend exchanges code for token
   ├─ Fetch user info (email, name)
   ├─ Create/link user account in DB
   └─ Issue JWT + refresh token

3. JWT stored in localStorage
   All subsequent requests:
   Authorization: Bearer <JWT>

4. Token refresh
   POST /api/v1/auth/refresh
   ├─ Use httpOnly refresh_token cookie
   ├─ Issue new JWT (24h expiry)
   └─ Continue session
```

### CORS & Security Headers

```
CORS (only localhost:3000 in dev, CDN domain in prod)
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
Strict-Transport-Security: max-age=31536000 (HTTPS only)
CSP: Content-Security-Policy (prevent XSS)
Rate Limiting: 100 req/minute per IP
```

---

## Key Architectural Decisions

### Decision 1: One Table vs. Multiple Tables
**Chosen**: One `universal_content` table with `content_type` discriminator

**Rationale**: 
- ✅ Scales to unlimited prosody types
- ✅ Single navigation logic
- ✅ Simpler moderation workflow
- ✅ Less code duplication

**Trade-off**: Using JSON for metadata (denormalized, not 100% ACID)

### Decision 2: Server-Side Rendering (Astro)
**Chosen**: Static pre-rendered HTML + minimal client hydration

**Rationale**:
- ✅ SEO-friendly (canonical URLs, og:meta tags)
- ✅ Fast initial load (no JS parsing needed)
- ✅ Content naturally static
- ✅ Works on slow networks

**Trade-off**: Cannot do real-time collab; build times longer

### Decision 3: JWT + OAuth2 (vs. Session Cookies)
**Chosen**: JWT tokens with fastapi + python-jose

**Rationale**:
- ✅ Stateless, scales horizontally
- ✅ No session DB queries
- ✅ Works with CDN (no sticky sessions)
- ✅ Mobile-friendly

**Trade-off**: Token revocation delayed (until expiry)

---

**Next**: See [Architecture.md](Architecture.md), especially the "Implementation Modules (Consolidated)" section, for schema and execution details.

**Last Updated**: March 28, 2026

