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
const { getOnchainSummary, getOnchainSignals } = useApi()

// Reactive state
const loading = ref(true)
const error = ref<string | null>(null)
const netflow = ref(0)
const gasPrice = ref(0)
const gasLevel = computed(() => gasPrice.value < 20 ? 'low' : gasPrice.value < 50 ? 'medium' : 'high')
const totalInflow = ref(0)
const totalOutflow = ref(0)
const activeAddresses = ref(0)
const stablecoinInflow = ref(0)

const whaleTransactions = ref<any[]>([])
const topAccumulation = ref<any[]>([])
const coinSignals = ref<any[]>([])

// Format large numbers
const formatValue = (val: number) => {
  if (val >= 1e9) return `$${(val / 1e9).toFixed(1)}B`
  if (val >= 1e6) return `$${(val / 1e6).toFixed(1)}M`
  if (val >= 1e3) return `$${(val / 1e3).toFixed(1)}K`
  return `$${val.toFixed(0)}`
}

const formatAddress = (addr: string) => {
  if (!addr) return 'Unknown'
  if (addr.length > 12) return `${addr.slice(0, 6)}...${addr.slice(-4)}`
  return addr
}

const timeAgo = (dateStr: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffHrs = Math.floor(diffMs / (1000 * 60 * 60))
  if (diffHrs < 1) return 'Just now'
  if (diffHrs < 24) return `${diffHrs}h ago`
  return `${Math.floor(diffHrs / 24)}d ago`
}

// Fetch data on mount
onMounted(async () => {
  try {
    loading.value = true
    
    // Fetch summary data
    const summary = await getOnchainSummary()
    if (summary) {
      totalInflow.value = summary.total_inflow_24h || 0
      totalOutflow.value = summary.total_outflow_24h || 0
      netflow.value = (summary.total_inflow_24h || 0) - (summary.total_outflow_24h || 0)
      gasPrice.value = summary.gas_price_gwei || 28
      activeAddresses.value = summary.active_addresses_24h || 0
      stablecoinInflow.value = summary.stablecoin_inflow_24h || 0
      
      // Whale transactions from summary
      if (summary.recent_whale_txs?.length) {
        whaleTransactions.value = summary.recent_whale_txs.map((tx: any, idx: number) => ({
          id: idx,
          symbol: tx.coin_id?.toUpperCase() || 'UNKNOWN',
          type: tx.tx_type === 'exchange_deposit' ? 'sell' : 'buy',
          amount: formatValue(tx.value_usd || 0),
          value: formatValue(tx.value_usd || 0),
          from: formatAddress(tx.from_address),
          to: formatAddress(tx.to_address),
          time: timeAgo(tx.tx_timestamp),
        }))
      }
      
      // Top accumulation from signals
      if (summary.top_signals?.length) {
        topAccumulation.value = summary.top_signals.slice(0, 5).map((s: any) => ({
          symbol: s.coin_id?.toUpperCase() || 'UNKNOWN',
          image: `https://assets.coingecko.com/coins/images/1/small/bitcoin.png`, // Default
          score: s.accumulation_score || s.bullish_probability || 50,
        }))
      }
    }
    
    // Fetch individual coin signals for display
    const coins = ['bitcoin', 'ethereum', 'chainlink', 'aave', 'pepe']
    const signalsPromises = coins.map(coin => getOnchainSignals(coin).catch(() => null))
    const signalsResults = await Promise.all(signalsPromises)
    
    coinSignals.value = signalsResults
      .filter(s => s !== null)
      .map((s: any) => ({
        coinId: s.coin_id,
        signal: s.overall_signal,
        whaleSignal: s.whale_activity?.signal,
        netFlow: s.whale_activity?.net_flow_usd || 0,
      }))
    
  } catch (e: any) {
    error.value = e.message || 'Failed to load data'
    console.error('Failed to fetch onchain data:', e)
  } finally {
    loading.value = false
  }
})
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
