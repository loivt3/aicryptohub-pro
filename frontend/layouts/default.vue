<template>
  <div class="flex flex-col min-h-screen">
    <!-- Header -->
    <header class="sticky top-0 z-50 glass-card border-b border-white/5">
      <div class="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
        <!-- Logo -->
        <NuxtLink to="/" class="flex items-center gap-2">
          <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-accent-purple flex items-center justify-center">
            <Icon name="ph:chart-line-up-bold" class="w-6 h-6 text-white" />
          </div>
          <span class="text-xl font-bold gradient-text">AI Crypto Hub</span>
        </NuxtLink>
        
        <!-- Desktop Nav -->
        <nav class="hidden md:flex items-center gap-6">
          <NuxtLink 
            v-for="item in navItems" 
            :key="item.path" 
            :to="item.path"
            class="text-gray-400 hover:text-white transition-colors"
            active-class="text-primary"
          >
            {{ item.label }}
          </NuxtLink>
        </nav>
        
        <!-- Auth Buttons -->
        <div class="flex items-center gap-3">
          <NuxtLink 
            to="/login" 
            class="px-4 py-2 text-sm text-gray-300 hover:text-white transition-colors"
          >
            Login
          </NuxtLink>
          <NuxtLink 
            to="/register" 
            class="px-4 py-2 text-sm bg-primary/20 text-primary rounded-lg hover:bg-primary/30 transition-colors"
          >
            Get Started
          </NuxtLink>
        </div>
      </div>
    </header>
    
    <!-- Main Content -->
    <main class="flex-1">
      <slot />
    </main>
    
    <!-- Footer -->
    <footer class="border-t border-white/5 py-8 mt-auto">
      <div class="max-w-7xl mx-auto px-4 text-center text-gray-500 text-sm">
        <p>© {{ new Date().getFullYear() }} AI Crypto Hub. AI-Powered Cryptocurrency Analysis.</p>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
const navItems = [
  { path: '/', label: 'Dashboard' },
  { path: '/market', label: 'Market' },
  { path: '/analysis', label: 'Analysis' },
  { path: '/portfolio', label: 'Portfolio' },
]
</script>
