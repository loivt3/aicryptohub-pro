/**
 * Device Detection Composable
 * Detects mobile/desktop and provides reactive state
 */

export const useDevice = () => {
    const isMobile = ref(false)
    const isTablet = ref(false)
    const screenWidth = ref(0)

    const MOBILE_BREAKPOINT = 768
    const TABLET_BREAKPOINT = 1024

    const updateDevice = () => {
        if (import.meta.client) {
            screenWidth.value = window.innerWidth
            isMobile.value = window.innerWidth < MOBILE_BREAKPOINT
            isTablet.value = window.innerWidth >= MOBILE_BREAKPOINT && window.innerWidth < TABLET_BREAKPOINT
        }
    }

    const isDesktop = computed(() => !isMobile.value && !isTablet.value)

    onMounted(() => {
        updateDevice()
        window.addEventListener('resize', updateDevice)
    })

    onUnmounted(() => {
        if (import.meta.client) {
            window.removeEventListener('resize', updateDevice)
        }
    })

    // SSR: Check user agent for initial render
    const userAgent = useRequestHeaders(['user-agent'])?.['user-agent'] || ''
    const isMobileSSR = /android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(userAgent.toLowerCase())

    return {
        isMobile: import.meta.server ? ref(isMobileSSR) : isMobile,
        isTablet,
        isDesktop,
        screenWidth,
    }
}
