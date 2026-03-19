# Backend Feature Request: User Public Statistics API

## Overview
The public user profile page (`/users/:username`) currently displays dummy/placeholder statistics. We need a backend API endpoint to provide real user contribution statistics.

## Required Endpoint

### `GET /users/:username/stats`

**Description:** Returns public statistics for a user's approved contributions.

**Response Model:**
```python
class UserPublicStatsOut(BaseModel):
    public_submissions: int      # Count of approved public submissions
    approved_count: int          # Total count of approved content
    likes_received: int          # Total likes on user's approved content
    bookmarks_received: int      # Total bookmarks on user's approved content (optional)
    
    class Config:
        orm_mode = True
```

**Example Response:**
```json
{
  "public_submissions": 42,
  "approved_count": 38,
  "likes_received": 156,
  "bookmarks_received": 89
}
```

## Implementation Requirements

### Database Queries Needed

1. **Public Submissions Count:**
   - Query `Submission` table
   - Filter: `contributor_id = user.id`
   - Filter: `status = 'approved'`
   - Filter: `visibility = 'public'`
   - Filter: `is_deleted = False`
   - Count results

2. **Approved Count:**
   - Query `Submission` table
   - Filter: `contributor_id = user.id`
   - Filter: `status = 'approved'`
   - Filter: `is_deleted = False`
   - Count results

3. **Likes Received:**
   - Join `Submission` with `UserInteraction`
   - Filter submissions by: `contributor_id = user.id` AND `status = 'approved'`
   - Filter interactions by: `interaction_type = 'like'` AND `active = True`
   - Sum/count likes

4. **Bookmarks Received (Optional):**
   - Similar to likes but filter by `interaction_type = 'bookmark'`

### Privacy Considerations

- ✅ Only count **approved** content (never show draft/pending/rejected counts publicly)
- ✅ Only show **public** submissions (exclude private visibility)
- ✅ Never expose email, passwords, or sensitive user data
- ✅ This endpoint should be publicly accessible (no auth required)
- ✅ Consider caching this data (updated on submission approval/rejection)

### File Locations

**Backend File:** `backend/app/api/v1/users.py`

**Current Code:**
```python
@router.get("/{username}", response_model=PublicUserOut)
def get_public_user(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

**Add New Endpoint:**
```python
@router.get("/{username}/stats", response_model=UserPublicStatsOut)
def get_user_stats(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Query for stats
    public_submissions = db.query(Submission).filter(
        Submission.contributor_id == user.id,
        Submission.status == 'approved',
        Submission.visibility == 'public',
        Submission.is_deleted == False
    ).count()
    
    approved_count = db.query(Submission).filter(
        Submission.contributor_id == user.id,
        Submission.status == 'approved',
        Submission.is_deleted == False
    ).count()
    
    # TODO: Implement likes/bookmarks aggregation
    likes_received = 0
    bookmarks_received = 0
    
    return UserPublicStatsOut(
        public_submissions=public_submissions,
        approved_count=approved_count,
        likes_received=likes_received,
        bookmarks_received=bookmarks_received
    )
```

## Frontend Integration

**Frontend File:** `frontend/src/pages/users/[username].astro`

**Current Dummy Implementation:**
```typescript
const dummyStats = {
  public_submissions: 0,
  approved_count: 0,
  likes_received: 0
};
```

**Replace With:**
```typescript
let userStats = null;
try {
  userStats = await api(`/users/${username}/stats`);
} catch (e) {
  // Fall back to dummy stats if endpoint not available
  userStats = {
    public_submissions: 0,
    approved_count: 0,
    likes_received: 0
  };
}
```

## Testing Checklist

- [ ] Endpoint returns correct count for users with approved submissions
- [ ] Endpoint returns zeros for users with no approved content
- [ ] Endpoint returns 404 for non-existent users
- [ ] Privacy: Draft submissions are NOT counted
- [ ] Privacy: Rejected submissions are NOT counted in public stats
- [ ] Privacy: Private visibility submissions are NOT counted in public_submissions
- [ ] Performance: Query is optimized (consider adding indexes)
- [ ] Optional: Add caching layer for frequently accessed profiles

## SEO Considerations

✅ **Already Implemented in Frontend:**
- Canonical URL: `<link rel="canonical" href="https://awadhi.new/users/${username}" />`
- Meta description includes role and join year
- Semantic HTML with proper headings
- Structured data with profile information
- Public profiles are crawlable (no noindex)

## Priority

**Priority:** Medium
**Effort:** Low (2-3 hours)
**Impact:** High (improves user profile credibility and engagement)

## Related Files

- Backend: `backend/app/api/v1/users.py`
- Backend Models: `backend/app/db/models.py` (User, Submission, UserInteraction)
- Frontend: `frontend/src/pages/users/[username].astro`

## Notes

- Current implementation shows "0" for all stats (dummy data)
- Frontend is already styled and ready to display real data
- No breaking changes - frontend has fallback to dummy data
- Consider adding this to the `/me` endpoint as well for logged-in users
