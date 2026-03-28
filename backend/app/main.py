# app/main.py
from fastapi import FastAPI
import os

#middleware
from fastapi.middleware.cors import CORSMiddleware

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


from app.core.settings import settings


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


app = FastAPI(title="Awadhi Corpus Backend", debug=settings.APP_DEBUG)


@app.on_event("startup")
def validate_required_environment() -> None:
    _validate_required_env()

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
    allow_methods=["*"],
    allow_headers=["*"],
)
# ------------------------------------

# API routers
app.include_router(auth_router.router)
app.include_router(admin_users_router.router)
app.include_router(users_router.router)
app.include_router(hierarchy_public_router.router)
app.include_router(hierarchy_admin_router.router)
app.include_router(submissions_router.router)
app.include_router(moderation_router.router) 
app.include_router(content_router.router) 
app.include_router(search_router.router)
app.include_router(analytics_router.router)
app.include_router(analytics_router.admin_router)
app.include_router(analytics_router.public_router)
app.include_router(admin_settings_router.router)
app.include_router(admin_audit_router.router)
# NEW: Register dictionary, idiom, article routes
app.include_router(dictionary_router.router)
app.include_router(idiom_router.router)
app.include_router(article_router.router)
app.include_router(rec_router.router)
app.include_router(interactions_router.router)
app.include_router(poetry_router.router)
app.include_router(telemetry_router.router)


@app.get("/health")
def health():
    return {"status": "ok"}
