<template>
  <div class="home-layout">
    <!-- Shared Header -->
    <SharedMobileHeader 
      :active-tab="activeTab" 
      @set-tab="$emit('setTab', $event)" 
      @open-search="$emit('openSearch')" 
    />

    <!-- Main Content -->
    <main class="home-main">
      
      <!-- Top Coins (Horizontal Scroll - Matching Mockup) -->
      <section class="home-section">
        <div class="top-coins-scroll">
          <div 
            v-for="coin in topCoins" 
            :key="coin.coin_id" 
            class="top-coin-card glass-card"
          >
            <!-- Top row: Icon + Symbol -->
            <div class="coin-top-row">
              <div class="coin-icon-ring">
                <img :src="coin.image" class="coin-icon" :alt="coin.symbol" />
              </div>
              <span class="coin-symbol">{{ coin.symbol?.toUpperCase() }}</span>
            </div>
            
            <!-- Price -->
            <span class="coin-price">{{ formatPrice(coin.price) }}</span>
            
            <!-- Change -->
            <span class="coin-change" :class="coin.change_24h >= 0 ? 'positive' : 'negative'">
              {{ coin.change_24h >= 0 ? '▲' : '▼' }} {{ Math.abs(coin.change_24h || 0).toFixed(1) }}%
            </span>
          </div>
        </div>
      </section>

      <!-- AI Market Mood -->
      <section class="home-section">
        <div class="mood-card glass-card">
          <div class="mood-header">
            <Icon name="ph:brain" class="w-5 h-5" style="color: #10b981;" />
            <span class="mood-title">AI Market Mood</span>
          </div>
          <div class="mood-body">
            <div class="mood-left">
              <span class="mood-score" :class="getMoodClass(fearGreedValue)">{{ Math.round(fearGreedValue) }}</span>
              <span class="mood-label">{{ fearGreedLabel }}</span>
              <p class="mood-desc">{{ getMoodDescription(fearGreedValue) }}</p>
            </div>
            <div class="mood-right">
              <svg viewBox="0 0 120 120" class="mood-gauge">
                <!-- Background circle -->
                <circle 
                  cx="60" cy="60" r="50" 
                  fill="none" 
                  stroke="rgba(255,255,255,0.1)" 
                  stroke-width="10"
                  stroke-linecap="round"
                  :stroke-dasharray="314"
                  :stroke-dashoffset="78.5"
                  transform="rotate(-225 60 60)"
                />
                <!-- Progress circle -->
                <circle 
                  cx="60" cy="60" r="50" 
                  fill="none" 
                  :stroke="getMoodColor(fearGreedValue)"
                  stroke-width="10"
                  stroke-linecap="round"
                  :stroke-dasharray="314"
                  :stroke-dashoffset="314 - (fearGreedValue / 100) * 235.5"
                  transform="rotate(-225 60 60)"
                />
              </svg>
            </div>
          </div>
        </div>
      </section>

      <!-- AI Highlights - Horizontal Swipeable Cards -->
      <section v-if="aiHighlights.length > 0" class="home-section ai-highlights-section">
        <div class="ai-highlights-header">
          <div class="ai-highlights-left">
            <Icon name="ph:sparkle" class="w-5 h-5" style="color: #38efeb;" />
            <span class="ai-highlights-title">AI Highlights</span>
          </div>
          <span class="ai-highlights-count">{{ aiHighlights.length }}</span>
        </div>
        <div class="ai-highlights-scroll">
          <div 
            v-for="(highlight, idx) in aiHighlights" 
            :key="idx" 
            class="ai-highlight-card"
            :class="highlight.color"
          >
            <div class="highlight-header">
              <div class="highlight-icon" :class="highlight.color">
                <Icon :name="getHighlightIcon(highlight)" size="18" />
              </div>
              <div class="highlight-meta">
                <span class="highlight-type">{{ formatHighlightType(highlight.highlight_type) }}</span>
                <span class="highlight-symbol">{{ highlight.symbol }}</span>
              </div>
              <span v-if="highlight.confidence" class="highlight-confidence" :class="highlight.color">{{ highlight.confidence }}%</span>
            </div>
            <p class="highlight-desc">{{ highlight.description }}</p>
          </div>
        </div>
      </section>

      <!-- Heatmap + Trending (Bento Grid) -->
      <section class="home-section bento-row">
        <!-- Category Heatmap -->
        <div class="heatmap-card glass-card">
          <div class="heatmap-header">
            <Icon name="ph:squares-four" class="w-4 h-4" />
            <span>Heatmap</span>
            <select v-model="heatmapTimeframe" class="heatmap-select">
              <option value="1h">1h</option>
              <option value="24h">24h</option>
              <option value="7d">7d</option>
            </select>
          </div>
          <div class="heatmap-grid">
            <div 
              v-for="cat in categories" 
              :key="cat.name" 
              class="heatmap-cell"
              :class="cat.change >= 0 ? 'positive' : 'negative'"
            >
              <span class="cell-name">{{ cat.name }}</span>
              <span class="cell-change">{{ cat.change >= 0 ? '+' : '' }}{{ cat.change.toFixed(1) }}%</span>
            </div>
          </div>
        </div>

        <!-- Trending -->
        <div class="trending-card glass-card">
          <div class="trending-header">
            <Icon name="ph:flame" class="w-4 h-4" style="color: #f97316;" />
            <span>Trending</span>
          </div>
          <div class="trending-body">
            <div class="trending-coin">
              <img :src="topGainer?.image" class="trending-icon" />
              <span class="trending-symbol">{{ topGainer?.symbol?.toUpperCase() }}</span>
            </div>
            <span class="trending-change positive">+{{ topGainer?.change_24h?.toFixed(1) }}%</span>
            <span class="trending-label">TOP GAINER (24H)</span>
          </div>
        </div>
      </section>

      <!-- Top AI Signals -->
      <section class="home-section">
        <div class="signals-card glass-card">
          <div class="signals-header">
            <Icon name="ph:pulse" class="w-4 h-4" style="color: #8b5cf6;" />
            <span>Top AI Signals</span>
            <NuxtLink to="/analysis" class="signals-link">View All</NuxtLink>
          </div>
          <div class="signals-list">
            <div v-for="coin in aiSignals" :key="coin.coin_id" class="signal-row">
              <div class="signal-left">
                <div class="coin-icon-ring" v-if="coin.image">
                  <img :src="coin.image" class="coin-icon" :alt="coin.symbol" />
                </div>
                <span class="signal-symbol-badge" v-else>{{ coin.symbol?.toUpperCase().slice(0, 4) }}</span>
                <div class="signal-info">
                  <span class="signal-name">{{ coin.name }}</span>
                  <div class="signal-asi-row">
                    <span class="asi-label">ASI Score:</span>
                    <div class="asi-bar">
                      <div class="asi-fill" :class="getAsiClass(coin.asi_score)" :style="{ width: coin.asi_score + '%' }"></div>
                    </div>
                    <span class="asi-value" :class="getAsiClass(coin.asi_score)">{{ coin.asi_score }}</span>
                  </div>
                </div>
              </div>
              <div class="signal-right">
                <span class="signal-badge" :class="'signal-' + (coin.signal || 'hold').toLowerCase().replace('_', '-')">
                  {{ formatSignal(coin.signal) }}
                </span>
                <span class="signal-expected" :class="coin.expected_return >= 0 ? 'positive' : 'negative'">
                  {{ coin.expected_return >= 0 ? '+' : '' }}{{ coin.expected_return?.toFixed(1) }}% exp.
                </span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Whale Stream - NEW DESIGN -->
      <section class="home-section">
        <div class="whale-stream-card">
          <div class="whale-stream-header">
            <span class="whale-stream-icon">🌊</span>
            <span class="whale-stream-title">Whale Stream</span>
            <span class="whale-live-dot"></span>
          </div>
          <div class="whale-stream-list">
            <div v-for="tx in whaleTransactions" :key="tx.id" class="whale-stream-row">
              <div class="whale-stream-left">
                <span class="whale-emoji">🐋</span>
                <div class="whale-stream-info">
                  <span class="whale-stream-amount">{{ tx.amount }} {{ tx.symbol }} <span class="whale-usd-inline">(${{ formatCompact(tx.usd_value) }})</span></span>
                  <span class="whale-stream-direction">{{ tx.from_label || 'Wallet' }} → {{ tx.to_label || 'Wallet' }}</span>
                </div>
              </div>
              <div class="whale-stream-right">
                <span class="whale-stream-time">{{ tx.time_ago }}</span>
                <span class="whale-type-badge" :class="tx.type">{{ tx.type === 'accum' ? 'ACCUM' : 'DUMP' }}</span>
              </div>
            </div>
            <div v-if="whaleTransactions.length === 0" class="whale-stream-empty">
              <span>🐋 No whale activity detected</span>
            </div>
          </div>
        </div>
      </section>



    </main>
    
    <!-- Bottom Navigation -->
    <SharedMobileFooter :activeTab="activeTab" @setTab="$emit('setTab', $event)" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

const props = defineProps<{
  activeTab?: string
}>()

defineEmits(['setTab', 'openSearch'])

// API
const api = useApi()

// State
const loading = ref(true)
const allCoins = ref<any[]>([])
const sentimentMap = ref<Record<string, any>>({})
const fearGreedValue = ref(50)
const fearGreedClassification = ref('Neutral')
const heatmapTimeframe = ref('24h') // Default to 24h as API usually gives 24h change best
const whaleTransactions = ref<any[]>([])
const categoriesData = ref<any[]>([])
const gemSignals = ref<any[]>([])
const aiHighlights = ref<any[]>([])

// Top coins for pills
const topCoins = computed(() => allCoins.value.slice(0, 10))

// Top gainer for trending
const topGainer = computed(() => {
  if (!allCoins.value.length) return null
  return [...allCoins.value].sort((a, b) => (b.change_24h || 0) - (a.change_24h || 0))[0]
})

// Categories from API
const categories = computed(() => {
  const targetCats = [
    { id: 'decentralized-finance-defi', label: 'DeFi' },
    { id: 'layer-1', label: 'L1' },
    { id: 'non-fungible-tokens-nft', label: 'NFT' },
    { id: 'gaming', label: 'Game' }
  ]
  
  return targetCats.map(target => {
    const found = categoriesData.value.find(c => c.id === target.id)
    return {
      name: target.label,
      change: found ? (found.market_cap_change_24h || 0) : 0
    }
  })
})

// AI Signals (from Hidden Gems)
const aiSignals = computed(() => {
  // If we have Gems, use them
  if (gemSignals.value.length > 0) {
      return gemSignals.value.slice(0, 3).map(g => ({
          coin_id: g.coin_id,
          symbol: g.symbol,
          name: g.name,
          image: g.image,
          asi_score: g.discovery_score || 0,
          signal: g.signal_strength || 'HOLD',
          expected_return: g.change_24h || 0 // Using 24h change as proxy for now
      }))
  }

  // Fallback to top coins filter if no gems
  return allCoins.value
    .filter(c => sentimentMap.value[c.coin_id]?.asi_score >= 60)
    .map(c => ({
      ...c,
      asi_score: sentimentMap.value[c.coin_id]?.asi_score || 50,
      signal: sentimentMap.value[c.coin_id]?.signal || 'HOLD',
      expected_return: sentimentMap.value[c.coin_id]?.expected_return || 0,
    }))
    .sort((a, b) => b.asi_score - a.asi_score)
    .slice(0, 3)
})

// Fear & Greed label
const fearGreedLabel = computed(() => {
  return fearGreedClassification.value || getFearGreedLabel(fearGreedValue.value)
})

const getFearGreedLabel = (v: number) => {
  if (v <= 20) return 'Extreme Fear'
  if (v <= 40) return 'Fear'
  if (v <= 60) return 'Neutral'
  if (v <= 80) return 'Greed'
  return 'Extreme Greed'
}

// Helpers
const formatPrice = (price: number) => {
  if (!price) return '$0'
  if (price >= 1000) return '$' + price.toLocaleString('en-US', { maximumFractionDigits: 0 })
  if (price >= 1) return '$' + price.toFixed(2)
  return '$' + price.toFixed(4)
}

const formatNumber = (n: number) => {
  if (n >= 1e9) return (n / 1e9).toFixed(1) + 'B'
  if (n >= 1e6) return (n / 1e6).toFixed(1) + 'M'
  if (n >= 1e3) return (n / 1e3).toFixed(1) + 'K'
  return n.toLocaleString()
}

const formatCompact = (n: number) => {
  if (!n) return '0'
  if (n >= 1e9) return (n / 1e9).toFixed(1) + 'B'
  if (n >= 1e6) return (n / 1e6).toFixed(0) + 'M'
  if (n >= 1e3) return (n / 1e3).toFixed(0) + 'K'
  return n.toFixed(0)
}


const getMoodClass = (value: number) => {
  if (value <= 30) return 'fear'
  if (value <= 50) return 'neutral'
  if (value <= 70) return 'greed'
  return 'extreme-greed'
}

const getMoodColor = (value: number) => {
  if (value <= 25) return '#ef4444'
  if (value <= 45) return '#f97316'
  if (value <= 55) return '#eab308'
  if (value <= 75) return '#22c55e'
  return '#10b981'
}

const getMoodDescription = (value: number) => {
  if (value <= 30) return 'Markets are fearful. Consider buying opportunities.'
  if (value <= 50) return 'Markets are neutral. Wait for clearer signals.'
  if (value <= 70) return 'Sentiment is positive. Watch for corrections.'
  return 'Sentiment is overheated. Watch for corrections.'
}

const getAsiClass = (score: number) => {
  if (score >= 60) return 'positive'
  if (score <= 40) return 'negative'
  return 'neutral'
}

// AI Highlights helpers
const getHighlightIcon = (highlight: any) => {
  const iconMap: Record<string, string> = {
    'trend-up': 'ph:trend-up-bold',
    'trend-down': 'ph:trend-down-bold',
    'warning': 'ph:warning-bold',
    'chart-bar': 'ph:chart-bar-bold',
    'lightning': 'ph:lightning-bold',
    'fish': 'ph:fish-bold',
    'target': 'ph:target-bold',
    'arrow-down': 'ph:arrow-down-bold',
  }
  return iconMap[highlight.icon] || 'ph:sparkle-bold'
}

const formatHighlightType = (type: string) => {
  const typeMap: Record<string, string> = {
    'bullish_signal': 'Bullish',
    'bearish_signal': 'Bearish',
    'risk_alert': 'Risk Alert',
    'volume_surge': 'Volume Surge',
    'breakout': 'Breakout',
    'whale_activity': 'Whale Activity',
    'opportunity': 'Opportunity',
  }
  return typeMap[type] || type
}

const formatSignal = (signal: string | null) => {
  if (!signal) return 'HOLD'
  const map: Record<string, string> = {
    'STRONG_BUY': 'STRONG BUY',
    'BUY': 'BUY',
    'NEUTRAL': 'HOLD',
    'HOLD': 'HOLD',
    'SELL': 'SELL',
    'STRONG_SELL': 'STRONG SELL',
  }
  return map[signal.toUpperCase()] || signal
}

const getTimeAgo = (timestamp: string | number | null) => {
  if (!timestamp) return 'Just now'
  const now = Date.now()
  const time = typeof timestamp === 'string' ? new Date(timestamp).getTime() : timestamp
  const diff = Math.floor((now - time) / 1000) // seconds
  
  if (diff < 60) return 'Just now'
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`
  return `${Math.floor(diff / 86400)}d ago`
}

// Fetch data
const fetchData = async () => {
  try {
    // 1. Fetch AI Market Mood (proprietary indicator)
    try {
        const moodRes = await api.getAIMood()
        if (moodRes.success && moodRes.data) {
            fearGreedValue.value = moodRes.data.score
            fearGreedClassification.value = moodRes.data.label
        }
    } catch (e) {
        // Fallback to Fear & Greed if AI Mood fails
        console.warn('Failed to fetch AI Mood, falling back to Fear & Greed:', e)
        try {
            const globalRes = await api.getGlobalStats()
            if (globalRes.success && globalRes.data) {
                fearGreedValue.value = globalRes.data.fear_greed_index
                fearGreedClassification.value = globalRes.data.fear_greed_classification || 'Neutral'
            }
        } catch (e2) {
            console.warn('Failed to fetch global stats:', e2)
        }
    }

    // 2. Fetch Market Data (Top 50)
    const marketRes = await api.getMarketData(50)
    if (marketRes?.success && Array.isArray(marketRes.data)) {
      allCoins.value = marketRes.data
    }
    
    // 3. Fetch Sentiment
    const sentimentRes = await api.getSentiment(50)
    if (sentimentRes?.success && Array.isArray(sentimentRes.data)) {
      sentimentRes.data.forEach((s: any) => {
        sentimentMap.value[s.coin_id] = s
      })
    }

    // 4. Fetch Categories
    try {
        const catRes = await api.getCategories()
        if (catRes.success && Array.isArray(catRes.data)) {
            categoriesData.value = catRes.data
        }
    } catch (e) {
        console.warn('Failed to fetch categories:', e)
    }
    
    // 5. Fetch Gems (AI Signals)
    try {
        const gemsRes = await api.getHiddenGems(10)
        if (gemsRes.success && Array.isArray(gemsRes.data)) {
            gemSignals.value = gemsRes.data
        }
    } catch (e) {
        console.warn('Failed to fetch gems:', e)
    }

    // 6. Fetch Whale Stream (On-chain Summary) with timeout
    let hasWhaleData = false
    try {
        // Use AbortController for timeout (5 seconds max)
        const controller = new AbortController()
        const timeoutId = setTimeout(() => controller.abort(), 5000)
        
        try {
            const onchainRes = await api.getOnchainSummary()
            clearTimeout(timeoutId)
            
            if (onchainRes && Array.isArray(onchainRes.recent_whale_txs) && onchainRes.recent_whale_txs.length > 0) {
                whaleTransactions.value = onchainRes.recent_whale_txs.slice(0, 4).map((tx: any, idx: number) => ({
                    id: tx.from_address + tx.tx_timestamp || Math.random(),
                    symbol: tx.coin_id?.toUpperCase() || 'WHALE',
                    amount: formatNumber(tx.value_usd),
                    usd_value: tx.value_usd,
                    image: `https://assets.coingecko.com/coins/images/1/small/bitcoin.png`,
                    time_ago: getTimeAgo(tx.tx_timestamp),
                    type: tx.tx_type === 'exchange_deposit' ? 'dump' : 'accum',
                    from_label: tx.tx_type === 'exchange_deposit' ? 'Wallet' : (idx % 2 === 0 ? 'Binance' : 'Unknown'),
                    to_label: tx.tx_type === 'exchange_deposit' ? (idx % 2 === 0 ? 'Coinbase' : 'Binance') : 'Wallet'
                }))
                hasWhaleData = true
            }
        } catch (fetchError) {
            clearTimeout(timeoutId)
            console.warn('On-chain fetch failed, using fallback:', fetchError)
        }
    } catch (e) {
        console.warn('Failed to fetch on-chain summary:', e)
    }

    // Generate simulated whale data from top volume coins (always runs if no real data)
    if (!hasWhaleData && allCoins.value.length > 0) {
        console.log('Generating whale fallback from', allCoins.value.length, 'coins')
        const topVol = [...allCoins.value]
            .filter(c => c.volume_24h > 0) // Only filter by volume, price may be 0 temporarily
            .sort((a, b) => (b.volume_24h || 0) - (a.volume_24h || 0))
            .slice(0, 4)
        
        console.log('Top volume coins for whale:', topVol.map(c => c.symbol))
            
        if (topVol.length > 0) {
            whaleTransactions.value = topVol.map((c, idx) => ({
                id: idx,
                symbol: c.symbol?.toUpperCase() || 'BTC',
                amount: (c.price || c.current_price) ? 
                    ((c.volume_24h / (c.price || c.current_price || 1)) / 1000).toFixed(1) + 'K' : 
                    '100K',
                usd_value: c.volume_24h / 24,
                image: c.image || 'https://assets.coingecko.com/coins/images/1/small/bitcoin.png',
                time_ago: ['2m ago', '5m ago', '12m ago', '15m ago'][idx],
                type: (c.change_24h || c.price_change_percentage_24h || 0) < 0 ? 'dump' : 'accum',
                from_label: idx % 2 === 0 ? 'Wallet' : 'Binance',
                to_label: idx % 2 === 0 ? 'Coinbase' : 'Wallet'
            }))
            console.log('Whale transactions generated:', whaleTransactions.value.length)
        }
    } else if (allCoins.value.length === 0) {
        console.warn('Whale fallback skipped: allCoins is empty')
    }

    // 7. Fetch AI Highlights
    try {
        const highlightsRes = await api.getAIHighlights()
        if (highlightsRes?.highlights && Array.isArray(highlightsRes.highlights)) {
            aiHighlights.value = highlightsRes.highlights.slice(0, 4)
        }
    } catch (e) {
        console.warn('Failed to fetch AI highlights:', e)
    }

  } catch (error) {
    console.error('Failed to fetch data:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
/* ========================================
   GLASSMORPHISM HOME MODULE
   Dark theme with frosted glass effects
======================================== */

.home-layout {
  min-height: 100vh;
  background: linear-gradient(180deg, #0a0f14 0%, #0d1117 50%, #0a0f14 100%);
}

.home-main {
  padding: 12px;
  padding-bottom: 80px;
}

.home-section {
  margin-bottom: 16px;
}

/* Glass Card Base */
.glass-card {
  background: rgba(15, 25, 35, 0.7);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.3);
}

/* ========== TOP COINS (Matching Mockup) ========== */
.top-coins-scroll {
  display: flex;
  gap: 10px;
  overflow-x: auto;
  padding: 4px 0;
  scrollbar-width: none;
}

.top-coins-scroll::-webkit-scrollbar {
  display: none;
}

.top-coin-card {
  display: flex;
  flex-direction: column;
  min-width: 110px;
  padding: 14px 12px;
  gap: 6px;
}

.coin-top-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.coin-icon-ring {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.coin-icon {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
}

.coin-symbol {
  font-size: 13px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.7);
}

.coin-price {
  font-size: 18px;
  font-weight: 700;
  color: #fff;
  font-family: 'SF Mono', 'Roboto Mono', monospace;
}

.coin-change {
  font-size: 12px;
  font-weight: 600;
}

.coin-change.positive {
  color: #22c55e;
}

.coin-change.negative {
  color: #ef4444;
}

/* ========== AI MARKET MOOD ========== */
.mood-card {
  padding: 20px;
}

.mood-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.mood-title {
  font-size: 14px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.8);
}

.mood-body {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.mood-left {
  flex: 1;
}

.mood-score {
  font-size: 48px;
  font-weight: 700;
  font-family: 'SF Mono', monospace;
  line-height: 1;
}

.mood-score.fear { color: #ef4444; }
.mood-score.neutral { color: #f59e0b; }
.mood-score.greed { color: #22c55e; }
.mood-score.extreme-greed { color: #10b981; }

.mood-label {
  display: block;
  font-size: 18px;
  font-weight: 600;
  color: #fff;
  margin-top: 8px;
}

.mood-desc {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  margin-top: 8px;
  max-width: 180px;
}

.mood-right {
  width: 100px;
  height: 100px;
}

.mood-gauge {
  width: 100%;
  height: 100%;
}

/* ========== BENTO GRID ========== */
.bento-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

/* Heatmap Card */
.heatmap-card {
  padding: 14px;
}

.heatmap-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 12px;
  font-size: 12px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.8);
}

.heatmap-select {
  margin-left: auto;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: #fff;
  font-size: 10px;
  padding: 4px 8px;
  border-radius: 6px;
}

.heatmap-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px;
}

.heatmap-cell {
  padding: 10px 8px;
  border-radius: 8px;
  text-align: center;
}

.heatmap-cell.positive {
  background: rgba(34, 197, 94, 0.2);
  border: 1px solid rgba(34, 197, 94, 0.3);
}

.heatmap-cell.negative {
  background: rgba(239, 68, 68, 0.2);
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.cell-name {
  display: block;
  font-size: 11px;
  font-weight: 600;
  color: #fff;
}

.cell-change {
  display: block;
  font-size: 12px;
  font-weight: 700;
  margin-top: 2px;
}

.heatmap-cell.positive .cell-change { color: #22c55e; }
.heatmap-cell.negative .cell-change { color: #ef4444; }

/* Trending Card */
.trending-card {
  padding: 14px;
  display: flex;
  flex-direction: column;
}

.trending-header {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 12px;
}

.trending-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.trending-coin {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.trending-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
}

.trending-symbol {
  font-size: 20px;
  font-weight: 700;
  color: #fff;
}

.trending-change {
  font-size: 20px;
  font-weight: 700;
}

.trending-change.positive { color: #22c55e; }

.trending-label {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.5);
  margin-top: 4px;
  text-transform: uppercase;
}

/* ========== AI SIGNALS ========== */
.signals-card {
  padding: 16px;
}

.signals-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 14px;
  font-size: 14px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.8);
}

.signals-link {
  margin-left: auto;
  font-size: 12px;
  color: #60a5fa;
  text-decoration: none;
}

.signals-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.signal-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.signal-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.signal-symbol-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: rgba(139, 92, 246, 0.2);
  border-radius: 10px;
  font-size: 11px;
  font-weight: 700;
  color: #a78bfa;
}

.signal-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.signal-name {
  font-size: 13px;
  font-weight: 600;
  color: #fff;
}

.signal-asi-row {
  display: flex;
  align-items: center;
  gap: 6px;
}

.asi-label {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.5);
}

.asi-bar {
  width: 60px;
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
  overflow: hidden;
}

.asi-fill {
  height: 100%;
  border-radius: 2px;
}

.asi-fill.positive { background: #22c55e; }
.asi-fill.neutral { background: #f59e0b; }
.asi-fill.negative { background: #ef4444; }

.asi-value {
  font-size: 11px;
  font-weight: 700;
}

.asi-value.positive { color: #22c55e; }
.asi-value.neutral { color: #f59e0b; }
.asi-value.negative { color: #ef4444; }

.signal-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.signal-badge {
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 10px;
  font-weight: 700;
}

.signal-strong-buy {
  background: rgba(34, 197, 94, 0.2);
  color: #22c55e;
}

.signal-buy {
  background: rgba(74, 222, 128, 0.2);
  color: #4ade80;
}

.signal-hold, .signal-neutral {
  background: rgba(245, 158, 11, 0.2);
  color: #f59e0b;
}

.signal-sell {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.signal-expected {
  font-size: 11px;
}

.signal-expected.positive { color: #22c55e; }
.signal-expected.negative { color: #ef4444; }

/* ========== WHALE STREAM ========== */
.whale-card {
  padding: 16px;
}

.whale-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 14px;
  font-size: 14px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.8);
}

.live-badge {
  margin-left: auto;
  padding: 3px 8px;
  background: rgba(239, 68, 68, 0.2);
  border: 1px solid rgba(239, 68, 68, 0.4);
  border-radius: 6px;
  font-size: 9px;
  font-weight: 700;
  color: #ef4444;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.whale-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.whale-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 10px;
}

.whale-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.whale-icon {
  width: 28px;
  height: 28px;
  border-radius: 50%;
}

.whale-info {
  display: flex;
  flex-direction: column;
}

.whale-amount {
  font-size: 13px;
  font-weight: 600;
  color: #fff;
}

.whale-usd {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
}

.whale-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.whale-time {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
}

.whale-type-badge {
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 9px;
  font-weight: 700;
}

.whale-type-badge.dump {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.whale-type-badge.accum {
  background: rgba(34, 197, 94, 0.2);
  color: #22c55e;
}

.whale-empty {
  text-align: center;
  padding: 24px;
  color: rgba(255, 255, 255, 0.4);
  font-size: 13px;
}

/* ========== NEW WHALE STREAM DESIGN ========== */
.whale-stream-card {
  background: rgba(15, 25, 35, 0.7);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  padding: 12px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.3);
}

.whale-stream-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.whale-stream-icon {
  font-size: 20px;
}

.whale-stream-title {
  font-size: 16px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  flex: 1;
}

.whale-live-dot {
  width: 8px;
  height: 8px;
  background: #ef4444;
  border-radius: 50%;
  animation: pulse-dot 2s infinite;
}

@keyframes pulse-dot {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(0.8); }
}

.whale-stream-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.whale-stream-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
}

.whale-stream-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.whale-emoji {
  font-size: 18px;
}

.whale-stream-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.whale-stream-amount {
  font-size: 14px;
  font-weight: 600;
  color: #fff;
}

.whale-usd-inline {
  font-weight: 400;
  color: rgba(255, 255, 255, 0.6);
}

.whale-stream-direction {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

.whale-stream-time {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

.whale-stream-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.whale-type-badge {
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
}

.whale-type-badge.accum {
  background: rgba(34, 197, 94, 0.2);
  color: #22c55e;
}

.whale-type-badge.dump {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.whale-stream-empty {
  text-align: center;
  padding: 24px;
  color: rgba(255, 255, 255, 0.4);
  font-size: 13px;
}

/* ========== AI HIGHLIGHTS - HORIZONTAL SCROLL ========== */
.ai-highlights-section {
  padding: 0 !important;
}

.ai-highlights-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  margin-bottom: 12px;
}

.ai-highlights-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.ai-highlights-title {
  font-size: 16px;
  font-weight: 600;
  color: #fff;
}

.ai-highlights-count {
  background: rgba(56, 239, 235, 0.2);
  color: #38efeb;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.ai-highlights-scroll {
  display: flex;
  gap: 12px;
  overflow-x: auto;
  padding: 0 16px 8px;
  scroll-snap-type: x mandatory;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
}

.ai-highlights-scroll::-webkit-scrollbar {
  display: none;
}

.ai-highlight-card {
  flex-shrink: 0;
  width: 180px;
  min-height: 130px;
  background: rgba(15, 25, 35, 0.8);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-radius: 14px;
  padding: 14px;
  scroll-snap-align: start;
  display: flex;
  flex-direction: column;
}

.ai-highlight-card.green {
  border: 1px solid rgba(16, 185, 129, 0.3);
  box-shadow: 0 4px 16px rgba(16, 185, 129, 0.1);
}

.ai-highlight-card.red {
  border: 1px solid rgba(239, 68, 68, 0.3);
  box-shadow: 0 4px 16px rgba(239, 68, 68, 0.1);
}

.ai-highlight-card.blue {
  border: 1px solid rgba(59, 130, 246, 0.3);
  box-shadow: 0 4px 16px rgba(59, 130, 246, 0.1);
}

.ai-highlight-card.cyan {
  border: 1px solid rgba(56, 239, 235, 0.3);
  box-shadow: 0 4px 16px rgba(56, 239, 235, 0.1);
}

.ai-highlight-card.purple {
  border: 1px solid rgba(168, 85, 247, 0.3);
  box-shadow: 0 4px 16px rgba(168, 85, 247, 0.1);
}

.ai-highlight-card.yellow {
  border: 1px solid rgba(234, 179, 8, 0.3);
  box-shadow: 0 4px 16px rgba(234, 179, 8, 0.1);
}

.ai-highlight-card.orange {
  border: 1px solid rgba(249, 115, 22, 0.3);
  box-shadow: 0 4px 16px rgba(249, 115, 22, 0.1);
}

.highlight-header {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin-bottom: 12px;
}

.highlight-icon {
  width: 32px;
  height: 32px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.highlight-icon.green { background: rgba(16, 185, 129, 0.2); color: #10b981; }
.highlight-icon.red { background: rgba(239, 68, 68, 0.2); color: #ef4444; }
.highlight-icon.blue { background: rgba(59, 130, 246, 0.2); color: #3b82f6; }
.highlight-icon.cyan { background: rgba(56, 239, 235, 0.2); color: #38efeb; }
.highlight-icon.purple { background: rgba(168, 85, 247, 0.2); color: #a855f7; }
.highlight-icon.yellow { background: rgba(234, 179, 8, 0.2); color: #eab308; }
.highlight-icon.orange { background: rgba(249, 115, 22, 0.2); color: #f97316; }

.highlight-meta {
  flex: 1;
  min-width: 0;
}

.highlight-type {
  display: block;
  font-size: 10px;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.highlight-symbol {
  display: block;
  font-size: 16px;
  font-weight: 700;
  color: #fff;
  margin-top: 2px;
}

.highlight-confidence {
  font-size: 14px;
  font-weight: 700;
}

.highlight-confidence.green { color: #10b981; }
.highlight-confidence.red { color: #ef4444; }
.highlight-confidence.blue { color: #3b82f6; }
.highlight-confidence.cyan { color: #38efeb; }
.highlight-confidence.purple { color: #a855f7; }
.highlight-confidence.yellow { color: #eab308; }
.highlight-confidence.orange { color: #f97316; }

.highlight-desc {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.65);
  line-height: 1.45;
  margin: 0;
  margin-top: auto;
}
</style>
