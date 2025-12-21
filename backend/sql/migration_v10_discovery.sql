-- Migration: Market Discovery Snapshot table
-- For fast-access to pre-computed market metrics

-- Snapshot table for market discovery data
CREATE TABLE IF NOT EXISTS market_discovery_snapshot (
    id SERIAL PRIMARY KEY,
    coin_id VARCHAR(50) NOT NULL UNIQUE,
    symbol VARCHAR(20),
    name VARCHAR(100),
    image VARCHAR(500),
    
    -- Current price
    price DECIMAL(30,12),
    
    -- Pre-computed % changes
    change_1h DECIMAL(10,4),
    change_4h DECIMAL(10,4),
    change_24h DECIMAL(10,4),
    change_7d DECIMAL(10,4),
    
    -- Volume metrics
    volume_24h DECIMAL(30,2),
    volume_1h DECIMAL(30,2),           -- Volume in last 1h (for pump detection)
    avg_volume_1h DECIMAL(30,2),       -- Average 1h volume (20 period)
    volume_change_pct DECIMAL(10,4),   -- volume_1h / avg_volume_1h * 100
    
    -- Market cap for filtering
    market_cap DECIMAL(30,2),
    market_cap_rank INT,
    
    -- Pump/Dump detection flags
    is_sudden_pump BOOLEAN DEFAULT FALSE,  -- change_1h > 3% AND volume spike
    is_sudden_dump BOOLEAN DEFAULT FALSE,  -- change_1h < -3% AND volume spike
    
    -- ASI integration
    asi_score INT,
    signal VARCHAR(20),
    
    -- Timestamps
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for fast sorting
CREATE INDEX IF NOT EXISTS idx_discovery_change_1h ON market_discovery_snapshot(change_1h DESC);
CREATE INDEX IF NOT EXISTS idx_discovery_change_4h ON market_discovery_snapshot(change_4h DESC);
CREATE INDEX IF NOT EXISTS idx_discovery_change_24h ON market_discovery_snapshot(change_24h DESC);
CREATE INDEX IF NOT EXISTS idx_discovery_volume ON market_discovery_snapshot(volume_24h DESC);
CREATE INDEX IF NOT EXISTS idx_discovery_pump ON market_discovery_snapshot(is_sudden_pump) WHERE is_sudden_pump = TRUE;
CREATE INDEX IF NOT EXISTS idx_discovery_dump ON market_discovery_snapshot(is_sudden_dump) WHERE is_sudden_dump = TRUE;
CREATE INDEX IF NOT EXISTS idx_discovery_updated ON market_discovery_snapshot(updated_at);
CREATE INDEX IF NOT EXISTS idx_discovery_market_cap ON market_discovery_snapshot(market_cap DESC);

-- View for Top Gainers (1h)
CREATE OR REPLACE VIEW v_top_gainers_1h AS
SELECT coin_id, symbol, name, image, price, change_1h, volume_24h, market_cap, market_cap_rank, asi_score, signal
FROM market_discovery_snapshot
WHERE volume_24h > 100000  -- Filter out low volume
  AND change_1h IS NOT NULL
ORDER BY change_1h DESC
LIMIT 50;

-- View for Top Losers (1h)
CREATE OR REPLACE VIEW v_top_losers_1h AS
SELECT coin_id, symbol, name, image, price, change_1h, volume_24h, market_cap, market_cap_rank, asi_score, signal
FROM market_discovery_snapshot
WHERE volume_24h > 100000
  AND change_1h IS NOT NULL
ORDER BY change_1h ASC
LIMIT 50;

-- View for Sudden Pumps
CREATE OR REPLACE VIEW v_sudden_pumps AS
SELECT coin_id, symbol, name, image, price, change_1h, volume_1h, avg_volume_1h, volume_change_pct, updated_at
FROM market_discovery_snapshot
WHERE is_sudden_pump = TRUE
  AND volume_24h > 100000
ORDER BY change_1h DESC;

-- View for Sudden Dumps (crash detection)
CREATE OR REPLACE VIEW v_sudden_dumps AS
SELECT coin_id, symbol, name, image, price, change_1h, volume_1h, avg_volume_1h, volume_change_pct, updated_at
FROM market_discovery_snapshot
WHERE is_sudden_dump = TRUE
  AND volume_24h > 100000
ORDER BY change_1h ASC;

-- Enable RLS
ALTER TABLE market_discovery_snapshot ENABLE ROW LEVEL SECURITY;

-- Allow public read access
CREATE POLICY "Allow public read on discovery" ON market_discovery_snapshot
    FOR SELECT USING (true);

-- Allow service role full access
CREATE POLICY "Allow service full access on discovery" ON market_discovery_snapshot
    FOR ALL USING (true);

COMMENT ON TABLE market_discovery_snapshot IS 'Pre-computed market discovery metrics updated every 5 minutes';
