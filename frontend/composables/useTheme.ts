const THEME_KEY = 'aihub-theme'

// Shared state across components
const isDark = ref(true)

export function useTheme() {
    // Initialize from localStorage on first call
    if (typeof window !== 'undefined') {
        const stored = localStorage.getItem(THEME_KEY)
        if (stored) {
            isDark.value = stored === 'dark'
        } else {
            // Default to dark, or check system preference
            isDark.value = window.matchMedia('(prefers-color-scheme: dark)').matches
        }
        applyTheme()
    }

    function toggleTheme() {
        isDark.value = !isDark.value
        applyTheme()
        if (typeof window !== 'undefined') {
            localStorage.setItem(THEME_KEY, isDark.value ? 'dark' : 'light')
        }
    }

    function setTheme(dark: boolean) {
        isDark.value = dark
        applyTheme()
        if (typeof window !== 'undefined') {
            localStorage.setItem(THEME_KEY, dark ? 'dark' : 'light')
        }
    }

    function applyTheme() {
        if (typeof document !== 'undefined') {
            document.documentElement.classList.toggle('theme-dark', isDark.value)
            document.documentElement.classList.toggle('theme-light', !isDark.value)
        }
    }

    // Watch for changes
    watch(isDark, applyTheme)

    return {
        isDark,
        toggleTheme,
        setTheme,
    }
}
