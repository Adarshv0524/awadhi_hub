# Awadhi Hub Active Issues (2026)

Last updated: March 28, 2026  
Scope: Post-verification reset after Hierarchical Poetry Expansion and Sitewide UI Overhaul

## 0) Tracker Policy

This tracker contains unresolved items only. Completed issues should be removed from active sections and preserved in archive or release notes.

Issue severity definitions:

1. P0: Production blocker, data loss, or security-critical issue.
2. P1: High-risk correctness or reliability issue requiring near-term fix.
3. P2: Medium-priority engineering debt with measurable quality impact.
4. P3: Low-priority debt and polish tasks.

Issue entry format:

1. ID and title.
2. Scope and affected layers.
3. Impact.
4. Proposed remediation.
5. Exit criteria.

## Current Backlog Status

P0: 0  
P1: 0  
P2: 0  
P3: 0

The previous P0-P3 backlog has been cleared. Only net-new, audit-discovered debt is listed below.

## 1) Active Debt Details

## Active Technical Debt

No unresolved P3 items.

## 2) Suggested Execution Order

No active debt items. Next execution cycle should focus on roadmap features only.

## Phase 4 Future Features

These are roadmap epics, not bug debt:

1. Realtime collaborative moderation and curation (WebSocket event streams).
2. Gamification progression tied to quality-reviewed contributions.
3. Reader personalization, bookmarks, and contextual learning trails.
4. Author/work dashboards with live engagement insights.

## 3) Future Feature Elaboration

1. Realtime moderation and curation
   Stream moderation events and queue updates to reduce stale dashboard state and improve reviewer throughput.

2. Gamification and reputation progression
   Expand contribution quality scoring, badge unlock logic, and transparent progression milestones.

3. Reader personalization
   Introduce saved reading states, chapter progression memory, and preference-aware discovery signals.

4. Analytics and dashboards
   Provide author/work/chapter performance views with trend windows and quality diagnostics.

## 4) Non-Goals for Current Cycle

1. No table-per-poetry-type schema expansion.
2. No merging of dictionary or idiom entities into poetry_nodes.
3. No undocumented API contract changes.

## Tracking Rules

1. Keep this file strictly unresolved-only.
2. Move completed items to archive notes, not active backlog.
3. Update this file in the same pull request as the fix.

## 5) Update Cadence

1. Re-evaluate active items after each merge batch affecting architecture.
2. Run monthly debt triage to adjust severity and order.
3. Perform full audit checkpoint once per quarter or before major release.
