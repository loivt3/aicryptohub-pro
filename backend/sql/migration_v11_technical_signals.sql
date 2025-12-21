-- Migration V11: Add technical indicator columns to market_discovery_snapshot
-- For MACD, Bollinger Bands, RSI, Pattern Detection, and Confirmation System

-- Add new columns for advanced technical analysis
ALTER TABLE market_discovery_snapshot
ADD COLUMN IF NOT EXISTS momentum_score INT,
ADD COLUMN IF NOT EXISTS trend_score DECIMAL(3,1),
ADD COLUMN IF NOT EXISTS trend_label VARCHAR(20),
ADD COLUMN IF NOT EXISTS rs_vs_btc DECIMAL(10,2),
ADD COLUMN IF NOT EXISTS rs_vs_market DECIMAL(10,2),
ADD COLUMN IF NOT EXISTS rs_score INT,
ADD COLUMN IF NOT EXISTS is_outperformer BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS is_anomaly BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS anomaly_type VARCHAR(20);

-- Candlestick pattern columns
ALTER TABLE market_discovery_snapshot
ADD COLUMN IF NOT EXISTS pattern_name VARCHAR(50),
ADD COLUMN IF NOT EXISTS pattern_direction VARCHAR(20),
ADD COLUMN IF NOT EXISTS pattern_reliability VARCHAR(20),
ADD COLUMN IF NOT EXISTS pattern_score INT DEFAULT 0;

-- RSI divergence columns
ALTER TABLE market_discovery_snapshot
ADD COLUMN IF NOT EXISTS rsi_14 DECIMAL(5,1),
ADD COLUMN IF NOT EXISTS has_divergence BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS divergence_type VARCHAR(20),
ADD COLUMN IF NOT EXISTS divergence_score INT DEFAULT 0;

-- MACD columns
ALTER TABLE market_discovery_snapshot
ADD COLUMN IF NOT EXISTS macd_histogram DECIMAL(20,8),
ADD COLUMN IF NOT EXISTS macd_signal_type VARCHAR(20),
ADD COLUMN IF NOT EXISTS macd_confirmed BOOLEAN DEFAULT FALSE;

-- Bollinger Bands columns
ALTER TABLE market_discovery_snapshot
ADD COLUMN IF NOT EXISTS bb_position VARCHAR(20),
ADD COLUMN IF NOT EXISTS bb_squeeze BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS bb_width DECIMAL(10,4),
ADD COLUMN IF NOT EXISTS bb_signal BOOLEAN DEFAULT FALSE;

-- Confirmation system columns
ALTER TABLE market_discovery_snapshot
ADD COLUMN IF NOT EXISTS volume_confirmed BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS ma_confirmed BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS rsi_extreme BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS near_sr BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS mtf_aligned BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS confirmation_count INT DEFAULT 0,
ADD COLUMN IF NOT EXISTS confirmation_score INT DEFAULT 0;

-- Discovery score and signal strength
ALTER TABLE market_discovery_snapshot
ADD COLUMN IF NOT EXISTS discovery_score INT,
ADD COLUMN IF NOT EXISTS signal_strength VARCHAR(30);

-- Create indexes for new columns
CREATE INDEX IF NOT EXISTS idx_discovery_momentum ON market_discovery_snapshot(momentum_score DESC);
CREATE INDEX IF NOT EXISTS idx_discovery_pattern ON market_discovery_snapshot(pattern_direction) WHERE pattern_direction IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_discovery_divergence ON market_discovery_snapshot(divergence_type) WHERE divergence_type IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_discovery_confirmation ON market_discovery_snapshot(confirmation_count DESC);
CREATE INDEX IF NOT EXISTS idx_discovery_score ON market_discovery_snapshot(discovery_score DESC);
CREATE INDEX IF NOT EXISTS idx_discovery_signal ON market_discovery_snapshot(signal_strength) WHERE signal_strength IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_discovery_outperformer ON market_discovery_snapshot(is_outperformer) WHERE is_outperformer = TRUE;
CREATE INDEX IF NOT EXISTS idx_discovery_bb_squeeze ON market_discovery_snapshot(bb_squeeze) WHERE bb_squeeze = TRUE;

-- View for Technical Signals
CREATE OR REPLACE VIEW v_technical_signals AS
SELECT 
    coin_id, symbol, name, image, price,
    change_1h, change_24h,
    pattern_name, pattern_direction, pattern_reliability,
    divergence_type, rsi_14,
    macd_signal_type, macd_histogram,
    bb_position, bb_squeeze, bb_width,
    confirmation_count, confirmation_score,
    signal_strength, discovery_score,
    volume_24h, market_cap_rank,
    updated_at
FROM market_discovery_snapshot
WHERE (pattern_name IS NOT NULL OR divergence_type IS NOT NULL)
  AND volume_24h > 100000
ORDER BY confirmation_count DESC, discovery_score DESC
LIMIT 50;

-- View for Hidden Gems
CREATE OR REPLACE VIEW v_hidden_gems AS
SELECT 
    coin_id, symbol, name, image, price,
    change_1h, change_24h, change_7d,
    momentum_score, rs_score, discovery_score,
    rs_vs_btc, rs_vs_market,
    pattern_name, pattern_direction,
    confirmation_count, signal_strength,
    volume_24h, market_cap, market_cap_rank
FROM market_discovery_snapshot
WHERE discovery_score >= 70
  AND market_cap_rank > 100
  AND is_outperformer = TRUE
  AND volume_24h > 100000
ORDER BY discovery_score DESC, confirmation_count DESC
LIMIT 30;

-- View for Bollinger Bands Squeeze (potential breakouts)
CREATE OR REPLACE VIEW v_bb_squeeze AS
SELECT 
    coin_id, symbol, name, image, price,
    change_1h, change_24h,
    bb_width, pattern_name, pattern_direction,
    macd_signal_type, confirmation_count,
    volume_24h, market_cap_rank
FROM market_discovery_snapshot
WHERE bb_squeeze = TRUE
  AND volume_24h > 100000
ORDER BY bb_width ASC
LIMIT 30;

COMMENT ON COLUMN market_discovery_snapshot.momentum_score IS 'Multi-factor momentum score 0-100';
COMMENT ON COLUMN market_discovery_snapshot.trend_score IS 'Trend strength -5 to +5';
COMMENT ON COLUMN market_discovery_snapshot.pattern_name IS 'Detected candlestick pattern';
COMMENT ON COLUMN market_discovery_snapshot.divergence_type IS 'BULLISH_DIV or BEARISH_DIV';
COMMENT ON COLUMN market_discovery_snapshot.macd_signal_type IS 'BULLISH, BEARISH, BULLISH_CROSS, BEARISH_CROSS';
COMMENT ON COLUMN market_discovery_snapshot.bb_squeeze IS 'Bollinger Bands squeeze (low volatility)';
COMMENT ON COLUMN market_discovery_snapshot.confirmation_count IS 'Number of confirming factors (0-7)';
COMMENT ON COLUMN market_discovery_snapshot.discovery_score IS 'Combined discovery score 0-100';
COMMENT ON COLUMN market_discovery_snapshot.signal_strength IS 'Signal strength: VERY_STRONG_BULL, STRONG_BULLISH, CONFIRMED_BULL, BULLISH, etc';
