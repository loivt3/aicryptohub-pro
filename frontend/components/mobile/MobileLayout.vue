<template>
  <div class="mobile-layout">
    <!-- Mobile Header -->
    <header class="m-header">
      <div class="m-header-content">
        <!-- Logo -->
        <div class="m-logo">
          <img src="/images/coinsight-logo-v2.png" alt="CoinSight" class="m-logo-img" />
        </div>
        
        <!-- BTC Ticker -->
        <div class="m-ticker">
          <span class="m-ticker-label">BTC</span>
          <span class="m-ticker-value" :class="{ negative: btcChange < 0 }">
            {{ formatPrice(btcPrice) }}
          </span>
        </div>
        
        <!-- Action Icons -->
        <div class="m-actions">
          <a href="https://aicryptohub.io" class="m-action-btn">
            <Icon name="ph:house" class="m-icon" />
          </a>
          <button class="m-action-btn" @click="$emit('openSearch')">
            <Icon name="ph:magnifying-glass" class="m-icon" />
          </button>
          <button 
            class="m-action-btn"
            :class="{ active: activeTab === 'alerts' }"
            @click="setActiveTab('alerts')"
          >
            <Icon name="ph:bell" class="m-icon" />
            <span v-if="alertCount > 0" class="m-badge">{{ alertCount > 9 ? '9+' : alertCount }}</span>
          </button>
          <button 
            class="m-action-btn"
            :class="{ active: activeTab === 'portfolio' }"
            @click="setActiveTab('portfolio')"
          >
            <Icon name="ph:wallet" class="m-icon" />
          </button>
        </div>
      </div>
    </header>
    
    <!-- Mobile Bottom Navigation -->
    <nav class="m-bottom-nav">
      <button 
        v-for="item in navItems" 
        :key="item.id"
        class="m-nav-item"
        :class="{ active: activeTab === item.id }"
        @click="setActiveTab(item.id)"
      >
        <Icon :name="item.icon" class="m-nav-icon" />
        <span class="m-nav-label">{{ item.label }}</span>
      </button>
    </nav>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{
  activeTab: string
}>()

const emit = defineEmits(['openSearch', 'update:activeTab'])

const navItems = [
  { id: 'dashboard', label: 'Dashboard', icon: 'solar:widget-2-linear' },
  { id: 'market', label: 'Market', icon: 'solar:graph-up-linear' },
  { id: 'analysis', label: 'Analysis', icon: 'solar:chart-2-linear' },
  { id: 'shadow', label: 'Shadow', icon: 'solar:radar-2-linear' },
  { id: 'aichat', label: 'AI Chat', icon: 'solar:chat-round-dots-linear' },
]

// Mock data
const btcPrice = ref(98500)
const btcChange = ref(2.4)
const alertCount = ref(3)

const setActiveTab = (tab: string) => {
  emit('update:activeTab', tab)
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
.m-header {
  position: sticky;
  top: 0;
  z-index: 50;
  background: rgba(15, 25, 35, 0.85);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.m-header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
}

.m-logo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.m-logo-img {
  height: 28px;
  width: auto;
}

.m-logo-icon {
  font-size: 1.25rem;
}

.m-logo-text {
  font-weight: 700;
  font-size: 1rem;
  background: linear-gradient(135deg, #38efeb, #9f7aea);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.m-ticker {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
}

.m-ticker-label {
  color: #6b7280;
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
  gap: 0.25rem;
}

.m-action-btn {
  position: relative;
  width: 2.25rem;
  height: 2.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  color: #9ca3af;
  cursor: pointer;
  border-radius: 0.5rem;
  transition: all 0.2s;
}

.m-action-btn:hover,
.m-action-btn.active {
  color: #38efeb;
  background: rgba(56, 239, 235, 0.1);
}

.m-icon {
  width: 1.25rem;
  height: 1.25rem;
}

.m-badge {
  position: absolute;
  top: 0;
  right: 0;
  min-width: 1rem;
  height: 1rem;
  padding: 0 0.25rem;
  background: #ef4444;
  color: white;
  font-size: 0.625rem;
  font-weight: 600;
  border-radius: 9999px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Bottom Navigation - Floating Island */
.m-bottom-nav {
  position: fixed;
  bottom: 24px; /* Move up for floating effect */
  left: 16px;
  right: 16px;
  z-index: 50;
  display: flex;
  justify-content: space-around;
  background: rgba(15, 25, 35, 0.85); /* Dark Glass */
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 24px; /* Pill shape */
  padding: 0.75rem 0; /* Slightly more padding */
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5); /* Deep shadow for lift */
}

.m-nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
  padding: 0.5rem 0.75rem;
  background: transparent;
  border: none;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.2s;
}

.m-nav-item.active {
  color: #38efeb;
  background: linear-gradient(180deg, rgba(56, 239, 235, 0.15) 0%, rgba(56, 239, 235, 0.0) 100%);
  border-radius: 12px;
}

.m-nav-icon {
  width: 1.25rem;
  height: 1.25rem;
}

.m-nav-label {
  font-size: 0.625rem;
  font-weight: 500;
}
</style>
