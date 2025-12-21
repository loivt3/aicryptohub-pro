/**
 * useCache - localStorage Cache with TTL
 * 
 * Provides caching for initial data load to speed up page refresh
 */

interface CacheEntry<T> {
    data: T
    timestamp: number
    ttl: number
}

const CACHE_PREFIX = 'aihub_cache_'

export const useCache = () => {
    /**
     * Get cached data if valid (not expired)
     */
    const getCache = <T>(key: string): T | null => {
        if (typeof window === 'undefined') return null

        try {
            const raw = localStorage.getItem(CACHE_PREFIX + key)
            if (!raw) return null

            const entry: CacheEntry<T> = JSON.parse(raw)
            const now = Date.now()

            // Check if expired
            if (now - entry.timestamp > entry.ttl * 1000) {
                localStorage.removeItem(CACHE_PREFIX + key)
                return null
            }

            return entry.data
        } catch (e) {
            console.warn('Cache read error:', e)
            return null
        }
    }

    /**
     * Set cache with TTL (in seconds)
     */
    const setCache = <T>(key: string, data: T, ttlSeconds: number = 60): void => {
        if (typeof window === 'undefined') return

        try {
            const entry: CacheEntry<T> = {
                data,
                timestamp: Date.now(),
                ttl: ttlSeconds,
            }
            localStorage.setItem(CACHE_PREFIX + key, JSON.stringify(entry))
        } catch (e) {
            console.warn('Cache write error:', e)
        }
    }

    /**
     * Clear specific cache or all caches
     */
    const clearCache = (key?: string): void => {
        if (typeof window === 'undefined') return

        if (key) {
            localStorage.removeItem(CACHE_PREFIX + key)
        } else {
            // Clear all caches with our prefix
            Object.keys(localStorage)
                .filter(k => k.startsWith(CACHE_PREFIX))
                .forEach(k => localStorage.removeItem(k))
        }
    }

    /**
     * Check if cache exists and is valid
     */
    const hasValidCache = (key: string): boolean => {
        return getCache(key) !== null
    }

    /**
     * Get cache age in seconds (or null if no cache)
     */
    const getCacheAge = (key: string): number | null => {
        if (typeof window === 'undefined') return null

        try {
            const raw = localStorage.getItem(CACHE_PREFIX + key)
            if (!raw) return null

            const entry = JSON.parse(raw)
            return Math.floor((Date.now() - entry.timestamp) / 1000)
        } catch {
            return null
        }
    }

    return {
        getCache,
        setCache,
        clearCache,
        hasValidCache,
        getCacheAge,
    }
}

// Cache keys constants
export const CACHE_KEYS = {
    MARKET_DATA: 'market_data',
    GLOBAL_STATS: 'global_stats',
    SENTIMENT: 'sentiment',
    MULTI_HORIZON: 'multi_horizon',
}

// Default TTLs (in seconds)
export const CACHE_TTL = {
    MARKET_DATA: 60,      // 1 minute
    GLOBAL_STATS: 60,     // 1 minute  
    SENTIMENT: 120,       // 2 minutes
    MULTI_HORIZON: 300,   // 5 minutes
}
