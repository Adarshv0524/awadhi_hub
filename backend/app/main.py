# app/main.py
from fastapi import FastAPI
import os
from contextlib import asynccontextmanager
from time import perf_counter
from uuid import uuid4
import hashlib

#middleware
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request

from app.api.v1 import auth as auth_router
from app.api.v1 import admin_users as admin_users_router
from app.api.v1 import users as users_router
from app.api.v1 import hierarchy_public as hierarchy_public_router
from app.api.v1 import hierarchy_admin as hierarchy_admin_router
from app.api.v1 import submissions as submissions_router  
from app.api.v1 import moderation as moderation_router 
from app.api.v1 import content as content_router 
from app.api.v1 import search as search_router
from app.api.v1 import analytics as analytics_router
from app.api.v1 import admin_settings as admin_settings_router
from app.api.v1 import admin_audit as admin_audit_router
# NEW: Add dictionary, idiom, article routers
from app.api.v1 import dictionary as dictionary_router
from app.api.v1 import idiom as idiom_router
from app.api.v1 import article as article_router
from app.api.v1 import recommendations as rec_router
from app.api.v1 import interactions as interactions_router
from app.api.v1 import poetry as poetry_router
from app.api.v1 import telemetry as telemetry_router
from app.api.v1 import ai_ops as ai_ops_router


from app.core.settings import settings
from app.auth.jwt import decode_token
from app.db.models import User
from app.db.session import SessionLocal, get_db
from app.services.admin_telemetry_service import AdminTelemetryEventData, persist_admin_telemetry_event
from app.services.audit_service import record_audit


def _required_env_value(name: str) -> str:
    value = (os.getenv(name) or "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _validate_required_env() -> None:
    # Accept either modern env names (DATABASE_URL/SECRET_KEY/OAUTH_CLIENT_ID)
    # or existing project settings (MYSQL_*/JWT_SECRET_KEY/GOOGLE_CLIENT_ID).
    database_url = (os.getenv("DATABASE_URL") or "").strip()
    mysql_ready = all(
        (os.getenv(name) or "").strip()
        for name in ["MYSQL_HOST", "MYSQL_PORT", "MYSQL_USER", "MYSQL_DATABASE"]
    )
    if not database_url and not mysql_ready:
        raise RuntimeError("Missing database configuration: set DATABASE_URL or MYSQL_* variables")

    secret_key = (os.getenv("SECRET_KEY") or os.getenv("JWT_SECRET_KEY") or "").strip()
    if not secret_key:
        raise RuntimeError("Missing required environment variable: SECRET_KEY (or JWT_SECRET_KEY)")

    oauth_client_id = (os.getenv("OAUTH_CLIENT_ID") or os.getenv("GOOGLE_CLIENT_ID") or "").strip()
    if not oauth_client_id:
        raise RuntimeError("Missing required environment variable: OAUTH_CLIENT_ID (or GOOGLE_CLIENT_ID)")

    if secret_key.lower() in {"replace-me", "changeme", "secret"}:
        raise RuntimeError("SECRET_KEY uses an insecure placeholder value")

    if oauth_client_id.lower() in {"replace-me", "changeme", "test"}:
        raise RuntimeError("OAUTH_CLIENT_ID uses an insecure placeholder value")


@asynccontextmanager
async def lifespan(app: FastAPI):
    _validate_required_env()
    yield


app = FastAPI(title="Awadhi Corpus Backend", debug=settings.APP_DEBUG, lifespan=lifespan)


def _is_admin_observability_path(path: str) -> bool:
    return path.startswith("/admin/") or path.startswith("/api/v1/admin/")


def _failure_class_from_status(status_code: int) -> str | None:
    if status_code < 400:
        return None
    if status_code == 401:
        return "auth"
    if status_code == 403:
        return "permission"
    if status_code == 404:
        return "not_found"
    if status_code == 429:
        return "rate_limit"
    if 400 <= status_code < 500:
        return "client"
    return "server"


def _module_from_path(path: str) -> str:
    p = path.lower()
    if "/admin/users" in p:
        return "users"
    if "/admin/system_settings" in p:
        return "settings"
    if "/admin/hierarchy" in p or p.startswith("/authors"):
        return "hierarchy"
    if "/admin/audit" in p:
        return "audit"
    if "/moderation" in p:
        return "moderation"
    return "analytics"


def _action_from_request(method: str, path: str, status_code: int) -> str:
    method = (method or "GET").upper()
    p = path.lower()
    if "export" in p:
        return "export"
    if "approve" in p:
        return "approve"
    if "reject" in p:
        return "reject"
    if method == "POST":
        return "create"
    if method in {"PUT", "PATCH"}:
        return "update"
    if method == "DELETE":
        return "delete"
    if method == "GET":
        return "view"
    if status_code >= 400:
        return "view"
    return "view"


def _extract_resource(path: str) -> tuple[str | None, str | None]:
    parts = [p for p in path.strip("/").split("/") if p]
    if len(parts) >= 2 and parts[0] == "api" and parts[1] == "v1":
        parts = parts[2:]
    if not parts:
        return None, None

    # /admin/<resource>/<id>
    if len(parts) >= 2 and parts[0] == "admin":
        resource = parts[1]
        for part in parts[2:]:
            if part.isdigit():
                return resource, part
        return resource, None

    # /authors/{slug}/works/{slug}/chapters/{id}
    if parts[0] == "authors":
        return "authors", parts[1] if len(parts) > 1 else None

    return parts[0], None


def _should_write_audit(method: str, path: str) -> bool:
    m = (method or "").upper()
    if m not in {"POST", "PUT", "PATCH", "DELETE"}:
        return False
    if path.startswith("/health"):
        return False
    if path.startswith("/api/v1/telemetry/"):
        return False
    return True


def _path_without_version(path: str) -> str:
    if path.startswith("/api/v1/"):
        return "/" + path[len("/api/v1/"):]
    if path == "/api/v1":
        return "/"
    return path


def _state_hash(raw: str | None) -> str | None:
    if not raw:
        return None
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _resolve_actor(authorization_header: str | None, db) -> tuple[int | None, str]:
    if not authorization_header or not authorization_header.startswith("Bearer "):
        return None, "anonymous"

    token = authorization_header.split(" ", 1)[1]
    try:
        payload = decode_token(token)
        user_id = int(payload.get("sub"))
    except Exception:
        return None, "unknown"

    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None, "unknown"
        return user.id, user.role or "unknown"
    except Exception:
        return None, "unknown"


def _open_telemetry_db_session(request: Request):
    provider = request.app.dependency_overrides.get(get_db, get_db)
    db_gen = provider()
    db = next(db_gen)
    return db, db_gen


@app.middleware("http")
async def admin_observability_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or request.headers.get("x-request-id") or str(uuid4())
    start = perf_counter()
    response = None
    error = None

    try:
        response = await call_next(request)
        return response
    except Exception as exc:
        error = exc
        raise
    finally:
        latency_ms = round((perf_counter() - start) * 1000.0, 2)
        path = request.url.path
        if response is not None:
            response.headers["X-Request-ID"] = request_id

        should_log = _is_admin_observability_path(path) and not path.startswith("/api/v1/telemetry/")

        if should_log:
            status_code = response.status_code if response is not None else 500
            result = "success" if status_code < 400 and error is None else "failure"
            module = _module_from_path(path)
            action = _action_from_request(request.method, path, status_code)
            resource_type, resource_id = _extract_resource(path)
            error_code = _failure_class_from_status(status_code)
            raw_before = request.headers.get("if-match") or request.headers.get("x-before-state")
            raw_after = response.headers.get("etag") if response is not None else None

            db = None
            db_gen = None
            try:
                db, db_gen = _open_telemetry_db_session(request)
                actor_user_id, actor_role = _resolve_actor(request.headers.get("Authorization"), db)
                persist_admin_telemetry_event(
                    db,
                    AdminTelemetryEventData(
                        session_id=request.cookies.get("session_id") or request.headers.get("X-Session-ID"),
                        request_id=request_id,
                        actor_user_id=actor_user_id,
                        actor_role=actor_role,
                        module=module,
                        action=action,
                        resource_type=resource_type,
                        resource_id=resource_id,
                        before_state_hash=_state_hash(raw_before),
                        after_state_hash=_state_hash(raw_after),
                        result=result,
                        error_code=error_code,
                        latency_ms=latency_ms,
                        client_meta={
                            "path": path,
                            "method": request.method,
                            "query": request.url.query,
                            "status_code": status_code,
                            "exception": type(error).__name__ if error else None,
                        },
                    ),
                )
            except Exception:
                # Telemetry should never block serving API responses.
                pass
            finally:
                if db_gen is not None:
                    try:
                        db_gen.close()
                    except Exception:
                        pass
                elif db is not None:
                    try:
                        db.close()
                    except Exception:
                        pass

        if _should_write_audit(request.method, path):
            status_code = response.status_code if response is not None else 500
            result = "success" if status_code < 400 and error is None else "failure"
            resource_type, resource_id_raw = _extract_resource(path)
            resource_id = int(resource_id_raw) if resource_id_raw and resource_id_raw.isdigit() else None

            db = None
            db_gen = None
            try:
                db, db_gen = _open_telemetry_db_session(request)
                actor_user_id, _ = _resolve_actor(request.headers.get("Authorization"), db)
                record_audit(
                    db=db,
                    actor_user_id=actor_user_id,
                    action=f"http:{request.method.upper()}:{_path_without_version(path)}",
                    resource_type=resource_type,
                    resource_id=resource_id,
                    metadata={
                        "request_id": request_id,
                        "method": request.method,
                        "path": path,
                        "query": request.url.query,
                        "status_code": status_code,
                        "result": result,
                    },
                )
                db.commit()
            except Exception:
                try:
                    if db is not None:
                        db.rollback()
                except Exception:
                    pass
            finally:
                if db_gen is not None:
                    try:
                        db_gen.close()
                    except Exception:
                        pass
                elif db is not None:
                    try:
                        db.close()
                    except Exception:
                        pass

# CORS configuration
# In production, set CORS_ORIGINS env variable with your frontend domain
allowed_origins = [
    "http://localhost:4321",  # Astro dev server
    "http://127.0.0.1:4321",  # IPv4 localhost
    "http://localhost:4322",  # Alternate Astro/Vite dev port
    "http://127.0.0.1:4322",  # Alternate IPv4 localhost port
]

# Add production origins from environment
prod_origins = os.getenv("CORS_ORIGINS", "")
if prod_origins:
    allowed_origins.extend([origin.strip() for origin in prod_origins.split(",") if origin.strip()])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    # Allow any localhost/127.0.0.1 dev port to prevent CORS during local port changes.
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "Accept",
        "Origin",
        "X-Requested-With",
        "X-Request-ID",
        "X-Session-ID",
        "If-Match",
        "X-Before-State",
    ],
)
# ------------------------------------

# Canonical API routers
app.include_router(auth_router.router, prefix="/api/v1")
app.include_router(admin_users_router.router, prefix="/api/v1")
app.include_router(users_router.router, prefix="/api/v1")
app.include_router(hierarchy_public_router.router, prefix="/api/v1")
app.include_router(hierarchy_admin_router.router, prefix="/api/v1")
app.include_router(submissions_router.router, prefix="/api/v1")
app.include_router(moderation_router.router, prefix="/api/v1")
app.include_router(content_router.router, prefix="/api/v1")
app.include_router(search_router.router, prefix="/api/v1")
app.include_router(analytics_router.router, prefix="/api/v1")
app.include_router(analytics_router.admin_router, prefix="/api/v1")
app.include_router(analytics_router.public_router, prefix="/api/v1")
app.include_router(admin_settings_router.router, prefix="/api/v1")
app.include_router(admin_audit_router.router, prefix="/api/v1")
app.include_router(dictionary_router.router, prefix="/api/v1")
app.include_router(idiom_router.router, prefix="/api/v1")
app.include_router(article_router.router, prefix="/api/v1")
app.include_router(rec_router.router, prefix="/api/v1")
app.include_router(interactions_router.router, prefix="/api/v1")
app.include_router(poetry_router.router, prefix="/api/v1")
app.include_router(telemetry_router.router, prefix="/api/v1")
app.include_router(ai_ops_router.router, prefix="/api/v1")
app.include_router(ai_ops_router.governance_router, prefix="/api/v1")

# Backward-compatible API namespace aliases for clients expecting `/api/v1/*`.
# Legacy unprefixed routes can be enabled explicitly for older clients.
legacy_default = "false" if settings.APP_ENV.lower() == "production" else "true"
enable_legacy_routes = os.getenv("ENABLE_LEGACY_UNPREFIXED_ROUTES", legacy_default).strip().lower() in {
    "1",
    "true",
    "yes",
}
if enable_legacy_routes:
    app.include_router(auth_router.router, include_in_schema=False)
    app.include_router(admin_users_router.router, include_in_schema=False)
    app.include_router(users_router.router, include_in_schema=False)
    app.include_router(hierarchy_public_router.router, include_in_schema=False)
    app.include_router(hierarchy_admin_router.router, include_in_schema=False)
    app.include_router(submissions_router.router, include_in_schema=False)
    app.include_router(moderation_router.router, include_in_schema=False)
    app.include_router(content_router.router, include_in_schema=False)
    app.include_router(search_router.router, include_in_schema=False)
    app.include_router(analytics_router.router, include_in_schema=False)
    app.include_router(analytics_router.admin_router, include_in_schema=False)
    app.include_router(analytics_router.public_router, include_in_schema=False)
    app.include_router(admin_settings_router.router, include_in_schema=False)
    app.include_router(admin_audit_router.router, include_in_schema=False)
    app.include_router(dictionary_router.router, include_in_schema=False)
    app.include_router(idiom_router.router, include_in_schema=False)
    app.include_router(article_router.router, include_in_schema=False)
    app.include_router(rec_router.router, include_in_schema=False)
    app.include_router(interactions_router.router, include_in_schema=False)
    app.include_router(poetry_router.router, include_in_schema=False)
    app.include_router(telemetry_router.router, include_in_schema=False)
    app.include_router(ai_ops_router.router, include_in_schema=False)
    app.include_router(ai_ops_router.governance_router, include_in_schema=False)


@app.get("/health")
def health():
    return {"status": "ok"}
