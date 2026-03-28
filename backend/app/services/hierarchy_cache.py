import threading
import time
from typing import Any

_CACHE_TTL_SECONDS = 3600
_cache_lock = threading.Lock()
_cache_store: dict[str, tuple[float, Any]] = {}


def _is_expired(expires_at: float) -> bool:
    return time.time() >= expires_at


def get_cached_value(key: str) -> Any | None:
    with _cache_lock:
        item = _cache_store.get(key)
        if not item:
            return None
        expires_at, value = item
        if _is_expired(expires_at):
            _cache_store.pop(key, None)
            return None
        return value


def set_cached_value(key: str, value: Any, ttl_seconds: int = _CACHE_TTL_SECONDS) -> None:
    expires_at = time.time() + max(1, int(ttl_seconds))
    with _cache_lock:
        _cache_store[key] = (expires_at, value)


def invalidate_hierarchy_cache(author_slug: str | None = None, work_slug: str | None = None) -> None:
    with _cache_lock:
        keys = list(_cache_store.keys())
        for key in keys:
            if key.startswith("authors:list"):
                _cache_store.pop(key, None)
                continue

            if author_slug and key.startswith(f"works:{author_slug}:"):
                _cache_store.pop(key, None)
                continue

            if author_slug and work_slug and key.startswith(f"chapters:{author_slug}:{work_slug}:"):
                _cache_store.pop(key, None)
                continue

            if author_slug and not work_slug and key.startswith(f"chapters:{author_slug}:"):
                _cache_store.pop(key, None)


def make_works_cache_key(author_slug: str, work_type: str | None, offset: int, limit: int) -> str:
    wt = (work_type or "all").strip().lower()
    return f"works:{author_slug}:{wt}:{offset}:{limit}"


def make_chapters_cache_key(author_slug: str, work_slug: str, offset: int, limit: int) -> str:
    return f"chapters:{author_slug}:{work_slug}:{offset}:{limit}"
