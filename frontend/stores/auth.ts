/**
 * Auth Store - Pinia
 * Quản lý authentication state
 */

import { defineStore } from 'pinia'

interface User {
    id: string
    email: string
    name?: string
}

interface AuthState {
    user: User | null
    token: string | null
    loading: boolean
    error: string | null
}

export const useAuthStore = defineStore('auth', {
    state: (): AuthState => ({
        user: null,
        token: null,
        loading: false,
        error: null,
    }),

    getters: {
        isAuthenticated: (state) => !!state.token,
        currentUser: (state) => state.user,
    },

    actions: {
        async login(email: string, password: string) {
            this.loading = true
            this.error = null

            try {
                const config = useRuntimeConfig()
                const response = await $fetch<{
                    access_token: string
                    user: User
                }>(`${config.public.apiBase}/auth/login`, {
                    method: 'POST',
                    body: { email, password },
                })

                this.token = response.access_token
                this.user = response.user

                // Store token in localStorage
                if (process.client) {
                    localStorage.setItem('auth_token', response.access_token)
                }

                return true
            } catch (err: any) {
                this.error = err.data?.detail || 'Login failed'
                return false
            } finally {
                this.loading = false
            }
        },

        async register(email: string, password: string, name?: string) {
            this.loading = true
            this.error = null

            try {
                const config = useRuntimeConfig()
                const response = await $fetch<{
                    access_token: string
                    user: User
                }>(`${config.public.apiBase}/auth/register`, {
                    method: 'POST',
                    body: { email, password, name },
                })

                this.token = response.access_token
                this.user = response.user

                if (process.client) {
                    localStorage.setItem('auth_token', response.access_token)
                }

                return true
            } catch (err: any) {
                this.error = err.data?.detail || 'Registration failed'
                return false
            } finally {
                this.loading = false
            }
        },

        logout() {
            this.token = null
            this.user = null

            if (process.client) {
                localStorage.removeItem('auth_token')
            }
        },

        // Check and restore auth state from localStorage
        initAuth() {
            if (process.client) {
                const token = localStorage.getItem('auth_token')
                if (token) {
                    this.token = token
                    // TODO: Validate token and fetch user profile
                }
            }
        },
    },
})
