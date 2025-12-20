/**
 * useSocket - Socket.IO Client Composable
 * Manages real-time WebSocket connection to backend
 * 
 * Features:
 * - Auto-connect/reconnect
 * - Price update subscription
 * - Connection status tracking
 * - Integration with market store
 */

import { ref, onMounted, onUnmounted, computed } from 'vue'
import { io, Socket } from 'socket.io-client'

// Connection state
const socket = ref<Socket | null>(null)
const connected = ref(false)
const connecting = ref(false)
const lastUpdate = ref<Date | null>(null)
const messageCount = ref(0)
const error = ref<string | null>(null)

// Price update callbacks
const priceCallbacks: Set<(data: PriceUpdate[]) => void> = new Set()

// Intent alert callbacks (Shadow Radar)
const intentAlertCallbacks: Set<(data: IntentAlert) => void> = new Set()

export interface PriceUpdate {
    s: string      // Symbol (e.g., 'BTC')
    p: number      // Price
    c: number      // Change % 24h
    h?: number     // High 24h
    l?: number     // Low 24h
    v?: number     // Volume 24h
}

export interface TickerPayload {
    t: number      // Timestamp
    d: PriceUpdate[]  // Data array
    c: number      // Count
}

export interface IntentAlert {
    coin_id: string
    symbol?: string
    divergence_type: string
    intent_score: number
    shadow_insight?: string
    is_golden_shadow?: boolean
}

export function useSocket() {
    const config = useRuntimeConfig()

    /**
     * Connect to Socket.IO server
     */
    const connect = () => {
        if (socket.value?.connected || connecting.value) {
            return
        }

        connecting.value = true
        error.value = null

        // Determine WebSocket URL based on environment
        let wsUrl = config.public.wsUrl

        // If wsUrl not set, derive from apiBase or window.location
        if (!wsUrl) {
            const apiBase = config.public.apiBase || ''

            // If apiBase is relative (starts with /), use current origin
            if (apiBase.startsWith('/') || !apiBase) {
                // Browser environment - use current page origin
                if (typeof window !== 'undefined') {
                    wsUrl = window.location.origin
                } else {
                    // SSR - use placeholder, will reconnect on client
                    wsUrl = ''
                }
            } else {
                // apiBase is absolute URL, extract base
                wsUrl = apiBase.replace('/api/v1', '')
            }
        }

        // Skip connection if no valid URL (SSR)
        if (!wsUrl) {
            connecting.value = false
            return
        }

        try {
            socket.value = io(wsUrl, {
                path: '/socket.io',
                transports: ['polling', 'websocket'],  // Try polling first (Cloudflare-friendly)
                reconnection: true,
                reconnectionAttempts: 10,
                reconnectionDelay: 1000,
                reconnectionDelayMax: 5000,
                timeout: 20000,  // Longer timeout for polling
            })

            // Connection events
            socket.value.on('connect', () => {
                connected.value = true
                connecting.value = false
                error.value = null
                console.log('[Socket.IO] Connected:', socket.value?.id)
            })

            socket.value.on('connected', (data: any) => {
                console.log('[Socket.IO] Server confirmed:', data)
            })

            socket.value.on('disconnect', (reason) => {
                connected.value = false
                console.log('[Socket.IO] Disconnected:', reason)
            })

            socket.value.on('connect_error', (err) => {
                connecting.value = false
                error.value = err.message
                console.error('[Socket.IO] Connection error:', err.message)
            })

            // Price update events
            socket.value.on('ticker_update', (payload: TickerPayload) => {
                messageCount.value++
                lastUpdate.value = new Date()

                // Notify all subscribers
                if (payload.d && Array.isArray(payload.d)) {
                    priceCallbacks.forEach(callback => {
                        try {
                            callback(payload.d)
                        } catch (e) {
                            console.error('[Socket.IO] Callback error:', e)
                        }
                    })
                }
            })

            // Single price update event
            socket.value.on('price_update', (data: PriceUpdate) => {
                priceCallbacks.forEach(callback => {
                    try {
                        callback([data])
                    } catch (e) {
                        console.error('[Socket.IO] Callback error:', e)
                    }
                })
            })

            // Intent divergence alerts (Shadow Radar)
            socket.value.on('intent_alert', (data: any) => {
                console.log('[Socket.IO] Intent alert received:', data)
                intentAlertCallbacks.forEach(callback => {
                    try {
                        callback(data)
                    } catch (e) {
                        console.error('[Socket.IO] Intent alert callback error:', e)
                    }
                })
            })

        } catch (e: any) {
            connecting.value = false
            error.value = e.message
            console.error('[Socket.IO] Init error:', e)
        }
    }

    /**
     * Disconnect from Socket.IO server
     */
    const disconnect = () => {
        if (socket.value) {
            socket.value.disconnect()
            socket.value = null
            connected.value = false
            connecting.value = false
        }
    }

    /**
     * Subscribe to specific symbols
     */
    const subscribeSymbols = (symbols: string[]) => {
        if (socket.value?.connected) {
            socket.value.emit('subscribe', symbols)
        }
    }

    /**
     * Unsubscribe from symbols
     */
    const unsubscribeSymbols = (symbols: string[]) => {
        if (socket.value?.connected) {
            socket.value.emit('unsubscribe', symbols)
        }
    }

    /**
     * Register callback for price updates
     */
    const onPriceUpdate = (callback: (data: PriceUpdate[]) => void) => {
        priceCallbacks.add(callback)
        return () => priceCallbacks.delete(callback)
    }

    /**
     * Get connection status
     */
    const status = computed(() => ({
        connected: connected.value,
        connecting: connecting.value,
        messageCount: messageCount.value,
        lastUpdate: lastUpdate.value,
        error: error.value,
    }))

    /**
     * Register callback for intent divergence alerts (Shadow Radar)
     */
    const onIntentAlert = (callback: (data: IntentAlert) => void) => {
        intentAlertCallbacks.add(callback)
        return () => intentAlertCallbacks.delete(callback)
    }

    return {
        // State
        connected: computed(() => connected.value),
        connecting: computed(() => connecting.value),
        error: computed(() => error.value),
        messageCount: computed(() => messageCount.value),
        lastUpdate: computed(() => lastUpdate.value),
        status,

        // Actions
        connect,
        disconnect,
        subscribeSymbols,
        unsubscribeSymbols,
        onPriceUpdate,
        onIntentAlert,
    }
}

/**
 * Auto-connect composable for components
 * Automatically connects on mount and disconnects on unmount
 */
export function useSocketAutoConnect() {
    const socketUtils = useSocket()

    onMounted(() => {
        socketUtils.connect()
    })

    onUnmounted(() => {
        // Don't disconnect - keep connection alive for other components
        // socketUtils.disconnect()
    })

    return socketUtils
}
