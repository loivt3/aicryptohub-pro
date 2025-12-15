<template>
  <div class="mobile-onchain">
    <!-- Header -->
    <section class="m-section">
      <h3 class="m-section-title">⛓️ On-Chain Signals</h3>
      <p class="m-text-muted" style="font-size: 12px;">Blockchain analytics & whale tracking</p>
    </section>

    <!-- Network Stats -->
    <section class="m-section">
      <div class="m-stats-scroll">
        <div class="m-stats-container">
          <div class="m-stat-card-pro">
            <div class="m-stat-header">
              <span class="m-stat-label">BTC NETFLOW</span>
              <span class="m-stat-change" :class="netflowBtc >= 0 ? 'positive' : 'negative'">
                {{ netflowBtc >= 0 ? '↑ Inflow' : '↓ Outflow' }}
              </span>
            </div>
            <div class="m-stat-value-large" :class="netflowBtc >= 0 ? 'm-text-danger' : 'm-text-success'">
              {{ Math.abs(netflowBtc).toLocaleString() }} BTC
            </div>
          </div>
          
          <div class="m-stat-card-pro">
            <div class="m-stat-header">
              <span class="m-stat-label">ETH GAS</span>
            </div>
            <div class="m-stat-value-large">{{ gasPrice }} Gwei</div>
            <div class="m-gas-indicator" :class="gasLevel"></div>
          </div>
          
          <div class="m-stat-card-pro">
            <div class="m-stat-header">
              <span class="m-stat-label">ACTIVE ADDR</span>
              <span class="m-stat-change positive">↑ 12%</span>
            </div>
            <div class="m-stat-value-large">1.2M</div>
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
      
      <div class="m-list">
        <div v-for="tx in whaleTransactions" :key="tx.id" class="m-list-item m-whale-item">
          <div class="m-whale-icon" :class="tx.type">
            {{ tx.type === 'buy' ? '🟢' : '🔴' }}
          </div>
          <div class="m-info">
            <span class="m-info-title">{{ tx.symbol }}</span>
            <span class="m-info-subtitle">{{ tx.time }}</span>
          </div>
          <div class="m-whale-amount">
            <span class="m-info-title">{{ tx.amount }}</span>
            <span class="m-info-subtitle">${{ tx.value }}</span>
          </div>
          <span class="m-whale-type" :class="tx.type">{{ tx.type.toUpperCase() }}</span>
        </div>
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
            <span class="m-flow-value m-text-danger">+$1.2B</span>
          </div>
          <span class="m-flow-signal">Bearish</span>
        </div>
        
        <div class="m-flow-card outflow">
          <div class="m-flow-icon">📤</div>
          <div class="m-flow-info">
            <span class="m-flow-label">Exchange Outflow</span>
            <span class="m-flow-value m-text-success">-$2.8B</span>
          </div>
          <span class="m-flow-signal">Bullish</span>
        </div>
      </div>
    </section>

    <!-- Top Accumulation -->
    <section class="m-section">
      <h3 class="m-section-title">📈 Top Accumulation</h3>
      
      <div class="m-list">
        <div v-for="coin in topAccumulation" :key="coin.symbol" class="m-list-item">
          <img :src="coin.image" class="m-avatar" />
          <div class="m-info">
            <span class="m-info-title">{{ coin.symbol }}</span>
            <span class="m-info-subtitle">{{ coin.name }}</span>
          </div>
          <div class="m-acc-bar">
            <div class="m-acc-fill" :style="{ width: coin.score + '%' }"></div>
          </div>
          <span class="m-acc-score m-text-success">{{ coin.score }}</span>
        </div>
      </div>
    </section>

    <!-- Contract Addresses -->
    <section class="m-section">
      <h3 class="m-section-title">📋 Smart Contract Activity</h3>
      
      <div class="m-contract-list">
        <div v-for="contract in contracts" :key="contract.address" class="m-contract-item">
          <div class="m-contract-header">
            <span class="m-contract-name">{{ contract.name }}</span>
            <span class="m-contract-chain">{{ contract.chain }}</span>
          </div>
          <div class="m-contract-address">{{ contract.address }}</div>
          <div class="m-contract-stats">
            <span>Txns: {{ contract.txns }}</span>
            <span>Vol: ${{ contract.volume }}</span>
          </div>
        </div>
      </div>
    </section>
    
    <div class="m-bottom-spacer"></div>
  </div>
</template>

<script setup lang="ts">
const netflowBtc = ref(-2450)
const gasPrice = ref(28)
const gasLevel = computed(() => {
  if (gasPrice.value < 20) return 'low'
  if (gasPrice.value < 50) return 'medium'
  return 'high'
})

const whaleTransactions = ref([
  { id: 1, symbol: 'BTC', type: 'buy', amount: '500 BTC', value: '49.2M', time: '2h ago' },
  { id: 2, symbol: 'ETH', type: 'sell', amount: '15,000 ETH', value: '51.7M', time: '4h ago' },
  { id: 3, symbol: 'SOL', type: 'buy', amount: '250,000 SOL', value: '46.2M', time: '5h ago' },
  { id: 4, symbol: 'BTC', type: 'buy', amount: '320 BTC', value: '31.5M', time: '8h ago' },
])

const topAccumulation = ref([
  { symbol: 'BTC', name: 'Bitcoin', image: 'https://assets.coingecko.com/coins/images/1/small/bitcoin.png', score: 92 },
  { symbol: 'ETH', name: 'Ethereum', image: 'https://assets.coingecko.com/coins/images/279/small/ethereum.png', score: 78 },
  { symbol: 'SOL', name: 'Solana', image: 'https://assets.coingecko.com/coins/images/4128/small/solana.png', score: 85 },
])

const contracts = ref([
  { name: 'Uniswap V3', chain: 'ETH', address: '0x1F98...C2d6', txns: '125K', volume: '892M' },
  { name: 'Raydium', chain: 'SOL', address: 'DvN3...9xq4', txns: '89K', volume: '456M' },
])
</script>

<style scoped>
.mobile-onchain {
  padding: 0;
}

.m-stat-card-pro {
  flex: 0 0 auto;
  min-width: 140px;
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

.m-gas-indicator {
  height: 4px;
  border-radius: 2px;
  margin-top: 8px;
}

.m-gas-indicator.low { background: #22c55e; width: 30%; }
.m-gas-indicator.medium { background: #f97316; width: 60%; }
.m-gas-indicator.high { background: #ef4444; width: 100%; }

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

/* Accumulation Bar */
.m-acc-bar {
  width: 60px;
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
}

.m-acc-fill {
  height: 100%;
  background: linear-gradient(90deg, #22c55e, #4ade80);
  border-radius: 3px;
}

.m-acc-score {
  font-size: 14px;
  font-weight: 700;
  min-width: 30px;
  text-align: right;
}

/* Contract List */
.m-contract-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.m-contract-item {
  padding: 12px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
}

.m-contract-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.m-contract-name {
  font-size: 14px;
  font-weight: 600;
  color: #ffffff;
}

.m-contract-chain {
  font-size: 10px;
  padding: 2px 6px;
  background: rgba(56, 239, 235, 0.15);
  color: #38efeb;
  border-radius: 4px;
}

.m-contract-address {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
  font-family: monospace;
  margin-bottom: 8px;
}

.m-contract-stats {
  display: flex;
  gap: 16px;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.6);
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
