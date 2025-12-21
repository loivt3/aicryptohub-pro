/**
 * Market Store - Pinia
 * Quản lý state cho market data
 */

import { defineStore } from 'pinia'

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
    market_cap_rank: number
    volume_24h: number
    sentiment_score?: number
    ai_signal?: string
}

export interface PriceUpdate {
    s: string      // Symbol (e.g., 'BTC')
    p: number      // Price
    c: number      // Change % 24h
}

interface MarketState {
    coins: Coin[]
    loading: boolean
    error: string | null
    lastUpdated: Date | null
    socketConnected: boolean
    socketMessageCount: number
}

export const useMarketStore = defineStore('market', {
    state: (): MarketState => ({
        coins: [],
        loading: false,
        error: null,
        lastUpdated: null,
        socketConnected: false,
        socketMessageCount: 0,
    }),

    getters: {
        topGainers: (state) => {
            return [...state.coins]
                .sort((a, b) => b.change_24h - a.change_24h)
                .slice(0, 10)
        },

        topLosers: (state) => {
            return [...state.coins]
                .sort((a, b) => a.change_24h - b.change_24h)
                .slice(0, 10)
        },

        topByMarketCap: (state) => {
            return [...state.coins]
                .sort((a, b) => b.market_cap - a.market_cap)
                .slice(0, 100)
        },

        getCoinById: (state) => (id: string) => {
            return state.coins.find(c => c.coin_id === id)
        },

        getCoinBySymbol: (state) => (symbol: string) => {
            return state.coins.find(c => c.symbol.toUpperCase() === symbol.toUpperCase())
        },
    },

    actions: {
        async fetchMarketData(limit = 100, skipCache = false) {
            const { getCache, setCache } = useCache()
            const CACHE_KEY = 'market_data'
            const CACHE_TTL = 60 // 1 minute

            // 1. Try to load from cache first (instant display)
            if (!skipCache) {
                const cached = getCache<Coin[]>(CACHE_KEY)
                if (cached && cached.length > 0) {
                    this.coins = cached
                    this.lastUpdated = new Date()
                    console.log('[Cache] Loaded market data from cache:', cached.length, 'coins')

                    // Background refresh after showing cached data
                    setTimeout(() => this.fetchMarketData(limit, true), 1000)
                    return
                }
            }

            // 2. Fetch from API
            this.loading = true
            this.error = null

            try {
                const config = useRuntimeConfig()
                const response = await $fetch<{ success: boolean; data: Coin[] }>(
                    `${config.public.apiBase}/market`,
                    { query: { limit } }
                )

                if (response.success && response.data) {
                    this.coins = response.data
                    this.lastUpdated = new Date()

                    // Save to cache for next load
                    setCache(CACHE_KEY, response.data, CACHE_TTL)
                    console.log('[Cache] Saved market data to cache')
                }
            } catch (err: any) {
                this.error = err.message || 'Failed to fetch market data'
                console.error('Market fetch error:', err)
            } finally {
                this.loading = false
            }
        },


        async fetchRealtimeData() {
            try {
                const config = useRuntimeConfig()
                const response = await $fetch<{ success: boolean; data: Coin[] }>(
                    `${config.public.apiBase}/market/realtime`
                )

                if (response.success && response.data.length) {
                    // Update existing coins with realtime prices
                    response.data.forEach(update => {
                        const index = this.coins.findIndex(c => c.coin_id === update.coin_id)
                        if (index !== -1) {
                            this.coins[index] = { ...this.coins[index], ...update }
                        }
                    })
                    this.lastUpdated = new Date()
                }
            } catch (err) {
                console.error('Realtime fetch error:', err)
            }
        },

        /**
         * Update prices from WebSocket
         * Called by useSocket composable when receiving ticker_update events
         */
        updatePricesFromSocket(updates: PriceUpdate[]) {
            if (!updates || !updates.length) return

            let updatedCount = 0

            updates.forEach(update => {
                // Find coin by symbol (Binance uses symbol like 'BTC', 'ETH')
                const index = this.coins.findIndex(
                    c => c.symbol.toUpperCase() === update.s.toUpperCase()
                )

                if (index !== -1) {
                    // Update price and change
                    this.coins[index] = {
                        ...this.coins[index],
                        price: update.p,
                        change_24h: update.c,
                    }
                    updatedCount++
                }
            })

            if (updatedCount > 0) {
                this.socketMessageCount++
                this.lastUpdated = new Date()
            }
        },

        /**
         * Set socket connection status
         */
        setSocketConnected(connected: boolean) {
            this.socketConnected = connected
        },
    },
})

