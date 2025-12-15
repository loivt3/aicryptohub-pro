<template>
  <div class="mobile-analysis">
    <!-- Header -->
    <section class="m-section">
      <h3 class="m-section-title">📊 AI Analysis</h3>
      <p class="m-text-muted" style="font-size: 12px;">AI-powered sentiment and technical analysis</p>
    </section>

    <!-- Overall Market Sentiment -->
    <section class="m-section">
      <div class="m-sentiment-card">
        <div class="m-sentiment-header">
          <h4>Market Sentiment</h4>
          <span class="m-badge" :class="overallSentiment.class">{{ overallSentiment.label }}</span>
        </div>
        <div class="m-sentiment-gauge">
          <AsiGauge :score="overallSentiment.score" :size="120" />
        </div>
        <p class="m-sentiment-text">{{ overallSentiment.summary }}</p>
      </div>
    </section>

    <!-- Signal Distribution -->
    <section class="m-section">
      <h3 class="m-section-title">Signal Distribution</h3>
      <div class="m-signal-dist">
        <div class="m-signal-bar">
          <div class="m-signal-fill buy" :style="{ width: signalDistribution.buy + '%' }"></div>
          <div class="m-signal-fill hold" :style="{ width: signalDistribution.hold + '%' }"></div>
          <div class="m-signal-fill sell" :style="{ width: signalDistribution.sell + '%' }"></div>
        </div>
        <div class="m-signal-legend">
          <span class="buy">🟢 Buy {{ signalDistribution.buy }}%</span>
          <span class="hold">🟡 Hold {{ signalDistribution.hold }}%</span>
          <span class="sell">🔴 Sell {{ signalDistribution.sell }}%</span>
        </div>
      </div>
    </section>

    <!-- Top AI Signals -->
    <section class="m-section">
      <h3 class="m-section-title">Top AI Signals</h3>
      <div class="m-list">
        <div v-for="coin in topSignals" :key="coin.coin_id" class="m-list-item" @click="expandedCoin = expandedCoin === coin.coin_id ? null : coin.coin_id">
          <img :src="coin.image" class="m-avatar" />
          <div class="m-info">
            <span class="m-info-title">{{ coin.symbol }}</span>
            <span class="m-info-subtitle">{{ coin.name }}</span>
          </div>
          <div class="m-asi-mini">
            <div class="m-asi-bar-mini">
              <div class="m-asi-fill-mini" :class="getAsiClass(coin.asi_score)" :style="{ width: coin.asi_score + '%' }"></div>
            </div>
            <span class="m-asi-label" :class="getAsiClass(coin.asi_score)">{{ coin.asi_score }}</span>
          </div>
          <span class="m-signal-badge" :class="getSignalClass(coin.signal)">{{ coin.signal }}</span>
          <Icon name="ph:caret-right" class="w-4 h-4 opacity-30" :class="{ 'rotate-90': expandedCoin === coin.coin_id }" />
        </div>
        
        <!-- Expanded Panel -->
        <div v-if="expandedCoin === coin.coin_id" v-for="coin in topSignals.filter(c => c.coin_id === expandedCoin)" :key="'exp-'+coin.coin_id" class="m-accordion-panel">
          <div class="m-ai-box">
            <div class="m-ai-box-header">
              <Icon name="ph:robot" class="w-4 h-4" />
              <span>AI ANALYSIS</span>
            </div>
            <p class="m-ai-box-text">{{ coin.reasoning }}</p>
          </div>
          
          <div class="m-stats-grid">
            <div class="m-stat-item">
              <span class="m-stat-label">RSI</span>
              <span class="m-stat-value">{{ coin.rsi }}</span>
            </div>
            <div class="m-stat-item">
              <span class="m-stat-label">MACD</span>
              <span class="m-stat-value" :class="coin.macd >= 0 ? 'm-text-success' : 'm-text-danger'">{{ coin.macd }}</span>
            </div>
            <div class="m-stat-item">
              <span class="m-stat-label">Volume</span>
              <span class="m-stat-value">{{ coin.volume_change }}%</span>
            </div>
          </div>
        </div>
      </div>
    </section>
    
    <div class="m-bottom-spacer"></div>
  </div>
</template>

<script setup lang="ts">
const expandedCoin = ref<string | null>(null)

const overallSentiment = computed(() => ({
  score: 68,
  label: 'Bullish',
  class: 'm-badge-success',
  summary: 'Market shows strong bullish momentum with 68% of coins showing positive signals. Bitcoin leading the rally with institutional interest.'
}))

const signalDistribution = ref({
  buy: 52,
  hold: 35,
  sell: 13
})

const topSignals = ref([
  { coin_id: 'bitcoin', symbol: 'BTC', name: 'Bitcoin', image: 'https://assets.coingecko.com/coins/images/1/small/bitcoin.png', asi_score: 72, signal: 'BUY', reasoning: 'Strong bullish momentum with RSI at 62. MACD showing positive crossover. Institutional accumulation detected.', rsi: 62, macd: 125, volume_change: 24 },
  { coin_id: 'ethereum', symbol: 'ETH', name: 'Ethereum', image: 'https://assets.coingecko.com/coins/images/279/small/ethereum.png', asi_score: 58, signal: 'HOLD', reasoning: 'Consolidating near resistance. Wait for breakout confirmation above $3500 for entry.', rsi: 55, macd: 45, volume_change: -8 },
  { coin_id: 'solana', symbol: 'SOL', name: 'Solana', image: 'https://assets.coingecko.com/coins/images/4128/small/solana.png', asi_score: 78, signal: 'STRONG_BUY', reasoning: 'Exceptional momentum with network metrics hitting ATH. Strong L1 narrative support.', rsi: 68, macd: 280, volume_change: 45 },
  { coin_id: 'cardano', symbol: 'ADA', name: 'Cardano', image: 'https://assets.coingecko.com/coins/images/975/small/cardano.png', asi_score: 65, signal: 'BUY', reasoning: 'Hydra scaling progress driving positive sentiment. Breaking out of accumulation zone.', rsi: 58, macd: 78, volume_change: 18 },
  { coin_id: 'dogecoin', symbol: 'DOGE', name: 'Dogecoin', image: 'https://assets.coingecko.com/coins/images/5/small/dogecoin.png', asi_score: 35, signal: 'SELL', reasoning: 'Meme coin narrative weakening. Whale distribution detected. Risk of further downside.', rsi: 42, macd: -55, volume_change: -22 },
])

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
.mobile-analysis {
  padding: 0;
}

.m-sentiment-card {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(56, 239, 235, 0.1) 100%);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 16px;
  text-align: center;
}

.m-sentiment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.m-sentiment-header h4 {
  font-size: 14px;
  font-weight: 600;
  color: #ffffff;
  margin: 0;
}

.m-sentiment-gauge {
  display: flex;
  justify-content: center;
  margin-bottom: 16px;
}

.m-sentiment-text {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.5;
  margin: 0;
}

/* Signal Distribution */
.m-signal-dist {
  background: rgba(255, 255, 255, 0.04);
  border-radius: 12px;
  padding: 16px;
}

.m-signal-bar {
  height: 8px;
  border-radius: 4px;
  display: flex;
  overflow: hidden;
  margin-bottom: 12px;
}

.m-signal-fill {
  height: 100%;
  transition: width 0.3s ease;
}

.m-signal-fill.buy { background: #22c55e; }
.m-signal-fill.hold { background: #f97316; }
.m-signal-fill.sell { background: #ef4444; }

.m-signal-legend {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
}

.m-signal-legend .buy { color: #22c55e; }
.m-signal-legend .hold { color: #f97316; }
.m-signal-legend .sell { color: #ef4444; }

/* ASI Mini Bar */
.m-asi-mini {
  display: flex;
  align-items: center;
  gap: 6px;
}

.m-asi-bar-mini {
  width: 40px;
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
  overflow: hidden;
}

.m-asi-fill-mini {
  height: 100%;
  border-radius: 2px;
}

.m-asi-fill-mini.positive { background: linear-gradient(90deg, #22c55e, #4ade80); }
.m-asi-fill-mini.negative { background: linear-gradient(90deg, #ef4444, #f87171); }
.m-asi-fill-mini.neutral { background: linear-gradient(90deg, #f97316, #fb923c); }

.m-asi-label {
  font-size: 11px;
  font-weight: 600;
  min-width: 20px;
}

.m-asi-label.positive { color: #22c55e; }
.m-asi-label.negative { color: #ef4444; }
.m-asi-label.neutral { color: #f97316; }

/* Signal Badge */
.m-signal-badge {
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
}

.m-signal-badge.buy {
  background: rgba(34, 197, 94, 0.2);
  color: #22c55e;
}

.m-signal-badge.sell {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.m-signal-badge.hold {
  background: rgba(249, 115, 22, 0.2);
  color: #f97316;
}

/* Stats Grid */
.m-stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.m-stat-item {
  background: rgba(255, 255, 255, 0.04);
  border-radius: 6px;
  padding: 8px;
  text-align: center;
}

.m-stat-label {
  font-size: 9px;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
  display: block;
  margin-bottom: 2px;
}

.m-stat-value {
  font-size: 14px;
  font-weight: 600;
  color: #ffffff;
}

/* AI Box */
.m-ai-box {
  background: rgba(139, 92, 246, 0.1);
  border: 1px solid rgba(139, 92, 246, 0.2);
  border-radius: 8px;
  padding: 10px;
  margin-bottom: 12px;
}

.m-ai-box-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 6px;
  font-size: 10px;
  font-weight: 600;
  color: #a78bfa;
  text-transform: uppercase;
}

.m-ai-box-text {
  font-size: 12px;
  line-height: 1.5;
  color: rgba(255, 255, 255, 0.85);
  margin: 0;
}

.m-accordion-panel {
  padding: 12px;
  background: rgba(255, 255, 255, 0.02);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.rotate-90 {
  transform: rotate(90deg);
}
</style>
