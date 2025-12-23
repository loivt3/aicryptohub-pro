-- Migration v13: Add missing columns to onchain_signals and create coin_contracts table
-- Date: 2025-12-23

-- =============================================================================
-- 1. Add missing columns to onchain_signals table
-- =============================================================================

-- Add whale inflow/outflow columns
ALTER TABLE onchain_signals 
ADD COLUMN IF NOT EXISTS whale_inflow_usd NUMERIC(24, 2) DEFAULT 0;

ALTER TABLE onchain_signals 
ADD COLUMN IF NOT EXISTS whale_outflow_usd NUMERIC(24, 2) DEFAULT 0;

-- Add dau_prev_day column
ALTER TABLE onchain_signals 
ADD COLUMN IF NOT EXISTS dau_prev_day INTEGER DEFAULT 0;

-- Add holder signal columns
ALTER TABLE onchain_signals 
ADD COLUMN IF NOT EXISTS holder_signal VARCHAR(20) DEFAULT 'NEUTRAL';

ALTER TABLE onchain_signals 
ADD COLUMN IF NOT EXISTS top10_change_pct NUMERIC(10, 2) DEFAULT 0;

ALTER TABLE onchain_signals 
ADD COLUMN IF NOT EXISTS accumulation_score NUMERIC(5, 2) DEFAULT 50;

-- Add last_dau_update timestamp
ALTER TABLE onchain_signals 
ADD COLUMN IF NOT EXISTS last_dau_update TIMESTAMP WITH TIME ZONE;


-- =============================================================================
-- 2. Create coin_contracts table
-- =============================================================================

CREATE TABLE IF NOT EXISTS coin_contracts (
    id SERIAL PRIMARY KEY,
    coin_id VARCHAR(100) NOT NULL,
    chain_id INTEGER NOT NULL,
    chain_slug VARCHAR(50) NOT NULL,
    contract_address VARCHAR(100) NOT NULL,
    decimals INTEGER DEFAULT 18,
    is_primary BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create unique index on coin_id + chain_id
CREATE UNIQUE INDEX IF NOT EXISTS idx_coin_contracts_coin_chain 
ON coin_contracts (coin_id, chain_id);

-- Create index on contract_address for lookups
CREATE INDEX IF NOT EXISTS idx_coin_contracts_address 
ON coin_contracts (contract_address);


-- =============================================================================
-- 3. Seed known contract addresses (hardcoded from database.py)
-- =============================================================================

INSERT INTO coin_contracts (coin_id, chain_id, chain_slug, contract_address, decimals, is_primary)
VALUES 
    -- Stablecoins
    ('tether', 1, 'ethereum', '0xdac17f958d2ee523a2206206994597c13d831ec7', 6, TRUE),
    ('usd-coin', 1, 'ethereum', '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48', 6, TRUE),
    ('dai', 1, 'ethereum', '0x6b175474e89094c44da98b954eedeac495271d0f', 18, TRUE),
    
    -- DeFi tokens
    ('staked-ether', 1, 'ethereum', '0xae7ab96520de3a18e5e111b5eaab095312d7fe84', 18, TRUE),
    ('wrapped-bitcoin', 1, 'ethereum', '0x2260fac5e5542a773aa44fbcfedf7c193bc2c599', 8, TRUE),
    ('chainlink', 1, 'ethereum', '0x514910771af9ca656af840dff83e8264ecf986ca', 18, TRUE),
    ('uniswap', 1, 'ethereum', '0x1f9840a85d5af5bf1d1762f925bdaddc4201f984', 18, TRUE),
    ('matic-network', 1, 'ethereum', '0x7d1afa7b718fb893db30a3abc0cfc608aacfebb0', 18, TRUE),
    
    -- Meme coins
    ('shiba-inu', 1, 'ethereum', '0x95ad61b0a150d79219dcf64e1e6cc01f0b64c4ce', 18, TRUE),
    ('pepe', 1, 'ethereum', '0x6982508145454ce325ddbe47a25d4ec3d2311933', 18, TRUE),
    
    -- Layer 2 tokens (on Ethereum as ERC-20)
    ('arbitrum', 1, 'ethereum', '0xb50721bcf8d664c30412cfbc6cf7a15145234ad1', 18, TRUE),
    ('optimism', 1, 'ethereum', '0x4200000000000000000000000000000000000042', 18, TRUE),
    
    -- Other popular tokens
    ('aave', 1, 'ethereum', '0x7fc66500c84a76ad7e9c93437bfc5ac33e2ddae9', 18, TRUE),
    ('maker', 1, 'ethereum', '0x9f8f72aa9304c8b593d555f12ef6589cc3a579a2', 18, TRUE),
    ('compound-governance-token', 1, 'ethereum', '0xc00e94cb662c3520282e6f5717214004a7f26888', 18, TRUE),
    ('curve-dao-token', 1, 'ethereum', '0xd533a949740bb3306d119cc777fa900ba034cd52', 18, TRUE),
    ('1inch', 1, 'ethereum', '0x111111111117dc0aa78b770fa6a738034120c302', 18, TRUE),
    
    -- BSC tokens
    ('pancakeswap-token', 56, 'bsc', '0x0e09fabb73bd3ade0a17ecc321fd13a19e81ce82', 18, TRUE),
    ('venus', 56, 'bsc', '0xcf6bb5389c92bdda8a3747ddb454cb7a64626c63', 18, TRUE)
    
ON CONFLICT (coin_id, chain_id) DO NOTHING;


-- =============================================================================
-- 4. Create whale_transactions table if not exists (from migration_v7)
-- =============================================================================

CREATE TABLE IF NOT EXISTS whale_transactions (
    id SERIAL PRIMARY KEY,
    coin_id VARCHAR(100) NOT NULL,
    chain_slug VARCHAR(50) DEFAULT 'ethereum',
    tx_hash VARCHAR(100) UNIQUE NOT NULL,
    from_address VARCHAR(100) NOT NULL,
    to_address VARCHAR(100) NOT NULL,
    value_usd NUMERIC(24, 2) NOT NULL,
    value_native NUMERIC(36, 18),
    tx_type VARCHAR(50),  -- exchange_deposit, exchange_withdraw, transfer
    is_exchange_related BOOLEAN DEFAULT FALSE,
    exchange_name VARCHAR(50),
    block_number BIGINT,
    tx_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_whale_tx_coin 
ON whale_transactions (coin_id, tx_timestamp);


-- =============================================================================
-- 5. Create daily_active_addresses table if not exists
-- =============================================================================

CREATE TABLE IF NOT EXISTS daily_active_addresses (
    id SERIAL PRIMARY KEY,
    coin_id VARCHAR(100) NOT NULL,
    chain_slug VARCHAR(50) DEFAULT 'ethereum',
    date DATE NOT NULL,
    active_addresses INTEGER DEFAULT 0,
    tx_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_dau_coin_chain_date 
ON daily_active_addresses (coin_id, chain_slug, date);


-- =============================================================================
-- 6. Create top_holder_snapshots table if not exists
-- =============================================================================

CREATE TABLE IF NOT EXISTS top_holder_snapshots (
    id SERIAL PRIMARY KEY,
    coin_id VARCHAR(100) NOT NULL,
    chain_slug VARCHAR(50) DEFAULT 'ethereum',
    snapshot_date DATE NOT NULL,
    top10_total_balance NUMERIC(36, 18),
    top10_pct_of_supply NUMERIC(10, 4),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_holder_snapshot_coin_date 
ON top_holder_snapshots (coin_id, snapshot_date);


-- Done!
SELECT 'Migration v13 completed successfully' as status;
