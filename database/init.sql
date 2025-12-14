-- AI Crypto Hub Pro - Database Schema
-- PostgreSQL / Supabase

-- =============================================
-- USERS & AUTH
-- =============================================

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100),
    is_admin BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);

-- =============================================
-- MARKET DATA
-- =============================================

CREATE TABLE IF NOT EXISTS aihub_coins (
    id SERIAL PRIMARY KEY,
    coin_id VARCHAR(100) UNIQUE NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    name VARCHAR(100) NOT NULL,
    image TEXT,
    current_price DECIMAL(24, 12) DEFAULT 0,
    market_cap DECIMAL(24, 2) DEFAULT 0,
    market_cap_rank INTEGER,
    volume_24h_usdt DECIMAL(24, 2) DEFAULT 0,
    price_change_percentage_1h DECIMAL(10, 4) DEFAULT 0,
    price_change_percentage_24h DECIMAL(10, 4) DEFAULT 0,
    price_change_percentage_7d DECIMAL(10, 4) DEFAULT 0,
    high_24h DECIMAL(24, 12) DEFAULT 0,
    low_24h DECIMAL(24, 12) DEFAULT 0,
    circulating_supply DECIMAL(24, 2),
    total_supply DECIMAL(24, 2),
    max_supply DECIMAL(24, 2),
    ath DECIMAL(24, 12),
    ath_date TIMESTAMP WITH TIME ZONE,
    atl DECIMAL(24, 12),
    atl_date TIMESTAMP WITH TIME ZONE,
    contract_address VARCHAR(100),
    chain_slug VARCHAR(50),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_coins_symbol ON aihub_coins(symbol);
CREATE INDEX idx_coins_rank ON aihub_coins(market_cap_rank);

-- =============================================
-- OHLCV DATA
-- =============================================

CREATE TABLE IF NOT EXISTS aihub_ohlcv (
    id SERIAL PRIMARY KEY,
    coin_id VARCHAR(100) NOT NULL,
    timestamp BIGINT NOT NULL,
    open DECIMAL(24, 12) NOT NULL,
    high DECIMAL(24, 12) NOT NULL,
    low DECIMAL(24, 12) NOT NULL,
    close DECIMAL(24, 12) NOT NULL,
    volume DECIMAL(24, 2) NOT NULL,
    interval VARCHAR(10) DEFAULT '1h',
    UNIQUE(coin_id, timestamp, interval)
);

CREATE INDEX idx_ohlcv_coin_time ON aihub_ohlcv(coin_id, timestamp DESC);

-- =============================================
-- AI SENTIMENT
-- =============================================

CREATE TABLE IF NOT EXISTS aihub_sentiment (
    id SERIAL PRIMARY KEY,
    coin_id VARCHAR(100) NOT NULL,
    asi_score DECIMAL(5, 2) DEFAULT 50,
    signal VARCHAR(10) DEFAULT 'HOLD',
    confidence DECIMAL(5, 2),
    reason TEXT,
    technical_score DECIMAL(5, 2),
    news_score DECIMAL(5, 2),
    provider VARCHAR(50) DEFAULT 'technical',
    analyzed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(coin_id)
);

CREATE INDEX idx_sentiment_coin ON aihub_sentiment(coin_id);

-- =============================================
-- PORTFOLIO
-- =============================================

CREATE TABLE IF NOT EXISTS portfolio_holdings (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    coin_id VARCHAR(100) NOT NULL,
    amount DECIMAL(24, 12) NOT NULL,
    buy_price DECIMAL(24, 12) NOT NULL,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, coin_id)
);

CREATE INDEX idx_portfolio_user ON portfolio_holdings(user_id);

-- =============================================
-- ON-CHAIN SIGNALS
-- =============================================

CREATE TABLE IF NOT EXISTS onchain_signals (
    id SERIAL PRIMARY KEY,
    coin_id VARCHAR(100) UNIQUE NOT NULL,
    overall_signal VARCHAR(20) DEFAULT 'NEUTRAL',
    bullish_probability DECIMAL(5, 2) DEFAULT 50,
    confidence_score DECIMAL(5, 2) DEFAULT 50,
    -- Whale activity
    whale_signal VARCHAR(20) DEFAULT 'NEUTRAL',
    whale_tx_count_24h INTEGER DEFAULT 0,
    whale_tx_change_pct DECIMAL(10, 2) DEFAULT 0,
    whale_net_flow_usd DECIMAL(24, 2) DEFAULT 0,
    -- Network health
    network_signal VARCHAR(20) DEFAULT 'NEUTRAL',
    dau_current INTEGER DEFAULT 0,
    dau_change_1d_pct DECIMAL(10, 2) DEFAULT 0,
    dau_trend VARCHAR(20) DEFAULT 'STABLE',
    -- Holder distribution
    holder_signal VARCHAR(20) DEFAULT 'NEUTRAL',
    top10_change_pct DECIMAL(10, 2) DEFAULT 0,
    accumulation_score DECIMAL(5, 2) DEFAULT 50,
    -- AI analysis
    ai_prediction TEXT,
    ai_summary TEXT,
    -- Timestamps
    last_whale_update TIMESTAMP WITH TIME ZONE,
    last_ai_analysis TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_onchain_coin ON onchain_signals(coin_id);

-- =============================================
-- SETTINGS (App Configuration)
-- =============================================

CREATE TABLE IF NOT EXISTS app_settings (
    key VARCHAR(100) PRIMARY KEY,
    value JSONB,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert default settings
INSERT INTO app_settings (key, value) VALUES
    ('refresh_interval', '15'),
    ('ai_provider', '"gemini"'),
    ('data_sources', '{"coingecko": true, "binance": true, "okx": true}'),
    ('cache_ttl', '60')
ON CONFLICT (key) DO NOTHING;
