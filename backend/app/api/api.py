"""
API Router Aggregator
Combines all endpoint routers into a single API router
"""

from fastapi import APIRouter

from app.api.endpoints import market, portfolio, sentiment, auth, onchain

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
