<template>
  <div class="mobile-market">
    <!-- Loading State -->
    <div v-if="loading" class="m-loading">
      <div class="m-spinner"></div>
      <p class="m-text-muted">Loading market data...</p>
    </div>

    <template v-else>
      <!-- Featured Index Hero Card -->
      <section class="m-section" v-if="featuredIndex">
        <div class="m-featured-card">
          <div class="m-featured-header">
            <span class="m-badge-accent">
              <span class="m-badge-dot"></span>
              FEATURED
            </span>
            <div class="m-featured-nav">
              <button @click="prevFeaturedIndex" class="m-nav-btn">
                <Icon name="ph:caret-left" class="w-4 h-4" />
              </button>
              <button @click="nextFeaturedIndex" class="m-nav-btn">
                <Icon name="ph:caret-right" class="w-4 h-4" />
              </button>
            </div>
          </div>
          
          <span class="m-featured-category">{{ featuredIndex.category }}</span>
          <h2 class="m-featured-name">{{ featuredIndex.name }}</h2>
          
          <div class="m-featured-price-row">
            <span class="m-featured-price">${{ formatMarketCap(featuredIndex.market_cap) }}</span>
            <span class="m-badge" :class="featuredIndex.change >= 0 ? 'm-badge-success' : 'm-badge-danger'">
              {{ featuredIndex.change >= 0 ? '↑' : '↓' }}
              {{ Math.abs(featuredIndex.change).toFixed(2) }}%
            </span>
          </div>
          
          <div class="m-chart-area">
            <svg viewBox="0 0 320 90" preserveAspectRatio="none">
              <defs>
                <linearGradient id="heroGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" :stop-color="featuredIndex.change >= 0 ? 'rgba(56, 239, 235, 0.3)' : 'rgba(239, 68, 68, 0.3)'" />
                  <stop offset="100%" stop-color="transparent" />
                </linearGradient>
              </defs>
              <path d="M0,50 C40,45 80,60 120,40 C160,20 200,55 240,35 C280,15 320,45 320,30 L320,90 L0,90 Z" fill="url(#heroGrad)" />
              <path d="M0,50 C40,45 80,60 120,40 C160,20 200,55 240,35 C280,15 320,45 320,30" 
                    fill="none" 
                    :stroke="featuredIndex.change >= 0 ? '#38efeb' : '#ef4444'" 
                    stroke-width="2.5"
                    stroke-linecap="round"/>
            </svg>
          </div>
          
          <button class="m-btn-primary" @click="openIndexDetail(featuredIndex)">
            <span>View Details</span>
            <Icon name="ph:caret-right" class="w-4 h-4" />
          </button>
        </div>
      </section>
      
      <!-- Popular Categories -->
      <section class="m-section">
        <h3 class="m-section-title">Popular Categories</h3>
        <div class="m-stats-scroll">
          <div class="m-stats-container">
            <div v-for="(index, i) in popularCategories" :key="index.id" 
                 class="m-scroll-card" 
                 @click="openIndexDetail(index)">
              <div class="m-scroll-card-header">
                <span class="m-scroll-card-badge">{{ index.category }}</span>
                <span class="m-scroll-card-link">DETAILS ↗</span>
              </div>
              <div class="m-scroll-card-name">{{ index.name }}</div>
              <div class="m-scroll-card-price">${{ formatMarketCap(index.market_cap) }}</div>
              <div class="m-scroll-card-change" :class="index.change >= 0 ? 'positive' : 'negative'">
                {{ index.change >= 0 ? '+' : '' }}{{ index.change.toFixed(2) }}%
              </div>
              <div class="m-scroll-card-chart">
                <svg viewBox="0 0 120 40" preserveAspectRatio="none">
                  <path d="M0,30 C15,25 30,35 45,20 C60,5 75,15 90,25 C105,35 120,20 120,20" 
                        fill="none" 
                        :stroke="index.change >= 0 ? '#38efeb' : '#ef4444'" 
                        stroke-width="1.5"/>
                </svg>
              </div>
            </div>
          </div>
        </div>
      </section>
      
      <!-- All Categories List -->
      <section class="m-section">
        <div class="m-section-header">
          <h3 class="m-section-title">All Categories</h3>
          <span class="m-badge-info">{{ categories.length }}</span>
        </div>
        
        <div class="m-list">
          <div v-for="(cat, idx) in categories" :key="cat.id" 
               class="m-list-item" 
               @click="openIndexDetail(cat)">
            <span class="m-rank">{{ idx + 1 }}</span>
            <div class="m-info">
              <span class="m-info-title">{{ cat.name }}</span>
              <span class="m-info-subtitle m-text-accent">{{ cat.category }}</span>
            </div>
            <div class="m-price-col">
              <span class="m-info-title">${{ formatMarketCap(cat.market_cap) }}</span>
              <span class="m-info-subtitle" :class="cat.change >= 0 ? 'm-text-success' : 'm-text-danger'">
                {{ cat.change >= 0 ? '+' : '' }}{{ cat.change.toFixed(2) }}%
              </span>
            </div>
            <Icon name="ph:caret-right" class="w-4 h-4 opacity-30" />
          </div>
        </div>
      </section>
    </template>
    
    <div class="m-bottom-spacer"></div>
  </div>
</template>

<script setup lang="ts">
const loading = ref(false)
const featuredIndexNum = ref(0)

// Mock data
const categories = ref([
  { id: 'defi', name: 'Decentralized Finance', category: 'DEFI', market_cap: 85000000000, change: 3.2 },
  { id: 'layer-1', name: 'Layer 1', category: 'L1', market_cap: 520000000000, change: -1.5 },
  { id: 'layer-2', name: 'Layer 2 Scaling', category: 'L2', market_cap: 28000000000, change: 5.8 },
  { id: 'nft', name: 'NFT & Collectibles', category: 'NFT', market_cap: 12000000000, change: -2.1 },
  { id: 'gaming', name: 'Gaming & Metaverse', category: 'GAMING', market_cap: 18000000000, change: 4.5 },
  { id: 'ai', name: 'Artificial Intelligence', category: 'AI', market_cap: 32000000000, change: 8.7 },
  { id: 'meme', name: 'Meme Coins', category: 'MEME', market_cap: 65000000000, change: -5.2 },
])

const featuredIndex = computed(() => categories.value[featuredIndexNum.value])
const popularCategories = computed(() => categories.value.slice(1, 6))

const prevFeaturedIndex = () => {
  featuredIndexNum.value = (featuredIndexNum.value - 1 + categories.value.length) % categories.value.length
}

const nextFeaturedIndex = () => {
  featuredIndexNum.value = (featuredIndexNum.value + 1) % categories.value.length
}

const openIndexDetail = (index: any) => {
  console.log('Open index detail:', index)
}

const formatMarketCap = (cap: number) => {
  if (cap >= 1e12) return (cap / 1e12).toFixed(1) + 'T'
  if (cap >= 1e9) return (cap / 1e9).toFixed(1) + 'B'
  if (cap >= 1e6) return (cap / 1e6).toFixed(1) + 'M'
  return cap.toLocaleString()
}
</script>

<style scoped>
.mobile-market {
  padding: 0;
}

.m-loading {
  text-align: center;
  padding: 60px 16px;
}

.m-featured-card {
  background: linear-gradient(135deg, rgba(56, 239, 235, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 16px;
  margin-bottom: 16px;
}

.m-featured-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.m-badge-accent {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  background: rgba(56, 239, 235, 0.15);
  border-radius: 20px;
  font-size: 10px;
  font-weight: 600;
  color: #38efeb;
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

.m-featured-nav {
  display: flex;
  gap: 6px;
}

.m-nav-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
}

.m-featured-category {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
  letter-spacing: 0.8px;
}

.m-featured-name {
  font-size: 20px;
  font-weight: 700;
  color: #ffffff;
  margin: 4px 0 12px;
}

.m-featured-price-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.m-featured-price {
  font-size: 24px;
  font-weight: 700;
  color: #ffffff;
}

.m-badge-success {
  background: rgba(34, 197, 94, 0.2);
  color: #22c55e;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
}

.m-badge-danger {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
}

.m-chart-area {
  height: 90px;
  margin: 0 -16px;
}

.m-chart-area svg {
  width: 100%;
  height: 100%;
}

.m-btn-primary {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 12px;
  background: linear-gradient(135deg, #38efeb, #0066ff);
  border: none;
  border-radius: 10px;
  color: #000;
  font-weight: 600;
  cursor: pointer;
}

/* Scroll Cards */
.m-scroll-card {
  flex: 0 0 auto;
  width: 160px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 12px;
  cursor: pointer;
  transition: background 0.2s;
}

.m-scroll-card:active {
  background: rgba(255, 255, 255, 0.08);
}

.m-scroll-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.m-scroll-card-badge {
  font-size: 9px;
  font-weight: 600;
  color: #38efeb;
  background: rgba(56, 239, 235, 0.15);
  padding: 2px 6px;
  border-radius: 4px;
}

.m-scroll-card-link {
  font-size: 8px;
  color: rgba(255, 255, 255, 0.4);
}

.m-scroll-card-name {
  font-size: 13px;
  font-weight: 600;
  color: #ffffff;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.m-scroll-card-price {
  font-size: 16px;
  font-weight: 700;
  color: #ffffff;
}

.m-scroll-card-change {
  font-size: 12px;
  font-weight: 600;
  margin-bottom: 8px;
}

.m-scroll-card-change.positive { color: #22c55e; }
.m-scroll-card-change.negative { color: #ef4444; }

.m-scroll-card-chart {
  height: 32px;
  margin: 0 -12px -12px;
}

.m-scroll-card-chart svg {
  width: 100%;
  height: 100%;
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
