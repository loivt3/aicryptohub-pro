<template>
  <header class="m-header">
    <div class="m-header-content">
      <!-- Left: Home Icon -->
      <div class="m-header-left">
        <a href="https://aicryptohub.io" class="m-action-btn" title="Home">
          <Icon name="ph:house" class="m-icon" />
        </a>
      </div>
      
      <!-- Center: Logo -->
      <div class="m-logo">
        <img :src="logoSrc" alt="CoinSight" class="m-logo-img" />
      </div>
      
      <!-- Right: Actions -->
      <div class="m-header-right">
        <button class="m-action-btn" @click="$emit('openSearch')" title="Search">
          <Icon name="ph:magnifying-glass" class="m-icon" />
        </button>
        <button 
          class="m-action-btn"
          :class="{ active: activeTab === 'alerts' }"
          @click="$emit('setTab', 'alerts')"
          title="Alerts"
        >
          <Icon name="ph:bell" class="m-icon" />
          <span v-if="alertCount > 0" class="m-alert-badge">{{ alertCount > 9 ? '9+' : alertCount }}</span>
        </button>
        <button 
          class="m-action-btn"
          :class="{ active: activeTab === 'portfolio' }"
          @click="$emit('setTab', 'portfolio')"
          title="Portfolio"
        >
          <Icon name="ph:briefcase" class="m-icon" />
        </button>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

// Props
defineProps<{
  activeTab?: string
}>()

// Emits
defineEmits<{
  (e: 'setTab', tab: string): void
  (e: 'openSearch'): void
}>()

// State
const btcPrice = ref(98500)
const btcChange = ref(2.4)
const alertCount = ref(3)

// Logo path - use explicit path to avoid hydration issues
const logoSrc = '/images/coinsight-logo.png'

// Format currency
const formatCurrency = (n: number, decimals = 2) => {
  if (!n) return '$--'
  if (n >= 1e12) return '$' + (n / 1e12).toFixed(decimals) + 'T'
  if (n >= 1e9) return '$' + (n / 1e9).toFixed(decimals) + 'B'
  if (n >= 1e6) return '$' + (n / 1e6).toFixed(decimals) + 'M'
  if (n >= 1) return '$' + n.toLocaleString('en-US', { minimumFractionDigits: decimals, maximumFractionDigits: decimals })
  return '$' + n.toFixed(6)
}

// TODO: Fetch real BTC price from API
onMounted(async () => {
  try {
    const api = useApi()
    const res = await api.getCoin('bitcoin')
    if (res.success && res.data) {
      btcPrice.value = res.data.price || 98500
      btcChange.value = res.data.change_24h || 0
    }
  } catch (e) {
    console.warn('Failed to fetch BTC price:', e)
  }
})
</script>

<style scoped>
.m-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(20, 28, 43, 0.95);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.m-header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
}

.m-header-left,
.m-header-right {
  display: flex;
  align-items: center;
  gap: 2px;
}

.m-header-left {
  min-width: 40px;
}

.m-logo {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
}

.m-logo-img {
  height: 60px;
  width: auto;
}

.m-ticker {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.75rem;
  padding: 4px 8px;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 6px;
}

.m-ticker-label {
  color: rgba(255, 255, 255, 0.5);
  font-weight: 500;
}

.m-ticker-value {
  color: #22c55e;
  font-weight: 600;
}

.m-ticker-value.negative {
  color: #ef4444;
}

.m-actions {
  display: flex;
  align-items: center;
  gap: 2px;
}

.m-action-btn {
  position: relative;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.2s;
  text-decoration: none;
}

.m-action-btn:hover,
.m-action-btn.active {
  color: #38efeb;
  background: rgba(56, 239, 235, 0.1);
}

.m-icon {
  width: 20px;
  height: 20px;
}

.m-alert-badge {
  position: absolute;
  top: 2px;
  right: 2px;
  min-width: 16px;
  height: 16px;
  padding: 0 4px;
  background: #ef4444;
  color: white;
  font-size: 10px;
  font-weight: 700;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
