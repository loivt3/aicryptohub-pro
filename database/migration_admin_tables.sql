-- Admin Console Database Migration
-- Tables for users, news, audit logs, and settings

-- ============================================
-- Admin Users Table
-- ============================================
CREATE TABLE IF NOT EXISTS admin_users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user', -- user, premium, admin
    is_active BOOLEAN DEFAULT TRUE,
    avatar_url TEXT,
    last_login TIMESTAMPTZ,
    login_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_admin_users_email ON admin_users(email);
CREATE INDEX IF NOT EXISTS idx_admin_users_role ON admin_users(role);
CREATE INDEX IF NOT EXISTS idx_admin_users_active ON admin_users(is_active);

-- Insert default admin user (password: admin123 - CHANGE THIS!)
INSERT INTO admin_users (email, password_hash, name, role)
VALUES ('admin@aicryptohub.io', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X.cZ7i2wPxRE0Kxmu', 'Super Admin', 'admin')
ON CONFLICT (email) DO NOTHING;


-- ============================================
-- News Articles Table
-- ============================================
CREATE TABLE IF NOT EXISTS admin_news (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    slug VARCHAR(500),
    excerpt TEXT,
    content TEXT,
    source VARCHAR(255),
    source_url TEXT,
    image_url TEXT,
    author VARCHAR(255),
    status VARCHAR(50) DEFAULT 'pending', -- pending, approved, rejected
    coin_ids TEXT[], -- Array of related coin IDs
    tags TEXT[],
    view_count INTEGER DEFAULT 0,
    published_at TIMESTAMPTZ,
    reviewed_by VARCHAR(255),
    reviewed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_admin_news_status ON admin_news(status);
CREATE INDEX IF NOT EXISTS idx_admin_news_created ON admin_news(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_admin_news_published ON admin_news(published_at DESC);


-- ============================================
-- API Request Logs Table
-- ============================================
CREATE TABLE IF NOT EXISTS admin_api_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    method VARCHAR(10) NOT NULL,
    endpoint VARCHAR(500) NOT NULL,
    status_code INTEGER,
    ip_address VARCHAR(45),
    user_agent TEXT,
    user_id INTEGER,
    duration_ms INTEGER,
    request_body JSONB,
    response_size INTEGER,
    error_message TEXT
);

-- Indexes (with automatic cleanup for old logs)
CREATE INDEX IF NOT EXISTS idx_api_logs_timestamp ON admin_api_logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_api_logs_endpoint ON admin_api_logs(endpoint);
CREATE INDEX IF NOT EXISTS idx_api_logs_status ON admin_api_logs(status_code);
CREATE INDEX IF NOT EXISTS idx_api_logs_ip ON admin_api_logs(ip_address);


-- ============================================
-- Login History Table
-- ============================================
CREATE TABLE IF NOT EXISTS admin_login_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES admin_users(id) ON DELETE CASCADE,
    user_email VARCHAR(255),
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    ip_address VARCHAR(45),
    location VARCHAR(255),
    user_agent TEXT,
    success BOOLEAN NOT NULL,
    failure_reason VARCHAR(255)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_login_history_user ON admin_login_history(user_id);
CREATE INDEX IF NOT EXISTS idx_login_history_time ON admin_login_history(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_login_history_ip ON admin_login_history(ip_address);


-- ============================================
-- Admin Actions Audit Table
-- ============================================
CREATE TABLE IF NOT EXISTS admin_audit_log (
    id SERIAL PRIMARY KEY,
    admin_id INTEGER REFERENCES admin_users(id) ON DELETE SET NULL,
    admin_email VARCHAR(255),
    action VARCHAR(100) NOT NULL,
    target_type VARCHAR(100), -- user, coin, news, settings, etc.
    target_id VARCHAR(255),
    details JSONB,
    ip_address VARCHAR(45),
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_audit_admin ON admin_audit_log(admin_id);
CREATE INDEX IF NOT EXISTS idx_audit_action ON admin_audit_log(action);
CREATE INDEX IF NOT EXISTS idx_audit_time ON admin_audit_log(timestamp DESC);


-- ============================================
-- IP Blacklist Table
-- ============================================
CREATE TABLE IF NOT EXISTS admin_ip_blacklist (
    id SERIAL PRIMARY KEY,
    ip_address VARCHAR(45) NOT NULL,
    reason TEXT,
    added_by VARCHAR(255),
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_blacklist_ip ON admin_ip_blacklist(ip_address);
CREATE INDEX IF NOT EXISTS idx_blacklist_expires ON admin_ip_blacklist(expires_at);


-- ============================================
-- Market Corrections History Table
-- ============================================
CREATE TABLE IF NOT EXISTS admin_market_corrections (
    id SERIAL PRIMARY KEY,
    coin_id VARCHAR(100) NOT NULL,
    old_price DECIMAL(24, 10),
    new_price DECIMAL(24, 10) NOT NULL,
    reason TEXT,
    applied_by VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_corrections_coin ON admin_market_corrections(coin_id);
CREATE INDEX IF NOT EXISTS idx_corrections_time ON admin_market_corrections(created_at DESC);


-- ============================================
-- Service Status Table (for process manager)
-- ============================================
CREATE TABLE IF NOT EXISTS admin_service_status (
    id SERIAL PRIMARY KEY,
    service_id VARCHAR(100) UNIQUE NOT NULL,
    service_name VARCHAR(255) NOT NULL,
    service_type VARCHAR(50), -- scraper, ai, onchain
    status VARCHAR(50) DEFAULT 'stopped', -- running, stopped, error
    pid INTEGER,
    uptime_seconds INTEGER DEFAULT 0,
    last_log TEXT,
    last_error TEXT,
    started_at TIMESTAMPTZ,
    stopped_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert default services
INSERT INTO admin_service_status (service_id, service_name, service_type, status)
VALUES 
    ('binance', 'Binance Streamer', 'scraper', 'stopped'),
    ('coingecko', 'CoinGecko Fetcher', 'scraper', 'stopped'),
    ('cmc', 'CoinMarketCap', 'scraper', 'stopped'),
    ('gemini', 'Gemini AI', 'ai', 'stopped'),
    ('deepseek', 'DeepSeek AI', 'ai', 'stopped'),
    ('sentiment', 'Sentiment Analyzer', 'ai', 'stopped'),
    ('ethereum', 'Ethereum Collector', 'onchain', 'stopped'),
    ('bsc', 'BSC Collector', 'onchain', 'stopped'),
    ('solana', 'Solana Collector', 'onchain', 'stopped')
ON CONFLICT (service_id) DO NOTHING;


-- ============================================
-- Cleanup function for old logs
-- ============================================
CREATE OR REPLACE FUNCTION cleanup_old_logs()
RETURNS void AS $$
BEGIN
    -- Delete API logs older than 30 days
    DELETE FROM admin_api_logs WHERE timestamp < NOW() - INTERVAL '30 days';
    
    -- Delete login history older than 90 days
    DELETE FROM admin_login_history WHERE timestamp < NOW() - INTERVAL '90 days';
END;
$$ LANGUAGE plpgsql;
