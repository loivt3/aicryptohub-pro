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
/* Dashboard Styles - WordPress AI Hub Pro Design */
.d-dashboard { 
  padding: var(--aihub-spacing-xl) 0; 
  background: var(--aihub-bg-primary);
  min-height: 100vh;
}

.d-section { margin-bottom: var(--aihub-spacing-xl); }

.d-section-header { 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  margin-bottom: 20px; 
}

.d-section-title { 
  display: flex; 
  align-items: center; 
  gap: 10px; 
  font-size: 22px; 
  font-weight: 700; 
  margin: 0; 
  color: #ffffff; 
}

.d-section-note { 
  font-size: 13px; 
  color: rgba(255, 255, 255, 0.4); 
}

/* Stats Grid - Premium Cards */
.d-stats-grid { 
  display: grid; 
  grid-template-columns: repeat(4, 1fr); 
  gap: 20px; 
}

.d-stat-card { 
  background: var(--aihub-bg-card); 
  border: 1px solid rgba(255, 255, 255, 0.08); 
  border-radius: 20px; 
  padding: 24px; 
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.d-stat-card:hover { 
  border-color: rgba(0, 212, 255, 0.4);
  box-shadow: 0 0 30px rgba(0, 212, 255, 0.15);
  transform: translateY(-4px); 
}

.d-stat-header { 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  margin-bottom: 12px; 
}

.d-stat-label { 
  font-size: 11px; 
  font-weight: 600; 
  color: rgba(255, 255, 255, 0.5); 
  letter-spacing: 1px; 
}

.d-stat-change { 
  font-size: 13px; 
  font-weight: 700;
  font-family: 'SF Mono', 'Roboto Mono', monospace;
}

.d-stat-change.up { color: #00ff88; }
.d-stat-change.down { color: #ff4757; }

.d-stat-value { 
  font-size: 32px; 
  font-weight: 800; 
  font-family: 'SF Mono', 'Roboto Mono', monospace;
  color: #ffffff; 
  margin-bottom: 16px;
  background: linear-gradient(135deg, #ffffff, #00d4ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.d-stat-sparkline { height: 48px; }
.d-stat-sparkline svg { width: 100%; height: 100%; }

.d-stat-progress { 
  height: 8px; 
  background: rgba(255,255,255,0.08); 
  border-radius: 4px; 
  overflow: hidden; 
}

.d-stat-bar { 
  height: 100%; 
  background: linear-gradient(90deg, #00d4ff, #0066ff); 
  border-radius: 4px; 
  transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
}

/* Gauge - Premium */
.d-stat-card--gauge { display: flex; flex-direction: column; }
.d-gauge-wrapper { display: flex; flex-direction: column; align-items: center; flex: 1; }
.d-gauge-svg { width: 100%; max-width: 160px; }
.d-gauge-value { text-align: center; margin-top: -8px; }

.d-gauge-number { 
  font-size: 40px; 
  font-weight: 800; 
  font-family: 'SF Mono', 'Roboto Mono', monospace;
  display: block; 
}

.d-gauge-number.greed { 
  color: #00ff88; 
  text-shadow: 0 0 30px rgba(0, 255, 136, 0.5);
}

.d-gauge-number.neutral { color: #ffa502; }

.d-gauge-number.fear { 
  color: #ff4757; 
  text-shadow: 0 0 30px rgba(255, 71, 87, 0.5);
}

.d-gauge-label { font-size: 13px; color: rgba(255, 255, 255, 0.5); font-weight: 500; }

/* Content Grid */
.d-content-grid { display: grid; grid-template-columns: 1fr 380px; gap: 28px; }

.d-table-card { 
  background: var(--aihub-bg-card); 
  border: 1px solid rgba(255, 255, 255, 0.08); 
  border-radius: 20px; 
  overflow: hidden;
}

.d-table { width: 100%; border-collapse: collapse; }

.d-table th, .d-table td { padding: 16px 20px; text-align: left; }

.d-table th { 
  font-size: 12px; 
  font-weight: 600; 
  color: rgba(255, 255, 255, 0.5); 
  border-bottom: 1px solid rgba(255, 255, 255, 0.06); 
  background: var(--aihub-bg-secondary);
  letter-spacing: 0.5px;
}

.d-table tbody tr { 
  border-bottom: 1px solid rgba(255, 255, 255, 0.04); 
  cursor: pointer; 
  transition: all 0.2s ease;
}

.d-table tbody tr:hover { 
  background: rgba(0, 212, 255, 0.05);
}

.d-rank { 
  display: inline-flex; 
  align-items: center; 
  justify-content: center; 
  width: 28px; 
  height: 28px; 
  background: rgba(0, 212, 255, 0.15); 
  border-radius: 50%; 
  font-size: 12px; 
  font-weight: 700;
  font-family: 'SF Mono', 'Roboto Mono', monospace; 
  color: #00d4ff; 
}

.d-coin-cell { display: flex; align-items: center; gap: 14px; }

.d-coin-avatar { 
  width: 40px; 
  height: 40px; 
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.1);
}

.d-coin-name { display: block; font-weight: 700; font-size: 15px; color: #ffffff; }
.d-coin-symbol { display: block; font-size: 12px; color: rgba(255, 255, 255, 0.5); }

.text-right { text-align: right; }
.text-success { color: #00ff88; font-weight: 600; }
.text-danger { color: #ff4757; font-weight: 600; }
.font-mono { font-family: 'SF Mono', 'Roboto Mono', monospace; }

/* ASI Bar - Premium */
.d-asi-cell { display: flex; align-items: center; gap: 10px; }

.d-asi-bar { 
  width: 70px; 
  height: 8px; 
  background: rgba(255,255,255,0.08); 
  border-radius: 4px; 
  overflow: hidden; 
}

.d-asi-fill { 
  height: 100%; 
  border-radius: 4px; 
  transition: width 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.d-asi-fill.positive { background: linear-gradient(90deg, #00ff88, #00d4ff); }
.d-asi-fill.neutral { background: linear-gradient(90deg, #ffa502, #ff7f50); }
.d-asi-fill.negative { background: linear-gradient(90deg, #ff4757, #ff6b81); }

.d-asi-value { 
  font-size: 13px; 
  font-weight: 700; 
  font-family: 'SF Mono', 'Roboto Mono', monospace;
  min-width: 28px; 
}

.d-asi-value.positive { color: #00ff88; }
.d-asi-value.neutral { color: #ffa502; }
.d-asi-value.negative { color: #ff4757; }

/* Signal Badge - Premium */
.d-signal { 
  padding: 6px 14px; 
  border-radius: 20px; 
  font-size: 11px; 
  font-weight: 700; 
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.signal-buy { 
  background: rgba(0, 255, 136, 0.15); 
  color: #00ff88;
  border: 1px solid rgba(0, 255, 136, 0.3);
}

.signal-hold { 
  background: rgba(255, 165, 2, 0.15); 
  color: #ffa502;
  border: 1px solid rgba(255, 165, 2, 0.3);
}

.signal-sell { 
  background: rgba(255, 71, 87, 0.15); 
  color: #ff4757;
  border: 1px solid rgba(255, 71, 87, 0.3);
}

/* Sidebar - Premium */
.d-sidebar { display: flex; flex-direction: column; gap: 20px; }

.d-sidebar-card { 
  background: var(--aihub-bg-card); 
  border: 1px solid rgba(255, 255, 255, 0.08); 
  border-radius: 20px; 
  padding: 24px;
  transition: all 0.3s ease;
}

.d-sidebar-card:hover {
  border-color: rgba(168, 85, 247, 0.3);
  box-shadow: 0 0 20px rgba(168, 85, 247, 0.1);
}

.d-sidebar-title { 
  font-size: 18px; 
  font-weight: 700; 
  margin: 0 0 20px; 
  color: #ffffff; 
}

.d-signals-summary { display: flex; justify-content: space-around; text-align: center; }
.d-signal-stat { padding: 14px; }

.d-signal-count { 
  display: block; 
  font-size: 36px; 
  font-weight: 800;
  font-family: 'SF Mono', 'Roboto Mono', monospace;
}

.d-signal-stat.buy .d-signal-count { 
  color: #00ff88;
  text-shadow: 0 0 20px rgba(0, 255, 136, 0.4);
}

.d-signal-stat.hold .d-signal-count { color: #ffa502; }

.d-signal-stat.sell .d-signal-count { 
  color: #ff4757;
  text-shadow: 0 0 20px rgba(255, 71, 87, 0.4);
}

.d-signal-label { font-size: 13px; color: rgba(255, 255, 255, 0.5); font-weight: 500; }

.d-trending-list { display: flex; flex-direction: column; gap: 14px; }

.d-trending-item { 
  display: flex; 
  align-items: center; 
  gap: 14px;
  padding: 10px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  transition: all 0.2s;
}

.d-trending-item:hover {
  background: rgba(0, 212, 255, 0.05);
}

.d-trending-avatar { 
  width: 40px; 
  height: 40px; 
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.1);
}

.d-trending-info { flex: 1; }
.d-trending-name { font-weight: 700; font-size: 15px; display: block; color: #ffffff; }

.d-trending-change { 
  font-size: 14px; 
  font-weight: 700;
  font-family: 'SF Mono', 'Roboto Mono', monospace;
}

.d-trending-change.up { color: #00ff88; }
.d-trending-change.down { color: #ff4757; }

.d-whale-list { display: flex; flex-direction: column; gap: 12px; }

.d-whale-item { 
  display: flex; 
  align-items: center; 
  gap: 12px; 
  padding: 14px; 
  background: rgba(255,255,255,0.03); 
  border-radius: 14px;
  border: 1px solid rgba(255, 255, 255, 0.04);
  transition: all 0.2s;
}

.d-whale-item:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.1);
}

.d-whale-type { font-size: 18px; }
.d-whale-info { flex: 1; }
.d-whale-amount { display: block; font-weight: 700; font-size: 14px; color: #ffffff; }
.d-whale-value { font-size: 12px; color: rgba(255, 255, 255, 0.5); }
.d-whale-time { font-size: 12px; color: rgba(255, 255, 255, 0.3); }
</style>
