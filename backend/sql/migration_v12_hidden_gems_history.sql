-- Migration V12: Hidden Gems Historical Tracking
-- Purpose: Track hidden gems detected and their performance over time
-- Created: 2024-12-22

-- ============================================================================
-- TABLE: hidden_gems_history
-- Tracks all gems detected and their 7d/30d performance
-- ============================================================================
CREATE TABLE IF NOT EXISTS hidden_gems_history (
    id SERIAL PRIMARY KEY,
    coin_id VARCHAR(100) NOT NULL,
    symbol VARCHAR(20),
    name VARCHAR(200),
    
    -- Detection context
    detected_at TIMESTAMP DEFAULT NOW(),
    detection_price DECIMAL(20, 8),
    discovery_score INT,
    signal_strength VARCHAR(50),
    confirmation_count INT,
    
    -- Why it was detected
    pattern_name VARCHAR(100),
    divergence_type VARCHAR(50),
    rs_vs_btc DECIMAL(10, 4),
    rs_vs_market DECIMAL(10, 4),
    volume_ratio DECIMAL(10, 4),
    is_accumulating BOOLEAN DEFAULT FALSE,
    
    -- Performance tracking (updated by scheduled job)
    price_7d DECIMAL(20, 8),
    price_14d DECIMAL(20, 8),
    price_30d DECIMAL(20, 8),
    return_7d DECIMAL(10, 4),   -- % return after 7 days
    return_14d DECIMAL(10, 4),  -- % return after 14 days
    return_30d DECIMAL(10, 4),  -- % return after 30 days
    btc_return_7d DECIMAL(10, 4),   -- BTC return for comparison
    btc_return_30d DECIMAL(10, 4),
    
    -- Evaluation
    status VARCHAR(20) DEFAULT 'pending', -- pending, success, failed, neutral
    evaluated_at TIMESTAMP
);

-- Unique constraint using functional index (one gem per coin per day)
CREATE UNIQUE INDEX IF NOT EXISTS idx_gems_history_unique_daily 
ON hidden_gems_history(coin_id, DATE(detected_at));

-- Indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_gems_history_coin ON hidden_gems_history(coin_id);
CREATE INDEX IF NOT EXISTS idx_gems_history_date ON hidden_gems_history(detected_at);
CREATE INDEX IF NOT EXISTS idx_gems_history_status ON hidden_gems_history(status);
CREATE INDEX IF NOT EXISTS idx_gems_history_score ON hidden_gems_history(discovery_score DESC);

-- ============================================================================
-- VIEW: v_gems_performance_summary
-- Summary statistics for gems performance
-- ============================================================================
CREATE OR REPLACE VIEW v_gems_performance_summary AS
SELECT 
    DATE(detected_at) as detection_date,
    COUNT(*) as gems_detected,
    COUNT(CASE WHEN status = 'success' THEN 1 END) as success_count,
    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_count,
    COUNT(CASE WHEN status = 'neutral' THEN 1 END) as neutral_count,
    ROUND(AVG(return_7d), 2) as avg_return_7d,
    ROUND(AVG(return_30d), 2) as avg_return_30d,
    ROUND(
        100.0 * COUNT(CASE WHEN status = 'success' THEN 1 END) / 
        NULLIF(COUNT(CASE WHEN status IN ('success', 'failed') THEN 1 END), 0), 
        1
    ) as success_rate_pct
FROM hidden_gems_history
WHERE evaluated_at IS NOT NULL
GROUP BY DATE(detected_at)
ORDER BY detection_date DESC;

-- ============================================================================
-- VIEW: v_gems_overall_stats
-- Overall performance statistics
-- ============================================================================
CREATE OR REPLACE VIEW v_gems_overall_stats AS
SELECT 
    COUNT(*) as total_gems,
    COUNT(CASE WHEN status = 'success' THEN 1 END) as total_success,
    COUNT(CASE WHEN status = 'failed' THEN 1 END) as total_failed,
    ROUND(AVG(return_7d), 2) as avg_return_7d,
    ROUND(AVG(return_30d), 2) as avg_return_30d,
    ROUND(AVG(btc_return_7d), 2) as avg_btc_return_7d,
    ROUND(AVG(return_7d) - AVG(btc_return_7d), 2) as alpha_7d,
    ROUND(AVG(return_30d) - AVG(btc_return_30d), 2) as alpha_30d,
    ROUND(
        100.0 * COUNT(CASE WHEN status = 'success' THEN 1 END) / 
        NULLIF(COUNT(CASE WHEN status IN ('success', 'failed') THEN 1 END), 0), 
        1
    ) as success_rate_pct,
    MAX(return_30d) as best_return_30d,
    MIN(return_30d) as worst_return_30d
FROM hidden_gems_history
WHERE evaluated_at IS NOT NULL;

-- ============================================================================
-- Add accumulation flag to market_discovery_snapshot
-- ============================================================================
ALTER TABLE market_discovery_snapshot 
ADD COLUMN IF NOT EXISTS is_accumulating BOOLEAN DEFAULT FALSE;

ALTER TABLE market_discovery_snapshot 
ADD COLUMN IF NOT EXISTS accumulation_score INT DEFAULT 0;

-- ============================================================================
-- Comments
-- ============================================================================
COMMENT ON TABLE hidden_gems_history IS 'Historical tracking of detected hidden gems and their performance';
COMMENT ON COLUMN hidden_gems_history.status IS 'pending=awaiting evaluation, success=>25% 30d return, failed=<-20% 30d return, neutral=between';
COMMENT ON COLUMN hidden_gems_history.is_accumulating IS 'True if detected during accumulation phase (high volume + stable price)';
