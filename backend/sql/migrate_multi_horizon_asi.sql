-- ============================================
-- Multi-Horizon ASI Migration Script
-- Adds short/medium/long-term ASI columns
-- ============================================

-- 1. Add new columns to aihub_sentiment
ALTER TABLE aihub_sentiment 
ADD COLUMN IF NOT EXISTS asi_short INTEGER DEFAULT 50,
ADD COLUMN IF NOT EXISTS asi_medium INTEGER DEFAULT 50,
ADD COLUMN IF NOT EXISTS asi_long INTEGER DEFAULT 50,
ADD COLUMN IF NOT EXISTS onchain_score INTEGER DEFAULT 50,
ADD COLUMN IF NOT EXISTS onchain_available BOOLEAN DEFAULT FALSE;

-- 2. Add comment for documentation
COMMENT ON COLUMN aihub_sentiment.asi_short IS 'Short-term ASI (1m+1h) for scalp/day trading';
COMMENT ON COLUMN aihub_sentiment.asi_medium IS 'Medium-term ASI (4h+1d) for swing trading';
COMMENT ON COLUMN aihub_sentiment.asi_long IS 'Long-term ASI (1d+1w) for position/HODL';
COMMENT ON COLUMN aihub_sentiment.onchain_score IS 'On-chain score (whale+network+holders)';

-- 3. Rename existing score column for clarity if needed
-- Note: sentiment_score is the existing combined score (0-1 scale)
-- asi_short/medium/long are 0-100 scale

-- 4. Verify changes
SELECT column_name, data_type, column_default 
FROM information_schema.columns 
WHERE table_name = 'aihub_sentiment'
ORDER BY ordinal_position;
