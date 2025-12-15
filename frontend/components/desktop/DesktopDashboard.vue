<template>
  <div class="d-dashboard">
    <!-- Hero Section -->
    <section class="d-hero">
      <div class="d-hero-content">
        <h1 class="d-hero-title">
          <span class="gradient-text">AI-Powered</span> Crypto Analysis
        </h1>
        <p class="d-hero-subtitle">
          Real-time market data, sentiment analysis, and on-chain signals powered by advanced AI.
        </p>
      </div>
    </section>
    
    <!-- Stats Grid - Matching Mobile Style -->
    <section class="d-section">
      <div class="d-stats-grid">
        <div class="d-stat-card">
          <div class="d-stat-header">
            <span class="d-stat-label">TOTAL MARKET CAP</span>
            <span class="d-stat-change" :class="marketCapChange >= 0 ? 'up' : 'down'">
              {{ marketCapChange >= 0 ? '▲' : '▼' }} {{ Math.abs(marketCapChange).toFixed(2) }}%
            </span>
          </div>
          <div class="d-stat-value">{{ formatMarketCap(totalMarketCap) }}</div>
          <div class="d-stat-sparkline">
            <svg viewBox="0 0 200 50" preserveAspectRatio="none">
              <defs>
                <linearGradient id="dSparkGreen" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" stop-color="rgba(34, 197, 94, 0.3)" />
                  <stop offset="100%" stop-color="transparent" />
                </linearGradient>
              </defs>
              <path d="M0,40 C20,35 40,25 60,30 C80,35 100,15 120,20 C140,25 160,10 180,15 C190,17 200,12 200,12 L200,50 L0,50 Z" fill="url(#dSparkGreen)" />
              <path d="M0,40 C20,35 40,25 60,30 C80,35 100,15 120,20 C140,25 160,10 180,15 C190,17 200,12 200,12" fill="none" stroke="#22c55e" stroke-width="2.5" stroke-linecap="round"/>
            </svg>
          </div>
        </div>

        <div class="d-stat-card">
          <div class="d-stat-header">
            <span class="d-stat-label">BTC DOMINANCE</span>
            <span class="d-stat-change" :class="btcDomChange >= 0 ? 'up' : 'down'">
              {{ btcDomChange >= 0 ? '▲' : '▼' }} {{ Math.abs(btcDomChange).toFixed(2) }}%
            </span>
          </div>
          <div class="d-stat-value">{{ btcDominance.toFixed(1) }}%</div>
          <div class="d-stat-bar">
            <div class="d-stat-bar-fill" :style="{ width: btcDominance + '%' }"></div>
          </div>
        </div>

        <div class="d-stat-card d-stat-card-gauge">
          <div class="d-stat-header">
            <span class="d-stat-label">FEAR & GREED INDEX</span>
          </div>
          <div class="d-gauge-container">
            <AsiGauge :score="fearGreedValue" :size="100" />
            <div class="d-gauge-label" :class="fearGreedClass">{{ fearGreedLabel }}</div>
          </div>
        </div>

        <div class="d-stat-card">
          <div class="d-stat-header">
            <span class="d-stat-label">24H VOLUME</span>
          </div>
          <div class="d-stat-value">{{ formatMarketCap(volume24h) }}</div>
          <div class="d-stat-sparkline">
            <svg viewBox="0 0 200 50" preserveAspectRatio="none">
              <defs>
                <linearGradient id="dSparkCyan" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" stop-color="rgba(56, 189, 248, 0.3)" />
                  <stop offset="100%" stop-color="transparent" />
                </linearGradient>
              </defs>
              <path d="M0,35 C20,30 40,40 60,25 C80,10 100,30 120,20 C140,10 160,35 180,20 C190,15 200,18 200,18 L200,50 L0,50 Z" fill="url(#dSparkCyan)" />
              <path d="M0,35 C20,30 40,40 60,25 C80,10 100,30 120,20 C140,10 160,35 180,20 C190,15 200,18 200,18" fill="none" stroke="#38bdf8" stroke-width="2.5" stroke-linecap="round"/>
            </svg>
          </div>
        </div>
      </div>
    </section>

    <!-- Main Content Grid -->
    <div class="d-content-grid">
      <!-- Main Area - Top Coins Table -->
      <section class="d-main-section">
        <div class="d-section-header">
          <h2 class="d-section-title">Top Cryptocurrencies</h2>
          <NuxtLink to="/market" class="d-section-link">View All →</NuxtLink>
        </div>
        
        <div class="d-table-card">
          <table class="d-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Coin</th>
                <th class="text-right">Price</th>
                <th class="text-right">1h</th>
                <th class="text-right">24h</th>
                <th class="text-right">7d</th>
                <th class="text-right">Market Cap</th>
                <th class="text-right">ASI</th>
                <th class="text-right">Signal</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(coin, index) in topCoins" :key="coin.coin_id" @click="openCoin(coin.coin_id)">
                <td class="d-rank">{{ index + 1 }}</td>
                <td>
                  <div class="d-coin-cell">
                    <img :src="coin.image" :alt="coin.name" class="d-coin-avatar" />
                    <div>
                      <p class="d-coin-name">{{ coin.name }}</p>
                      <p class="d-coin-symbol">{{ coin.symbol }}</p>
                    </div>
                  </div>
                </td>
                <td class="text-right font-mono">${{ formatPrice(coin.price) }}</td>
                <td class="text-right" :class="coin.change_1h >= 0 ? 'text-success' : 'text-danger'">
                  {{ coin.change_1h >= 0 ? '+' : '' }}{{ coin.change_1h?.toFixed(2) }}%
                </td>
                <td class="text-right" :class="coin.change_24h >= 0 ? 'text-success' : 'text-danger'">
                  {{ coin.change_24h >= 0 ? '+' : '' }}{{ coin.change_24h?.toFixed(2) }}%
                </td>
                <td class="text-right" :class="coin.change_7d >= 0 ? 'text-success' : 'text-danger'">
                  {{ coin.change_7d >= 0 ? '+' : '' }}{{ coin.change_7d?.toFixed(2) }}%
                </td>
                <td class="text-right text-muted">${{ formatMarketCap(coin.market_cap) }}</td>
                <td class="text-right">
                  <div class="d-asi-cell">
                    <div class="d-asi-bar">
                      <div class="d-asi-fill" :class="getAsiClass(coin.asi_score)" :style="{ width: coin.asi_score + '%' }"></div>
                    </div>
                    <span class="d-asi-value" :class="getAsiClass(coin.asi_score)">{{ coin.asi_score }}</span>
                  </div>
                </td>
                <td class="text-right">
                  <span class="d-signal-badge" :class="getSignalClass(coin.signal)">{{ coin.signal }}</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
      
      <!-- Sidebar -->
      <aside class="d-sidebar">
        <!-- AI Signals Summary -->
        <div class="d-sidebar-card">
          <h3 class="d-sidebar-title">🤖 AI Market Signals</h3>
          <div class="d-signals-summary">
            <div class="d-signal-stat">
              <span class="d-signal-count buy">{{ signalCounts.buy }}</span>
              <span class="d-signal-label">Buy</span>
            </div>
            <div class="d-signal-stat">
              <span class="d-signal-count hold">{{ signalCounts.hold }}</span>
              <span class="d-signal-label">Neutral</span>
            </div>
            <div class="d-signal-stat">
              <span class="d-signal-count sell">{{ signalCounts.sell }}</span>
              <span class="d-signal-label">Sell</span>
            </div>
          </div>
          <div class="d-signal-bar">
            <div class="d-signal-fill buy" :style="{ width: (signalCounts.buy / 250 * 100) + '%' }"></div>
            <div class="d-signal-fill hold" :style="{ width: (signalCounts.hold / 250 * 100) + '%' }"></div>
            <div class="d-signal-fill sell" :style="{ width: (signalCounts.sell / 250 * 100) + '%' }"></div>
          </div>
        </div>
        
        <!-- Trending -->
        <div class="d-sidebar-card">
          <h3 class="d-sidebar-title">🔥 Trending</h3>
          <div class="d-trending-list">
            <div v-for="coin in trendingCoins" :key="coin.coin_id" class="d-trending-item" @click="openCoin(coin.coin_id)">
              <img :src="coin.image" :alt="coin.name" class="d-trending-avatar" />
              <span class="d-trending-symbol">{{ coin.symbol }}</span>
              <span class="d-trending-change" :class="coin.change_24h >= 0 ? 'up' : 'down'">
                {{ coin.change_24h >= 0 ? '+' : '' }}{{ coin.change_24h?.toFixed(1) }}%
              </span>
            </div>
          </div>
        </div>
        
        <!-- Whale Activity -->
        <div class="d-sidebar-card">
          <h3 class="d-sidebar-title">🐋 Whale Activity</h3>
          <div class="d-whale-list">
            <div v-for="tx in whaleTransactions" :key="tx.id" class="d-whale-item">
              <span class="d-whale-type" :class="tx.type">{{ tx.type === 'buy' ? '🟢' : '🔴' }}</span>
              <span class="d-whale-coin">{{ tx.symbol }}</span>
              <span class="d-whale-amount">${{ tx.value }}</span>
              <span class="d-whale-time">{{ tx.time }}</span>
            </div>
          </div>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
const router = useRouter()

// Market Stats
const totalMarketCap = ref(3200000000000)
const marketCapChange = ref(2.5)
const btcDominance = ref(52.3)
const btcDomChange = ref(-0.3)
const fearGreedValue = ref(72)
const volume24h = ref(142000000000)

const fearGreedClass = computed(() => {
  if (fearGreedValue.value >= 60) return 'greed'
  if (fearGreedValue.value <= 40) return 'fear'
  return 'neutral'
})

const fearGreedLabel = computed(() => {
  if (fearGreedValue.value >= 75) return 'Extreme Greed'
  if (fearGreedValue.value >= 60) return 'Greed'
  if (fearGreedValue.value >= 40) return 'Neutral'
  if (fearGreedValue.value >= 25) return 'Fear'
  return 'Extreme Fear'
})

// Top Coins
const topCoins = ref([
  { coin_id: 'bitcoin', symbol: 'BTC', name: 'Bitcoin', image: 'https://assets.coingecko.com/coins/images/1/small/bitcoin.png', price: 98500, change_1h: 0.3, change_24h: 2.4, change_7d: 5.8, market_cap: 1900000000000, asi_score: 72, signal: 'BUY' },
  { coin_id: 'ethereum', symbol: 'ETH', name: 'Ethereum', image: 'https://assets.coingecko.com/coins/images/279/small/ethereum.png', price: 3450, change_1h: -0.1, change_24h: 1.8, change_7d: 3.2, market_cap: 415000000000, asi_score: 58, signal: 'HOLD' },
  { coin_id: 'solana', symbol: 'SOL', name: 'Solana', image: 'https://assets.coingecko.com/coins/images/4128/small/solana.png', price: 185, change_1h: 0.8, change_24h: 5.2, change_7d: 12.4, market_cap: 82000000000, asi_score: 78, signal: 'STRONG_BUY' },
  { coin_id: 'ripple', symbol: 'XRP', name: 'XRP', image: 'https://assets.coingecko.com/coins/images/44/small/xrp-symbol-white-128.png', price: 2.35, change_1h: -0.2, change_24h: -1.2, change_7d: 8.5, market_cap: 135000000000, asi_score: 52, signal: 'HOLD' },
  { coin_id: 'cardano', symbol: 'ADA', name: 'Cardano', image: 'https://assets.coingecko.com/coins/images/975/small/cardano.png', price: 1.05, change_1h: 0.4, change_24h: 3.1, change_7d: 6.2, market_cap: 37000000000, asi_score: 65, signal: 'BUY' },
  { coin_id: 'dogecoin', symbol: 'DOGE', name: 'Dogecoin', image: 'https://assets.coingecko.com/coins/images/5/small/dogecoin.png', price: 0.32, change_1h: -0.5, change_24h: -2.1, change_7d: -4.3, market_cap: 47000000000, asi_score: 35, signal: 'SELL' },
  { coin_id: 'avalanche', symbol: 'AVAX', name: 'Avalanche', image: 'https://assets.coingecko.com/coins/images/12559/small/Avalanche_Circle_RedWhite_Trans.png', price: 42, change_1h: 0.6, change_24h: 4.5, change_7d: 9.8, market_cap: 17000000000, asi_score: 70, signal: 'BUY' },
])

const signalCounts = ref({ buy: 127, hold: 89, sell: 34 })

const trendingCoins = ref([
  { coin_id: 'solana', symbol: 'SOL', image: 'https://assets.coingecko.com/coins/images/4128/small/solana.png', change_24h: 12.5 },
  { coin_id: 'sui', symbol: 'SUI', image: 'https://assets.coingecko.com/coins/images/26375/small/sui_asset.jpeg', change_24h: 8.4 },
  { coin_id: 'render', symbol: 'RNDR', image: 'https://assets.coingecko.com/coins/images/11636/small/rndr.png', change_24h: 6.2 },
  { coin_id: 'injective', symbol: 'INJ', image: 'https://assets.coingecko.com/coins/images/12882/small/Secondary_Symbol.png', change_24h: 5.8 },
])

const whaleTransactions = ref([
  { id: 1, symbol: 'BTC', type: 'buy', value: '49.2M', time: '2h' },
  { id: 2, symbol: 'ETH', type: 'sell', value: '31.5M', time: '4h' },
  { id: 3, symbol: 'SOL', type: 'buy', value: '28.1M', time: '6h' },
])

const openCoin = (coinId: string) => {
  router.push(`/coin/${coinId}`)
}

const formatPrice = (price: number) => {
  if (price >= 1) return price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
  return price.toFixed(6)
}

const formatMarketCap = (cap: number) => {
  if (cap >= 1e12) return (cap / 1e12).toFixed(2) + 'T'
  if (cap >= 1e9) return (cap / 1e9).toFixed(2) + 'B'
  if (cap >= 1e6) return (cap / 1e6).toFixed(2) + 'M'
  return cap.toLocaleString()
}

const getAsiClass = (score: number) => {
  if (score >= 60) return 'positive'
  if (score <= 40) return 'negative'
  return 'neutral'
}

const getSignalClass = (signal: string) => {
  if (signal?.includes('BUY')) return 'buy'
  if (signal?.includes('SELL')) return 'sell'
  return 'hold'
}
</script>

<style scoped>
.d-dashboard {
  padding: 0 0 40px;
}

/* Hero */
.d-hero {
  text-align: center;
  padding: 48px 0;
  background: linear-gradient(180deg, rgba(56, 239, 235, 0.05) 0%, transparent 100%);
}

.d-hero-title {
  font-size: 48px;
  font-weight: 700;
  margin-bottom: 16px;
}

.d-hero-subtitle {
  font-size: 18px;
  color: rgba(255, 255, 255, 0.6);
  max-width: 600px;
  margin: 0 auto;
}

/* Section */
.d-section {
  margin-bottom: 32px;
}

.d-section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.d-section-title {
  font-size: 24px;
  font-weight: 700;
  margin: 0;
}

.d-section-link {
  color: #38efeb;
  text-decoration: none;
  font-size: 14px;
}

.d-section-link:hover {
  text-decoration: underline;
}

/* Stats Grid */
.d-stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.d-stat-card {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  padding: 20px;
  overflow: hidden;
}

.d-stat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.d-stat-label {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.d-stat-change {
  font-size: 12px;
  font-weight: 600;
}

.d-stat-change.up { color: #22c55e; }
.d-stat-change.down { color: #ef4444; }

.d-stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #ffffff;
  margin-bottom: 12px;
}

.d-stat-sparkline {
  height: 50px;
  margin: 0 -20px -20px;
}

.d-stat-sparkline svg {
  width: 100%;
  height: 100%;
}

.d-stat-bar {
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
}

.d-stat-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #f97316, #fb923c);
  border-radius: 4px;
}

/* Gauge */
.d-stat-card-gauge {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.d-gauge-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.d-gauge-label {
  font-size: 14px;
  font-weight: 600;
}

.d-gauge-label.greed { color: #22c55e; }
.d-gauge-label.fear { color: #ef4444; }
.d-gauge-label.neutral { color: #f97316; }

/* Content Grid */
.d-content-grid {
  display: grid;
  grid-template-columns: 1fr 360px;
  gap: 24px;
}

/* Table */
.d-table-card {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  overflow: hidden;
}

.d-table {
  width: 100%;
  border-collapse: collapse;
}

.d-table th,
.d-table td {
  padding: 14px 16px;
  text-align: left;
}

.d-table th {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  font-weight: 500;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  text-transform: uppercase;
}

.d-table tbody tr {
  cursor: pointer;
  transition: background 0.2s;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
}

.d-table tbody tr:hover {
  background: rgba(255, 255, 255, 0.04);
}

.d-rank {
  color: rgba(255, 255, 255, 0.4);
  font-weight: 500;
}

.d-coin-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.d-coin-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
}

.d-coin-name {
  font-weight: 600;
  margin: 0;
}

.d-coin-symbol {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  margin: 0;
}

.text-right { text-align: right; }
.text-success { color: #22c55e; }
.text-danger { color: #ef4444; }
.text-muted { color: rgba(255, 255, 255, 0.5); }
.font-mono { font-family: 'SF Mono', monospace; }

/* ASI Cell */
.d-asi-cell {
  display: flex;
  align-items: center;
  gap: 8px;
  justify-content: flex-end;
}

.d-asi-bar {
  width: 50px;
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
}

.d-asi-fill {
  height: 100%;
  border-radius: 3px;
}

.d-asi-fill.positive { background: linear-gradient(90deg, #22c55e, #4ade80); }
.d-asi-fill.negative { background: linear-gradient(90deg, #ef4444, #f87171); }
.d-asi-fill.neutral { background: linear-gradient(90deg, #f97316, #fb923c); }

.d-asi-value {
  font-size: 13px;
  font-weight: 600;
  min-width: 24px;
}

.d-asi-value.positive { color: #22c55e; }
.d-asi-value.negative { color: #ef4444; }
.d-asi-value.neutral { color: #f97316; }

/* Signal Badge */
.d-signal-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
}

.d-signal-badge.buy {
  background: rgba(34, 197, 94, 0.2);
  color: #22c55e;
}

.d-signal-badge.sell {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.d-signal-badge.hold {
  background: rgba(249, 115, 22, 0.2);
  color: #f97316;
}

/* Sidebar */
.d-sidebar {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.d-sidebar-card {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  padding: 20px;
}

.d-sidebar-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 16px;
}

/* Signals Summary */
.d-signals-summary {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
}

.d-signal-stat {
  text-align: center;
}

.d-signal-count {
  display: block;
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 4px;
}

.d-signal-count.buy { color: #22c55e; }
.d-signal-count.hold { color: #f97316; }
.d-signal-count.sell { color: #ef4444; }

.d-signal-label {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
}

.d-signal-bar {
  height: 8px;
  border-radius: 4px;
  display: flex;
  overflow: hidden;
}

.d-signal-fill {
  height: 100%;
}

.d-signal-fill.buy { background: #22c55e; }
.d-signal-fill.hold { background: #f97316; }
.d-signal-fill.sell { background: #ef4444; }

/* Trending */
.d-trending-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.d-trending-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px;
  border-radius: 10px;
  cursor: pointer;
  transition: background 0.2s;
}

.d-trending-item:hover {
  background: rgba(255, 255, 255, 0.06);
}

.d-trending-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
}

.d-trending-symbol {
  flex: 1;
  font-weight: 600;
}

.d-trending-change {
  font-size: 13px;
  font-weight: 600;
}

.d-trending-change.up { color: #22c55e; }
.d-trending-change.down { color: #ef4444; }

/* Whale */
.d-whale-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.d-whale-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}

.d-whale-type {
  font-size: 12px;
}

.d-whale-coin {
  font-weight: 600;
  flex: 1;
}

.d-whale-amount {
  color: rgba(255, 255, 255, 0.7);
}

.d-whale-time {
  color: rgba(255, 255, 255, 0.4);
  font-size: 11px;
}

@media (max-width: 1200px) {
  .d-stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .d-content-grid {
    grid-template-columns: 1fr;
  }
}
</style>
