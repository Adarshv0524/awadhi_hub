# app/main.py
from fastapi import FastAPI

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


from app.core.settings import settings

app = FastAPI(title="Awadhi Corpus Backend", debug=settings.APP_DEBUG)

# CORS configuration
# In production, set CORS_ORIGINS env variable with your frontend domain
allowed_origins = [
    "http://localhost:4321",  # Astro dev server
    "http://127.0.0.1:4321",  # IPv4 localhost
    "http://localhost:4322",  # Alternate Astro/Vite dev port
    "http://127.0.0.1:4322",  # Alternate IPv4 localhost port
]

# Add production origins from environment
import os
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
app.include_router(admin_settings_router.router)
app.include_router(admin_audit_router.router)
# NEW: Register dictionary, idiom, article routes
app.include_router(dictionary_router.router)
app.include_router(idiom_router.router)
app.include_router(article_router.router)
app.include_router(rec_router.router)
app.include_router(interactions_router.router)


@app.get("/health")
def health():
    return {"status": "ok"}
