<template>
  <div class="min-h-screen flex items-center justify-center py-12 px-4">
    <div class="max-w-md w-full">
      <div class="text-center mb-8">
        <div class="w-16 h-16 mx-auto rounded-2xl bg-gradient-to-br from-primary to-accent-purple flex items-center justify-center mb-4">
          <Icon name="ph:chart-line-up-bold" class="w-8 h-8 text-white" />
        </div>
        <h1 class="text-2xl font-bold">Create Account</h1>
        <p class="text-gray-400 mt-2">Start your crypto journey with AI insights</p>
      </div>
      
      <div class="glass-card p-6">
        <form @submit.prevent="handleRegister" class="space-y-4">
          <div>
            <label class="block text-sm font-medium mb-2">Name</label>
            <input 
              v-model="name"
              type="text" 
              class="w-full px-4 py-3 bg-dark-800 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-primary/50"
              placeholder="Your name"
            />
          </div>
          
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
              minlength="8"
              class="w-full px-4 py-3 bg-dark-800 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-primary/50"
              placeholder="••••••••"
            />
            <p class="text-xs text-gray-500 mt-1">At least 8 characters</p>
          </div>
          
          <div>
            <label class="flex items-start gap-2">
              <input type="checkbox" required class="mt-1 rounded" />
              <span class="text-sm text-gray-400">
                I agree to the 
                <NuxtLink to="/terms" class="text-primary">Terms of Service</NuxtLink>
                and
                <NuxtLink to="/privacy" class="text-primary">Privacy Policy</NuxtLink>
              </span>
            </label>
          </div>
          
          <button 
            type="submit"
            :disabled="loading"
            class="w-full py-3 bg-gradient-to-r from-primary to-accent-purple text-dark-950 font-bold rounded-xl hover:opacity-90 transition-opacity disabled:opacity-50"
          >
            {{ loading ? 'Creating account...' : 'Create Account' }}
          </button>
          
          <p v-if="error" class="text-red-400 text-sm text-center">{{ error }}</p>
        </form>
        
        <div class="mt-6 text-center">
          <p class="text-gray-400">
            Already have an account?
            <NuxtLink to="/login" class="text-primary hover:underline">Sign in</NuxtLink>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  title: 'Register',
  layout: 'auth',
})

useSeoMeta({
  title: 'Create Account - AI Crypto Hub',
  description: 'Sign up for AI Crypto Hub to access AI-powered cryptocurrency analysis and portfolio tracking.',
})

const authStore = useAuthStore()
const router = useRouter()

const name = ref('')
const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

const handleRegister = async () => {
  loading.value = true
  error.value = ''
  
  const success = await authStore.register(email.value, password.value, name.value)
  
  if (success) {
    router.push('/')
  } else {
    error.value = authStore.error || 'Registration failed'
  }
  
  loading.value = false
}
</script>
