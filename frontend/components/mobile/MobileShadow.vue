<template>
  <div class="mobile-shadow">
    <!-- Header -->
    <div class="shadow-header">
      <h1 class="page-title">
        <span class="title-icon">👁️</span>
        Shadow Analysis
      </h1>
      <p class="page-subtitle">Intent Divergence Engine</p>
    </div>

    <!-- Coin Selector -->
    <div class="coin-selector">
      <button 
        v-for="coin in topCoins" 
        :key="coin.id"
        class="coin-btn"
        :class="{ active: selectedCoin === coin.id }"
        @click="selectCoin(coin.id, coin.symbol)"
      >
        <img :src="coin.image" :alt="coin.symbol" class="coin-img" />
        <span>{{ coin.symbol }}</span>
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Analyzing whale behavior...</p>
    </div>

    <!-- Shadow Radar Component -->
    <ShadowRadar 
      v-else
      :coin-id="selectedCoin"
      :divergence-data="divergenceData"
      @golden-shadow="handleGoldenShadow"
    />

    <!-- Historical Divergence -->
    <div class="history-section" v-if="divergenceHistory.length">
      <h3 class="section-title">
        <span>📜</span> Recent Divergence Signals
      </h3>
      <div class="history-list">
        <div 
          v-for="item in divergenceHistory" 
          :key="item.id"
          class="history-item"
          :class="`type-${item.divergence_type}`"
        >
          <div class="history-icon">
            {{ getIcon(item.divergence_type) }}
          </div>
          <div class="history-content">
            <div class="history-label">{{ item.divergence_label || formatType(item.divergence_type) }}</div>
            <div class="history-meta">
              <span class="history-score">Intent: {{ item.intent_score }}/100</span>
              <span class="history-time">{{ formatTime(item.timestamp) }}</span>
            </div>
          </div>
          <div class="history-sentiment" :class="getSentimentClass(item.sentiment_score)">
            {{ item.sentiment_score }}
          </div>
        </div>
      </div>
    </div>

    <!-- How It Works -->
    <div class="how-it-works">
      <h3 class="section-title">
        <span>💡</span> How Shadow Analysis Works
      </h3>
      <div class="explainer-cards">
        <div class="explainer-card">
          <div class="explainer-icon">🐋</div>
          <div class="explainer-title">Whale Tracking</div>
          <div class="explainer-text">Monitor large wallet movements and exchange flows</div>
        </div>
        <div class="explainer-card">
          <div class="explainer-icon">😨</div>
          <div class="explainer-title">Crowd Sentiment</div>
          <div class="explainer-text">Analyze market fear & greed from news + social</div>
        </div>
        <div class="explainer-card">
          <div class="explainer-icon">⚡</div>
          <div class="explainer-title">Intent Divergence</div>
          <div class="explainer-text">Detect when whales act opposite to crowd</div>
        </div>
      </div>
    </div>

    <!-- Intent Alert (toast) -->
    <IntentAlert
      v-if="showAlert"
      :alert-type="alertData.type"
      :coin-id="alertData.coinId"
      :coin-symbol="alertData.symbol"
      :intent-score="alertData.intentScore"
      :message="alertData.message"
      @dismiss="showAlert = false"
      @click="handleAlertClick"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

// Components
import ShadowRadar from './ShadowRadar.vue'
import IntentAlert from '../shared/IntentAlert.vue'

// State
const selectedCoin = ref('bitcoin')
const selectedSymbol = ref('BTC')
const loading = ref(false)
const divergenceData = ref(null)
const divergenceHistory = ref([])
const showAlert = ref(false)
const alertData = ref({})

// Top coins for quick selection
const topCoins = ref([
  { id: 'bitcoin', symbol: 'BTC', image: 'https://assets.coingecko.com/coins/images/1/small/bitcoin.png' },
  { id: 'ethereum', symbol: 'ETH', image: 'https://assets.coingecko.com/coins/images/279/small/ethereum.png' },
  { id: 'solana', symbol: 'SOL', image: 'https://assets.coingecko.com/coins/images/4128/small/solana.png' },
  { id: 'binancecoin', symbol: 'BNB', image: 'https://assets.coingecko.com/coins/images/825/small/bnb-icon2_2x.png' },
])

// WebSocket for real-time alerts
let socket = null

// Methods
async function selectCoin(coinId, symbol) {
  selectedCoin.value = coinId
  selectedSymbol.value = symbol
  await fetchDivergence()
}

async function fetchDivergence() {
  loading.value = true
  try {
    const response = await fetch(`/api/v1/intent-divergence/${selectedCoin.value}`)
    if (response.ok) {
      divergenceData.value = await response.json()
    }
  } catch (error) {
    console.error('Failed to fetch divergence:', error)
  } finally {
    loading.value = false
  }
}

async function fetchHistory() {
  try {
    const response = await fetch(`/api/v1/intent-divergence/history?limit=5`)
    if (response.ok) {
      divergenceHistory.value = await response.json()
    }
  } catch (error) {
    console.error('Failed to fetch history:', error)
  }
}

function handleGoldenShadow(data) {
  alertData.value = {
    type: 'golden_shadow',
    coinId: data.coin_id,
    symbol: selectedSymbol.value,
    intentScore: data.intent_score,
    message: data.shadow_insight || 'High-confidence divergence detected!'
  }
  showAlert.value = true
}

function handleAlertClick(data) {
  // Navigate to coin or show detail
  showAlert.value = false
}

function setupWebSocket() {
  // Connect to real-time intent alerts
  try {
    const wsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws/intent-alerts`
    socket = new WebSocket(wsUrl)
    
    socket.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (data.type === 'golden_shadow' || data.is_golden_shadow) {
        alertData.value = {
          type: data.divergence_type || 'golden_shadow',
          coinId: data.coin_id,
          symbol: data.symbol || 'COIN',
          intentScore: data.intent_score,
          message: data.shadow_insight || 'New divergence signal detected!'
        }
        showAlert.value = true
      }
    }
  } catch (error) {
    console.warn('WebSocket not available:', error)
  }
}

// Helpers
function getIcon(type) {
  const icons = {
    'shadow_accumulation': '🟢',
    'bull_trap': '🔴',
    'confirmation': '🔵',
    'neutral': '⚪'
  }
  return icons[type] || '📊'
}

function formatType(type) {
  const labels = {
    'shadow_accumulation': 'Shadow Accumulation',
    'bull_trap': 'Bull Trap',
    'confirmation': 'Confirmation',
    'neutral': 'Neutral'
  }
  return labels[type] || type
}

function formatTime(timestamp) {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  const now = new Date()
  const diff = (now - date) / 1000 / 60 // minutes
  
  if (diff < 60) return `${Math.round(diff)}m ago`
  if (diff < 1440) return `${Math.round(diff / 60)}h ago`
  return date.toLocaleDateString()
}

function getSentimentClass(score) {
  if (score >= 60) return 'sentiment-bullish'
  if (score <= 40) return 'sentiment-bearish'
  return 'sentiment-neutral'
}

// Lifecycle
onMounted(() => {
  fetchDivergence()
  fetchHistory()
  setupWebSocket()
})

onUnmounted(() => {
  if (socket) {
    socket.close()
  }
})
</script>

<style scoped>
.mobile-shadow {
  min-height: 100vh;
  background: linear-gradient(180deg, #0a0a1a 0%, #12122a 100%);
  padding: 16px;
  padding-bottom: 100px;
}

.shadow-header {
  text-align: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 800;
  color: #fff;
  margin: 0 0 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.title-icon {
  font-size: 28px;
}

.page-subtitle {
  font-size: 13px;
  color: #8b8fa3;
  margin: 0;
}

.coin-selector {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 8px;
  margin-bottom: 20px;
  -webkit-overflow-scrolling: touch;
}

.coin-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 24px;
  color: #8b8fa3;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.coin-btn.active {
  background: rgba(0, 212, 255, 0.15);
  border-color: rgba(0, 212, 255, 0.5);
  color: #00d4ff;
}

.coin-img {
  width: 20px;
  height: 20px;
  border-radius: 50%;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #8b8fa3;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(0, 212, 255, 0.2);
  border-top-color: #00d4ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 700;
  color: #fff;
  margin: 24px 0 16px;
}

.history-section {
  margin-top: 24px;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  border-left: 3px solid;
}

.type-shadow_accumulation { border-left-color: #00ff88; }
.type-bull_trap { border-left-color: #ff4444; }
.type-confirmation { border-left-color: #00d4ff; }
.type-neutral { border-left-color: #8b8fa3; }

.history-icon {
  font-size: 20px;
}

.history-content {
  flex: 1;
}

.history-label {
  font-size: 14px;
  font-weight: 600;
  color: #fff;
  margin-bottom: 4px;
}

.history-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #8b8fa3;
}

.history-sentiment {
  font-size: 14px;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 8px;
}

.sentiment-bullish { 
  background: rgba(0, 255, 136, 0.15); 
  color: #00ff88; 
}
.sentiment-bearish { 
  background: rgba(255, 68, 68, 0.15); 
  color: #ff4444; 
}
.sentiment-neutral { 
  background: rgba(139, 143, 163, 0.15); 
  color: #8b8fa3; 
}

.how-it-works {
  margin-top: 24px;
}

.explainer-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.explainer-card {
  padding: 16px 10px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  text-align: center;
}

.explainer-icon {
  font-size: 28px;
  margin-bottom: 8px;
}

.explainer-title {
  font-size: 12px;
  font-weight: 700;
  color: #fff;
  margin-bottom: 6px;
}

.explainer-text {
  font-size: 10px;
  color: #8b8fa3;
  line-height: 1.4;
}
</style>
