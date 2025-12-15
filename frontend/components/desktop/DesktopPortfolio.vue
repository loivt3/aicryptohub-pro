<template>
  <div class="d-portfolio">
    <section class="d-section">
      <div class="d-section-header">
        <h1 class="d-page-title">Portfolio</h1>
        <button class="d-btn-primary" @click="showModal = true">+ Add Holding</button>
      </div>
    </section>

    <!-- Summary Cards -->
    <section class="d-section">
      <div class="d-summary-grid">
        <div class="d-summary-card">
          <span class="d-summary-icon">💰</span>
          <div class="d-summary-info">
            <span class="d-summary-label">Total Value</span>
            <span class="d-summary-value">${{ formatPrice(totalValue) }}</span>
          </div>
        </div>
        <div class="d-summary-card">
          <span class="d-summary-icon">📊</span>
          <div class="d-summary-info">
            <span class="d-summary-label">Total P&L</span>
            <span class="d-summary-value" :class="totalPnL >= 0 ? 'up' : 'down'">
              {{ totalPnL >= 0 ? '+' : '' }}${{ formatPrice(totalPnL) }}
            </span>
          </div>
        </div>
        <div class="d-summary-card">
          <span class="d-summary-icon">🏆</span>
          <div class="d-summary-info">
            <span class="d-summary-label">Best Performer</span>
            <span class="d-summary-value up">{{ bestPerformer }}</span>
          </div>
        </div>
        <div class="d-summary-card">
          <span class="d-summary-icon">📉</span>
          <div class="d-summary-info">
            <span class="d-summary-label">Worst Performer</span>
            <span class="d-summary-value down">{{ worstPerformer }}</span>
          </div>
        </div>
      </div>
    </section>

    <!-- Holdings Table -->
    <section class="d-section">
      <h2 class="d-section-title">Holdings</h2>
      <div class="d-table-card">
        <table class="d-table">
          <thead>
            <tr>
              <th>Asset</th>
              <th class="text-right">Amount</th>
              <th class="text-right">Avg. Buy</th>
              <th class="text-right">Current Price</th>
              <th class="text-right">Value</th>
              <th class="text-right">P&L</th>
              <th class="text-right">Allocation</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="h in holdings" :key="h.coin_id">
              <td>
                <div class="d-coin-cell">
                  <img :src="h.image" class="d-coin-avatar" />
                  <div><p class="d-coin-name">{{ h.symbol }}</p><p class="d-coin-symbol">{{ h.name }}</p></div>
                </div>
              </td>
              <td class="text-right font-mono">{{ h.amount.toLocaleString() }}</td>
              <td class="text-right font-mono">${{ h.buy_price.toLocaleString() }}</td>
              <td class="text-right font-mono">${{ h.current_price.toLocaleString() }}</td>
              <td class="text-right font-mono">${{ formatPrice(h.value) }}</td>
              <td class="text-right" :class="h.pnl >= 0 ? 'text-success' : 'text-danger'">
                {{ h.pnl >= 0 ? '+' : '' }}${{ formatPrice(h.pnl) }}
                <span class="d-pnl-pct">({{ h.pnl_pct >= 0 ? '+' : '' }}{{ h.pnl_pct.toFixed(1) }}%)</span>
              </td>
              <td class="text-right">
                <div class="d-alloc-bar">
                  <div class="d-alloc-fill" :style="{ width: h.allocation + '%' }"></div>
                </div>
                <span class="d-alloc-pct">{{ h.allocation.toFixed(1) }}%</span>
              </td>
              <td class="text-right">
                <button class="d-action-btn" @click="editHolding(h)">✏️</button>
                <button class="d-action-btn" @click="removeHolding(h.coin_id)">🗑️</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
const showModal = ref(false)

const holdings = ref([
  { coin_id: 'bitcoin', symbol: 'BTC', name: 'Bitcoin', image: 'https://assets.coingecko.com/coins/images/1/small/bitcoin.png', amount: 0.5, buy_price: 45000, current_price: 98500, value: 49250, pnl: 26750, pnl_pct: 118.9, allocation: 64.5 },
  { coin_id: 'ethereum', symbol: 'ETH', name: 'Ethereum', image: 'https://assets.coingecko.com/coins/images/279/small/ethereum.png', amount: 5, buy_price: 2800, current_price: 3450, value: 17250, pnl: 3250, pnl_pct: 23.2, allocation: 22.6 },
  { coin_id: 'solana', symbol: 'SOL', name: 'Solana', image: 'https://assets.coingecko.com/coins/images/4128/small/solana.png', amount: 50, buy_price: 100, current_price: 185, value: 9250, pnl: 4250, pnl_pct: 85.0, allocation: 12.1 },
])

const totalValue = computed(() => holdings.value.reduce((sum, h) => sum + h.value, 0))
const totalPnL = computed(() => holdings.value.reduce((sum, h) => sum + h.pnl, 0))
const bestPerformer = computed(() => holdings.value.reduce((best, h) => h.pnl_pct > best.pnl_pct ? h : best).symbol)
const worstPerformer = computed(() => holdings.value.reduce((worst, h) => h.pnl_pct < worst.pnl_pct ? h : worst).symbol)

const formatPrice = (n: number) => n.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
const editHolding = (h: any) => console.log('Edit', h)
const removeHolding = (id: string) => holdings.value = holdings.value.filter(h => h.coin_id !== id)
</script>

<style scoped>
.d-portfolio { padding: 24px 0; }
.d-page-title { font-size: 32px; font-weight: 700; margin: 0; }
.d-section { margin-bottom: 24px; }
.d-section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.d-section-title { font-size: 20px; font-weight: 600; margin: 0 0 16px; }
.d-btn-primary { padding: 12px 20px; background: linear-gradient(135deg, #38efeb, #0066ff); border: none; border-radius: 10px; color: #000; font-weight: 600; cursor: pointer; }
.d-summary-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
.d-summary-card { display: flex; align-items: center; gap: 16px; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 20px; }
.d-summary-icon { font-size: 32px; }
.d-summary-label { display: block; font-size: 12px; color: rgba(255,255,255,0.5); margin-bottom: 4px; }
.d-summary-value { display: block; font-size: 24px; font-weight: 700; }
.d-summary-value.up { color: #22c55e; }
.d-summary-value.down { color: #ef4444; }
.d-table-card { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; overflow: hidden; }
.d-table { width: 100%; border-collapse: collapse; }
.d-table th, .d-table td { padding: 14px 16px; text-align: left; }
.d-table th { font-size: 12px; color: rgba(255,255,255,0.5); border-bottom: 1px solid rgba(255,255,255,0.06); }
.d-table tbody tr { border-bottom: 1px solid rgba(255,255,255,0.04); }
.d-table tbody tr:hover { background: rgba(255,255,255,0.04); }
.d-coin-cell { display: flex; align-items: center; gap: 10px; }
.d-coin-avatar { width: 32px; height: 32px; border-radius: 50%; }
.d-coin-name { font-weight: 600; margin: 0; }
.d-coin-symbol { font-size: 12px; color: rgba(255,255,255,0.5); margin: 0; }
.text-right { text-align: right; }
.text-success { color: #22c55e; }
.text-danger { color: #ef4444; }
.font-mono { font-family: monospace; }
.d-pnl-pct { font-size: 11px; color: rgba(255,255,255,0.5); margin-left: 4px; }
.d-alloc-bar { width: 60px; height: 6px; background: rgba(255,255,255,0.1); border-radius: 3px; overflow: hidden; display: inline-block; margin-right: 8px; }
.d-alloc-fill { height: 100%; background: linear-gradient(90deg, #38efeb, #0066ff); }
.d-alloc-pct { font-size: 12px; }
.d-action-btn { background: transparent; border: none; cursor: pointer; padding: 4px 8px; font-size: 14px; }
</style>
