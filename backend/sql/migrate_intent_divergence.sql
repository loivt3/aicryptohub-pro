-- ============================================
-- Intent Divergence Engine - Database Migration
-- Whale behavioral profiles and intent logs
-- ============================================

-- Whale Behavioral Profiles (Memory for whale addresses)
CREATE TABLE IF NOT EXISTS whale_behavioral_profiles (
    id SERIAL PRIMARY KEY,
    address VARCHAR(42) UNIQUE NOT NULL,
    chain_id INTEGER DEFAULT 1,
    -- Behavior classification
    behavior_label VARCHAR(30),  -- value_hunter, news_front_runner, panic_seller, accumulator, mixed
    behavior_confidence FLOAT DEFAULT 0,
    -- Performance tracking
    success_rate FLOAT DEFAULT 0,  -- % of profitable trades
    total_transactions INT DEFAULT 0,
    profitable_trades INT DEFAULT 0,
    avg_trade_size_usd FLOAT DEFAULT 0,
    -- Timing analysis
    avg_reaction_latency_minutes INT DEFAULT 0,  -- Time between sentiment spike and trade
    trades_before_news INT DEFAULT 0,  -- Trades made 1-2h before news
    trades_during_fear INT DEFAULT 0,  -- Trades when sentiment < 30
    trades_during_greed INT DEFAULT 0,  -- Trades when sentiment > 70
    -- Activity
    last_active TIMESTAMP,
    first_seen TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Index for quick lookups
CREATE INDEX IF NOT EXISTS idx_whale_profiles_address ON whale_behavioral_profiles(address);
CREATE INDEX IF NOT EXISTS idx_whale_profiles_label ON whale_behavioral_profiles(behavior_label);
CREATE INDEX IF NOT EXISTS idx_whale_profiles_active ON whale_behavioral_profiles(last_active DESC);

-- Intent Divergence Logs (Historical tracking)
CREATE TABLE IF NOT EXISTS intent_divergence_logs (
    id SERIAL PRIMARY KEY,
    coin_id VARCHAR(50) NOT NULL,
    symbol VARCHAR(20),
    timestamp TIMESTAMP DEFAULT NOW(),
    -- Sentiment data
    sentiment_score INT,  -- 0-100
    emotional_tone VARCHAR(20),
    crowd_action VARCHAR(30),
    -- Whale data
    whale_score INT,  -- Whale momentum score 0-100
    whale_net_flow_usd FLOAT,  -- Positive = inflow to exchange (bearish)
    active_whale_count INT DEFAULT 0,
    -- Divergence analysis
    divergence_type VARCHAR(30),  -- shadow_accumulation, bull_trap, confirmation, neutral
    intent_score INT,  -- 0-100 strength of divergence signal
    -- Whale profile summary
    dominant_whale_behavior VARCHAR(30),
    avg_whale_reaction_latency INT,
    -- AI insight
    shadow_insight TEXT,
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for intent logs
CREATE INDEX IF NOT EXISTS idx_intent_logs_coin ON intent_divergence_logs(coin_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_intent_logs_type ON intent_divergence_logs(divergence_type);
CREATE INDEX IF NOT EXISTS idx_intent_logs_score ON intent_divergence_logs(intent_score DESC);

-- Whale Transaction History (for behavior analysis)
CREATE TABLE IF NOT EXISTS whale_transaction_history (
    id SERIAL PRIMARY KEY,
    address VARCHAR(42) NOT NULL,
    coin_id VARCHAR(50),
    chain_id INTEGER DEFAULT 1,
    tx_hash VARCHAR(66),
    -- Transaction details
    tx_type VARCHAR(20),  -- buy, sell, transfer
    amount_usd FLOAT,
    token_amount FLOAT,
    -- Market context at transaction time
    price_at_tx FLOAT,
    price_change_24h_at_tx FLOAT,
    rsi_at_tx FLOAT,
    sentiment_at_tx INT,
    -- Outcome tracking
    price_after_24h FLOAT,
    price_after_7d FLOAT,
    is_profitable BOOLEAN,
    profit_pct FLOAT,
    -- Timing
    tx_timestamp TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for tx history
CREATE INDEX IF NOT EXISTS idx_whale_tx_address ON whale_transaction_history(address, tx_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_whale_tx_coin ON whale_transaction_history(coin_id, tx_timestamp DESC);

-- Golden Shadow Entry Signals (High-confidence divergence alerts)
CREATE TABLE IF NOT EXISTS golden_shadow_signals (
    id SERIAL PRIMARY KEY,
    coin_id VARCHAR(50) NOT NULL,
    symbol VARCHAR(20),
    signal_type VARCHAR(30),  -- entry, exit
    -- Signal data
    intent_score INT,
    divergence_type VARCHAR(30),
    sentiment_score INT,
    whale_score INT,
    -- Price context
    price_at_signal FLOAT,
    suggested_entry FLOAT,
    suggested_stop FLOAT,
    suggested_target FLOAT,
    -- AI insight
    shadow_insight TEXT,
    -- Outcome tracking
    outcome VARCHAR(20),  -- pending, success, failure
    actual_price_24h FLOAT,
    actual_price_7d FLOAT,
    -- Metadata
    signal_timestamp TIMESTAMP DEFAULT NOW(),
    expired_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_golden_signals_coin ON golden_shadow_signals(coin_id, signal_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_golden_signals_pending ON golden_shadow_signals(outcome) WHERE outcome = 'pending';

-- Log completion
DO $$
BEGIN
    RAISE NOTICE 'Intent Divergence Engine migration complete';
END $$;
