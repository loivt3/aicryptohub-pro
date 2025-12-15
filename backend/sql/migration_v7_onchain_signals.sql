-- ==============================================
-- On-Chain Signals Schema - Migration V7
-- AI Crypto Hub Pro
-- Adds whale tracking, DAU, and AI signals
-- ==============================================

-- 1. Whale Transactions (>$100K transactions)
CREATE TABLE IF NOT EXISTS whale_transactions (
    id SERIAL PRIMARY KEY,
    coin_id VARCHAR(100) NOT NULL,
    chain_slug VARCHAR(50) NOT NULL,
    tx_hash VARCHAR(100) UNIQUE NOT NULL,
    
    -- Transaction details
    from_address VARCHAR(100),
    to_address VARCHAR(100),
    value_usd NUMERIC(20, 2),                    -- USD value at time of tx
    value_native NUMERIC(38, 18),                -- Native token amount
    
    -- Classification
    tx_type VARCHAR(30) DEFAULT 'transfer',      -- transfer, exchange_deposit, exchange_withdraw, contract_call
    is_exchange_related BOOLEAN DEFAULT FALSE,
    exchange_name VARCHAR(50),                    -- Binance, Coinbase, etc (if known)
    
    -- Timing
    block_number BIGINT,
    tx_timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for whale_transactions
CREATE INDEX IF NOT EXISTS idx_whale_tx_coin ON whale_transactions(coin_id);
CREATE INDEX IF NOT EXISTS idx_whale_tx_timestamp ON whale_transactions(tx_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_whale_tx_type ON whale_transactions(tx_type);
CREATE INDEX IF NOT EXISTS idx_whale_tx_chain ON whale_transactions(chain_slug);

-- 2. Daily Active Addresses (for trend calculation)
CREATE TABLE IF NOT EXISTS daily_active_addresses (
    id SERIAL PRIMARY KEY,
    coin_id VARCHAR(100) NOT NULL,
    chain_slug VARCHAR(50) NOT NULL,
    date DATE NOT NULL,
    
    -- Metrics
    active_addresses INTEGER NOT NULL DEFAULT 0, -- Unique addresses with activity
    new_addresses INTEGER DEFAULT 0,              -- First-time addresses
    tx_count INTEGER DEFAULT 0,                   -- Total transactions
    transfer_volume_usd NUMERIC(20, 2),           -- Total transfer volume
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Unique constraint per coin per day
    UNIQUE (coin_id, chain_slug, date)
);

-- Indexes for daily_active_addresses
CREATE INDEX IF NOT EXISTS idx_dau_coin ON daily_active_addresses(coin_id);
CREATE INDEX IF NOT EXISTS idx_dau_date ON daily_active_addresses(date DESC);

-- 3. On-Chain Signals (computed analysis results)
CREATE TABLE IF NOT EXISTS onchain_signals (
    id SERIAL PRIMARY KEY,
    coin_id VARCHAR(100) UNIQUE NOT NULL,
    
    -- ===============================
    -- Whale Activity Signals
    -- ===============================
    whale_tx_count_24h INTEGER DEFAULT 0,         -- Large tx in last 24h
    whale_tx_count_prev_24h INTEGER DEFAULT 0,    -- Previous 24h (for comparison)
    whale_tx_change_pct NUMERIC(10, 2),           -- % change vs previous period
    whale_inflow_usd NUMERIC(20, 2) DEFAULT 0,    -- To exchanges
    whale_outflow_usd NUMERIC(20, 2) DEFAULT 0,   -- From exchanges
    whale_net_flow_usd NUMERIC(20, 2) DEFAULT 0,  -- Net (negative = bullish)
    whale_signal VARCHAR(20) DEFAULT 'NEUTRAL',   -- BULLISH, BEARISH, NEUTRAL
    
    -- ===============================
    -- Network Health / DAU Signals
    -- ===============================
    dau_current INTEGER,                          -- Current day active addresses
    dau_prev_day INTEGER,                         -- Previous day
    dau_avg_7d INTEGER,                           -- 7-day average
    dau_change_1d_pct NUMERIC(10, 2),             -- 1-day change %
    dau_change_3d_pct NUMERIC(10, 2),             -- 3-day change %
    dau_change_7d_pct NUMERIC(10, 2),             -- 7-day change %
    dau_trend VARCHAR(20) DEFAULT 'STABLE',       -- GROWING, DECLINING, STABLE
    network_signal VARCHAR(20) DEFAULT 'NEUTRAL',
    
    -- ===============================
    -- Top Holders Signals
    -- ===============================
    top10_balance_current NUMERIC(38, 8),         -- Current top 10 total balance
    top10_balance_prev_7d NUMERIC(38, 8),         -- 7 days ago
    top10_change_pct NUMERIC(10, 2),              -- % change
    top100_change_pct NUMERIC(10, 2),             -- Top 100 % change
    accumulation_score NUMERIC(5, 2),             -- 0-100 (higher = more accumulation)
    holder_signal VARCHAR(20) DEFAULT 'NEUTRAL',
    
    -- ===============================
    -- Overall Signal & AI Analysis
    -- ===============================
    overall_signal VARCHAR(20) DEFAULT 'NEUTRAL', -- BULLISH, BEARISH, NEUTRAL
    bullish_probability NUMERIC(5, 2),            -- 0-100%
    confidence_score NUMERIC(5, 2),               -- 0-100%
    
    -- AI Analysis
    ai_prediction TEXT,                           -- Gemini reasoning text
    ai_summary VARCHAR(500),                      -- Short summary
    
    -- ===============================
    -- Metadata
    -- ===============================
    data_sources JSONB,                           -- {"whale": "etherscan", "dau": "glassnode"}
    last_whale_update TIMESTAMP,
    last_dau_update TIMESTAMP,
    last_holder_update TIMESTAMP,
    last_ai_analysis TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for onchain_signals
CREATE INDEX IF NOT EXISTS idx_signals_coin ON onchain_signals(coin_id);
CREATE INDEX IF NOT EXISTS idx_signals_overall ON onchain_signals(overall_signal);
CREATE INDEX IF NOT EXISTS idx_signals_updated ON onchain_signals(updated_at DESC);

-- 4. Top Holder History (for tracking accumulation over time)
CREATE TABLE IF NOT EXISTS top_holder_snapshots (
    id SERIAL PRIMARY KEY,
    coin_id VARCHAR(100) NOT NULL,
    chain_slug VARCHAR(50) NOT NULL,
    snapshot_date DATE NOT NULL,
    
    -- Aggregated data
    top10_total_balance NUMERIC(38, 8),
    top10_pct_of_supply NUMERIC(10, 6),
    top100_total_balance NUMERIC(38, 8),
    top100_pct_of_supply NUMERIC(10, 6),
    
    -- Individual top 10 holders (JSONB for flexibility)
    top10_holders JSONB,  -- [{"address": "0x...", "balance": 1000, "pct": 5.2, "label": "Binance"}, ...]
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE (coin_id, chain_slug, snapshot_date)
);

-- Index for snapshots
CREATE INDEX IF NOT EXISTS idx_holder_snapshot_coin ON top_holder_snapshots(coin_id);
CREATE INDEX IF NOT EXISTS idx_holder_snapshot_date ON top_holder_snapshots(snapshot_date DESC);

-- 5. Update trigger for onchain_signals.updated_at
CREATE OR REPLACE FUNCTION update_onchain_signals_modtime()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_onchain_signals_modtime ON onchain_signals;
CREATE TRIGGER update_onchain_signals_modtime
    BEFORE UPDATE ON onchain_signals
    FOR EACH ROW EXECUTE FUNCTION update_onchain_signals_modtime();

-- 6. Known Exchange Addresses (for whale tx classification)
CREATE TABLE IF NOT EXISTS known_addresses (
    id SERIAL PRIMARY KEY,
    address VARCHAR(100) NOT NULL,
    chain_slug VARCHAR(50) NOT NULL,
    
    -- Labels
    label VARCHAR(100) NOT NULL,                  -- "Binance Hot Wallet", "Coinbase Deposit"
    address_type VARCHAR(30),                     -- exchange, whale, contract, team, foundation
    exchange_name VARCHAR(50),                    -- Binance, Coinbase, Kraken, etc.
    is_deposit BOOLEAN DEFAULT FALSE,             -- Is this a deposit address?
    is_hot_wallet BOOLEAN DEFAULT FALSE,
    
    -- Verification
    verified BOOLEAN DEFAULT FALSE,
    source VARCHAR(50),                           -- "etherscan", "manual", "arkham"
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE (address, chain_slug)
);

-- Indexes for known_addresses
CREATE INDEX IF NOT EXISTS idx_known_addr ON known_addresses(address);
CREATE INDEX IF NOT EXISTS idx_known_chain ON known_addresses(chain_slug);
CREATE INDEX IF NOT EXISTS idx_known_exchange ON known_addresses(exchange_name);

-- 7. Pre-populate some known exchange addresses
INSERT INTO known_addresses (address, chain_slug, label, address_type, exchange_name, is_hot_wallet, verified, source) VALUES
-- Ethereum
('0x28c6c06298d514db089934071355e5743bf21d60', 'ethereum', 'Binance Hot Wallet 14', 'exchange', 'Binance', TRUE, TRUE, 'etherscan'),
('0x21a31ee1afc51d94c2efccaa2092ad1028285549', 'ethereum', 'Binance Hot Wallet 15', 'exchange', 'Binance', TRUE, TRUE, 'etherscan'),
('0xdfd5293d8e347dfe59e90efd55b2956a1343963d', 'ethereum', 'Binance Hot Wallet 16', 'exchange', 'Binance', TRUE, TRUE, 'etherscan'),
('0x503828976d22510aad0339f96bf6eb6083ed4457', 'ethereum', 'Coinbase Commerce', 'exchange', 'Coinbase', TRUE, TRUE, 'etherscan'),
('0xa9d1e08c7793af67e9d92fe308d5697fb81d3e43', 'ethereum', 'Coinbase 10', 'exchange', 'Coinbase', TRUE, TRUE, 'etherscan'),
('0x71660c4005ba85c37ccec55d0c4493e66fe775d3', 'ethereum', 'Coinbase 3', 'exchange', 'Coinbase', TRUE, TRUE, 'etherscan'),
('0x2b5634c42055806a59e9107ed44d43c426e58258', 'ethereum', 'Kraken Hot Wallet', 'exchange', 'Kraken', TRUE, TRUE, 'etherscan'),
('0x53d284357ec70ce289d6d64134dfac8e511c8a3d', 'ethereum', 'Kraken Cold Wallet', 'exchange', 'Kraken', FALSE, TRUE, 'etherscan'),
('0x1151314c646ce4e0efd76d1af4760ae66a9fe30f', 'ethereum', 'Bitfinex Hot Wallet', 'exchange', 'Bitfinex', TRUE, TRUE, 'etherscan'),
('0x742d35cc6634c0532925a3b844bc454e4438f44e', 'ethereum', 'Bitfinex Cold Wallet', 'exchange', 'Bitfinex', FALSE, TRUE, 'etherscan'),
('0xdc76cd25977e0a5ae17155770273ad58648900d3', 'ethereum', 'OKX Hot Wallet', 'exchange', 'OKX', TRUE, TRUE, 'etherscan'),
('0x98c3d3183c4b8a650614ad179a1a98be0a8d6b8e', 'ethereum', 'Bybit Hot Wallet', 'exchange', 'Bybit', TRUE, TRUE, 'etherscan')
ON CONFLICT (address, chain_slug) DO NOTHING;

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Migration V7 completed: On-Chain Signals tables created';
END $$;
