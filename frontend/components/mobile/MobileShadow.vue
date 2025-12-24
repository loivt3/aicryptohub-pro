<template>
  <div class="mobile-shadow">
    <!-- Shared Header -->
    <SharedMobileHeader 
      :active-tab="activeTab" 
      @set-tab="emit('setTab', $event)" 
      @open-search="emit('openSearch')" 
    />

    <!-- Main Content -->
    <main class="m-main">
      <!-- Hero Stats Cards -->
      <section class="m-section">
        <div class="m-stats-scroll">
          <div class="m-stats-container">
            <!-- Whale Activity Card -->
            <div class="m-stat-card-pro">
              <div class="m-stat-header">
                <span class="m-stat-label">🐋 WHALE ACTIVITY</span>
                <span class="m-stat-change" :class="whaleFlowDirection">
                  {{ whaleFlowDirection === 'positive' ? '▲ IN' : '▼ OUT' }}
                </span>
              </div>
              <div class="m-stat-value-large">{{ formatWhaleFlow(divergenceData?.whale_net_flow_usd) }}</div>
              <div class="m-stat-sparkline">
                <svg viewBox="0 0 120 40" preserveAspectRatio="none">
                  <defs>
                    <linearGradient id="whaleGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                      <stop offset="0%" :stop-color="whaleFlowDirection === 'positive' ? 'rgba(34, 197, 94, 0.5)' : 'rgba(239, 68, 68, 0.5)'" />
                      <stop offset="100%" stop-color="rgba(0, 0, 0, 0)" />
                    </linearGradient>
                  </defs>
                  <path d="M0,30 C10,28 20,22 30,20 C40,18 50,25 60,18 C70,12 80,16 90,10 C100,6 110,14 120,8 L120,40 L0,40 Z" fill="url(#whaleGrad)" />
                  <path d="M0,30 C10,28 20,22 30,20 C40,18 50,25 60,18 C70,12 80,16 90,10 C100,6 110,14 120,8" fill="none" :stroke="whaleFlowDirection === 'positive' ? '#22c55e' : '#ef4444'" stroke-width="2" stroke-linecap="round"/>
                </svg>
              </div>
            </div>

            <!-- Crowd Sentiment Card -->
            <div class="m-stat-card-pro">
              <div class="m-stat-header">
                <span class="m-stat-label">😨 CROWD FEAR</span>
                <span class="m-stat-change" :class="crowdSentimentClass">
                  {{ crowdSentimentLabel }}
                </span>
              </div>
              <div class="m-stat-value-large">{{ divergenceData?.sentiment_score || 50 }}/100</div>
              <div class="m-sentiment-bar">
                <div class="m-sentiment-fill" :style="{ width: (divergenceData?.sentiment_score || 50) + '%' }" :class="crowdSentimentClass"></div>
              </div>
            </div>

            <!-- Intent Score Gauge -->
            <div class="m-stat-card-pro" style="min-width: 130px;">
              <div class="m-stat-header">
                <span class="m-stat-label">⚡ INTENT SCORE</span>
              </div>
              <div class="m-gauge-wrapper">
                <svg viewBox="0 0 100 50" class="m-gauge-svg">
                  <defs>
                    <linearGradient id="intentGaugeGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                      <stop offset="0%" stop-color="#ef4444" />
                      <stop offset="25%" stop-color="#f97316" />
                      <stop offset="50%" stop-color="#eab308" />
                      <stop offset="75%" stop-color="#84cc16" />
                      <stop offset="100%" stop-color="#22c55e" />
                    </linearGradient>
                  </defs>
                  <path d="M 10 45 A 40 40 0 0 1 90 45" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="6" stroke-linecap="round"/>
                  <path d="M 10 45 A 40 40 0 0 1 90 45" fill="none" stroke="url(#intentGaugeGrad)" stroke-width="6" stroke-linecap="round"/>
                  <line :x1="50" :y1="45" :x2="50 + 25 * Math.cos((180 - (divergenceData?.intent_score || 50) * 1.8) * Math.PI / 180)" :y2="45 - 25 * Math.sin((180 - (divergenceData?.intent_score || 50) * 1.8) * Math.PI / 180)" stroke="#fff" stroke-width="2" stroke-linecap="round"/>
                  <circle cx="50" cy="45" r="3" fill="#1a1f2e" stroke="#fff" stroke-width="1"/>
                </svg>
              </div>
              <div class="m-gauge-value">
                <span class="m-gauge-number" :class="intentScoreClass">{{ divergenceData?.intent_score || 50 }}</span>
                <span class="m-gauge-label">{{ intentLabel }}</span>
              </div>
            </div>

            <!-- Divergence Type Card -->
            <div class="m-stat-card-pro">
              <div class="m-stat-header">
                <span class="m-stat-label">🎯 DIVERGENCE</span>
              </div>
              <div class="m-divergence-badge" :class="divergenceBadgeClass">
                {{ divergenceData?.divergence_label || 'Analyzing...' }}
              </div>
              <div class="m-divergence-desc">
                {{ getDivergenceDescription(divergenceData?.divergence_type) }}
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Coin Selector -->
      <section class="m-section">
        <div class="m-section-header">
          <h3 class="m-section-title">
            <Icon name="ph:coins" class="w-4 h-4" style="color: #a855f7;" />
            Select Asset
          </h3>
        </div>
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
      </section>

      <!-- Loading State -->
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Analyzing whale behavior...</p>
      </div>

      <!-- Shadow Radar Chart -->
      <template v-else>
        <!-- Radar Chart Section -->
        <section class="m-section">
          <div class="m-section-header">
            <h3 class="m-section-title">
              <Icon name="ph:radar" class="w-4 h-4" style="color: #00d4ff;" />
              Intent Radar
            </h3>
          </div>
          <div class="radar-chart-container">
            <ShadowRadar 
              :coin-id="selectedCoin"
              :divergence-data="divergenceData"
              @golden-shadow="handleGoldenShadow"
            />
          </div>
        </section>

        <!-- Whale Profiles -->
        <section class="m-section" v-if="divergenceData?.active_whale_profiles?.length">
          <div class="m-section-header">
            <h3 class="m-section-title">
              <Icon name="ph:users-three" class="w-4 h-4" style="color: #f97316;" />
              Active Whale Profiles
            </h3>
          </div>
          <div class="whale-profiles-grid">
            <div 
              v-for="profile in divergenceData.active_whale_profiles" 
              :key="profile.behavior"
              class="whale-profile-card"
              :class="`profile-${profile.behavior}`"
            >
              <div class="profile-icon">{{ getProfileIcon(profile.behavior) }}</div>
              <div class="profile-info">
                <span class="profile-name">{{ formatBehavior(profile.behavior) }}</span>
                <span class="profile-count">{{ profile.count }} whales</span>
              </div>
              <div class="profile-trend" :class="getProfileTrend(profile.behavior)">
                {{ getProfileTrendIcon(profile.behavior) }}
              </div>
            </div>
          </div>
        </section>

        <!-- Shadow Insight AI Box -->
        <section class="m-section" v-if="divergenceData?.shadow_insight">
          <div class="m-ai-box">
            <div class="m-ai-box-header">
              <Icon name="ph:brain" class="w-4 h-4" />
              <span>AI SHADOW INSIGHT</span>
            </div>
            <p class="m-ai-box-text">{{ divergenceData.shadow_insight }}</p>
            <div class="m-ai-action-hint" v-if="divergenceData.action_hint">
              <span class="hint-label">💡 Action:</span>
              <span class="hint-text">{{ divergenceData.action_hint }}</span>
            </div>
          </div>
        </section>

        <!-- Golden Shadow Alert -->
        <section class="m-section" v-if="divergenceData?.is_golden_shadow">
          <div class="golden-shadow-banner">
            <div class="golden-icon">⚡</div>
            <div class="golden-content">
              <strong>Golden Shadow Entry Detected!</strong>
              <span>High-confidence whale-crowd divergence signal</span>
            </div>
          </div>
        </section>

        <!-- Exchange Flow Stats (NEW) -->
        <section class="m-section">
          <div class="m-section-header">
            <h3 class="m-section-title">
              <Icon name="ph:arrows-left-right" class="w-4 h-4" style="color: #38bdf8;" />
              Exchange Flow
            </h3>
          </div>
          <div class="m-flow-cards">
            <div class="m-flow-card m-flow-inflow">
              <div class="m-flow-icon">📥</div>
              <div class="m-flow-info">
                <span class="m-flow-label">Inflow (24h)</span>
                <span class="m-flow-value danger">{{ formatCurrency(exchangeInflow) }}</span>
              </div>
            </div>
            <div class="m-flow-card m-flow-outflow">
              <div class="m-flow-icon">📤</div>
              <div class="m-flow-info">
                <span class="m-flow-label">Outflow (24h)</span>
                <span class="m-flow-value success">{{ formatCurrency(exchangeOutflow) }}</span>
              </div>
            </div>
          </div>
        </section>

        <!-- Recent Whale Transactions (NEW) -->
        <section class="m-section" v-if="whaleTransactions.length">
          <div class="m-section-header">
            <h3 class="m-section-title">
              <Icon name="ph:list-magnifying-glass" class="w-4 h-4" style="color: #a855f7;" />
              Recent Whale Txs
            </h3>
            <span class="m-section-link" @click="fetchOnchainData">Refresh</span>
          </div>
          <div class="m-whale-tx-list">
            <div 
              v-for="(tx, idx) in whaleTransactions" 
              :key="idx"
              class="m-whale-tx-item"
              :class="tx.tx_type === 'exchange_deposit' ? 'tx-sell' : 'tx-buy'"
            >
              <div class="m-tx-icon">{{ tx.tx_type === 'exchange_deposit' ? '🔴' : '🟢' }}</div>
              <div class="m-tx-info">
                <span class="m-tx-coin">{{ tx.coin_id?.toUpperCase() }}</span>
                <span class="m-tx-addresses">
                  {{ formatAddress(tx.from_address) }} → {{ tx.exchange_name || formatAddress(tx.to_address) }}
                </span>
              </div>
              <div class="m-tx-meta">
                <span class="m-tx-value">{{ formatCurrency(tx.value_usd) }}</span>
                <span class="m-tx-time">{{ formatTxTime(tx.tx_timestamp) }}</span>
              </div>
            </div>
          </div>
        </section>

        <!-- Historical Divergence Signals -->
        <section class="m-section">
          <div class="m-section-header">
            <h3 class="m-section-title">
              <Icon name="ph:clock-counter-clockwise" class="w-4 h-4" style="color: #8b5cf6;" />
              Recent Signals
            </h3>
            <span class="m-section-link" @click="fetchHistory">Refresh</span>
          </div>
          
          <div v-if="divergenceHistory.length" class="m-list m-list--dark">
            <div 
              v-for="item in divergenceHistory" 
              :key="item.id"
              class="m-list-item m-list-item--signal"
              :class="`signal-${item.divergence_type}`"
            >
              <div class="signal-icon">{{ getIcon(item.divergence_type) }}</div>
              <div class="signal-content">
                <span class="signal-label">{{ item.divergence_label || formatType(item.divergence_type) }}</span>
                <span class="signal-meta">
                  <span class="signal-coin">{{ item.symbol || item.coin_id }}</span>
                  <span class="signal-time">{{ formatTime(item.timestamp) }}</span>
                </span>
              </div>
              <div class="signal-score" :class="getScoreClass(item.intent_score)">
                {{ item.intent_score }}
              </div>
            </div>
          </div>
          
          <div v-else class="empty-state">
            <Icon name="ph:clock" class="empty-icon" />
            <p>No recent signals detected</p>
          </div>
        </section>

        <!-- How It Works (Minimized) -->
        <section class="m-section">
          <div class="m-section-header">
            <h3 class="m-section-title">
              <Icon name="ph:info" class="w-4 h-4" style="color: #38efeb;" />
              How It Works
            </h3>
            <button class="m-section-link" @click="showExplainer = !showExplainer">
              {{ showExplainer ? 'Hide' : 'Learn' }}
            </button>
          </div>
          
          <div v-if="showExplainer" class="explainer-grid">
            <div class="explainer-card">
              <div class="explainer-icon">🐋</div>
              <div class="explainer-title">Whale Tracking</div>
              <div class="explainer-text">Monitor large wallet movements and exchange flows in real-time</div>
            </div>
            <div class="explainer-card">
              <div class="explainer-icon">😨</div>
              <div class="explainer-title">Crowd Sentiment</div>
              <div class="explainer-text">Analyze market fear & greed from news + social media</div>
            </div>
            <div class="explainer-card">
              <div class="explainer-icon">⚡</div>
              <div class="explainer-title">Intent Divergence</div>
              <div class="explainer-text">Detect when whales act opposite to crowd - buy signals</div>
            </div>
            <div class="explainer-card">
              <div class="explainer-icon">🎯</div>
              <div class="explainer-title">Golden Shadow</div>
              <div class="explainer-text">High-confidence entry when all signals align perfectly</div>
            </div>
          </div>
        </section>
      </template>

      <div class="m-bottom-spacer"></div>
    </main>

    <!-- Bottom Navigation (using SharedMobileFooter for consistent routing) -->
    <SharedMobileFooter />

    <!-- Intent Alert Toast -->
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
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useSocket } from '~/composables/useSocket'

// Components
import ShadowRadar from './ShadowRadar.vue'
import IntentAlert from '../shared/IntentAlert.vue'

// Props & Emits
const props = defineProps({
  activeTab: { type: String, default: 'shadow' }
})

const emit = defineEmits(['setTab', 'openSearch'])

// Header data
const btcPrice = ref(98500)
const btcChange = ref(2.4)
const alertCount = ref(3)

// Helper function for currency formatting
const formatCurrency = (n, decimals = 2) => {
  if (!n) return '$--'
  if (n >= 1e12) return '$' + (n / 1e12).toFixed(decimals) + 'T'
  if (n >= 1e9) return '$' + (n / 1e9).toFixed(decimals) + 'B'
  if (n >= 1e6) return '$' + (n / 1e6).toFixed(decimals) + 'M'
  if (n >= 1) return '$' + n.toLocaleString('en-US', { minimumFractionDigits: decimals, maximumFractionDigits: decimals })
  return '$' + n.toFixed(6)
}

// State
const selectedCoin = ref('bitcoin')
const selectedSymbol = ref('BTC')
const loading = ref(false)
const divergenceData = ref(null)
const divergenceHistory = ref([])
const showAlert = ref(false)
const alertData = ref({})
const showExplainer = ref(false)

// Onchain data state
const onchainSummary = ref(null)
const whaleTransactions = ref([])
const exchangeInflow = ref(0)
const exchangeOutflow = ref(0)

// Top coins for quick selection
const topCoins = ref([
  { id: 'bitcoin', symbol: 'BTC', image: 'https://assets.coingecko.com/coins/images/1/small/bitcoin.png' },
  { id: 'ethereum', symbol: 'ETH', image: 'https://assets.coingecko.com/coins/images/279/small/ethereum.png' },
  { id: 'solana', symbol: 'SOL', image: 'https://assets.coingecko.com/coins/images/4128/small/solana.png' },
  { id: 'binancecoin', symbol: 'BNB', image: 'https://assets.coingecko.com/coins/images/825/small/bnb-icon2_2x.png' },
  { id: 'ripple', symbol: 'XRP', image: 'https://assets.coingecko.com/coins/images/44/small/xrp-symbol-white-128.png' },
])

// Get API base from runtime config
const config = useRuntimeConfig()
const apiBase = config.public.apiBase

// Socket.IO for real-time alerts
const { connect: connectSocket, onIntentAlert, disconnect: disconnectSocket } = useSocket()
let unsubscribeAlert = null

// Computed properties
const overallSignal = computed(() => {
  if (!divergenceData.value) return 'ANALYZING'
  const type = divergenceData.value.divergence_type
  if (type === 'shadow_accumulation') return 'BULLISH'
  if (type === 'bull_trap') return 'BEARISH'
  if (type === 'confirmation') return 'NEUTRAL'
  return 'NEUTRAL'
})

const overallSignalClass = computed(() => {
  const signal = overallSignal.value
  if (signal === 'BULLISH') return 'signal-bullish'
  if (signal === 'BEARISH') return 'signal-bearish'
  return 'signal-neutral'
})

const whaleFlowDirection = computed(() => {
  const flow = divergenceData.value?.whale_net_flow_usd || 0
  return flow >= 0 ? 'positive' : 'negative'
})

const crowdSentimentClass = computed(() => {
  const score = divergenceData.value?.sentiment_score || 50
  if (score >= 60) return 'positive'
  if (score <= 40) return 'negative'
  return 'neutral'
})

const crowdSentimentLabel = computed(() => {
  const score = divergenceData.value?.sentiment_score || 50
  if (score >= 70) return 'GREEDY'
  if (score >= 55) return 'GREED'
  if (score >= 45) return 'NEUTRAL'
  if (score >= 30) return 'FEAR'
  return 'PANIC'
})

const intentScoreClass = computed(() => {
  const score = divergenceData.value?.intent_score || 50
  if (score >= 70) return 'greed'
  if (score >= 50) return 'neutral'
  return 'fear'
})

const intentLabel = computed(() => {
  const score = divergenceData.value?.intent_score || 50
  if (score >= 80) return 'Very Strong'
  if (score >= 60) return 'Strong'
  if (score >= 40) return 'Moderate'
  return 'Weak'
})

const divergenceBadgeClass = computed(() => {
  const type = divergenceData.value?.divergence_type || 'neutral'
  return {
    'badge-accumulation': type === 'shadow_accumulation',
    'badge-trap': type === 'bull_trap',
    'badge-confirmation': type === 'confirmation',
    'badge-neutral': type === 'neutral'
  }
})

// Methods
async function selectCoin(coinId, symbol) {
  selectedCoin.value = coinId
  selectedSymbol.value = symbol
  await fetchDivergence()
}

async function fetchDivergence() {
  loading.value = true
  try {
    const response = await fetch(`${apiBase}/intent-divergence/${selectedCoin.value}`)
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
    const response = await fetch(`${apiBase}/intent-divergence/history?limit=5`)
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
  showAlert.value = false
}

function setupWebSocket() {
  connectSocket()
  
  unsubscribeAlert = onIntentAlert((data) => {
    if (data.divergence_type === 'golden_shadow' || data.is_golden_shadow) {
      alertData.value = {
        type: data.divergence_type || 'golden_shadow',
        coinId: data.coin_id,
        symbol: data.symbol || 'COIN',
        intentScore: data.intent_score,
        message: data.shadow_insight || 'New divergence signal detected!'
      }
      showAlert.value = true
    }
  })
}

// Helpers
function formatWhaleFlow(flow) {
  if (!flow) return '$0'
  const absFlow = Math.abs(flow)
  if (absFlow >= 1e9) return '$' + (absFlow / 1e9).toFixed(1) + 'B'
  if (absFlow >= 1e6) return '$' + (absFlow / 1e6).toFixed(1) + 'M'
  if (absFlow >= 1e3) return '$' + (absFlow / 1e3).toFixed(0) + 'K'
  return '$' + absFlow.toFixed(0)
}

function getDivergenceDescription(type) {
  const descriptions = {
    'shadow_accumulation': 'Whales buying while crowd sells',
    'bull_trap': 'Whales selling while crowd buys',
    'confirmation': 'Both sides moving together',
    'neutral': 'No clear divergence pattern'
  }
  return descriptions[type] || 'Analyzing patterns...'
}

function getProfileIcon(behavior) {
  const icons = {
    'value_hunter': '🎯',
    'accumulator': '📈',
    'distributor': '📉',
    'panic_seller': '😱',
    'mixed': '🔀',
    'unknown': '❓'
  }
  return icons[behavior] || '🐋'
}

function formatBehavior(behavior) {
  const labels = {
    'value_hunter': 'Value Hunter',
    'accumulator': 'Accumulator',
    'distributor': 'Distributor',
    'panic_seller': 'Panic Seller',
    'mixed': 'Mixed',
    'unknown': 'Unknown'
  }
  return labels[behavior] || behavior
}

function getProfileTrend(behavior) {
  if (['value_hunter', 'accumulator'].includes(behavior)) return 'bullish'
  if (['distributor', 'panic_seller'].includes(behavior)) return 'bearish'
  return 'neutral'
}

function getProfileTrendIcon(behavior) {
  if (['value_hunter', 'accumulator'].includes(behavior)) return '↑'
  if (['distributor', 'panic_seller'].includes(behavior)) return '↓'
  return '→'
}

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
  const diff = (now - date) / 1000 / 60
  
  if (diff < 60) return `${Math.round(diff)}m ago`
  if (diff < 1440) return `${Math.round(diff / 60)}h ago`
  return date.toLocaleDateString()
}

function getScoreClass(score) {
  if (score >= 70) return 'score-high'
  if (score >= 50) return 'score-mid'
  return 'score-low'
}

// Fetch onchain summary data
async function fetchOnchainData() {
  try {
    const response = await fetch(`${apiBase}/onchain/summary`)
    if (response.ok) {
      const data = await response.json()
      onchainSummary.value = data
      whaleTransactions.value = data.recent_whale_txs?.slice(0, 5) || []
      exchangeInflow.value = data.total_inflow_24h || 0
      exchangeOutflow.value = data.total_outflow_24h || 0
    }
  } catch (error) {
    console.error('Failed to fetch onchain data:', error)
  }
}

function formatTxTime(timestamp) {
  if (!timestamp) return '-'
  const date = new Date(timestamp)
  const now = new Date()
  const diff = (now - date) / 1000 / 60
  if (diff < 60) return `${Math.round(diff)}m ago`
  if (diff < 1440) return `${Math.round(diff / 60)}h ago`
  return `${Math.floor(diff / 1440)}d ago`
}

function formatAddress(addr) {
  if (!addr) return 'Unknown'
  if (addr.length > 12) return `${addr.slice(0, 6)}...${addr.slice(-4)}`
  return addr
}

// Lifecycle
onMounted(() => {
  fetchDivergence()
  fetchHistory()
  fetchOnchainData()
  setupWebSocket()
})

onUnmounted(() => {
  if (unsubscribeAlert) {
    unsubscribeAlert()
  }
})
</script>

<style scoped>
.mobile-shadow {
  min-height: 100vh;
  background: linear-gradient(180deg, #0a0a1a 0%, #0d0d24 100%);
  padding: 0 8px 8px 8px;
  padding-bottom: 80px;
}
/* Main content area */
.m-main {
  padding: 12px 0;
}

.m-section {
  margin-bottom: 20px;
}

.m-section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.m-section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 700;
  color: #fff;
  margin: 0;
}

.m-section-link {
  font-size: 12px;
  color: #38efeb;
  cursor: pointer;
}

/* Stats scroll */
.m-stats-scroll {
  overflow-x: auto;
  margin: 0 -16px;
  padding: 0 16px 8px;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
}

.m-stats-scroll::-webkit-scrollbar {
  display: none;
}

.m-stats-container {
  display: flex;
  gap: 10px;
}

.m-stat-card-pro {
  min-width: 140px;
  padding: 14px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 14px;
  flex-shrink: 0;
}

.m-stat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.m-stat-label {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.6);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.m-stat-change {
  font-size: 10px;
  font-weight: 600;
}

.m-stat-change.positive { color: #22c55e; }
.m-stat-change.negative { color: #ef4444; }
.m-stat-change.neutral { color: #eab308; }

.m-stat-value-large {
  font-size: 20px;
  font-weight: 700;
  color: #fff;
  margin-bottom: 8px;
}

.m-stat-sparkline {
  height: 30px;
}

.m-stat-sparkline svg {
  width: 100%;
  height: 100%;
}

/* Sentiment bar */
.m-sentiment-bar {
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
}

.m-sentiment-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.5s ease;
}

.m-sentiment-fill.positive { background: linear-gradient(90deg, #22c55e, #84cc16); }
.m-sentiment-fill.negative { background: linear-gradient(90deg, #ef4444, #f97316); }
.m-sentiment-fill.neutral { background: linear-gradient(90deg, #eab308, #f97316); }

/* Gauge */
.m-gauge-wrapper {
  margin: 8px 0;
}

.m-gauge-svg {
  width: 100%;
  height: 40px;
}

.m-gauge-value {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: -8px;
}

.m-gauge-number {
  font-size: 18px;
  font-weight: 700;
}

.m-gauge-number.greed { color: #22c55e; }
.m-gauge-number.neutral { color: #eab308; }
.m-gauge-number.fear { color: #ef4444; }

.m-gauge-label {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.5);
}

/* Divergence badge */
.m-divergence-badge {
  display: inline-block;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  margin-bottom: 8px;
}

.badge-accumulation {
  background: rgba(34, 197, 94, 0.2);
  color: #22c55e;
  border: 1px solid rgba(34, 197, 94, 0.4);
}

.badge-trap {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.4);
}

.badge-confirmation {
  background: rgba(56, 189, 248, 0.2);
  color: #38bdf8;
  border: 1px solid rgba(56, 189, 248, 0.4);
}

.badge-neutral {
  background: rgba(139, 143, 163, 0.2);
  color: #8b8fa3;
  border: 1px solid rgba(139, 143, 163, 0.4);
}

.m-divergence-desc {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
}

/* Coin selector */
.coin-selector {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 8px;
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
  background: rgba(168, 85, 247, 0.15);
  border-color: rgba(168, 85, 247, 0.5);
  color: #a855f7;
}

.coin-img {
  width: 20px;
  height: 20px;
  border-radius: 50%;
}

/* Loading */
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
  border: 3px solid rgba(168, 85, 247, 0.2);
  border-top-color: #a855f7;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Radar container */
.radar-chart-container {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 16px;
  padding: 16px;
}

/* Whale profiles grid */
.whale-profiles-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.whale-profile-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 12px;
  border-left: 3px solid;
}

.profile-value_hunter { border-left-color: #22c55e; }
.profile-accumulator { border-left-color: #38bdf8; }
.profile-distributor { border-left-color: #f97316; }
.profile-panic_seller { border-left-color: #ef4444; }
.profile-mixed { border-left-color: #8b5cf6; }
.profile-unknown { border-left-color: #6b7280; }

.profile-icon {
  font-size: 20px;
}

.profile-info {
  flex: 1;
}

.profile-name {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: #fff;
}

.profile-count {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.5);
}

.profile-trend {
  font-size: 14px;
  font-weight: 700;
}

.profile-trend.bullish { color: #22c55e; }
.profile-trend.bearish { color: #ef4444; }
.profile-trend.neutral { color: #8b8fa3; }

/* AI Box */
.m-ai-box {
  background: linear-gradient(135deg, rgba(168, 85, 247, 0.1), rgba(56, 239, 235, 0.05));
  border: 1px solid rgba(168, 85, 247, 0.2);
  border-radius: 14px;
  padding: 16px;
}

.m-ai-box-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 11px;
  font-weight: 700;
  color: #a855f7;
  margin-bottom: 10px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.m-ai-box-text {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.85);
  line-height: 1.5;
  margin: 0;
}

.m-ai-action-hint {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.hint-label {
  font-size: 12px;
  color: #38efeb;
  font-weight: 600;
}

.hint-text {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
  margin-left: 6px;
}

/* Golden Shadow Banner */
.golden-shadow-banner {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px;
  background: linear-gradient(135deg, rgba(255, 215, 0, 0.15), rgba(255, 165, 0, 0.08));
  border-radius: 14px;
  border: 1px solid rgba(255, 215, 0, 0.35);
  animation: pulse-gold 2s infinite;
}

.golden-icon {
  font-size: 28px;
}

.golden-content strong {
  display: block;
  font-size: 14px;
  color: #ffd700;
  margin-bottom: 2px;
}

.golden-content span {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
}

@keyframes pulse-gold {
  0%, 100% { box-shadow: 0 0 0 0 rgba(255, 215, 0, 0.4); }
  50% { box-shadow: 0 0 20px 5px rgba(255, 215, 0, 0.15); }
}

/* Signal list */
.m-list {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 14px;
  overflow: hidden;
}

.m-list--dark {
  background: rgba(0, 0, 0, 0.2);
}

.m-list-item--signal {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  border-left: 3px solid transparent;
}

.m-list-item--signal:last-child {
  border-bottom: none;
}

.signal-shadow_accumulation { border-left-color: #22c55e; }
.signal-bull_trap { border-left-color: #ef4444; }
.signal-confirmation { border-left-color: #38bdf8; }
.signal-neutral { border-left-color: #8b8fa3; }

.signal-icon {
  font-size: 18px;
}

.signal-content {
  flex: 1;
}

.signal-label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: #fff;
}

.signal-meta {
  display: flex;
  gap: 8px;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
}

.signal-coin {
  color: #a855f7;
  font-weight: 500;
}

.signal-score {
  font-size: 13px;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 8px;
}

.score-high {
  background: rgba(34, 197, 94, 0.15);
  color: #22c55e;
}

.score-mid {
  background: rgba(234, 179, 8, 0.15);
  color: #eab308;
}

.score-low {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
}

/* Empty state */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 20px;
  color: rgba(255, 255, 255, 0.4);
}

.empty-icon {
  width: 40px;
  height: 40px;
  margin-bottom: 12px;
  opacity: 0.3;
}

/* Explainer grid */
.explainer-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.explainer-card {
  padding: 14px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  text-align: center;
}

.explainer-icon {
  font-size: 26px;
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
  color: rgba(255, 255, 255, 0.5);
  line-height: 1.4;
}

/* Exchange Flow Section */
.m-flow-cards {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.m-flow-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 14px;
}

.m-flow-inflow {
  border-left: 3px solid #ef4444;
}

.m-flow-outflow {
  border-left: 3px solid #22c55e;
}

.m-flow-icon {
  font-size: 20px;
}

.m-flow-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.m-flow-label {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.6);
  text-transform: uppercase;
}

.m-flow-value {
  font-size: 16px;
  font-weight: 700;
}

.m-flow-value.danger { color: #ef4444; }
.m-flow-value.success { color: #22c55e; }

/* Whale Transactions List */
.m-whale-tx-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.m-whale-tx-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
}

.m-whale-tx-item.tx-sell {
  border-left: 3px solid #ef4444;
}

.m-whale-tx-item.tx-buy {
  border-left: 3px solid #22c55e;
}

.m-tx-icon {
  font-size: 16px;
}

.m-tx-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
  overflow: hidden;
}

.m-tx-coin {
  font-size: 13px;
  font-weight: 600;
  color: #fff;
}

.m-tx-addresses {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.5);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.m-tx-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
}

.m-tx-value {
  font-size: 13px;
  font-weight: 600;
  color: #fff;
}

.m-tx-time {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.4);
}

/* Bottom navigation */
.m-bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: space-around;
  background: rgba(10, 10, 26, 0.95);
  backdrop-filter: blur(12px);
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  padding: 10px 0;
  z-index: 100;
}

.m-nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  color: rgba(255, 255, 255, 0.5);
  text-decoration: none;
  transition: color 0.2s;
}

.m-nav-item.active {
  color: #a855f7;
}

.m-nav-icon {
  width: 22px;
  height: 22px;
}

.m-nav-label {
  font-size: 10px;
  font-weight: 500;
}

.m-bottom-spacer {
  height: 20px;
}
</style>
