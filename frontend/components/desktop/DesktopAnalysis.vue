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

    <!-- Shadow Insight Section -->
    <section class="d-section">
      <h2 class="d-section-title">👁️ Shadow Insight</h2>
      <div class="d-shadow-grid">
        <!-- Intent Score -->
        <div class="d-overview-card">
          <h3>Intent Score</h3>
          <div class="d-intent-display">
            <span class="d-intent-value" :style="{ color: getIntentColor(shadowData.intent_score) }">
              {{ shadowData.intent_score }}
            </span>
            <div class="d-intent-bar">
              <div class="d-intent-fill" :style="{ width: shadowData.intent_score + '%', background: getIntentGradient(shadowData.intent_score) }"></div>
            </div>
          </div>
          <div class="d-divergence-badge" :class="shadowData.divergence_type">
            {{ formatDivergence(shadowData.divergence_type) }}
          </div>
        </div>
        
        <!-- Whale vs Crowd -->
        <div class="d-overview-card">
          <h3>Whale vs Crowd</h3>
          <div class="d-metrics-row">
            <div class="d-metric-item">
              <span class="d-metric-icon">🐋</span>
              <span class="d-metric-label">Whale Score</span>
              <span class="d-metric-value" :style="{ color: shadowData.whale_score > 50 ? '#22c55e' : '#ef4444' }">
                {{ shadowData.whale_score }}
              </span>
            </div>
            <div class="d-metric-item">
              <span class="d-metric-icon">😨</span>
              <span class="d-metric-label">Crowd Fear</span>
              <span class="d-metric-value" :style="{ color: shadowData.sentiment_score > 50 ? '#22c55e' : '#ef4444' }">
                {{ shadowData.sentiment_score }}
              </span>
            </div>
          </div>
        </div>
        
        <!-- AI Shadow Insight -->
        <div class="d-overview-card d-shadow-insight-card" v-if="shadowData.shadow_insight">
          <h3>🧠 AI Shadow Insight</h3>
          <p class="d-shadow-text">{{ shadowData.shadow_insight }}</p>
          <div v-if="shadowData.is_golden_shadow" class="d-golden-badge">
            ⚡ Golden Shadow Entry Detected
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
const api = useApi()

const signals = ref([
  { symbol: 'BTC', image: 'https://assets.coingecko.com/coins/images/1/small/bitcoin.png', price: 98500, change: 2.4, asi: 72, signal: 'BUY', reasoning: 'Strong bullish momentum, MACD positive' },
  { symbol: 'SOL', image: 'https://assets.coingecko.com/coins/images/4128/small/solana.png', price: 185, change: 5.2, asi: 78, signal: 'STRONG_BUY', reasoning: 'Network metrics ATH, breaking resistance' },
  { symbol: 'ETH', image: 'https://assets.coingecko.com/coins/images/279/small/ethereum.png', price: 3450, change: 1.8, asi: 58, signal: 'HOLD', reasoning: 'Consolidating, wait for breakout' },
  { symbol: 'DOGE', image: 'https://assets.coingecko.com/coins/images/5/small/dogecoin.png', price: 0.32, change: -2.1, asi: 35, signal: 'SELL', reasoning: 'Whale distribution detected' },
])

// Shadow data
const shadowData = ref({
  intent_score: 65,
  whale_score: 72,
  sentiment_score: 38,
  divergence_type: 'shadow_accumulation',
  shadow_insight: 'Whales are quietly accumulating while retail investors show fear. This divergence pattern historically precedes bullish momentum.',
  is_golden_shadow: true,
})

// Helper functions
const getIntentColor = (score: number) => {
  if (score >= 70) return '#22c55e'
  if (score >= 55) return '#4ade80'
  if (score <= 30) return '#ef4444'
  if (score <= 45) return '#f97316'
  return '#eab308'
}

const getIntentGradient = (score: number) => {
  if (score >= 60) return 'linear-gradient(90deg, #22c55e, #4ade80)'
  if (score <= 40) return 'linear-gradient(90deg, #ef4444, #f97316)'
  return 'linear-gradient(90deg, #eab308, #fcd34d)'
}

const formatDivergence = (divType: string) => {
  const labels: Record<string, string> = {
    shadow_accumulation: '🐋 Shadow Accumulation',
    bull_trap: '⚠️ Bull Trap',
    confirmation: '✓ Confirmation',
    neutral: '— Neutral',
  }
  return labels[divType] || divType
}

// Fetch shadow data on mount for BTC (default)
onMounted(async () => {
  try {
    const res = await api.getIntentDivergence('bitcoin')
    if (res) {
      shadowData.value = {
        intent_score: res.intent_score || 50,
        whale_score: res.whale_score || 50,
        sentiment_score: res.sentiment_score || 50,
        divergence_type: res.divergence_type || 'neutral',
        shadow_insight: res.shadow_insight || '',
        is_golden_shadow: res.is_golden_shadow || false,
      }
    }
  } catch (e) {
    console.warn('Shadow data not available:', e)
  }
})
</script>

<style scoped>
.d-analysis { padding: 24px 0; }
.d-page-title { font-size: 32px; font-weight: 700; margin: 0; }
.d-overview-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.d-shadow-grid { display: grid; grid-template-columns: 1fr 1fr 2fr; gap: 16px; }
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

/* Shadow Section Styles */
.d-intent-display { text-align: center; margin-bottom: 16px; }
.d-intent-value { font-size: 48px; font-weight: 700; display: block; }
.d-intent-bar { height: 8px; background: rgba(255,255,255,0.1); border-radius: 4px; margin-top: 12px; overflow: hidden; }
.d-intent-fill { height: 100%; border-radius: 4px; }
.d-divergence-badge { padding: 6px 14px; border-radius: 20px; font-size: 12px; font-weight: 600; text-align: center; }
.d-divergence-badge.shadow_accumulation { background: rgba(34, 197, 94, 0.2); color: #22c55e; }
.d-divergence-badge.bull_trap { background: rgba(239, 68, 68, 0.2); color: #ef4444; }
.d-divergence-badge.confirmation { background: rgba(0, 212, 255, 0.2); color: #00d4ff; }
.d-divergence-badge.neutral { background: rgba(234, 179, 8, 0.2); color: #eab308; }
.d-metrics-row { display: flex; flex-direction: column; gap: 12px; }
.d-metric-item { display: flex; align-items: center; gap: 10px; padding: 12px; background: rgba(0,0,0,0.2); border-radius: 10px; }
.d-metric-icon { font-size: 24px; }
.d-metric-label { flex: 1; font-size: 14px; color: rgba(255,255,255,0.6); }
.d-metric-value { font-size: 20px; font-weight: 700; }
.d-shadow-insight-card { border-left: 3px solid #a855f7; }
.d-shadow-text { font-size: 14px; color: rgba(255,255,255,0.75); line-height: 1.6; margin: 0 0 12px; }
.d-golden-badge { padding: 10px 16px; background: linear-gradient(135deg, rgba(234, 179, 8, 0.15), rgba(168, 85, 247, 0.1)); border: 1px solid rgba(234, 179, 8, 0.3); border-radius: 10px; font-size: 13px; font-weight: 600; color: #eab308; }
</style>

