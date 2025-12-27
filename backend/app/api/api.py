"""
API Router Aggregator
Combines all endpoint routers into a single API router
"""

from fastapi import APIRouter

from app.api.endpoints import market, portfolio, sentiment, auth, onchain, admin, news, alerts
from app.api.endpoints import admin_data, admin_users, admin_fetcher, admin_ai_workers
from app.api.endpoints import triggers, realtime, intent_divergence, discovery, risk

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

api_router.include_router(
    news.router,
    prefix="/news",
    tags=["News"]
)

api_router.include_router(
    alerts.router,
    prefix="/alerts",
    tags=["AI Alerts & Highlights"]
)

# AI Risk Assessment
api_router.include_router(
    risk.router,
    prefix="/risk",
    tags=["AI Risk"]
)

# Intent Divergence (Shadow Analysis)
api_router.include_router(
    intent_divergence.router,
    tags=["Intent Divergence"]
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

# Admin Fetcher Process Manager
api_router.include_router(
    admin_fetcher.router,
    prefix="/admin",
    tags=["Admin Fetcher"]
)

# Admin AI Workers Process Manager
api_router.include_router(
    admin_ai_workers.router,
    prefix="/admin",
    tags=["Admin AI Workers"]
)

# Market Discovery Engine
try:
    from app.api.endpoints import discovery
    api_router.include_router(
        discovery.router,
        prefix="/discovery",
        tags=["Market Discovery"]
    )
except ImportError:
    pass  # Discovery module not yet available
