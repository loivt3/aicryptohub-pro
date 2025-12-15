<template>
  <div class="mobile-dashboard">
    <!-- Hero Section -->
    <div class="m-hero">
      <h1 class="m-hero-title">
        <span class="gradient-text">AI-Powered</span> Analysis
      </h1>
      <p class="m-hero-subtitle">Real-time market data and signals</p>
    </div>
    
    <!-- Stats Cards (Horizontal Scroll) -->
    <div class="m-stats-scroll">
      <div class="m-stats-container">
        <div v-for="stat in stats" :key="stat.label" class="m-stat-card">
          <p class="m-stat-label">{{ stat.label }}</p>
          <p class="m-stat-value">{{ stat.value }}</p>
          <p class="m-stat-change" :class="stat.change >= 0 ? 'up' : 'down'">
            {{ stat.change >= 0 ? '+' : '' }}{{ stat.change }}%
          </p>
        </div>
      </div>
    </div>
    
    <!-- Top Gainers Section -->
    <section class="m-section">
      <div class="m-section-header">
        <h2 class="m-section-title">🚀 Top Gainers</h2>
        <NuxtLink to="/market" class="m-section-link">View All</NuxtLink>
      </div>
      
      <div class="m-coin-list">
        <div 
          v-for="coin in topGainers" 
          :key="coin.coin_id"
          class="m-coin-item"
          @click="openCoin(coin.coin_id)"
        >
          <img :src="coin.image" :alt="coin.name" class="m-coin-avatar" />
          <div class="m-coin-info">
            <p class="m-coin-name">{{ coin.name }}</p>
            <p class="m-coin-symbol">{{ coin.symbol }}</p>
          </div>
          <div class="m-coin-price">
            <p class="m-coin-value">${{ formatPrice(coin.price) }}</p>
            <p class="m-coin-change up">+{{ coin.change_24h?.toFixed(2) }}%</p>
          </div>
        </div>
      </div>
    </section>
    
    <!-- Top Losers Section -->
    <section class="m-section">
      <div class="m-section-header">
        <h2 class="m-section-title">📉 Top Losers</h2>
      </div>
      
      <div class="m-coin-list">
        <div 
          v-for="coin in topLosers" 
          :key="coin.coin_id"
          class="m-coin-item"
          @click="openCoin(coin.coin_id)"
        >
          <img :src="coin.image" :alt="coin.name" class="m-coin-avatar" />
          <div class="m-coin-info">
            <p class="m-coin-name">{{ coin.name }}</p>
            <p class="m-coin-symbol">{{ coin.symbol }}</p>
          </div>
          <div class="m-coin-price">
            <p class="m-coin-value">${{ formatPrice(coin.price) }}</p>
            <p class="m-coin-change down">{{ coin.change_24h?.toFixed(2) }}%</p>
          </div>
        </div>
      </div>
    </section>
    
    <!-- AI Signals Section -->
    <section class="m-section">
      <div class="m-section-header">
        <h2 class="m-section-title">🤖 AI Signals</h2>
        <NuxtLink to="/analysis" class="m-section-link">View All</NuxtLink>
      </div>
      
      <div class="m-signal-list">
        <div v-for="signal in aiSignals" :key="signal.coin_id" class="m-signal-item">
          <div class="m-signal-coin">
            <img :src="signal.image" :alt="signal.name" class="m-signal-avatar" />
            <span class="m-signal-symbol">{{ signal.symbol }}</span>
          </div>
          <div class="m-signal-score">
            <AsiGauge :score="signal.asi_score" :size="48" />
          </div>
          <span 
            class="m-signal-badge"
            :class="getSignalClass(signal.signal)"
          >
            {{ signal.signal }}
          </span>
        </div>
      </div>
    </section>
    
    <!-- Bottom padding for nav bar -->
    <div class="m-bottom-spacer"></div>
  </div>
</template>

<script setup lang="ts">
const router = useRouter()

// Mock data
const stats = ref([
  { label: 'Market Cap', value: '$3.2T', change: 2.5 },
  { label: 'BTC Dom', value: '52.3%', change: -0.3 },
  { label: 'Fear & Greed', value: '72', change: 5 },
  { label: '24h Volume', value: '$142B', change: 8.2 },
])

const topGainers = ref([
  { coin_id: 'solana', symbol: 'SOL', name: 'Solana', image: 'https://assets.coingecko.com/coins/images/4128/small/solana.png', price: 185, change_24h: 12.5 },
  { coin_id: 'avalanche', symbol: 'AVAX', name: 'Avalanche', image: 'https://assets.coingecko.com/coins/images/12559/small/Avalanche_Circle_RedWhite_Trans.png', price: 42, change_24h: 8.3 },
  { coin_id: 'chainlink', symbol: 'LINK', name: 'Chainlink', image: 'https://assets.coingecko.com/coins/images/877/small/chainlink-new-logo.png', price: 18.5, change_24h: 6.2 },
])

const topLosers = ref([
  { coin_id: 'dogecoin', symbol: 'DOGE', name: 'Dogecoin', image: 'https://assets.coingecko.com/coins/images/5/small/dogecoin.png', price: 0.32, change_24h: -4.2 },
  { coin_id: 'shiba-inu', symbol: 'SHIB', name: 'Shiba Inu', image: 'https://assets.coingecko.com/coins/images/11939/small/shiba.png', price: 0.000022, change_24h: -3.8 },
])

const aiSignals = ref([
  { coin_id: 'bitcoin', symbol: 'BTC', name: 'Bitcoin', image: 'https://assets.coingecko.com/coins/images/1/small/bitcoin.png', asi_score: 72, signal: 'BUY' },
  { coin_id: 'ethereum', symbol: 'ETH', name: 'Ethereum', image: 'https://assets.coingecko.com/coins/images/279/small/ethereum.png', asi_score: 58, signal: 'HOLD' },
  { coin_id: 'solana', symbol: 'SOL', name: 'Solana', image: 'https://assets.coingecko.com/coins/images/4128/small/solana.png', asi_score: 78, signal: 'STRONG_BUY' },
])

const openCoin = (coinId: string) => {
  router.push(`/coin/${coinId}`)
}

const formatPrice = (price: number) => {
  if (price >= 1) return price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
  return price.toFixed(6)
}

const getSignalClass = (signal: string) => {
  if (signal?.includes('BUY')) return 'buy'
  if (signal?.includes('SELL')) return 'sell'
  return 'hold'
}
</script>

<style scoped>
.mobile-dashboard {
  padding: 1rem;
  padding-bottom: 80px;
}

.m-hero {
  text-align: center;
  padding: 1.5rem 0;
}

.m-hero-title {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.m-hero-subtitle {
  color: #9ca3af;
  font-size: 0.875rem;
}

/* Stats Scroll */
.m-stats-scroll {
  overflow-x: auto;
  margin: 0 -1rem;
  padding: 0 1rem;
  scrollbar-width: none;
}

.m-stats-scroll::-webkit-scrollbar {
  display: none;
}

.m-stats-container {
  display: flex;
  gap: 0.75rem;
  padding-bottom: 0.5rem;
}

.m-stat-card {
  flex: 0 0 auto;
  min-width: 120px;
  padding: 1rem;
  background: rgba(20, 28, 43, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 1rem;
}

.m-stat-label {
  font-size: 0.75rem;
  color: #9ca3af;
  margin-bottom: 0.25rem;
}

.m-stat-value {
  font-size: 1.125rem;
  font-weight: 700;
}

.m-stat-change {
  font-size: 0.75rem;
  margin-top: 0.25rem;
}

.m-stat-change.up { color: #22c55e; }
.m-stat-change.down { color: #ef4444; }

/* Sections */
.m-section {
  margin-top: 1.5rem;
}

.m-section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.m-section-title {
  font-size: 1rem;
  font-weight: 600;
}

.m-section-link {
  color: #38efeb;
  font-size: 0.75rem;
  text-decoration: none;
}

/* Coin List */
.m-coin-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.m-coin-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: rgba(20, 28, 43, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 0.75rem;
  cursor: pointer;
  transition: background 0.2s;
}

.m-coin-item:active {
  background: rgba(20, 28, 43, 0.9);
}

.m-coin-avatar {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
}

.m-coin-info {
  flex: 1;
}

.m-coin-name {
  font-weight: 500;
  font-size: 0.875rem;
}

.m-coin-symbol {
  color: #6b7280;
  font-size: 0.75rem;
}

.m-coin-price {
  text-align: right;
}

.m-coin-value {
  font-weight: 600;
  font-size: 0.875rem;
  font-family: 'SF Mono', monospace;
}

.m-coin-change {
  font-size: 0.75rem;
}

.m-coin-change.up { color: #22c55e; }
.m-coin-change.down { color: #ef4444; }

/* AI Signals */
.m-signal-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.m-signal-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem;
  background: rgba(20, 28, 43, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 0.75rem;
}

.m-signal-coin {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.m-signal-avatar {
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
}

.m-signal-symbol {
  font-weight: 600;
}

.m-signal-badge {
  padding: 0.25rem 0.75rem;
  font-size: 0.75rem;
  font-weight: 600;
  border-radius: 9999px;
}

.m-signal-badge.buy {
  background: rgba(34, 197, 94, 0.2);
  color: #22c55e;
}

.m-signal-badge.sell {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.m-signal-badge.hold {
  background: rgba(249, 115, 22, 0.2);
  color: #f97316;
}

.m-bottom-spacer {
  height: 20px;
}
</style>
