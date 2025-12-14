/**
 * TypeScript Type Definitions
 * Shared types for the frontend application
 */

// =============================================
// Market Types
// =============================================

export interface Coin {
    coin_id: string
    symbol: string
    name: string
    image?: string
    price: number
    change_1h?: number
    change_24h: number
    change_7d?: number
    market_cap: number
    market_cap_rank?: number
    volume_24h: number
    high_24h?: number
    low_24h?: number
}

export interface CoinWithSentiment extends Coin {
    asi_score?: number
    signal?: string
    reason?: string
}

export interface OHLCVCandle {
    timestamp: number
    open: number
    high: number
    low: number
    close: number
    volume: number
}

export interface MarketDataResponse {
    success: boolean
    data: Coin[]
    meta: {
        count: number
        timestamp: string
        source: string
    }
}

// =============================================
// Sentiment Types
// =============================================

export interface SentimentData {
    coin_id: string
    symbol?: string
    name?: string
    asi_score: number
    signal: 'STRONG_BUY' | 'BUY' | 'NEUTRAL' | 'SELL' | 'STRONG_SELL'
    reason?: string
    confidence?: number
    provider?: string
    analyzed_at?: string
}

export interface TechnicalIndicators {
    rsi_14?: number
    macd_line?: number
    macd_signal?: number
    macd_histogram?: number
    bb_upper?: number
    bb_middle?: number
    bb_lower?: number
    bb_percent_b?: number
    stoch_k?: number
    stoch_d?: number
    adx?: number
    ema_9?: number
    ema_21?: number
    ema_50?: number
    current_price?: number
    price_change_24h?: number
}

// =============================================
// Portfolio Types
// =============================================

export interface PortfolioHolding {
    coin_id: string
    symbol?: string
    name?: string
    image?: string
    amount: number
    buy_price: number
    current_price?: number
    value?: number
    pnl?: number
    pnl_percent?: number
    created_at?: string
    updated_at?: string
}

export interface PortfolioSummary {
    total_value: number
    total_invested: number
    total_pnl: number
    total_pnl_percent: number
    holdings_count: number
}

export interface AddHoldingRequest {
    coin_id: string
    amount: number
    buy_price: number
}

// =============================================
// Auth Types
// =============================================

export interface User {
    id: string
    email: string
    name?: string
    is_admin?: boolean
}

export interface LoginRequest {
    email: string
    password: string
}

export interface RegisterRequest {
    email: string
    password: string
    name?: string
}

export interface TokenResponse {
    access_token: string
    token_type: string
    expires_in: number
    user: User
}

// =============================================
// On-Chain Types
// =============================================

export interface WhaleActivity {
    signal: string
    tx_count_24h: number
    change_24h_pct: number
    net_flow_usd: number
}

export interface NetworkHealth {
    signal: string
    dau_current: number
    dau_change_1d_pct: number
    trend: string
}

export interface OnChainSignals {
    coin_id: string
    overall_signal: string
    bullish_probability: number
    whale_activity: WhaleActivity
    network_health: NetworkHealth
    ai_prediction?: string
    ai_summary?: string
    updated_at?: string
}

// =============================================
// API Response Types
// =============================================

export interface ApiResponse<T> {
    success: boolean
    data?: T
    error?: string
    message?: string
}

export interface PaginatedResponse<T> {
    success: boolean
    data: T[]
    meta: {
        total: number
        page: number
        per_page: number
        pages: number
    }
}
