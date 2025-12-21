-- Migration: Add contract_address and chain_id to aihub_coins
-- Run on BOTH Supabase and Proxmox

-- ============================================
-- Add contract_address column to aihub_coins
-- ============================================
ALTER TABLE aihub_coins 
ADD COLUMN IF NOT EXISTS contract_address character varying;

ALTER TABLE aihub_coins 
ADD COLUMN IF NOT EXISTS chain_id integer DEFAULT 1;

ALTER TABLE aihub_coins 
ADD COLUMN IF NOT EXISTS chain_slug character varying DEFAULT 'ethereum';

ALTER TABLE aihub_coins 
ADD COLUMN IF NOT EXISTS decimals integer DEFAULT 18;

-- Index for faster lookups
CREATE INDEX IF NOT EXISTS idx_coins_contract_address 
ON aihub_coins(contract_address) 
WHERE contract_address IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_coins_chain_id 
ON aihub_coins(chain_id);

-- ============================================
-- Populate contract_address from tokens_on_chain
-- (if tokens_on_chain exists and has data)
-- ============================================
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'tokens_on_chain') THEN
        UPDATE aihub_coins c
        SET 
            contract_address = t.contract_address,
            chain_id = t.chain_id,
            decimals = t.decimals
        FROM tokens_on_chain t
        WHERE c.coin_id = t.coin_id
          AND c.contract_address IS NULL
          AND t.chain_id = 1;  -- Prioritize Ethereum mainnet
    END IF;
END $$;

-- ============================================
-- Create onchain_signals table if not exists
-- (needed for on-chain ASI integration)
-- ============================================
CREATE TABLE IF NOT EXISTS onchain_signals (
    id SERIAL PRIMARY KEY,
    coin_id character varying NOT NULL UNIQUE,
    -- Whale Activity
    whale_tx_count_24h integer DEFAULT 0,
    whale_tx_change_pct numeric DEFAULT 0,
    whale_inflow_usd numeric DEFAULT 0,
    whale_outflow_usd numeric DEFAULT 0,
    whale_net_flow_usd numeric DEFAULT 0,
    whale_signal character varying DEFAULT 'NEUTRAL',
    -- Network Health / DAU
    dau_current integer DEFAULT 0,
    dau_prev_day integer DEFAULT 0,
    dau_change_1d_pct numeric DEFAULT 0,
    dau_trend character varying DEFAULT 'stable',
    network_signal character varying DEFAULT 'NEUTRAL',
    -- Top Holders
    top10_change_pct numeric DEFAULT 0,
    accumulation_score numeric DEFAULT 0,
    holder_signal character varying DEFAULT 'NEUTRAL',
    -- Overall
    overall_signal character varying DEFAULT 'NEUTRAL',
    bullish_probability numeric DEFAULT 50,
    confidence_score numeric DEFAULT 0,
    ai_prediction character varying,
    ai_summary text,
    -- Metadata
    last_whale_update timestamp without time zone,
    last_dau_update timestamp without time zone,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

-- Index for onchain_signals
CREATE INDEX IF NOT EXISTS idx_onchain_signals_coin 
ON onchain_signals(coin_id);

CREATE INDEX IF NOT EXISTS idx_onchain_signals_overall 
ON onchain_signals(overall_signal);

-- ============================================
-- Create behavioral_sentiment table if not exists
-- ============================================
CREATE TABLE IF NOT EXISTS behavioral_sentiment (
    id SERIAL PRIMARY KEY,
    coin_id character varying NOT NULL,
    symbol character varying NOT NULL,
    sentiment_score integer DEFAULT 50,
    emotional_tone character varying DEFAULT 'neutral',
    expected_crowd_action character varying DEFAULT 'hold',
    news_intensity integer DEFAULT 1,
    dominant_category character varying,
    impact_duration character varying,
    whale_alignment character varying,
    intent_divergence_score integer DEFAULT 0,
    confidence_score numeric DEFAULT 0.5,
    related_event_ids jsonb DEFAULT '[]',
    reasoning text,
    raw_ai_response text,
    provider character varying DEFAULT 'gemini',
    analyzed_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_behavioral_sentiment_coin 
ON behavioral_sentiment(coin_id, analyzed_at DESC);

-- Done!
SELECT 'Migration completed: contract_address added to aihub_coins' as status;
