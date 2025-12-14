<template>
  <div class="min-h-screen flex items-center justify-center py-12 px-4">
    <div class="max-w-md w-full">
      <div class="text-center mb-8">
        <div class="w-16 h-16 mx-auto rounded-2xl bg-gradient-to-br from-primary to-accent-purple flex items-center justify-center mb-4">
          <Icon name="ph:chart-line-up-bold" class="w-8 h-8 text-white" />
        </div>
        <h1 class="text-2xl font-bold">Welcome Back</h1>
        <p class="text-gray-400 mt-2">Sign in to your AI Crypto Hub account</p>
      </div>
      
      <div class="glass-card p-6">
        <form @submit.prevent="handleLogin" class="space-y-4">
          <div>
            <label class="block text-sm font-medium mb-2">Email</label>
            <input 
              v-model="email"
              type="email" 
              required
              class="w-full px-4 py-3 bg-dark-800 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-primary/50"
              placeholder="you@example.com"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium mb-2">Password</label>
            <input 
              v-model="password"
              type="password" 
              required
              class="w-full px-4 py-3 bg-dark-800 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-primary/50"
              placeholder="••••••••"
            />
          </div>
          
          <div class="flex items-center justify-between text-sm">
            <label class="flex items-center gap-2">
              <input type="checkbox" class="rounded" />
              <span class="text-gray-400">Remember me</span>
            </label>
            <NuxtLink to="/forgot-password" class="text-primary hover:underline">
              Forgot password?
            </NuxtLink>
          </div>
          
          <button 
            type="submit"
            :disabled="loading"
            class="w-full py-3 bg-gradient-to-r from-primary to-accent-purple text-dark-950 font-bold rounded-xl hover:opacity-90 transition-opacity disabled:opacity-50"
          >
            {{ loading ? 'Signing in...' : 'Sign In' }}
          </button>
          
          <p v-if="error" class="text-red-400 text-sm text-center">{{ error }}</p>
        </form>
        
        <div class="mt-6 text-center">
          <p class="text-gray-400">
            Don't have an account?
            <NuxtLink to="/register" class="text-primary hover:underline">Sign up</NuxtLink>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  title: 'Login',
  layout: 'auth',
})

useSeoMeta({
  title: 'Login - AI Crypto Hub',
  description: 'Sign in to access your AI Crypto Hub dashboard and portfolio.',
})

const authStore = useAuthStore()
const router = useRouter()

const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  loading.value = true
  error.value = ''
  
  const success = await authStore.login(email.value, password.value)
  
  if (success) {
    router.push('/')
  } else {
    error.value = authStore.error || 'Login failed'
  }
  
  loading.value = false
}
</script>
