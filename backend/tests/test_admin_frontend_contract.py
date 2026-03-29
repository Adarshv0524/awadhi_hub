from __future__ import annotations

import re
from pathlib import Path

from app.main import app


FRONTEND_ADMIN_WRAPPER = (
    Path(__file__).resolve().parents[2] / "frontend" / "src" / "lib" / "admin.ts"
)


def _is_placeholder(segment: str) -> bool:
    return segment.startswith("{") and segment.endswith("}")


def _path_matches(frontend_path: str, backend_path: str) -> bool:
    frontend_segments = [s for s in frontend_path.split("/") if s]
    backend_segments = [s for s in backend_path.split("/") if s]

    if len(frontend_segments) != len(backend_segments):
        return False

    for f_seg, b_seg in zip(frontend_segments, backend_segments):
        if _is_placeholder(f_seg) or _is_placeholder(b_seg):
            continue
        if f_seg != b_seg:
            return False

    return True


def _extract_frontend_admin_paths(source: str) -> set[str]:
    raw_paths = set(re.findall(r"/admin/[A-Za-z0-9_/${}?=&-]+", source))
    normalized: set[str] = set()

    for path in raw_paths:
        path = path.split("?", 1)[0]
        path = re.sub(r"\$\{[^}]+\}", "{param}", path)
        normalized.add(path)

    return normalized


def test_frontend_admin_wrapper_paths_match_backend_route_inventory() -> None:
    source = FRONTEND_ADMIN_WRAPPER.read_text(encoding="utf-8")
    frontend_paths = _extract_frontend_admin_paths(source)

    assert frontend_paths, "No /admin/* paths were found in frontend/src/lib/admin.ts"

    backend_paths = {
        route.path
        for route in app.routes
        if hasattr(route, "path") and isinstance(route.path, str) and route.path.startswith("/admin/")
    }

    unmatched = sorted(
        frontend_path
        for frontend_path in frontend_paths
        if not any(_path_matches(frontend_path, backend_path) for backend_path in backend_paths)
    )

    assert not unmatched, (
        "Frontend admin wrapper contains paths that do not exist in backend route inventory: "
        f"{unmatched}"
    )
