-- ==============================================
-- Seed Exchange Addresses for On-Chain Collector
-- AI Crypto Hub Pro
-- ==============================================
-- This script populates the known_addresses table with major exchange hot wallets
-- Enables accurate inflow/outflow classification for whale transactions

-- Create table if not exists
CREATE TABLE IF NOT EXISTS known_addresses (
    id SERIAL PRIMARY KEY,
    address VARCHAR(100) NOT NULL,
    chain_slug VARCHAR(50) DEFAULT 'ethereum',
    address_type VARCHAR(50) DEFAULT 'exchange',  -- 'exchange', 'bridge', 'contract'
    label VARCHAR(100),
    exchange_name VARCHAR(50),
    is_deposit BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (address, chain_slug)
);

-- ===========================
-- BINANCE HOT WALLETS (10)
-- ===========================
INSERT INTO known_addresses (address, chain_slug, label, exchange_name, is_deposit) VALUES
('0x28c6c06298d514db089934071355e5743bf21d60', 'ethereum', 'Binance Hot 14', 'Binance', false),
('0x21a31ee1afc51d94c2efccaa2092ad1028285549', 'ethereum', 'Binance 20', 'Binance', false),
('0xdfd5293d8e347dfe59e90efd55b2956a1343963d', 'ethereum', 'Binance 8', 'Binance', false),
('0x56eddb7aa87536c09ccc2793473599fd21a8b17f', 'ethereum', 'Binance 16', 'Binance', false),
('0x9696f59e4d72e237be84ffd425dcad154bf96976', 'ethereum', 'Binance 18', 'Binance', false),
('0xf977814e90da44bfa03b6295a0616a897441acec', 'ethereum', 'Binance 1', 'Binance', false),
('0xbe0eb53f46cd790cd13851d5eff43d12404d33e8', 'ethereum', 'Binance 7', 'Binance', true),
('0x5a52e96bacdabb82fd05763e25335261b270efcb', 'ethereum', 'Binance 6', 'Binance', false),
('0x3c783c21a0383057d128bae431894a5c19f9cf06', 'ethereum', 'Binance 4', 'Binance', false),
('0xb3f923eabaf178fc1bd8e13902fc5c61d3ddef5b', 'ethereum', 'Binance 3', 'Binance', false)
ON CONFLICT (address, chain_slug) DO NOTHING;

-- BSC Binance
INSERT INTO known_addresses (address, chain_slug, label, exchange_name, is_deposit) VALUES
('0x8894e0a0c962cb723c1976a4421c95949be2d4e3', 'bsc', 'Binance Hot BSC 1', 'Binance', false),
('0xe2fc31f816a9b94326492132018c3aecc4a93ae1', 'bsc', 'Binance Hot BSC 2', 'Binance', false)
ON CONFLICT (address, chain_slug) DO NOTHING;

-- ===========================
-- COINBASE (5)
-- ===========================
INSERT INTO known_addresses (address, chain_slug, label, exchange_name, is_deposit) VALUES
('0x503828976d22510aad0201ac7ec88293211d23da', 'ethereum', 'Coinbase 2', 'Coinbase', false),
('0x71660c4005ba85c37ccec55d0c4493e66fe775d3', 'ethereum', 'Coinbase 3', 'Coinbase', false),
('0xddfabcdc4d8ffc6d5beaf154f18b778f892a0740', 'ethereum', 'Coinbase 4', 'Coinbase', false),
('0xa9d1e08c7793af67e9d92fe308d5697fb81d3e43', 'ethereum', 'Coinbase 6', 'Coinbase', false),
('0x77696bb39917c91a0c3908d577d5e322095425ca', 'ethereum', 'Coinbase 7', 'Coinbase', false)
ON CONFLICT (address, chain_slug) DO NOTHING;

-- ===========================
-- OKX / OKEX (5)
-- ===========================
INSERT INTO known_addresses (address, chain_slug, label, exchange_name, is_deposit) VALUES
('0x6cc5f688a315f3dc28a7781717a9a798a59fda7b', 'ethereum', 'OKX', 'OKX', false),
('0x236f9f97e0e62388479bf9e5ba4889e46b0273c3', 'ethereum', 'OKX 2', 'OKX', false),
('0xa7efae728d2936e78bda97dc267687568dd593f3', 'ethereum', 'OKX 3', 'OKX', false),
('0x98ec059dc3adfbdd63429454aeb0c990fba4a128', 'ethereum', 'OKX 4', 'OKX', false),
('0x5050f69a03b5ef9e50dc7f4d0b0750b3f8c7c6bc', 'ethereum', 'OKX 5', 'OKX', false)
ON CONFLICT (address, chain_slug) DO NOTHING;

-- ===========================
-- KRAKEN (4)
-- ===========================
INSERT INTO known_addresses (address, chain_slug, label, exchange_name, is_deposit) VALUES
('0x2910543af39aba0cd09dbb2d50200b3e800a63d2', 'ethereum', 'Kraken 4', 'Kraken', false),
('0x0a869d79a7052c7f1b55a8ebabbea3420f0d1e13', 'ethereum', 'Kraken 6', 'Kraken', false),
('0xe853c56864a2ebe4576a807d26fdc4a0ada51919', 'ethereum', 'Kraken 3', 'Kraken', false),
('0xda9dfa130df4de4673b89022ee50ff26f6ea73cf', 'ethereum', 'Kraken 5', 'Kraken', false)
ON CONFLICT (address, chain_slug) DO NOTHING;

-- ===========================
-- BYBIT (4)
-- ===========================
INSERT INTO known_addresses (address, chain_slug, label, exchange_name, is_deposit) VALUES
('0xf89d7b9c864f589bbf53a82105107622b35eaa40', 'ethereum', 'Bybit Hot', 'Bybit', false),
('0x1db92e2eebc8e0c075a02bea49a2935bcd2dfcf4', 'ethereum', 'Bybit 2', 'Bybit', false),
('0xee5b5b923ffce93a870b3104b7ca09c3db80047a', 'ethereum', 'Bybit 3', 'Bybit', false),
('0x6cfc6efca15b5ba69f64dc3346f3a8c2d36bde0c', 'ethereum', 'Bybit 4', 'Bybit', false)
ON CONFLICT (address, chain_slug) DO NOTHING;

-- ===========================
-- KUCOIN (3)
-- ===========================
INSERT INTO known_addresses (address, chain_slug, label, exchange_name, is_deposit) VALUES
('0x2b5634c42055806a59e9107ed44d43c426e58258', 'ethereum', 'KuCoin', 'KuCoin', false),
('0x689c56aef474df92d44a1b70850f808488f9769c', 'ethereum', 'KuCoin 2', 'KuCoin', false),
('0xa3f68d722fba26173e60d1f213bcf4a50d379b6e', 'ethereum', 'KuCoin 3', 'KuCoin', false)
ON CONFLICT (address, chain_slug) DO NOTHING;

-- ===========================
-- HUOBI / HTX (4)
-- ===========================
INSERT INTO known_addresses (address, chain_slug, label, exchange_name, is_deposit) VALUES
('0x5401dbf7da53e1c9dbf484e3d69505815f2f5e6e', 'ethereum', 'HTX', 'HTX', false),
('0xecd0d12e21805553f6287c3d8e28dc27e8e37a8a', 'ethereum', 'HTX 2', 'HTX', false),
('0x46340b20830761efd32832a74d7169b29feb9758', 'ethereum', 'HTX 3', 'HTX', false),
('0x1062a747393198f70f71ec65a582423dba7e5ab3', 'ethereum', 'HTX 4', 'HTX', false)
ON CONFLICT (address, chain_slug) DO NOTHING;

-- ===========================
-- GATE.IO (3)
-- ===========================
INSERT INTO known_addresses (address, chain_slug, label, exchange_name, is_deposit) VALUES
('0x0d0707963952f2fba59dd06f2b425ace40b492fe', 'ethereum', 'Gate.io', 'Gate.io', false),
('0x1c4b70a3968436b9a0a9cf5205c787eb81bb558c', 'ethereum', 'Gate.io 2', 'Gate.io', false),
('0xd793281182a0e3e023116f6c08bb84f09da0b59f', 'ethereum', 'Gate.io 3', 'Gate.io', false)
ON CONFLICT (address, chain_slug) DO NOTHING;

-- ===========================
-- BITFINEX (3)
-- ===========================
INSERT INTO known_addresses (address, chain_slug, label, exchange_name, is_deposit) VALUES
('0x876eabf441b2ee5b5b0554fd502a8e0600950cfa', 'ethereum', 'Bitfinex', 'Bitfinex', false),
('0x742d35cc6634c0532925a3b844bc454e4438f44e', 'ethereum', 'Bitfinex 2', 'Bitfinex', false),
('0x1151314c646ce4e0efd76d1af4760ae66a9fe30f', 'ethereum', 'Bitfinex 3', 'Bitfinex', false)
ON CONFLICT (address, chain_slug) DO NOTHING;

-- ===========================
-- CRYPTO.COM (2)
-- ===========================
INSERT INTO known_addresses (address, chain_slug, label, exchange_name, is_deposit) VALUES
('0x6262998ced04146fa42253a5c0af90ca02dfd2a3', 'ethereum', 'Crypto.com', 'Crypto.com', false),
('0x46340b20830761efd32832a74d7169b29feb9758', 'ethereum', 'Crypto.com 2', 'Crypto.com', false)
ON CONFLICT (address, chain_slug) DO NOTHING;

-- ===========================
-- GEMINI (2)
-- ===========================
INSERT INTO known_addresses (address, chain_slug, label, exchange_name, is_deposit) VALUES
('0xd24400ae8bfebb18ca49be86258a3c749cf46853', 'ethereum', 'Gemini', 'Gemini', false),
('0x6fc82a5fe25a5cdb58bc74600a40a69c065263f8', 'ethereum', 'Gemini 2', 'Gemini', false)
ON CONFLICT (address, chain_slug) DO NOTHING;

-- Log completion
DO $$
BEGIN
    RAISE NOTICE 'Successfully seeded % exchange addresses', 
        (SELECT COUNT(*) FROM known_addresses WHERE address_type = 'exchange');
END $$;
