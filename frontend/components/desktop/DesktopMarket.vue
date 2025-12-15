<template>
  <div class="d-market">
    <!-- Header -->
    <section class="d-section">
      <div class="d-section-header">
        <h1 class="d-page-title">Market Categories</h1>
        <div class="d-search-box">
          <Icon name="ph:magnifying-glass" class="d-search-icon" />
          <input v-model="searchQuery" type="text" placeholder="Search categories..." class="d-search-input" />
        </div>
      </div>
    </section>

    <!-- Featured Category -->
    <section class="d-section" v-if="featuredCategory">
      <div class="d-featured-card">
        <div class="d-featured-content">
          <span class="d-badge-accent">
            <span class="d-badge-dot"></span>
            FEATURED
          </span>
          <span class="d-featured-category">{{ featuredCategory.category }}</span>
          <h2 class="d-featured-name">{{ featuredCategory.name }}</h2>
          <div class="d-featured-stats">
            <div class="d-featured-stat">
              <span class="d-featured-label">Market Cap</span>
              <span class="d-featured-value">${{ formatMarketCap(featuredCategory.market_cap) }}</span>
            </div>
            <div class="d-featured-stat">
              <span class="d-featured-label">24h Change</span>
              <span class="d-featured-value" :class="featuredCategory.change >= 0 ? 'up' : 'down'">
                {{ featuredCategory.change >= 0 ? '+' : '' }}{{ featuredCategory.change.toFixed(2) }}%
              </span>
            </div>
            <div class="d-featured-stat">
              <span class="d-featured-label">Top Coins</span>
              <span class="d-featured-value">{{ featuredCategory.coins_count }}</span>
            </div>
          </div>
          <button class="d-btn-primary" @click="openCategory(featuredCategory)">
            View Category
            <Icon name="ph:arrow-right" class="w-4 h-4" />
          </button>
        </div>
        <div class="d-featured-chart">
          <svg viewBox="0 0 400 150" preserveAspectRatio="none">
            <defs>
              <linearGradient id="featuredGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" :stop-color="featuredCategory.change >= 0 ? 'rgba(56, 239, 235, 0.3)' : 'rgba(239, 68, 68, 0.3)'" />
                <stop offset="100%" stop-color="transparent" />
              </linearGradient>
            </defs>
            <path d="M0,100 C50,90 100,120 150,80 C200,40 250,90 300,60 C350,30 400,70 400,50 L400,150 L0,150 Z" fill="url(#featuredGrad)" />
            <path d="M0,100 C50,90 100,120 150,80 C200,40 250,90 300,60 C350,30 400,70 400,50" 
                  fill="none" 
                  :stroke="featuredCategory.change >= 0 ? '#38efeb' : '#ef4444'" 
                  stroke-width="3"
                  stroke-linecap="round"/>
          </svg>
        </div>
      </div>
    </section>

    <!-- Categories Grid -->
    <section class="d-section">
      <h2 class="d-section-title">All Categories</h2>
      <div class="d-categories-grid">
        <div v-for="cat in filteredCategories" :key="cat.id" class="d-category-card" @click="openCategory(cat)">
          <div class="d-category-header">
            <span class="d-category-badge">{{ cat.category }}</span>
            <span class="d-category-count">{{ cat.coins_count }} coins</span>
          </div>
          <h3 class="d-category-name">{{ cat.name }}</h3>
          <div class="d-category-stats">
            <div class="d-category-mcap">${{ formatMarketCap(cat.market_cap) }}</div>
            <div class="d-category-change" :class="cat.change >= 0 ? 'up' : 'down'">
              {{ cat.change >= 0 ? '+' : '' }}{{ cat.change.toFixed(2) }}%
            </div>
          </div>
          <div class="d-category-chart">
            <svg viewBox="0 0 120 40" preserveAspectRatio="none">
              <path d="M0,30 C15,25 30,35 45,20 C60,5 75,15 90,25 C105,35 120,20 120,20" 
                    fill="none" 
                    :stroke="cat.change >= 0 ? '#38efeb' : '#ef4444'" 
                    stroke-width="2"/>
            </svg>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
const searchQuery = ref('')

const categories = ref([
  { id: 'defi', name: 'Decentralized Finance', category: 'DEFI', market_cap: 85000000000, change: 3.2, coins_count: 245 },
  { id: 'layer-1', name: 'Layer 1', category: 'L1', market_cap: 520000000000, change: -1.5, coins_count: 68 },
  { id: 'layer-2', name: 'Layer 2 Scaling', category: 'L2', market_cap: 28000000000, change: 5.8, coins_count: 42 },
  { id: 'nft', name: 'NFT & Collectibles', category: 'NFT', market_cap: 12000000000, change: -2.1, coins_count: 156 },
  { id: 'gaming', name: 'Gaming & Metaverse', category: 'GAMING', market_cap: 18000000000, change: 4.5, coins_count: 189 },
  { id: 'ai', name: 'Artificial Intelligence', category: 'AI', market_cap: 32000000000, change: 8.7, coins_count: 78 },
  { id: 'meme', name: 'Meme Coins', category: 'MEME', market_cap: 65000000000, change: -5.2, coins_count: 312 },
  { id: 'exchange', name: 'Exchange Tokens', category: 'CEX', market_cap: 95000000000, change: 1.8, coins_count: 34 },
])

const featuredCategory = computed(() => categories.value[0])

const filteredCategories = computed(() => {
  if (!searchQuery.value) return categories.value
  return categories.value.filter(c => 
    c.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
    c.category.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})

const openCategory = (cat: any) => {
  console.log('Open category:', cat)
}

const formatMarketCap = (cap: number) => {
  if (cap >= 1e12) return (cap / 1e12).toFixed(1) + 'T'
  if (cap >= 1e9) return (cap / 1e9).toFixed(1) + 'B'
  if (cap >= 1e6) return (cap / 1e6).toFixed(1) + 'M'
  return cap.toLocaleString()
}
</script>

<style scoped>
.d-market {
  padding: 24px 0;
}

.d-page-title {
  font-size: 32px;
  font-weight: 700;
  margin: 0;
}

.d-search-box {
  position: relative;
  width: 300px;
}

.d-search-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  width: 18px;
  height: 18px;
  color: rgba(255, 255, 255, 0.4);
}

.d-search-input {
  width: 100%;
  padding: 12px 16px 12px 44px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: #ffffff;
  font-size: 14px;
}

.d-search-input:focus {
  outline: none;
  border-color: #38efeb;
}

/* Featured Card */
.d-featured-card {
  display: grid;
  grid-template-columns: 1fr 1fr;
  background: linear-gradient(135deg, rgba(56, 239, 235, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  overflow: hidden;
}

.d-featured-content {
  padding: 32px;
}

.d-badge-accent {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  background: rgba(56, 239, 235, 0.15);
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
  color: #38efeb;
  margin-bottom: 16px;
}

.d-badge-dot {
  width: 8px;
  height: 8px;
  background: #38efeb;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.d-featured-category {
  display: block;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 8px;
}

.d-featured-name {
  font-size: 32px;
  font-weight: 700;
  margin: 0 0 24px;
}

.d-featured-stats {
  display: flex;
  gap: 32px;
  margin-bottom: 24px;
}

.d-featured-stat {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.d-featured-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

.d-featured-value {
  font-size: 20px;
  font-weight: 700;
}

.d-featured-value.up { color: #22c55e; }
.d-featured-value.down { color: #ef4444; }

.d-btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 14px 24px;
  background: linear-gradient(135deg, #38efeb, #0066ff);
  border: none;
  border-radius: 12px;
  color: #000;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.d-btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(56, 239, 235, 0.3);
}

.d-featured-chart {
  display: flex;
  align-items: flex-end;
}

.d-featured-chart svg {
  width: 100%;
  height: 150px;
}

/* Categories Grid */
.d-categories-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.d-category-card {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.2s;
}

.d-category-card:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(56, 239, 235, 0.3);
  transform: translateY(-4px);
}

.d-category-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.d-category-badge {
  padding: 4px 10px;
  background: rgba(56, 239, 235, 0.15);
  border-radius: 6px;
  font-size: 10px;
  font-weight: 600;
  color: #38efeb;
}

.d-category-count {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
}

.d-category-name {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 12px;
  color: #ffffff;
}

.d-category-stats {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.d-category-mcap {
  font-size: 18px;
  font-weight: 700;
}

.d-category-change {
  font-size: 14px;
  font-weight: 600;
}

.d-category-change.up { color: #22c55e; }
.d-category-change.down { color: #ef4444; }

.d-category-chart {
  height: 40px;
  margin: 0 -20px -20px;
}

.d-category-chart svg {
  width: 100%;
  height: 100%;
}

@media (max-width: 1200px) {
  .d-categories-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
