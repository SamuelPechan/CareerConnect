from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.auth import router as auth_router
from app.api.routes.companies import router as companies_router
from app.api.routes.contacts import router as contacts_router
from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.discovery import router as discovery_router
from app.api.routes.health import router as health_router
from app.api.routes.message_drafts import router as message_drafts_router
from app.api.routes.networking import router as networking_router
from app.api.routes.opportunities import router as opportunities_router
from app.api.routes.profile import router as profile_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(title=settings.app_name, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_frontend_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix=settings.api_prefix)
app.include_router(auth_router, prefix=settings.api_prefix)
app.include_router(dashboard_router, prefix=settings.api_prefix)
app.include_router(profile_router, prefix=settings.api_prefix)
app.include_router(opportunities_router, prefix=settings.api_prefix)
app.include_router(companies_router, prefix=settings.api_prefix)
app.include_router(discovery_router, prefix=settings.api_prefix)
app.include_router(contacts_router, prefix=settings.api_prefix)
app.include_router(networking_router, prefix=settings.api_prefix)
app.include_router(message_drafts_router, prefix=settings.api_prefix)
