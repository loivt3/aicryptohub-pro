<template>
  <div class="mobile-onchain">
    <!-- Header -->
    <section class="m-section">
      <h3 class="m-section-title">⛓️ On-Chain Signals</h3>
      <p class="m-text-muted" style="font-size: 12px;">Blockchain analytics & whale tracking</p>
    </section>

    <!-- Loading State -->
    <section v-if="loading" class="m-section">
      <div class="m-loading-indicator">Loading on-chain data...</div>
    </section>

    <!-- Network Stats -->
    <section v-else class="m-section">
      <div class="m-stats-scroll">
        <div class="m-stats-container">
          <div class="m-stat-card-pro">
            <div class="m-stat-header">
              <span class="m-stat-label">NET FLOW</span>
              <span class="m-stat-change" :class="netFlow >= 0 ? 'negative' : 'positive'">
                {{ netFlow >= 0 ? '↑ Inflow' : '↓ Outflow' }}
              </span>
            </div>
            <div class="m-stat-value-large" :class="netFlow >= 0 ? 'm-text-danger' : 'm-text-success'">
              ${{ formatValue(Math.abs(netFlow)) }}
            </div>
          </div>
          
          <div class="m-stat-card-pro">
            <div class="m-stat-header">
              <span class="m-stat-label">BULLISH</span>
            </div>
            <div class="m-stat-value-large m-text-success">{{ stats.bullish_count || 0 }}</div>
          </div>
          
          <div class="m-stat-card-pro">
            <div class="m-stat-header">
              <span class="m-stat-label">BEARISH</span>
            </div>
            <div class="m-stat-value-large m-text-danger">{{ stats.bearish_count || 0 }}</div>
          </div>
          
          <div class="m-stat-card-pro">
            <div class="m-stat-header">
              <span class="m-stat-label">NEUTRAL</span>
            </div>
            <div class="m-stat-value-large" style="color: #94a3b8;">{{ stats.neutral_count || 0 }}</div>
          </div>
        </div>
      </div>
    </section>

    <!-- Whale Transactions -->
    <section class="m-section">
      <div class="m-section-header">
        <h3 class="m-section-title">🐋 Whale Transactions</h3>
        <span class="m-badge-info">Last 24h</span>
      </div>
      
      <div class="m-list" v-if="whaleTransactions.length > 0">
        <div v-for="(tx, idx) in whaleTransactions" :key="idx" class="m-list-item m-whale-item">
          <div class="m-whale-icon" :class="tx.tx_type?.includes('withdraw') ? 'buy' : 'sell'">
            {{ tx.tx_type?.includes('withdraw') ? '🟢' : '🔴' }}
          </div>
          <div class="m-info">
            <span class="m-info-title">{{ tx.coin_id?.toUpperCase() }}</span>
            <span class="m-info-subtitle">{{ formatTime(tx.tx_timestamp) }}</span>
          </div>
          <div class="m-whale-amount">
            <span class="m-info-title">${{ formatValue(tx.value_usd) }}</span>
            <span class="m-info-subtitle">{{ tx.exchange_name || 'Unknown' }}</span>
          </div>
          <span class="m-whale-type" :class="tx.tx_type?.includes('withdraw') ? 'buy' : 'sell'">
            {{ tx.tx_type?.includes('withdraw') ? 'OUT' : 'IN' }}
          </span>
        </div>
      </div>
      <div v-else class="m-empty-state">
        <span>No whale transactions in last 24h</span>
      </div>
    </section>

    <!-- Exchange Flows -->
    <section class="m-section">
      <h3 class="m-section-title">📊 Exchange Flows</h3>
      
      <div class="m-flow-cards">
        <div class="m-flow-card inflow">
          <div class="m-flow-icon">📥</div>
          <div class="m-flow-info">
            <span class="m-flow-label">Exchange Inflow</span>
            <span class="m-flow-value m-text-danger">+${{ formatValue(totalInflow) }}</span>
          </div>
          <span class="m-flow-signal">{{ totalInflow > totalOutflow ? 'Bearish' : 'Neutral' }}</span>
        </div>
        
        <div class="m-flow-card outflow">
          <div class="m-flow-icon">📤</div>
          <div class="m-flow-info">
            <span class="m-flow-label">Exchange Outflow</span>
            <span class="m-flow-value m-text-success">-${{ formatValue(totalOutflow) }}</span>
          </div>
          <span class="m-flow-signal">{{ totalOutflow > totalInflow ? 'Bullish' : 'Neutral' }}</span>
        </div>
      </div>
    </section>

    <!-- Top Signals -->
    <section class="m-section" v-if="topSignals.length > 0">
      <h3 class="m-section-title">📈 Top On-Chain Signals</h3>
      
      <div class="m-list">
        <div v-for="coin in topSignals" :key="coin.coin_id" class="m-list-item">
          <img :src="coin.image || `https://assets.coingecko.com/coins/images/1/small/bitcoin.png`" class="m-avatar" />
          <div class="m-info">
            <span class="m-info-title">{{ coin.coin_id?.toUpperCase() }}</span>
            <span class="m-info-subtitle">Signal: {{ coin.overall_signal || 'NEUTRAL' }}</span>
          </div>
          <div class="m-signal-col">
            <span class="m-signal-badge" :class="getSignalClass(coin.overall_signal)">
              {{ coin.bullish_probability?.toFixed(0) || 50 }}%
            </span>
          </div>
        </div>
      </div>
    </section>
    
    <div class="m-bottom-spacer"></div>
  </div>
</template>

<script setup lang="ts">
const loading = ref(true)
const stats = ref<any>({})
const whaleTransactions = ref<any[]>([])
const topSignals = ref<any[]>([])
const totalInflow = ref(0)
const totalOutflow = ref(0)

const netFlow = computed(() => totalInflow.value - totalOutflow.value)

// Fetch on-chain data
const fetchOnChainData = async () => {
  loading.value = true
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase || '/api/v1'
  
  try {
    const response = await $fetch<any>(`${apiBase}/onchain/summary`)
    
    if (response) {
      stats.value = response.stats || {}
      whaleTransactions.value = response.recent_whale_txs || []
      topSignals.value = response.signals || []
      totalInflow.value = response.total_inflow || 0
      totalOutflow.value = response.total_outflow || 0
    }
  } catch (error) {
    console.error('[OnChain] Failed to fetch data:', error)
  } finally {
    loading.value = false
  }
}

// Format large numbers
const formatValue = (value: number) => {
  if (!value) return '0'
  if (value >= 1e9) return (value / 1e9).toFixed(2) + 'B'
  if (value >= 1e6) return (value / 1e6).toFixed(2) + 'M'
  if (value >= 1e3) return (value / 1e3).toFixed(2) + 'K'
  return value.toFixed(0)
}

// Format timestamp
const formatTime = (timestamp: string) => {
  if (!timestamp) return '--'
  const date = new Date(timestamp)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffHrs = Math.floor(diffMs / (1000 * 60 * 60))
  if (diffHrs < 1) return 'Just now'
  if (diffHrs < 24) return `${diffHrs}h ago`
  return `${Math.floor(diffHrs / 24)}d ago`
}

// Get signal class
const getSignalClass = (signal: string) => {
  if (!signal) return ''
  const s = signal.toLowerCase()
  if (s.includes('bull') || s.includes('buy')) return 'm-signal-buy'
  if (s.includes('bear') || s.includes('sell')) return 'm-signal-sell'
  return 'm-signal-neutral'
}

onMounted(() => {
  fetchOnChainData()
})
</script>

<style scoped>
.mobile-onchain {
  padding: 0;
}

.m-loading-indicator {
  text-align: center;
  padding: 40px;
  color: rgba(255, 255, 255, 0.5);
}

.m-empty-state {
  text-align: center;
  padding: 24px;
  color: rgba(255, 255, 255, 0.4);
  font-size: 13px;
}

.m-stats-scroll {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.m-stats-container {
  display: flex;
  gap: 10px;
  padding-bottom: 8px;
}

.m-stat-card-pro {
  flex: 0 0 auto;
  min-width: 120px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 12px;
}

.m-stat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.m-stat-label {
  font-size: 9px;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
}

.m-stat-change {
  font-size: 9px;
  font-weight: 600;
}

.m-stat-change.positive { color: #22c55e; }
.m-stat-change.negative { color: #ef4444; }

.m-stat-value-large {
  font-size: 18px;
  font-weight: 700;
  color: #ffffff;
}

/* Whale Transactions */
.m-whale-item {
  gap: 10px;
}

.m-whale-icon {
  font-size: 16px;
}

.m-whale-amount {
  text-align: right;
}

.m-whale-type {
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 9px;
  font-weight: 700;
}

.m-whale-type.buy {
  background: rgba(34, 197, 94, 0.2);
  color: #22c55e;
}

.m-whale-type.sell {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

/* Flow Cards */
.m-flow-cards {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.m-flow-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 12px;
}

.m-flow-card.inflow {
  border-left: 3px solid #ef4444;
}

.m-flow-card.outflow {
  border-left: 3px solid #22c55e;
}

.m-flow-icon {
  font-size: 24px;
}

.m-flow-info {
  flex: 1;
}

.m-flow-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  display: block;
}

.m-flow-value {
  font-size: 18px;
  font-weight: 700;
}

.m-flow-signal {
  font-size: 11px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.7);
}

/* Signals */
.m-signal-col {
  text-align: right;
}

.m-signal-badge {
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
}

.m-signal-buy {
  background: rgba(34, 197, 94, 0.2);
  color: #22c55e;
}

.m-signal-sell {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.m-signal-neutral {
  background: rgba(148, 163, 184, 0.2);
  color: #94a3b8;
}

.m-badge-info {
  background: rgba(88, 166, 255, 0.15);
  color: #58a6ff;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
}
</style>
