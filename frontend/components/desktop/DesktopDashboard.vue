<template>
  <div class="d-dashboard">
    <!-- Stats Cards Row (WordPress Style) -->
    <section class="d-section">
      <div class="d-stats-grid">
        <!-- Total Market Cap -->
        <div class="d-stat-card">
          <div class="d-stat-header">
            <span class="d-stat-label">TOTAL MARKET CAP</span>
            <span class="d-stat-change" :class="avgChange >= 0 ? 'up' : 'down'">
              {{ avgChange >= 0 ? '▲' : '▼' }} {{ Math.abs(avgChange).toFixed(2) }}%
            </span>
          </div>
          <div class="d-stat-value">{{ formatCurrency(totalMarketCap) }}</div>
          <div class="d-stat-sparkline">
            <svg viewBox="0 0 120 40" preserveAspectRatio="none">
              <defs>
                <linearGradient id="sparkGreen" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" stop-color="rgba(34, 197, 94, 0.4)" />
                  <stop offset="100%" stop-color="rgba(34, 197, 94, 0)" />
                </linearGradient>
              </defs>
              <path d="M0,35 C8,32 16,28 24,25 C32,22 40,30 48,24 C56,18 64,22 72,16 C80,10 88,15 96,12 C104,9 112,14 120,10 L120,40 L0,40 Z" fill="url(#sparkGreen)" />
              <path d="M0,35 C8,32 16,28 24,25 C32,22 40,30 48,24 C56,18 64,22 72,16 C80,10 88,15 96,12 C104,9 112,14 120,10" fill="none" stroke="#22c55e" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </div>
        </div>

        <!-- BTC Dominance -->
        <div class="d-stat-card">
          <div class="d-stat-header">
            <span class="d-stat-label">BTC DOMINANCE</span>
            <span class="d-stat-change" :class="btcDomChange >= 0 ? 'up' : 'down'">
              {{ btcDomChange >= 0 ? '▲' : '▼' }} {{ Math.abs(btcDomChange).toFixed(2) }}%
            </span>
          </div>
          <div class="d-stat-value">{{ btcDominance.toFixed(1) }}%</div>
          <div class="d-stat-progress">
            <div class="d-stat-bar" :style="{ width: btcDominance + '%' }"></div>
          </div>
        </div>

        <!-- Fear & Greed with Gauge -->
        <div class="d-stat-card d-stat-card--gauge">
          <div class="d-stat-header">
            <span class="d-stat-label">FEAR & GREED INDEX</span>
          </div>
          <div class="d-gauge-wrapper">
            <svg viewBox="0 0 100 60" class="d-gauge-svg">
              <defs>
                <linearGradient id="gaugeGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stop-color="#ef4444" />
                  <stop offset="25%" stop-color="#f97316" />
                  <stop offset="50%" stop-color="#eab308" />
                  <stop offset="75%" stop-color="#84cc16" />
                  <stop offset="100%" stop-color="#22c55e" />
                </linearGradient>
              </defs>
              <path d="M 10 50 A 40 40 0 0 1 90 50" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="8" stroke-linecap="round"/>
              <path d="M 10 50 A 40 40 0 0 1 90 50" fill="none" stroke="url(#gaugeGrad)" stroke-width="8" stroke-linecap="round"/>
              <line :x1="50" :y1="50" :x2="50 + 28 * Math.cos((180 - fearGreedValue * 1.8) * Math.PI / 180)" :y2="50 - 28 * Math.sin((180 - fearGreedValue * 1.8) * Math.PI / 180)" stroke="#fff" stroke-width="2" stroke-linecap="round"/>
              <circle cx="50" cy="50" r="4" fill="#1a1f2e" stroke="#fff" stroke-width="2"/>
            </svg>
            <div class="d-gauge-value">
              <span class="d-gauge-number" :class="fearGreedClass">{{ fearGreedValue }}</span>
              <span class="d-gauge-label">{{ fearGreedLabel }}</span>
            </div>
          </div>
        </div>

        <!-- 24H Volume -->
        <div class="d-stat-card">
          <div class="d-stat-header">
            <span class="d-stat-label">24H VOLUME</span>
          </div>
          <div class="d-stat-value">{{ formatCurrency(total24hVolume) }}</div>
          <div class="d-stat-sparkline">
            <svg viewBox="0 0 120 40" preserveAspectRatio="none">
              <defs>
                <linearGradient id="sparkCyan" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" stop-color="rgba(56, 189, 248, 0.4)" />
                  <stop offset="100%" stop-color="rgba(56, 189, 248, 0)" />
                </linearGradient>
              </defs>
              <path d="M0,28 C10,22 20,30 30,18 C40,6 50,20 60,14 C70,8 80,25 90,15 C100,5 110,18 120,12 L120,40 L0,40 Z" fill="url(#sparkCyan)" />
              <path d="M0,28 C10,22 20,30 30,18 C40,6 50,20 60,14 C70,8 80,25 90,15 C100,5 110,18 120,12" fill="none" stroke="#38bdf8" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </div>
        </div>
      </div>
    </section>

    <!-- Main Content Grid -->
    <div class="d-content-grid">
      <!-- Coins Table -->
      <section class="d-main-section">
        <div class="d-section-header">
          <h2 class="d-section-title">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#22C55E" stroke-width="2"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></svg>
            Top Cryptocurrencies
          </h2>
          <span class="d-section-note">ASI = AI Sentiment Index</span>
        </div>

        <div class="d-table-card">
          <table class="d-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Coin</th>
                <th class="text-right">Price</th>
                <th class="text-right">24h</th>
                <th class="text-right">7d</th>
                <th class="text-right">Market Cap</th>
                <th>ASI</th>
                <th>Signal</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(coin, idx) in topCoins" :key="coin.id" @click="navigateTo(`/coin/${coin.id}`)">
                <td><span class="d-rank">{{ idx + 1 }}</span></td>
                <td>
                  <div class="d-coin-cell">
                    <img :src="coin.image" class="d-coin-avatar" />
                    <div>
                      <span class="d-coin-name">{{ coin.symbol }}</span>
                      <span class="d-coin-symbol">{{ coin.name }}</span>
                    </div>
                  </div>
                </td>
                <td class="text-right font-mono">{{ formatPrice(coin.price) }}</td>
                <td class="text-right" :class="coin.change24h >= 0 ? 'text-success' : 'text-danger'">
                  {{ coin.change24h >= 0 ? '+' : '' }}{{ coin.change24h.toFixed(2) }}%
                </td>
                <td class="text-right" :class="coin.change7d >= 0 ? 'text-success' : 'text-danger'">
                  {{ coin.change7d >= 0 ? '+' : '' }}{{ coin.change7d.toFixed(2) }}%
                </td>
                <td class="text-right font-mono">{{ formatMarketCap(coin.marketCap) }}</td>
                <td>
                  <div class="d-asi-cell">
                    <div class="d-asi-bar"><div class="d-asi-fill" :class="getAsiClass(coin.asi)" :style="{ width: coin.asi + '%' }"></div></div>
                    <span class="d-asi-value" :class="getAsiClass(coin.asi)">{{ coin.asi }}</span>
                  </div>
                </td>
                <td><span class="d-signal" :class="'signal-' + coin.signal.toLowerCase()">{{ coin.signal }}</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- Sidebar -->
      <aside class="d-sidebar">
        <!-- AI Signals Summary -->
        <div class="d-sidebar-card">
          <h3 class="d-sidebar-title">📊 AI Market Signals</h3>
          <div class="d-signals-summary">
            <div class="d-signal-stat buy"><span class="d-signal-count">{{ signalCounts.buy }}</span><span class="d-signal-label">Buy</span></div>
            <div class="d-signal-stat hold"><span class="d-signal-count">{{ signalCounts.hold }}</span><span class="d-signal-label">Neutral</span></div>
            <div class="d-signal-stat sell"><span class="d-signal-count">{{ signalCounts.sell }}</span><span class="d-signal-label">Sell</span></div>
          </div>
        </div>

        <!-- Trending Coins -->
        <div class="d-sidebar-card">
          <h3 class="d-sidebar-title">🔥 Trending</h3>
          <div class="d-trending-list">
            <div v-for="coin in trendingCoins" :key="coin.id" class="d-trending-item">
              <img :src="coin.image" class="d-trending-avatar" />
              <div class="d-trending-info">
                <span class="d-trending-name">{{ coin.symbol }}</span>
                <span class="d-trending-change" :class="coin.change >= 0 ? 'up' : 'down'">{{ coin.change >= 0 ? '+' : '' }}{{ coin.change.toFixed(1) }}%</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Whale Activity -->
        <div class="d-sidebar-card">
          <h3 class="d-sidebar-title">🐋 Whale Activity</h3>
          <div class="d-whale-list">
            <div v-for="tx in whaleTransactions" :key="tx.id" class="d-whale-item">
              <span class="d-whale-type" :class="tx.type">{{ tx.type === 'buy' ? '🟢' : '🔴' }}</span>
              <div class="d-whale-info">
                <span class="d-whale-amount">{{ tx.amount }} {{ tx.symbol }}</span>
                <span class="d-whale-value">${{ tx.value }}</span>
              </div>
              <span class="d-whale-time">{{ tx.time }}</span>
            </div>
          </div>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
// Stats data
const totalMarketCap = ref(3200000000000)
const avgChange = ref(2.5)
const btcDominance = ref(52.3)
const btcDomChange = ref(-0.3)
const fearGreedValue = ref(72)
const total24hVolume = ref(142000000000)

const fearGreedLabel = computed(() => {
  if (fearGreedValue.value >= 75) return 'Extreme Greed'
  if (fearGreedValue.value >= 55) return 'Greed'
  if (fearGreedValue.value >= 45) return 'Neutral'
  if (fearGreedValue.value >= 25) return 'Fear'
  return 'Extreme Fear'
})

const fearGreedClass = computed(() => {
  if (fearGreedValue.value >= 55) return 'greed'
  if (fearGreedValue.value >= 45) return 'neutral'
  return 'fear'
})

// Coins data
const topCoins = ref([
  { id: 'bitcoin', symbol: 'BTC', name: 'Bitcoin', image: 'https://assets.coingecko.com/coins/images/1/small/bitcoin.png', price: 98500, change24h: 2.4, change7d: 5.8, marketCap: 1900000000000, asi: 78, signal: 'BUY' },
  { id: 'ethereum', symbol: 'ETH', name: 'Ethereum', image: 'https://assets.coingecko.com/coins/images/279/small/ethereum.png', price: 3450, change24h: 1.8, change7d: 4.2, marketCap: 415000000000, asi: 65, signal: 'HOLD' },
  { id: 'solana', symbol: 'SOL', name: 'Solana', image: 'https://assets.coingecko.com/coins/images/4128/small/solana.png', price: 185, change24h: 5.2, change7d: 12.4, marketCap: 82000000000, asi: 82, signal: 'BUY' },
  { id: 'xrp', symbol: 'XRP', name: 'XRP', image: 'https://assets.coingecko.com/coins/images/44/small/xrp-symbol-white-128.png', price: 2.35, change24h: -1.2, change7d: 8.5, marketCap: 135000000000, asi: 58, signal: 'HOLD' },
  { id: 'cardano', symbol: 'ADA', name: 'Cardano', image: 'https://assets.coingecko.com/coins/images/975/small/cardano.png', price: 0.98, change24h: 3.1, change7d: 15.2, marketCap: 34000000000, asi: 71, signal: 'BUY' },
])

const signalCounts = computed(() => ({
  buy: topCoins.value.filter(c => c.signal === 'BUY').length * 25,
  hold: topCoins.value.filter(c => c.signal === 'HOLD').length * 18,
  sell: topCoins.value.filter(c => c.signal === 'SELL').length * 7,
}))

const trendingCoins = ref([
  { id: 'pepe', symbol: 'PEPE', image: 'https://assets.coingecko.com/coins/images/29850/small/pepe.png', change: 45.2 },
  { id: 'bonk', symbol: 'BONK', image: 'https://assets.coingecko.com/coins/images/28600/small/bonk.jpg', change: 28.5 },
  { id: 'wif', symbol: 'WIF', image: 'https://assets.coingecko.com/coins/images/33566/small/dogwifhat.jpg', change: 18.3 },
])

const whaleTransactions = ref([
  { id: 1, type: 'buy', symbol: 'BTC', amount: '500', value: '49.2M', time: '2h' },
  { id: 2, type: 'sell', symbol: 'ETH', amount: '15K', value: '51.7M', time: '4h' },
  { id: 3, type: 'buy', symbol: 'SOL', amount: '250K', value: '46.2M', time: '5h' },
])

const formatCurrency = (n: number) => '$' + (n >= 1e12 ? (n/1e12).toFixed(2) + 'T' : n >= 1e9 ? (n/1e9).toFixed(2) + 'B' : n.toLocaleString())
const formatPrice = (p: number) => '$' + (p >= 1 ? p.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : p.toFixed(6))
const formatMarketCap = (n: number) => n >= 1e12 ? '$' + (n/1e12).toFixed(2) + 'T' : '$' + (n/1e9).toFixed(1) + 'B'
const getAsiClass = (v: number) => v >= 60 ? 'positive' : v <= 40 ? 'negative' : 'neutral'
</script>

<style scoped>
.d-dashboard { padding: 24px 0; }
.d-section { margin-bottom: 24px; }
.d-section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.d-section-title { display: flex; align-items: center; gap: 8px; font-size: 20px; font-weight: 600; margin: 0; color: var(--text-primary); }
.d-section-note { font-size: 12px; color: var(--text-muted); }

/* Stats Grid */
.d-stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
.d-stat-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 16px; padding: 20px; transition: all 0.3s; }
.d-stat-card:hover { border-color: var(--border-hover); transform: translateY(-2px); }
.d-stat-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.d-stat-label { font-size: 11px; font-weight: 600; color: var(--text-muted); letter-spacing: 0.5px; }
.d-stat-change { font-size: 12px; font-weight: 600; }
.d-stat-change.up { color: #22c55e; }
.d-stat-change.down { color: #ef4444; }
.d-stat-value { font-size: 28px; font-weight: 700; color: var(--text-primary); margin-bottom: 12px; }
.d-stat-sparkline { height: 40px; }
.d-stat-sparkline svg { width: 100%; height: 100%; }
.d-stat-progress { height: 6px; background: rgba(255,255,255,0.1); border-radius: 3px; overflow: hidden; }
.d-stat-bar { height: 100%; background: linear-gradient(90deg, #f97316, #fb923c); border-radius: 3px; transition: width 0.5s; }

/* Gauge */
.d-stat-card--gauge { display: flex; flex-direction: column; }
.d-gauge-wrapper { display: flex; flex-direction: column; align-items: center; flex: 1; }
.d-gauge-svg { width: 100%; max-width: 140px; }
.d-gauge-value { text-align: center; margin-top: -10px; }
.d-gauge-number { font-size: 32px; font-weight: 700; display: block; }
.d-gauge-number.greed { color: #22c55e; }
.d-gauge-number.neutral { color: #eab308; }
.d-gauge-number.fear { color: #ef4444; }
.d-gauge-label { font-size: 12px; color: var(--text-muted); }

/* Content Grid */
.d-content-grid { display: grid; grid-template-columns: 1fr 360px; gap: 24px; }
.d-table-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 16px; overflow: hidden; }
.d-table { width: 100%; border-collapse: collapse; }
.d-table th, .d-table td { padding: 14px 16px; text-align: left; }
.d-table th { font-size: 12px; font-weight: 600; color: var(--text-muted); border-bottom: 1px solid var(--border); background: var(--bg-secondary); }
.d-table tbody tr { border-bottom: 1px solid var(--border); cursor: pointer; transition: background 0.2s; }
.d-table tbody tr:hover { background: var(--bg-card-hover); }
.d-rank { display: inline-flex; align-items: center; justify-content: center; width: 24px; height: 24px; background: rgba(56, 239, 235, 0.15); border-radius: 50%; font-size: 11px; font-weight: 600; color: #38efeb; }
.d-coin-cell { display: flex; align-items: center; gap: 12px; }
.d-coin-avatar { width: 32px; height: 32px; border-radius: 50%; }
.d-coin-name { display: block; font-weight: 600; color: var(--text-primary); }
.d-coin-symbol { display: block; font-size: 12px; color: var(--text-muted); }
.text-right { text-align: right; }
.text-success { color: #22c55e; }
.text-danger { color: #ef4444; }
.font-mono { font-family: 'SF Mono', Monaco, monospace; }

/* ASI Bar */
.d-asi-cell { display: flex; align-items: center; gap: 8px; }
.d-asi-bar { width: 60px; height: 6px; background: rgba(255,255,255,0.1); border-radius: 3px; overflow: hidden; }
.d-asi-fill { height: 100%; border-radius: 3px; transition: width 0.3s; }
.d-asi-fill.positive { background: linear-gradient(90deg, #22c55e, #4ade80); }
.d-asi-fill.neutral { background: linear-gradient(90deg, #eab308, #fbbf24); }
.d-asi-fill.negative { background: linear-gradient(90deg, #ef4444, #f87171); }
.d-asi-value { font-size: 12px; font-weight: 600; min-width: 24px; }
.d-asi-value.positive { color: #22c55e; }
.d-asi-value.neutral { color: #eab308; }
.d-asi-value.negative { color: #ef4444; }

/* Signal Badge */
.d-signal { padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 600; text-transform: uppercase; }
.signal-buy { background: rgba(34, 197, 94, 0.15); color: #22c55e; }
.signal-hold { background: rgba(234, 179, 8, 0.15); color: #eab308; }
.signal-sell { background: rgba(239, 68, 68, 0.15); color: #ef4444; }

/* Sidebar */
.d-sidebar { display: flex; flex-direction: column; gap: 16px; }
.d-sidebar-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 16px; padding: 20px; }
.d-sidebar-title { font-size: 16px; font-weight: 600; margin: 0 0 16px; color: var(--text-primary); }
.d-signals-summary { display: flex; justify-content: space-around; text-align: center; }
.d-signal-stat { padding: 12px; }
.d-signal-count { display: block; font-size: 28px; font-weight: 700; }
.d-signal-stat.buy .d-signal-count { color: #22c55e; }
.d-signal-stat.hold .d-signal-count { color: #eab308; }
.d-signal-stat.sell .d-signal-count { color: #ef4444; }
.d-signal-label { font-size: 12px; color: var(--text-muted); }
.d-trending-list { display: flex; flex-direction: column; gap: 12px; }
.d-trending-item { display: flex; align-items: center; gap: 12px; }
.d-trending-avatar { width: 32px; height: 32px; border-radius: 50%; }
.d-trending-info { flex: 1; }
.d-trending-name { font-weight: 600; display: block; color: var(--text-primary); }
.d-trending-change { font-size: 12px; font-weight: 600; }
.d-trending-change.up { color: #22c55e; }
.d-trending-change.down { color: #ef4444; }
.d-whale-list { display: flex; flex-direction: column; gap: 12px; }
.d-whale-item { display: flex; align-items: center; gap: 10px; padding: 10px; background: rgba(255,255,255,0.04); border-radius: 10px; }
.d-whale-type { font-size: 16px; }
.d-whale-info { flex: 1; }
.d-whale-amount { display: block; font-weight: 600; font-size: 13px; color: var(--text-primary); }
.d-whale-value { font-size: 11px; color: var(--text-muted); }
.d-whale-time { font-size: 11px; color: var(--text-dimmed); }
</style>
