-- ============================================
-- Multi-Horizon ASI Migration Script
-- RUN AS SUPERUSER: psql -U postgres -d aihub_pro -f ...
-- ============================================

-- 1. Add new columns to aihub_sentiment
ALTER TABLE aihub_sentiment 
ADD COLUMN IF NOT EXISTS asi_short INTEGER DEFAULT 50,
ADD COLUMN IF NOT EXISTS asi_medium INTEGER DEFAULT 50,
ADD COLUMN IF NOT EXISTS asi_long INTEGER DEFAULT 50,
ADD COLUMN IF NOT EXISTS onchain_score INTEGER DEFAULT 50,
ADD COLUMN IF NOT EXISTS onchain_available BOOLEAN DEFAULT FALSE;

-- 2. Grant permissions to aihub_pro user
GRANT ALL ON TABLE aihub_sentiment TO aihub_pro;

-- 3. Verify changes
SELECT column_name, data_type, column_default 
FROM information_schema.columns 
WHERE table_name = 'aihub_sentiment'
ORDER BY ordinal_position;
