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

interface MarketState {
    coins: Coin[]
    loading: boolean
    error: string | null
    lastUpdated: Date | null
}

export const useMarketStore = defineStore('market', {
    state: (): MarketState => ({
        coins: [],
        loading: false,
        error: null,
        lastUpdated: null,
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
    },

    actions: {
        async fetchMarketData(limit = 100) {
            this.loading = true
            this.error = null

            try {
                const config = useRuntimeConfig()
                const response = await $fetch<{ success: boolean; data: Coin[] }>(
                    `${config.public.apiBase}/market`,
                    { query: { limit } }
                )

                if (response.success) {
                    this.coins = response.data
                    this.lastUpdated = new Date()
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
    },
})
