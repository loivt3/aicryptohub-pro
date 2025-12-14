"""
Schemas Package
"""

from app.schemas.schemas import (
    # Auth
    UserBase,
    UserCreate,
    UserResponse,
    TokenResponse,
    LoginRequest,
    # Market
    CoinBase,
    CoinData,
    MarketDataResponse,
    OHLCVData,
    # Sentiment
    SentimentData,
    AnalysisRequest,
    # Portfolio
    HoldingBase,
    AddHoldingRequest,
    UpdateHoldingRequest,
    PortfolioHolding,
    PortfolioSummary,
    # OnChain
    WhaleActivity,
    NetworkHealth,
    OnChainSignals,
    # Common
    SuccessResponse,
    ErrorResponse,
)

__all__ = [
    "UserBase",
    "UserCreate",
    "UserResponse",
    "TokenResponse",
    "LoginRequest",
    "CoinBase",
    "CoinData",
    "MarketDataResponse",
    "OHLCVData",
    "SentimentData",
    "AnalysisRequest",
    "HoldingBase",
    "AddHoldingRequest",
    "UpdateHoldingRequest",
    "PortfolioHolding",
    "PortfolioSummary",
    "WhaleActivity",
    "NetworkHealth",
    "OnChainSignals",
    "SuccessResponse",
    "ErrorResponse",
]
