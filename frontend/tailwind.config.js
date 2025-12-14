/** @type {import('tailwindcss').Config} */
export default {
    content: [
        './components/**/*.{js,vue,ts}',
        './layouts/**/*.vue',
        './pages/**/*.vue',
        './plugins/**/*.{js,ts}',
        './app.vue',
        './error.vue',
    ],
    darkMode: 'class',
    theme: {
        extend: {
            colors: {
                // Brand colors from AI Hub Pro
                primary: {
                    DEFAULT: '#38efeb',
                    50: '#ecfffe',
                    100: '#cffffe',
                    200: '#a5fffe',
                    300: '#67fffc',
                    400: '#38efeb',
                    500: '#0ed3d0',
                    600: '#08a9aa',
                    700: '#0d8688',
                    800: '#126a6c',
                    900: '#145859',
                },
                accent: {
                    purple: '#9f7aea',
                    pink: '#ed64a6',
                    cyan: '#38efeb',
                },
                dark: {
                    DEFAULT: '#0a0f1a',
                    50: '#f6f7f9',
                    100: '#eceef2',
                    200: '#d4d9e3',
                    300: '#afb8ca',
                    400: '#8593ab',
                    500: '#667691',
                    600: '#515f78',
                    700: '#434d62',
                    800: '#141c2b',
                    900: '#0f1625',
                    950: '#0a0f1a',
                },
            },
            fontFamily: {
                sans: ['Inter', 'system-ui', 'sans-serif'],
                mono: ['SF Mono', 'Monaco', 'monospace'],
            },
            animation: {
                'fade-in': 'fadeIn 0.3s ease-out',
                'slide-up': 'slideUp 0.3s ease-out',
                'pulse-glow': 'pulseGlow 2s ease-in-out infinite',
            },
            keyframes: {
                fadeIn: {
                    '0%': { opacity: '0' },
                    '100%': { opacity: '1' },
                },
                slideUp: {
                    '0%': { opacity: '0', transform: 'translateY(10px)' },
                    '100%': { opacity: '1', transform: 'translateY(0)' },
                },
                pulseGlow: {
                    '0%, 100%': { boxShadow: '0 0 5px rgba(56, 239, 235, 0.5)' },
                    '50%': { boxShadow: '0 0 20px rgba(56, 239, 235, 0.8)' },
                },
            },
            boxShadow: {
                'glow': '0 0 15px rgba(56, 239, 235, 0.3)',
                'glow-lg': '0 0 30px rgba(56, 239, 235, 0.4)',
            },
        },
    },
    plugins: [],
}
