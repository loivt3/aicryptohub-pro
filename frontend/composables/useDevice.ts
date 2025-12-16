/**
 * Device Detection Composable
 * Detects mobile/desktop and provides reactive state
 * Fixed for Cloudflare Tunnel SSR compatibility
 */

export const useDevice = () => {
    const MOBILE_BREAKPOINT = 768
    const TABLET_BREAKPOINT = 1024

    // SSR: Check user-agent for initial render
    let isMobileSSR = false
    if (import.meta.server) {
        const headers = useRequestHeaders(['user-agent'])
        const userAgent = headers?.['user-agent'] || ''
        isMobileSSR = /android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini|mobile/i.test(userAgent.toLowerCase())
    }

    // Start with SSR value
    const isMobile = ref(isMobileSSR)
    const isTablet = ref(false)
    const screenWidth = ref(isMobileSSR ? 375 : 1920)

    const updateDevice = () => {
        if (typeof window !== 'undefined') {
            screenWidth.value = window.innerWidth
            isMobile.value = window.innerWidth < MOBILE_BREAKPOINT
            isTablet.value = window.innerWidth >= MOBILE_BREAKPOINT && window.innerWidth < TABLET_BREAKPOINT
        }
    }

    const isDesktop = computed(() => !isMobile.value && !isTablet.value)

    // Update immediately on client
    if (import.meta.client) {
        // Run synchronously before mount for immediate detection
        if (typeof window !== 'undefined') {
            screenWidth.value = window.innerWidth
            isMobile.value = window.innerWidth < MOBILE_BREAKPOINT
            isTablet.value = window.innerWidth >= MOBILE_BREAKPOINT && window.innerWidth < TABLET_BREAKPOINT
        }
    }

    onMounted(() => {
        updateDevice()
        window.addEventListener('resize', updateDevice)
    })

    onUnmounted(() => {
        if (typeof window !== 'undefined') {
            window.removeEventListener('resize', updateDevice)
        }
    })

    return {
        isMobile,
        isTablet,
        isDesktop,
        screenWidth,
    }
}

