<template>
  <div class="d-analysis">
    <section class="d-section">
      <h1 class="d-page-title">AI Analysis</h1>
    </section>

    <!-- Overview Cards -->
    <section class="d-section">
      <div class="d-overview-grid">
        <div class="d-overview-card">
          <h3>Market Sentiment</h3>
          <div class="d-sentiment-row">
            <AsiGauge :score="68" :size="120" />
            <div class="d-sentiment-info">
              <span class="d-sentiment-value positive">68</span>
              <span class="d-sentiment-label">Bullish</span>
            </div>
          </div>
        </div>
        <div class="d-overview-card">
          <h3>Signal Distribution</h3>
          <div class="d-dist-bar">
            <div class="d-dist-fill buy" style="width:52%"></div>
            <div class="d-dist-fill hold" style="width:35%"></div>
            <div class="d-dist-fill sell" style="width:13%"></div>
          </div>
          <div class="d-dist-legend">
            <span class="buy">🟢 Buy 52%</span>
            <span class="hold">🟡 Hold 35%</span>
            <span class="sell">🔴 Sell 13%</span>
          </div>
        </div>
      </div>
    </section>

    <!-- Signals Table -->
    <section class="d-section">
      <h2 class="d-section-title">Top AI Signals</h2>
      <div class="d-table-card">
        <table class="d-table">
          <thead>
            <tr>
              <th>Coin</th>
              <th>Price</th>
              <th>24h</th>
              <th>ASI</th>
              <th>Signal</th>
              <th>Reasoning</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="s in signals" :key="s.symbol">
              <td><div class="d-coin-cell"><img :src="s.image" class="d-coin-avatar"/><span>{{ s.symbol }}</span></div></td>
              <td>${{ s.price.toLocaleString() }}</td>
              <td :class="s.change >= 0 ? 'text-success' : 'text-danger'">{{ s.change >= 0 ? '+' : '' }}{{ s.change }}%</td>
              <td><span :class="s.asi >= 60 ? 'text-success' : s.asi <= 40 ? 'text-danger' : ''">{{ s.asi }}</span></td>
              <td><span class="d-signal-badge" :class="s.signal.includes('BUY') ? 'buy' : s.signal.includes('SELL') ? 'sell' : 'hold'">{{ s.signal }}</span></td>
              <td class="d-reasoning">{{ s.reasoning }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
const signals = ref([
  { symbol: 'BTC', image: 'https://assets.coingecko.com/coins/images/1/small/bitcoin.png', price: 98500, change: 2.4, asi: 72, signal: 'BUY', reasoning: 'Strong bullish momentum, MACD positive' },
  { symbol: 'SOL', image: 'https://assets.coingecko.com/coins/images/4128/small/solana.png', price: 185, change: 5.2, asi: 78, signal: 'STRONG_BUY', reasoning: 'Network metrics ATH, breaking resistance' },
  { symbol: 'ETH', image: 'https://assets.coingecko.com/coins/images/279/small/ethereum.png', price: 3450, change: 1.8, asi: 58, signal: 'HOLD', reasoning: 'Consolidating, wait for breakout' },
  { symbol: 'DOGE', image: 'https://assets.coingecko.com/coins/images/5/small/dogecoin.png', price: 0.32, change: -2.1, asi: 35, signal: 'SELL', reasoning: 'Whale distribution detected' },
])
</script>

<style scoped>
.d-analysis { padding: 24px 0; }
.d-page-title { font-size: 32px; font-weight: 700; margin: 0; }
.d-overview-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.d-overview-card { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 24px; }
.d-overview-card h3 { font-size: 16px; margin: 0 0 16px; }
.d-sentiment-row { display: flex; align-items: center; gap: 24px; }
.d-sentiment-info { display: flex; flex-direction: column; }
.d-sentiment-value { font-size: 48px; font-weight: 700; }
.d-sentiment-value.positive { color: #22c55e; }
.d-sentiment-label { font-size: 18px; color: rgba(255,255,255,0.7); }
.d-dist-bar { height: 12px; border-radius: 6px; display: flex; overflow: hidden; margin-bottom: 12px; }
.d-dist-fill { height: 100%; }
.d-dist-fill.buy { background: #22c55e; }
.d-dist-fill.hold { background: #f97316; }
.d-dist-fill.sell { background: #ef4444; }
.d-dist-legend { display: flex; gap: 16px; font-size: 13px; }
.d-dist-legend .buy { color: #22c55e; }
.d-dist-legend .hold { color: #f97316; }
.d-dist-legend .sell { color: #ef4444; }
.d-section { margin-bottom: 24px; }
.d-section-title { font-size: 20px; font-weight: 600; margin: 0 0 16px; }
.d-table-card { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; overflow: hidden; }
.d-table { width: 100%; border-collapse: collapse; }
.d-table th, .d-table td { padding: 14px 16px; text-align: left; }
.d-table th { font-size: 12px; color: rgba(255,255,255,0.5); border-bottom: 1px solid rgba(255,255,255,0.06); }
.d-table tbody tr { border-bottom: 1px solid rgba(255,255,255,0.04); }
.d-table tbody tr:hover { background: rgba(255,255,255,0.04); }
.d-coin-cell { display: flex; align-items: center; gap: 10px; }
.d-coin-avatar { width: 28px; height: 28px; border-radius: 50%; }
.text-success { color: #22c55e; }
.text-danger { color: #ef4444; }
.d-signal-badge { padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 700; }
.d-signal-badge.buy { background: rgba(34,197,94,0.2); color: #22c55e; }
.d-signal-badge.sell { background: rgba(239,68,68,0.2); color: #ef4444; }
.d-signal-badge.hold { background: rgba(249,115,22,0.2); color: #f97316; }
.d-reasoning { font-size: 12px; color: rgba(255,255,255,0.6); max-width: 250px; }
</style>
