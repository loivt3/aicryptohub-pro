import { createRouter, createWebHistory } from 'vue-router'

const routes = [
    {
        path: '/',
        component: () => import('@/layouts/AdminLayout.vue'),
        children: [
            // Dashboard
            {
                path: '',
                name: 'dashboard',
                component: () => import('@/views/DashboardView.vue'),
                meta: { title: 'Dashboard', icon: 'home' }
            },

            // Process Manager
            {
                path: 'process',
                name: 'process-manager',
                component: () => import('@/views/ProcessManagerView.vue'),
                meta: { title: 'Process Manager', icon: 'settings' }
            },

            // Data Management (CMS)
            {
                path: 'data',
                name: 'data-management',
                component: () => import('@/views/DataManagementView.vue'),
                meta: { title: 'Data Management', icon: 'server' }
            },
            {
                path: 'data/coins',
                name: 'coins-manager',
                component: () => import('@/views/data/CoinsManagerView.vue'),
                meta: { title: 'Coins Manager', parent: 'data-management' }
            },
            {
                path: 'data/news',
                name: 'news-curation',
                component: () => import('@/views/data/NewsCurationView.vue'),
                meta: { title: 'News Curation', parent: 'data-management' }
            },
            {
                path: 'data/corrections',
                name: 'market-corrections',
                component: () => import('@/views/data/MarketCorrectionsView.vue'),
                meta: { title: 'Market Corrections', parent: 'data-management' }
            },

            // System Configuration
            {
                path: 'settings',
                name: 'settings',
                component: () => import('@/views/SettingsView.vue'),
                meta: { title: 'System Settings', icon: 'cog' }
            },
            {
                path: 'settings/backend',
                name: 'backend-settings',
                component: () => import('@/views/settings/BackendSettingsView.vue'),
                meta: { title: 'Backend Settings', parent: 'settings' }
            },
            {
                path: 'settings/frontend',
                name: 'frontend-settings',
                component: () => import('@/views/settings/FrontendSettingsView.vue'),
                meta: { title: 'Frontend Settings', parent: 'settings' }
            },
            {
                path: 'settings/ai',
                name: 'ai-tuning',
                component: () => import('@/views/settings/AITuningView.vue'),
                meta: { title: 'AI Tuning', parent: 'settings' }
            },

            // User & Roles
            {
                path: 'users',
                name: 'users',
                component: () => import('@/views/UsersView.vue'),
                meta: { title: 'Users & Roles', icon: 'people' }
            },

            // Audit & Security
            {
                path: 'audit',
                name: 'audit',
                component: () => import('@/views/AuditView.vue'),
                meta: { title: 'Audit & Security', icon: 'shield' }
            },
        ]
    },

    // Login (outside layout)
    {
        path: '/login',
        name: 'login',
        component: () => import('@/views/LoginView.vue'),
        meta: { title: 'Admin Login' }
    },
]

const router = createRouter({
    history: createWebHistory('/admin/'),
    routes,
})

// Navigation guard for auth (disabled for initial testing)
router.beforeEach((to, from, next) => {
    // Temporarily allow all access for debugging
    // TODO: Re-enable auth after fixing boot loop
    const token = localStorage.getItem('admin_token')

    // Always allow login page
    if (to.name === 'login') {
        next()
        return
    }

    // For now, auto-set token if not present to allow access
    if (!token) {
        localStorage.setItem('admin_token', 'debug_token')
    }
    next()
})

export default router
