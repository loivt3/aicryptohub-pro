<template>
  <div class="mobile-layout">
    <!-- Header -->
    <header class="m-header">
      <div class="m-header-content">
        <div class="m-logo">
          <span class="m-logo-icon">🔥</span>
          <span class="m-logo-text">AI Hub</span>
        </div>
        <div class="m-ticker">
          <span class="m-ticker-label">BTC</span>
          <span class="m-ticker-value" :class="{ negative: btcChange < 0 }">
            {{ formatCurrency(btcPrice, 0) }}
          </span>
        </div>
        <div class="m-actions">
          <a href="https://aicryptohub.io" class="m-action-btn" title="Home">
            <Icon name="ph:house" class="m-icon" />
          </a>
          <button class="m-action-btn" @click="$emit('openSearch')" title="Search">
            <Icon name="ph:magnifying-glass" class="m-icon" />
          </button>
          <button class="m-action-btn" :class="{ active: activeTab === 'alerts' }" @click="$emit('setTab', 'alerts')" title="Alerts">
            <Icon name="ph:bell" class="m-icon" />
          </button>
          <button class="m-action-btn" :class="{ active: activeTab === 'portfolio' }" @click="$emit('setTab', 'portfolio')" title="Portfolio">
            <Icon name="ph:briefcase" class="m-icon" />
          </button>
        </div>
      </div>
    </header>

    <main class="m-main">
      <!-- Loading State -->
      <div v-if="loading" class="m-card m-card--dark" style="text-align: center; padding: 60px 16px;">
        <div class="m-spinner"></div>
        <p class="m-text-muted" style="margin-top: 16px;">Loading market data...</p>
      </div>

      <!-- Empty State -->
      <div v-else-if="indices.length === 0" class="m-card m-card--dark" style="text-align: center; padding: 60px 16px;">
        <span style="font-size: 56px; display: block; margin-bottom: 16px;">📊</span>
        <h3 style="margin-bottom: 8px;">No Indices Available</h3>
        <p class="m-text-muted">Please sync indices from settings</p>
      </div>

      <!-- Content -->
      <template v-else>
        <!-- Featured Index Hero Card (from featured-card.php) -->
        <section class="m-section" v-if="featuredIndex">
          <div class="m-card m-featured-card m-card--dark">
            <!-- Top Row: Badge + Nav -->
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
              <span class="m-badge m-badge--accent">
                <span class="m-badge-dot"></span>
                FEATURED
              </span>
              <div style="display: flex; gap: 8px;">
                <button @click="prevFeaturedIndex" class="m-action-btn m-action-btn--dark" aria-label="Previous">
                  <Icon name="ph:caret-left" class="m-icon" />
                </button>
                <button @click="nextFeaturedIndex" class="m-action-btn m-action-btn--dark" aria-label="Next">
                  <Icon name="ph:caret-right" class="m-icon" />
                </button>
              </div>
            </div>
            
            <!-- Category Tag -->
            <span class="m-info-subtitle" style="text-transform: uppercase; letter-spacing: 0.8px;">
              {{ featuredIndex.category_id.replace(/-/g, ' ') }}
            </span>
            
            <!-- Name -->
            <h2 class="m-featured-name">{{ featuredIndex.name }}</h2>
            
            <!-- Price + Change -->
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
              <span class="m-featured-price">{{ formatCurrency(featuredIndex.market_cap, 2) }}</span>
              <span class="m-badge" :class="Number(featuredIndex.market_cap_change_24h) >= 0 ? 'm-badge--success' : 'm-badge--danger'">
                {{ Number(featuredIndex.market_cap_change_24h) >= 0 ? '↑' : '↓' }}
                {{ Math.abs(Number(featuredIndex.market_cap_change_24h) || 0).toFixed(2) }}%
              </span>
            </div>
            
            <!-- Chart -->
            <div class="m-chart-area">
              <svg viewBox="0 0 320 90" preserveAspectRatio="none">
                <defs>
                  <linearGradient id="heroGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" :stop-color="Number(featuredIndex.market_cap_change_24h) >= 0 ? 'rgba(56, 239, 235, 0.3)' : 'rgba(239, 68, 68, 0.3)'" />
                    <stop offset="100%" stop-color="transparent" />
                  </linearGradient>
                </defs>
                <path :d="getChartPath(featuredIndex.category_id, 320, 90, true)" fill="url(#heroGrad)" />
                <path :d="getChartPath(featuredIndex.category_id, 320, 90, false)" 
                      fill="none" 
                      :stroke="Number(featuredIndex.market_cap_change_24h) >= 0 ? '#38efeb' : '#ef4444'" 
                      stroke-width="2.5"
                      stroke-linecap="round"/>
              </svg>
            </div>
            
            <!-- CTA Button -->
            <button class="m-btn m-btn--primary" @click="openIndexDetail(featuredIndex)">
              <span>View Details</span>
              <Icon name="ph:caret-right" class="m-icon" />
            </button>
          </div>
        </section>
        
        <!-- Popular Categories (from scroll-cards.php) -->
        <section class="m-section">
          <h3 class="m-section-title">Popular Categories</h3>
          <div class="m-scroll">
            <template v-for="(index, i) in popularCategories" :key="index.category_id">
              <div class="m-scroll-card" @click="openIndexDetail(index)">
                <div class="m-scroll-card__header">
                  <span class="m-scroll-card__badge">{{ formatCategoryId(index.category_id) }}</span>
                  <span class="m-scroll-card__link">DETAILS ↗</span>
                </div>
                <div class="m-scroll-card__name">{{ index.name }}</div>
                <div class="m-scroll-card__price">{{ formatCurrency(index.market_cap, 1) }}</div>
                <div class="m-scroll-card__change" :class="Number(index.market_cap_change_24h) >= 0 ? 'positive' : 'negative'">
                  {{ Number(index.market_cap_change_24h) >= 0 ? '+' : '' }}{{ (Number(index.market_cap_change_24h) || 0).toFixed(2) }}%
                </div>
                <div class="m-scroll-card__chart">
                  <svg viewBox="0 0 120 40" preserveAspectRatio="none">
                    <defs>
                      <linearGradient :id="'scg-' + i" x1="0%" y1="0%" x2="0%" y2="100%">
                        <stop offset="0%" :stop-color="Number(index.market_cap_change_24h) >= 0 ? 'rgba(56,239,235,0.25)' : 'rgba(239,68,68,0.25)'" />
                        <stop offset="100%" stop-color="transparent" />
                      </linearGradient>
                    </defs>
                    <path d="M0,30 C15,25 30,35 45,20 C60,5 75,15 90,25 C105,35 120,20 120,20 L120,40 L0,40 Z" :fill="'url(#scg-' + i + ')'" />
                    <path d="M0,30 C15,25 30,35 45,20 C60,5 75,15 90,25 C105,35 120,20 120,20" fill="none" :stroke="Number(index.market_cap_change_24h) >= 0 ? '#38efeb' : '#ef4444'" stroke-width="1.5"/>
                  </svg>
                </div>
              </div>
            </template>
          </div>
        </section>
        
        <!-- All Categories List (from indices-table.php) -->
        <section class="m-section">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <h3 class="m-section-title" style="margin: 0;">All Categories</h3>
            <span class="m-badge m-badge--info">{{ validIndices.length }}</span>
          </div>
          
          <div class="m-list m-list--dark">
            <div v-for="(index, idx) in validIndices" :key="index.category_id" class="m-list-item" @click="openIndexDetail(index)" style="cursor: pointer;">
              <span class="m-rank">{{ idx + 1 }}</span>
              <div class="m-info">
                <span class="m-info-title">{{ index.name }}</span>
                <span class="m-info-subtitle m-text-accent">{{ formatCategoryId(index.category_id) }}</span>
              </div>
              <div style="text-align: right; min-width: 80px;">
                <span class="m-info-title">{{ formatCurrency(index.market_cap, 1) }}</span>
                <span class="m-info-subtitle" :class="Number(index.market_cap_change_24h) >= 0 ? 'm-text-success' : 'm-text-danger'">
                  {{ Number(index.market_cap_change_24h) >= 0 ? '+' : '' }}{{ (Number(index.market_cap_change_24h) || 0).toFixed(2) }}%
                </span>
              </div>
              <div style="width: 50px; height: 24px;">
                <svg viewBox="0 0 50 24" preserveAspectRatio="none" style="width: 100%; height: 100%;">
                  <path :d="getChartPath(index.category_id, 50, 24, false)" 
                        fill="none" 
                        :stroke="Number(index.market_cap_change_24h) >= 0 ? '#38efeb' : '#ef4444'" 
                        stroke-width="1.5"/>
                </svg>
              </div>
              <Icon name="ph:caret-right" class="m-icon" style="opacity: 0.3;" />
            </div>
          </div>
        </section>
      </template>

      <div class="m-bottom-spacer"></div>
    </main>

    <!-- Bottom Navigation -->
    <nav class="m-bottom-nav">
      <button class="m-nav-item" :class="{ active: activeTab === 'dashboard' }" @click="$emit('setTab', 'dashboard')">
        <Icon name="ph:squares-four" class="m-nav-icon" />
        <span class="m-nav-label">Dashboard</span>
      </button>
      <button class="m-nav-item active" :class="{ active: activeTab === 'market' }">
        <Icon name="ph:trend-up" class="m-nav-icon" />
        <span class="m-nav-label">Market</span>
      </button>
      <button class="m-nav-item" :class="{ active: activeTab === 'analysis' }" @click="$emit('setTab', 'analysis')">
        <Icon name="ph:chart-line-up" class="m-nav-icon" />
        <span class="m-nav-label">Analysis</span>
      </button>
      <button class="m-nav-item" :class="{ active: activeTab === 'news' }" @click="$emit('setTab', 'news')">
        <Icon name="ph:newspaper" class="m-nav-icon" />
        <span class="m-nav-label">News</span>
      </button>
      <button class="m-nav-item" :class="{ active: activeTab === 'aichat' }" @click="$emit('setTab', 'aichat')">
        <Icon name="ph:chat-dots" class="m-nav-icon" />
        <span class="m-nav-label">AI Chat</span>
      </button>
    </nav>

    <!-- Index Detail Modal (from detail-modal-mobile.php) -->
    <Teleport to="body">
      <div v-if="showIndexDetail && selectedIndex" class="m-modal-overlay" @click.self="closeIndexDetail">
        <div class="m-modal m-modal--full">
          <!-- Header with Close -->
          <div class="m-modal-header">
            <div style="flex: 1;">
              <span class="m-badge m-badge--info" style="margin-bottom: 4px; display: inline-block;">{{ selectedIndex.category_id }}</span>
              <h3 style="margin: 0;">{{ selectedIndex.name }}</h3>
            </div>
            <button class="m-modal-close" @click="closeIndexDetail">×</button>
          </div>
          
          <!-- Scrollable Content -->
          <div class="m-modal-body" style="max-height: 80vh;">
            <!-- Price Block -->
            <section class="m-section">
              <div class="m-card" style="text-align: center;">
                <span class="m-info-subtitle">Total Market Cap</span>
                <span class="m-featured-price" style="display: block; margin: 8px 0;">{{ formatCurrency(selectedIndex.market_cap, 2) }}</span>
                <span class="m-badge" :class="Number(selectedIndex.market_cap_change_24h) >= 0 ? 'm-badge--success' : 'm-badge--danger'">
                  {{ Number(selectedIndex.market_cap_change_24h) >= 0 ? '▲' : '▼' }}
                  {{ Math.abs(Number(selectedIndex.market_cap_change_24h) || 0).toFixed(2) }}%
                </span>
              </div>
            </section>
            
            <!-- Stats -->
            <section class="m-section">
              <div class="m-list">
                <div class="m-list-item">
                  <div class="m-info">
                    <span class="m-info-title">Market Sentiment</span>
                  </div>
                  <span class="m-badge" :class="Number(selectedIndex.market_cap_change_24h) >= 0 ? 'm-badge--success' : 'm-badge--danger'">
                    {{ Number(selectedIndex.market_cap_change_24h) >= 0 ? '🟢 Bullish' : '🔴 Bearish' }}
                  </span>
                </div>
                <div class="m-list-item">
                  <div class="m-info">
                    <span class="m-info-title">24H Momentum</span>
                  </div>
                  <span class="m-badge" :class="Number(selectedIndex.market_cap_change_24h) >= 0 ? 'm-badge--success' : 'm-badge--danger'">
                    {{ Number(selectedIndex.market_cap_change_24h) >= 0 ? '+' : '' }}{{ (Number(selectedIndex.market_cap_change_24h) || 0).toFixed(2) }}%
                  </span>
                </div>
                <div class="m-list-item">
                  <div class="m-info">
                    <span class="m-info-title">Top Assets</span>
                  </div>
                  <span class="m-text-accent">{{ selectedIndex.top_coins_text || 'BTC, ETH, SOL' }}</span>
                </div>
                <div class="m-list-item">
                  <div class="m-info">
                    <span class="m-info-title">24H Volume</span>
                  </div>
                  <span>{{ formatCurrency(selectedIndex.volume_24h, 0) }}</span>
                </div>
              </div>
            </section>
            
            <!-- Action Buttons -->
            <section class="m-section">
              <div style="display: flex; gap: 8px;">
                <button class="m-btn" :class="{ 'm-btn--active': isIndexWatchlisted(selectedIndex.category_id) }" @click="toggleIndexWatchlist(selectedIndex.category_id)" style="flex: 1;">
                  <Icon name="ph:bookmark" class="m-icon" style="margin-right: 6px;" />
                  {{ isIndexWatchlisted(selectedIndex.category_id) ? 'Watchlisted' : 'Watchlist' }}
                </button>
                <button class="m-btn" @click="exportIndexData(selectedIndex)" style="flex: 1;">
                  <Icon name="ph:download" class="m-icon" style="margin-right: 6px;" />
                  Export
                </button>
              </div>
            </section>
            
            <!-- Chart Section -->
            <section class="m-section">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <h3 class="m-section-title" style="margin: 0;">Price Chart</h3>
                <div style="display: flex; gap: 4px;">
                  <button v-for="tf in timeFilters" :key="tf" 
                          class="m-filter-chip" 
                          :class="{ active: detailTimeFilter === tf }"
                          @click="detailTimeFilter = tf">
                    {{ tf }}
                  </button>
                </div>
              </div>
              <div class="m-card">
                <div class="m-chart-area" style="height: 120px;">
                  <svg viewBox="0 0 320 120" preserveAspectRatio="none" style="width: 100%; height: 100%;">
                    <defs>
                      <linearGradient id="mobileChartGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                        <stop offset="0%" :stop-color="Number(selectedIndex.market_cap_change_24h) >= 0 ? 'rgba(56, 239, 235, 0.3)' : 'rgba(239, 68, 68, 0.3)'" />
                        <stop offset="100%" stop-color="rgba(0,0,0,0)" />
                      </linearGradient>
                    </defs>
                    <path :d="getDetailChartPath(selectedIndex.category_id, detailTimeFilter, 320, 120, true)" fill="url(#mobileChartGrad)" />
                    <path :d="getDetailChartPath(selectedIndex.category_id, detailTimeFilter, 320, 120, false)" 
                          fill="none" 
                          :stroke="Number(selectedIndex.market_cap_change_24h) >= 0 ? '#38efeb' : '#ef4444'" 
                          stroke-width="2"
                          stroke-linecap="round"/>
                  </svg>
                </div>
              </div>
            </section>
            
            <!-- Composition Section -->
            <section class="m-section">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <h3 class="m-section-title" style="margin: 0;">Index Composition</h3>
                <span class="m-badge m-badge--info">{{ selectedIndex.coins_count || categoryCoins.length }}</span>
              </div>
              
              <!-- Loading State -->
              <div v-if="categoryCoinsLoading" class="m-card" style="text-align: center; padding: 40px 16px;">
                <div class="m-spinner"></div>
                <p class="m-text-muted" style="margin-top: 12px;">Loading...</p>
              </div>
              
              <!-- Coins List -->
              <div v-else class="m-list">
                <template v-if="categoryCoins.length > 0">
                  <div class="m-list-item" v-for="(coin, idx) in categoryCoins.slice(0, 20)" :key="coin.coin_id">
                    <span class="m-rank">{{ idx + 1 }}</span>
                    <img v-if="coin.image" :src="coin.image" class="m-avatar" />
                    <div v-else class="m-avatar" style="background: rgba(255,255,255,0.1); display: flex; align-items: center; justify-content: center; font-size: 10px; font-weight: 700;">{{ coin.symbol?.slice(0,2) }}</div>
                    <div class="m-info">
                      <span class="m-info-title">{{ coin.symbol?.toUpperCase() }}</span>
                      <span class="m-info-subtitle">{{ coin.name }}</span>
                    </div>
                    <div style="text-align: right;">
                      <span class="m-info-title">{{ formatCurrency(coin.price, 2) }}</span>
                      <span class="m-info-subtitle" :class="Number(coin.change_24h) >= 0 ? 'm-text-success' : 'm-text-danger'">
                        {{ Number(coin.change_24h) >= 0 ? '+' : '' }}{{ (Number(coin.change_24h) || 0).toFixed(2) }}%
                      </span>
                    </div>
                  </div>
                </template>
                
                <!-- From API top_3_coins -->
                <template v-else-if="selectedIndex.top_3_coins && selectedIndex.top_3_coins.length > 0">
                  <div class="m-list-item" v-for="(coinUrl, idx) in selectedIndex.top_3_coins" :key="'api-'+idx">
                    <span class="m-rank">{{ idx + 1 }}</span>
                    <img :src="coinUrl" class="m-avatar" />
                    <div class="m-info">
                      <span class="m-info-title">Asset {{ idx + 1 }}</span>
                    </div>
                    <span class="m-text-muted">--</span>
                  </div>
                </template>
                
                <!-- Empty -->
                <div v-else class="m-card" style="text-align: center; padding: 40px 16px;">
                  <p class="m-text-muted">No data available</p>
                </div>
              </div>
            </section>
            
            <!-- About Section -->
            <section class="m-section">
              <h3 class="m-section-title">About</h3>
              <div class="m-card">
                <p class="m-text-muted" style="margin: 0; line-height: 1.6;">{{ selectedIndex.description || 'This category tracks cryptocurrencies weighted by market cap.' }}</p>
              </div>
            </section>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
interface MarketIndex {
  category_id: string
  name: string
  market_cap: number
  market_cap_change_24h: number
  volume_24h?: number
  top_3_coins?: string[]
  top_coins_text?: string
  coins_count?: number
  description?: string
  updated_at?: string
}

interface Coin {
  coin_id: string
  symbol: string
  name: string
  image?: string
  price: number
  change_24h: number
}

defineProps<{
  activeTab?: string
}>()

defineEmits<{
  (e: 'setTab', tab: string): void
  (e: 'openSearch'): void
}>()

const loading = ref(false)
const featuredIndexIdx = ref(0)
const selectedIndex = ref<MarketIndex | null>(null)
const showIndexDetail = ref(false)
const categoryCoinsLoading = ref(false)
const categoryCoins = ref<Coin[]>([])
const detailTimeFilter = ref('1D')
const watchlistedIndices = ref<string[]>([])

const timeFilters = ['1H', '1D', '1W', '1M']

// Market data
const btcPrice = ref(98500)
const btcChange = ref(2.4)

// Sample indices data (to be replaced with API call)
const indices = ref<MarketIndex[]>([
  { category_id: 'layer-1', name: 'Layer 1 (L1)', market_cap: 2800000000000, market_cap_change_24h: 2.5, volume_24h: 89000000000, coins_count: 45, top_coins_text: 'BTC, ETH, SOL' },
  { category_id: 'smart-contract-platform', name: 'Smart Contract Platform', market_cap: 580000000000, market_cap_change_24h: 3.2, volume_24h: 28000000000, coins_count: 32, top_coins_text: 'ETH, SOL, ADA' },
  { category_id: 'decentralized-finance-defi', name: 'DeFi', market_cap: 120000000000, market_cap_change_24h: -1.8, volume_24h: 8500000000, coins_count: 156, top_coins_text: 'LINK, UNI, AAVE' },
  { category_id: 'meme-token', name: 'Meme Tokens', market_cap: 65000000000, market_cap_change_24h: -4.2, volume_24h: 12000000000, coins_count: 89, top_coins_text: 'DOGE, SHIB, PEPE' },
  { category_id: 'artificial-intelligence', name: 'Artificial Intelligence', market_cap: 42000000000, market_cap_change_24h: 8.5, volume_24h: 3200000000, coins_count: 28, top_coins_text: 'RNDR, FET, TAO' },
  { category_id: 'gaming', name: 'Gaming (GameFi)', market_cap: 18000000000, market_cap_change_24h: 1.2, volume_24h: 1800000000, coins_count: 67, top_coins_text: 'IMX, GALA, AXS' },
  { category_id: 'layer-2', name: 'Layer 2 (L2)', market_cap: 28000000000, market_cap_change_24h: 4.1, volume_24h: 2400000000, coins_count: 18, top_coins_text: 'ARB, OP, MATIC' },
  { category_id: 'real-world-assets-rwa', name: 'Real World Assets (RWA)', market_cap: 12000000000, market_cap_change_24h: 2.8, volume_24h: 890000000, coins_count: 24, top_coins_text: 'ONDO, MKR, LINK' },
])

const validIndices = computed(() => indices.value.filter(idx => idx.market_cap > 0))
const popularCategories = computed(() => validIndices.value.slice(1, 7))
const featuredIndex = computed(() => validIndices.value[featuredIndexIdx.value])

const prevFeaturedIndex = () => {
  if (featuredIndexIdx.value > 0) {
    featuredIndexIdx.value--
  } else {
    featuredIndexIdx.value = validIndices.value.length - 1
  }
}

const nextFeaturedIndex = () => {
  if (featuredIndexIdx.value < validIndices.value.length - 1) {
    featuredIndexIdx.value++
  } else {
    featuredIndexIdx.value = 0
  }
}

const openIndexDetail = (index: MarketIndex) => {
  selectedIndex.value = index
  showIndexDetail.value = true
  loadCategoryCoins(index.category_id)
}

const closeIndexDetail = () => {
  showIndexDetail.value = false
  selectedIndex.value = null
  categoryCoins.value = []
}

const loadCategoryCoins = async (categoryId: string) => {
  categoryCoinsLoading.value = true
  // Simulate API call - replace with actual API
  await new Promise(resolve => setTimeout(resolve, 500))
  // Sample coins for demo
  categoryCoins.value = [
    { coin_id: 'bitcoin', symbol: 'BTC', name: 'Bitcoin', image: 'https://assets.coingecko.com/coins/images/1/small/bitcoin.png', price: 98500, change_24h: 2.4 },
    { coin_id: 'ethereum', symbol: 'ETH', name: 'Ethereum', image: 'https://assets.coingecko.com/coins/images/279/small/ethereum.png', price: 3450, change_24h: 1.8 },
    { coin_id: 'solana', symbol: 'SOL', name: 'Solana', image: 'https://assets.coingecko.com/coins/images/4128/small/solana.png', price: 185, change_24h: 8.5 },
  ]
  categoryCoinsLoading.value = false
}

const isIndexWatchlisted = (categoryId: string) => {
  return watchlistedIndices.value.includes(categoryId)
}

const toggleIndexWatchlist = (categoryId: string) => {
  const idx = watchlistedIndices.value.indexOf(categoryId)
  if (idx > -1) {
    watchlistedIndices.value.splice(idx, 1)
  } else {
    watchlistedIndices.value.push(categoryId)
  }
}

const exportIndexData = (index: MarketIndex) => {
  console.log('Export:', index)
}

const formatCategoryId = (categoryId: string) => {
  return categoryId.replace(/-/g, ' ').toUpperCase()
}

const formatCurrency = (n: number, decimals = 2) => {
  if (!n) return '$--'
  if (n >= 1e12) return '$' + (n / 1e12).toFixed(decimals) + 'T'
  if (n >= 1e9) return '$' + (n / 1e9).toFixed(decimals) + 'B'
  if (n >= 1e6) return '$' + (n / 1e6).toFixed(decimals) + 'M'
  if (n >= 1) return '$' + n.toLocaleString('en-US', { minimumFractionDigits: decimals, maximumFractionDigits: decimals })
  return '$' + n.toFixed(6)
}

const getChartPath = (categoryId: string, width: number, height: number, fill: boolean) => {
  const hash = categoryId.split('').reduce((a, b) => ((a << 5) - a) + b.charCodeAt(0), 0)
  const points: number[] = []
  
  for (let i = 0; i <= 10; i++) {
    const x = (i / 10) * width
    const y = height * 0.2 + Math.sin(hash + i * 0.8) * height * 0.3 + Math.cos(hash * 2 + i * 0.5) * height * 0.15
    points.push(x, Math.max(height * 0.1, Math.min(height * 0.9, y)))
  }
  
  let path = `M${points[0]},${points[1]}`
  for (let i = 2; i < points.length; i += 2) {
    const p0x = i >= 4 ? points[i - 4] : points[0]
    const p0y = i >= 4 ? points[i - 3] : points[1]
    const p1x = points[i - 2]
    const p1y = points[i - 1]
    const p2x = points[i]
    const p2y = points[i + 1]
    
    const cp1x = p1x + (p2x - p0x) / 6
    const cp1y = p1y + (p2y - p0y) / 6
    const cp2x = p2x - (p2x - p1x) / 6
    const cp2y = p2y - (p2y - p1y) / 6
    
    path += ` C${cp1x},${cp1y} ${cp2x},${cp2y} ${p2x},${p2y}`
  }
  
  if (fill) {
    path += ` L${width},${height} L0,${height} Z`
  }
  
  return path
}

const getDetailChartPath = (categoryId: string, timeFilter: string, width: number, height: number, fill: boolean) => {
  // Add time filter variation to the chart
  const tfOffset = timeFilter === '1H' ? 0 : timeFilter === '1D' ? 1 : timeFilter === '1W' ? 2 : 3
  return getChartPath(categoryId + tfOffset, width, height, fill)
}
</script>

<style scoped>
/* Featured Card */
.m-featured-card {
  padding: 16px !important;
  background: linear-gradient(160deg, rgba(20,25,40,0.98) 0%, rgba(12,15,28,0.98) 100%);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 14px;
  overflow: hidden;
}

.m-featured-name {
  font-size: 1.5rem;
  font-weight: 700;
  color: #fff;
  margin: 4px 0 12px;
}

.m-featured-price {
  font-size: 1.8rem;
  font-weight: 700;
  color: #fff;
}

.m-chart-area {
  height: 90px;
  margin: 0 -16px 16px;
}

.m-chart-area svg {
  width: 100%;
  height: 100%;
}

/* Badge Variants */
.m-badge--accent {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  background: rgba(56, 239, 235, 0.15);
  border: 1px solid rgba(56, 239, 235, 0.3);
  border-radius: 12px;
  font-size: 0.65rem;
  font-weight: 700;
  color: #38efeb;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.m-badge-dot {
  width: 6px;
  height: 6px;
  background: #38efeb;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.m-badge--success {
  background: rgba(34, 197, 94, 0.2);
  color: #22c55e;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
}

.m-badge--danger {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
}

.m-badge--info {
  background: rgba(56, 189, 248, 0.15);
  color: #38bdf8;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
}

/* Scroll Cards */
.m-scroll {
  display: flex;
  gap: 10px;
  overflow-x: auto;
  padding: 4px 0;
  margin: 0 -8px;
  padding-left: 8px;
  padding-right: 8px;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
}

.m-scroll::-webkit-scrollbar {
  display: none;
}

.m-scroll-card {
  flex: 0 0 auto;
  min-width: 150px;
  padding: 14px;
  background: linear-gradient(145deg, rgba(30,35,50,0.95) 0%, rgba(20,25,40,0.95) 100%);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.m-scroll-card:hover {
  border-color: rgba(56, 239, 235, 0.3);
}

.m-scroll-card__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.m-scroll-card__badge {
  font-size: 0.55rem;
  font-weight: 600;
  color: rgba(255,255,255,0.5);
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.m-scroll-card__link {
  font-size: 0.55rem;
  font-weight: 600;
  color: #38efeb;
}

.m-scroll-card__name {
  font-size: 0.9rem;
  font-weight: 600;
  color: #fff;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.m-scroll-card__price {
  font-size: 1.1rem;
  font-weight: 700;
  color: #fff;
  margin-bottom: 2px;
}

.m-scroll-card__change {
  font-size: 0.8rem;
  font-weight: 600;
}

.m-scroll-card__change.positive {
  color: #22c55e;
}

.m-scroll-card__change.negative {
  color: #ef4444;
}

.m-scroll-card__chart {
  height: 40px;
  margin: 8px -14px -14px;
}

.m-scroll-card__chart svg {
  width: 100%;
  height: 100%;
}

/* Modal */
.m-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.8);
  z-index: 10000;
  display: flex;
  align-items: flex-end;
}

.m-modal--full {
  width: 100%;
  max-height: 90vh;
  background: #0b0f19;
  border-radius: 20px 20px 0 0;
  overflow: hidden;
}

.m-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid rgba(255,255,255,0.06);
}

.m-modal-header h3 {
  font-size: 1rem;
  font-weight: 600;
  color: #fff;
  margin: 0;
}

.m-modal-close {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255,255,255,0.1);
  border: none;
  border-radius: 50%;
  color: #fff;
  font-size: 20px;
  cursor: pointer;
}

.m-modal-body {
  padding: 16px;
  overflow-y: auto;
  max-height: calc(90vh - 60px);
}

/* Filter Chip */
.m-filter-chip {
  padding: 6px 10px;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 6px;
  color: rgba(255,255,255,0.6);
  font-size: 0.7rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.m-filter-chip.active {
  background: rgba(56, 239, 235, 0.15);
  border-color: rgba(56, 239, 235, 0.4);
  color: #38efeb;
}

/* Button Active State */
.m-btn--active {
  background: rgba(56, 239, 235, 0.15) !important;
  border-color: rgba(56, 239, 235, 0.4) !important;
  color: #38efeb !important;
}

/* Bottom spacer */
.m-bottom-spacer {
  height: 80px;
}

/* Action Button Dark variant */
.m-action-btn--dark {
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.1);
}
</style>
