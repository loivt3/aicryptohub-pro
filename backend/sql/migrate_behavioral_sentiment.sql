-- ============================================
-- AI Behavioral Alpha - Database Migration
-- Adds new fields for advanced sentiment analysis
-- ============================================

-- Add new columns to aihub_sentiment table
ALTER TABLE aihub_sentiment 
    ADD COLUMN IF NOT EXISTS emotional_tone VARCHAR(20) DEFAULT 'Neutral',
    ADD COLUMN IF NOT EXISTS expected_crowd_action VARCHAR(30) DEFAULT 'Hold',
    ADD COLUMN IF NOT EXISTS news_intensity INTEGER DEFAULT 5,
    ADD COLUMN IF NOT EXISTS impact_duration VARCHAR(10) DEFAULT 'days',
    ADD COLUMN IF NOT EXISTS event_id VARCHAR(100),
    ADD COLUMN IF NOT EXISTS emotional_category VARCHAR(30),
    ADD COLUMN IF NOT EXISTS dominant_news_category VARCHAR(30);

-- Create news_events table for tracking crypto news
CREATE TABLE IF NOT EXISTS news_events (
    id SERIAL PRIMARY KEY,
    event_id VARCHAR(100) UNIQUE NOT NULL,
    coin_id VARCHAR(50),
    symbol VARCHAR(20),
    title TEXT NOT NULL,
    summary TEXT,
    source VARCHAR(100),
    source_url TEXT,
    category VARCHAR(30),  -- regulatory, technical, whale_movement, social_hype
    publish_time TIMESTAMP NOT NULL,
    event_time TIMESTAMP,  -- Extracted actual event time (may differ from publish)
    sentiment_score INTEGER DEFAULT 50,
    emotional_tone VARCHAR(20) DEFAULT 'Neutral',
    news_intensity INTEGER DEFAULT 5,
    is_front_running BOOLEAN DEFAULT FALSE,  -- True if event_time << publish_time
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create behavioral_sentiment table for high-granularity analysis
CREATE TABLE IF NOT EXISTS behavioral_sentiment (
    id SERIAL PRIMARY KEY,
    coin_id VARCHAR(50) NOT NULL,
    symbol VARCHAR(20),
    -- Core sentiment
    sentiment_score INTEGER DEFAULT 50,  -- 0-100
    emotional_tone VARCHAR(20) DEFAULT 'Neutral',  -- Fear, FUD, FOMO, Euphoria, Neutral
    -- Crowd behavior prediction
    expected_crowd_action VARCHAR(30) DEFAULT 'Hold',  -- Sell-off, Buy-dip, Hold, FOMO-buy, Panic-sell
    news_intensity INTEGER DEFAULT 5,  -- 1-10
    -- News context
    dominant_category VARCHAR(30),  -- regulatory, technical, whale_movement, social_hype
    impact_duration VARCHAR(10) DEFAULT 'days',  -- hours, days, weeks
    related_event_ids TEXT[],  -- Array of news event IDs
    -- Whale correlation
    whale_alignment VARCHAR(20),  -- with_crowd, against_crowd, neutral
    intent_divergence_score FLOAT DEFAULT 0,  -- -100 to +100
    -- Metadata
    analysis_source VARCHAR(50) DEFAULT 'gemini',
    confidence_score FLOAT DEFAULT 0.5,
    raw_ai_response TEXT,
    analyzed_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    -- Unique constraint per coin per analysis
    UNIQUE(coin_id, analyzed_at)
);

-- Create indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_sentiment_analyzed_at 
    ON aihub_sentiment(analyzed_at);
CREATE INDEX IF NOT EXISTS idx_news_events_time 
    ON news_events(event_time, coin_id);
CREATE INDEX IF NOT EXISTS idx_news_events_category 
    ON news_events(category, coin_id);
CREATE INDEX IF NOT EXISTS idx_behavioral_sentiment_coin 
    ON behavioral_sentiment(coin_id, analyzed_at DESC);
CREATE INDEX IF NOT EXISTS idx_behavioral_sentiment_time 
    ON behavioral_sentiment(analyzed_at);

-- Log completion
DO $$
BEGIN
    RAISE NOTICE 'AI Behavioral Alpha migration complete';
END $$;
