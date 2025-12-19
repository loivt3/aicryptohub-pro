<template>
  <header class="d-header">
    <!-- Ticker Bar -->
    <div class="d-ticker-bar">
      <div class="d-ticker-items">
        <div class="d-ticker-item">
          <span class="d-ticker-label">Coins:</span>
          <strong>{{ totalCoins }}</strong>
        </div>
        <div class="d-ticker-item" :class="{ negative: btcChange < 0 }">
          <span class="d-ticker-label">BTC:</span>
          <strong>{{ formatPrice(btcPrice) }}</strong>
          <span class="d-ticker-change" :class="btcChange >= 0 ? 'up' : 'down'">
            {{ btcChange >= 0 ? '+' : '' }}{{ btcChange.toFixed(2) }}%
          </span>
        </div>
        <div class="d-ticker-item" :class="{ negative: ethChange < 0 }">
          <span class="d-ticker-label">ETH:</span>
          <strong>{{ formatPrice(ethPrice) }}</strong>
          <span class="d-ticker-change" :class="ethChange >= 0 ? 'up' : 'down'">
            {{ ethChange >= 0 ? '+' : '' }}{{ ethChange.toFixed(2) }}%
          </span>
        </div>
        <div class="d-ticker-item">
          <span class="d-ticker-label">Gas:</span>
          <strong>{{ gasPrice }} Gwei</strong>
        </div>
        <div class="d-ticker-item">
          <span class="d-ticker-label">Fear & Greed:</span>
          <strong :class="fearGreedClass">{{ fearGreedValue }}</strong>
        </div>
      </div>
      <div class="d-ticker-time">
        <span>Last Update:</span>
        <strong>{{ lastUpdated }}</strong>
      </div>
    </div>
    
    <!-- Main Header -->
    <div class="d-header-main">
      <NuxtLink to="/" class="d-logo">
        <img src="/images/coinsight-logo-v2.png" alt="CoinSight" class="d-logo-img" />
      </NuxtLink>
      
      <nav class="d-nav">
        <NuxtLink 
          v-for="item in navItems" 
          :key="item.path"
          :to="item.path"
          class="d-nav-item"
          :class="{ active: isActive(item.path) }"
        >
          <Icon :name="item.icon" class="d-nav-icon" />
          {{ item.label }}
        </NuxtLink>
      </nav>
      
      <div class="d-header-actions">
        <button class="d-search-btn" @click="$emit('openSearch')">
          <Icon name="ph:magnifying-glass" class="w-5 h-5" />
          <span>Search</span>
          <kbd>⌘K</kbd>
        </button>
        
        <div class="d-header-icons">
          <button class="d-icon-btn" title="Notifications">
            <Icon name="ph:bell" class="w-5 h-5" />
            <span class="d-badge">3</span>
          </button>
          <button class="d-icon-btn" title="Settings">
            <Icon name="ph:gear" class="w-5 h-5" />
          </button>
          <!-- Theme Toggle -->
          <button class="d-icon-btn d-theme-toggle" :title="isDark ? 'Light Mode' : 'Dark Mode'" @click="toggleTheme">
            <Icon :name="isDark ? 'ph:sun' : 'ph:moon'" class="w-5 h-5" />
          </button>
        </div>
        
        <div class="d-user-menu">
          <NuxtLink to="/login" class="d-btn-text">Login</NuxtLink>
          <NuxtLink to="/register" class="d-btn-primary">Get Started</NuxtLink>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
const route = useRoute()
const { isDark, toggleTheme } = useTheme()

defineEmits(['openSearch'])

const navItems = [
  { path: '/', label: 'Dashboard', icon: 'ph:squares-four' },
  { path: '/market', label: 'Market', icon: 'ph:chart-line-up' },
  { path: '/analysis', label: 'Analysis', icon: 'ph:chart-bar' },
  { path: '/portfolio', label: 'Portfolio', icon: 'ph:wallet' },
  { path: '/onchain', label: 'On-Chain', icon: 'ph:link' },
]

// Market data
const totalCoins = ref(250)
const btcPrice = ref(98500)
const btcChange = ref(2.4)
const ethPrice = ref(3450)
const ethChange = ref(1.8)
const gasPrice = ref(28)
const fearGreedValue = ref(72)
const lastUpdated = ref(new Date().toLocaleTimeString())

const fearGreedClass = computed(() => {
  if (fearGreedValue.value >= 60) return 'greed'
  if (fearGreedValue.value <= 40) return 'fear'
  return 'neutral'
})

const isActive = (path: string) => {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}

const formatPrice = (price: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0,
  }).format(price)
}
</script>

<style scoped>
.d-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: var(--bg-primary);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border);
  transition: background-color 0.3s, border-color 0.3s;
}

/* Ticker Bar */
.d-ticker-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 24px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border);
  font-size: 12px;
}

.d-ticker-items {
  display: flex;
  gap: 24px;
}

.d-ticker-item {
  display: flex;
  align-items: center;
  gap: 6px;
  color: rgba(255, 255, 255, 0.6);
}

.d-ticker-item strong {
  color: #ffffff;
  font-weight: 600;
}

.d-ticker-label {
  color: rgba(255, 255, 255, 0.4);
}

.d-ticker-change {
  font-size: 11px;
  font-weight: 600;
}

.d-ticker-change.up { color: #22c55e; }
.d-ticker-change.down { color: #ef4444; }

.d-ticker-time {
  color: rgba(255, 255, 255, 0.4);
  font-size: 11px;
}

.d-ticker-time strong {
  color: rgba(255, 255, 255, 0.6);
}

/* Fear & Greed Colors */
.greed { color: #22c55e !important; }
.fear { color: #ef4444 !important; }
.neutral { color: #f97316 !important; }

/* Main Header */
.d-header-main {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 64px;
}

/* Logo */
.d-logo {
  display: flex;
  align-items: center;
  text-decoration: none;
}

.d-logo-img {
  height: 36px;
  width: auto;
}

/* Navigation */
.d-nav {
  display: flex;
  align-items: center;
  gap: 4px;
}

.d-nav-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  color: rgba(255, 255, 255, 0.6);
  text-decoration: none;
  border-radius: 10px;
  transition: all 0.2s;
  font-size: 14px;
  font-weight: 500;
}

.d-nav-item:hover {
  color: #ffffff;
  background: rgba(255, 255, 255, 0.06);
}

.d-nav-item.active {
  color: #38efeb;
  background: rgba(56, 239, 235, 0.1);
}

.d-nav-icon {
  width: 20px;
  height: 20px;
}

/* Header Actions */
.d-header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.d-search-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  color: rgba(255, 255, 255, 0.5);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.d-search-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
}

.d-search-btn kbd {
  padding: 2px 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  font-size: 11px;
  font-family: inherit;
}

.d-header-icons {
  display: flex;
  align-items: center;
  gap: 4px;
}

.d-icon-btn {
  position: relative;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: 10px;
  color: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  transition: all 0.2s;
}

.d-icon-btn:hover {
  background: rgba(255, 255, 255, 0.06);
  color: #ffffff;
}

.d-badge {
  position: absolute;
  top: 6px;
  right: 6px;
  min-width: 16px;
  height: 16px;
  padding: 0 4px;
  background: #ef4444;
  border-radius: 8px;
  font-size: 10px;
  font-weight: 600;
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
}

.d-user-menu {
  display: flex;
  align-items: center;
  gap: 12px;
}

.d-btn-text {
  padding: 8px 16px;
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: color 0.2s;
}

.d-btn-text:hover {
  color: #ffffff;
}

.d-btn-primary {
  padding: 8px 20px;
  background: linear-gradient(135deg, #38efeb, #0066ff);
  border-radius: 10px;
  color: #000;
  text-decoration: none;
  font-size: 14px;
  font-weight: 600;
  transition: transform 0.2s, box-shadow 0.2s;
}

.d-btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 20px rgba(56, 239, 235, 0.3);
}
</style>
