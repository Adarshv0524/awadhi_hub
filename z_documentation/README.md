# Awadhi New Documentation Hub

Last updated: March 28, 2026

This folder contains the consolidated technical documentation after a full re-audit focused on consistency, optimization, SEO, and UI/UX.

## ⚠️ Status & Issues: Single Source of Truth

**All project status information is tracked in [issues/Issues.md](issues/Issues.md).**

Do NOT rely on status claims in other documentation files for current project state. Always check Issues.md for:
- Active issues and their priority order
- Resolved/completed work items
- Current implementation status

When implementation status changes, update issues/Issues.md first, then reflect changes in Architecture.md and supporting docs.

## Core files

- README.md
  - This index and navigation guide.
- Architecture.md
  - High-level architecture summary and design decisions.

## Subfolders

- api/API_REFERENCE.md
  - Backend and frontend API contract reference.
- architecture/CONTENT_DELIVERY_ARCHITECTURE.md
  - Detailed hierarchy, content linking, and navigation design.
- audit/MODULE_STATUS_REPORT.md
  - Per-module implementation breakdown and technical details (reference only; current status in Issues.md).
- issues/Issues.md
  - **Active issue log from latest complete audit. ONLY authoritative source for project status.**
- runtime/RUNTIME_ANALYSIS.md
  - Runtime behavior, diagnostics, and performance notes (reference only; active issues in Issues.md).

## What changed in this consolidation

- Removed redundant and stale markdown files from archive and legacy audit snapshots.
- Kept only actively useful documents needed for development and maintenance.
- Established issues/Issues.md as the single authoritative tracker for all status information.
- Linked all supporting documentation back to this Issues.md for status verification.

## Recommended reading order

1. **issues/Issues.md** (always first for current status)
2. Architecture.md
3. architecture/CONTENT_DELIVERY_ARCHITECTURE.md
4. api/API_REFERENCE.md
5. audit/MODULE_STATUS_REPORT.md (technical reference, not status authority)
6. runtime/RUNTIME_ANALYSIS.md (diagnostics and observations)

## Maintenance rule (CRITICAL for documentation governance)

**When implementation status changes:**

1. **Update issues/Issues.md first** (add to COMPLETED or update Open status)
2. **Reflect major architectural changes** in Architecture.md and architecture/CONTENT_DELIVERY_ARCHITECTURE.md
3. **Keep all other files stable** as reference material only
4. **Never add task status claims** in any file other than issues/Issues.md to prevent drift

This single-authority model ensures readers always find current status in one place.

