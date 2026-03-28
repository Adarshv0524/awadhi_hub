# Awadhi Hub Active Issues (2026)

Last updated: March 28, 2026  
Scope: Post-verification reset after Hierarchical Poetry Expansion and Sitewide UI Overhaul

## Current Backlog Status

P0: 0  
P1: 0  
P2: 1  
P3: 2

The previous P0-P3 backlog has been cleared. Only net-new, audit-discovered debt is listed below.

## Active Technical Debt

### P2

1. IDEDIT-001: Idiom edit parity gap
	Submission edit flow does not expose idiom romanized text field, while create flow requires it. This can cause moderator-side data quality drift after edits.

### P3

1. POETRY-OBS-001: Renderer fallback observability
	Poetry dispatcher falls back correctly for unknown poetry_type but does not emit telemetry/logging, reducing visibility into unmet renderer coverage.

2. POETRY-EDGE-001: other_poetry media contract
	other_poetry currently follows text-first handling. Rich media payload and rendering policy is not yet formalized.

## Phase 4 Future Features

These are roadmap epics, not bug debt:

1. Realtime collaborative moderation and curation (WebSocket event streams).
2. Gamification progression tied to quality-reviewed contributions.
3. Reader personalization, bookmarks, and contextual learning trails.
4. Author/work dashboards with live engagement insights.

## Tracking Rules

1. Keep this file strictly unresolved-only.
2. Move completed items to archive notes, not active backlog.
3. Update this file in the same pull request as the fix.

