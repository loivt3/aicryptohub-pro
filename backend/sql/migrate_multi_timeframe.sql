-- ============================================
-- Multi-Timeframe Migration Script
-- Run this on Proxmox server to update schema
-- ============================================

-- 1. Add new indexes for multi-timeframe queries
CREATE INDEX IF NOT EXISTS idx_ohlcv_timeframe ON aihub_ohlcv(timeframe);
CREATE INDEX IF NOT EXISTS idx_ohlcv_symbol_tf_time ON aihub_ohlcv(symbol, timeframe, open_time);

-- 2. Add unique constraint for OHLCV deduplication (prevents duplicate candles)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'uq_ohlcv_symbol_tf_time'
    ) THEN
        ALTER TABLE aihub_ohlcv ADD CONSTRAINT uq_ohlcv_symbol_tf_time 
            UNIQUE (symbol, timeframe, open_time);
    END IF;
END $$;

-- 3. Fix any existing wrong timeframe codes (60 should be 1)
UPDATE aihub_ohlcv SET timeframe = 1 WHERE timeframe = 60;

-- 4. Verify changes
SELECT 
    timeframe, 
    COUNT(*) as count,
    MIN(open_time) as oldest,
    MAX(open_time) as newest
FROM aihub_ohlcv 
GROUP BY timeframe 
ORDER BY timeframe;
