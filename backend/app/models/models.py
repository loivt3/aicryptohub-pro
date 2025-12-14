"""
SQLAlchemy Models for PostgreSQL
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Text, 
    DateTime, ForeignKey, Numeric, JSON, Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()


class User(Base):
    """User model for authentication"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100))
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    holdings = relationship("PortfolioHolding", back_populates="user", cascade="all, delete-orphan")


class Coin(Base):
    """Cryptocurrency coin data"""
    __tablename__ = "aihub_coins"
    
    id = Column(Integer, primary_key=True)
    coin_id = Column(String(100), unique=True, nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    image = Column(Text)
    current_price = Column(Numeric(24, 12), default=0)
    market_cap = Column(Numeric(24, 2), default=0)
    market_cap_rank = Column(Integer, index=True)
    volume_24h_usdt = Column(Numeric(24, 2), default=0)
    price_change_percentage_1h = Column(Numeric(10, 4), default=0)
    price_change_percentage_24h = Column(Numeric(10, 4), default=0)
    price_change_percentage_7d = Column(Numeric(10, 4), default=0)
    high_24h = Column(Numeric(24, 12), default=0)
    low_24h = Column(Numeric(24, 12), default=0)
    circulating_supply = Column(Numeric(24, 2))
    total_supply = Column(Numeric(24, 2))
    max_supply = Column(Numeric(24, 2))
    ath = Column(Numeric(24, 12))
    ath_date = Column(DateTime(timezone=True))
    atl = Column(Numeric(24, 12))
    atl_date = Column(DateTime(timezone=True))
    contract_address = Column(String(100))
    chain_slug = Column(String(50))
    updated_at = Column(DateTime(timezone=True), server_default=func.now())


class OHLCV(Base):
    """OHLCV candlestick data"""
    __tablename__ = "aihub_ohlcv"
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False, index=True)
    open_time = Column(DateTime(timezone=True), nullable=False)
    open = Column(Numeric(24, 12), nullable=False)
    high = Column(Numeric(24, 12), nullable=False)
    low = Column(Numeric(24, 12), nullable=False)
    close = Column(Numeric(24, 12), nullable=False)
    volume = Column(Numeric(24, 2), nullable=False)
    timeframe = Column(Integer, default=60)  # minutes
    
    __table_args__ = (
        Index('idx_ohlcv_symbol_time', 'symbol', 'open_time', unique=True),
    )


class Sentiment(Base):
    """AI Sentiment analysis results"""
    __tablename__ = "aihub_sentiment"
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), unique=True, nullable=False, index=True)
    ai_signal = Column(String(20), default="NEUTRAL")
    sentiment_score = Column(Numeric(5, 4), default=0.5)  # 0-1
    sentiment_reason = Column(Text)
    provider = Column(String(50), default="technical")
    analyzed_at = Column(DateTime(timezone=True), server_default=func.now())


class PortfolioHolding(Base):
    """User portfolio holdings"""
    __tablename__ = "portfolio_holdings"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    coin_id = Column(String(100), nullable=False)
    amount = Column(Numeric(24, 12), nullable=False)
    buy_price = Column(Numeric(24, 12), nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="holdings")
    
    __table_args__ = (
        Index('idx_portfolio_user_coin', 'user_id', 'coin_id', unique=True),
    )


class OnChainSignal(Base):
    """On-chain analysis signals"""
    __tablename__ = "onchain_signals"
    
    id = Column(Integer, primary_key=True)
    coin_id = Column(String(100), unique=True, nullable=False, index=True)
    overall_signal = Column(String(20), default="NEUTRAL")
    bullish_probability = Column(Numeric(5, 2), default=50)
    confidence_score = Column(Numeric(5, 2), default=50)
    
    # Whale activity
    whale_signal = Column(String(20), default="NEUTRAL")
    whale_tx_count_24h = Column(Integer, default=0)
    whale_tx_change_pct = Column(Numeric(10, 2), default=0)
    whale_net_flow_usd = Column(Numeric(24, 2), default=0)
    
    # Network health
    network_signal = Column(String(20), default="NEUTRAL")
    dau_current = Column(Integer, default=0)
    dau_change_1d_pct = Column(Numeric(10, 2), default=0)
    dau_trend = Column(String(20), default="STABLE")
    
    # AI analysis
    ai_prediction = Column(Text)
    ai_summary = Column(Text)
    
    # Timestamps
    last_whale_update = Column(DateTime(timezone=True))
    last_ai_analysis = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True), server_default=func.now())


class AppSetting(Base):
    """Application settings"""
    __tablename__ = "app_settings"
    
    key = Column(String(100), primary_key=True)
    value = Column(JSON)
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
