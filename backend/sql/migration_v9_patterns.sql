-- Migration: Add candlestick patterns table for backtesting
-- Run on Supabase: Dashboard > SQL Editor > New Query

-- Table to store detected candlestick patterns
CREATE TABLE IF NOT EXISTS aihub_patterns (
    id SERIAL PRIMARY KEY,
    coin_id VARCHAR(50) NOT NULL,
    symbol VARCHAR(20),
    timeframe VARCHAR(10) NOT NULL,  -- '1h', '4h', '1d', '1w'
    
    -- Pattern details
    pattern VARCHAR(50) NOT NULL,     -- 'Bullish Engulfing', 'Morning Star', etc.
    direction VARCHAR(20) NOT NULL,   -- 'BULLISH', 'BEARISH', 'NEUTRAL'
    reliability VARCHAR(10) NOT NULL, -- 'HIGH', 'WEAK'
    priority INT DEFAULT 5,           -- Pattern priority 1-10
    
    -- Volume confirmation
    volume_ratio DECIMAL(5,2),        -- Volume / SMA20 ratio
    
    -- Price at detection (for accuracy calculation)
    price_at_detection DECIMAL(20,8),
    price_after_24h DECIMAL(20,8),    -- Filled by scheduler later
    price_after_72h DECIMAL(20,8),    -- Filled by scheduler later
    
    -- Pattern accuracy tracking
    was_accurate BOOLEAN,             -- True if price moved in predicted direction
    profit_24h DECIMAL(10,4),         -- % change after 24h
    profit_72h DECIMAL(10,4),         -- % change after 72h
    
    -- Metadata
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    candle_timestamp TIMESTAMP,       -- Timestamp of the candle that formed pattern
    
    -- Indexes
    CONSTRAINT unique_pattern_detection UNIQUE (coin_id, timeframe, pattern, candle_timestamp)
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_patterns_coin ON aihub_patterns(coin_id);
CREATE INDEX IF NOT EXISTS idx_patterns_pattern ON aihub_patterns(pattern);
CREATE INDEX IF NOT EXISTS idx_patterns_direction ON aihub_patterns(direction);
CREATE INDEX IF NOT EXISTS idx_patterns_detected_at ON aihub_patterns(detected_at);
CREATE INDEX IF NOT EXISTS idx_patterns_timeframe ON aihub_patterns(timeframe);
CREATE INDEX IF NOT EXISTS idx_patterns_reliability ON aihub_patterns(reliability);

-- Views for analysis
CREATE OR REPLACE VIEW v_pattern_accuracy AS
SELECT 
    pattern,
    direction,
    reliability,
    timeframe,
    COUNT(*) as total_detections,
    COUNT(CASE WHEN was_accurate = true THEN 1 END) as accurate_count,
    ROUND(
        100.0 * COUNT(CASE WHEN was_accurate = true THEN 1 END) / NULLIF(COUNT(*), 0), 
        2
    ) as accuracy_pct,
    ROUND(AVG(profit_24h), 2) as avg_profit_24h,
    ROUND(AVG(profit_72h), 2) as avg_profit_72h
FROM aihub_patterns
WHERE was_accurate IS NOT NULL
GROUP BY pattern, direction, reliability, timeframe
ORDER BY accuracy_pct DESC;

-- View for recent patterns
CREATE OR REPLACE VIEW v_recent_patterns AS
SELECT 
    p.coin_id,
    p.symbol,
    p.timeframe,
    p.pattern,
    p.direction,
    p.reliability,
    p.volume_ratio,
    p.price_at_detection,
    p.detected_at
FROM aihub_patterns p
WHERE p.detected_at > NOW() - INTERVAL '24 hours'
ORDER BY p.detected_at DESC;

-- Enable RLS
ALTER TABLE aihub_patterns ENABLE ROW LEVEL SECURITY;

-- Allow public read access
CREATE POLICY "Allow public read access on patterns" ON aihub_patterns
    FOR SELECT USING (true);

-- Allow service role full access
CREATE POLICY "Allow service role full access on patterns" ON aihub_patterns
    FOR ALL USING (true);

COMMENT ON TABLE aihub_patterns IS 'Candlestick pattern detection history for backtesting and accuracy analysis';
