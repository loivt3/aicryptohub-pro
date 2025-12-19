-- AI Hub Pro - Complete Proxmox Schema
-- EXACT COPY from Supabase for full compatibility
-- Run as postgres superuser: su - postgres && psql -d aihub_pro

-- ============================================
-- STEP 1: Grant permissions (run first!)
-- ============================================
GRANT ALL ON SCHEMA public TO aihub_pro;
ALTER SCHEMA public OWNER TO aihub_pro;

-- ============================================
-- STEP 2: Create sequences
-- ============================================
CREATE SEQUENCE IF NOT EXISTS ai_sentiment_id_seq;
CREATE SEQUENCE IF NOT EXISTS aihub_coin_metadata_id_seq;
CREATE SEQUENCE IF NOT EXISTS aihub_coins_id_seq;
CREATE SEQUENCE IF NOT EXISTS aihub_ohlcv_id_seq;
CREATE SEQUENCE IF NOT EXISTS aihub_price_history_id_seq;
CREATE SEQUENCE IF NOT EXISTS aihub_sentiment_id_seq;
CREATE SEQUENCE IF NOT EXISTS analysis_jobs_id_seq;
CREATE SEQUENCE IF NOT EXISTS chains_id_seq;
CREATE SEQUENCE IF NOT EXISTS ohlcv_1h_id_seq;
CREATE SEQUENCE IF NOT EXISTS tokens_on_chain_id_seq;
CREATE SEQUENCE IF NOT EXISTS token_top_holders_id_seq;

-- ============================================
-- STEP 3: Create tables
-- ============================================

-- ai_sentiment
CREATE TABLE IF NOT EXISTS ai_sentiment (
    id integer NOT NULL DEFAULT nextval('ai_sentiment_id_seq'),
    coin_id character varying NOT NULL UNIQUE,
    asi_score integer DEFAULT 50,
    signal character varying DEFAULT 'NEUTRAL',
    reasoning text,
    indicators text,
    provider character varying DEFAULT 'technical',
    analyzed_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ai_sentiment_pkey PRIMARY KEY (id)
);

-- aihub_coin_metadata
CREATE TABLE IF NOT EXISTS aihub_coin_metadata (
    id integer NOT NULL DEFAULT nextval('aihub_coin_metadata_id_seq'),
    symbol character varying NOT NULL UNIQUE,
    name character varying,
    coingecko_id character varying,
    image_url character varying,
    category character varying,
    rank integer DEFAULT 0,
    tier smallint DEFAULT 3,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT aihub_coin_metadata_pkey PRIMARY KEY (id)
);

-- aihub_coins (MAIN TABLE)
CREATE TABLE IF NOT EXISTS aihub_coins (
    id integer NOT NULL DEFAULT nextval('aihub_coins_id_seq'),
    symbol character varying NOT NULL UNIQUE,
    name character varying,
    image_url character varying,
    price numeric NOT NULL DEFAULT 0,
    change_24h numeric DEFAULT 0,
    volume_24h numeric DEFAULT 0,
    market_cap numeric DEFAULT 0,
    rank integer DEFAULT 0,
    tier smallint DEFAULT 3,
    ai_signal character varying DEFAULT 'HOLD',
    sentiment_score numeric DEFAULT 0.5,
    sentiment_reason text,
    last_updated timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    coin_id character varying,
    high_24h numeric DEFAULT 0,
    low_24h numeric DEFAULT 0,
    price_change_1h numeric DEFAULT 0,
    price_change_7d numeric DEFAULT 0,
    price_change_30d numeric DEFAULT 0,
    circulating_supply numeric DEFAULT 0,
    total_supply numeric DEFAULT 0,
    max_supply numeric DEFAULT NULL,
    ath numeric DEFAULT 0,
    ath_date timestamp without time zone,
    atl numeric DEFAULT 0,
    atl_date timestamp without time zone,
    sparkline_7d jsonb,
    CONSTRAINT aihub_coins_pkey PRIMARY KEY (id)
);

-- aihub_ohlcv
CREATE TABLE IF NOT EXISTS aihub_ohlcv (
    id bigint NOT NULL DEFAULT nextval('aihub_ohlcv_id_seq'),
    symbol character varying NOT NULL,
    timeframe smallint NOT NULL,
    open_time timestamp without time zone NOT NULL,
    open numeric NOT NULL,
    high numeric NOT NULL,
    low numeric NOT NULL,
    close numeric NOT NULL,
    volume numeric DEFAULT 0,
    trades_count integer DEFAULT 0,
    CONSTRAINT aihub_ohlcv_pkey PRIMARY KEY (id)
);

-- aihub_price_history
CREATE TABLE IF NOT EXISTS aihub_price_history (
    id bigint NOT NULL DEFAULT nextval('aihub_price_history_id_seq'),
    symbol character varying NOT NULL,
    price numeric NOT NULL,
    volume_24h numeric DEFAULT 0,
    market_cap numeric DEFAULT 0,
    change_24h numeric DEFAULT 0,
    recorded_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT aihub_price_history_pkey PRIMARY KEY (id)
);

-- aihub_sentiment
CREATE TABLE IF NOT EXISTS aihub_sentiment (
    id integer NOT NULL DEFAULT nextval('aihub_sentiment_id_seq'),
    symbol character varying NOT NULL UNIQUE,
    ai_signal character varying DEFAULT 'HOLD',
    sentiment_score numeric DEFAULT 0.5,
    sentiment_reason text,
    provider character varying,
    analyzed_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT aihub_sentiment_pkey PRIMARY KEY (id)
);

-- analysis_jobs
CREATE TABLE IF NOT EXISTS analysis_jobs (
    id integer NOT NULL DEFAULT nextval('analysis_jobs_id_seq'),
    job_type character varying NOT NULL,
    status character varying DEFAULT 'pending',
    payload jsonb NOT NULL,
    result jsonb,
    error_message text,
    attempts integer DEFAULT 0,
    max_attempts integer DEFAULT 3,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    started_at timestamp without time zone,
    completed_at timestamp without time zone,
    CONSTRAINT analysis_jobs_pkey PRIMARY KEY (id)
);

-- chains
CREATE TABLE IF NOT EXISTS chains (
    id integer NOT NULL DEFAULT nextval('chains_id_seq'),
    slug character varying NOT NULL UNIQUE,
    name character varying NOT NULL,
    chain_id integer,
    api_url text NOT NULL,
    api_key_setting_name character varying,
    rpc_url text,
    is_evm boolean DEFAULT true,
    native_symbol character varying NOT NULL,
    explorer_name character varying,
    block_time_seconds integer DEFAULT 12,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chains_pkey PRIMARY KEY (id)
);

-- ohlcv_1h
CREATE TABLE IF NOT EXISTS ohlcv_1h (
    id integer NOT NULL DEFAULT nextval('ohlcv_1h_id_seq'),
    coin_id character varying NOT NULL,
    open numeric,
    high numeric,
    low numeric,
    close numeric,
    volume numeric,
    candle_time timestamp without time zone NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ohlcv_1h_pkey PRIMARY KEY (id)
);

-- ohlcv_4h
CREATE TABLE IF NOT EXISTS ohlcv_4h (
    id integer NOT NULL DEFAULT nextval('ohlcv_1h_id_seq'),
    coin_id character varying NOT NULL,
    open numeric,
    high numeric,
    low numeric,
    close numeric,
    volume numeric,
    candle_time timestamp without time zone NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ohlcv_4h_pkey PRIMARY KEY (id)
);

-- ohlcv_5m
CREATE TABLE IF NOT EXISTS ohlcv_5m (
    id integer NOT NULL DEFAULT nextval('ohlcv_1h_id_seq'),
    coin_id character varying NOT NULL,
    open numeric,
    high numeric,
    low numeric,
    close numeric,
    volume numeric,
    candle_time timestamp without time zone NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ohlcv_5m_pkey PRIMARY KEY (id)
);

-- tokens_on_chain (create first for FK)
CREATE TABLE IF NOT EXISTS tokens_on_chain (
    id integer NOT NULL DEFAULT nextval('tokens_on_chain_id_seq'),
    coin_id character varying NOT NULL,
    chain_id integer NOT NULL,
    contract_address character varying NOT NULL,
    token_name character varying,
    token_symbol character varying,
    decimals integer DEFAULT 18,
    total_supply numeric,
    circulating_supply numeric,
    holder_count integer DEFAULT 0,
    is_verified boolean DEFAULT false,
    token_type character varying DEFAULT 'ERC20',
    implementation_address character varying,
    last_fetched_at timestamp without time zone,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT tokens_on_chain_pkey PRIMARY KEY (id)
);

-- token_top_holders
CREATE TABLE IF NOT EXISTS token_top_holders (
    id integer NOT NULL DEFAULT nextval('token_top_holders_id_seq'),
    token_id integer NOT NULL,
    rank integer NOT NULL CHECK (rank > 0 AND rank <= 100),
    wallet_address character varying NOT NULL,
    balance numeric NOT NULL,
    balance_formatted numeric,
    percentage numeric,
    wallet_label character varying,
    is_contract boolean DEFAULT false,
    is_exchange boolean DEFAULT false,
    fetched_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT token_top_holders_pkey PRIMARY KEY (id)
);

-- ============================================
-- STEP 4: Add foreign keys
-- ============================================
ALTER TABLE tokens_on_chain 
    ADD CONSTRAINT tokens_on_chain_chain_id_fkey 
    FOREIGN KEY (chain_id) REFERENCES chains(id) ON DELETE CASCADE;

ALTER TABLE token_top_holders 
    ADD CONSTRAINT token_top_holders_token_id_fkey 
    FOREIGN KEY (token_id) REFERENCES tokens_on_chain(id) ON DELETE CASCADE;

-- ============================================
-- STEP 5: Create indexes
-- ============================================
CREATE INDEX IF NOT EXISTS idx_coins_symbol ON aihub_coins(symbol);
CREATE INDEX IF NOT EXISTS idx_coins_market_cap ON aihub_coins(market_cap DESC);
CREATE INDEX IF NOT EXISTS idx_coins_rank ON aihub_coins(rank);
CREATE INDEX IF NOT EXISTS idx_ohlcv_symbol ON aihub_ohlcv(symbol);
CREATE INDEX IF NOT EXISTS idx_ohlcv_symbol_time ON aihub_ohlcv(symbol, open_time);
CREATE INDEX IF NOT EXISTS idx_ohlcv_timeframe ON aihub_ohlcv(timeframe);
CREATE INDEX IF NOT EXISTS idx_ohlcv_symbol_tf_time ON aihub_ohlcv(symbol, timeframe, open_time);
CREATE INDEX IF NOT EXISTS idx_sentiment_symbol ON aihub_sentiment(symbol);
CREATE INDEX IF NOT EXISTS idx_price_history_symbol ON aihub_price_history(symbol);
CREATE INDEX IF NOT EXISTS idx_chains_slug ON chains(slug);

-- Unique constraint for OHLCV deduplication (prevents duplicate candles)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'uq_ohlcv_symbol_tf_time'
    ) THEN
        ALTER TABLE aihub_ohlcv ADD CONSTRAINT uq_ohlcv_symbol_tf_time 
            UNIQUE (symbol, timeframe, open_time);
    END IF;
END $$;

-- ============================================
-- STEP 6: Grant permissions to user
-- ============================================
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO aihub_pro;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO aihub_pro;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO aihub_pro;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO aihub_pro;
