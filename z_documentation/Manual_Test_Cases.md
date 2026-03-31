# Manual End-To-End Test Cases

Last updated: March 31, 2026  
Focus: Hierarchical flow, pointer behavior, polymorphic rendering, UX, and backend consistency

## Execution Notes

1. Run each case against a seeded environment with at least one mixed-form chapter.
2. Record result as Pass or Fail with screenshot or API payload snippet.
3. For failed cases, map issue id from Issues.md.

## Test Matrix (58 Cases)

1. Case ID: E2E-001
Title: Author listing loads
Precondition: backend and frontend running
Steps: open /authors
Expected: list renders without error and links to author pages

2. Case ID: E2E-002
Title: Author to works transition
Precondition: author has at least one work
Steps: open an author page and click first work
Expected: /{author}/{work} opens with work cards

3. Case ID: E2E-003
Title: Work to chapters transition
Precondition: work has chapters
Steps: open work page and click chapter
Expected: /{author}/{work}/{chapter} loads chapter reader

4. Case ID: E2E-004
Title: Chapter stream first paint
Precondition: chapter has at least 5 nodes
Steps: refresh chapter page
Expected: first chunk appears and total count is visible

5. Case ID: E2E-005
Title: Mixed poetry rendering in one chapter
Precondition: chapter contains doha and chaupai
Steps: inspect first 10 entries
Expected: renderer switches by poetry_type without layout break

6. Case ID: E2E-006
Title: Unknown poetry type fallback
Precondition: one node has unsupported poetry_type
Steps: open chapter containing that node
Expected: generic renderer appears and page remains stable

7. Case ID: E2E-007
Title: Node detail deep link
Precondition: chapter has node id
Steps: click a chapter entry
Expected: /poetry/{id} opens with hierarchy breadcrumb and node context

8. Case ID: E2E-008
Title: Detail previous and next links
Precondition: node has neighbors
Steps: open middle node detail
Expected: both previous and next controls are visible and correct

9. Case ID: E2E-009
Title: First node edge behavior
Precondition: open first sequence in chapter
Steps: inspect nav on detail page
Expected: previous is null or disabled, next is available

10. Case ID: E2E-010
Title: Last node edge behavior
Precondition: open last sequence in chapter
Steps: inspect nav on detail page
Expected: next is null or disabled, previous is available

11. Case ID: E2E-011
Title: Gapped sequence handling
Precondition: chapter contains sequence numbers 1,2,5
Steps: open sequence 2 and evaluate nav
Expected: next resolves to sequence 5

12. Case ID: E2E-012
Title: Hanuman chain semantic check
Precondition: fixture includes Jai Hanuman, Ram dut atulit, Mahavir vikram
Steps: open Ram dut atulit node
Expected: previous points to Jai Hanuman and next points to Mahavir vikram

13. Case ID: E2E-013
Title: Breadcrumb correctness
Precondition: open any chapter page
Steps: inspect breadcrumb links
Expected: links match author, work, chapter hierarchy

14. Case ID: E2E-014
Title: Breadcrumb mobile overflow behavior
Precondition: mobile viewport
Steps: open long-title chapter
Expected: breadcrumb remains readable and does not cause horizontal page break

15. Case ID: E2E-015
Title: Load more chapter content
Precondition: chapter total greater than initial chunk
Steps: click Load More until end
Expected: new unique entries append with no duplicates

16. Case ID: E2E-016
Title: Keyboard navigation scope
Precondition: chapter page loaded
Steps: focus non-reader element and press arrow keys
Expected: reader should not hijack global navigation behavior

17. Case ID: E2E-017
Title: Reader keyboard navigation focused
Precondition: focus reader container
Steps: press left and right arrows
Expected: current highlight updates and scroll centers target entry

18. Case ID: E2E-018
Title: SEO metadata on chapter page
Precondition: chapter route open
Steps: inspect page source
Expected: canonical URL and structured data include chapter and item list

19. Case ID: E2E-019
Title: SEO metadata on detail page
Precondition: poetry detail route open
Steps: inspect page source
Expected: breadcrumb and creative work structured data are present

20. Case ID: E2E-020
Title: Public hierarchy API consistency
Precondition: api available
Steps: call /authors/{author}/works/{work}/chapters
Expected: response includes id, slug, title, number, poetry_nodes_count

21. Case ID: E2E-021
Title: Poetry stream API contract
Precondition: valid chapter id
Steps: call /api/v1/poetry/chapters/{id}/stream
Expected: hierarchy object plus paginated items with poetry_type and sequence_no

22. Case ID: E2E-022
Title: Poetry nav API contract
Precondition: valid chapter and sequence
Steps: call /api/v1/poetry/chapters/{id}/nav?sequence_no=n
Expected: current node plus optional previous and next summaries

23. Case ID: E2E-023
Title: Legacy doha navigation contract
Precondition: doha_entries seeded
Steps: call /content/doha/{id}/navigation
Expected: previous/current/next resolve correctly by chapter sequence

24. Case ID: E2E-024
Title: Concurrent reader stability
Precondition: two browser tabs same chapter
Steps: navigate independently and load more in each tab
Expected: no duplicated nodes, no stale-reader crashes

25. Case ID: E2E-025
Title: Empty chapter graceful state
Precondition: chapter exists with zero nodes
Steps: open chapter route
Expected: user sees empty-state guidance and hierarchy links, no console crash

26. Case ID: E2E-026
Title: Dashboard pending review filter accuracy
Precondition: user has at least one pending_review submission
Steps: open dashboard submissions tab and select pending filter
Expected: pending_review entries are shown and count matches API

27. Case ID: E2E-027
Title: Dashboard content links for non-doha poetry
Precondition: likes or bookmarks include chaupai or jhulana item
Steps: click content link from dashboard item
Expected: link resolves to /poetry/{id} and page loads

28. Case ID: E2E-028
Title: Audit list does not leak raw payload in hover
Precondition: admin audit logs contain before or after or metadata
Steps: hover audit table cells and inspect tooltip behavior
Expected: no raw JSON payload appears in title tooltip

29. Case ID: E2E-029
Title: Recommendations card styling integrity in production build
Precondition: run production frontend build and open detail page with recommendations
Steps: inspect recommendation type colors and hover states
Expected: type styling renders correctly without missing dynamic classes

30. Case ID: E2E-030
Title: Modal focus trap consistency
Precondition: open report modal and delete modal from different pages
Steps: tab forward and backward across controls and press Escape
Expected: focus remains trapped in modal, Escape closes, and focus returns to trigger

31. Case ID: E2E-031
Title: Reader key scope isolation
Precondition: chapter page with sidebar or top nav focusable elements
Steps: focus non-reader element then press arrow keys
Expected: reader index does not change while focus is outside reader container

32. Case ID: E2E-032
Title: Search throttling behavior for rapid typing
Precondition: open search page in all-content mode
Steps: type a 12-character query quickly and observe network panel
Expected: requests are debounced and do not spike per keystroke across all modules

33. Case ID: E2E-033
Title: Mobile chapter breadcrumb context recovery
Precondition: long author/work/chapter names
Steps: open chapter page on small viewport and navigate breadcrumb
Expected: user can access full labels without losing path context

34. Case ID: E2E-034
Title: Admin nav parity desktop vs mobile
Precondition: admin logged in
Steps: compare nav destinations on desktop sidebar and mobile menu
Expected: both navs expose same destinations and active-state cues

35. Case ID: E2E-035
Title: Moderation board keyboard flow
Precondition: moderation queue populated
Steps: tab through filters, row actions, and report panel controls
Expected: navigation order is predictable and actionable without pointer device

36. Case ID: E2E-036
Title: Canonical-only admin route mode compatibility
Precondition: backend started with legacy unprefixed routes disabled
Steps: open /admin, /admin/users, /admin/settings, and /admin/audit
Expected: all admin screens load data successfully without relying on unprefixed endpoint aliases

37. Case ID: E2E-037
Title: Moderator audit access policy parity
Precondition: moderator account with own audit events exists
Steps: login as moderator and attempt to access audit logs through intended UI path
Expected: behavior matches product policy consistently across frontend guard and backend authorization

38. Case ID: E2E-038
Title: Hierarchy create chapter work-selection request correctness
Precondition: at least one author with one work exists
Steps: open admin hierarchy page, select work in create chapter panel, inspect chapter list request
Expected: request uses valid author/work identifiers and chapter list loads without malformed URL segments

39. Case ID: E2E-039
Title: Admin auth guard canonical endpoint behavior
Precondition: backend serves canonical /api/v1 paths and valid admin token exists
Steps: open any admin page and inspect auth guard me-request network call
Expected: guard resolves authenticated user through canonical endpoint and does not depend on unprefixed /auth/me alias

40. Case ID: E2E-040
Title: Dashboard pending review filter correctness
Precondition: contributor has at least one submission in pending_review status
Steps: open /dashboard, go to submissions tab, choose Pending Review filter
Expected: pending_review submissions are visible and count aligns with /submissions/me?status=pending_review

41. Case ID: E2E-041
Title: View Published link resolves canonical content route
Precondition: contributor has approved entries across at least doha and one non-doha type
Steps: open /submissions and click View Published for each approved item
Expected: each link resolves to valid canonical detail route (for example /poetry/{id} for doha) without 404

42. Case ID: E2E-042
Title: Profile editor API path compatibility in canonical-only mode
Precondition: backend started with legacy unprefixed routes disabled and authenticated user session
Steps: open /me/edit, update name and bio, submit save
Expected: profile loads and saves successfully without dependence on unprefixed /auth/me or /users/me aliases

43. Case ID: E2E-043
Title: Dashboard engagement KPI correctness against backend aggregates
Precondition: contributor has approved public content with known likes and views
Steps: open /dashboard and compare KPI cards with backend aggregate data source
Expected: totals match canonical contributor aggregates and do not overcount or miss content types

44. Case ID: E2E-044
Title: User bookmarks and likes pagination stability
Precondition: user has more than one page of bookmarks and likes
Steps: paginate forward and backward in bookmarks and likes tabs
Expected: no duplicate rows, no skipped rows, and page counters remain accurate

45. Case ID: E2E-045
Title: Public profile privacy and presentation contract
Precondition: user has name, bio, and mixed submission states (draft, pending_review, approved)
Steps: open /users/{username} in anonymous session and inspect profile fields and stats
Expected: public-safe fields only, draft or moderation-private data not exposed, and style remains consistent with dark theme tokens

46. Case ID: E2E-046
Title: Governance checklist contract parity
Precondition: admin logged in with access to mission control panel
Steps: open admin mission control and inspect checklist payload keys in network response
Expected: UI field names and backend checklist schema match exactly with no undefined governance values

47. Case ID: E2E-047
Title: SLO failure-class label integrity
Precondition: telemetry contains at least one failed admin event with error classification
Steps: open admin SLO panel and compare rendered failure labels to SLO API payload
Expected: displayed failure class labels match payload keys and counts without blanks

48. Case ID: E2E-048
Title: Telemetry emitter coverage for critical admin actions
Precondition: admin performs users/settings/audit interactions in one session
Steps: execute representative actions and inspect telemetry ingest/export trail
Expected: critical actions produce attributable telemetry events with request or session correlation

49. Case ID: E2E-049
Title: Moderation triage idempotent recommendation logging
Precondition: pending moderation queue exists
Steps: call moderation triage endpoint repeatedly with same queue window
Expected: governance event log avoids duplicate recommendation records for unchanged submissions in short polling windows

50. Case ID: E2E-050
Title: Retention policy execution reliability
Precondition: seeded telemetry and model-governance records older than policy windows
Steps: run retention workflow in scheduled-equivalent scenario and verify deletion counts and remaining records
Expected: stale records are purged according to policy with auditable run outcome

51. Case ID: E2E-051
Title: Search route indexability policy
Precondition: search page is publicly reachable
Steps: open /search with and without query params, inspect meta robots and canonical in page source
Expected: query-result views are noindex,follow (or equivalent policy) and canonical does not point to noisy query variants

52. Case ID: E2E-052
Title: Sitemap dynamic coverage beyond default page caps
Precondition: dataset has more records than one sitemap fetch page for at least one content class
Steps: fetch /sitemap.xml and verify representative URLs from older pages are present
Expected: sitemap includes long-tail records through full pagination or sitemap index chaining

53. Case ID: E2E-053
Title: Listing-page canonical behavior under filters and pagination
Precondition: open list pages with filter and page query states (for example poetry and articles)
Steps: compare canonical tag on base list, filtered list, and paginated list URLs
Expected: canonical strategy is deterministic and avoids consolidating materially distinct index-worthy states incorrectly

54. Case ID: E2E-054
Title: Catch-all slug canonical redirect policy
Precondition: at least one content item is reachable via primary route and an alias slug route
Steps: open alias variant and inspect response and canonical tag
Expected: non-canonical variant redirects to canonical URL or is defensively noindexed

55. Case ID: E2E-055
Title: Structured-data minimum coverage by route archetype
Precondition: representative detail, list, and hub pages exist
Steps: inspect JSON-LD blocks on index, authors, poetry list, chapter detail, and poetry detail pages
Expected: each route class exposes expected schema type set (for example WebSite or CollectionPage on hubs, ItemList on lists, CreativeWork/BreadcrumbList on detail)

56. Case ID: E2E-056
Title: Robots rules alignment with index policy
Precondition: robots endpoint available
Steps: open /robots.txt and verify directives against intended public vs utility route map
Expected: low-value utility surfaces are disallowed consistently and public content routes remain crawlable

57. Case ID: E2E-057
Title: Hreflang and alternate-link correctness
Precondition: page rendered through BaseLayout
Steps: inspect head links for rel=alternate and hreflang attributes on representative pages
Expected: output is either fully valid locale cluster or intentionally minimal without partial misleading alternates

58. Case ID: E2E-058
Title: SEO metadata contract regression smoke
Precondition: run frontend integration or E2E smoke setup
Steps: assert canonical, robots, og tags, and structured data presence rules for detail, list, search, and catch-all routes
Expected: all route classes satisfy SEO contract expectations and regressions fail the suite
