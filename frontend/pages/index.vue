<template>
  <div class="app-container" :class="{ 'mobile': isMobile }">
    <!-- Mobile Layout -->
    <template v-if="isMobile">
      <!-- Mobile Header -->
      <MobileLayout 
        :activeTab="activeTab" 
        @update:activeTab="activeTab = $event"
        @openSearch="showSearch = true"
      />
      
      <!-- Mobile Content -->
      <main class="mobile-main">
        <MobileDashboard v-if="activeTab === 'dashboard'" />
        <MobileMarket v-else-if="activeTab === 'market'" />
        <MobileAnalysis v-else-if="activeTab === 'analysis'" />
        <MobilePortfolio v-else-if="activeTab === 'portfolio'" />
        <MobileAlerts v-else-if="activeTab === 'alerts'" />
        <MobileOnChain v-else-if="activeTab === 'onchain'" />
        <MobileAIChat v-else-if="activeTab === 'aichat'" />
      </main>
      
      <!-- Mobile Search Overlay -->
      <MobileSearch :isOpen="showSearch" @close="showSearch = false" @select="onCoinSelect" />
    </template>
    
    <!-- Desktop Layout -->
    <template v-else>
      <DesktopHeader @openSearch="showSearch = true" />
      <main class="desktop-main">
        <DesktopDashboard />
      </main>
    </template>
  </div>
</template>

<script setup lang="ts">
import '~/assets/css/mobile.css'

// Device detection
const { isMobile } = useDevice()

// Mobile state
const activeTab = ref('dashboard')
const showSearch = ref(false)

// SEO
useSeoMeta({
  title: 'AI Crypto Hub - AI-Powered Crypto Analysis',
  description: 'Real-time cryptocurrency dashboard with AI-powered market analysis, sentiment signals, and on-chain data.',
})

const onCoinSelect = (coin: any) => {
  console.log('Selected coin:', coin)
  navigateTo(`/coin/${coin.coin_id}`)
}
</script>

<style>
/* Base App Styles */
.app-container {
  min-height: 100vh;
  background: #0b0f19;
  color: #ffffff;
}

.app-container.mobile {
  padding-bottom: 70px;
}

/* Mobile Main */
.mobile-main {
  padding: 0 12px;
}

/* Desktop Main */
.desktop-main {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
}

/* Gradient text */
.gradient-text {
  background: linear-gradient(135deg, #38efeb, #9f7aea);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* Glass card */
.glass-card {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  backdrop-filter: blur(12px);
}

/* Text utilities */
.m-text-success { color: #22c55e !important; }
.m-text-danger { color: #ef4444 !important; }
.m-text-muted { color: rgba(255, 255, 255, 0.5) !important; }
.m-text-accent { color: #38efeb !important; }

/* Common section styles */
.m-section {
  margin-bottom: 16px;
}

.m-section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.m-section-title {
  font-size: 16px;
  font-weight: 700;
  color: #ffffff;
  margin: 0;
}

.m-section-link {
  font-size: 12px;
  color: #38efeb;
  text-decoration: none;
}

/* Stats scroll container */
.m-stats-scroll {
  overflow-x: auto;
  margin: 0 -12px;
  padding: 0 12px 8px;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
}

.m-stats-scroll::-webkit-scrollbar {
  display: none;
}

.m-stats-container {
  display: flex;
  gap: 8px;
}

/* List styles */
.m-list {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  overflow: hidden;
}

.m-list-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  cursor: pointer;
  transition: background 0.2s;
}

.m-list-item:last-child {
  border-bottom: none;
}

.m-list-item:active {
  background: rgba(255, 255, 255, 0.05);
}

.m-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
}

.m-info {
  flex: 1;
  min-width: 0;
}

.m-info-title {
  font-size: 14px;
  font-weight: 600;
  color: #ffffff;
  display: block;
}

.m-info-subtitle {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  display: block;
}

.m-price-col {
  text-align: right;
  min-width: 80px;
}

/* Bottom spacer */
.m-bottom-spacer {
  height: 20px;
}

/* Spinner */
.m-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid rgba(255, 255, 255, 0.1);
  border-top-color: #38efeb;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
