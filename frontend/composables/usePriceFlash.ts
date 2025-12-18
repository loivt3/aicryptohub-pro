/**
 * usePriceFlash - Track price changes and apply flash animations
 * Usage: const { flashClass, updatePrice } = usePriceFlash()
 */
import { ref, computed, onUnmounted } from 'vue'

interface PriceState {
    price: number
    flashClass: string
    timeout: ReturnType<typeof setTimeout> | null
}

// Global state to track prices across components
const priceStates = new Map<string, PriceState>()

export function usePriceFlash(symbol: string) {
    const flashClass = ref('')

    const updatePrice = (newPrice: number) => {
        if (!symbol || !newPrice) return

        const key = symbol.toUpperCase()
        const state = priceStates.get(key)

        if (state && state.price !== newPrice) {
            // Clear previous timeout
            if (state.timeout) {
                clearTimeout(state.timeout)
            }

            // Determine flash direction - use price-flash classes for price-only effect
            if (newPrice > state.price) {
                flashClass.value = 'price-flash-up'
            } else if (newPrice < state.price) {
                flashClass.value = 'price-flash-down'
            }

            // Clear flash after animation
            const timeout = setTimeout(() => {
                flashClass.value = ''
            }, 800)

            priceStates.set(key, { price: newPrice, flashClass: flashClass.value, timeout })
        } else if (!state) {
            // First time seeing this symbol
            priceStates.set(key, { price: newPrice, flashClass: '', timeout: null })
        }
    }

    // Cleanup on unmount
    onUnmounted(() => {
        const state = priceStates.get(symbol?.toUpperCase())
        if (state?.timeout) {
            clearTimeout(state.timeout)
        }
    })

    return {
        flashClass: computed(() => flashClass.value),
        updatePrice,
    }
}

/**
 * usePriceFlashRow - For table rows, track multiple prices
 */
export function usePriceFlashRow() {
    const flashStates = ref<Map<string, string>>(new Map())
    const timeouts = new Map<string, ReturnType<typeof setTimeout>>()

    const updatePrice = (symbol: string, newPrice: number) => {
        if (!symbol || !newPrice) return ''

        const key = symbol.toUpperCase()
        const state = priceStates.get(key)

        if (state && state.price !== newPrice) {
            // Clear previous timeout
            if (timeouts.has(key)) {
                clearTimeout(timeouts.get(key)!)
            }

            // Determine flash direction - use price-flash classes for price-only effect
            const flashClass = newPrice > state.price ? 'price-flash-up' : 'price-flash-down'
            flashStates.value.set(key, flashClass)

            // Clear flash after animation
            const timeout = setTimeout(() => {
                flashStates.value.set(key, '')
            }, 800)

            timeouts.set(key, timeout)
            priceStates.set(key, { price: newPrice, flashClass, timeout: null })

            return flashClass
        } else if (!state) {
            priceStates.set(key, { price: newPrice, flashClass: '', timeout: null })
        }

        return flashStates.value.get(key) || ''
    }

    const getFlashClass = (symbol: string) => {
        return flashStates.value.get(symbol?.toUpperCase()) || ''
    }

    // Cleanup on unmount
    onUnmounted(() => {
        timeouts.forEach((timeout) => clearTimeout(timeout))
        timeouts.clear()
    })

    return {
        updatePrice,
        getFlashClass,
    }
}
