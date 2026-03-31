# Awadhi New Documentation

Last updated: March 31, 2026  
Audit status: Complete restructure for hierarchy and content delivery

## Aim Of The Project

Awadhi New is a hierarchy-first literary platform for classical and community content.  
Its core goal is to preserve reading order and context across:

1. Author
2. Work
3. Chapter
4. Content node

The platform must support mixed verse forms inside one chapter stream while keeping stable navigation, SEO-safe URLs, and moderation traceability.

## Current Implementation Status

### Implemented

1. Hierarchy entities and public hierarchy APIs are active.
2. Polymorphic poetry delivery is active through poetry_nodes plus poetry_type.
3. Chapter-level streaming and chapter-local next or previous resolution are active.
4. Chapter page rendering supports mixed forms through a dispatcher.
5. Dedicated detail pages for nodes exist under /poetry/{id}.

### Audit Reality Check

1. Navigation algorithm is functionally correct for gapped sequences in tests.
2. Direct fixture coverage for the Hanuman Chalisa example lines is not present.
3. Frontend chapter reader has UX and accessibility risks under keyboard and long-list usage.
4. Backend chapter stream has avoidable performance overhead under high volume.

## Core Documentation Set

1. Architecture.md
Deep implementation map for hierarchy, pointer logic, chapter page composition, and data flow.

2. Issues.md
GitHub-style audit log categorized by Wiring, Styling, Data Structure, Optimization, and Logical Flow.

3. api/API_REFERENCE.md
API reference with an audited section for content delivery endpoints and contracts.

4. Manual_Test_Cases.md
End-to-end manual validation suite with 58 hard test cases.

## Notes For Contributors

1. This folder is intentionally consolidated; avoid adding parallel architecture or issue markdowns.
2. Update Architecture.md and Issues.md in the same pull request as any hierarchy or navigation change.
3. If a previously documented issue is fixed, move it to the Resolved section in Issues.md.
