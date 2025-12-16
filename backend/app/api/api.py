"""
API Router Aggregator
Combines all endpoint routers into a single API router
"""

from fastapi import APIRouter

from app.api.endpoints import market, portfolio, sentiment, auth, onchain, admin
from app.api.endpoints import admin_data, admin_users
from app.api.endpoints import triggers, realtime

api_router = APIRouter()

# Public endpoints
api_router.include_router(
    market.router,
    prefix="/market",
    tags=["Market Data"]
)

api_router.include_router(
    sentiment.router,
    prefix="/sentiment",
    tags=["AI Sentiment"]
)

api_router.include_router(
    onchain.router,
    prefix="/onchain",
    tags=["On-Chain Data"]
)

# Real-time streaming
api_router.include_router(
    realtime.router,
    tags=["Real-time"]
)

# Auth endpoints
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

# Protected endpoints
api_router.include_router(
    portfolio.router,
    prefix="/portfolio",
    tags=["Portfolio"]
)

# Admin/trigger endpoints
api_router.include_router(
    triggers.router,
    tags=["Triggers"]
)

# Admin Console API
api_router.include_router(
    admin.router,
    prefix="/admin",
    tags=["Admin Console"]
)

# Admin Data Management
api_router.include_router(
    admin_data.router,
    prefix="/admin/data",
    tags=["Admin Data"]
)

# Admin Users & Audit
api_router.include_router(
    admin_users.router,
    prefix="/admin",
    tags=["Admin Users"]
)


