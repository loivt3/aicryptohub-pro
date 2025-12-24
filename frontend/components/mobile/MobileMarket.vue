<template>
  <div class="mobile-layout">
    <!-- Header -->
    <header class="m-header-simple">
      <h1 class="m-header-title">Discovery</h1>
      <button class="m-search-btn" @click="$emit('openSearch')">
        <Icon name="lucide:search" class="w-5 h-5" />
      </button>
    </header>

    <main class="m-main">
      <!-- Market Heatmap Section -->
      <section class="m-section">
        <div class="heatmap-header">
          <h2 class="heatmap-title">Market Heatmap</h2>
          <div class="heatmap-tabs">
            <button 
              v-for="tf in ['1H', '4H', '24H']" 
              :key="tf"
              class="heatmap-tab"
              :class="{ active: heatmapTimeframe === tf }"
              @click="heatmapTimeframe = tf"
            >{{ tf }}</button>
          </div>
        </div>
        
        <!-- Bento Grid Heatmap -->
        <div class="heatmap-grid">
          <!-- BTC - Large cell -->
          <div 
            class="heatmap-cell heatmap-cell--large"
            :class="getHeatmapCellClass(topCoins[0])"
            v-if="topCoins[0]"
          >
            <div class="heatmap-cell-top">
              <span class="heatmap-symbol">{{ topCoins[0].symbol }}</span>
              <span class="heatmap-change" :class="getChangeClass(topCoins[0])">
                {{ formatChange(topCoins[0]) }}
              </span>
            </div>
            <div class="heatmap-cell-bottom">
              <span class="heatmap-label">Vol</span>
              <span class="heatmap-vol">{{ formatVolume(topCoins[0].volume_24h) }}</span>
            </div>
          </div>
          
          <!-- ETH - Large cell -->
          <div 
            class="heatmap-cell heatmap-cell--large"
            :class="getHeatmapCellClass(topCoins[1])"
            v-if="topCoins[1]"
          >
            <div class="heatmap-cell-top">
              <span class="heatmap-symbol">{{ topCoins[1].symbol }}</span>
              <span class="heatmap-change" :class="getChangeClass(topCoins[1])">
                {{ formatChange(topCoins[1]) }}
              </span>
            </div>
            <div class="heatmap-cell-bottom">
              <span class="heatmap-label">Vol</span>
              <span class="heatmap-vol">{{ formatVolume(topCoins[1].volume_24h) }}</span>
            </div>
          </div>
          
          <!-- SOL, BNB - Medium cells -->
          <div 
            v-for="coin in topCoins.slice(2, 4)" 
            :key="coin.coin_id"
            class="heatmap-cell heatmap-cell--medium"
            :class="getHeatmapCellClass(coin)"
          >
            <span class="heatmap-symbol">{{ coin.symbol }}</span>
            <span class="heatmap-change-small" :class="getChangeClass(coin)">
              {{ formatChange(coin) }}
            </span>
          </div>
          
          <!-- XRP, DOGE - Small cells -->
          <div 
            v-for="coin in topCoins.slice(4, 6)" 
            :key="coin.coin_id"
            class="heatmap-cell heatmap-cell--small"
            :class="getHeatmapCellClass(coin)"
          >
            <span class="heatmap-symbol-sm">{{ coin.symbol }}</span>
            <span class="heatmap-change-sm" :class="getChangeClass(coin)">
              {{ formatChange(coin) }}
            </span>
          </div>
        </div>
      </section>

      <!-- The Screener Section -->
      <section class="m-section">
        <h2 class="screener-title">The Screener</h2>
        
        <!-- Category Filter Tabs -->
        <div class="screener-tabs">
          <button 
            v-for="cat in categories" 
            :key="cat.id"
            class="screener-tab"
            :class="{ active: activeCategory === cat.id }"
            @click="activeCategory = cat.id"
          >{{ cat.label }}</button>
        </div>
        
        <!-- Table Header -->
        <div class="screener-header">
          <span class="screener-col screener-col--asset">Asset</span>
          <span class="screener-col screener-col--price">Price</span>
          <span class="screener-col screener-col--asi">ASI Score</span>
        </div>
        
        <!-- Coin List -->
        <div class="screener-list">
          <div 
            v-for="coin in filteredCoins" 
            :key="coin.coin_id"
            class="screener-row"
          >
            <div class="screener-asset">
              <img :src="coin.image" class="screener-avatar" :alt="coin.symbol" />
              <div class="screener-info">
                <span class="screener-symbol">{{ coin.symbol }}</span>
                <span class="screener-name">{{ coin.name }}</span>
              </div>
            </div>
            <div class="screener-price-col">
              <span class="screener-price">{{ formatPrice(coin.price) }}</span>
              <span class="screener-change" :class="getChangeClass(coin)">
                {{ formatChange(coin) }}
              </span>
            </div>
            <div class="screener-asi-col">
              <span class="asi-badge" :class="getAsiBadgeClass(coin.asi_score)">
                {{ coin.asi_score || '--' }}
              </span>
            </div>
          </div>
        </div>
      </section>

      <div class="m-bottom-spacer"></div>
    </main>

    <!-- Bottom Navigation - Keep Original -->
    <nav class="m-bottom-nav">
      <button class="m-nav-item" :class="{ active: activeTab === 'dashboard' }" @click="$emit('setTab', 'dashboard')">
        <Icon name="ph:squares-four" class="m-nav-icon" />
        <span class="m-nav-label">Dashboard</span>
      </button>
      <button class="m-nav-item" :class="{ active: activeTab === 'market' }" @click="$emit('setTab', 'market')">
        <Icon name="ph:trend-up" class="m-nav-icon" />
        <span class="m-nav-label">Market</span>
      </button>
      <button class="m-nav-item" :class="{ active: activeTab === 'analysis' }" @click="$emit('setTab', 'analysis')">
        <Icon name="ph:chart-line-up" class="m-nav-icon" />
        <span class="m-nav-label">Analysis</span>
      </button>
      <button class="m-nav-item" :class="{ active: activeTab === 'shadow' }" @click="$emit('setTab', 'shadow')">
        <Icon name="ph:eye" class="m-nav-icon" />
        <span class="m-nav-label">Shadow</span>
      </button>
      <button class="m-nav-item" :class="{ active: activeTab === 'aichat' }" @click="$emit('setTab', 'aichat')">
        <Icon name="ph:chat-dots" class="m-nav-icon" />
        <span class="m-nav-label">AI Chat</span>
      </button>
    </nav>
  </div>
</template>

<script setup lang="ts">
interface Coin {
  coin_id: string
  symbol: string
  name: string
  image?: string
  price: number
  change_1h?: number
  change_24h: number
  change_7d?: number
  volume_24h?: number
  market_cap?: number
  asi_score?: number
  category?: string
}

defineProps<{
  activeTab?: string
}>()

defineEmits<{
  (e: 'setTab', tab: string): void
  (e: 'openSearch'): void
}>()

const heatmapTimeframe = ref<'1H' | '4H' | '24H'>('24H')
const activeCategory = ref('all')
const loading = ref(true)
const allCoins = ref<Coin[]>([])

const categories = [
  { id: 'all', label: 'All' },
  { id: 'layer-1', label: 'Layer 1' },
  { id: 'ai', label: 'AI Tokens' },
  { id: 'meme', label: 'Meme' },
  { id: 'rwa', label: 'RWA' },
]

// Top coins for heatmap - DYNAMIC based on market cap (top 6)
const topCoins = computed(() => {
  return [...allCoins.value]
    .sort((a, b) => (b.market_cap || 0) - (a.market_cap || 0))
    .slice(0, 6)
})

// Filtered coins for screener
const filteredCoins = computed(() => {
  if (activeCategory.value === 'all') {
    return allCoins.value.slice(0, 20)
  }
  return allCoins.value
    .filter(c => c.category === activeCategory.value)
    .slice(0, 20)
})

// Get change value based on timeframe
const getChangeValue = (coin: Coin) => {
  if (heatmapTimeframe.value === '1H') return coin.change_1h || 0
  if (heatmapTimeframe.value === '4H') return (coin.change_1h || 0) * 2 // approximation
  return coin.change_24h || 0
}

const formatChange = (coin: Coin) => {
  const val = getChangeValue(coin)
  return (val >= 0 ? '+' : '') + val.toFixed(1) + '%'
}

const getChangeClass = (coin: Coin) => {
  const val = getChangeValue(coin)
  return val >= 0 ? 'positive' : 'negative'
}

const getHeatmapCellClass = (coin: Coin | undefined) => {
  if (!coin) return ''
  const val = getChangeValue(coin)
  if (val >= 3) return 'heatmap-strong-up'
  if (val >= 0) return 'heatmap-up'
  if (val >= -3) return 'heatmap-down'
  return 'heatmap-strong-down'
}

const formatPrice = (price: number) => {
  if (!price) return '$--'
  if (price >= 1000) return '$' + price.toLocaleString('en-US', { maximumFractionDigits: 0 })
  if (price >= 1) return '$' + price.toFixed(2)
  return '$' + price.toFixed(4)
}

const formatVolume = (vol: number | undefined) => {
  if (!vol) return '$--'
  if (vol >= 1e9) return '$' + (vol / 1e9).toFixed(0) + 'B'
  if (vol >= 1e6) return '$' + (vol / 1e6).toFixed(0) + 'M'
  return '$' + vol.toLocaleString()
}

const getAsiBadgeClass = (score: number | undefined) => {
  if (!score) return ''
  if (score >= 70) return 'asi-high'
  if (score >= 50) return 'asi-medium'
  return 'asi-low'
}

// Fetch data
const fetchData = async () => {
  loading.value = true
  try {
    const config = useRuntimeConfig()
    const res = await $fetch<any>(`${config.public.apiBase}/market?limit=100`)
    if (res?.data) {
      allCoins.value = res.data.map((c: any) => ({
        coin_id: c.coin_id,
        symbol: c.symbol?.toUpperCase(),
        name: c.name,
        image: c.image,
        price: c.price,
        change_1h: c.change_1h || c.price_change_1h,
        change_24h: c.change_24h,
        change_7d: c.change_7d || c.price_change_7d,
        volume_24h: c.volume_24h,
        market_cap: c.market_cap,
        asi_score: c.asi_score,
        category: c.category,
      }))
    }
  } catch (e) {
    console.error('Failed to fetch coins:', e)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
/* Dark Background */
.mobile-layout {
  background: #0a0f14 !important;
}

/* Simple Header */
.m-header-simple {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: transparent;
}

.m-header-title {
  font-size: 20px;
  font-weight: 700;
  color: #fff;
  margin: 0;
}

.m-search-btn {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
}

/* Heatmap Section */
.heatmap-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.heatmap-title {
  font-size: 18px;
  font-weight: 600;
  color: #fff;
  margin: 0;
}

.heatmap-tabs {
  display: flex;
  gap: 4px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  padding: 3px;
}

.heatmap-tab {
  padding: 6px 12px;
  background: transparent;
  border: none;
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.5);
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.heatmap-tab.active {
  background: #38efeb;
  color: #000;
}

/* Heatmap Grid - Bento Layout */
.heatmap-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: auto auto auto;
  gap: 10px;
}

.heatmap-cell {
  border-radius: 16px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  /* Glassmorphism base */
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

.heatmap-cell::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 16px;
  padding: 1px;
  background: linear-gradient(135deg, rgba(255,255,255,0.15), rgba(255,255,255,0.02));
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
}

.heatmap-cell--large {
  grid-column: span 1;
  min-height: 130px;
}

.heatmap-cell--medium {
  min-height: 75px;
}

.heatmap-cell--small {
  min-height: 55px;
  padding: 12px 14px;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
}

/* Heatmap Colors - Glassmorphism with Glow */
.heatmap-strong-up {
  background: linear-gradient(145deg, rgba(16, 185, 129, 0.25) 0%, rgba(5, 150, 105, 0.15) 100%);
  border: 1px solid rgba(16, 185, 129, 0.35);
  box-shadow: 
    0 4px 24px -1px rgba(16, 185, 129, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.08);
}

.heatmap-up {
  background: linear-gradient(145deg, rgba(16, 185, 129, 0.15) 0%, rgba(5, 150, 105, 0.08) 100%);
  border: 1px solid rgba(16, 185, 129, 0.2);
  box-shadow: 
    0 4px 16px -1px rgba(16, 185, 129, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.05);
}

.heatmap-down {
  background: linear-gradient(145deg, rgba(239, 68, 68, 0.15) 0%, rgba(220, 38, 38, 0.08) 100%);
  border: 1px solid rgba(239, 68, 68, 0.2);
  box-shadow: 
    0 4px 16px -1px rgba(239, 68, 68, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.05);
}

.heatmap-strong-down {
  background: linear-gradient(145deg, rgba(239, 68, 68, 0.25) 0%, rgba(220, 38, 38, 0.15) 100%);
  border: 1px solid rgba(239, 68, 68, 0.35);
  box-shadow: 
    0 4px 24px -1px rgba(239, 68, 68, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.08);
}

.heatmap-cell-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.heatmap-symbol {
  font-size: 20px;
  font-weight: 700;
  color: #fff;
}

.heatmap-symbol-sm {
  font-size: 14px;
  font-weight: 600;
  color: #fff;
}

.heatmap-change {
  font-size: 13px;
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 6px;
}

.heatmap-change.positive {
  background: rgba(34, 197, 94, 0.2);
  color: #22c55e;
}

.heatmap-change.negative {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.heatmap-change-small,
.heatmap-change-sm {
  font-size: 12px;
  font-weight: 600;
}

.heatmap-change-small.positive,
.heatmap-change-sm.positive {
  color: #22c55e;
}

.heatmap-change-small.negative,
.heatmap-change-sm.negative {
  color: #ef4444;
}

.heatmap-cell-bottom {
  display: flex;
  justify-content: flex-end;
  gap: 6px;
  align-items: baseline;
}

.heatmap-label {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
}

.heatmap-vol {
  font-size: 14px;
  font-weight: 600;
  color: #fff;
  font-family: 'SF Mono', monospace;
}

/* Screener Section - Glassmorphism Container */
.screener-title {
  font-size: 18px;
  font-weight: 600;
  color: #fff;
  margin: 0 0 16px 0;
}

.screener-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
  padding-bottom: 4px;
}

.screener-tabs::-webkit-scrollbar {
  display: none;
}

.screener-tab {
  flex-shrink: 0;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  color: rgba(255, 255, 255, 0.6);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.25s ease;
}

.screener-tab:hover {
  background: rgba(255, 255, 255, 0.06);
  border-color: rgba(255, 255, 255, 0.15);
}

.screener-tab.active {
  background: rgba(56, 239, 235, 0.12);
  border-color: rgba(56, 239, 235, 0.4);
  color: #38efeb;
  box-shadow: 0 0 16px -4px rgba(56, 239, 235, 0.3);
}

/* Screener Table - Glass Card */
.screener-header {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 12px 12px 0 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.screener-col {
  font-size: 12px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.4);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.screener-col--asset {
  flex: 1;
}

.screener-col--price {
  width: 100px;
  text-align: right;
}

.screener-col--asi {
  width: 80px;
  text-align: center;
}

.screener-list {
  display: flex;
  flex-direction: column;
  background: rgba(255, 255, 255, 0.02);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-radius: 0 0 16px 16px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-top: none;
  overflow: hidden;
}

.screener-row {
  display: flex;
  align-items: center;
  padding: 14px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
  transition: background 0.2s ease;
}

.screener-row:hover {
  background: rgba(255, 255, 255, 0.03);
}

.screener-row:last-child {
  border-bottom: none;
}

.screener-asset {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
}

.screener-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
}

.screener-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.screener-symbol {
  font-size: 14px;
  font-weight: 600;
  color: #fff;
}

.screener-name {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
}

.screener-price-col {
  width: 100px;
  text-align: right;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.screener-price {
  font-size: 14px;
  font-weight: 600;
  color: #fff;
  font-family: 'SF Mono', monospace;
}

.screener-change {
  font-size: 12px;
  font-weight: 500;
}

.screener-change.positive {
  color: #22c55e;
}

.screener-change.negative {
  color: #ef4444;
}

.screener-asi-col {
  width: 80px;
  display: flex;
  justify-content: center;
}

.asi-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  font-size: 14px;
  font-weight: 700;
  font-family: 'SF Mono', monospace;
}

.asi-high {
  background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
  color: #fff;
}

.asi-medium {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  color: #fff;
}

.asi-low {
  background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%);
  color: #fff;
}

/* Bottom spacer */
.m-bottom-spacer {
  height: 100px;
}
</style>
