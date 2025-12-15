<template>
  <div class="d-onchain">
    <section class="d-section">
      <h1 class="d-page-title">⛓️ On-Chain Signals</h1>
      <p class="d-page-subtitle">Blockchain analytics, whale tracking, and exchange flows</p>
    </section>

    <!-- Stats Row -->
    <section class="d-section">
      <div class="d-stats-row">
        <div class="d-stat-card">
          <span class="d-stat-label">BTC EXCHANGE NETFLOW</span>
          <span class="d-stat-value" :class="netflow >= 0 ? 'danger' : 'success'">
            {{ netflow >= 0 ? '+' : '' }}{{ netflow.toLocaleString() }} BTC
          </span>
          <span class="d-stat-signal">{{ netflow >= 0 ? '📥 Bearish' : '📤 Bullish' }}</span>
        </div>
        <div class="d-stat-card">
          <span class="d-stat-label">ETH GAS PRICE</span>
          <span class="d-stat-value">{{ gasPrice }} Gwei</span>
          <div class="d-gas-indicator" :class="gasLevel"></div>
        </div>
        <div class="d-stat-card">
          <span class="d-stat-label">ACTIVE ADDRESSES (24H)</span>
          <span class="d-stat-value">1.2M</span>
          <span class="d-stat-change success">↑ 12% vs 7d avg</span>
        </div>
        <div class="d-stat-card">
          <span class="d-stat-label">STABLECOIN INFLOW</span>
          <span class="d-stat-value success">+$2.8B</span>
          <span class="d-stat-signal">Bullish</span>
        </div>
      </div>
    </section>

    <!-- Content Grid -->
    <div class="d-content-grid">
      <!-- Whale Transactions -->
      <section class="d-main-section">
        <h2 class="d-section-title">🐋 Whale Transactions (24h)</h2>
        <div class="d-table-card">
          <table class="d-table">
            <thead>
              <tr><th>Type</th><th>Coin</th><th>Amount</th><th>Value</th><th>From</th><th>To</th><th>Time</th></tr>
            </thead>
            <tbody>
              <tr v-for="tx in whaleTransactions" :key="tx.id">
                <td><span class="d-tx-type" :class="tx.type">{{ tx.type === 'buy' ? '🟢 Buy' : '🔴 Sell' }}</span></td>
                <td><strong>{{ tx.symbol }}</strong></td>
                <td class="font-mono">{{ tx.amount }}</td>
                <td class="font-mono">${{ tx.value }}</td>
                <td class="d-address">{{ tx.from }}</td>
                <td class="d-address">{{ tx.to }}</td>
                <td class="text-muted">{{ tx.time }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- Sidebar -->
      <aside class="d-sidebar">
        <div class="d-sidebar-card">
          <h3 class="d-sidebar-title">📊 Exchange Flows</h3>
          <div class="d-flow-item inflow">
            <span class="d-flow-icon">📥</span>
            <div class="d-flow-info">
              <span>Exchange Inflow</span>
              <strong class="danger">+$1.2B</strong>
            </div>
          </div>
          <div class="d-flow-item outflow">
            <span class="d-flow-icon">📤</span>
            <div class="d-flow-info">
              <span>Exchange Outflow</span>
              <strong class="success">-$2.8B</strong>
            </div>
          </div>
        </div>

        <div class="d-sidebar-card">
          <h3 class="d-sidebar-title">📈 Top Accumulation</h3>
          <div class="d-acc-list">
            <div v-for="coin in topAccumulation" :key="coin.symbol" class="d-acc-item">
              <img :src="coin.image" class="d-acc-avatar" />
              <span class="d-acc-symbol">{{ coin.symbol }}</span>
              <div class="d-acc-bar"><div class="d-acc-fill" :style="{ width: coin.score + '%' }"></div></div>
              <span class="d-acc-score success">{{ coin.score }}</span>
            </div>
          </div>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
const netflow = ref(-2450)
const gasPrice = ref(28)
const gasLevel = computed(() => gasPrice.value < 20 ? 'low' : gasPrice.value < 50 ? 'medium' : 'high')

const whaleTransactions = ref([
  { id: 1, symbol: 'BTC', type: 'buy', amount: '500 BTC', value: '49.2M', from: '0x1a2b...3c4d', to: 'Binance', time: '2h ago' },
  { id: 2, symbol: 'ETH', type: 'sell', amount: '15,000 ETH', value: '51.7M', from: 'Coinbase', to: '0x5e6f...7g8h', time: '4h ago' },
  { id: 3, symbol: 'SOL', type: 'buy', amount: '250,000 SOL', value: '46.2M', from: '0x9i0j...1k2l', to: 'FTX', time: '5h ago' },
  { id: 4, symbol: 'BTC', type: 'buy', amount: '320 BTC', value: '31.5M', from: '0x3m4n...5o6p', to: 'Kraken', time: '8h ago' },
])

const topAccumulation = ref([
  { symbol: 'BTC', image: 'https://assets.coingecko.com/coins/images/1/small/bitcoin.png', score: 92 },
  { symbol: 'ETH', image: 'https://assets.coingecko.com/coins/images/279/small/ethereum.png', score: 78 },
  { symbol: 'SOL', image: 'https://assets.coingecko.com/coins/images/4128/small/solana.png', score: 85 },
])
</script>

<style scoped>
.d-onchain { padding: 24px 0; }
.d-page-title { font-size: 32px; font-weight: 700; margin: 0 0 8px; }
.d-page-subtitle { color: rgba(255,255,255,0.5); margin: 0; }
.d-section { margin-bottom: 24px; }
.d-section-title { font-size: 20px; font-weight: 600; margin: 0 0 16px; }
.d-stats-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
.d-stat-card { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 20px; }
.d-stat-label { display: block; font-size: 11px; color: rgba(255,255,255,0.5); margin-bottom: 8px; }
.d-stat-value { display: block; font-size: 24px; font-weight: 700; margin-bottom: 8px; }
.d-stat-value.success { color: #22c55e; }
.d-stat-value.danger { color: #ef4444; }
.d-stat-signal { font-size: 12px; color: rgba(255,255,255,0.6); }
.d-stat-change { font-size: 12px; }
.d-stat-change.success { color: #22c55e; }
.d-gas-indicator { height: 6px; border-radius: 3px; margin-top: 8px; }
.d-gas-indicator.low { background: #22c55e; width: 30%; }
.d-gas-indicator.medium { background: #f97316; width: 60%; }
.d-gas-indicator.high { background: #ef4444; width: 100%; }
.d-content-grid { display: grid; grid-template-columns: 1fr 360px; gap: 24px; }
.d-table-card { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; overflow: hidden; }
.d-table { width: 100%; border-collapse: collapse; }
.d-table th, .d-table td { padding: 14px 16px; text-align: left; }
.d-table th { font-size: 12px; color: rgba(255,255,255,0.5); border-bottom: 1px solid rgba(255,255,255,0.06); }
.d-table tbody tr { border-bottom: 1px solid rgba(255,255,255,0.04); }
.d-tx-type { font-size: 12px; font-weight: 600; }
.d-address { font-size: 12px; font-family: monospace; color: rgba(255,255,255,0.5); }
.font-mono { font-family: monospace; }
.text-muted { color: rgba(255,255,255,0.4); }
.d-sidebar { display: flex; flex-direction: column; gap: 16px; }
.d-sidebar-card { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 20px; }
.d-sidebar-title { font-size: 16px; font-weight: 600; margin: 0 0 16px; }
.d-flow-item { display: flex; align-items: center; gap: 12px; padding: 12px; background: rgba(255,255,255,0.04); border-radius: 10px; margin-bottom: 8px; }
.d-flow-item.inflow { border-left: 3px solid #ef4444; }
.d-flow-item.outflow { border-left: 3px solid #22c55e; }
.d-flow-icon { font-size: 20px; }
.d-flow-info { flex: 1; }
.d-flow-info span { display: block; font-size: 12px; color: rgba(255,255,255,0.6); }
.d-flow-info strong { font-size: 18px; }
.d-flow-info strong.success { color: #22c55e; }
.d-flow-info strong.danger { color: #ef4444; }
.d-acc-list { display: flex; flex-direction: column; gap: 12px; }
.d-acc-item { display: flex; align-items: center; gap: 10px; }
.d-acc-avatar { width: 28px; height: 28px; border-radius: 50%; }
.d-acc-symbol { font-weight: 600; min-width: 40px; }
.d-acc-bar { flex: 1; height: 6px; background: rgba(255,255,255,0.1); border-radius: 3px; overflow: hidden; }
.d-acc-fill { height: 100%; background: linear-gradient(90deg, #22c55e, #4ade80); }
.d-acc-score { font-weight: 600; min-width: 30px; text-align: right; }
.d-acc-score.success { color: #22c55e; }
</style>
