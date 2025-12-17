import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
    plugins: [vue()],
    base: '/admin/',
    resolve: {
        alias: {
            '@': resolve(__dirname, 'src'),
        },
    },
    server: {
        port: 3001,
        host: true,
        allowedHosts: ['app.aicryptohub.io', 'localhost'],
        hmr: {
            // Disable HMR in production-like environment to avoid websocket errors
            host: 'app.aicryptohub.io',
            protocol: 'wss',
            clientPort: 443,
        },
        proxy: {
            '/api': {
                target: 'http://backend:8000',
                changeOrigin: true,
            },
            '/admin-api': {
                target: 'http://backend:8000',
                changeOrigin: true,
                rewrite: (path) => path.replace(/^\/admin-api/, '/api/v1/admin'),
            },
            '/ws': {
                target: 'ws://backend:8000',
                ws: true,
            },
        },
    },
    build: {
        outDir: 'dist',
        assetsDir: 'assets',
    },
})
