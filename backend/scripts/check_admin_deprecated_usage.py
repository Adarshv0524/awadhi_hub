from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCAN_DIRS = [
    ROOT / "frontend" / "src" / "pages" / "admin",
    ROOT / "frontend" / "src" / "components" / "admin",
    ROOT / "frontend" / "src" / "lib" / "analytics.ts",
]

# Deprecated admin analytics endpoints that must not be referenced by dashboards.
DEPRECATED_PATTERNS = {
    r"/analytics/top": "GET /analytics/top",
    r"/analytics/growth": "GET /analytics/growth",
    r"/analytics/demand": "GET /analytics/demand",
    r"/admin/analytics/content-performance": "GET /admin/analytics/content-performance",
    r"/admin/analytics/contributor-trends": "GET /admin/analytics/contributor-trends",
}


def iter_files() -> list[Path]:
    files: list[Path] = []
    for entry in SCAN_DIRS:
        if entry.is_file():
            files.append(entry)
            continue
        if entry.is_dir():
            files.extend(sorted(p for p in entry.rglob("*") if p.suffix in {".ts", ".svelte", ".astro"}))
    return files


def main() -> int:
    files = iter_files()
    violations: list[str] = []

    for path in files:
        source = path.read_text(encoding="utf-8")
        relative = path.relative_to(ROOT)
        for pattern, label in DEPRECATED_PATTERNS.items():
            for match in re.finditer(pattern, source):
                line = source.count("\n", 0, match.start()) + 1
                violations.append(f"{relative}:{line} -> {label}")

    if violations:
        print("Deprecated admin analytics endpoint references found:")
        for item in violations:
            print(f" - {item}")
        print(f"Total deprecated endpoint references: {len(violations)}")
        return 1

    print("Deprecated admin analytics endpoint references: 0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
