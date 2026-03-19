# Backend TODO: User Likes Endpoint

## Issue: Missing Likes Retrieval Endpoint

**Status**: Not implemented  
**Priority**: Medium (User Dashboard MVP feature)  
**Frontend Ready**: Dashboard UI implemented with dummy data

---

## Required API Endpoint

### GET /interactions/users/:userId/likes

Retrieves paginated list of content items liked by a specific user.

**Purpose**: 
- Enable users to view all content they've liked in their dashboard
- Provide "My Likes" tab functionality

**Request Parameters**:
```
GET /interactions/users/{userId}/likes?limit={limit}&offset={offset}
```

| Parameter | Type    | Required | Default | Description                          |
|-----------|---------|----------|---------|--------------------------------------|
| `userId`  | integer | Yes      | -       | User ID (path parameter)             |
| `limit`   | integer | No       | 20      | Number of items per page             |
| `offset`  | integer | No       | 0       | Pagination offset                    |

**Response Format**:
```json
{
  "count": 42,
  "results": [
    {
      "content_type": "doha",
      "content_id": 123,
      "created_at": "2024-01-15T10:30:00Z"
    },
    {
      "content_type": "dictionary",
      "content_id": 456,
      "created_at": "2024-01-10T14:20:00Z"
    }
  ]
}
```

**Response Fields**:
- `count`: Total number of liked items for the user
- `results`: Array of liked content items
  - `content_type`: Type of content ("doha", "dictionary", "idiom", "article")
  - `content_id`: ID of the liked content item
  - `created_at`: When the like was created (ISO 8601 timestamp)

**Status Codes**:
- `200 OK`: Successfully retrieved likes
- `401 Unauthorized`: User not authenticated
- `403 Forbidden`: User cannot view another user's likes (privacy)
- `404 Not Found`: User does not exist

---

## Database Schema Reference

**Table**: `user_interactions`

```sql
CREATE TABLE user_interactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content_type VARCHAR(50) NOT NULL,  -- 'doha', 'dictionary', 'idiom', 'article'
    content_id INTEGER NOT NULL,
    interaction_type VARCHAR(50) NOT NULL,  -- 'like', 'bookmark'
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, content_type, content_id, interaction_type)
);
```

**Query Example**:
```sql
SELECT content_type, content_id, created_at
FROM user_interactions
WHERE user_id = $1 
  AND interaction_type = 'like'
ORDER BY created_at DESC
LIMIT $2 OFFSET $3;
```

---

## Implementation Notes

### Backend Service
- Create new function in `app/services/interaction_service.py`:
  ```python
  async def get_user_likes(
      db: Session,
      user_id: int,
      limit: int = 20,
      offset: int = 0
  ) -> Dict[str, Any]:
      """Retrieve paginated likes for a user."""
      # Count total likes
      total = db.query(UserInteraction).filter(
          UserInteraction.user_id == user_id,
          UserInteraction.interaction_type == "like"
      ).count()
      
      # Get paginated results
      likes = db.query(UserInteraction).filter(
          UserInteraction.user_id == user_id,
          UserInteraction.interaction_type == "like"
      ).order_by(
          UserInteraction.created_at.desc()
      ).limit(limit).offset(offset).all()
      
      return {
          "count": total,
          "results": [
              {
                  "content_type": like.content_type,
                  "content_id": like.content_id,
                  "created_at": like.created_at.isoformat()
              }
              for like in likes
          ]
      }
  ```

### API Endpoint
- Add to `app/api/v1/interactions.py` (or relevant router file):
  ```python
  @router.get("/users/{user_id}/likes")
  async def get_user_likes_endpoint(
      user_id: int,
      limit: int = Query(20, ge=1, le=100),
      offset: int = Query(0, ge=0),
      current_user: User = Depends(get_current_user),
      db: Session = Depends(get_db)
  ):
      """Get paginated likes for a user."""
      # Privacy: Users can only view their own likes
      if current_user.id != user_id and current_user.role not in ["admin", "moderator"]:
          raise HTTPException(status_code=403, detail="Cannot view other users' likes")
      
      result = await get_user_likes(db, user_id, limit, offset)
      return result
  ```

### Privacy Considerations
- **Default Privacy**: Users should only see their own likes
- **Exception**: Admins/moderators may need access for moderation purposes
- **Future Feature**: Consider adding a privacy setting to make likes public/private

### Testing Requirements
1. **Unit Tests**:
   - Test `get_user_likes` service function
   - Verify pagination works correctly
   - Test empty results (user with no likes)

2. **API Tests**:
   - Test authenticated user can retrieve their own likes
   - Test user cannot retrieve another user's likes (403 Forbidden)
   - Test admin/moderator can retrieve any user's likes
   - Test pagination parameters work correctly
   - Test limit validation (min 1, max 100)

3. **Integration Tests**:
   - Test with actual like interactions
   - Verify likes are ordered by created_at DESC
   - Test with different content types

---

## Related Frontend Implementation

**File**: `frontend/src/components/dashboard/DashboardClient.svelte`

**Current State**: Implemented with dummy data  
**Waiting For**: Backend API endpoint

**Frontend Code Location**:
```svelte
{:else if activeTab === "likes"}
  <!-- Likes Tab -->
  <h3 class="text-xl font-semibold text-cyan-400 mb-6">My Likes</h3>

  <!-- Empty State (Dummy implementation - TODO: Backend needed) -->
  <div class="text-center py-16">
    <div class="text-6xl mb-4">❤️</div>
    <h4 class="text-xl font-semibold text-slate-300 mb-2">Likes feature coming soon</h4>
    ...
  </div>
{/if}
```

**Once Backend is Ready**:
1. Add `getUserLikes()` function to `frontend/src/lib/interactions.ts`:
   ```typescript
   export async function getUserLikes(
     userId: number,
     limit = 20,
     offset = 0
   ) {
     return api(
       `/interactions/users/${userId}/likes?limit=${limit}&offset=${offset}`
     );
   }
   ```

2. Update DashboardClient.svelte:
   - Call `getUserLikes()` in `onMount()`
   - Replace dummy empty state with actual likes list
   - Add pagination controls (like bookmarks tab)
   - Show content type badges and links

---

## Acceptance Criteria

- [ ] API endpoint `/interactions/users/:userId/likes` created
- [ ] Endpoint returns paginated results with `{count, results}` format
- [ ] Privacy check: users can only view their own likes (except admin/moderator)
- [ ] Results ordered by `created_at DESC` (newest first)
- [ ] Pagination works correctly with `limit` and `offset` parameters
- [ ] Unit tests written and passing
- [ ] API endpoint tests written and passing
- [ ] Documentation updated in API docs
- [ ] Frontend can successfully call endpoint and display results

---

## Estimated Effort

- **Backend Implementation**: 2-3 hours
  - Service function: 30 min
  - API endpoint: 30 min
  - Privacy logic: 30 min
  - Tests: 1-2 hours

- **Frontend Integration**: 1 hour
  - Add `getUserLikes()` function: 15 min
  - Update dashboard component: 30 min
  - Testing: 15 min

**Total**: 3-4 hours

---

## Notes

- Similar pattern to existing `getUserBookmarks()` endpoint
- Can reuse privacy/pagination logic
- Frontend UI already designed and implemented
- No database schema changes needed (table already exists)
- Low complexity, high user value feature
