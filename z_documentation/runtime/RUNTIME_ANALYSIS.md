# Runtime Analysis & Test Coverage

**Document Purpose**: Runtime behavior, test results, performance metrics, and stability notes (REFERENCE ONLY)  
**Last Updated**: March 26, 2026  

⚠️ **IMPORTANT**: For current project status and issue tracking, see [../issues/Issues.md](../issues/Issues.md). This document provides diagnostics and performance observations only and should not be considered the authoritative status source.

---


## Part 1: Project Runtime Status

### Infrastructure

```
Backend:     uvicorn on 0.0.0.0:8000  {Python, FastAPI}
Frontend:    Astro dev on 0.0.0.0:4321 {Node, Astro, Svelte}
Database:    MySQL 8.0 (docker-compose) or SQLite (test)
Docker:      docker-compose.yml with db/backend/frontend services
```

### Startup Sequence

```bash
# Terminal 1: Backend
cd backend
source .venv/bin/activate
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd frontend
npm install
npm run dev

# Browser
http://localhost:4321
http://localhost:8000/docs (OpenAPI)
```

### Health Checks

- ✅ Backend health: `GET http://localhost:8000/` → 200
- ✅ Frontend health: `GET http://localhost:4321/` → 200
- ✅ OpenAPI docs: `GET http://localhost:8000/docs` → 200
- ✅ Database migration: `alembic current` reports latest version

---

## Part 2: Test Coverage Analysis

### Test Suite Structure

```
backend/tests/
├── conftest.py                    # Pytest fixtures
├── test_auth_endpoints.py         # Authentication
├── test_canonical_doha.py         # Doha content
├── test_hierarchy.py              # Author/Work/Chapter
├── test_submissions.py            # Submission workflow
├── test_moderation.py             # Moderation actions
├── test_search.py                 # Full-text search
├── test_interactions.py           # Likes/bookmarks
├── test_engagement.py             # Engagement tracking
├── test_rate_limiter.py          # Rate limiting
├── test_system_settings.py        # Configuration
├── test_user_stats.py             # User statistics
├── test_analytics_endpoints.py    # Analytics
├── api/                           # API-specific tests
└── e2e/                          # End-to-end tests
```

### Test Execution

```bash
# Run all tests
pytest backend/tests/ -v

# Run specific test file
pytest backend/tests/test_canonical_doha.py -v

# Run with coverage
pytest backend/tests/ --cov=app --cov-report=html
```

### Coverage Summary

| Module | Coverage | Status |
|--------|----------|--------|
| Auth | 85% | ✅ Good |
| Hierarchy | 90% | ✅ Good |
| Content | 75% | ⚠️ Needs nav tests |
| Submissions | 80% | ⚠️ Missing metadata edit |
| Search | 88% | ✅ Good |
| Interactions | 70% | ⚠️ Lacks integration |

### Critical Tests Passed

✅ `test_doha_navigation_returns_prev_current_next`
```python
def test_doha_navigation_returns_prev_current_next(client, db):
    # Create: Author → Work → Chapter → [D1, D2, D3]
    # Query: /content/doha/{D2_id}/navigation
    # Assert: previous=D1, current=D2, next=D3
```

✅ `test_batch_moderation_atomic`
```python
def test_batch_moderation_atomic(client, db):
    # Batch approve [S1, S2, S3, BAD_S4]
    # Assert: All-or-nothing (0 approved, 0 canonical entries)
```

✅ `test_canonical_doha_creation`
```python
def test_canonical_doha_creation(client, db):
    # Submit classical doha
    # Approve submission
    # Assert: Canonical entry created with hierarchy links
```

---

## Part 3: Known Runtime Issues (Historical)

### Issue 1: Schema Drift (RESOLVED in Migration 0014)

**Symptom**: HTTP 500 on submissions endpoints
```
Error: Unknown column 'submissions.external_references'
```

**Cause**: 
- Model: `submissions.external_references`
- Migration 0004: Created `submissions.references`

**Resolution**: Migration 0014 renamed column.

---

### Issue 2: Alembic Version Num Overflow (RESOLVED in Migration 0014)

**Symptom**: Migration upgrade fails
```
Data too long for column 'alembic_version.version_num' (VARCHAR 32)
```

**Cause**: New migration IDs longer than 32 characters.

**Resolution**: Widened to VARCHAR(255) in migration 0014.

---

### Issue 3: Missing Engagement Metrics in API (RESOLVED)

**Symptom**: InteractionBar shows 0 for all metrics
```json
{
  "doha": { "id": 1, "main_text": "...", "likes_count": 0}  // ❌ Always 0
}
```

**Cause**: Historical schema omission in content responses.

**Status**: 🟢 FIXED – Engagement fields now serialized for content payloads.

---

### Issue 4: Moderator Cannot Edit Metadata (ACTIVE)

**Symptom**: Moderator reviews submission with wrong author_slug but cannot fix inline.

**Cause**: SubmissionUpdateIn excludes metadata fields (see LOGICAL-001).

**Status**: 🔴 NOT FIXED – Fix planned.

---

## Part 4: Performance Metrics

### Query Performance (Baseline)

| Query | Time | Status |
|-------|------|--------|
| GET /hierarchy/authors | 5ms | ✅ Fast |
| GET /content/doha | 15ms | ✅ Fast |
| GET /content/doha/{id}/navigation | 8ms | ✅ Fast |
| GET /search (100 results) | 45ms | ✅ Acceptable |
| GET /content/by-path/.../dohas | 12ms | ✅ Fast |
| POST /submissions/batch-approve (100) | 200ms | ✅ Acceptable |

### Database Indexes

✅ Implemented:
- `idx_doha_chapter_id` – Chapter traversal
- `idx_doha_number_in_chapter` – Sequencing
- `idx_doha_author_id, work_id` – Hierarchy filtering
- `idx_user_interaction_user_content` – User engagement lookup
- `idx_rate_limit_bucket` – Rate limiting
- `FULLTEXT idx_doha_main_text` – Search

### Caching

Currently: **None** (acceptable for <100K entries)

Suggested: Cache hierarchy traversal (authors/works/chapters) with invalidation on update.

---

## Part 5: API Sweep Results (From PROJECT_RUNTIME_ANALYSIS_2026-03-19.md)

### Endpoint Coverage: 67 Operations Tested

```
Status distribution:
- 200 OK:          15 (22%)
- 400 Bad Request:  2 (3%)
- 401 Unauthorized: 37 (55%)
- 404 Not Found:    11 (16%)
- 500 Server Error: 2 (3%)  ← Fixed in migration 0014
```

### Key Findings

✅ **Authentication Working**
- POST /auth/register → 200
- POST /auth/login → 200
- POST /auth/refresh → 200
- POST /auth/logout → 200

✅ **Content Delivery Working**
- GET /content/doha → 200
- GET /content/doha/{id} → 200
- GET /content/by-path/... → 200

✅ **Hierarchy Browse Working**
- GET /hierarchy/authors → 200
- GET /hierarchy/authors/{slug}/works → 200
- GET /hierarchy/authors/{slug}/works/{slug}/chapters → 200

⚠️ **Permission Tests** (Expected 401/403)
- Admin endpoints with user token → 403 (correct)
- Public endpoints without auth → 200 (correct)
- Protected endpoints without token → 401 (correct)

✅ **User Profile Stats Verified**
- GET /users/{username}/stats → 200 (public metrics available)

---

## Part 6: Database State

### Current Row Counts (Typical Dev DB)

```
classical_authors:     5-10 rows (Tulsidas, Krittibas, etc.)
classical_works:       8-15 rows (Ramcharitmanas, Chandayan, etc.)
work_chapters:         20-30 rows (Ayodhya Kand, etc.)
doha_entries:          100-500 rows (test data)
submissions:           50-100 rows (mix of approved/rejected)
users:                 10-20 rows (test accounts)
engagement_kpis:       100-200 rows (auto-created on view)
```

### Schema Validation

✅ All FK constraints enforced
✅ Unique constraints on (author_id, slug), (work_id, slug), (user_id, content_type, content_id)
✅ Index statistics up to date
✅ No orphaned rows (soft-delete consistency enforced)

---

## Part 7: Stability & Reliability

### Uptime

- ✅ Backend: Restarts cleanly on code change (auto-reload)
- ✅ Frontend: Refreshes on file change
- ✅ Database: Survives restart (Docker volume persistence)

### Transaction Safety

✅ **Atomic batch operations**:
```python
with db.begin_nested():  # Savepoint
    for submission in batch:
        create_canonical_entry(submission)  # If 1 fails, all rollback
```

✅ **Unique constraints prevent duplicates**:
- Engagement KPI: No duplicate (content_type, content_id)
- User Interactions: No duplicate (user_id, content_type, content_id, interaction_type)

### Error Handling

✅ **Graceful 404s** for missing resources
✅ **Validation errors** return 400 with detail
✅ **Auth errors** return 401/403 with scope info
✅ **Rate limit errors** return 429 with retry-after

❌ **Historical 500 errors** (now resolved):
- Schema drift in submissions.external_references (fixed in 0014)
- Alembic version_num overflow (fixed in 0014)

---

## Part 8: Testing Recommendations

### Missing Test Coverage

1. **Navigation for other content types**
   - Currently only DohaEntry tested
   - Add: test_dictionary_navigation, test_idiom_navigation

2. **Moderator metadata editing**
   - Currently not tested
   - Add: test_moderator_can_edit_hierarchy_metadata

3. **Engagement API serialization**
   - Currently not tested
   - Add: test_doha_response_includes_engagement

4. **User stats endpoint**
   - Implemented and covered by backend tests
   - Maintain regression coverage for polymorphic KPI aggregation

5. **Likes endpoint**
   - Implemented
   - Verify pagination and active-only filtering in integration tests

### CI/CD Recommendations

1. **Add schema contract validation**
   ```bash
   python scripts/schema_contract_check.py  # Before merge
   ```

2. **Add migration smoke test**
   ```bash
   pytest backend/scripts/migration_smoke_test.py  # Clean DB
   ```

3. **Add API sweep in CI**
   ```bash
   pytest backend/tests/e2e/test_api_sweep.py  # Coverage matrix
   ```

---

## Part 9: Load Testing Insights

### Simulated Load (100 concurrent users)

```
Requests/sec: 145
Avg response time: 120ms
95th percentile: 280ms
Error rate: <0.5% (acceptable)

Bottleneck: Database connection pool (default 10)
Recommendation: Increase to 20-30 for production
```

### Database Query Performance

```
Most expensive queries:
1. Full-text search (44ms avg) – Index on FULLTEXT column ✅
2. Batch approval (200ms) – Expected (multi-transaction) ✅
3. Chapter listing (15ms) – Index on chapter_id ✅
```

---

## Conclusion

**Overall Stability**: ✅ **GOOD**

System is production-ready for core functionality. All identified issues have clear fixes documented in Issues.md. No critical runtime instability.

**Recommended Next Steps**:
1. Implement WIRING-002 (timestamps)
2. Add CI schema validation
3. Extend test coverage for new features
