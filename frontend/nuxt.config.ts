// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
    devtools: { enabled: true },

    // Enable SSR for SEO
    ssr: true,

    // Runtime config
    runtimeConfig: {
        // Private keys (server-side only)
        apiSecret: '',

        // Public keys (exposed to client)
        public: {
            apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://127.0.0.1:8000/api/v1',
            wsUrl: process.env.NUXT_PUBLIC_WS_URL || 'http://127.0.0.1:8000',
            appName: 'AI Crypto Hub',
        }
    },

    // Modules
    modules: [
        '@pinia/nuxt',
        '@nuxtjs/tailwindcss',
        '@vueuse/nuxt',
        'nuxt-icon',
    ],

    // App config
    app: {
        head: {
            title: 'AI Crypto Hub - AI-Powered Cryptocurrency Analysis',
            htmlAttrs: {
                lang: 'en'
            },
            meta: [
                { charset: 'utf-8' },
                { name: 'viewport', content: 'width=device-width, initial-scale=1' },
                {
                    name: 'description',
                    content: 'Real-time cryptocurrency market data with AI-powered sentiment analysis, technical indicators, and on-chain signals.'
                },
                { name: 'theme-color', content: '#0a0f1a' },
                // Open Graph
                { property: 'og:type', content: 'website' },
                { property: 'og:site_name', content: 'AI Crypto Hub' },
                { property: 'og:title', content: 'AI Crypto Hub - AI-Powered Cryptocurrency Analysis' },
                { property: 'og:description', content: 'Real-time cryptocurrency market data with AI-powered sentiment analysis.' },
                // Twitter Card
                { name: 'twitter:card', content: 'summary_large_image' },
            ],
            link: [
                { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' },
                { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
                { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap' },
            ]
        }
    },

    // CSS
    css: [
        '~/assets/css/main.css',
        '~/assets/css/shared.css',
    ],

    // Tailwind config
    tailwindcss: {
        cssPath: '~/assets/css/tailwind.css',
        configPath: 'tailwind.config.js',
    },

    // TypeScript
    typescript: {
        strict: true,
    },

    // Nitro server config
    nitro: {
        preset: 'node-server',
    },
})
