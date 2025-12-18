/**
 * API Composable
 * Centralized API client using $fetch
 */

export const useApi = () => {
    const config = useRuntimeConfig()
    const authStore = useAuthStore()

    const baseURL = config.public.apiBase

    const apiFetch = async <T>(
        endpoint: string,
        options: {
            method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
            body?: any
            query?: Record<string, any>
            auth?: boolean
        } = {}
    ): Promise<T> => {
        const headers: Record<string, string> = {}

        // Add auth header if needed
        if (options.auth && authStore.token) {
            headers['Authorization'] = `Bearer ${authStore.token}`
        }

        return $fetch<T>(`${baseURL}${endpoint}`, {
            method: options.method || 'GET',
            body: options.body,
            query: options.query,
            headers,
        })
    }

    return {
        // Market endpoints
        getMarketData: (limit = 100) =>
            apiFetch<{ success: boolean; data: any[] }>('/market', { query: { limit } }),

        getMarketRealtime: () =>
            apiFetch<{ success: boolean; data: any[] }>('/market/realtime'),

        getCoin: (coinId: string) =>
            apiFetch<{ success: boolean; data: any }>(`/market/${coinId}`),

        getOHLCV: (symbol: string, interval = '1h', limit = 200) =>
            apiFetch<{ success: boolean; data: any[] }>(`/market/ohlcv/${symbol}`, {
                query: { interval, limit }
            }),

        // Global market stats
        getGlobalStats: () =>
            apiFetch<{
                success: boolean;
                data: {
                    total_market_cap: number;
                    total_volume_24h: number;
                    btc_dominance: number;
                    eth_dominance: number;
                    market_cap_change_24h: number;
                    fear_greed_index: number;
                    fear_greed_classification: string;
                }
            }>('/market/stats/global'),

        // Sentiment endpoints
        getSentiment: (limit = 100) =>
            apiFetch<{ success: boolean; data: any[] }>('/sentiment', { query: { limit } }),

        getCoinSentiment: (coinId: string) =>
            apiFetch<any>(`/sentiment/${coinId}`),

        // Portfolio endpoints (auth required)
        getPortfolio: () =>
            apiFetch<any[]>('/portfolio', { auth: true }),

        getPortfolioSummary: () =>
            apiFetch<any>('/portfolio/summary', { auth: true }),

        addHolding: (coinId: string, amount: number, buyPrice: number) =>
            apiFetch<any>('/portfolio', {
                method: 'POST',
                body: { coin_id: coinId, amount, buy_price: buyPrice },
                auth: true,
            }),

        deleteHolding: (coinId: string) =>
            apiFetch<void>(`/portfolio/${coinId}`, { method: 'DELETE', auth: true }),

        // On-chain endpoints
        getOnchainSummary: () =>
            apiFetch<any>('/onchain/summary'),

        getOnchainSignals: (coinId: string) =>
            apiFetch<any>(`/onchain/signals/${coinId}`),
    }
}
