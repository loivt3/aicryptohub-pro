-- ==============================================
-- On-Chain Data Schema for PostgreSQL
-- AI Crypto Hub Pro
-- ==============================================

-- 1. Supported blockchain networks
CREATE TABLE IF NOT EXISTS chains (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(50) UNIQUE NOT NULL,           -- 'ethereum', 'bsc', 'polygon'
    name VARCHAR(100) NOT NULL,                  -- 'Ethereum', 'BNB Smart Chain'
    chain_id INTEGER,                            -- 1 for ETH, 56 for BSC
    explorer_api_url VARCHAR(255),               -- 'https://api.etherscan.io/api'
    explorer_name VARCHAR(50),                   -- 'Etherscan', 'BscScan'
    native_symbol VARCHAR(10),                   -- 'ETH', 'BNB'
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Pre-populate with 10 most popular chains
INSERT INTO chains (slug, name, chain_id, explorer_api_url, explorer_name, native_symbol) VALUES
('ethereum', 'Ethereum', 1, 'https://api.etherscan.io/api', 'Etherscan', 'ETH'),
('bsc', 'BNB Smart Chain', 56, 'https://api.bscscan.com/api', 'BscScan', 'BNB'),
('polygon', 'Polygon', 137, 'https://api.polygonscan.com/api', 'PolygonScan', 'MATIC'),
('arbitrum', 'Arbitrum One', 42161, 'https://api.arbiscan.io/api', 'Arbiscan', 'ETH'),
('optimism', 'Optimism', 10, 'https://api-optimistic.etherscan.io/api', 'Optimism Etherscan', 'ETH'),
('avalanche', 'Avalanche C-Chain', 43114, 'https://api.snowtrace.io/api', 'Snowtrace', 'AVAX'),
('base', 'Base', 8453, 'https://api.basescan.org/api', 'BaseScan', 'ETH'),
('fantom', 'Fantom Opera', 250, 'https://api.ftmscan.com/api', 'FTMScan', 'FTM'),
('cronos', 'Cronos', 25, 'https://api.cronoscan.com/api', 'CronoScan', 'CRO'),
('zksync', 'zkSync Era', 324, 'https://api-era.zksync.network/api', 'zkSync Explorer', 'ETH')
ON CONFLICT (slug) DO NOTHING;

-- 2. Token contract metadata
CREATE TABLE IF NOT EXISTS tokens_on_chain (
    id SERIAL PRIMARY KEY,
    coin_id VARCHAR(100) NOT NULL,               -- Reference to coin (e.g., 'ethereum', 'uniswap')
    chain_id INTEGER REFERENCES chains(id),
    contract_address VARCHAR(100) NOT NULL,      -- Token contract address
    
    -- Metadata from explorer API
    token_name VARCHAR(100),
    token_symbol VARCHAR(20),
    decimals INTEGER DEFAULT 18,
    total_supply NUMERIC(78, 0),                 -- Very large numbers for supply
    holder_count INTEGER DEFAULT 0,
    
    -- Additional info
    is_verified BOOLEAN DEFAULT FALSE,           -- Contract verification status
    token_type VARCHAR(20) DEFAULT 'ERC20',      -- ERC20, BEP20, etc.
    
    -- Timestamps
    last_fetched_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Unique constraint
    UNIQUE (chain_id, contract_address)
);

-- Index for fast lookups
CREATE INDEX IF NOT EXISTS idx_tokens_coin_id ON tokens_on_chain(coin_id);
CREATE INDEX IF NOT EXISTS idx_tokens_contract ON tokens_on_chain(contract_address);

-- 3. Top token holders
CREATE TABLE IF NOT EXISTS token_top_holders (
    id SERIAL PRIMARY KEY,
    token_id INTEGER REFERENCES tokens_on_chain(id) ON DELETE CASCADE,
    
    -- Holder info
    rank INTEGER NOT NULL,                       -- 1-100
    wallet_address VARCHAR(100) NOT NULL,
    balance NUMERIC(78, 0) NOT NULL,             -- Raw balance (with decimals)
    balance_formatted NUMERIC(38, 8),            -- Human readable balance
    percentage NUMERIC(10, 6),                   -- Percentage of total supply
    
    -- Labels (if available)
    wallet_label VARCHAR(100),                   -- 'Binance Hot Wallet', 'Uniswap V3'
    is_contract BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Unique constraint per token rank
    UNIQUE (token_id, rank)
);

-- Index for fast lookups
CREATE INDEX IF NOT EXISTS idx_holders_token ON token_top_holders(token_id);
CREATE INDEX IF NOT EXISTS idx_holders_wallet ON token_top_holders(wallet_address);

-- 4. Update trigger for updated_at
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers
DROP TRIGGER IF EXISTS update_chains_modtime ON chains;
CREATE TRIGGER update_chains_modtime
    BEFORE UPDATE ON chains
    FOR EACH ROW EXECUTE FUNCTION update_modified_column();

DROP TRIGGER IF EXISTS update_tokens_modtime ON tokens_on_chain;
CREATE TRIGGER update_tokens_modtime
    BEFORE UPDATE ON tokens_on_chain
    FOR EACH ROW EXECUTE FUNCTION update_modified_column();
