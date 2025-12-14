"""
Pydantic Schemas for Request/Response validation
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr


# =============================================
# Auth Schemas
# =============================================

class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: str
    is_admin: bool = False
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# =============================================
# Market Schemas
# =============================================

class CoinBase(BaseModel):
    coin_id: str
    symbol: str
    name: str
    image: Optional[str] = None


class CoinData(CoinBase):
    price: float
    change_1h: Optional[float] = None
    change_24h: float
    change_7d: Optional[float] = None
    market_cap: float
    market_cap_rank: Optional[int] = None
    volume_24h: float
    high_24h: Optional[float] = None
    low_24h: Optional[float] = None

    class Config:
        from_attributes = True


class MarketDataResponse(BaseModel):
    success: bool
    data: List[dict]
    meta: dict


class OHLCVData(BaseModel):
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float


# =============================================
# Sentiment Schemas
# =============================================

class SentimentData(BaseModel):
    coin_id: str
    symbol: Optional[str] = None
    name: Optional[str] = None
    asi_score: float
    signal: str
    reason: Optional[str] = None
    confidence: Optional[float] = None
    provider: Optional[str] = None
    analyzed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AnalysisRequest(BaseModel):
    coin_ids: List[str] = []
    force_refresh: bool = False


# =============================================
# Portfolio Schemas
# =============================================

class HoldingBase(BaseModel):
    coin_id: str
    amount: float
    buy_price: float


class AddHoldingRequest(HoldingBase):
    pass


class UpdateHoldingRequest(BaseModel):
    amount: Optional[float] = None
    buy_price: Optional[float] = None


class PortfolioHolding(HoldingBase):
    symbol: Optional[str] = None
    name: Optional[str] = None
    image: Optional[str] = None
    current_price: Optional[float] = None
    value: Optional[float] = None
    pnl: Optional[float] = None
    pnl_percent: Optional[float] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PortfolioSummary(BaseModel):
    total_value: float
    total_invested: float
    total_pnl: float
    total_pnl_percent: float
    holdings_count: int


# =============================================
# On-Chain Schemas
# =============================================

class WhaleActivity(BaseModel):
    signal: str = "NEUTRAL"
    tx_count_24h: int = 0
    change_24h_pct: float = 0
    net_flow_usd: float = 0


class NetworkHealth(BaseModel):
    signal: str = "NEUTRAL"
    dau_current: int = 0
    dau_change_1d_pct: float = 0
    trend: str = "STABLE"


class OnChainSignals(BaseModel):
    coin_id: str
    overall_signal: str = "NEUTRAL"
    bullish_probability: float = 50
    whale_activity: WhaleActivity
    network_health: NetworkHealth
    ai_prediction: Optional[str] = None
    ai_summary: Optional[str] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# =============================================
# Common Schemas
# =============================================

class SuccessResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    detail: Optional[str] = None
